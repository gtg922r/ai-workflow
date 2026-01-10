---
title: Agent Skills Spec (condensed reference)
source: https://agentskills.io/specification
purpose: Deep reference for validating and authoring skills
---

# Agent Skills Spec — condensed reference

This file is a **portable summary** of the Agent Skills open standard, optimized for authoring and validation workflows.

If you’re authoring a new skill, you generally only need:

- the required `SKILL.md` frontmatter fields (`name`, `description`)
- naming constraints
- recommended structure and progressive disclosure conventions

## Directory structure (minimum)

A skill is a directory containing at minimum a `SKILL.md` file:

```
skill-name/
└── SKILL.md
```

Optional directories (recommended conventions):

- `scripts/`: executable code the agent can run
- `references/`: additional documentation loaded on demand
- `assets/`: templates/resources (schemas, boilerplate, sample data)

## `SKILL.md` format

`SKILL.md` must contain:

1. YAML frontmatter
2. Markdown body (instructions)

### Frontmatter (required)

```yaml
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

### Frontmatter (optional fields)

```yaml
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents.
license: Apache-2.0
compatibility: Requires git, docker, jq, and access to the internet
metadata:
  author: example-org
  version: "1.0"
allowed-tools: Bash(git:*) Bash(jq:*) Read
---
```

Notes:

- `allowed-tools` is **experimental** and support varies by agent/provider.
- `compatibility` is optional; include only when environment constraints matter.

## Field constraints (validation)

### `name` (required)

Constraints:

- 1–64 characters
- lowercase letters, numbers, and hyphens only (`a-z`, `0-9`, `-`)
- must not start or end with `-`
- must not contain consecutive hyphens (`--`)
- must match the parent directory name

Valid examples:

```yaml
name: pdf-processing
```

Invalid examples:

```yaml
name: PDF-Processing   # uppercase not allowed
```

```yaml
name: -pdf             # cannot start with hyphen
```

```yaml
name: pdf--processing  # consecutive hyphens not allowed
```

### `description` (required)

Constraints:

- 1–1024 characters, non-empty

Best practice:

- describe **what** it does and **when to use it**
- include **keywords** a user will say, to help discovery

Good example:

```yaml
description: Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.
```

Poor example:

```yaml
description: Helps with PDFs.
```

### `compatibility` (optional)

Constraints:

- if present, 1–500 characters

Use it to note:

- intended product(s) or surface(s)
- system package requirements
- expected network access or restrictions

### `metadata` (optional)

- arbitrary key/value map (strings recommended)
- make key names reasonably unique to avoid collisions

### `license` (optional)

- license name or reference to a bundled license file

## Body content (instructions)

The Markdown body has **no strict structure requirements**. Write what helps an agent do the task correctly.

Recommended sections:

- Step-by-step workflow
- Examples of inputs/outputs
- Common edge cases

## Progressive disclosure (recommended)

Skills should minimize context use by loading information in stages:

1. **Metadata**: `name` and `description` are loaded at startup for all skills
2. **Instructions**: full `SKILL.md` body is loaded only when the skill is activated
3. **Resources**: referenced files/scripts are loaded/executed only as needed

Recommended guidance:

- Keep `SKILL.md` under ~500 lines.
- Move long references/checklists/schemas into `references/`.

## File references (best practices)

When referencing other files in your skill, use **relative paths from the skill root**:

```markdown
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script:
scripts/extract.py
```

Recommended:

- keep references “one level deep” from `SKILL.md`
- avoid deep chains of nested references

## Validation tooling

The `skills-ref` reference library can validate skills:

```bash
skills-ref validate ./my-skill
```

This checks frontmatter validity and naming conventions.

