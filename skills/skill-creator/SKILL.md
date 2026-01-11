---
name: skill-creator
description: Create new Agent Skills that conform to the Agent Skills open standard (SKILL.md frontmatter + instructions), using progressive disclosure and optional scripts/references/assets. Use when the user asks to create, scaffold, or improve a skill, or needs provider-specific install guidance for Gemini CLI, Claude Code, or OpenAI Codex.
license: Apache-2.0
metadata:
  author: ai-workflow-tools
  version: "1.0"
---

# Skill Creator

Create high-quality, spec-compliant Agent Skills from a natural-language request. This skill is for **authoring** skills (folders with `SKILL.md` plus optional `scripts/`, `references/`, `assets/`) and for **adapting** a skill to different agent providers.

## When to use this skill

Use this skill when the user wants to:

- Create a new skill directory and `SKILL.md`
- Improve an existing skill (clarity, structure, progressive disclosure, safety)
- Ensure a skill conforms to the Agent Skills standard
- Understand differences across Gemini CLI, Claude Code, and OpenAI Codex skills (discovery, activation, locations, constraints)
- Add optional `scripts/`, `references/`, or `assets/` to make a skill more reliable

## Output contract (what you must produce)

When creating a new skill, produce:

- A new folder named exactly like the skill `name`
- `SKILL.md` at the folder root with valid YAML frontmatter (`name`, `description`) and clear Markdown instructions
- Optional supporting files only when helpful (keep the root `SKILL.md` concise)
- Installation instructions for Gemini CLI, Claude Code, and OpenAI Codex (unless the user explicitly only targets one provider)

When improving an existing skill, produce:

- Concrete edits to make it conform to spec and provider constraints
- A short explanation of what changed and why (focused on correctness and usability)

## Authoring workflow

### 1) Classify the request: simple vs. nuanced

Treat as **simple** (make reasonable defaults and proceed) if:

- The skill is a straightforward, single-purpose workflow
- No external systems/accounts are required (or it’s a generic integration pattern)
- Dependencies are standard CLI tools (git, jq) or easily optional

Treat as **nuanced** (ask targeted questions before writing files) if any apply:

- The skill requires credentials, vendor APIs, network access, or data governance constraints
- The skill must be safe against prompt injection / untrusted inputs (e.g., URL fetching, log parsing, document ingestion)
- The workflow varies by environment (CI vs local, monorepo vs polyrepo, regulated domains)
- The user wants cross-provider parity (Gemini + Claude + Codex) with constraints that differ by surface

### 2) If nuanced: ask only the minimum high-signal questions

Ask at most 5–8 questions. Prefer multiple choice. Use these categories:

- **Purpose & success**: What should the skill reliably produce? What does “done” look like?
- **Triggering**: What user phrases/tasks should activate it? What should *not* activate it?
- **Environment**: Local only? CI? Network allowed? Any required tools?
- **Inputs/outputs**: File paths, formats, naming, output destinations
- **Safety**: What data is sensitive? Any restricted operations (delete, network, secrets)?
- **Provider target**: Gemini CLI / Claude Code / Codex (or all three)

If the user can’t answer, choose conservative defaults and document assumptions in `SKILL.md`.

### 3) Choose a spec-compliant `name`

Select a short, descriptive, kebab-case identifier.

Must satisfy the Agent Skills standard, and also consider provider-specific constraints (see `references/PROVIDERS.md`).

If the user gives an invalid name, propose a corrected name and proceed with that.

### 4) Write excellent frontmatter

Always include:

- `name`: must match the folder name
- `description`: the most important discovery signal (include “use when…” keywords)

Optionally include (only if meaningful):

- `license`
- `compatibility` (only when there are real environment requirements)
- `metadata` (author/version, internal tags)
- `allowed-tools` (only if the target agent supports/benefits from it)

### 5) Structure `SKILL.md` for progressive disclosure

Keep `SKILL.md` focused on:

- When to use the skill (activation cues)
- Step-by-step workflow (deterministic and auditable)
- Examples (input → output)
- Common pitfalls / edge cases
- Safety constraints and “do not do” rules

Move deep reference material into `references/` and link it.

### 6) Add scripts only when they increase reliability

Use `scripts/` when you can replace a brittle reasoning step with deterministic computation (validation, formatting, codegen, checks).

Scripts must:

- Have clear usage and error messages
- Avoid destructive operations by default
- Document dependencies (and provide a no-script fallback in instructions)

### 7) Validate the skill

Run the `validate_skill.py` script provided in this skill's `scripts/` directory against the newly created skill folder:

`python3 skills/skill-creator/scripts/validate_skill.py <path-to-new-skill>`

Fix any errors reported by the tool before proceeding.

### 8) Provider-specific packaging and install guidance

After writing the skill, include installation instructions for:

- Gemini CLI (project/user tiers, enablement, reload)
- Claude Code (project/user placement)
- OpenAI Codex (repo/user/admin scopes and precedence)

Use `references/PROVIDERS.md` as the source of truth and keep the `SKILL.md` summary short.

## Quality checklist (must pass before you finish)

- The folder name equals frontmatter `name`
- `name` and `description` meet length/character constraints
- The `description` is specific enough to be discoverable and includes “use when…” cues
- `SKILL.md` instructions are actionable, ordered, and safe
- Long details are moved to `references/` (progressive disclosure)
- File references use relative paths and stay shallow
- Provider differences and install instructions are correct and clearly separated
- The skill passes `skills/skill-creator/scripts/validate_skill.py` without errors

## References

- Agent Skills spec essentials: `references/SPEC.md`
- Provider differences + install instructions: `references/PROVIDERS.md`
- Authoring templates + examples: `references/TEMPLATES.md`
- Validation and naming rules checklist: `references/VALIDATION.md`
