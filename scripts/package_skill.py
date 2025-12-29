#!/usr/bin/env python3
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

from validate_skill import validate_skill


def _should_exclude(relative_path: Path) -> bool:
    parts = set(relative_path.parts)
    if ".git" in parts or ".skillops" in parts or "__pycache__" in parts:
        return True
    if relative_path.name in {".DS_Store"}:
        return True
    if relative_path.suffix == ".pyc":
        return True
    return False


def package_skill(*, skill_dir: Path, out_dir: Path) -> Path:
    skill_dir = skill_dir.expanduser().resolve()
    out_dir = out_dir.expanduser().resolve()

    validation = validate_skill(skill_dir)
    for warning in validation.warnings:
        print(f"[WARN] {warning}")
    if not validation.ok:
        raise SystemExit("[ERROR] Refusing to package: skill validation failed (run scripts/validate_skill.py).")

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{skill_dir.name}.skill"

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in sorted(skill_dir.rglob("*")):
            if not file_path.is_file():
                continue
            relative = file_path.relative_to(skill_dir)
            if _should_exclude(relative):
                continue
            arcname = file_path.relative_to(skill_dir.parent)
            zipf.write(file_path, arcname)

    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Package a skill folder into a distributable .skill (zip) file.")
    parser.add_argument("skill_dir", help="Path to the skill directory (contains SKILL.md)")
    parser.add_argument("out_dir", nargs="?", default="dist", help="Output directory for the .skill file (default: dist/)")
    args = parser.parse_args()

    out_path = package_skill(skill_dir=Path(args.skill_dir), out_dir=Path(args.out_dir))
    print(f"[OK] Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
