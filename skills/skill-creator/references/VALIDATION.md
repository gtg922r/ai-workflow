## Validation checklist (author + reviewer)

### 1) Directory and file layout

- The skill is a directory named exactly `/<name>/`
- `SKILL.md` exists at the skill root
- Optional folders are only added if useful: `scripts/`, `references/`, `assets/`

### 2) Frontmatter validity (Agent Skills spec)

Required:

- `name` present
- `description` present

`name` constraints:

- 1–64 chars
- matches regex: `^[a-z0-9]+(?:-[a-z0-9]+)*$`
- matches the parent directory name

`description` constraints:

- 1–1024 chars
- includes what the skill does and when to use it (keywords for discovery)

Optional fields (if present):

- `compatibility` is 1–500 chars and only included for real requirements
- `metadata` is a key/value map (strings)
- `allowed-tools` is space-delimited (note: experimental; support varies)

### 3) Provider-specific checks (high-signal)

Gemini CLI:

- Keep `description` keyword-rich (Gemini relies heavily on it for activation)
- Assume an explicit activation step with user consent

Claude (not all surfaces behave the same):

- Avoid reserved words in `name` (Claude docs mention `"anthropic"`, `"claude"`)
- Don’t put XML tags in `name`/`description`
- If targeting Claude API, document stricter runtime constraints (no network; no package installs)

Codex:

- Ensure the skill can be invoked explicitly (users may mention `$skill-name`) and implicitly
- Keep instructions compatible with a repo-first workflow (skills are often checked into `.codex/skills`)

### 4) Instruction quality

- The workflow is step-by-step and auditable
- It has explicit “ask before destructive action” rules
- It includes examples and expected output formats
- It avoids deep reference chains and keeps `SKILL.md` reasonably short (guideline: <500 lines)

### 5) Optional validation tooling

If you have the Agent Skills reference tooling installed, validate via:

```bash
skills-ref validate ./<skill-name>
```

If not, you can use the included script in this repository’s `skill-creator` skill:

```bash
python3 skills/skill-creator/scripts/validate_skill.py ./<skill-name>
```
