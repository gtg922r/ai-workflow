---
title: Provider notes (Gemini CLI, Claude, Codex)
purpose: Installation, discovery locations, and behavioral differences
---

# Provider notes: Gemini CLI vs Claude vs OpenAI Codex

This reference captures the **practical differences** between major skill consumers and how to **install** skills after you generate them.

## Common ground (all providers)

- A skill is a folder containing `SKILL.md` with YAML frontmatter (`name`, `description`) and a Markdown body.
- Skills are discovered via **progressive disclosure**:
  - metadata is loaded at startup
  - full `SKILL.md` body is loaded only when the skill is used/activated
  - additional files are loaded only when referenced

## Google Gemini CLI

### Enablement

- Skills are an **experimental** feature.
- Enable via config toggle `experimental.skills` (or search “Skills” in `/settings` interactive UI).

### Discovery locations (tiers) and precedence

Gemini CLI discovers skills from:

1. **Project**: `.gemini/skills/` (highest precedence)
2. **User**: `~/.gemini/skills/`
3. **Extension**: skills bundled with installed extensions (lowest precedence)

If multiple skills share the same `name`, **Project > User > Extension** wins.

### Managing skills

- Interactive: `/skills list`, `/skills enable <name>`, `/skills disable <name>`, `/skills reload`
- Terminal: `gemini skills list`, `gemini skills enable <name>`, `gemini skills disable <name>`

### Activation and consent (security)

Gemini activates skills via an `activate_skill` flow and shows a consent prompt that includes:

- the skill’s name and purpose
- the directory path it will gain access to

After approval, Gemini can read files inside the skill directory.

### Install instructions (Gemini CLI)

1. Create a skill folder named exactly like the frontmatter `name` (e.g. `my-skill/`).
2. Place it in one of:
   - project: `.gemini/skills/my-skill/`
   - user: `~/.gemini/skills/my-skill/`
3. Reload skills:
   - in-session: `/skills reload`
   - or terminal: `gemini skills list` (and use enable/disable as needed)

## Anthropic Claude (multiple “surfaces”)

Claude supports skills across multiple products; **custom skills do not automatically sync across surfaces**.

### Claude Code (filesystem-based)

#### Discovery locations

Typical locations:

- project: `.claude/skills/<skill-name>/`
- user: `~/.claude/skills/<skill-name>/`

(Exact behavior may vary by version/config; these are the common conventions.)

#### Runtime characteristics

- Skills are filesystem-based; Claude reads `SKILL.md` and other referenced files from disk.
- Scripts are typically executed via shell tooling provided by the product.

#### Install instructions (Claude Code)

1. Create `my-skill/` containing `SKILL.md`.
2. Copy it to `.claude/skills/my-skill/` (project) or `~/.claude/skills/my-skill/` (user).
3. Restart/refresh Claude Code so it re-scans skills (if it doesn’t auto-detect).

### Claude.ai (web app)

#### Install model

- Custom skills are typically uploaded as a **zip** via Settings (plan-dependent; code execution must be enabled).
- Skills are **per-user** in Claude.ai; teammates must upload separately.

#### Install instructions (Claude.ai)

1. Zip the skill folder so that `SKILL.md` is at the zip root inside `<skill-name>/SKILL.md`.
2. Upload via Claude.ai Settings → Features (location may vary over time).
3. Start a new chat/session so the uploaded skill is available.

### Claude API (container + upload)

#### Install model

- Skills must be uploaded to the API (`/v1/skills` endpoints).
- Requires enabling relevant beta headers (skills + code execution + files API).
- Custom skills are typically shared workspace-wide (org/workspace scope).

#### Runtime constraints (important)

- **No network access** for skill execution (as documented in the referenced spec).
- **No runtime package installation**; only preinstalled packages are available in the execution environment.

#### Install instructions (Claude API)

High-level:

1. Create and zip the skill directory.
2. Upload to the Skills API to obtain a `skill_id`.
3. Reference that `skill_id` when invoking the code execution container/tool.

### Extra Claude-specific naming constraints

Some Claude surfaces/documentation impose extra constraints beyond the open spec (e.g., reserved words like “anthropic”, “claude”). Prefer conservative naming if you want maximum portability.

## OpenAI Codex (CLI + IDE extensions)

### Invocation modes

- **Explicit**: user selects skills via `/skills` UI or mentions a skill with `$skill-name`.
- **Implicit**: Codex can choose a skill when the task matches the skill’s `description`.

### Discovery locations (scopes) and precedence

Codex searches multiple locations; higher precedence overrides lower for same-named skills.

Common locations (high → low):

- repo scope: `$CWD/.codex/skills`
- repo scope (parent): `$CWD/../.codex/skills` (when in a git repo)
- repo root: `$REPO_ROOT/.codex/skills`
- user: `~/.codex/skills` (default on macOS/Linux)
- admin: `/etc/codex/skills`
- system: bundled with Codex

### Install instructions (Codex)

1. Create `my-skill/` with `SKILL.md`.
2. Copy it into one of:
   - repo: `<repo>/.codex/skills/my-skill/`
   - user: `~/.codex/skills/my-skill/`
3. Restart Codex (or reload if your surface supports it).
4. Use it explicitly by mentioning `$my-skill` or selecting it via `/skills`, or let Codex invoke it implicitly.

