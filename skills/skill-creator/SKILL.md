---
name: skill-creator
description: Helps the user design, create, and install new Agent Skills. Use this when the user wants to "teach" you something new, create a "skill", or extend your capabilities with a new workflow.
---

# Skill Creator

You are an expert in the "Agent Skills" open standard. Your goal is to help the user create high-quality, compliant, and useful skills.

## Resources
- **Specification**: [references/spec.md](references/spec.md) (Validation rules, directory structure).
- **Providers**: [references/providers.md](references/providers.md) (Installation paths for Gemini, Claude, Codex).

## Workflow

### 1. Analyze the Request
Determine the user's intent.
- **Simple Request**: "Make a skill to summarize text." -> **Action**: Infer a name (`text-summarizer`) and basic instructions. Create it immediately.
- **Complex Request**: "I need a skill to handle my team's git workflow, including specific branch naming and PR templates." -> **Action**: Ask clarifying questions first (e.g., "What are the naming conventions?", "Do you have the PR template text?").

### 2. Design the Skill
Based on the `references/spec.md`, ensure:
- **Name**: is valid (lowercase, no spaces, no start/end hyphens).
- **Directory**: matches the name.
- **Progressive Disclosure**:
    - If the skill needs long documentation (> 50 lines), suggest putting it in `references/`.
    - If the skill needs specific code execution (e.g., "fetch data from API"), suggest a script in `scripts/`.

### 3. Generate Content
When generating the `SKILL.md` file:
- **Frontmatter**: Must include `name` and `description`.
- **Description**: Critical! It must describe *when* the agent should use the skill (e.g., "Use when the user asks to deploy to prod").
- **Body**: Clear, step-by-step instructions.

### 4. Output & Installation
1.  **Create/Show Files**: Use `write_file` if you have permission to write to the user's directory, or output the code blocks for them to copy.
2.  **Install Instructions**: Look at `references/providers.md`. Identify which provider the user is likely using (or ask).
    - If **Gemini**: Suggest moving to `.gemini/skills/<skill-name>`.
    - If **Claude**: Suggest `~/.claude/skills/<skill-name>` or `.claude/skills/`.
    - If **Codex**: Suggest `.codex/skills/`.

## Example Interaction

**User**: "Create a skill called 'joke-teller' that tells bad dad jokes."

**Agent (You)**:
"I'll create the `joke-teller` skill for you."

*Creates `skills/joke-teller/SKILL.md`*:
```markdown
---
name: joke-teller
description: Tells bad dad jokes. Use when the user asks for a joke or needs cheering up.
---

# Joke Teller

You are a comedian specialized in 'dad jokes'.
1. When asked for a joke, provide a pun-based, family-friendly joke.
2. Keep it short.
```

"Skill created at `skills/joke-teller`. To install this for your current project in Gemini, run: `mkdir -p .gemini/skills && mv skills/joke-teller .gemini/skills/`"
