# Skill Authoring Best Practices

> Guidelines for creating effective, reliable Agent Skills that work well across platforms.

## Core Principles

### 1. Write for Discovery First

The `description` field is the most important part of your skill. Agents use it to decide when to activate your skill. A poor description means your skill never gets used.

**The Description Formula:**
> [What it does] + [When to use it] + [Trigger keywords/phrases]

**Example - Good:**
```yaml
description: Generate and validate JSON schemas from example data or descriptions. Use when working with JSON, creating API contracts, validating data structures, or when the user mentions schemas, validation, or data formats.
```

**Example - Poor:**
```yaml
description: Helps with JSON stuff.
```

### 2. Design for Progressive Disclosure

Don't put everything in SKILL.md. Structure content so agents load only what they need:

| Content Type | Location | When Loaded |
|--------------|----------|-------------|
| Core workflow | SKILL.md body | When skill activates |
| Detailed reference | `references/*.md` | When specifically needed |
| Executable code | `scripts/*.py` | When execution required |
| Templates/data | `assets/*` | When referenced |

**Good Structure:**
```
json-schema-skill/
├── SKILL.md                    # Quick workflow, links to details
├── references/
│   ├── JSON-SCHEMA-SPEC.md     # Full JSON Schema specification
│   ├── VALIDATION-RULES.md     # Detailed validation rules
│   └── COMMON-PATTERNS.md      # Pattern library
├── scripts/
│   └── validate.py             # Validation script
└── assets/
    └── templates/              # Schema templates
```

### 3. Be Actionable, Not Abstract

Write instructions that tell the agent exactly what to do, not just concepts to understand.

**Good - Actionable:**
```markdown
## How to validate a schema

1. Read the schema file using `cat schema.json`
2. Run validation: `python scripts/validate.py schema.json`
3. If validation fails, check the error message for the failing keyword
4. Fix the issue and re-validate
```

**Poor - Abstract:**
```markdown
## Validation

JSON schemas should be validated before use. Consider the various keywords
and their semantics when reviewing schemas for correctness.
```

### 4. Include Concrete Examples

Every skill should have at least one complete, copy-pasteable example.

```markdown
## Example: Create a user schema

Input:
\`\`\`json
{"name": "Alice", "age": 30, "email": "alice@example.com"}
\`\`\`

Generated schema:
\`\`\`json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "age": {"type": "integer", "minimum": 0},
    "email": {"type": "string", "format": "email"}
  },
  "required": ["name", "email"]
}
\`\`\`
```

### 5. Handle Errors Gracefully

Document what can go wrong and how to handle it.

```markdown
## Error Handling

### Invalid JSON input
If the input is not valid JSON:
1. Identify the syntax error location
2. Suggest the correction
3. Ask the user to provide corrected input

### Missing required fields
If the generated schema is missing fields the user expects:
1. Ask which fields should be required
2. Regenerate with explicit requirements
```

---

## Writing Effective Instructions

### Use Clear Headings

Structure with scannable headings:
```markdown
# Skill Name

## When to use this skill
## Prerequisites  
## Quick start
## Step-by-step workflow
## Examples
## Troubleshooting
## References
```

### Use Numbered Steps for Workflows

Agents follow numbered steps more reliably:
```markdown
## Deployment workflow

1. Verify all tests pass: `npm test`
2. Build the production bundle: `npm run build`
3. Check bundle size: `du -sh dist/`
4. Deploy to staging: `./deploy.sh staging`
5. Run smoke tests: `./smoke-test.sh staging`
6. If smoke tests pass, deploy to production: `./deploy.sh prod`
```

### Use Code Blocks for Commands

Always wrap commands and code in fenced code blocks:
```markdown
Run the migration:
\`\`\`bash
python manage.py migrate --database=production
\`\`\`
```

### Be Explicit About Assumptions

State what you expect to be true:
```markdown
## Prerequisites

This skill assumes:
- Python 3.9+ is installed
- The `requests` library is available
- User has API credentials in `~/.config/api-keys`
```

---

## Naming Conventions

### Skill Names

- Use lowercase letters, numbers, and hyphens only
- Make names descriptive but concise
- Avoid generic names like "helper" or "tool"

**Good names:**
- `pr-review`
- `docker-compose-generator`
- `sql-query-optimizer`
- `api-mock-server`

**Poor names:**
- `Helper` (uppercase, generic)
- `my_tool` (underscores)
- `thing` (meaningless)

### File Naming in Skills

- Use UPPERCASE for documentation: `SKILL.md`, `REFERENCE.md`, `README.md`
- Use lowercase-with-hyphens for code: `validate-schema.py`
- Use descriptive names: `AUTH-PATTERNS.md` not `patterns.md`

---

## Security Considerations

### Document Required Permissions

Be explicit about what access your skill needs:
```yaml
compatibility: Requires read/write access to ~/.ssh/, network access for API calls
```

### Avoid Hardcoded Secrets

Never include credentials in skills:
```markdown
## Configuration

Set your API key as an environment variable:
\`\`\`bash
export API_KEY="your-key-here"
\`\`\`

The skill will read from `$API_KEY`.
```

### Warn About Destructive Operations

If a skill can delete or modify data:
```markdown
## ⚠️ Warning

This skill modifies the production database. Before running:
1. Ensure you have a recent backup
2. Test on staging first
3. Run during low-traffic periods
```

### Audit Scripts Carefully

All scripts in `scripts/` should:
- Have no hidden functionality
- Not make unexpected network calls
- Not access files outside the expected scope
- Include comments explaining their purpose

---

## Size and Performance

### Keep SKILL.md Focused

- Target under 500 lines
- Target under 5000 tokens
- Move detailed content to references

### Minimize Required Reading

The agent should be able to complete common tasks by reading only SKILL.md. Reserve references for edge cases and deep details.

### Use Efficient Scripts

Scripts should:
- Execute quickly
- Return concise output
- Handle errors with clear messages

---

## Cross-Platform Compatibility

### Test on Multiple Platforms

If possible, test your skill on:
- Claude Code
- Gemini CLI
- OpenAI Codex

### Use Standard Tools

Prefer widely-available tools:
- `bash`, `sh` over specialized shells
- `python3` over less common languages
- Standard Unix utilities (`grep`, `sed`, `curl`)

### Document Platform Requirements

```yaml
compatibility: Works on macOS and Linux. Windows requires WSL. Needs git and docker.
```

### Handle Platform Differences

```markdown
## Platform notes

- **Gemini CLI**: User will be prompted to approve skill activation
- **Codex**: Can invoke explicitly with `$skill-name`
- **Claude Code**: Activates automatically based on task
```

---

## Common Mistakes to Avoid

### ❌ Vague Descriptions
```yaml
description: A useful skill for developers.
```

### ❌ No Examples
Skills without examples leave agents guessing about expected behavior.

### ❌ Assuming Context
Don't assume the agent knows things not stated in the skill.

### ❌ Overly Long SKILL.md
If your SKILL.md is over 1000 lines, split into references.

### ❌ Untested Scripts
Always test scripts before including them.

### ❌ Missing Error Handling
Document what to do when things go wrong.

### ❌ Inconsistent Formatting
Use consistent Markdown formatting throughout.

---

## Checklist Before Publishing

- [ ] Name is valid (lowercase, hyphens, matches directory)
- [ ] Description clearly explains what AND when
- [ ] SKILL.md is under 500 lines
- [ ] At least one concrete example included
- [ ] Error cases documented
- [ ] Scripts tested and working
- [ ] No hardcoded secrets or credentials
- [ ] Cross-platform considerations noted
- [ ] Validated with `skills-ref validate`

---

*For the complete specification, see https://agentskills.io/specification*
