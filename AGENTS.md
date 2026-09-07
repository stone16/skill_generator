# Agent Instructions (SkillOps)

- Keep an A/B/C/D/NEG prompt suite in `datasets/trigger_cases.json` for each Skill under
  `skills/`. Reuse cases for equivalent wording changes; update them when trigger scope
  changes or coverage is missing, so discoverability can be backtested.
  Manually verify every Skill's groups using the case ID's skill-name prefix,
  including D/NEG cases with empty `expected` lists; preflight does not enforce coverage.
- Before finishing work that changes Skills or trigger cases, run `python3 scripts/skillops_preflight.py` and report the summary + whether the gate passes.
- Keep generated artifacts out of git (`.skillops/`, `skills_index.json`, `trigger_eval_results.json`, `__pycache__/`); only commit source assets (skills, datasets, scripts, docs).
- Put external benchmark repos under `reference/` (gitignored) and use `--skills-dir` to run the same preflight flow on them.

For routing boundary changes, also evaluate contrasting requests without showing
the evaluator expected labels, then compare its selections with the expected sets,
including exclusion of overlapping sibling skills. Report the observed selections
and whether the evidence is manual review or the optional `--use-codex` evaluator.
The default BM25 gate measures lexical top-k recall, not exclusive semantic routing;
even the optional Codex gate does not enforce per-case exact matches.

See `HM.markdown` for the human-facing SOP and CI flow.

## Scope and delivery

Preserve unrelated work and use a feature branch with atomic conventional commits.
For instruction-only edits, verify affected links and `git diff --check`; skill or
trigger changes still require the preflight gate above. Report the exact change,
check results, and any unresolved limitation with file/line evidence.
