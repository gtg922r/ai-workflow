# Work Log: command-workflow-doctor
## New Custom Command: Workflow Doctor

Started: 2026-01-15 00:08:46

---

## Progress

[00:08:46] Starting work on story: New Custom Command: Workflow Doctor
[00:08:46] Beginning iteration 4

### Implementation Summary

Created `commands/gemini/workflow/workflow-doctor.toml` - a comprehensive diagnostic command that:

1. **Agent CLI Detection**: Checks for Gemini CLI, Claude Code, and OpenAI Codex installations with version info
2. **Configuration Validation**: Verifies existence of config directories (`~/.gemini`, `~/.claude`, `~/.codex`) and their subdirectories (commands, skills)
3. **Environment Variables**: Checks for API keys (GOOGLE_API_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY) without exposing values
4. **Component Inventory**: Lists installed commands and skills with symlink status
5. **Symlink Health**: Detects broken symlinks in all agent config directories
6. **Related Tools**: Checks for supporting tools (gh, git, node, python)
7. **Actionable Report**: Generates a structured report with emoji indicators and numbered fix recommendations

The command uses shell injection (`!{...}`) to gather real-time system information and produces a formatted diagnostic report with:
- Overall health status (✅/⚠️/❌)
- Per-section findings
- Prioritized remediation steps
[00:10:13] Iteration 4 completed: **Usage**: Once installed, invoke with `/workflow:workflow-doctor` in Gemini CLI. Optionally pass co
