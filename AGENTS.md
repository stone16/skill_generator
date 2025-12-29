# Agent Instructions (SkillOps)

- When adding or updating any Skill under `skills/`, also update `datasets/trigger_cases.json` with a prompt suite (A/B/C/D/NEG) so discoverability can be backtested.
- Before finishing work that changes Skills or trigger cases, run `python3 scripts/skillops_preflight.py` and report the summary + whether the gate passes.
- Keep generated artifacts out of git (`.skillops/`, `skills_index.json`, `trigger_eval_results.json`, `__pycache__/`); only commit source assets (skills, datasets, scripts, docs).
- Put external benchmark repos under `reference/` (gitignored) and use `--skills-dir` to run the same preflight flow on them.

See `HM.markdown` for the human-facing SOP and CI flow.

