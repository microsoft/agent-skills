---
name: wiki-ado-convert
description: Converts VitePress/GFM wiki markdown to Azure DevOps Wiki-compatible format. Generates a Node.js build script that transforms Mermaid syntax, strips front matter, fixes links, and outputs ADO-compatible copies to dist/ado-wiki/.
---

# ADO Wiki Converter

Generate a Node.js build script that transforms VitePress/GFM markdown documentation into Azure DevOps Wiki-compatible format. The source files remain untouched — the script produces transformed copies in `dist/ado-wiki/`.

## Why This Is Needed

Azure DevOps Wikis use a markdown dialect that differs from GFM and VitePress in several critical ways. Documentation that renders perfectly in VitePress will have broken diagrams, raw front matter, dead links, and rendering issues when published as an ADO Wiki.

## ADO Wiki Incompatibilities

### CRITICAL — Will Break Rendering

| Issue | VitePress/GFM | ADO Wiki | Fix |
|-------|--------------|----------|-----|
| Mermaid code fences | ` ```mermaid ` ... ` ``` ` | `::: mermaid` ... `:::` | Convert opening/closing fences |
| `flowchart` keyword | `flowchart TD` | `graph TD` | Replace `flowchart` with `graph` (preserve direction) |
| `<br>` in Mermaid labels | `Node[Label<br>Text]` | Not supported | Strip `<br>` variants (replace with space) |
| Long arrows `---->` | `A ---->B` | Not supported | Replace with `-->` |
| YAML front matter | `---` ... `---` at file start | Rendered as visible raw text | Strip entirely |
| Parent-relative source links | `[text](../../src/file.cs)` | Broken (wiki is separate) | Convert to plain text |
| VitePress container directives | `::: tip` / `::: warning` | Not supported | Convert to ADO alert blockquotes `> [!TIP]` / `> [!WARNING]` |

### MODERATE — May Not Render Optimally

| Issue | Notes |
|-------|-------|
| Mermaid `style` directives | ADO's Mermaid version may ignore inline styling. Leave as-is (cosmetic). |
| Mermaid thick arrows `==>` | May work. Leave as-is. |
| Mermaid dotted arrows `-.->` | May work. Leave as-is. |
| Subgraph linking | Links to/from subgraphs not supported, but nodes inside subgraphs work fine. |

### NOT AN ISSUE (Compatible As-Is)

- ✅ Standard markdown tables, blockquotes, horizontal rules
- ✅ Unicode emoji, fenced code blocks with language identifiers
- ✅ Same-directory relative links (`./other-page.md`)
- ✅ External HTTP/HTTPS links
- ✅ Bold, italic, strikethrough, inline code
- ✅ Lists (ordered, unordered, nested), headings 1-6
- ✅ Images with relative paths

## ADO Wiki Mermaid Supported Diagram Types

As of 2025:
- ✅ `sequenceDiagram`, `gantt`, `graph` (NOT `flowchart`), `classDiagram`
- ✅ `stateDiagram`, `stateDiagram-v2`, `journey`, `pie`, `erDiagram`
- ✅ `requirementDiagram`, `gitGraph`, `timeline`
- ❌ `mindmap`, `sankey`, `quadrantChart`, `xychart`, `block`

## Build Script Structure

The generated script should be a **Node.js ESM module** (`scripts/build-ado-wiki.js`) using only built-in Node.js modules (`node:fs/promises`, `node:path`, `node:url`). No external dependencies.

### Transformation Functions

#### 1. Strip YAML Front Matter

Remove `---` delimited YAML blocks at file start. ADO renders these as visible text.

```javascript
function stripFrontMatter(content) {
  if (!content.startsWith('---')) return content;
  const endIndex = content.indexOf('\n---', 3);
  if (endIndex === -1) return content;
  let rest = content.slice(endIndex + 4);
  if (rest.startsWith('\n')) rest = rest.slice(1);
  return rest;
}
```

#### 2. Convert Mermaid Blocks

Process line-by-line, tracking mermaid block state. Apply fixes ONLY inside mermaid blocks:

- Opening: ` ```mermaid ` → `::: mermaid`
- Closing: ` ``` ` → `:::`
- `flowchart` → `graph` (preserve direction: TD, LR, TB, RL, BT)
- Strip `<br>`, `<br/>`, `<br />` (replace with space)
- Replace long arrows (`---->` with 4+ dashes) with `-->`

```javascript
function convertMermaidBlocks(content) {
  const lines = content.split('\n');
  const result = [];
  let inMermaid = false;

  for (const line of lines) {
    const trimmed = line.trimEnd();

    if (!inMermaid && /^```mermaid\s*$/.test(trimmed)) {
      result.push('::: mermaid');
      inMermaid = true;
      continue;
    }

    if (inMermaid && /^```\s*$/.test(trimmed)) {
      result.push(':::');
      inMermaid = false;
      continue;
    }

    if (inMermaid) {
      let fixed = line;
      fixed = fixed.replace(/^(\s*)flowchart(\s+)/, '$1graph$2');
      fixed = fixed.replace(/<br\s*\/?>/gi, ' ');
      fixed = fixed.replace(/-{4,}>/g, '-->');
      result.push(fixed);
    } else {
      result.push(line);
    }
  }

  return result.join('\n');
}
```

#### 3. Convert Parent-Relative Source Links

Convert `[text](../path)` to plain text. Preserves same-directory `.md` links and external URLs.

```javascript
function convertSourceLinks(content) {
  return content.replace(
    /\[([^\]]*)\]\(\.\.\/[^)]*\)/g,
    (match, linkText) => linkText
  );
}
```

#### 4. Convert VitePress Container Directives (Optional)

Convert `::: tip` / `::: warning` / `::: danger` to ADO alert blockquotes:

```javascript
function convertContainerDirectives(content) {
  // ::: tip → > [!TIP]
  // ::: warning → > [!WARNING]
  // ::: danger → > [!CAUTION]
  // ::: info → > [!NOTE]
  // closing ::: → (blank line)
}
```

### Script Main Flow

```javascript
async function main() {
  const files = await collectMarkdownFiles(ROOT);
  const stats = { frontMatter: 0, mermaid: 0, sourceLinks: 0, containers: 0 };

  for (const filePath of files) {
    let content = await readFile(filePath, 'utf-8');
    content = stripFrontMatter(content);
    content = convertMermaidBlocks(content);
    content = convertSourceLinks(content);

    const outPath = join(OUTPUT, relative(ROOT, filePath));
    await mkdir(dirname(outPath), { recursive: true });
    await writeFile(outPath, content, 'utf-8');
  }

  // Print transformation statistics
}
```

### Skip Directories

The script should skip: `node_modules`, `.vitepress`, `.git`, `dist`, `build`, `out`, `target`, and any non-documentation directories.

### npm Script Integration

```json
{
  "scripts": {
    "build:ado": "node scripts/build-ado-wiki.js"
  }
}
```

## Verification Checklist

After the script runs, verify:
1. File count in `dist/ado-wiki/` matches source (minus skipped dirs)
2. Zero ` ```mermaid ` fences remaining — all converted to `::: mermaid`
3. Zero `flowchart` keywords remaining — all converted to `graph`
4. No YAML front matter in output files
5. Parent-relative links converted to plain text
6. Same-directory `.md` links preserved
7. Directory structure preserved
8. Non-markdown files (images, etc.) copied as-is

## Important Notes

- **Source files are NEVER modified** — only copies in `dist/ado-wiki/`
- **Images must be copied too** — if source has images, copy them with same relative paths
- The script should work with **any VitePress wiki**, not just this specific one
- Print statistics at the end showing count of each transformation type
- Script uses zero external dependencies — only Node.js builtins
