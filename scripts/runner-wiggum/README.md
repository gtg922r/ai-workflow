# Ralph Wiggum Agent Runner

A terminal-based autonomous AI agent runner that implements the "Ralph Wiggum" loop pattern for AI-driven development.

## What is Ralph Wiggum?

The "Ralph Wiggum" approach (named after the Simpsons character) is a technique for running AI coding agents in an autonomous loop until development tasks are complete. The key insight is:

> **Each iteration starts fresh, reads the same on-disk state, and commits work for one story at a time.**

This approach is "deterministically bad in an undeterministic world" — meaning the technique produces consistent, correctable outputs that can be tuned over time.

## Features

- **Beautiful TUI** - Modern terminal interface built with Textual
- **Multi-agent support** - Works with Claude Code CLI and Cursor CLI
- **PRD-driven** - Define user stories in a simple JSON format
- **Progress tracking** - Session stats, run history, and cost tracking
- **Sandboxed execution** - Agents run with restricted permissions
- **Easy restart** - Continue where you left off

## Quick Start

### 1. Install `uv` (if you haven't already)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install an AI Agent CLI

**Claude Code CLI** (recommended):
```bash
npm install -g @anthropic-ai/claude-code
```

**Cursor CLI**:
```bash
# Install Cursor, which includes the `agent` CLI
# See: https://cursor.com/docs/cli/using
curl https://cursor.com/install -fsS | bash
```

### 3. Set Up Your Project

Copy the runner to your project:
```bash
cp -r /path/to/runner-wiggum /your/project/scripts/
```

Create your PRD file (`prd.json`):
```json
{
  "projectName": "My Project",
  "branchName": "feature/my-feature",
  "userStories": [
    {
      "id": "story-1",
      "title": "Implement user authentication",
      "description": "Add login and registration functionality",
      "acceptanceCriteria": [
        "Users can register with email and password",
        "Users can log in with valid credentials",
        "Failed logins show appropriate error messages"
      ],
      "passes": false
    }
  ]
}
```

Optionally customize `prompt.md` and `AGENTS.md` for your project.

### 4. Run the TUI

From your project directory, run:

```bash
uv run scripts/runner-wiggum/ralph.py
```

That's it! `uv` automatically handles the virtual environment and dependencies.

Or specify a different project path:

```bash
uv run scripts/runner-wiggum/ralph.py --path /path/to/your/project
```

**Alternative:** Make the script directly executable:

```bash
chmod +x scripts/runner-wiggum/ralph.py
./scripts/runner-wiggum/ralph.py
```

## TUI Controls

| Key | Action |
|-----|--------|
| `s` | Start the agent loop |
| `p` | Pause after current iteration |
| `r` | Restart the session |
| `c` | Open configuration |
| `q` | Quit |

## Configuration

The TUI allows you to configure:

- **Agent** - Choose between Claude Code or Cursor
- **Max Iterations** - Limit how many iterations to run
- **Timeout** - Maximum time per iteration (seconds)
- **Allow Network** - Enable/disable network access for the agent
- **Auto-restart** - Automatically restart when PRD is complete

## File Structure

```
your-project/
├── prd.json           # Your user stories
├── prompt.md          # Custom prompt template (optional)
├── AGENTS.md          # Project context for agents (optional)
├── progress.txt       # Append-only learnings (auto-generated)
├── session.txt        # Current session state (auto-generated)
└── scripts/
    └── runner-wiggum/
        ├── ralph.py         # TUI entry point
        ├── core/            # Core runner logic
        ├── agents/          # Agent backends
        ├── templates/       # Example templates
        └── requirements.txt
```

## How It Works

1. **Load PRD** - Read user stories from `prd.json`
2. **Find next story** - Get the first story where `passes: false`
3. **Build prompt** - Combine template with story context and progress history
4. **Run agent** - Execute the AI agent in headless mode
5. **Parse output** - Look for completion signal (`<promise>COMPLETE</promise>`)
6. **Update state** - Mark story complete, save progress
7. **Repeat** - Continue until all stories pass or max iterations reached

## PRD Format

```json
{
  "projectName": "Project name for display",
  "branchName": "Git branch name (for reference)",
  "userStories": [
    {
      "id": "unique-id",
      "title": "Short title",
      "description": "Detailed description of the story",
      "acceptanceCriteria": [
        "Criterion 1",
        "Criterion 2"
      ],
      "passes": false
    }
  ]
}
```

### Story Best Practices

1. **Keep stories small** - Should be completable in one context window
2. **Be specific** - Clear acceptance criteria the agent can verify
3. **Independent** - Stories should be independently verifiable
4. **Test-driven** - Include testing requirements in criteria

## Prompt Template

The default prompt template uses these placeholders:

- `{{PRD_STATUS}}` - Current PRD completion status
- `{{STORY}}` - Current story details
- `{{PROGRESS}}` - Contents of progress.txt

Customize `prompt.md` in your project root to change agent behavior.

## Agent Configuration

### Claude Code CLI

The runner uses these flags by default:
- `-p` - Print/headless mode
- `--dangerously-skip-permissions` - Auto-approve all actions
- `--allowedTools` - Restrict to safe tools (Edit, Write, Read, Bash for git/npm/python)

### Cursor CLI

As of [January 2026](https://cursor.com/changelog/cli-jan-08-2026), the Cursor CLI uses the `agent` command:

- `-p` or `--print` - Non-interactive mode (has full write access automatically)
- `--output-format text|json` - Control output format for parsing
- `--resume [thread id]` - Continue from previous conversation
- `agent ls` - List previous conversations
- `agent resume` - Resume most recent conversation

The CLI automatically reads `AGENTS.md` and `CLAUDE.md` from project root and supports MCP via `mcp.json`.

## Tips for Effective Ralph Loops

1. **Start with a good AGENTS.md** - Give the agent project context
2. **Write comprehensive tests** - Agents will exploit weak tests
3. **Keep code clean** - Prevent "meaning decay" over iterations
4. **Review progress.txt** - Learn from what the agent discovers
5. **Tune the prompt** - Add signs for common failure modes

## References

- [Geoffrey Huntley's Ralph article](https://ghuntley.com/ralph/)
- [snarktank/ralph implementation](https://github.com/snarktank/ralph)
- [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code)
- [Cursor CLI documentation](https://docs.cursor.com)

## License

MIT

