---
name: runner-ralph
description: Instructions for configuring and running the Runner Ralph autonomous development loop. Use when the user wants to start an automated coding session, configure a PRD, or understand how to use the runner script.
---

# Runner Ralph

This skill provides instructions on how to use `scripts/runner-ralph/ralph.py`, an autonomous agent runner that implements a PRD-driven development loop.

## Purpose

Runner Ralph runs AI coding agents (Claude Code or Cursor) in a loop to complete user stories defined in a `prd.json` file. It handles:
- Git branching and merging per story
- Progress tracking and work logging
- Iterative execution until acceptance criteria are met

## 1. Prerequisites

Ensure the environment is set up:
1. **Install `uv`**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. **Install an Agent CLI**:
   - **Cursor**: `curl https://cursor.com/install -fsS | bash` (Preferred)
   - **Claude**: `npm install -g @anthropic-ai/claude-code`

## 2. Configuration: `prd.json`

The runner is driven by a `prd.json` file in the project root.

**File Format:**
```json
{
  "projectName": "My Project",
  "branchName": "feature/my-feature",
  "userStories": [
    {
      "id": "story-1",
      "title": "Implement user authentication",
      "description": "Add login and registration functionality",
      "type": "feature",
      "spec": [
        "Support password reset via email",
        "Use existing user table"
      ],
      "acceptanceCriteria": [
        "Users can register with email/password",
        "Users can log in",
        "Failed logins show error messages"
      ],
      "passes": false
    }
  ]
}
```

**Fields:**
- `type`: Optional. Can be `feature`, `bug`, `chore`, `test`. Triggers specialized prompts (e.g., `prompt_feature.md`).
- `spec`: Optional. Additional requirements or implementation notes.
- `passes`: Set to `true` by the runner when complete.

**Other Config Files:**
- `AGENTS.md`: Project context and guidelines (recommended).
- `prompt.md`: Custom system prompt template (optional).

## 3. Running Ralph

Execute the runner using `uv`.

### Interactive TUI Mode (Default)
Best for monitoring progress in real-time.

```bash
uv run scripts/runner-ralph/ralph.py
```

### Headless / Console Mode
Best for scripts or background execution.

```bash
uv run scripts/runner-ralph/ralph.py
```

### Key Flags

| Flag | Description | Example |
|------|-------------|---------|
| `--path` | Path to project root (default: current dir) | `--path /path/to/project` |
| `--agent` | Agent backend (`cursor` or `claude`) | `--agent cursor` |
| `--model` | Specific model to use | `--model claude-sonnet-4-20250514` |
| `--iterations` | Max number of iterations | `--iterations 5` |
| `--review` | Enable post-implementation code review | `--review` |
| `--no-git` | Disable git branching/commits | `--no-git` |
| `--use-main` | Branch from main instead of current branch | `--use-main` |

## 4. Workflow

When you run Ralph, it follows this cycle:

1. **Read PRD**: Finds the first incomplete story in `prd.json`.
2. **Git Setup**:
   - Ensures working directory is clean.
   - Creates a story branch: `ralph/<story-id>`.
3. **Execution**:
   - Generates a prompt combining `AGENTS.md`, `prompt.md`, `prd.json`, and current progress.
   - Runs the Agent CLI (Cursor or Claude).
   - Logs decisions and learnings to `worklogs/<story-id>.md`.
4. **Completion**:
   - Agent signals `<promise>COMPLETE</promise>`.
   - **Review (Optional)**: A "reviewer" agent critiques the code.
   - **Merge**: Commits changes and merges `ralph/<story-id>` back to the base branch.
   - **Update**: Marks story as passed in `prd.json`.
5. **Repeat**: Moves to the next story.

## 5. Troubleshooting

- **"Working directory not clean"**: Commit or stash changes before running. Ralph needs a clean slate to manage branches.
- **Agent not found**: Ensure the CLI (`agent` for Cursor, `claude` for Claude) is in your PATH.
- **Stuck loop**: Check `progress.txt` or the specific `worklogs/<story-id>.md` to see what the agent is struggling with. You may need to refine the story description or add hints to `AGENTS.md`.

## Provider Installation

### Gemini CLI
This skill is provider-agnostic but requires a compatible Agent CLI (Cursor or Claude) to perform the actual coding work.

### Claude Code
Ensure `@anthropic-ai/claude-code` is installed globally or available in the environment.

### Cursor
Ensure the Cursor CLI is installed. The command is typically `agent`.
