# Scripts

This skill includes small, dependency-free utilities that help agents create and validate skills deterministically.

## validate_skill.py

Validates a skill directory against the core Agent Skills spec constraints:

```bash
python3 scripts/validate_skill.py ./my-skill
```

## scaffold_skill.py

Bootstraps a new skill folder with a compliant `SKILL.md`:

```bash
python3 scripts/scaffold_skill.py --output-root . --name my-skill --description "Does X. Use when Y." --with-references --with-scripts
```

