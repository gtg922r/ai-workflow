# Skill Installation Guide

> How to install Agent Skills on Claude Code, Google Gemini CLI, and OpenAI Codex.

After creating a skill, use these instructions to install it on your preferred agent platform.

## Quick Reference

| Platform | Personal Location | Project Location |
|----------|------------------|------------------|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Gemini CLI | `~/.gemini/skills/` | `.gemini/skills/` |
| OpenAI Codex | `~/.codex/skills/` | `.codex/skills/` |

---

## Claude Code Installation

### Option 1: Personal Skills (Available in All Projects)

```bash
# Create the skills directory if it doesn't exist
mkdir -p ~/.claude/skills

# Copy your skill
cp -r my-skill ~/.claude/skills/

# Verify installation
ls ~/.claude/skills/my-skill/SKILL.md
```

### Option 2: Project Skills (Available in This Repo Only)

```bash
# From your project root
mkdir -p .claude/skills

# Copy your skill
cp -r my-skill .claude/skills/

# Optionally commit to version control
git add .claude/skills/my-skill
git commit -m "Add my-skill agent skill"
```

### Option 3: Claude API Upload (Organization-Wide)

For sharing skills across your organization via the Claude API:

```python
import anthropic

client = anthropic.Anthropic()

# Create a skill from a directory
with open("my-skill/SKILL.md", "r") as f:
    skill_content = f.read()

# Upload via Skills API (requires skills-2025-10-02 beta)
# See Claude API documentation for full details
```

### Verification (Claude Code)

Start a new Claude Code session and ask:
> "What skills do you have available?"

Or test the skill directly by asking for something that matches its description.

---

## Google Gemini CLI Installation

### Prerequisites

Enable experimental skills feature:
```bash
# Via settings
gemini settings

# Or add to config file
# Set experimental.skills = true
```

### Option 1: Personal Skills (All Projects)

```bash
# Create the skills directory
mkdir -p ~/.gemini/skills

# Copy your skill
cp -r my-skill ~/.gemini/skills/

# Verify
ls ~/.gemini/skills/my-skill/SKILL.md
```

### Option 2: Project Skills (This Repo Only)

```bash
# From your project root
mkdir -p .gemini/skills

# Copy your skill  
cp -r my-skill .gemini/skills/

# Commit to share with team
git add .gemini/skills/my-skill
git commit -m "Add my-skill agent skill"
```

### Option 3: Extension Bundling

Skills can be bundled within Gemini extensions. See Gemini CLI extension documentation for details.

### Verification (Gemini CLI)

```bash
# List all discovered skills
gemini skills list

# Or in interactive session
/skills list
```

### Managing Skills (Gemini CLI)

```bash
# Disable a skill
gemini skills disable my-skill

# Re-enable a skill
gemini skills enable my-skill

# Reload after adding new skills
# In interactive session:
/skills reload
```

---

## OpenAI Codex Installation

### Option 1: Repository Skills (Highest Priority)

```bash
# From your project root
mkdir -p .codex/skills

# Copy your skill
cp -r my-skill .codex/skills/

# Commit to share with team
git add .codex/skills/my-skill
git commit -m "Add my-skill agent skill"
```

### Option 2: User Skills (All Projects)

```bash
# Create user skills directory
mkdir -p ~/.codex/skills

# Copy your skill
cp -r my-skill ~/.codex/skills/

# Verify
ls ~/.codex/skills/my-skill/SKILL.md
```

### Option 3: Using Skill Installer

For skills from the curated repository:

```
$skill-installer my-skill
```

Or from a custom repository:

```
$skill-installer https://github.com/org/skills-repo my-skill
```

### Option 4: Admin/System Skills

For machine-wide or container skills:

```bash
# Requires appropriate permissions
sudo mkdir -p /etc/codex/skills
sudo cp -r my-skill /etc/codex/skills/
```

### Verification (Codex)

```bash
# In Codex, use the skills selector
/skills

# Or mention the skill directly
$my-skill help
```

### Skill Precedence in Codex

If multiple skills have the same name, higher-precedence locations win:

1. `$CWD/.codex/skills/` (current directory)
2. `$CWD/../.codex/skills/` (parent in git repo)
3. `$REPO_ROOT/.codex/skills/` (repo root)
4. `~/.codex/skills/` (user)
5. `/etc/codex/skills/` (admin)
6. Built-in skills (system)

---

## Cross-Platform Installation Script

For skills that should work on all platforms:

```bash
#!/bin/bash
# install-skill.sh - Install a skill to all supported platforms

SKILL_DIR="$1"

if [ -z "$SKILL_DIR" ] || [ ! -f "$SKILL_DIR/SKILL.md" ]; then
    echo "Usage: ./install-skill.sh <skill-directory>"
    echo "Error: Skill directory must contain SKILL.md"
    exit 1
fi

SKILL_NAME=$(basename "$SKILL_DIR")

echo "Installing skill: $SKILL_NAME"

# Claude Code
if [ -d ~/.claude ] || mkdir -p ~/.claude/skills 2>/dev/null; then
    cp -r "$SKILL_DIR" ~/.claude/skills/
    echo "✓ Installed to Claude Code (~/.claude/skills/$SKILL_NAME)"
fi

# Gemini CLI
if [ -d ~/.gemini ] || mkdir -p ~/.gemini/skills 2>/dev/null; then
    cp -r "$SKILL_DIR" ~/.gemini/skills/
    echo "✓ Installed to Gemini CLI (~/.gemini/skills/$SKILL_NAME)"
fi

# OpenAI Codex
if [ -d ~/.codex ] || mkdir -p ~/.codex/skills 2>/dev/null; then
    cp -r "$SKILL_DIR" ~/.codex/skills/
    echo "✓ Installed to OpenAI Codex (~/.codex/skills/$SKILL_NAME)"
fi

echo ""
echo "Installation complete! Restart your agent session to use the skill."
```

Usage:
```bash
chmod +x install-skill.sh
./install-skill.sh ./my-skill
```

---

## Uninstalling Skills

### Claude Code
```bash
rm -rf ~/.claude/skills/my-skill      # Personal
rm -rf .claude/skills/my-skill        # Project
```

### Gemini CLI
```bash
rm -rf ~/.gemini/skills/my-skill      # Personal
rm -rf .gemini/skills/my-skill        # Project

# Then reload
# In session: /skills reload
```

### OpenAI Codex
```bash
rm -rf ~/.codex/skills/my-skill       # User
rm -rf .codex/skills/my-skill         # Repo
```

---

## Troubleshooting

### Skill Not Discovered

1. **Check file structure**: Ensure `SKILL.md` exists in skill root
2. **Verify name match**: Directory name must match `name` field in frontmatter
3. **Restart session**: Most agents need a session restart to discover new skills
4. **Check path**: Ensure skill is in a valid discovery location

### Skill Not Activating

1. **Review description**: Is it clear enough for the agent to match?
2. **Test explicit activation**: 
   - Codex: `$skill-name`
   - Gemini: `/skills list` then mention skill by name
3. **Check for conflicts**: Another skill with same name may have higher priority

### Permission Errors

1. **Check directory permissions**: 
   ```bash
   chmod -R 755 ~/.claude/skills/my-skill
   ```
2. **Verify read access to all files**
3. **For system paths**: Use `sudo` appropriately

### Validation Errors

Use the official validator:
```bash
npx skills-ref validate ./my-skill
```

Common issues:
- Name doesn't match directory
- Invalid characters in name
- Description too long (>1024 chars)
- Missing required fields

---

## Post-Installation Testing

After installing, test your skill:

1. **Start a new session** with your agent
2. **Ask about available skills** to verify discovery
3. **Trigger the skill** with a matching request
4. **Verify behavior** matches your expectations
5. **Test edge cases** documented in the skill

---

*For more information, see the Agent Skills specification at https://agentskills.io*
