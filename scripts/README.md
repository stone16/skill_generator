# Scripts

## Initialize a new local skill skeleton

```bash
python3 scripts/init_skill.py my-skill --path skills --resources scripts,references,assets
```

Optional example files:

```bash
python3 scripts/init_skill.py my-skill --path skills --resources scripts,references,assets --examples
```

## Validate and package a skill for distribution

```bash
python3 scripts/validate_skill.py skills/my-skill
python3 scripts/package_skill.py skills/my-skill dist
```

## Run SkillOps preflight (index + trigger backtests)

```bash
python3 scripts/skillops_preflight.py
```

## Index installed Codex skills

```bash
python3 scripts/index_skills.py --out .skillops/skills_index.json
```

By default this scans `$CODEX_HOME/skills` (or `~/.codex/skills`).

## Run trigger/discoverability eval (BM25 baseline)

```bash
python3 scripts/trigger_eval.py --skills .skillops/skills_index.json --cases datasets/trigger_cases.example.json --top-k 5 --out .skillops/trigger_eval_results.json
```

## Optional: also ask Codex to route skills (over BM25 top-N candidates)

```bash
python3 scripts/trigger_eval.py --skills .skillops/skills_index.json --cases datasets/trigger_cases.example.json --top-k 5 --bm25-candidates 20 --use-codex --out .skillops/trigger_eval_results.json
```
