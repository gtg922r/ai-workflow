#!/usr/bin/env python3

"""
Lightweight validator for Agent Skills directories.

This is not a full replacement for skills-ref; it focuses on the highest-signal
spec checks: presence, name/description constraints, and folder/name match.

Usage:
  python3 validate_skill.py /path/to/skill-dir
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _fail(errors: list[str], warnings: list[str]) -> int:
    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    return 1


def _read_frontmatter(skill_md: Path) -> tuple[dict, list[str]]:
    """
    Returns (frontmatter_dict, warnings).
    Attempts YAML parsing if PyYAML is available; otherwise uses a conservative
    fallback parser for common 'key: value' and simple multiline blocks.
    """
    warnings: list[str] = []
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md must start with YAML frontmatter delimited by '---'.")

    # Find closing delimiter.
    try:
        end_idx = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as e:
        raise ValueError("SKILL.md frontmatter must be closed with a second '---' line.") from e

    yaml_lines = lines[1:end_idx]
    yaml_text = "\n".join(yaml_lines) + "\n"

    try:
        import yaml  # type: ignore

        data = yaml.safe_load(yaml_text) or {}
        if not isinstance(data, dict):
            raise ValueError("Frontmatter YAML must parse to a mapping/object.")
        return data, warnings
    except ModuleNotFoundError:
        warnings.append("PyYAML not installed; using fallback frontmatter parser.")
    except Exception as e:  # noqa: BLE001 - show YAML error but continue with fallback.
        warnings.append(f"PyYAML parse failed ({e}); using fallback frontmatter parser.")

    # Fallback parser: top-level keys only; supports:
    #   key: value
    #   key:
    #     indented continuation lines...
    data: dict[str, str] = {}
    i = 0
    while i < len(yaml_lines):
        line = yaml_lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line.startswith((" ", "\t")):
            # Indented line without an owning key; ignore.
            i += 1
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, rest = m.group(1), m.group(2)
        if rest:
            data[key] = rest.strip().strip('"').strip("'")
            i += 1
            continue
        # Multiline scalar (common in examples): key: \n   line1\n   line2
        i += 1
        buf: list[str] = []
        while i < len(yaml_lines):
            nxt = yaml_lines[i]
            if not nxt.startswith((" ", "\t")):
                break
            buf.append(nxt.strip())
            i += 1
        data[key] = " ".join(s for s in buf if s)

    return data, warnings


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip())
        return 2

    skill_dir = Path(argv[1]).expanduser().resolve()
    skill_md = skill_dir / "SKILL.md"

    errors: list[str] = []
    warnings: list[str] = []

    if not skill_dir.exists() or not skill_dir.is_dir():
        errors.append(f"Skill directory not found: {skill_dir}")
        return _fail(errors, warnings)

    if not skill_md.exists():
        errors.append(f"Missing required file: {skill_md}")
        return _fail(errors, warnings)

    # Size heuristics (progressive disclosure guidance).
    try:
        line_count = len(skill_md.read_text(encoding="utf-8").splitlines())
        if line_count > 500:
            warnings.append(
                f"SKILL.md is {line_count} lines (guideline is <500); consider moving details to references/."
            )
    except Exception as e:  # noqa: BLE001
        warnings.append(f"Could not read SKILL.md to check line count: {e}")

    try:
        fm, fm_warnings = _read_frontmatter(skill_md)
        warnings.extend(fm_warnings)
    except Exception as e:  # noqa: BLE001
        errors.append(str(e))
        return _fail(errors, warnings)

    # Required: name/description
    name = fm.get("name")
    desc = fm.get("description")

    if not isinstance(name, str) or not name.strip():
        errors.append("Frontmatter must include non-empty 'name'.")
    if not isinstance(desc, str) or not desc.strip():
        errors.append("Frontmatter must include non-empty 'description'.")

    if isinstance(name, str) and name.strip():
        name = name.strip()
        if len(name) > 64:
            errors.append(f"'name' must be <= 64 characters (got {len(name)}).")
        if not NAME_RE.match(name):
            errors.append(
                "'name' must match ^[a-z0-9]+(?:-[a-z0-9]+)*$ "
                "(lowercase letters/numbers, hyphen-separated; no leading/trailing hyphen; no consecutive hyphens)."
            )
        if skill_dir.name != name:
            errors.append(f"Directory name must match frontmatter name: dir='{skill_dir.name}' name='{name}'.")

    if isinstance(desc, str) and desc.strip():
        desc = desc.strip()
        if len(desc) > 1024:
            errors.append(f"'description' must be <= 1024 characters (got {len(desc)}).")

    compat = fm.get("compatibility")
    if compat is not None:
        if not isinstance(compat, str):
            warnings.append("'compatibility' is present but is not a string (some clients may reject this).")
        else:
            compat = compat.strip()
            if compat and len(compat) > 500:
                errors.append(f"'compatibility' must be <= 500 characters (got {len(compat)}).")

    if errors:
        return _fail(errors, warnings)

    for w in warnings:
        print(f"WARNING: {w}")
    print("OK: Skill appears valid (basic checks passed).")
    print(f"- name: {name}")
    print(f"- SKILL.md: {skill_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

