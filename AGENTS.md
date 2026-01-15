# Agent Operational Context

## Purpose
This repository houses tools, skills, and configurations designed to support personal AI workflows. It is structured to be provider-agnostic where possible, with specific overrides or specs in designated folders.

## Operational Guidelines
- **Structure Adherence**: Maintain the established directory structure.
    - Place provider-specific CLI commands in `commands/<provider>/`.
    - Google gemini-cli spec Extensions go in `extensions`
    - Generic Agent Skills go in `skills/`.
    - Standalone scripts and runners go in `scripts/`.
    - Reusable prompts go in `prompts/`.
- **Documentation Updating**: Whenever new content is added, be sure to update README.md
  - The README.md table of contents should contain a brief, informative description of all content
- **Commits**: Use [Conventional Commits](https://www.conventionalcommits.org/) for all git commits.

## Navigation
- **`commands/`**: Look here for specific tool definitions.
- **`extensions/`**: Implementation of agent extensions.
- **`scripts/`**: Standalone tools and runners (e.g., runner-ralph).
- **`prompts/`**: Source of truth for system prompts and templates.
