# AI Workflow Tools

This repository serves as a centralized hub for personal AI agent workflows, tools, and configurations. It organizes resources for various AI assistants to enhance productivity and automation.

## Structure

- **`commands/`**: Agent or provider-specific command specifications (e.g., `commands/gemini/`).
- **`extensions/`**: Custom extensions (geminiCLI spec) to expand agent capabilities.
- **`skills/`**: Specialized skill definitions for agents (following the [Agent Skills](https://agentskills.io) open standard).
- **`prompts/`**: A collection of reusable system and task-specific prompts.

## Skills

### skill-creator

Create new Agent Skills conforming to the open Agent Skills standard. This skill helps you design and scaffold skills for AI agents, handling metadata, instructions, references, scripts, and assets.

**Features:**
- Intelligent skill creation (simple skills use defaults, complex skills prompt for clarification)
- Full Agent Skills specification support with progressive disclosure
- Cross-provider compatibility (Gemini CLI, Claude Code, OpenAI Codex)
- Installation instructions for all major providers

**Location:** `skills/skill-creator/`

**Installation:**

| Provider | Command |
|----------|---------|
| Gemini CLI | `cp -r skills/skill-creator ~/.gemini/skills/` |
| Claude Code | `cp -r skills/skill-creator ~/.claude/skills/` |
| OpenAI Codex | `cp -r skills/skill-creator ~/.codex/skills/` |

## Usage

Refer to `AGENTS.md` for detailed operational context and guidelines on how AI agents should interact with this repository.