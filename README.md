# AI Workflow Tools

This repository serves as a centralized hub for personal AI agent workflows, tools, and configurations. It organizes resources for various AI assistants to enhance productivity and automation.

## Quick Install

Install components directly via NPX:

```bash
npx github:ryancash/ai-workflow
```

The interactive installer will guide you through:
- Selecting a target agent (Gemini CLI, Claude Code, or OpenAI Codex)
- Choosing installation scope (global user profile or local project)
- Picking which commands, skills, and scripts to install

## Structure

- **`commands/`**: Agent or provider-specific command specifications (e.g., `commands/gemini/`).
- **`extensions/`**: Custom extensions (geminiCLI spec) to expand agent capabilities.
- **`scripts/`**: Standalone tools and runners for AI workflows.
  - **`scripts/runner-ralph/`**: A TUI-based autonomous AI agent runner implementing the "Runner Ralph" loop pattern. Supports Claude Code CLI and Cursor CLI for PRD-driven development.
- **`skills/`**: Specialized skill definitions for agents.
  - **`skills/command-creator/`**: Creates and manages custom commands (`.toml`) for the Gemini CLI, supporting reusable prompts, context-aware arguments, and dynamic shell execution.
  - **`skills/skill-creator/`**: A meta-skill that helps an agent author new, spec-compliant Agent Skills (with progressive disclosure) and provides Gemini/Claude/Codex installation guidance.
- **`prompts/`**: A collection of reusable system and task-specific prompts.

## Manual Usage

Refer to `AGENTS.md` for detailed operational context and guidelines on how AI agents should interact with this repository.

## Available Commands

### Gemini
- **Workflow**
  - `compare-prs`: Compare multiple GitHub PRs and recommend the best one.
  - `create-pr`: Create a GitHub PR for local changes, intelligently handling branch state (main vs feature branch, unpushed commits).
  - `workflow-doctor`: Diagnose and validate your AI workflow environment, checking CLIs, configs, API keys, and installed components with actionable recommendations.
- **Creative**
  - `poem`: Generate a 7-line poem about a specified topic.




