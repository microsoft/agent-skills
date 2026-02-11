---
description: Generate a Node.js build script that converts the VitePress wiki to Azure DevOps Wiki-compatible markdown in dist/ado-wiki/. Transforms Mermaid syntax, strips front matter, fixes links.
---

# Deep Wiki: Azure DevOps Wiki Export

You are a Technical Documentation Engineer. Generate a Node.js build script that converts the VitePress wiki output into Azure DevOps (ADO) Wiki-compatible markdown.

## Context

Azure DevOps Wikis use a markdown dialect that differs from GFM/VitePress in critical ways. This command creates a preprocessing script that reads the generated wiki `.md` files, applies targeted transformations, and writes ADO-compatible copies to `dist/ado-wiki/`.

**Source files are NEVER modified.** Only transformed copies are written to the output directory.

## Process

### Step 1: Scan the Wiki Directory

Locate the generated wiki output (typically `wiki/` or the VitePress source directory). Scan for incompatibilities:

```bash
# Count mermaid code fence blocks
grep -rc '```mermaid' --include="*.md" wiki/ | grep -v ':0$'

# Find flowchart keyword usage
grep -rn '^\s*flowchart ' --include="*.md" wiki/

# Find <br> tags in mermaid labels  
grep -rn '<br>' --include="*.md" wiki/ | head -20

# Count YAML front matter files
for f in $(find wiki/ -name "*.md"); do
  head -1 "$f" | grep -q '^---$' && echo "FRONT MATTER: $f"
done

# Find parent-relative links
grep -rn '](\.\./' --include="*.md" wiki/ | wc -l

# Find VitePress container directives
grep -rn '^:::' --include="*.md" wiki/ | grep -v mermaid
```

Report the scan results before proceeding.

### Step 2: Generate the Build Script

Create `scripts/build-ado-wiki.js` — a Node.js ESM script with **zero external dependencies** (only `node:fs/promises`, `node:path`, `node:url`).

The script must apply these transformations in order:

#### a) Strip YAML Front Matter
Remove `---` delimited YAML blocks at file start. ADO renders these as visible raw text.

#### b) Convert Mermaid Blocks
Process line-by-line, apply fixes ONLY inside mermaid blocks:
- Opening fence: ` ```mermaid ` → `::: mermaid`
- Closing fence: ` ``` ` → `:::`
- `flowchart` → `graph` (preserve direction: TD, LR, TB, RL, BT)
- Strip `<br>`, `<br/>`, `<br />` variants (replace with space)
- Replace long arrows (`---->` with 4+ dashes) with `-->`

#### c) Convert Parent-Relative Source Links
Convert `[text](../../path)` to plain text. Preserve same-directory `.md` links and external URLs.

#### d) Convert VitePress Container Directives
Convert `::: tip` → `> [!TIP]`, `::: warning` → `> [!WARNING]`, `::: danger` → `> [!CAUTION]`, `::: info` → `> [!NOTE]`. Content inside containers becomes blockquoted text.

#### e) Copy Non-Markdown Assets
Copy images, diagrams, and other non-markdown files to `dist/ado-wiki/` preserving relative paths.

### Step 3: Configure the Script

The script should:
- Auto-detect the wiki source directory (`wiki/`, `wiki-site/`, or configurable via CLI arg)
- Output to `dist/ado-wiki/`
- Skip: `node_modules/`, `.vitepress/`, `.git/`, `dist/`
- Print statistics: count of each transformation type applied
- Exit with code 0 on success, 1 on error

### Step 4: Add npm Script

Add to the wiki's `package.json`:

```json
{
  "scripts": {
    "build:ado": "node scripts/build-ado-wiki.js"
  }
}
```

### Step 5: Verify

After generating the script, run it and verify:
1. File count matches source (minus skipped dirs)
2. Zero ` ```mermaid ` fences remaining
3. Zero `flowchart` keywords in mermaid blocks
4. No YAML front matter in output
5. Parent-relative links converted to plain text
6. Same-directory `.md` links preserved
7. Directory structure preserved

## ADO Wiki Incompatibility Reference

### CRITICAL (Must Fix)

| Issue | GFM/VitePress | ADO Wiki | Transform |
|-------|--------------|----------|-----------|
| Mermaid fences | ` ```mermaid ` | `::: mermaid` | Convert fences |
| `flowchart` keyword | `flowchart TD` | `graph TD` | Replace keyword |
| `<br>` in Mermaid | `Node[A<br>B]` | Breaks diagram | Strip (→ space) |
| Long arrows | `---->` | Not supported | → `-->` |
| YAML front matter | `---`...`---` | Raw visible text | Strip |
| Parent source links | `[t](../../src)` | Broken path | → plain text |
| Container directives | `::: tip` | Not supported | → `> [!TIP]` |

### Compatible As-Is (No Action Needed)

- ✅ Tables, blockquotes, horizontal rules, emoji
- ✅ Fenced code blocks, relative `.md` links, external URLs
- ✅ Bold, italic, strikethrough, inline code, lists, headings

### ADO Mermaid Supported Types

✅ `sequenceDiagram`, `gantt`, `graph`, `classDiagram`, `stateDiagram`, `journey`, `pie`, `erDiagram`, `gitGraph`, `timeline`
❌ `flowchart` (use `graph`), `mindmap`, `sankey`, `quadrantChart`, `xychart`, `block`

$ARGUMENTS
