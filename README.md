# AI Workflow Tools

This repository serves as a centralized hub for personal AI agent workflows, tools, and configurations. It organizes resources for various AI assistants to enhance productivity and automation.

## Structure

- **`commands/`**: Agent or provider-specific command specifications (e.g., `commands/gemini/`).
- **`extensions/`**: Custom extensions (geminiCLI spec) to expand agent capabilities.
- **`scripts/`**: Standalone tools and runners for AI workflows.
  - **`scripts/runner-wiggum/`**: A TUI-based autonomous AI agent runner implementing the "Ralph Wiggum" loop pattern. Supports Claude Code CLI and Cursor CLI for PRD-driven development.
- **`skills/`**: Specialized skill definitions for agents.
  - **`skills/command-creator/`**: Creates and manages custom commands (`.toml`) for the Gemini CLI, supporting reusable prompts, context-aware arguments, and dynamic shell execution.
  - **`skills/skill-creator/`**: A meta-skill that helps an agent author new, spec-compliant Agent Skills (with progressive disclosure) and provides Gemini/Claude/Codex installation guidance.
- **`prompts/`**: A collection of reusable system and task-specific prompts.

## Usage

Refer to `AGENTS.md` for detailed operational context and guidelines on how AI agents should interact with this repository.

## Available Commands

### Gemini
- **Workflow**
  - `compare-prs`: Compare multiple GitHub PRs and recommend the best one.




