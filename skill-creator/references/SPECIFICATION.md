# Agent Skills Specification

> Complete format specification for creating valid Agent Skills.

This document provides the full specification for the Agent Skills standard. Use this reference when you need detailed validation rules or edge case handling.

## Directory Structure

A skill is a directory containing at minimum a `SKILL.md` file:

```
skill-name/
├── SKILL.md          # Required: instructions + metadata
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
└── assets/           # Optional: templates, resources
```

**Important**: The directory name MUST match the `name` field in SKILL.md frontmatter.

## SKILL.md Format

### Frontmatter (YAML)

The file must begin with YAML frontmatter between `---` markers:

```yaml
---
name: skill-name
description: What this skill does and when to use it.
---
```

### Required Fields

| Field | Constraints |
|-------|-------------|
| `name` | 1-64 characters. Lowercase letters, numbers, hyphens only. No leading/trailing/consecutive hyphens. Must match directory name. |
| `description` | 1-1024 characters. Non-empty. Describes what AND when. |

### Optional Fields

| Field | Constraints | Purpose |
|-------|-------------|---------|
| `license` | Any string | License name or reference to bundled file |
| `compatibility` | Max 500 chars | Environment requirements (tools, network, etc.) |
| `metadata` | Key-value map | Arbitrary additional metadata |
| `allowed-tools` | Space-delimited | Pre-approved tools (experimental) |

## Name Field Validation

### Valid Names
- `pdf-processing`
- `code-review`
- `data-analysis`
- `my-skill-v2`
- `a` (single character is valid)

### Invalid Names
- `PDF-Processing` (uppercase not allowed)
- `-pdf` (cannot start with hyphen)
- `pdf-` (cannot end with hyphen)
- `pdf--processing` (consecutive hyphens not allowed)
- `my skill` (spaces not allowed)
- `my_skill` (underscores not allowed)
- String longer than 64 characters

### Name Regex Pattern
```regex
^[a-z0-9]([a-z0-9-]*[a-z0-9])?$
```

## Description Field Guidelines

The description is the MOST CRITICAL field for skill discovery. Agents use this to decide when to activate a skill.

### Good Descriptions
```yaml
description: Extract text and tables from PDF files, fill PDF forms, and merge multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.
```

```yaml
description: Review code for style, security vulnerabilities, and performance issues. Activate when the user asks for code review, feedback on code, or to check their changes.
```

### Poor Descriptions
```yaml
description: Helps with PDFs.  # Too vague
```

```yaml
description: A skill for doing things.  # Meaningless
```

### Description Formula
> [What it does] + [When to use it] + [Trigger keywords]

## Body Content

Everything after the frontmatter closing `---` is the instruction body. There are no format restrictions, but follow these guidelines:

### Recommended Structure
```markdown
# Skill Name

## When to use this skill
[Activation conditions and triggers]

## Prerequisites  
[Any required setup or dependencies]

## Instructions
[Step-by-step workflow]

## Examples
[Concrete usage examples]

## Edge Cases
[Error handling and special situations]

## References
[Links to bundled files for more detail]
```

### Size Guidelines
- Keep SKILL.md under 500 lines
- Target under 5000 tokens for main instructions
- Move detailed reference material to separate files
- Use progressive disclosure

## Progressive Disclosure

Skills should load context efficiently in three levels:

### Level 1: Metadata (~100 tokens)
Only `name` and `description` loaded at agent startup.

### Level 2: Instructions (<5000 tokens recommended)
Full SKILL.md body loaded when skill is activated.

### Level 3: Resources (as needed)
Additional files in `scripts/`, `references/`, `assets/` loaded only when referenced.

## Optional Directories

### scripts/

Executable code the agent can run:
- Should be self-contained
- Include helpful error messages
- Handle edge cases gracefully
- Document dependencies

Supported languages vary by agent platform. Common: Python, Bash, JavaScript.

### references/

Additional documentation loaded on demand:
- `REFERENCE.md` - Detailed technical reference
- Domain-specific files (`api.md`, `schema.md`)
- Keep individual files focused

### assets/

Static resources:
- Templates (code, document, config)
- Example data files
- Schemas, lookup tables

## File References

Reference other skill files using relative paths:

```markdown
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script:
scripts/extract.py
```

Keep references one level deep. Avoid deeply nested chains.

## Validation

Use the official validation library:

```bash
npx skills-ref validate ./my-skill
```

Or programmatically:
```javascript
import { validateSkill } from 'skills-ref';
const result = await validateSkill('./my-skill');
```

## Complete Valid Example

```yaml
---
name: api-testing
description: Test REST APIs with automated request generation and response validation. Use when testing endpoints, debugging API issues, or validating API contracts.
license: MIT
compatibility: Requires curl or httpie, jq for JSON processing
metadata:
  author: api-team
  version: "2.1"
allowed-tools: Bash(curl:*) Bash(jq:*) Read Write
---

# API Testing

## When to use this skill
Activate when the user wants to:
- Test API endpoints
- Debug API responses
- Validate request/response formats
- Generate API test cases

## Prerequisites
- `curl` or `httpie` installed
- `jq` for JSON processing
- Access to the target API

## Testing Workflow

1. **Identify the endpoint**: Get the URL, method, and expected payload
2. **Construct the request**: Build appropriate headers and body
3. **Execute and capture**: Run the request, save the response
4. **Validate response**: Check status code, headers, body structure
5. **Report results**: Summarize pass/fail with details

## Example

Testing a user creation endpoint:

\`\`\`bash
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com"}' \
  | jq .
\`\`\`

Expected: 201 Created with user object containing `id` field.

## Error Handling

- **Connection refused**: Check if API server is running
- **401 Unauthorized**: Verify authentication credentials
- **422 Unprocessable**: Validate request body format

## References

See [references/HTTP-STATUS-CODES.md](references/HTTP-STATUS-CODES.md) for status code meanings.
See [references/AUTH-PATTERNS.md](references/AUTH-PATTERNS.md) for authentication strategies.
```

---

*Full specification: https://agentskills.io/specification*
