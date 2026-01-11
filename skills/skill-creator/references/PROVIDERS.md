# Provider-Specific Guide

This document details how different AI agent providers discover, activate, and use Agent Skills, along with installation instructions for each.

## Provider Comparison

| Feature | Gemini CLI | Claude Code | OpenAI Codex |
|---------|------------|-------------|--------------|
| Skill Discovery | Automatic | Automatic | Automatic |
| Explicit Invocation | `/skills` command | Automatic | `/skills` or `$skill-name` |
| Implicit Invocation | Yes | Yes | Yes |
| Project Skills | `.gemini/skills/` | `.claude/skills/` | `.codex/skills/` |
| User Skills | `~/.gemini/skills/` | `~/.claude/skills/` | `~/.codex/skills/` |
| Extension Skills | Yes (via extensions) | Yes (via plugins) | Yes (system-level) |
| Skill Management | `/skills` slash command | Automatic | `/skills` slash command |
| Activation Consent | Yes (prompted) | Automatic | Varies |

---

## Gemini CLI

### Overview

Gemini CLI discovers skills from three tiers with precedence: Project > User > Extension.

Skills are experimental and must be enabled via `experimental.skills` in settings or through the `/settings` interactive UI.

### Skill Locations

| Scope | Location | Use Case |
|-------|----------|----------|
| Project | `.gemini/skills/` | Team-shared, version-controlled skills |
| User | `~/.gemini/skills/` | Personal skills across all projects |
| Extension | Bundled in extensions | Distributed via Gemini extensions |

### Installation

**User-level skill:**
```bash
# Create the user skills directory
mkdir -p ~/.gemini/skills

# Copy or create your skill
cp -r my-skill ~/.gemini/skills/
```

**Project-level skill:**
```bash
# Create the project skills directory
mkdir -p .gemini/skills

# Copy or create your skill
cp -r my-skill .gemini/skills/

# Commit to version control
git add .gemini/skills/my-skill
git commit -m "feat: add my-skill agent skill"
```

### Management Commands

```bash
# List all discovered skills
gemini skills list

# Enable a skill
gemini skills enable my-skill

# Disable a skill
gemini skills disable my-skill

# Reload skills (in interactive session)
/skills reload
```

### How It Works

1. **Discovery**: At session start, Gemini injects skill names and descriptions into the system prompt
2. **Activation**: Gemini calls `activate_skill` tool when a task matches
3. **Consent**: You see a confirmation prompt with skill details
4. **Injection**: Upon approval, SKILL.md content and folder structure are added to context
5. **Execution**: The skill's directory is added to allowed file paths

### Gemini-Specific Notes

- Skills override by name (higher precedence wins)
- Use `--scope project` or `--scope user` with enable/disable commands
- Extension skills are bundled within installed Gemini extensions

---

## Claude Code

### Overview

Claude Code uses filesystem-based skill discovery. Skills are loaded automatically based on directory structure.

### Skill Locations

| Scope | Location | Use Case |
|-------|----------|----------|
| Project | `.claude/skills/` | Repository-specific skills |
| User | `~/.claude/skills/` | Personal skills across projects |
| Plugins | Via Claude Code Plugins | Shared/distributed skills |

### Installation

**User-level skill:**
```bash
# Create the user skills directory
mkdir -p ~/.claude/skills

# Copy or create your skill
cp -r my-skill ~/.claude/skills/
```

**Project-level skill:**
```bash
# Create the project skills directory
mkdir -p .claude/skills

# Copy or create your skill
cp -r my-skill .claude/skills/

# Commit to version control
git add .claude/skills/my-skill
git commit -m "feat: add my-skill agent skill"
```

### How It Works

1. **Startup**: Claude loads metadata (name, description) for all discovered skills
2. **Matching**: When a request matches a skill's description, Claude reads SKILL.md via bash
3. **Execution**: Claude follows instructions, reading additional files as referenced
4. **Scripts**: Scripts execute via bash; only output enters context (not code)

### Claude-Specific Notes

- Skills leverage Claude's VM environment with filesystem access
- Scripts run without loading source code into context (efficient)
- No practical limit on bundled content (files load on demand)
- Claude Code skills are separate from Claude.ai and API skills

### Progressive Disclosure in Claude

| Level | When Loaded | Token Cost |
|-------|-------------|------------|
| Metadata | Always (startup) | ~100 tokens/skill |
| Instructions | When triggered | < 5k tokens |
| Resources | As needed | Effectively unlimited |

---

## OpenAI Codex

### Overview

Codex loads skills from multiple locations with a precedence hierarchy. Skills can be invoked explicitly (via `/skills` or `$skill-name`) or implicitly.

### Skill Locations (by precedence, high to low)

| Scope | Location | Use Case |
|-------|----------|----------|
| REPO (CWD) | `$CWD/.codex/skills` | Current working directory skills |
| REPO (Parent) | `$CWD/../.codex/skills` | Parent folder shared skills |
| REPO (Root) | `$REPO_ROOT/.codex/skills` | Repository-wide skills |
| USER | `~/.codex/skills` | Personal cross-project skills |
| ADMIN | `/etc/codex/skills` | System-wide/container skills |
| SYSTEM | Bundled with Codex | Built-in skills |

### Installation

**User-level skill:**
```bash
# Create the user skills directory
mkdir -p ~/.codex/skills

# Copy or create your skill
cp -r my-skill ~/.codex/skills/
```

**Project-level skill:**
```bash
# Create the project skills directory
mkdir -p .codex/skills

# Copy or create your skill
cp -r my-skill .codex/skills/

# Commit to version control
git add .codex/skills/my-skill
git commit -m "feat: add my-skill agent skill"
```

**System-level skill (admin):**
```bash
# Requires admin privileges
sudo mkdir -p /etc/codex/skills
sudo cp -r my-skill /etc/codex/skills/
```

### Skill Invocation

**Explicit invocation:**
```
# Using slash command
/skills

# Using skill mention
$my-skill please do something
```

**Implicit invocation:**
Codex automatically activates skills when tasks match descriptions.

### Built-in Codex Skills

Codex includes bundled skills:
- `$skill-creator` - Create new skills
- `$skill-installer` - Install skills from repositories

Install additional skills:
```bash
$skill-installer linear
$skill-installer notion-spec-to-implementation
$skill-installer create-plan
```

### Codex-Specific Notes

- Skills with the same name override based on precedence
- Restart Codex after installing new skills
- Web and iOS don't support explicit invocation yet
- Use `metadata.short-description` for user-facing descriptions

---

## Cross-Provider Compatibility

### Universal Structure

All providers support the core skill structure:

```
skill-name/
├── SKILL.md          # Required (universal)
├── scripts/          # Supported by all
├── references/       # Supported by all
└── assets/           # Supported by all
```

### Portable SKILL.md

Create skills that work across providers:

```yaml
---
name: my-portable-skill
description: Clear description of purpose and when to use. Works across Gemini CLI, Claude Code, and OpenAI Codex.
metadata:
  author: your-name
  version: "1.0"
---

# My Portable Skill

## Instructions
[Provider-agnostic instructions here]
```

### Provider-Specific Customization

If you need provider-specific behavior, document it in the skill:

```markdown
## Provider Notes

### Gemini CLI
- Enable via `/settings` experimental features
- Use `/skills enable my-skill` to activate

### Claude Code
- Automatically discovered from `.claude/skills/`
- Uses bash for file and script access

### OpenAI Codex
- Invoke explicitly with `$my-skill`
- Or let Codex detect implicitly
```

---

## Installation Summary

### Quick Install Commands

**For all providers (user-level):**
```bash
# Gemini CLI
mkdir -p ~/.gemini/skills && cp -r my-skill ~/.gemini/skills/

# Claude Code
mkdir -p ~/.claude/skills && cp -r my-skill ~/.claude/skills/

# OpenAI Codex
mkdir -p ~/.codex/skills && cp -r my-skill ~/.codex/skills/
```

**For all providers (project-level):**
```bash
# Gemini CLI
mkdir -p .gemini/skills && cp -r my-skill .gemini/skills/

# Claude Code
mkdir -p .claude/skills && cp -r my-skill .claude/skills/

# OpenAI Codex
mkdir -p .codex/skills && cp -r my-skill .codex/skills/
```

### Post-Installation

| Provider | Action Required |
|----------|-----------------|
| Gemini CLI | Run `/skills reload` or restart session |
| Claude Code | Automatic (filesystem-based) |
| OpenAI Codex | Restart Codex to pick up new skills |
