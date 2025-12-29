#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MAX_SKILL_NAME_LENGTH = 64
ALLOWED_RESOURCES: set[str] = {"scripts", "references", "assets"}

SKILL_TEMPLATE = """---
name: {skill_name}
description: [TODO: Describe what this skill does and when to use it. Include triggering cues: scenarios, file types, tools, and common user phrasing. Keep it concise.]
---

# {skill_title}

## Overview

[TODO: 1–2 sentences. Assume Codex is already smart; only include non-obvious procedural/domain context.]

## Workflow

1. [TODO: Step-by-step, imperative form]
2. [TODO: Call out when to ask clarifying questions]
3. [TODO: Define acceptance criteria / output shape]

## Resources (optional)

Use progressive disclosure:
- Put deterministic/repeated steps in `scripts/` (runnable helpers).
- Put long-tail docs/specs in `references/` (load only when needed).
- Put templates/boilerplate in `assets/` (copy/use in outputs).

[TODO: Replace this section with concrete commands/paths once you add resources.]
"""

EXAMPLE_SCRIPT = """#!/usr/bin/env python3
from __future__ import annotations

def main() -> int:
    print("TODO: Implement helper script for {skill_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""

EXAMPLE_REFERENCE = """# {skill_title} · Reference

Put detailed docs here (schemas, API notes, policies, long examples).
Keep SKILL.md lean; load this file only when needed.
"""

EXAMPLE_ASSET = """This is a placeholder asset file.
Replace with real templates (pptx/docx), boilerplate, images, fonts, etc.
"""


def _normalize_skill_name(raw: str) -> str:
    normalized = raw.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized


def _title_case_skill_name(skill_name: str) -> str:
    return " ".join(word.capitalize() for word in skill_name.split("-") if word)


def _parse_resources(raw_resources: str) -> list[str]:
    if not raw_resources:
        return []
    resources = [item.strip() for item in raw_resources.split(",") if item.strip()]
    invalid = sorted({item for item in resources if item not in ALLOWED_RESOURCES})
    if invalid:
        allowed = ", ".join(sorted(ALLOWED_RESOURCES))
        print(f"[ERROR] Unknown resource type(s): {', '.join(invalid)}")
        print(f"   Allowed: {allowed}")
        raise SystemExit(1)
    deduped: list[str] = []
    seen: set[str] = set()
    for resource in resources:
        if resource in seen:
            continue
        seen.add(resource)
        deduped.append(resource)
    return deduped


def _write_text(path: Path, content: str, *, executable: bool = False) -> None:
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(0o755)


def _create_resource_dirs(skill_dir: Path, *, skill_name: str, skill_title: str, resources: list[str], examples: bool) -> None:
    for resource in resources:
        resource_dir = skill_dir / resource
        resource_dir.mkdir(parents=True, exist_ok=True)
        if not examples:
            continue

        if resource == "scripts":
            _write_text(resource_dir / "example.py", EXAMPLE_SCRIPT.format(skill_name=skill_name), executable=True)
        elif resource == "references":
            _write_text(resource_dir / "example.md", EXAMPLE_REFERENCE.format(skill_title=skill_title))
        elif resource == "assets":
            _write_text(resource_dir / "example_asset.txt", EXAMPLE_ASSET)


def init_skill(*, skill_name: str, parent_dir: Path, resources: list[str], examples: bool) -> Path:
    skill_dir = (parent_dir / skill_name).resolve()
    if skill_dir.exists():
        raise SystemExit(f"[ERROR] Skill directory already exists: {skill_dir}")

    skill_dir.mkdir(parents=True, exist_ok=False)
    skill_title = _title_case_skill_name(skill_name)
    _write_text(skill_dir / "SKILL.md", SKILL_TEMPLATE.format(skill_name=skill_name, skill_title=skill_title))

    if resources:
        _create_resource_dirs(skill_dir, skill_name=skill_name, skill_title=skill_title, resources=resources, examples=examples)

    return skill_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a new skill folder with a SKILL.md template.")
    parser.add_argument("skill_name", help="Skill name (will be normalized to hyphen-case)")
    parser.add_argument("--path", required=True, help="Parent output directory (e.g., skills/)")
    parser.add_argument("--resources", default="", help="Comma-separated list: scripts,references,assets")
    parser.add_argument("--examples", action="store_true", help="Create example files inside selected resource directories")
    args = parser.parse_args()

    raw_skill_name = str(args.skill_name)
    skill_name = _normalize_skill_name(raw_skill_name)
    if not skill_name:
        raise SystemExit("[ERROR] Skill name must include at least one letter or digit.")
    if len(skill_name) > MAX_SKILL_NAME_LENGTH:
        raise SystemExit(
            f"[ERROR] Skill name '{skill_name}' is too long ({len(skill_name)} characters). Maximum is {MAX_SKILL_NAME_LENGTH}."
        )
    if raw_skill_name != skill_name:
        print(f"Note: Normalized skill name from '{raw_skill_name}' to '{skill_name}'.")

    resources = _parse_resources(str(args.resources))
    if args.examples and not resources:
        raise SystemExit("[ERROR] --examples requires --resources to be set.")

    parent_dir = Path(args.path).expanduser()
    if not parent_dir.is_absolute():
        parent_dir = (Path.cwd() / parent_dir).resolve()

    print(f"Initializing skill: {skill_name}")
    print(f"  Parent dir: {parent_dir}")
    print(f"  Resources: {', '.join(resources) if resources else '(none)'}")
    print(f"  Examples: {'yes' if args.examples else 'no'}")
    print()

    skill_dir = init_skill(skill_name=skill_name, parent_dir=parent_dir, resources=resources, examples=bool(args.examples))

    print(f"[OK] Created: {skill_dir}")
    print("Next:")
    print(f"- Edit: {skill_dir / 'SKILL.md'} (finish description + workflow)")
    print("- Add trigger suite: datasets/trigger_cases.json (A/B/C/D/NEG)")
    print("- Run: python3 scripts/skillops_preflight.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

