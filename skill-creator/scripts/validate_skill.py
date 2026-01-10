#!/usr/bin/env python3
"""
Minimal validator for Agent Skills folders.

Validates:
  - skill directory name matches SKILL.md frontmatter `name`
  - `name` format/length rules from the Agent Skills spec
  - `description` non-empty and <= 1024 chars
  - optional `compatibility` <= 500 chars

This intentionally avoids external dependencies (no PyYAML).
It supports a small, practical subset of YAML used by SKILL.md frontmatter.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ValidationError(Exception):
    pass


@dataclass(frozen=True)
class Frontmatter:
    data: Dict[str, Any]
    start_line: int
    end_line: int


def _strip_quotes(value: str) -> str:
    v = value.strip()
    if len(v) >= 2 and ((v[0] == v[-1] == '"') or (v[0] == v[-1] == "'")):
        return v[1:-1]
    return v


def _consume_block(lines: List[str], start_idx: int, parent_indent: int) -> Tuple[str, int]:
    """
    Consume indented lines following a key with an empty value (e.g., "description:").
    Joins lines with spaces, trimming indentation.
    Returns (text, next_index).
    """
    parts: List[str] = []
    i = start_idx
    while i < len(lines):
        raw = lines[i].rstrip("\n")
        if not raw.strip():
            i += 1
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent <= parent_indent:
            break
        parts.append(raw.strip())
        i += 1
    return " ".join(parts).strip(), i


def _consume_literal_or_folded(
    lines: List[str], start_idx: int, parent_indent: int, mode: str
) -> Tuple[str, int]:
    """
    Consume YAML block scalars:
      - "|" literal: preserves newlines (roughly)
      - ">" folded: folds newlines into spaces (roughly)
    Returns (text, next_index).
    """
    parts: List[str] = []
    i = start_idx
    while i < len(lines):
        raw = lines[i].rstrip("\n")
        indent = len(raw) - len(raw.lstrip(" "))
        if raw.strip() == "":
            parts.append("")
            i += 1
            continue
        if indent <= parent_indent:
            break
        parts.append(raw.strip())
        i += 1

    if mode == "|":
        # Keep paragraph structure but strip trailing whitespace.
        return "\n".join(parts).rstrip(), i
    # Folded: collapse newlines into spaces, but keep double newlines as paragraph breaks.
    out_lines: List[str] = []
    para: List[str] = []
    for p in parts:
        if p == "":
            if para:
                out_lines.append(" ".join(para).strip())
                para = []
            out_lines.append("")
        else:
            para.append(p)
    if para:
        out_lines.append(" ".join(para).strip())
    return "\n".join(out_lines).strip(), i


def parse_frontmatter(skill_md_path: str) -> Frontmatter:
    with open(skill_md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines or lines[0].strip() != "---":
        raise ValidationError("SKILL.md must start with YAML frontmatter delimited by '---'.")

    # Find closing delimiter
    end = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end = idx
            break
    if end is None:
        raise ValidationError("SKILL.md frontmatter is missing the closing '---' delimiter.")

    fm_lines = [ln.rstrip("\n") for ln in lines[1:end]]
    data: Dict[str, Any] = {}
    stack: List[Tuple[int, Dict[str, Any]]] = [(0, data)]  # (indent, mapping)

    i = 0
    while i < len(fm_lines):
        raw = fm_lines[i]
        i += 1

        if not raw.strip() or raw.lstrip().startswith("#"):
            continue

        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()

        # Adjust stack for indentation
        while len(stack) > 1 and indent < stack[-1][0]:
            stack.pop()
        current = stack[-1][1]

        if ":" not in line:
            raise ValidationError(f"Invalid frontmatter line (missing ':'): {raw!r}")

        key, rest = line.split(":", 1)
        key = key.strip()
        rest = rest.lstrip()

        # Nested mapping start: "metadata:"
        if rest == "":
            # Could be a block scalar continued on next lines (e.g. description:)
            # We decide based on peeking at next non-empty line.
            peek = i
            while peek < len(fm_lines) and fm_lines[peek].strip() == "":
                peek += 1

            if peek < len(fm_lines):
                peek_raw = fm_lines[peek]
                peek_indent = len(peek_raw) - len(peek_raw.lstrip(" "))
                peek_line = peek_raw.strip()

                # If the next indented content looks like key-value, treat as mapping.
                if peek_indent > indent and ":" in peek_line and not peek_line.startswith(("-", "[")):
                    new_map: Dict[str, Any] = {}
                    current[key] = new_map
                    stack.append((peek_indent, new_map))
                    continue

                # Otherwise treat as a folded block scalar (common for multiline description)
                if peek_indent > indent:
                    text, next_i = _consume_block(fm_lines, peek, indent)
                    current[key] = text
                    i = next_i
                    continue

            # Empty key with no value and no content: store empty string
            current[key] = ""
            continue

        # Block scalar: "description: |" or "description: >"
        if rest in {"|", ">"}:
            text, next_i = _consume_literal_or_folded(fm_lines, i, indent, rest)
            current[key] = text
            i = next_i
            continue

        # Simple scalar
        current[key] = _strip_quotes(rest)

    return Frontmatter(data=data, start_line=1, end_line=end + 1)


def validate_name(name: str) -> List[str]:
    errs: List[str] = []
    if not (1 <= len(name) <= 64):
        errs.append("`name` must be 1–64 characters.")
    if not NAME_RE.match(name):
        errs.append("`name` must match ^[a-z0-9]+(?:-[a-z0-9]+)*$ (lowercase, digits, hyphens; no leading/trailing/consecutive hyphens).")
    return errs


def validate_skill_dir(skill_dir: str) -> List[str]:
    errors: List[str] = []

    if not os.path.isdir(skill_dir):
        return [f"Not a directory: {skill_dir}"]

    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        return [f"Missing required file: {skill_md}"]

    try:
        fm = parse_frontmatter(skill_md)
    except ValidationError as e:
        return [str(e)]

    name = str(fm.data.get("name", "")).strip()
    description = str(fm.data.get("description", "")).strip()
    compatibility = fm.data.get("compatibility")

    if not name:
        errors.append("Missing required frontmatter field: `name`.")
    else:
        errors.extend(validate_name(name))
        dir_name = os.path.basename(os.path.abspath(skill_dir))
        if dir_name != name:
            errors.append(f"Skill directory name must match frontmatter `name`: dir={dir_name!r}, name={name!r}.")

    if not description:
        errors.append("Missing required frontmatter field: `description` (must be non-empty).")
    else:
        if len(description) > 1024:
            errors.append("`description` must be <= 1024 characters.")

    if compatibility is not None:
        comp = str(compatibility).strip()
        if not comp:
            errors.append("`compatibility` must be non-empty if provided.")
        elif len(comp) > 500:
            errors.append("`compatibility` must be <= 500 characters.")

    return errors


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an Agent Skill folder (SKILL.md frontmatter + naming rules).")
    parser.add_argument("skill_dir", help="Path to a skill directory containing SKILL.md")
    args = parser.parse_args(argv)

    errors = validate_skill_dir(args.skill_dir)
    if errors:
        print("Validation failed:")
        for e in errors:
            print(f"- {e}")
        return 2

    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

