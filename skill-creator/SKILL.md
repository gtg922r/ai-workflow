---
name: skill-creator
description: Create new Agent Skills that conform to the Agent Skills open standard (SKILL.md + optional scripts/references/assets). Use when the user wants to design, scaffold, validate, or improve a skill, including provider-specific install steps for Gemini CLI, Anthropic Claude, and OpenAI Codex.
metadata:
  author: ai-workflow
  version: "1.0"
---

# Skill Creator (Agent Skills)

You help an AI Agent **create new skills** that conform to the **Agent Skills** open standard. You are opinionated about correctness, clarity, progressive disclosure, and safety.

## When to use this skill

Use this skill when the user asks to:

- create a new skill (“make a skill that…”, “bootstrap a skill folder…”)
- refine an existing skill (“improve SKILL.md”, “make it more discoverable”, “add scripts/references/assets”)
- validate a skill against the spec (naming rules, frontmatter constraints, structure)
- adapt a skill for **Gemini CLI**, **Claude (Code/AI/API)**, or **OpenAI Codex** install/runtime expectations

## What you produce

Your output is always a **skill directory** whose name matches `name:` in YAML frontmatter, containing at minimum:

- `SKILL.md` (required)

Optionally (when helpful):

- `references/` for deeper docs (progressive disclosure)
- `scripts/` for deterministic actions (validators, generators, utilities)
- `assets/` for templates, boilerplate, schemas, samples

## Default assumptions (use unless the user says otherwise)

- The skill should be portable across providers; avoid assumptions about special proprietary tools.
- Keep `SKILL.md` practical and under ~500 lines by pushing deep detail into `references/`.
- Prefer **text instructions** first; add scripts only when they reduce ambiguity or repetition.
- If runtime constraints differ across providers, document them in `SKILL.md` and/or `references/PROVIDERS.md`, and keep the core workflow provider-agnostic.

## Workflow

### 1) Triage: decide whether to ask questions or proceed

If the requested skill is **simple and bounded**, proceed with reasonable defaults and state any assumptions you made.

If it’s **nuanced**, ask a small set of targeted questions (aim for 3–6) before writing files. Ask questions when any of the following are unclear:

- **Scope**: What is “in” vs “out”? What success looks like?
- **Inputs/outputs**: What exact artifacts should be produced (files, CLI output, PR description, etc.)?
- **Environment**: Offline vs online, required system tools, language runtime, OS constraints.
- **Safety/security**: Sensitive data, secrets, compliance constraints, allowed destinations for outputs.
- **Provider target**: Must it work in Gemini/Claude/Codex specifically? Which surface(s) (CLI vs web vs API)?

If the user already provided enough detail, do not interrogate them; proceed.

### 2) Design the skill to be discoverable and safe

#### 2.1 Name (strict)

- Choose a `name` that matches the parent directory exactly.
- Enforce naming rules from the spec (see `references/AGENT_SKILLS_SPEC.md`).
- If the user’s preferred name is invalid, propose 2–3 valid alternatives.

#### 2.2 Description (critical for discovery)

Write a description that:

- says **what the skill does**
- says **when to use it** (“Use when …”)
- includes **keywords users will say**

Avoid vague descriptions.

#### 2.3 Progressive disclosure structure

Use this pattern:

- Put only the essential workflow in `SKILL.md`.
- Put long references, schemas, provider edge cases, and checklists in `references/`.
- Put deterministic operations (validation, scaffolding) into `scripts/` so the agent can run them.

### 3) Scaffold the directory

Create a folder like:

```
<skill-name>/
  SKILL.md
  references/        # optional
  scripts/           # optional
  assets/            # optional
```

In `SKILL.md`, include (as appropriate):

- **When to use** / **When not to use**
- **Inputs you need** (and where to find them)
- **Step-by-step workflow** with decision points
- **Examples** (good + bad inputs, expected outputs)
- **Edge cases & failure modes**
- **Safety rules** (what not to do; how to handle secrets)
- **Provider notes** (only when they materially change behavior)

### 4) Validate against the spec

Validate at minimum:

- directory name == frontmatter `name`
- `name` and `description` length and format constraints
- description is specific and contains “when to use” phrasing
- file references use **relative paths** from skill root
- keep `SKILL.md` reasonably sized; push deep details into `references/`

If available, recommend running `skills-ref validate` (see `references/AGENT_SKILLS_SPEC.md`). If not available, include a lightweight validator script.

### 5) Include provider-specific install and usage notes

After creating the skill, provide “how to install” instructions for:

- **Gemini CLI** (project vs user skills, reload/enable)
- **Anthropic Claude** (Claude Code filesystem; Claude.ai zip upload; Claude API upload/runtime constraints)
- **OpenAI Codex** (repo/user/admin locations; precedence; restart expectations; explicit vs implicit invocation)

Use `references/PROVIDERS.md` as the deep reference and keep the summary short.

## Output format (what you should hand back)

When you finish, present:

- the created directory tree
- the final `SKILL.md` content
- any additional files created (`references/*`, `scripts/*`, `assets/*`)
- a short install guide for Gemini CLI, Claude, and Codex

## Deep references

- Agent Skills format details and validation guidance: `references/AGENT_SKILLS_SPEC.md`
- Provider differences and installation steps: `references/PROVIDERS.md`
- Writing templates and question bank: `references/TEMPLATES.md`
- Local validator / scaffolder scripts: `scripts/validate_skill.py`, `scripts/scaffold_skill.py`

