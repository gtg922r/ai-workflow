## Agent Skills spec (reference)

This reference summarizes the Agent Skills open standard described at `agentskills.io` and is intended to be used as the “source of truth” when authoring or validating skills.

### Skill = directory with `SKILL.md`

Minimum valid structure:

```
skill-name/
└── SKILL.md
```

Common optional directories:

```
skill-name/
├── SKILL.md
├── scripts/      # executable helpers (bash/python/js, depends on agent)
├── references/   # extra docs loaded on demand
└── assets/       # templates, examples, static resources
```

### `SKILL.md` format

`SKILL.md` must contain:

- YAML frontmatter
- followed by a Markdown body

Frontmatter delimiter is the standard `---` at start and end of the YAML block.

#### Required frontmatter fields

```yaml
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

#### Optional frontmatter fields

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

Field constraints (Agent Skills spec):

| Field | Required | Constraints |
| --- | --- | --- |
| `name` | Yes | Max 64 chars. Lowercase letters, numbers, hyphens only. No leading/trailing hyphen. No consecutive hyphens. Must match parent directory name. |
| `description` | Yes | 1–1024 chars. Non-empty. Describes what the skill does **and when to use it** (discovery keywords matter). |
| `license` | No | License name or reference to a bundled license file. |
| `compatibility` | No | 1–500 chars if present. Use only when environment requirements exist (product/system/network). |
| `metadata` | No | Arbitrary key/value mapping (strings). |
| `allowed-tools` | No | Space-delimited list of pre-approved tools (experimental; support varies). |

#### `name` rules (canonical)

`name` must:

- be 1–64 characters
- contain only `a-z`, `0-9`, and `-`
- not start or end with `-`
- not contain `--`
- match the folder name

Examples:

- ✅ `pdf-processing`
- ✅ `data-analysis`
- ❌ `PDF-Processing` (uppercase)
- ❌ `-pdf` (leading hyphen)
- ❌ `pdf--processing` (consecutive hyphens)

#### `description` guidance

The `description` is the primary discovery signal. It should:

- mention what the skill does
- include “use when…” phrasing and task keywords users will say

Good:

> Extracts text and tables from PDFs, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.

Poor:

> Helps with PDFs.

### Body content (Markdown)

The Markdown body has no required structure; write what helps the agent do the task reliably.

Recommended content:

- step-by-step workflow
- examples (input → output)
- edge cases and common failures
- safety constraints (“don’t do X without confirmation”)

### Progressive disclosure (how to keep skills efficient)

Skills should be structured so agents load content in stages:

1. **Metadata**: `name` + `description` are loaded at startup for all enabled skills
2. **Instructions**: full `SKILL.md` body is loaded when the skill is activated
3. **Resources**: referenced files in `scripts/`, `references/`, `assets/` are loaded only when needed

Guidance:

- keep `SKILL.md` under ~500 lines
- move detailed docs into `references/` and link them from `SKILL.md`
- keep reference files focused and shallow

### Referencing other files

Use relative paths from the skill root:

- `references/REFERENCE.md`
- `scripts/validate.py`
- `assets/template.yaml`

Avoid deep nested chains (don’t make references that require further references to understand basics).

### Validation

The spec recommends validating skills with the `skills-ref` reference library:

```bash
skills-ref validate ./my-skill
```
