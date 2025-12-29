#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="SkillOps preflight: index skills, run trigger backtests, and enforce simple gates."
    )
    parser.add_argument(
        "--skills-dir",
        default="",
        help="Skills directory to index (default: ./skills if present, else Codex home skills).",
    )
    parser.add_argument(
        "--cases",
        default="",
        help="Cases JSON path (default: datasets/trigger_cases.json, else datasets/trigger_cases.example.json).",
    )
    parser.add_argument("--top-k", type=int, default=5, help="BM25 top-k for hit/recall metrics (default: 5).")
    parser.add_argument(
        "--bm25-candidates",
        type=int,
        default=20,
        help="Top-N BM25 candidates to pass to Codex when --use-codex (default: 20).",
    )
    parser.add_argument("--use-codex", action="store_true", help="Also run Codex as a skill router (requires codex CLI).")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout seconds per Codex routing call (default: 120).")
    parser.add_argument(
        "--out-dir",
        default=".skillops",
        help="Directory to write generated artifacts (default: .skillops).",
    )

    parser.add_argument("--no-gate", action="store_true", help="Run preflight but never fail the build.")
    parser.add_argument("--min-bm25-hit-at-k", type=float, default=0.8, help="Gate: minimum bm25_hit_at_k.")
    parser.add_argument("--min-bm25-recall-at-k", type=float, default=0.6, help="Gate: minimum bm25_recall_at_k.")

    parser.add_argument("--min-codex-macro-recall", type=float, default=0.6, help="Gate: minimum codex_macro_recall.")
    parser.add_argument(
        "--max-codex-false-invoke-rate",
        type=float,
        default=0.2,
        help="Gate: maximum codex_false_invoke_rate (negative cases only).",
    )
    parser.add_argument("--max-codex-errors", type=int, default=0, help="Gate: maximum codex_errors.")

    args = parser.parse_args()

    root = _repo_root()

    out_dir = Path(args.out_dir).expanduser()
    if not out_dir.is_absolute():
        out_dir = (root / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    skills_dir = Path(args.skills_dir).expanduser() if args.skills_dir else Path()
    if not args.skills_dir:
        local_skills = root / "skills"
        if local_skills.is_dir():
            skills_dir = local_skills
    if skills_dir and not skills_dir.is_absolute():
        skills_dir = (root / skills_dir).resolve()

    cases_path = Path(args.cases).expanduser() if args.cases else Path()
    if not args.cases:
        default_cases = root / "datasets" / "trigger_cases.json"
        fallback_cases = root / "datasets" / "trigger_cases.example.json"
        cases_path = default_cases if default_cases.is_file() else fallback_cases
    if not cases_path.is_absolute():
        cases_path = (root / cases_path).resolve()
    if not cases_path.is_file():
        raise SystemExit(f"Cases file not found: {cases_path}")

    skills_index_path = out_dir / "skills_index.json"
    trigger_results_path = out_dir / "trigger_eval_results.json"

    index_cmd = [sys.executable, str(root / "scripts" / "index_skills.py"), "--out", str(skills_index_path)]
    if skills_dir:
        index_cmd.extend(["--skills-dir", str(skills_dir)])
    _run(index_cmd)

    index_payload = _load_json(skills_index_path)
    skills_count = int(index_payload.get("count", 0))
    cases_payload = _load_json(cases_path)
    cases_count = len(cases_payload.get("cases", []))

    if skills_count == 0 and cases_count == 0:
        print("No skills and no cases found; skipping trigger eval.")
        return 0
    if skills_count == 0 and cases_count > 0:
        raise SystemExit("Cases exist but no skills were indexed. Check --skills-dir / skills/ directory.")
    if skills_count > 0 and cases_count == 0:
        raise SystemExit("Skills exist but no trigger cases found. Fill datasets/trigger_cases.json.")

    eval_cmd = [
        sys.executable,
        str(root / "scripts" / "trigger_eval.py"),
        "--skills",
        str(skills_index_path),
        "--cases",
        str(cases_path),
        "--top-k",
        str(int(args.top_k)),
        "--bm25-candidates",
        str(int(args.bm25_candidates)),
        "--out",
        str(trigger_results_path),
    ]
    if args.use_codex:
        eval_cmd.extend(["--use-codex", "--timeout", str(int(args.timeout))])
    _run(eval_cmd)

    results_payload = _load_json(trigger_results_path)
    summary = results_payload.get("summary", {})

    if args.no_gate:
        return 0

    failures: list[str] = []

    bm25_hit_at_k = float(summary.get("bm25_hit_at_k", 0.0))
    bm25_recall_at_k = float(summary.get("bm25_recall_at_k", 0.0))

    if bm25_hit_at_k < float(args.min_bm25_hit_at_k):
        failures.append(f"bm25_hit_at_k {bm25_hit_at_k:.3f} < {float(args.min_bm25_hit_at_k):.3f}")
    if bm25_recall_at_k < float(args.min_bm25_recall_at_k):
        failures.append(f"bm25_recall_at_k {bm25_recall_at_k:.3f} < {float(args.min_bm25_recall_at_k):.3f}")

    if args.use_codex:
        codex_errors = int(summary.get("codex_errors", 0))
        codex_macro_recall = float(summary.get("codex_macro_recall", 0.0))
        codex_false_invoke_rate = float(summary.get("codex_false_invoke_rate", 1.0))

        if codex_errors > int(args.max_codex_errors):
            failures.append(f"codex_errors {codex_errors} > {int(args.max_codex_errors)}")
        if codex_macro_recall < float(args.min_codex_macro_recall):
            failures.append(f"codex_macro_recall {codex_macro_recall:.3f} < {float(args.min_codex_macro_recall):.3f}")
        if codex_false_invoke_rate > float(args.max_codex_false_invoke_rate):
            failures.append(
                f"codex_false_invoke_rate {codex_false_invoke_rate:.3f} > {float(args.max_codex_false_invoke_rate):.3f}"
            )

    if failures:
        print("Trigger backtesting gate failed:")
        for f in failures:
            print(f"- {f}")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

