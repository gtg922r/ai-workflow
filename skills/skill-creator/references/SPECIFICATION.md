# Agent Skills Specification Reference

This document contains the complete format specification for Agent Skills based on the [official standard](https://agentskills.io/specification).

## Directory Structure

A skill is a directory containing at minimum a `SKILL.md` file:

```
skill-name/
├── SKILL.md          # Required
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
└── assets/           # Optional: templates, resources
```

## SKILL.md Format

The `SKILL.md` file must contain YAML frontmatter followed by Markdown content.

### Required Frontmatter Fields

```yaml
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

### Optional Frontmatter Fields

```yaml
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents.
license: Apache-2.0
compatibility: Requires pdfplumber, PyPDF2
metadata:
  author: example-org
  version: "1.0"
  tags: pdf documents extraction
allowed-tools: Bash(python:*) Read Write
---
```

## Field Specifications

### `name` Field (Required)

| Constraint | Requirement |
|------------|-------------|
| Length | 1-64 characters |
| Characters | Lowercase letters (`a-z`), numbers (`0-9`), hyphens (`-`) |
| Start/End | Cannot start or end with hyphen |
| Consecutive | No consecutive hyphens (`--`) |
| Directory | Must match parent directory name |

**Valid examples:**
- `pdf-processing`
- `code-review`
- `data-analysis`
- `my-skill-v2`

**Invalid examples:**
- `PDF-Processing` (uppercase not allowed)
- `-pdf-skill` (starts with hyphen)
- `skill--name` (consecutive hyphens)
- `my_skill` (underscores not allowed)

### `description` Field (Required)

| Constraint | Requirement |
|------------|-------------|
| Length | 1-1024 characters |
| Content | Non-empty, describes what AND when |
| Keywords | Include specific task-matching terms |

**Good example:**
```yaml
description: Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.
```

**Poor example:**
```yaml
description: Helps with PDFs.
```

### `license` Field (Optional)

Specifies the license applied to the skill. Keep it short—either the license name or reference to a bundled file.

```yaml
license: MIT
```

```yaml
license: Proprietary. See LICENSE.txt for terms.
```

### `compatibility` Field (Optional)

| Constraint | Requirement |
|------------|-------------|
| Length | 1-500 characters (if provided) |
| Content | Environment requirements, dependencies |

```yaml
compatibility: Requires Python 3.9+, pdfplumber, and network access
```

```yaml
compatibility: Designed for Claude Code. Requires git and docker.
```

### `metadata` Field (Optional)

A map of string keys to string values for additional properties.

```yaml
metadata:
  author: your-name
  version: "2.1"
  category: development
  tags: testing automation ci
```

### `allowed-tools` Field (Optional, Experimental)

Space-delimited list of pre-approved tools. Support varies by agent implementation.

```yaml
allowed-tools: Bash(git:*) Bash(npm:*) Read Write Edit
```

## Body Content Guidelines

The Markdown body after frontmatter contains skill instructions. No format restrictions, but structure for clarity:

### Recommended Sections

1. **Title** (`# Skill Name`)
2. **When to Use** - Trigger conditions
3. **How to Use** - Step-by-step instructions
4. **Examples** - Input/output demonstrations
5. **Edge Cases** - Error handling and special situations

### Token Budget

| Content | Recommended Limit |
|---------|-------------------|
| SKILL.md body | < 5000 tokens (~500 lines) |
| Individual reference files | Focused, single-topic |
| Total activated content | Minimize for context efficiency |

## Optional Directories

### `scripts/`

Executable code that agents can run:

```
scripts/
├── validate.py
├── transform.sh
└── helpers/
    └── utils.py
```

**Script requirements:**
- Self-contained or clearly document dependencies
- Include helpful error messages
- Handle edge cases gracefully
- Common languages: Python, Bash, JavaScript, TypeScript

### `references/`

Additional documentation loaded on demand:

```
references/
├── REFERENCE.md      # Detailed technical reference
├── API.md            # API documentation
├── TROUBLESHOOTING.md # Common issues and solutions
└── schemas/
    └── config.json   # Configuration schemas
```

**Reference file guidelines:**
- Keep files focused on single topics
- Use clear, descriptive filenames
- Avoid deeply nested structures
- Reference from SKILL.md when needed

### `assets/`

Static resources and templates:

```
assets/
├── templates/
│   ├── report.html
│   └── config.yaml
├── examples/
│   └── sample-input.json
└── data/
    └── lookup-table.csv
```

## Progressive Disclosure Model

Skills use three-level progressive disclosure:

### Level 1: Discovery (~100 tokens)
- Loaded at agent startup
- Contains only `name` and `description`
- Used for skill matching and selection

### Level 2: Activation (< 5000 tokens)
- Loaded when skill is triggered
- Contains full SKILL.md body
- Primary instructions for the agent

### Level 3: Resources (as needed)
- Loaded on demand during execution
- Referenced files from `scripts/`, `references/`, `assets/`
- Keeps context efficient

## File References

When referencing files within your skill, use relative paths from the skill root:

```markdown
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script:
\`\`\`bash
python scripts/extract.py input.pdf
\`\`\`

Use the template at `assets/templates/report.html`.
```

**Best practices:**
- Keep references one level deep from SKILL.md
- Avoid circular references
- Don't create deeply nested reference chains

## Validation

Use the official validation tool:

```bash
# Install the reference library
npm install -g @agentskills/skills-ref

# Validate a skill
skills-ref validate ./my-skill
```

### Validation Checklist

- [ ] SKILL.md exists at skill root
- [ ] Valid YAML frontmatter with `---` delimiters
- [ ] `name` field present and valid format
- [ ] `name` matches directory name
- [ ] `description` field present and non-empty
- [ ] No syntax errors in frontmatter
- [ ] Markdown body is valid
- [ ] Referenced files exist
- [ ] Scripts are executable (if applicable)

## Complete Example

```
code-review/
├── SKILL.md
├── scripts/
│   └── diff-analyzer.py
├── references/
│   ├── STYLE-GUIDE.md
│   └── SECURITY-CHECKLIST.md
└── assets/
    └── templates/
        └── review-template.md
```

**SKILL.md:**

```markdown
---
name: code-review
description: Perform comprehensive code reviews following team standards. Use when asked to review code, check changes, or provide feedback on pull requests.
metadata:
  author: dev-team
  version: "1.0"
---

# Code Review

## When to Use
Activate when the user wants to:
- Review code changes or pull requests
- Get feedback on code quality
- Check for security issues or bugs

## Review Process

1. **Analyze Changes**
   Run the diff analyzer for structured output:
   \`\`\`bash
   python scripts/diff-analyzer.py
   \`\`\`

2. **Check Style**
   Review against [style guide](references/STYLE-GUIDE.md)

3. **Security Scan**
   Follow [security checklist](references/SECURITY-CHECKLIST.md)

4. **Provide Feedback**
   Use the template at `assets/templates/review-template.md`

## Output Format

Structure feedback as:
- **Summary**: One-line overview
- **Strengths**: What's done well (2-3 points)
- **Suggestions**: Non-blocking improvements
- **Required**: Must-fix issues before merge
```
