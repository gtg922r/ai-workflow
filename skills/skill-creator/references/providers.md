# Provider-Specific Details

## Google Gemini CLI
- **Project Skills**: `.gemini/skills/` (Version controlled, shared with team).
- **User Skills**: `~/.gemini/skills/` (Personal, cross-project).
- **Management**: 
  - CLI: `gemini skills list`, `gemini skills enable/disable <name>`.
  - Chat: `/skills list`, `/skills disable <name>`.
- **Nuance**: Supports `activate_skill` tool to dynamically load context.

## Anthropic Claude
### Claude Code (CLI)
- **Locations**: 
  - Personal: `~/.claude/skills/`
  - Project: `.claude/skills/`
- **Network**: Full network access (user's machine).

### Claude.ai & API
- **Claude.ai**: Upload via Settings > Features. (Individual user only).
- **API**: Use `files-api` to upload.
- **Constraints**: 
  - Claude.ai: Varying network access.
  - API: No internet access, no runtime package installation.

## OpenAI Codex
- **Project/Repo Skills**: 
  - `$CWD/.codex/skills`
  - `$REPO_ROOT/.codex/skills`
- **User Skills**: 
  - `~/.codex/skills` (macOS/Linux)
  - `$CODEX_HOME/skills`
- **Management**: `/skills` command or `$skill-name` invocation.
