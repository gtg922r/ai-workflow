# Agent Skills Specification

## Directory Structure
A skill is a directory containing at minimum a `SKILL.md` file.
```
skill-name/
├── SKILL.md          # Required: instructions + metadata
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
└── assets/           # Optional: templates, resources
```

## SKILL.md Format
Must contain YAML frontmatter followed by Markdown content.

### Frontmatter
```yaml
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

**Constraints:**
1. **`name` (Required)**: 
   - 1-64 characters.
   - Lowercase letters, numbers, and hyphens only (`a-z`, `0-9`, `-`).
   - Must NOT start or end with a hyphen.
   - Must NOT contain consecutive hyphens (`--`).
   - Must match the parent directory name.

2. **`description` (Required)**:
   - 1-1024 characters.
   - Non-empty.
   - Should describe **what** it does and **when** to use it.

3. **Optional Fields**:
   - `license`: License name or file reference.
   - `compatibility`: Environment requirements (max 500 chars).
   - `metadata`: Key-value map.
   - `allowed-tools`: Space-delimited list of pre-approved tools (Experimental).

### Body Content
Markdown instructions for the agent.
- Step-by-step instructions.
- Examples.
- References to files in `scripts/`, `references/`, `assets/`.

## Best Practices
1. **Progressive Disclosure**: Keep `SKILL.md` under 500 lines. Move heavy docs to `references/` and code to `scripts/`.
2. **File References**: Use relative paths (e.g., `scripts/myscript.py`). Keep references shallow (one level deep).
