---
description: Generate a fast, concise wiki for the current repository — optimized for speed, minimal tool calls, and avoiding rate limits. Produces a complete VitePress site without running builds.
---

# Deep Wiki: Crisp (Fast Wiki Generation)

You are a Technical Documentation Architect. Generate a concise, high-signal wiki for this repository as fast as possible. This is the speed-optimized alternative to `/deep-wiki:generate`.

## Design Philosophy

**Speed over depth. Signal over exhaustiveness. Ship over perfection.**

- Scan structure and key files, don't trace every call chain
- Generate fewer, denser pages (5–8 total, not 15–20)
- 1–2 diagrams per page (not 3–5)
- Parallelize everything you can
- Minimize tool calls — batch reads, scan directories once
- Do NOT run `npm install` or `npm run build` — the deploy workflow handles that
- Still produces a fully working VitePress site when built

## Process

Execute ALL steps. Steps 1–2 are sequential. Steps 3–7 can be parallelized.

### Step 1: Source Repository Resolution

1. Run `git remote get-url origin` to detect remote URL
2. Ask the user if not already provided: _"Source repo URL? (or 'local' for local-only citations)"_
3. Determine branch: `git rev-parse --abbrev-ref HEAD`
4. Store citation format:
   - **Remote**: `[file:line](REPO_URL/blob/BRANCH/file#Lline)`
   - **Local**: `(file:line)`

### Step 2: Quick Repository Scan (ONE PASS)

Scan the repo in a single pass — do NOT re-read files:

```bash
# Get structure + key files in one shot
find . -maxdepth 3 -type f \( -name "*.md" -o -name "package.json" -o -name "pyproject.toml" -o -name "Cargo.toml" -o -name "*.csproj" -o -name "go.mod" -o -name "Dockerfile" -o -name "*.yml" -o -name "*.yaml" \) | head -50
```

From this single scan, identify:
- Language and framework (from config files)
- Entry points (main/index/app files)
- Project structure (top-level directories)
- Key technologies
- Test setup (if any)

**Read at most 10–15 source files total.** Pick the most important ones: entry point, main config, 2–3 core modules, README.

### Steps 3–7: PARALLELIZE THESE

Generate all of the following in parallel (or as fast as possible). Do NOT wait for one to finish before starting the next.

---

### Step 3: Generate Wiki Pages (5–8 pages max)

Create these pages in `wiki/`:

| Page | File | Content |
|------|------|---------|
| **Overview** | `index.md` | Quick Start commands, architecture diagram, documentation map table, tech stack table. Developer-focused, NO hero layout. |
| **Architecture** | `01-architecture/overview.md` | System diagram (1 `graph LR`), component table, key design decisions |
| **Getting Started** | `02-getting-started/setup.md` | Prerequisites, install, run, test — actual commands only |
| **Core Modules** | `03-core/modules.md` | Table of all modules with purpose + key file + source. 1 diagram showing relationships |
| **API / Interface** | `04-api/endpoints.md` | Table of routes/APIs/CLI commands. Only if applicable — skip for libraries with no API |
| **Data Layer** | `05-data/models.md` | Data models, storage, schema. Only if applicable — skip if no DB/storage |
| **Configuration** | `06-config/settings.md` | Config options table, environment variables, deployment. Merge with another page if small |
| **Contributing** | `07-contributing/guide.md` | Dev setup, testing, PR process. Derive from CONTRIBUTING.md or conventions |

**Skip pages that don't apply.** A 5-page wiki for a small project is fine. Don't pad.

**Per-page rules:**
- VitePress frontmatter: `title` and `description`
- 1–2 Mermaid diagrams max (dark-mode: fills `#2d333b`, borders `#6d5dfc`, text `#e6edf3`)
- `<!-- Sources: file:line, file:line -->` after each diagram
- At least 3 source file citations per page
- Cross-reference other wiki pages with relative links where relevant
- End with a "Related Pages" table if there are connections
- Tables over prose — always

### Step 4: Generate Onboarding (Contributor Guide ONLY)

Generate ONE onboarding guide: `wiki/onboarding/contributor-guide.md`

- 500–800 lines (not 1000–2500)
- Part I: Tech stack overview with key concepts
- Part II: Codebase walkthrough — directory structure, entry points, key files
- Part III: Getting productive — setup, running, testing, first PR
- Include 2–3 diagrams, a glossary, and a key files table

Also create `wiki/onboarding/index.md` hub page linking to the contributor guide.

### Step 5: Scaffold VitePress Site

Create the full VitePress scaffolding in `wiki/`:

**Files to create:**
- `wiki/package.json` — VitePress + mermaid + medium-zoom deps
- `wiki/.gitignore` — `node_modules/`, `.vitepress/cache/`, `.vitepress/dist/`
- `wiki/.vitepress/config.mts` — Dark theme, Mermaid config, dynamic sidebar, `ignoreDeadLinks: true`
- `wiki/.vitepress/theme/index.ts` — Medium-zoom for images, Mermaid click-to-zoom modal, focus mode toggle
- `wiki/.vitepress/theme/custom.css` — Full dark theme, Mermaid overrides, zoom CSS, focus mode CSS
- `wiki/.vitepress/public/logo.svg` — Brand logo

**Follow `/deep-wiki:build` for exact config, theme, and CSS specifications.** The key difference: do NOT run `npm install` or `npm run build` — just create the files. The GitHub Actions workflow will handle builds.

**Base path**: Check if this is a project site (needs `base: '/repo-name/'`) or user site (default `base: '/'`).

### Step 6: Generate AGENTS.md + llms.txt

**AGENTS.md** (only if they don't already exist):
- `./AGENTS.md` — Root project instructions (build, test, structure, conventions, boundaries)
- `./CLAUDE.md` — Companion pointer to AGENTS.md
- `wiki/AGENTS.md` — Wiki folder instructions (VitePress commands, content conventions)
- `wiki/CLAUDE.md` — Companion pointer

**llms.txt** (always generate):
- `./llms.txt` — Root discovery (links into wiki/)
- `wiki/llms.txt` — Wiki-relative links
- `wiki/llms-full.txt` — Full page content inlined in `<doc>` blocks
- `wiki/.vitepress/public/llms.txt` — Served at `/llms.txt` on deployed site

Follow `/deep-wiki:llms` and `/deep-wiki:agents` specs but keep content proportional to the crisp wiki size.

### Step 7: Generate Deploy Workflow (only if missing)

Check for existing workflows first:
```bash
ls .github/workflows/deploy-wiki.yml 2>/dev/null
grep -rl "deploy-pages\|pages-artifact" .github/workflows/ 2>/dev/null
```

If no pages workflow exists, create `.github/workflows/deploy-wiki.yml` per `/deep-wiki:deploy` spec.

Also generate `wiki/package-lock.json` is NOT needed — the workflow uses `npm install` (not `npm ci`) for crisp wikis. Update the workflow to use `npm install` instead of `npm ci`:

```yaml
      - name: Install dependencies
        run: npm install
        working-directory: wiki
```

---

## Post-Generation Report

After all steps complete, output:

```
## Crisp Wiki Generated ✅

### Pages Created
- wiki/index.md — Landing page
- wiki/01-architecture/overview.md — System architecture
- wiki/02-getting-started/setup.md — Setup & installation
- ... (list all)

### Infrastructure
- wiki/package.json — VitePress project
- wiki/.vitepress/config.mts — Site config
- wiki/.vitepress/theme/ — Dark theme + zoom
- wiki/AGENTS.md — Agent instructions
- wiki/llms.txt — LLM-friendly summary
- .github/workflows/deploy-wiki.yml — GitHub Pages deployment

### What You Need To Do

> ⚠️ GitHub Pages requires manual enablement.

1. **Commit everything:**
   ```bash
   git add wiki/ .github/workflows/ llms.txt AGENTS.md CLAUDE.md
   git commit -m "docs: add crisp wiki with VitePress site"
   git push
   ```

2. **Enable GitHub Pages:**
   - Go to **Settings → Pages → Source → GitHub Actions**
   - Without this, the workflow runs but the site won't publish

3. **Preview locally (optional):**
   ```bash
   cd wiki && npm install && npm run dev
   ```

### Crisp vs Full Wiki
To expand this wiki later with deeper analysis, onboarding guides for all audiences, and more detailed pages, run `/deep-wiki:generate`.
```

## Rate Limit Awareness

This command is designed to minimize API calls and avoid rate limits:

- **Single-pass scanning** — read the repo structure once, don't re-scan
- **Batch file reads** — read multiple files in one tool call where possible
- **Fewer pages** — 5–8 pages vs 15–20 in full generate
- **Fewer diagrams** — 1–2 per page vs 3–5
- **One onboarding guide** — not four
- **No build step** — skip `npm install` and `npm run build` entirely
- **Parallel generation** — steps 3–7 run concurrently

## Mermaid Rules (Same as Full Wiki)

- Dark-mode colors: fills `#2d333b`, borders `#6d5dfc`, text `#e6edf3`
- Subgraph backgrounds: `#161b22`, borders `#30363d`
- Lines: `#8b949e`
- `autonumber` in all `sequenceDiagram` blocks
- `<br>` not `<br/>` in labels

## Citation Rules (Same as Full Wiki)

- Remote: `[file:line](REPO_URL/blob/BRANCH/file#Lline)`
- Local: `(file:line)`
- `<!-- Sources: ... -->` after every Mermaid diagram
- "Source" column in tables listing code artifacts

$ARGUMENTS
