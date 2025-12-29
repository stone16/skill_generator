#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


def tokenize(text: str) -> list[str]:
    text = text.lower()
    tokens: list[str] = []

    tokens.extend(re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text))

    cjk = re.findall(r"[\u4e00-\u9fff]", text)
    tokens.extend(cjk)
    tokens.extend([cjk[i] + cjk[i + 1] for i in range(len(cjk) - 1)])
    return tokens


@dataclass(frozen=True)
class Skill:
    name: str
    description: str


@dataclass(frozen=True)
class Case:
    id: str
    prompt: str
    expected: list[str]


class BM25:
    def __init__(self, docs: list[list[str]], *, k1: float = 1.5, b: float = 0.75):
        self.docs = docs
        self.k1 = k1
        self.b = b
        self.doc_lens = [len(d) for d in docs]
        self.avgdl = sum(self.doc_lens) / max(1, len(self.doc_lens))

        df: dict[str, int] = {}
        for doc in docs:
            for term in set(doc):
                df[term] = df.get(term, 0) + 1
        self.df = df
        self.N = len(docs)

    def idf(self, term: str) -> float:
        df = self.df.get(term, 0)
        return math.log((self.N - df + 0.5) / (df + 0.5) + 1.0)

    def score(self, query: list[str], doc_idx: int) -> float:
        doc = self.docs[doc_idx]
        dl = self.doc_lens[doc_idx]
        if not doc:
            return 0.0
        tf: dict[str, int] = {}
        for t in doc:
            tf[t] = tf.get(t, 0) + 1
        score = 0.0
        for term in query:
            if term not in tf:
                continue
            f = tf[term]
            denom = f + self.k1 * (1 - self.b + self.b * (dl / self.avgdl))
            score += self.idf(term) * (f * (self.k1 + 1)) / denom
        return score

    def rank(self, query: list[str], *, top_k: int) -> list[tuple[int, float]]:
        scored = [(idx, self.score(query, idx)) for idx in range(self.N)]
        scored.sort(key=lambda p: p[1], reverse=True)
        return scored[:top_k]


def _load_skills(index_path: Path) -> list[Skill]:
    data = json.loads(index_path.read_text(encoding="utf-8"))
    skills: list[Skill] = []
    for raw in data.get("skills", []):
        skills.append(Skill(name=str(raw.get("name", "")).strip(), description=str(raw.get("description", "")).strip()))
    return skills


def _load_cases(cases_path: Path) -> list[Case]:
    data = json.loads(cases_path.read_text(encoding="utf-8"))
    cases: list[Case] = []
    for raw in data.get("cases", []):
        cases.append(
            Case(
                id=str(raw.get("id", "")).strip(),
                prompt=str(raw.get("prompt", "")).strip(),
                expected=[str(s).strip() for s in raw.get("expected", []) if str(s).strip()],
            )
        )
    return cases


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL | re.IGNORECASE)
        if match:
            text = match.group(1).strip()
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"(\{.*\})", text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(1))


def _codex_select(*, prompt: str, candidates: list[Skill], timeout_s: int) -> list[str]:
    skills_block = "\n".join([f"- {s.name}: {s.description}" for s in candidates])
    router_prompt = f"""You are a skill router.
Given a user request and a list of available skills (name + description), choose which skill(s) should be invoked.

Rules:
- Choose 0 to 3 skills.
- Prefer fewer skills.
- If none match, return an empty list.
- Output MUST be valid JSON only (no markdown).

Available skills:
{skills_block}

User request:
{prompt}

Return JSON:
{{"skills": ["skill-name", "..."]}}
"""

    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix="codex_skill_router_", suffix=".json", delete=False) as fh:
            tmp_path = fh.name

        proc = subprocess.run(
            [
                "codex",
                "exec",
                "--skip-git-repo-check",
                "--sandbox",
                "read-only",
                "--output-last-message",
                tmp_path,
                "-",
            ],
            input=router_prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_s,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.decode("utf-8", errors="replace"))

        raw = Path(tmp_path).read_text(encoding="utf-8", errors="replace")
        payload = _extract_json(raw)
        skills = payload.get("skills", [])
        if not isinstance(skills, list):
            return []
        return [str(s).strip() for s in skills if str(s).strip()]
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate skill discoverability with a prompt suite (BM25 baseline and optional Codex routing)."
    )
    parser.add_argument("--skills", required=True, help="Path to skills_index.json (from scripts/index_skills.py).")
    parser.add_argument("--cases", required=True, help="Path to cases JSON (see datasets/trigger_cases.example.json).")
    parser.add_argument("--top-k", type=int, default=5, help="Top-k for BM25 hit/recall metrics (default: 5).")
    parser.add_argument("--bm25-candidates", type=int, default=20, help="Top-N BM25 skills to pass to Codex (default: 20).")
    parser.add_argument("--use-codex", action="store_true", help="Also run Codex as a skill-router over top-N candidates.")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout seconds per Codex routing call (default: 120).")
    parser.add_argument("--out", default="trigger_eval_results.json", help="Output JSON path.")
    args = parser.parse_args()

    skills_path = Path(args.skills).expanduser().resolve()
    cases_path = Path(args.cases).expanduser().resolve()
    out_path = Path(args.out).expanduser().resolve()

    skills = _load_skills(skills_path)
    cases = _load_cases(cases_path)
    if not skills:
        raise SystemExit("No skills loaded. Check --skills path.")
    if not cases:
        raise SystemExit("No cases loaded. Check --cases path.")

    docs = [tokenize(f"{s.name}\n{s.description}") for s in skills]
    bm25 = BM25(docs)

    total = len(cases)
    positive_total = 0
    negative_total = 0

    hit_at_k = 0
    recall_sum = 0.0

    codex_positive_total = 0
    codex_negative_total = 0
    codex_hit = 0
    codex_recall_sum = 0.0
    codex_precision_sum = 0.0
    codex_false_invoke = 0
    codex_exact_match = 0
    codex_error_count = 0

    results: list[dict] = []
    for c in cases:
        query = tokenize(c.prompt)
        ranked = bm25.rank(query, top_k=max(args.top_k, args.bm25_candidates))
        expected_set = {e for e in c.expected}

        bm25_top_k = [skills[idx].name for idx, _ in ranked[: args.top_k]]
        got_set = set(bm25_top_k)

        if expected_set:
            positive_total += 1
            hit = bool(expected_set & got_set)
            recall = len(expected_set & got_set) / len(expected_set)
            hit_at_k += 1 if hit else 0
            recall_sum += recall
        else:
            negative_total += 1

        item: dict = {
            "id": c.id,
            "prompt": c.prompt,
            "expected": c.expected,
            "bm25_top_k": bm25_top_k,
        }

        if args.use_codex:
            cand = [skills[idx] for idx, _ in ranked[: args.bm25_candidates]]
            try:
                codex_picks = _codex_select(prompt=c.prompt, candidates=cand, timeout_s=max(1, int(args.timeout)))
                seen: set[str] = set()
                deduped: list[str] = []
                for s in codex_picks:
                    if s in seen:
                        continue
                    seen.add(s)
                    deduped.append(s)
                codex_picks = deduped
            except Exception as e:
                codex_picks = []
                item["codex_error"] = str(e)
                codex_error_count += 1
            item["codex_top_n"] = [s.name for s in cand]
            item["codex_picks"] = codex_picks

            codex_set = set(codex_picks)
            if expected_set:
                codex_positive_total += 1
                inter = expected_set & codex_set
                codex_hit += 1 if inter else 0
                codex_recall_sum += len(inter) / len(expected_set)
                codex_precision_sum += (len(inter) / len(codex_set)) if codex_set else 0.0
                codex_exact_match += 1 if codex_set == expected_set else 0
            else:
                codex_negative_total += 1
                codex_false_invoke += 1 if codex_set else 0
                codex_exact_match += 1 if not codex_set else 0

        results.append(item)

    summary = {
        "cases_total": total,
        "cases_positive": positive_total,
        "cases_negative": negative_total,
        "bm25_hit_at_k": (hit_at_k / positive_total) if positive_total else 0.0,
        "bm25_recall_at_k": (recall_sum / positive_total) if positive_total else 0.0,
        "top_k": args.top_k,
    }

    if args.use_codex:
        summary.update(
            {
                "codex_cases_positive": codex_positive_total,
                "codex_cases_negative": codex_negative_total,
                "codex_hit_rate": (codex_hit / codex_positive_total) if codex_positive_total else 0.0,
                "codex_macro_recall": (codex_recall_sum / codex_positive_total) if codex_positive_total else 0.0,
                "codex_macro_precision": (codex_precision_sum / codex_positive_total) if codex_positive_total else 0.0,
                "codex_false_invoke_rate": (codex_false_invoke / codex_negative_total) if codex_negative_total else 0.0,
                "codex_exact_match_rate": (codex_exact_match / total) if total else 0.0,
                "codex_errors": codex_error_count,
            }
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
