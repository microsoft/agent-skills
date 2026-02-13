# 🌊 Deep Wiki

**AI-Powered Wiki Generator for Code Repositories — GitHub Copilot CLI Plugin**

Generate comprehensive, structured, Mermaid-rich documentation wikis for any codebase — with dark-mode VitePress sites, onboarding guides, and deep research capabilities. Distilled from the prompt architectures of [OpenDeepWiki](https://github.com/AIDotNet/OpenDeepWiki) and [deepwiki-open](https://github.com/AsyncFuncAI/deepwiki-open).

## Installation

### From a marketplace

```bash
# Inside Copilot CLI, run these slash commands:
/plugin marketplace add microsoft/skills
/plugin install deep-wiki@skills
```

```bash
copilot --plugin-dir ./deep-wiki
```

## Commands

| Command | Description |
|---------|-------------|
| `/deep-wiki:generate` | Generate a complete wiki — catalogue + all pages + onboarding guides + VitePress site |
| `/deep-wiki:crisp` | Fast wiki generation — concise, parallelized, rate-limit-friendly. 5–8 pages, no build step |
| `/deep-wiki:catalogue` | Generate only the hierarchical wiki structure as JSON |
| `/deep-wiki:page <topic>` | Generate a single wiki page with dark-mode Mermaid diagrams |
| `/deep-wiki:changelog` | Generate a structured changelog from git commits |
| `/deep-wiki:research <topic>` | Multi-turn deep investigation with evidence-based analysis |
| `/deep-wiki:ask <question>` | Ask a question about the repository |
| `/deep-wiki:onboard` | Generate 4 audience-tailored onboarding guides (Contributor, Staff Engineer, Executive, PM) |
| `/deep-wiki:agents` | Generate `AGENTS.md` files for pertinent folders (only where missing) |
| `/deep-wiki:llms` | Generate `llms.txt` and `llms-full.txt` for LLM-friendly project access |
| `/deep-wiki:ado` | Generate a Node.js script to convert wiki to Azure DevOps Wiki-compatible format |
| `/deep-wiki:build` | Package generated wiki as a VitePress site with dark theme |
| `/deep-wiki:deploy` | Generate GitHub Actions workflow to deploy wiki to GitHub Pages |

## Agents

| Agent | Description |
|-------|-------------|
| `wiki-architect` | Analyzes repos, generates structured catalogues + onboarding architecture |
| `wiki-writer` | Generates pages with dark-mode Mermaid diagrams and deep citations |
| `wiki-researcher` | Deep research with zero tolerance for shallow analysis — evidence-first |

View available agents: `/agents`

## Skills (Auto-Invoked)

| Skill | Triggers When |
|-------|---------------|
| `wiki-architect` | User asks to create a wiki, document a repo, or map a codebase |
| `wiki-page-writer` | User asks to document a component or generate a technical deep-dive |
| `wiki-changelog` | User asks about recent changes or wants a changelog |
| `wiki-researcher` | User wants in-depth investigation across multiple files |
| `wiki-qa` | User asks a question about how something works in the repo |
| `wiki-vitepress` | User asks to build a site or package wiki as VitePress |
| `wiki-onboarding` | User asks for onboarding docs or getting-started guides |
| `wiki-agents-md` | User asks to generate AGENTS.md files for coding agent context |
| `wiki-llms-txt` | User asks to generate llms.txt or make docs LLM-friendly |
| `wiki-ado-convert` | User asks to export wiki for Azure DevOps or convert Mermaid/markdown for ADO |

## Quick Start

```bash
# Install the plugin (slash command inside Copilot CLI)
/plugin install deep-wiki@skills

# Generate a full wiki with onboarding guides and VitePress site
/deep-wiki:generate

# Fast wiki — concise, parallelized, avoids rate limits
/deep-wiki:crisp

# Just the structure
/deep-wiki:catalogue

# Single page with dark-mode diagrams
/deep-wiki:page Authentication System

# Generate onboarding guides
/deep-wiki:onboard

# Build VitePress dark-theme site
/deep-wiki:build

# Research a topic (evidence-based, 5 iterations)
/deep-wiki:research How does the caching layer work?

# Ask a question
/deep-wiki:ask What database migrations exist?

# Generate llms.txt for LLM-friendly access
/deep-wiki:llms

# Deploy wiki to GitHub Pages (optional)
/deep-wiki:deploy
```

## How It Works

```
Repository → Scan → Catalogue (JSON TOC) → Per-Section Pages → Assembled Wiki
                                                    ↓
                                         Mermaid Diagrams + Citations
                                                    ↓
                                         Onboarding Guides (Contributor, Staff Engineer, Executive, PM)
                                                    ↓
                                         VitePress Site (Dark Theme + Click-to-Zoom)
                                                    ↓
                                         AGENTS.md Files (Only If Missing)
                                                    ↓
                                         llms.txt + llms-full.txt (LLM-friendly)
                                                    ↓
                                         GitHub Pages Deployment (Optional)
```

| Step | Component | What It Does |
|------|-----------|-------------|
| 1 | `wiki-architect` | Analyzes repo → hierarchical JSON table of contents |
| 2 | `wiki-page-writer` | For each TOC entry → rich Markdown with dark-mode Mermaid + citations |
| 3 | `wiki-onboarding` | Generates 4 audience-tailored onboarding guides in `onboarding/` folder |
| 4 | `wiki-vitepress` | Packages all pages into a VitePress dark-theme static site |
| 5 | `wiki-changelog` | Git commits → categorized changelog |
| 6 | `wiki-researcher` | Multi-turn investigation with evidence standard |
| 7 | `wiki-qa` | Q&A grounded in actual source code |
| 8 | `wiki-agents-md` | Generates `AGENTS.md` files for pertinent folders (only if missing) |
| 9 | `wiki-llms-txt` | Generates `llms.txt` + `llms-full.txt` for LLM-friendly access |
| 10 | `wiki-ado-convert` | Converts VitePress wiki to Azure DevOps Wiki-compatible format |

## Design Principles

1. **Source-linked citations**: Before any task, resolve the source repo URL (or confirm local). All citations use `[file:line](REPO_URL/blob/BRANCH/file#Lline)` for remote repos, `(file:line)` for local
2. **Structure-first**: Always generate a TOC/catalogue before page content
3. **Evidence-based**: Every claim cites `file_path:line_number` with clickable links — no hand-waving
4. **Diagram-rich**: Minimum 3–5 dark-mode Mermaid diagrams per page using multiple diagram types, with click-to-zoom and `<!-- Sources: ... -->` comment blocks. More diagrams = better — use them liberally for architecture, flows, state, data models, and decisions.
5. **Table-driven**: Prefer tables over prose for any structured information. Use summary tables, comparison tables, and always include a "Source" column with citations.
6. **Progressive disclosure**: Big picture first, then drill into details. Every section starts with a TL;DR.
7. **Hierarchical depth**: Max 4 levels for component-level granularity
8. **Systems thinking**: Architecture → Subsystems → Components → Methods
9. **Never invent**: All content derived from actual code — trace real implementations
10. **Dark-mode native**: All output designed for dark-theme rendering (VitePress)
11. **Depth before breadth**: Trace actual code paths, never guess from file names
12. **Agent-discoverable**: Output placed at standard paths (`llms.txt` at repo root, `AGENTS.md` in key folders) so coding agents and MCP tools find documentation automatically

## Agent & MCP Integration

The generated output is designed to be discoverable by coding agents using the [GitHub MCP Server](https://github.com/github/github-mcp-server) or any MCP-compatible tool:

| File | Path | Discovery Method |
|------|------|-----------------|
| `llms.txt` | Repo root (`./llms.txt`) | Standard llms.txt spec location — agents check here first via `get_file_contents` |
| `llms-full.txt` | `wiki/llms-full.txt` | Full inlined docs — agents load this for comprehensive context |
| `AGENTS.md` | Root + key folders | Standard agent instructions file — references wiki docs in Documentation section |
| Wiki pages | `wiki/**/*.md` | Searchable via `search_code` — all pages contain source-linked citations |
| `llms.txt` | `wiki/.vitepress/public/` | Served at `/llms.txt` on deployed VitePress site |

**How it works with GitHub MCP:**

1. Agent calls `get_file_contents` on `llms.txt` → gets project summary + links to all wiki pages
2. Agent calls `get_file_contents` on specific wiki pages → gets full documentation with source citations
3. Agent calls `search_code` with patterns → finds relevant wiki sections across the repository
4. Agent reads `AGENTS.md` → Documentation section points to wiki and onboarding guides

## Plugin Structure

```
deep-wiki/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest (name, version, description)
├── commands/                 # Slash commands (/deep-wiki:*)
│   ├── generate.md          # Full wiki generation pipeline
│   ├── crisp.md             # Fast, concise wiki (rate-limit-friendly)
│   ├── catalogue.md         # Wiki structure as JSON
│   ├── page.md              # Single page with dark-mode diagrams
│   ├── changelog.md         # Git-based changelog
│   ├── research.md          # 5-iteration deep research
│   ├── ask.md               # Q&A about the repo
│   ├── onboard.md           # Onboarding guide generation
│   ├── agents.md            # AGENTS.md generation (only if missing)
│   ├── llms.md              # llms.txt generation for LLM-friendly access
│   ├── deploy.md            # GitHub Pages deployment workflow generation
│   ├── ado.md               # Azure DevOps Wiki export script generation
│   └── build.md             # VitePress site packaging
├── skills/                   # Auto-invoked based on context
│   ├── wiki-architect/
│   │   └── SKILL.md
│   ├── wiki-page-writer/
│   │   └── SKILL.md
│   ├── wiki-changelog/
│   │   └── SKILL.md
│   ├── wiki-researcher/
│   │   └── SKILL.md
│   ├── wiki-qa/
│   │   └── SKILL.md
│   ├── wiki-vitepress/
│   │   └── SKILL.md         # VitePress packaging + dark-mode Mermaid
│   ├── wiki-onboarding/
│   │   └── SKILL.md         # Onboarding guide generation
│   ├── wiki-agents-md/
│   │   └── SKILL.md         # AGENTS.md generation for coding agents
│   ├── wiki-llms-txt/
│   │   └── SKILL.md         # llms.txt generation for LLM-friendly access
│   └── wiki-ado-convert/
│       └── SKILL.md         # Azure DevOps Wiki conversion
├── agents/                   # Custom agents (visible in /agents)
│   ├── wiki-architect.md
│   ├── wiki-writer.md
│   └── wiki-researcher.md
└── README.md
```

## License

MIT
