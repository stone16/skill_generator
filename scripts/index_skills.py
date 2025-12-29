#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class SkillRecord:
    name: str
    description: str
    skill_dir: str
    skill_md: str
    scope_hint: str
    has_scripts: bool
    has_references: bool
    has_assets: bool


FRONTMATTER_BOUNDARY = "---"


def _extract_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_BOUNDARY:
        return ""
    try:
        end_idx = lines[1:].index(FRONTMATTER_BOUNDARY) + 1
    except ValueError:
        return ""
    return "\n".join(lines[1:end_idx]).strip("\n")


def _parse_frontmatter_minimal(frontmatter: str) -> dict[str, str]:
    """
    Minimal YAML-ish parser that supports:
      - key: value (single-line)
      - key: | / > (indented block scalar)
    We only care about 'name' and 'description'.
    """

    result: dict[str, str] = {}
    lines = frontmatter.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        i += 1

        if not stripped or stripped.startswith("#"):
            continue

        match = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", stripped)
        if not match:
            continue

        key = match.group(1)
        raw_value = match.group(2)

        if raw_value in {"|", ">"}:
            block_lines: list[str] = []
            while i < len(lines):
                next_line = lines[i]
                if not next_line.startswith((" ", "\t")):
                    break
                block_lines.append(next_line.lstrip())
                i += 1
            value = "\n".join(block_lines).strip()
        else:
            value = raw_value.strip()
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]

        if key in {"name", "description"}:
            result[key] = value

    return result


def _infer_scope(skill_dir: Path) -> str:
    parts = set(skill_dir.parts)
    if ".system" in parts:
        return ".system"
    if ".curated" in parts:
        return ".curated"
    if ".experimental" in parts:
        return ".experimental"
    return "custom"


def _default_skills_dir() -> Path:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    return codex_home / "skills"


def _discover_skill_dirs(skills_dir: Path) -> list[Path]:
    if not skills_dir.exists():
        return []
    skill_mds = list(skills_dir.rglob("SKILL.md"))
    return sorted({p.parent for p in skill_mds})


def _load_record(skill_dir: Path) -> SkillRecord | None:
    skill_md = skill_dir / "SKILL.md"
    try:
        content = skill_md.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    frontmatter = _extract_frontmatter(content)
    parsed = _parse_frontmatter_minimal(frontmatter) if frontmatter else {}
    name = (parsed.get("name") or "").strip() or skill_dir.name
    description = (parsed.get("description") or "").strip()

    return SkillRecord(
        name=name,
        description=description,
        skill_dir=str(skill_dir),
        skill_md=str(skill_md),
        scope_hint=_infer_scope(skill_dir),
        has_scripts=(skill_dir / "scripts").is_dir(),
        has_references=(skill_dir / "references").is_dir(),
        has_assets=(skill_dir / "assets").is_dir(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Index Codex skills (name/description/path) into JSON.")
    parser.add_argument(
        "--skills-dir",
        default="",
        help="Skills directory (default: $CODEX_HOME/skills or ~/.codex/skills).",
    )
    parser.add_argument(
        "--out",
        default="skills_index.json",
        help="Output JSON path (default: skills_index.json).",
    )
    args = parser.parse_args()

    skills_dir = Path(args.skills_dir).expanduser() if args.skills_dir else _default_skills_dir()
    skills_dir = skills_dir.resolve()

    records: list[SkillRecord] = []
    for skill_dir in _discover_skill_dirs(skills_dir):
        record = _load_record(skill_dir)
        if record is None:
            continue
        records.append(record)

    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(
            {"skills_dir": str(skills_dir), "count": len(records), "skills": [asdict(r) for r in records]},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {len(records)} skills to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

