#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
RECOMMENDED_MAX_SKILL_MD_LINES = 500

FRONTMATTER_BOUNDARY = "---"

DISALLOWED_DOC_FILENAMES = {
    "README.md",
    "INSTALLATION_GUIDE.md",
    "QUICK_REFERENCE.md",
    "CHANGELOG.md",
}

IGNORED_FILE_NAMES = {
    ".DS_Store",
}


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: list[str]
    warnings: list[str]


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
    Minimal YAML-ish parser supporting:
      - key: value (single-line)
      - key: | / > (indented block scalar, incl. |-, >-, etc)

    Note: This is intentionally minimal to avoid external deps.
    """

    result: dict[str, str] = {}
    lines = frontmatter.splitlines()
    i = 0

    def parse_value(raw: str) -> str:
        value = raw.strip()
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        return value.strip()

    while i < len(lines):
        stripped = lines[i].strip()
        i += 1

        if not stripped or stripped.startswith("#"):
            continue

        match = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", stripped)
        if not match:
            continue

        key = match.group(1)
        raw_value = match.group(2)

        is_block_scalar = raw_value.strip().startswith(("|", ">"))
        if is_block_scalar:
            block_lines: list[str] = []
            while i < len(lines):
                next_line = lines[i]
                if next_line == "":
                    block_lines.append("")
                    i += 1
                    continue
                if not next_line.startswith((" ", "\t")):
                    break
                block_lines.append(next_line.lstrip())
                i += 1
            value = "\n".join(block_lines).strip()
        elif raw_value.strip() == "":
            # Capture indented structure as raw text (we don't validate nested keys here).
            block_lines: list[str] = []
            while i < len(lines):
                next_line = lines[i]
                if next_line and not next_line.startswith((" ", "\t")):
                    break
                block_lines.append(next_line.lstrip())
                i += 1
            value = "\n".join(block_lines).strip()
        else:
            value = parse_value(raw_value)

        result[key] = value

    return result


def _iter_skill_files(skill_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in skill_dir.rglob("*"):
        if path.is_dir():
            continue
        if path.name in IGNORED_FILE_NAMES:
            continue
        files.append(path)
    return files


def validate_skill(skill_dir: Path) -> ValidationResult:
    skill_dir = skill_dir.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not skill_dir.exists():
        return ValidationResult(ok=False, errors=[f"Skill path not found: {skill_dir}"], warnings=[])
    if not skill_dir.is_dir():
        return ValidationResult(ok=False, errors=[f"Skill path is not a directory: {skill_dir}"], warnings=[])

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        errors.append("Missing SKILL.md")
        return ValidationResult(ok=False, errors=errors, warnings=warnings)

    content = skill_md.read_text(encoding="utf-8", errors="replace")
    if not content.startswith(FRONTMATTER_BOUNDARY):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return ValidationResult(ok=False, errors=errors, warnings=warnings)

    frontmatter = _extract_frontmatter(content)
    if not frontmatter:
        errors.append("Invalid YAML frontmatter: missing closing ---")
        return ValidationResult(ok=False, errors=errors, warnings=warnings)

    parsed = _parse_frontmatter_minimal(frontmatter)
    name = (parsed.get("name") or "").strip()
    description = (parsed.get("description") or "").strip()

    if not name:
        errors.append("Frontmatter missing non-empty 'name'")
    if not description:
        errors.append("Frontmatter missing non-empty 'description'")

    if name:
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", name):
            errors.append("Frontmatter 'name' must be hyphen-case (lowercase letters/digits, single hyphens)")
        if len(name) > MAX_SKILL_NAME_LENGTH:
            errors.append(f"Frontmatter 'name' too long ({len(name)} > {MAX_SKILL_NAME_LENGTH})")

        if skill_dir.name != name:
            warnings.append(f"Skill directory name '{skill_dir.name}' differs from frontmatter name '{name}'")

    if description:
        if len(description) > MAX_DESCRIPTION_LENGTH:
            errors.append(f"Frontmatter 'description' too long ({len(description)} > {MAX_DESCRIPTION_LENGTH})")
        if "<" in description or ">" in description:
            warnings.append("Frontmatter 'description' contains angle brackets; consider removing to avoid noisy routing")
        if "TODO" in description.upper():
            errors.append("Frontmatter 'description' still contains TODO placeholder text")

    line_count = len(content.splitlines())
    if line_count > RECOMMENDED_MAX_SKILL_MD_LINES:
        warnings.append(f"SKILL.md is long ({line_count} lines); consider moving details into references/ to save context")

    for file_path in _iter_skill_files(skill_dir):
        if file_path.name in DISALLOWED_DOC_FILENAMES:
            errors.append(f"Disallowed doc file found: {file_path.relative_to(skill_dir)} (keep skills minimal; no extra docs)")
        if file_path.name.endswith(".pyc") or "__pycache__" in file_path.parts:
            warnings.append(f"Generated Python artifact found under skill: {file_path.relative_to(skill_dir)}")

    ok = not errors
    return ValidationResult(ok=ok, errors=errors, warnings=warnings)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a skill folder (minimal checks; no external deps).")
    parser.add_argument("skill_dir", help="Path to the skill directory (contains SKILL.md)")
    args = parser.parse_args()

    result = validate_skill(Path(args.skill_dir))
    for warning in result.warnings:
        print(f"[WARN] {warning}")
    if not result.ok:
        print("[ERROR] Skill validation failed:")
        for error in result.errors:
            print(f"- {error}")
        return 1
    print("[OK] Skill is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

