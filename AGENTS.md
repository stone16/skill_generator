# Agent Instructions (SkillOps)

- Keep an A/B/C/D/NEG prompt suite in `datasets/trigger_cases.json` for each Skill under
  `skills/`. Reuse cases for equivalent wording changes; update them when trigger scope
  changes or coverage is missing, so discoverability can be backtested.
- Before finishing work that changes Skills or trigger cases, run `python3 scripts/skillops_preflight.py` and report the summary + whether the gate passes.
- Keep generated artifacts out of git (`.skillops/`, `skills_index.json`, `trigger_eval_results.json`, `__pycache__/`); only commit source assets (skills, datasets, scripts, docs).
- Put external benchmark repos under `reference/` (gitignored) and use `--skills-dir` to run the same preflight flow on them.

See `HM.markdown` for the human-facing SOP and CI flow.

## Scope and delivery

Preserve unrelated work and use a feature branch with atomic conventional commits.
For instruction-only edits, verify affected links and `git diff --check`; skill or
trigger changes still require the preflight gate above. Report the exact change,
check results, and any unresolved limitation with file/line evidence.
