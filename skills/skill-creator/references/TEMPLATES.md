## Templates and patterns

Use these as starting points when creating new skills.

### Minimal `SKILL.md` template (good for simple skills)

```markdown
---
name: <skill-name>
description: <what it does>. Use when <trigger keywords / user phrasing>.
---

# <Human-friendly title>

## When to use this skill
- Use when ...
- Do not use when ...

## Inputs you may receive
- ...

## Workflow
1. ...
2. ...
3. ...

## Output format
- ...

## Edge cases and safety
- ...

## Examples
### Example 1
Input:
...

Output:
...
```

### “Nuanced skill” template (adds safety + references)

```markdown
---
name: <skill-name>
description: <capability>. Use when <keywords>. Avoid when <anti-triggers>.
compatibility: Requires <tools>; network access: <yes/no>; intended for <provider/surface>.
metadata:
  author: <team>
  version: "0.1"
---

# <Title>

## Scope and non-goals
- In scope: ...
- Out of scope: ...

## Safety rules (must follow)
- Never ...
- Always ...
- Ask before ...

## Questions to ask (only if needed)
- ...

## Workflow
### 1) Gather context
...

### 2) Execute
...

### 3) Verify
...

## References
- See [REFERENCE](references/REFERENCE.md) for ...
```

### Reference file template (`references/REFERENCE.md`)

Keep these small and specific.

```markdown
## <Topic>

### Key facts
- ...

### Decision table
| If | Then |
| --- | --- |
| ... | ... |
```

### Script wrapper pattern (optional)

If you include scripts, document:

- what the script does
- how to run it
- what inputs it expects
- what output/errors look like

Example snippet for `SKILL.md`:

```markdown
## Validation (optional)

Run:

`python3 scripts/validate_skill.py ./my-skill`

If Python is unavailable, do a manual check using `references/VALIDATION.md`.
```
