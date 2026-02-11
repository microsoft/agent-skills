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
| `/deep-wiki:catalogue` | Generate only the hierarchical wiki structure as JSON |
| `/deep-wiki:page <topic>` | Generate a single wiki page with dark-mode Mermaid diagrams |
| `/deep-wiki:changelog` | Generate a structured changelog from git commits |
| `/deep-wiki:research <topic>` | Multi-turn deep investigation with evidence-based analysis |
| `/deep-wiki:ask <question>` | Ask a question about the repository |
| `/deep-wiki:onboard` | Generate Principal-Level + Zero-to-Hero onboarding guides |
| `/deep-wiki:agents` | Generate `AGENTS.md` files for pertinent folders (only where missing) |
| `/deep-wiki:ado` | Generate a Node.js script to convert wiki to Azure DevOps Wiki-compatible format |
| `/deep-wiki:build` | Package generated wiki as a VitePress site with dark theme |

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
| `wiki-ado-convert` | User asks to export wiki for Azure DevOps or convert Mermaid/markdown for ADO |

## Quick Start

```bash
# Install the plugin (slash command inside Copilot CLI)
/plugin install deep-wiki@skills

# Generate a full wiki with onboarding guides and VitePress site
/deep-wiki:generate

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
```

## How It Works

```
Repository → Scan → Catalogue (JSON TOC) → Per-Section Pages → Assembled Wiki
                                                    ↓
                                         Mermaid Diagrams + Citations
                                                    ↓
                                         Onboarding Guides (Principal + Zero-to-Hero)
                                                    ↓
                                         VitePress Site (Dark Theme + Click-to-Zoom)
                                                    ↓
                                         AGENTS.md Files (Only If Missing)
```

| Step | Component | What It Does |
|------|-----------|-------------|
| 1 | `wiki-architect` | Analyzes repo → hierarchical JSON table of contents |
| 2 | `wiki-page-writer` | For each TOC entry → rich Markdown with dark-mode Mermaid + citations |
| 3 | `wiki-onboarding` | Generates Principal-Level + Zero-to-Hero onboarding guides |
| 4 | `wiki-vitepress` | Packages all pages into a VitePress dark-theme static site |
| 5 | `wiki-changelog` | Git commits → categorized changelog |
| 6 | `wiki-researcher` | Multi-turn investigation with evidence standard |
| 7 | `wiki-qa` | Q&A grounded in actual source code |
| 8 | `wiki-agents-md` | Generates `AGENTS.md` files for pertinent folders (only if missing) |
| 9 | `wiki-ado-convert` | Converts VitePress wiki to Azure DevOps Wiki-compatible format |

## Design Principles

1. **Structure-first**: Always generate a TOC/catalogue before page content
2. **Evidence-based**: Every claim cites `file_path:line_number` — no hand-waving
3. **Diagram-rich**: Minimum 2 dark-mode Mermaid diagrams per page with click-to-zoom
4. **Hierarchical depth**: Max 4 levels for component-level granularity
5. **Systems thinking**: Architecture → Subsystems → Components → Methods
6. **Never invent**: All content derived from actual code — trace real implementations
7. **Dark-mode native**: All output designed for dark-theme rendering (VitePress)
8. **Depth before breadth**: Trace actual code paths, never guess from file names

## Plugin Structure

```
deep-wiki/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest (name, version, description)
├── commands/                 # Slash commands (/deep-wiki:*)
│   ├── generate.md          # Full wiki generation pipeline
│   ├── catalogue.md         # Wiki structure as JSON
│   ├── page.md              # Single page with dark-mode diagrams
│   ├── changelog.md         # Git-based changelog
│   ├── research.md          # 5-iteration deep research
│   ├── ask.md               # Q&A about the repo
│   ├── onboard.md           # Onboarding guide generation
│   ├── agents.md            # AGENTS.md generation (only if missing)
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
│       └── SKILL.md         # AGENTS.md generation for coding agents
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
