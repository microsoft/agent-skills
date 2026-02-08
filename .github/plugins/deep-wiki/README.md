# 🌊 Deep Wiki

**AI-Powered Wiki Generator for Code Repositories — GitHub Copilot CLI Plugin**

Generate comprehensive, structured, Mermaid-rich documentation wikis for any codebase. Distilled from the prompt architectures of [OpenDeepWiki](https://github.com/AIDotNet/OpenDeepWiki) and [deepwiki-open](https://github.com/AsyncFuncAI/deepwiki-open).

## Installation

### From a marketplace

```bash
copilot marketplace add microsoft/skills
copilot plugin install deep-wiki@skills
```

### Local development

```bash
copilot --plugin-dir ./deep-wiki
```

## Commands

| Command | Description |
|---------|-------------|
| `/deep-wiki:generate` | Generate a complete wiki — catalogue + all pages |
| `/deep-wiki:catalogue` | Generate only the hierarchical wiki structure as JSON |
| `/deep-wiki:page <topic>` | Generate a single wiki page for a topic |
| `/deep-wiki:changelog` | Generate a structured changelog from git commits |
| `/deep-wiki:research <topic>` | Multi-turn deep investigation of a specific topic |
| `/deep-wiki:ask <question>` | Ask a question about the repository |

## Agents

| Agent | Description |
|-------|-------------|
| `wiki-architect` | Analyzes repos and generates structured wiki catalogues |
| `wiki-writer` | Generates documentation pages with Mermaid diagrams |
| `wiki-researcher` | Multi-turn deep research on specific codebase topics |

View available agents: `/agents`

## Skills (Auto-Invoked)

| Skill | Triggers When |
|-------|---------------|
| `wiki-architect` | User asks to create a wiki, document a repo, or map a codebase |
| `wiki-page-writer` | User asks to document a component or generate a technical deep-dive |
| `wiki-changelog` | User asks about recent changes or wants a changelog |
| `wiki-researcher` | User wants in-depth investigation across multiple files |
| `wiki-qa` | User asks a question about how something works in the repo |

## Quick Start

```bash
# Install the plugin
copilot plugin install deep-wiki@skills

# Generate a full wiki
/deep-wiki:generate

# Just the structure
/deep-wiki:catalogue

# Single page
/deep-wiki:page Authentication System

# Research a topic
/deep-wiki:research How does the caching layer work?

# Ask a question
/deep-wiki:ask What database migrations exist?
```

## How It Works

```
Repository → Scan → Catalogue (JSON TOC) → Per-Section Pages → Assembled Wiki
                                                    ↓
                                         Mermaid Diagrams + Citations
```

| Step | Component | What It Does |
|------|-----------|-------------|
| 1 | `wiki-architect` | Analyzes repo → hierarchical JSON table of contents |
| 2 | `wiki-page-writer` | For each TOC entry → rich Markdown with Mermaid + citations |
| 3 | `wiki-changelog` | Git commits → categorized changelog |
| 4 | `wiki-researcher` | Multi-turn investigation of specific topics |
| 5 | `wiki-qa` | Q&A grounded in actual source code |

## Design Principles

1. **Structure-first**: Always generate a TOC/catalogue before page content
2. **Evidence-based**: Every claim cites `file_path:line_number`
3. **Diagram-rich**: Minimum 2 Mermaid diagrams per page
4. **Hierarchical depth**: Max 4 levels for component-level granularity
5. **Systems thinking**: Architecture → Subsystems → Components → Methods
6. **Never invent**: All content derived from actual code — no guessing

## Plugin Structure

```
deep-wiki/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest (name, version, description)
├── commands/                 # Slash commands (/deep-wiki:*)
│   ├── generate.md
│   ├── catalogue.md
│   ├── page.md
│   ├── changelog.md
│   ├── research.md
│   └── ask.md
├── skills/                   # Auto-invoked based on context
│   ├── wiki-architect/
│   │   └── SKILL.md
│   ├── wiki-page-writer/
│   │   └── SKILL.md
│   ├── wiki-changelog/
│   │   └── SKILL.md
│   ├── wiki-researcher/
│   │   └── SKILL.md
│   └── wiki-qa/
│       └── SKILL.md
├── agents/                   # Custom agents (visible in /agents)
│   ├── wiki-architect.md
│   ├── wiki-writer.md
│   └── wiki-researcher.md
└── README.md
```

## License

MIT
