# Scripts

## Index installed Codex skills

```bash
python3 scripts/index_skills.py --out skills_index.json
```

By default this scans `$CODEX_HOME/skills` (or `~/.codex/skills`).

## Run trigger/discoverability eval (BM25 baseline)

```bash
python3 scripts/trigger_eval.py --skills skills_index.json --cases datasets/trigger_cases.example.json --top-k 5 --out trigger_eval_results.json
```

## Optional: also ask Codex to route skills (over BM25 top-N candidates)

```bash
python3 scripts/trigger_eval.py --skills skills_index.json --cases datasets/trigger_cases.example.json --top-k 5 --bm25-candidates 20 --use-codex --out trigger_eval_results.json
```

