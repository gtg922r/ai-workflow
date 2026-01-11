## Provider differences + installation instructions

This reference summarizes how three providers consume Agent Skills and how to install a newly created skill for each provider.

### Cross-provider mental model (what stays the same)

Across providers, a skill is still:

- A directory named `skill-name/`
- Containing `SKILL.md` with YAML frontmatter (`name`, `description`) and Markdown instructions
- Optionally containing `scripts/`, `references/`, `assets/`
- Discovered via **metadata first** (name/description), then **activated** to load full instructions (progressive disclosure)

### Gemini CLI (Google) specifics

#### How Gemini uses skills

- Gemini discovers skills from multiple locations and loads only metadata initially.
- When it decides a skill is relevant, it activates it using an `activate_skill` tool.
- Activation typically triggers a user confirmation prompt and then:
  - injects `SKILL.md` instructions into context
  - grants read access to the skill directory so the agent can load bundled resources

#### Discovery locations (tiers) + precedence

Higher precedence overrides lower when names collide:

1. **Project skills**: `.gemini/skills/`
2. **User skills**: `~/.gemini/skills/`
3. **Extension skills**: bundled inside installed extensions

Precedence: **Project > User > Extension**

#### Install a new skill (Gemini CLI)

Choose scope:

- **Project scope (recommended for teams)**:
  - Create: `.gemini/skills/<skill-name>/SKILL.md` (and optional subfolders)
- **User scope (personal, cross-project)**:
  - Create: `~/.gemini/skills/<skill-name>/SKILL.md`

Enable skills (experimental):

- Toggle `experimental.skills` in settings (or search “Skills” in `/settings`)

Reload / manage:

- In an interactive session: `/skills list`, `/skills reload`, `/skills enable <name>`, `/skills disable <name>`
- From terminal: `gemini skills list|enable|disable`

Notes:

- If multiple skills share a name, the higher-precedence one is used.
- Gemini can show the skill directory tree upon activation, which makes it easier for the model to find bundled resources.

### Claude Code (Anthropic) specifics

#### How Claude Code uses skills

- Claude Code supports **custom skills** as filesystem directories.
- Skills are loaded via progressive disclosure: metadata first, then `SKILL.md` body when triggered.
- The environment constraints vary by “surface” (Claude.ai vs API vs Claude Code); Claude Code generally behaves like a local developer machine.

#### Install a new skill (Claude Code)

Common locations:

- **Project scope**: `.claude/skills/<skill-name>/`
- **User scope**: `~/.claude/skills/<skill-name>/`

Notes:

- Claude has additional constraints in some surfaces (especially Claude API: no network, no installing packages at runtime). If targeting multiple Claude surfaces, document constraints via `compatibility`.
- Claude documentation notes extra validation rules beyond the open spec:
  - the `name` must not be reserved words like `"anthropic"` or `"claude"`
  - frontmatter must not contain XML tags

### OpenAI Codex specifics

#### How Codex uses skills

Codex can use skills in two ways:

- **Implicit invocation**: Codex decides to use a skill based on description match.
- **Explicit invocation**: users can mention a skill (e.g., via `$skill-name` in some UIs) or select from `/skills`.

Codex reads full instructions of invoked skills and any extra references checked into the skill.

#### Discovery locations (scopes) + precedence

Higher precedence overrides lower when names collide (high → low):

- `REPO`: `$CWD/.codex/skills`
- `REPO`: `$CWD/../.codex/skills` (when launched inside a git repo)
- `REPO`: `$REPO_ROOT/.codex/skills`
- `USER`: `~/.codex/skills` (macOS/Linux default)
- `ADMIN`: `/etc/codex/skills`
- `SYSTEM`: bundled with Codex

#### Install a new skill (Codex)

Choose scope:

- **Repo scope**: place at one of the `REPO` locations above (committable)
- **User scope**: `~/.codex/skills/<skill-name>/SKILL.md`
- **Admin scope**: `/etc/codex/skills/<skill-name>/SKILL.md` (if you manage the machine/container)

After installing, restart Codex (or reload skills if the surface supports it).

### Practical authoring implications

- **Discovery quality matters everywhere**: spend time on `description` and include “use when…” keywords.
- **Name collisions resolve differently by location**: don’t “fork” a skill name unless you intend an override.
- **Surface constraints differ**: if your skill requires network access, credentials, or installs packages, document this in `compatibility` and add safe fallbacks.
