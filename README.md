# AI Workflow Tools

This repository serves as a centralized hub for personal AI agent workflows, tools, and configurations. It organizes resources for various AI assistants to enhance productivity and automation.

## Structure

- **`commands/`**: Agent or provider-specific command specifications (e.g., `commands/gemini/`).
- **`extensions/`**: Custom extensions (geminiCLI spec) to expand agent capabilities.
  - **`extensions/obsidian-mcp/`**: Connects Gemini CLI to your Obsidian vault via MCP, providing safe read/write access to notes with 11 tools and 6 pre-built commands.
- **`skills/`**: specialized skill definitions for agents.
  - **`skills/command-creator/`**: Creates and manages custom commands (`.toml`) for the Gemini CLI, supporting reusable prompts, context-aware arguments, and dynamic shell execution.
  - **`skills/skill-creator/`**: A meta-skill that helps an agent author new, spec-compliant Agent Skills (with progressive disclosure) and provides Gemini/Claude/Codex installation guidance.
- **`prompts/`**: A collection of reusable system and task-specific prompts.

## Usage

Refer to `AGENTS.md` for detailed operational context and guidelines on how AI agents should interact with this repository.

## Available Extensions

### Gemini CLI
- **obsidian-mcp**: Connect Gemini to your Obsidian vault for note management
  - Commands: `/obsidian:search`, `/obsidian:daily`, `/obsidian:summary`, `/obsidian:new`, `/obsidian:tag`, `/obsidian:link`
  - Tools: 11 MCP tools for file operations, search, and metadata management
  - [Documentation](extensions/obsidian-mcp/README.md)

## Available Commands

### Gemini
- **Workflow**
  - `compare-prs`: Compare multiple GitHub PRs and recommend the best one.




