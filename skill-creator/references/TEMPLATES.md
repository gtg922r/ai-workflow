---
title: Authoring templates (SKILL.md + files) and question bank
purpose: Copy/paste scaffolds for skill generation
---

# Templates and question bank

Use these templates to quickly create high-quality skills that remain discoverable and portable across providers.

## SKILL.md template (recommended)

```markdown
---
name: <skill-name>  # must match folder name
description: <what it does>. Use when <keywords users say / situations>.
license: <optional>
compatibility: <optional: environment/runtime constraints>
metadata:
  author: <optional>
  version: "1.0"
---

# <Human-friendly Skill Title>

## When to use this skill
- Use when ...
- Use when ...

## When NOT to use this skill
- Do not use when ...

## Inputs you need
- **Input A**: where it comes from, format
- **Input B**: where it comes from, format

## Workflow
1. Step ...
2. Step ...
3. Decision point: if ..., then ...

## Output expectations
- The output should include ...
- The output must NOT include ...

## Examples
### Example 1: <short label>
**Input**
...

**Expected output**
...

## Edge cases and failure modes
- If ..., then ...
- If ..., then ...

## Safety and security
- Never exfiltrate secrets.
- If sensitive data is detected, ...

## References
- See `references/REFERENCE.md` for ...
```

## Simple skill template (for small, bounded skills)

Use this when the behavior is straightforward and doesn’t need scripts.

```markdown
---
name: <skill-name>
description: <what it does>. Use when <clear trigger words>.
---

# <Skill Title>

## Quick start
When asked to <task>, do:
1. ...
2. ...

## Checklist
- [ ] ...
- [ ] ...
```

## Reference file template (`references/REFERENCE.md`)

```markdown
# Reference

## Definitions
- **Term**: meaning

## Detailed procedures
...

## FAQs
...
```

## Suggested “discoverable” description patterns

Good descriptions almost always include:

- a crisp capability statement (“Generate …”, “Review …”, “Extract …”)
- explicit triggers (“Use when the user asks … / mentions …”)
- keywords (“PDF”, “invoice”, “SOC2”, “migration”, “Terraform”, etc.)

Example formula:

> “<Does X, Y, Z>. Use when <user mentions A/B/C> or when <situation D>.”

## Question bank (ask only when needed)

Pick the smallest set that resolves ambiguity.

### Scope & success

- What is the exact outcome you want this skill to produce (files, commands, a report, a PR, etc.)?
- What is explicitly out of scope?
- Should it optimize for correctness, speed, cost, or safety?

### Inputs/outputs

- What are the inputs (format, location, example)?
- What output format do you want (markdown report, JSON, patch files, etc.)?
- Should it generate templates, or only instructions?

### Environment & dependencies

- Must it run offline? Is network access allowed?
- Which tools are guaranteed available (git, docker, jq, python, node)?
- Any OS constraints (Linux/macOS/Windows)?

### Provider targeting

- Which providers/surfaces must be supported (Gemini CLI, Claude Code, Claude.ai, Claude API, Codex CLI/IDE)?
- Any restrictions on tool usage or code execution?

### Safety/security/compliance

- Will it touch secrets, credentials, PII, production systems, or regulated data?
- What should it do if it encounters sensitive data?
- Are there compliance requirements (SOC2, HIPAA, GDPR) that affect logging/output?

