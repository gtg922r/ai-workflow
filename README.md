# AI Workflow Tools

This repository serves as a centralized hub for personal AI agent workflows, tools, and configurations. It organizes resources for various AI assistants to enhance productivity and automation.

## Quick Install

Install components directly via NPX:

```bash
# Recommended (works reliably across npm/npx versions)
npx --yes --package github:gtg922r/ai-workflow ai-workflow
```

If you prefer the shorter form, some environments also support:

```bash
npx github:gtg922r/ai-workflow
```

### Requirements

- **Node.js**: `>= 18` (see `package.json#engines`)
- **Git**: available on your PATH (`git --version`)
- **Network access**: ability to fetch from GitHub

The interactive installer will guide you through:
- Selecting a target agent (Gemini CLI, Claude Code, or OpenAI Codex)
- Choosing installation scope (global user profile or local project)
- Picking which commands, skills, and scripts to install

## Structure

- **`commands/`**: Agent or provider-specific command specifications (e.g., `commands/gemini/`).
- **`extensions/`**: Custom extensions (geminiCLI spec) to expand agent capabilities.
- **`scripts/`**: Standalone tools and runners for AI workflows.
- **`scripts/runner-ralph/`**: A TUI-based autonomous AI agent runner implementing the "Runner Ralph" loop pattern. Supports Claude Code CLI and Cursor CLI for PRD-driven development, including optional per-story feature specs.
- **`skills/`**: Specialized skill definitions for agents.
  - **`skills/command-creator/`**: Creates and manages custom commands (`.toml`) for the Gemini CLI, supporting reusable prompts, context-aware arguments, and dynamic shell execution.
  - **`skills/skill-creator/`**: A meta-skill that helps an agent author new, spec-compliant Agent Skills (with progressive disclosure) and provides Gemini/Claude/Codex installation guidance.
  - **`skills/runner-ralph/`**: Instructions for configuring and running the Runner Ralph autonomous development loop. Use when the user wants to start an automated coding session, configure a PRD, or understand how to use the runner script.
- **`prompts/`**: A collection of reusable system and task-specific prompts.

## Manual Usage

Refer to `AGENTS.md` for detailed operational context and guidelines on how AI agents should interact with this repository.

## Available Commands

### Gemini
  - `workflow-doctor`: Check for common workflow issues and suggest fixes.
  - `create-pr`: Create a pull request from the current branch.
  - `compare-prs`: Compare two pull requests to see what has changed.




