# AI Workflow Tools

This repository serves as a centralized hub for personal AI agent workflows, tools, and configurations. It organizes resources for various AI assistants to enhance productivity and automation.

## Structure

- **`commands/`**: Agent or provider-specific command specifications (e.g., `commands/gemini/`).
- **`extensions/`**: Custom extensions (geminiCLI spec) to expand agent capabilities.
- **`skills/`**: specialized skill definitions for agents.
  - **`skills/skill-creator/`**: A meta-skill that helps an agent author new, spec-compliant Agent Skills (with progressive disclosure) and provides Gemini/Claude/Codex installation guidance.
- **`prompts/`**: A collection of reusable system and task-specific prompts.

## Usage

Refer to `AGENTS.md` for detailed operational context and guidelines on how AI agents should interact with this repository.

## Available Commands

### Gemini
- **Workflow**
  - `compare-PRs`: Compares multiple conflicting PRs for the same feature and outputs a decision report.




