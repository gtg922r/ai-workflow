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
- **Git state management** - Automatic branching, commits, and merging per story
- **Post-implementation review** - Optional reviewer phase to critique code before merging
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

That's it! `uv` automatically handles Python 3.11+, the virtual environment, and dependencies.

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
- **Review Phase** - Enable post-implementation code review before merging

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
        ├── ralph.py         # TUI/CLI entry point
        ├── core/
        │   ├── runner.py    # Main orchestration
        │   ├── controller.py # TUI controller layer
        │   ├── git.py       # Git state management
        │   ├── prd.py       # PRD parsing
        │   └── progress.py  # Progress logging
        ├── agents/          # Agent backends
        ├── templates/       # Example templates
        └── requirements.txt
```

## How It Works

1. **Load PRD** - Read user stories from `prd.json`
2. **Check git state** - Ensure working directory is clean
3. **Create branch** - Switch to `wiggum/{story-id}` branch
4. **Build prompt** - Combine template with story context and progress history
5. **Run agent** - Execute the AI agent in headless mode
6. **Parse output** - Look for completion signal (`<promise>COMPLETE</promise>`)
7. **Review phase** (optional) - Run a reviewer pass to critique the implementation
8. **Commit & merge** - Stage all changes, commit with story title, merge to main
9. **Update state** - Mark story complete, save progress
10. **Repeat** - Continue until all stories pass or max iterations reached

## Git State Management

The runner automatically manages git branches to keep each story as an atomic, safe unit of work:

### Branch Workflow

1. **Pre-flight check** - Verifies working directory is clean before starting
2. **Story branches** - Creates `wiggum/{story-id}` branch for each story
3. **Automatic commits** - On story completion, stages all changes and commits with title
4. **Merge to main** - Merges completed story branch back to main, deletes branch
5. **Failure recovery** - Offers to hard reset branch on failure/abort

### CLI Options

```bash
# Disable git management entirely
uv run ralph.py --no-git

# Use a different main branch name
uv run ralph.py --main-branch develop
```

### Dirty Working Directory

If the working directory has uncommitted changes at startup, the runner will:
- Display the current changes
- Prompt to continue anyway (console mode) or fail (TUI mode by default)

### Failure Recovery

When a story fails with uncommitted changes:
- The runner prompts to reset the branch
- Choosing "yes" discards all changes and returns to main
- Choosing "no" keeps the branch for manual inspection

## Review Phase

The review phase is an optional post-implementation step that critiques code before merging. When enabled, after an implementation agent signals completion, a second "reviewer" pass examines the changes.

### How Review Works

1. After detecting `<promise>COMPLETE</promise>`, the runner triggers a review
2. The reviewer sees:
   - The story's acceptance criteria
   - The `git diff` showing all changes from main
   - The project's `AGENTS.md` guidelines
3. The reviewer outputs either:
   - `<verdict>APPROVE</verdict>` - Changes are ready to merge
   - `<verdict>REJECT</verdict>` - Changes need revision
4. If APPROVED: Story is marked complete and merged to main
5. If REJECTED: Story is reopened with feedback, and the loop continues

### Enabling Review

```bash
# CLI flag
uv run ralph.py --no-tui --review

# Or enable in TUI configuration screen
```

### Review Output

Review results are logged to `progress.txt`, including:
- The verdict (APPROVE/REJECT)
- The reviewer's full analysis
- Any feedback for rejected changes

### When to Use Review

Review is useful when:
- Working on complex or high-stakes changes
- Training the agent loop on a new codebase
- Catching common patterns the implementer misses

Review adds overhead (an extra agent call per completion), so consider disabling for simple tasks or rapid iteration.

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
      "type": "feature",
      "acceptanceCriteria": [
        "Criterion 1",
        "Criterion 2"
      ],
      "passes": false
    }
  ]
}
```

### Story Types

The optional `type` field enables task-type specific prompts:

| Type | Description | Prompt Style |
|------|-------------|--------------|
| `feature` | New functionality | Creative, expansive - encourages design thinking |
| `bug` | Bug fixes | Strict, analytic - focuses on root cause analysis |
| `chore` | Maintenance tasks | Uses default prompt |
| `test` | Test coverage | Uses default prompt |

When a story has a `type` field, the runner looks for `prompt_{type}.md` (e.g., `prompt_feature.md`) before falling back to the generic `prompt.md`.

### Story Best Practices

1. **Keep stories small** - Should be completable in one context window
2. **Be specific** - Clear acceptance criteria the agent can verify
3. **Independent** - Stories should be independently verifiable
4. **Test-driven** - Include testing requirements in criteria

## Prompt Templates

The runner supports task-type specific prompts to optimize agent behavior for different kinds of work.

### Template Resolution Order

1. Type-specific in project root: `prompt_{type}.md`
2. Generic in project root: `prompt.md`
3. Type-specific bundled: `templates/prompt_{type}.md`
4. Generic bundled: `templates/prompt.md`

### Built-in Templates

| Template | Purpose |
|----------|---------|
| `prompt.md` | Generic development tasks |
| `prompt_feature.md` | Feature development - creative, design-focused |
| `prompt_bug.md` | Bug fixes - strict, analytical, minimal-change focused |

### Template Placeholders

All templates support these placeholders:

- `{{PRD_STATUS}}` - Current PRD completion status
- `{{STORY}}` - Current story details
- `{{PROGRESS}}` - Contents of progress.txt

### Customizing Templates

Override any template by creating it in your project root:

```bash
# Custom feature prompt
cp scripts/runner-wiggum/templates/prompt_feature.md prompt_feature.md
# Edit to taste...
```

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

