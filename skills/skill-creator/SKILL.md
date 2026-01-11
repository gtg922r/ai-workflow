---
name: skill-creator
description: Create new Agent Skills conforming to the open Agent Skills standard. Use when the user wants to create, design, or scaffold a new skill for AI agents. Handles skill metadata, instructions, references, scripts, and assets. Supports Gemini CLI, Claude Code, OpenAI Codex, and other compatible agents.
metadata:
  author: ai-workflow-tools
  version: "1.0"
  tags: skill authoring development agent-skills
---

# Skill Creator

You are an expert skill author helping users create high-quality Agent Skills that conform to the [Agent Skills](https://agentskills.io) open standard.

## When to Use This Skill

Activate this skill when the user wants to:
- Create a new agent skill from scratch
- Design skill structure and content
- Understand skill authoring best practices
- Convert existing workflows into skills
- Install skills for specific providers (Gemini CLI, Claude Code, OpenAI Codex)

## Skill Creation Workflow

### Step 1: Understand the Request

**For simple, straightforward skills:**
- If the skill purpose is clear and well-defined, proceed directly to creation
- Use reasonable defaults and best practices
- Create a focused, minimal skill that does one thing well

**For complex or nuanced skills:**
Ask clarifying questions to understand:
1. **Purpose**: What specific task or capability should this skill provide?
2. **Trigger conditions**: When should an agent activate this skill?
3. **Scope**: Should it be project-specific, user-wide, or shared?
4. **Resources needed**: Does it require scripts, templates, or reference docs?
5. **Target providers**: Which agents will use it (Gemini CLI, Claude Code, Codex, all)?

### Step 2: Design the Skill Structure

Every skill requires at minimum:

```
skill-name/
└── SKILL.md          # Required: metadata + instructions
```

For more complex skills, add optional directories:

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code (Python, Bash, etc.)
├── references/       # Optional: detailed documentation, schemas
└── assets/           # Optional: templates, examples, data files
```

### Step 3: Write the SKILL.md

The SKILL.md file has two parts:

#### YAML Frontmatter (Required)

```yaml
---
name: skill-name
description: Clear description of what this skill does and when to use it.
---
```

**Name requirements:**
- 1-64 characters
- Lowercase letters, numbers, and hyphens only (`a-z`, `0-9`, `-`)
- Cannot start or end with a hyphen
- No consecutive hyphens (`--`)
- Must match the parent directory name

**Description best practices:**
- 1-1024 characters
- Describe both WHAT the skill does AND WHEN to use it
- Include keywords that help agents identify relevant tasks
- Be specific enough to distinguish from similar skills

#### Markdown Body (Instructions)

Write clear, actionable instructions. Recommended structure:

```markdown
# Skill Title

## When to Use
[Describe trigger conditions and use cases]

## How to Use
[Step-by-step instructions for the agent]

## Examples
[Concrete input/output examples]

## Edge Cases
[Common pitfalls and how to handle them]
```

### Step 4: Apply Progressive Disclosure

Keep context efficient by layering information:

| Level | Content | Token Budget | When Loaded |
|-------|---------|--------------|-------------|
| Metadata | `name` + `description` | ~100 tokens | Always (at startup) |
| Instructions | SKILL.md body | < 5000 tokens | When skill activates |
| Resources | Referenced files | As needed | On demand |

**Guidelines:**
- Keep SKILL.md under 500 lines
- Move detailed reference material to `references/` files
- Use file references for comprehensive documentation
- Scripts execute without loading code into context

### Step 5: Validate the Skill

Before finalizing, verify:

- [ ] `name` field matches directory name
- [ ] `name` follows naming conventions (lowercase, hyphens, no consecutive --)
- [ ] `description` clearly states purpose AND activation triggers
- [ ] Instructions are clear and actionable
- [ ] File references use relative paths from skill root
- [ ] No deeply nested reference chains

## Quick Templates

### Minimal Skill

```markdown
---
name: my-skill
description: Brief description of capability and when to use it.
---

# My Skill

## Instructions
1. Step one
2. Step two
3. Step three
```

### Skill with Scripts

```markdown
---
name: data-processor
description: Process and validate data files. Use when working with CSV, JSON, or XML data transformation.
---

# Data Processor

## Quick Start
Run the validation script:
\`\`\`bash
python scripts/validate.py input.csv
\`\`\`

## Detailed Usage
See [references/GUIDE.md](references/GUIDE.md) for complete documentation.
```

### Workflow Skill

```markdown
---
name: code-review
description: Perform code reviews following team standards. Use when asked to review, check, or provide feedback on code changes.
---

# Code Review

## Review Process
1. **Scope**: Review only the changed files
2. **Style**: Check adherence to project conventions
3. **Security**: Flag potential vulnerabilities
4. **Tests**: Verify test coverage for new logic

## Output Format
Provide feedback as:
- **Strengths**: What's done well
- **Suggestions**: Improvements to consider
- **Required Changes**: Issues that must be fixed
```

## Provider-Specific Information

For detailed information about how each provider discovers, activates, and uses skills, see [references/PROVIDERS.md](references/PROVIDERS.md).

### Quick Installation Summary

| Provider | User Skills Location | Project Skills Location |
|----------|---------------------|------------------------|
| Gemini CLI | `~/.gemini/skills/` | `.gemini/skills/` |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| OpenAI Codex | `~/.codex/skills/` | `.codex/skills/` |

## Additional Resources

- **Full Specification**: See [references/SPECIFICATION.md](references/SPECIFICATION.md) for complete format details
- **Provider Details**: See [references/PROVIDERS.md](references/PROVIDERS.md) for provider-specific behavior
- **Example Skills**: See [references/EXAMPLES.md](references/EXAMPLES.md) for comprehensive examples
- **Official Standard**: https://agentskills.io
