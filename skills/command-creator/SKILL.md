---
name: command-creator
description: Create and manage custom commands for the Gemini CLI. Use when the user wants to save a prompt as a reusable command, create project-specific shortcuts, or automate repetitive tasks with context-aware arguments.
---

# Command Creator

## Purpose
Helps users author `.toml` command definitions for the Gemini CLI, enabling reusable prompts, context-aware arguments (`{{args}}`), and dynamic shell execution (`!{...}`).

## When to use this skill
- User wants to "save this prompt" or "make a command for X".
- User wants to create a shortcut for a repetitive task.
- User wants to share a specific workflow with their team (via project-specific commands).

## Workflow

### 1. Requirements Gathering
Clarify the following if not provided:
- **Scope**: Global (`~/.gemini/commands`) or Project-specific (`<project-root>/.gemini/commands`)? *Default to Project-specific if inside a project.*
- **Name**: What should the command be called? (e.g., `/fix`, `/git:commit`).
- **Goal**: What should the command do?
- **Arguments**: Does it need user input? (Implies `{{args}}` usage).

### 2. Command Design
Construct the TOML content based on [COMMANDS_DOC](references/COMMANDS_DOC.md).

**Key Considerations:**
- **Naming**: Map command names to file paths (e.g., `/git:commit` -> `.../commands/git/commit.toml`).
- **Arguments**:
    - Use `{{args}}` for raw injection in the prompt.
    - Use `!{command {{args}}}` for shell commands (arguments are auto-escaped).
- **Dynamic Content**:
    - Use `!{...}` for shell output injection (e.g., `git diff`).
    - Use `@{...}` for file content injection.
- **Description**: Always include a `description` field for `/help` visibility.

### 3. Safety & Validation
- **Shell Injection**: When using `!{...}`, ensure the command is safe. Warn the user that `!{...}` blocks trigger a confirmation dialog.
- **Escape**: Verify `{{args}}` is used correctly inside `!{...}` to prevent injection vulnerabilities (the CLI handles escaping, but the structure must be valid).

### 4. Implementation
1.  Create the directory structure if it doesn't exist.
2.  Write the `.toml` file.

## Examples

### Simple Prompt
*User: "Make a command /explain that explains the code in the file I give it"*
```toml
description = "Explains the code provided as an argument."
prompt = """
Please explain the following code:

@{ {{args}} }
"""
```

### Git Workflow
*User: "Create a command to summarize my changes"*
```toml
description = "Summarizes staged git changes."
prompt = """
Summarize these changes:
!{git diff --staged}
"""
```

## References
- [Custom Commands Documentation](references/COMMANDS_DOC.md) - Full syntax and behavior details.
