# ai-workflow

Personal AI Tools and Workflows: Skills, Extensions, and Custom Commands to support working with AI

## Skills

### skill-creator

An Agent Skill that helps AI agents create new skills conforming to the [Agent Skills open standard](https://agentskills.io).

**Features:**
- Intelligently handles both simple and complex skill requests
- Uses progressive disclosure with detailed reference documentation
- Supports all major agent platforms: Claude Code, Google Gemini CLI, and OpenAI Codex
- Includes installation instructions for each platform
- Provides best practices and complete examples

**Structure:**
```
skill-creator/
├── SKILL.md                         # Main skill instructions
└── references/
    ├── SPECIFICATION.md             # Full Agent Skills spec details
    ├── PROVIDERS.md                 # Platform-specific differences
    ├── INSTALLATION.md              # Installation guides for all platforms
    ├── BEST-PRACTICES.md            # Authoring guidelines
    └── EXAMPLES.md                  # Complete example skills
```

**Installation:**

```bash
# Claude Code
cp -r skill-creator ~/.claude/skills/

# Google Gemini CLI
cp -r skill-creator ~/.gemini/skills/

# OpenAI Codex
cp -r skill-creator ~/.codex/skills/
```

**Usage:**

Once installed, simply ask your agent to create a skill:
- "Create a skill for writing git commit messages"
- "Help me build a code review skill"
- "I need a skill for deploying to AWS"

For simple requests, the skill will create immediately with sensible defaults. For complex requests, it will ask clarifying questions first.

## License

MIT
