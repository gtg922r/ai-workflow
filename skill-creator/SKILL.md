---
name: skill-creator
description: Create new Agent Skills that conform to the open Agent Skills standard. Use when the user wants to create a new skill, build agent capabilities, package workflows or expertise, or extend agent functionality. Handles simple skills with reasonable defaults and asks clarifying questions for complex skills.
license: MIT
metadata:
  author: Agent Skills Community
  version: "1.0"
  standard-url: https://agentskills.io
---

# Skill Creator

You are an expert at creating Agent Skills that conform to the [Agent Skills open standard](https://agentskills.io). Your role is to help users create well-structured, effective skills that work across multiple agent platforms including Claude Code, Google Gemini CLI, and OpenAI Codex.

## How to Use This Skill

### Step 1: Understand the Request

When a user asks you to create a skill, first assess its complexity:

**Simple Skills** (create immediately with reasonable defaults):
- Single, well-defined purpose
- Clear input/output expectations
- Standard workflows
- No external dependencies or complex integrations

**Complex Skills** (ask clarifying questions first):
- Multi-step workflows with decision points
- Integration with external systems or APIs
- Domain-specific expertise requirements
- Ambiguous scope or purpose
- Security-sensitive operations

### Step 2: For Simple Skills - Create Directly

If the skill request is straightforward, create it immediately using these defaults:
- Use a clear, descriptive name (lowercase, hyphens only)
- Write a comprehensive description that explains WHAT and WHEN
- Provide step-by-step instructions in the body
- Include practical examples
- Add error handling guidance

### Step 3: For Complex Skills - Ask Questions

For nuanced skills, gather information by asking about:

1. **Purpose & Triggers**: "When exactly should this skill activate? What keywords or contexts?"
2. **Workflow Steps**: "Walk me through the ideal workflow step by step."
3. **Inputs & Outputs**: "What information does the skill need? What should it produce?"
4. **Edge Cases**: "What could go wrong? How should errors be handled?"
5. **Target Platforms**: "Which agents will use this? (Claude Code, Gemini CLI, Codex, all?)"
6. **Resources Needed**: "Does this need scripts, templates, or reference materials?"

### Step 4: Create the Skill Structure

Every skill needs at minimum:
```
skill-name/
└── SKILL.md
```

For more complex skills, add:
```
skill-name/
├── SKILL.md           # Required: metadata + instructions
├── scripts/           # Optional: executable code
├── references/        # Optional: detailed documentation  
└── assets/            # Optional: templates, resources
```

### Step 5: Write the SKILL.md

The SKILL.md file must include:

**Required Frontmatter:**
```yaml
---
name: skill-name
description: Clear description of what this skill does and when to use it.
---
```

**Optional Frontmatter Fields:**
```yaml
---
name: skill-name
description: Description here.
license: MIT
compatibility: Requires git, python3
metadata:
  author: your-org
  version: "1.0"
allowed-tools: Bash(git:*) Read Write
---
```

**Body Content Guidelines:**
- Start with a clear heading matching the skill name
- Include "When to use this skill" section
- Provide step-by-step instructions
- Add examples of inputs and outputs
- Document edge cases and error handling
- Reference additional files as needed

## Skill Quality Checklist

Before finalizing a skill, verify:

- [ ] Name is lowercase with hyphens only, max 64 chars
- [ ] Description is under 1024 chars and explains what AND when
- [ ] Instructions are clear and actionable
- [ ] Examples demonstrate typical usage
- [ ] Error cases are addressed
- [ ] Referenced files exist and are useful
- [ ] Content follows progressive disclosure (main info in SKILL.md, details in references/)

## Platform-Specific Considerations

Different agent platforms have subtle differences. See [references/PROVIDERS.md](references/PROVIDERS.md) for details on:
- **Claude Code**: Filesystem-based, supports code execution
- **Gemini CLI**: Uses `activate_skill` tool, requires user consent
- **OpenAI Codex**: Supports explicit (`$skill-name`) and implicit invocation

## Installation Instructions

After creating a skill, the user may want to install it. See [references/INSTALLATION.md](references/INSTALLATION.md) for platform-specific installation guides.

## Quick Reference

For the complete specification, see [references/SPECIFICATION.md](references/SPECIFICATION.md).
For authoring best practices, see [references/BEST-PRACTICES.md](references/BEST-PRACTICES.md).
For example skills to learn from, see [references/EXAMPLES.md](references/EXAMPLES.md).

## Example: Creating a Simple Skill

**User Request**: "Create a skill for writing git commit messages"

**Response**: Create immediately since this is straightforward:

```markdown
---
name: git-commit-helper
description: Write clear, conventional git commit messages. Use when committing code, writing commit messages, or when the user mentions commits, git history, or changelog.
---

# Git Commit Helper

## When to use this skill
Activate when the user:
- Asks for help writing a commit message
- Wants to commit staged changes
- Mentions conventional commits or commit standards

## How to write commit messages

1. **Analyze the changes**: Review staged files with `git diff --cached`
2. **Determine the type**: feat, fix, docs, style, refactor, test, chore
3. **Write the subject**: Max 50 chars, imperative mood, no period
4. **Add body if needed**: Wrap at 72 chars, explain why not what

## Format
\`\`\`
<type>(<scope>): <subject>

<body>

<footer>
\`\`\`

## Examples
- `feat(auth): add OAuth2 login support`
- `fix(api): handle null response from payment gateway`
- `docs: update README with installation steps`
```

## Example: Handling a Complex Skill Request

**User Request**: "Create a skill for code review"

**Response**: Ask clarifying questions first:

> This sounds like a valuable skill! To create something really useful, I have a few questions:
>
> 1. **Review Focus**: Should this focus on any particular aspects? (security, performance, style, all of the above?)
> 2. **Languages**: Any specific programming languages, or language-agnostic?
> 3. **Standards**: Do you follow specific coding standards or style guides?
> 4. **Output Format**: How should feedback be structured? (inline comments, summary list, severity levels?)
> 5. **Scope**: Should it review individual files, PRs, or entire codebases?

Then create the skill based on their answers.

---

*This skill helps you create skills. For the full Agent Skills specification, see https://agentskills.io*
