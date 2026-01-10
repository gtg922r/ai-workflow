#!/usr/bin/env python3
"""
Scaffold a new Agent Skill directory with a compliant SKILL.md.

This is intentionally dependency-free and produces a conservative, portable
baseline that works across providers.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from typing import Optional


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ScaffoldError(Exception):
    pass


def _title_from_name(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("-"))


def _validate_name(name: str) -> None:
    if not (1 <= len(name) <= 64):
        raise ScaffoldError("`name` must be 1–64 characters.")
    if not NAME_RE.match(name):
        raise ScaffoldError(
            "`name` must match ^[a-z0-9]+(?:-[a-z0-9]+)*$ (lowercase, digits, hyphens; no leading/trailing/consecutive hyphens)."
        )


def _write_text(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _skill_md(name: str, description: str, title: Optional[str], author: Optional[str], version: str) -> str:
    safe_title = title.strip() if title else _title_from_name(name)
    meta = ""
    if author:
        meta = f"\nmetadata:\n  author: {author}\n  version: {version!r}"
    elif version:
        meta = f"\nmetadata:\n  version: {version!r}"

    return f"""---
name: {name}
description: {description}
{meta.lstrip()}
---

# {safe_title}

## When to use this skill
- Use when ...

## When NOT to use this skill
- Do not use when ...

## Inputs you need
- **Input**: ...

## Workflow
1. ...
2. ...

## Output expectations
- Provide ...

## Examples
### Example
**Input**
...

**Expected output**
...

## Edge cases and failure modes
- If ..., then ...

## Safety and security
- Do not expose secrets or sensitive data.
"""


def scaffold(
    output_root: str,
    name: str,
    description: str,
    title: Optional[str],
    author: Optional[str],
    version: str,
    with_references: bool,
    with_scripts: bool,
    with_assets: bool,
    force: bool,
) -> str:
    _validate_name(name)
    description = description.strip()
    if not description:
        raise ScaffoldError("`description` must be non-empty.")
    if len(description) > 1024:
        raise ScaffoldError("`description` must be <= 1024 characters.")

    skill_dir = os.path.join(output_root, name)
    if os.path.exists(skill_dir):
        if not force:
            raise ScaffoldError(f"Output directory already exists: {skill_dir} (use --force to overwrite)")
    else:
        os.makedirs(skill_dir, exist_ok=True)

    _write_text(os.path.join(skill_dir, "SKILL.md"), _skill_md(name, description, title, author, version))

    if with_references:
        os.makedirs(os.path.join(skill_dir, "references"), exist_ok=True)
        _write_text(
            os.path.join(skill_dir, "references", "REFERENCE.md"),
            "# Reference\n\nAdd deeper documentation here (loaded on demand).\n",
        )

    if with_scripts:
        os.makedirs(os.path.join(skill_dir, "scripts"), exist_ok=True)
        _write_text(
            os.path.join(skill_dir, "scripts", "README.md"),
            "# Scripts\n\nPut deterministic utilities here (validators, generators, etc.).\n",
        )

    if with_assets:
        os.makedirs(os.path.join(skill_dir, "assets"), exist_ok=True)
        _write_text(
            os.path.join(skill_dir, "assets", "README.md"),
            "# Assets\n\nPut templates/resources here (schemas, boilerplate, samples).\n",
        )

    return skill_dir


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Scaffold a new Agent Skill directory.")
    p.add_argument("--output-root", default=".", help="Directory to create the skill folder in (default: .)")
    p.add_argument("--name", required=True, help="Skill name (must match spec naming rules)")
    p.add_argument("--description", required=True, help="Skill description (what it does and when to use it)")
    p.add_argument("--title", help="Human-friendly title used in SKILL.md heading")
    p.add_argument("--author", help="Optional metadata.author")
    p.add_argument("--version", default="1.0", help="Optional metadata.version (default: 1.0)")
    p.add_argument("--with-references", action="store_true", help="Create references/ with REFERENCE.md")
    p.add_argument("--with-scripts", action="store_true", help="Create scripts/ with README.md")
    p.add_argument("--with-assets", action="store_true", help="Create assets/ with README.md")
    p.add_argument("--force", action="store_true", help="Overwrite existing output directory contents")
    args = p.parse_args(argv)

    try:
        path = scaffold(
            output_root=args.output_root,
            name=args.name,
            description=args.description,
            title=args.title,
            author=args.author,
            version=args.version,
            with_references=args.with_references,
            with_scripts=args.with_scripts,
            with_assets=args.with_assets,
            force=args.force,
        )
    except ScaffoldError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    print(f"Created skill at: {os.path.abspath(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

