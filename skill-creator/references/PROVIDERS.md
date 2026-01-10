# Provider-Specific Differences

> How Agent Skills work differently across Claude Code, Google Gemini CLI, and OpenAI Codex.

While Agent Skills follow a common standard, each provider implements them with subtle differences. Understanding these differences helps you create skills that work well across all platforms.

## Quick Comparison

| Feature | Claude Code | Gemini CLI | OpenAI Codex |
|---------|-------------|------------|--------------|
| Discovery Location | `.claude/skills/`, `~/.claude/skills/` | `.gemini/skills/`, `~/.gemini/skills/` | `.codex/skills/`, `~/.codex/skills/` |
| Activation Method | Automatic via bash read | `activate_skill` tool | Explicit (`$skill`) or implicit |
| User Consent | No explicit prompt | Consent prompt required | No explicit prompt |
| Network Access | Full access | Full access | Varies by environment |
| Code Execution | Full bash/python | Full bash/python | Sandboxed |
| Skill Scope | Personal + Project | Project > User > Extension | Repo > User > Admin > System |

## Claude Code

### Overview
Claude Code uses a filesystem-based approach where skills are directories on the user's machine. Claude discovers and uses them automatically based on task matching.

### Discovery Locations
```
~/.claude/skills/          # Personal skills (all projects)
.claude/skills/            # Project skills (this repo only)
```

### Activation Behavior
- **Automatic**: Claude reads SKILL.md via bash when task matches description
- **No consent prompt**: Skills activate without explicit user approval
- **Progressive loading**: Only loads referenced files when needed

### Unique Features
- **Code execution environment**: Full access to VM with filesystem, bash, and installed packages
- **No network restrictions**: Skills can make external API calls
- **API integration**: Skills can also be uploaded via Claude API for organization-wide sharing

### Considerations When Authoring
- Scripts have full system access—document security implications
- Can assume standard Unix tools are available
- Network-dependent skills work without restriction

### Example: Claude Code Specific Skill
```yaml
---
name: claude-code-deployer
description: Deploy applications using Claude Code's full system access. Use when deploying to servers, running Docker, or executing system commands.
compatibility: Claude Code (requires full system access)
---
```

## Google Gemini CLI

### Overview
Gemini CLI treats skills as "on-demand expertise" loaded through an explicit `activate_skill` tool with user consent.

### Discovery Locations (Precedence: High to Low)
```
.gemini/skills/            # Project skills (highest priority)
~/.gemini/skills/          # User skills
<extension>/skills/        # Extension-bundled skills
```

### Activation Behavior
- **Tool-based**: Uses `activate_skill` tool to load skills
- **Consent required**: User sees confirmation prompt with skill name, purpose, and directory path
- **Directory access granted**: Upon approval, skill directory is added to allowed file paths

### Unique Features
- **Experimental flag**: Requires `experimental.skills` setting to enable
- **Interactive management**: `/skills` command for list, enable, disable, reload
- **Extension support**: Skills can be bundled with Gemini extensions
- **Precedence rules**: Project skills override user skills override extension skills

### Slash Commands
```
/skills list              # Show all discovered skills
/skills disable <name>    # Disable a skill
/skills enable <name>     # Re-enable a skill
/skills reload            # Refresh skill discovery
```

### CLI Commands
```bash
gemini skills list
gemini skills enable my-skill
gemini skills disable my-skill
```

### Considerations When Authoring
- User will see consent prompt—make description clear and trustworthy
- Skill directory path is shown to user—keep paths clean
- Consider extension bundling for distribution

### Example: Gemini CLI Specific Skill
```yaml
---
name: gemini-extension-helper
description: Create and package Gemini CLI extensions. Use when building extensions, bundling skills, or extending Gemini CLI functionality.
compatibility: Designed for Gemini CLI (or similar products)
---
```

## OpenAI Codex

### Overview
OpenAI Codex supports both explicit (user-invoked) and implicit (AI-selected) skill activation, with a sophisticated scoping system.

### Discovery Locations (Precedence: High to Low)
```
$CWD/.codex/skills/        # Current working directory
$CWD/../.codex/skills/     # Parent directory (in git repos)
$REPO_ROOT/.codex/skills/  # Repository root
~/.codex/skills/           # User skills ($CODEX_HOME)
/etc/codex/skills/         # Admin/system skills
<bundled>/                 # Built-in Codex skills
```

### Activation Methods

**Explicit Invocation**:
```
$skill-name   # Mention skill with $ prefix
/skills       # Slash command to select skill
```

**Implicit Invocation**:
- Codex autonomously selects based on task matching description

### Unique Features
- **Built-in skills**: Includes `$skill-creator`, `$skill-installer`, etc.
- **Skill installer**: `$skill-installer <name>` to download from curated repos
- **Scope hierarchy**: Fine-grained control over skill precedence
- **IDE integration**: Works in both CLI and IDE extensions

### Metadata Extension
Codex supports additional metadata:
```yaml
metadata:
  short-description: Optional user-facing description
```

### Considerations When Authoring
- Support both explicit (`$skill-name`) and implicit invocation
- Consider scope—repo skills override user skills
- Can distribute via `skill-installer` ecosystem

### Example: Codex Specific Skill
```yaml
---
name: codex-plan-creator
description: Create detailed implementation plans before coding. Use when the user asks to plan, design, or architect a feature before implementation.
metadata:
  short-description: Create implementation plans
---
```

## Cross-Platform Best Practices

### 1. Use Standard Locations
If targeting multiple platforms, provide installation instructions for each:
```
# Claude Code
cp -r my-skill ~/.claude/skills/

# Gemini CLI  
cp -r my-skill ~/.gemini/skills/

# OpenAI Codex
cp -r my-skill ~/.codex/skills/
```

### 2. Avoid Platform-Specific Dependencies
- Don't assume specific tools beyond basic Unix utilities
- Document any platform-specific requirements in `compatibility`
- Test on multiple platforms when possible

### 3. Use Compatibility Field
```yaml
compatibility: Works with Claude Code, Gemini CLI, Codex. Requires git and python3.
```

### 4. Handle Network Differences
- Codex may have network restrictions in some environments
- Claude Code and Gemini CLI typically have full network access
- Document network requirements clearly

### 5. Consider Consent UX (Gemini)
Gemini CLI shows a consent dialog—make your skill's purpose crystal clear:
```yaml
description: Reviews code for security vulnerabilities using static analysis. Activates when user requests security review or mentions vulnerability scanning. ONLY reads code, does not modify files.
```

## Platform Detection

Skills cannot directly detect which platform is running them, but you can:

1. **Check environment variables**: Different platforms may set different vars
2. **Check available tools**: Test for platform-specific commands
3. **Use conditional instructions**: "If using Gemini CLI, run `/skills list` first"

## Summary

| If You Need | Best Platform |
|-------------|---------------|
| Full system access | Claude Code |
| User consent workflow | Gemini CLI |
| Explicit skill invocation | OpenAI Codex |
| Extension bundling | Gemini CLI |
| Organization-wide sharing | Claude API |
| IDE integration | OpenAI Codex |

---

*For installation instructions, see [INSTALLATION.md](INSTALLATION.md)*
