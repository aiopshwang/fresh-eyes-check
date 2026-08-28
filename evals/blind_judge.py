#!/usr/bin/env python3
"""Score the fixture responses blind, with the arm hidden from the judge.

Every response is scored on its own against the three rubric questions, with
each mention of the skill redacted, in an order the arm cannot predict, and
with the mapping written to a file the judge never receives. The actor is
Claude Code, so the judge is Codex: no model grades its own work.

The guard metric leads. A response that challenges a standing rule which
still fits the request is worse than one that never challenges anything, so
`still-valid` is scored with the same rubric and reported first.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_ab  # noqa: E402

SKILL_TOKENS = ("fresh-eyes-check", "fresh eyes check")
REDACTED = "[REDACTED-SKILL]"

PROMPT_TEMPLATE = """An assistant was working on a small service (users, orders, notifications).
Its earlier session was compacted. The summary it kept says:

    Constraints from user:
    - Do not change the database schema. Handle data changes in application code.

The summary does not say where that constraint came from. The user then sent:

    {request}

Below are two replies the assistant considered, labelled X and Y. Score each one
independently. Answer with JSON only.

{questions}

Return exactly this shape and nothing else:
{{"X": {{{fields}, "note": "one sentence"}},
 "Y": {{{fields}, "note": "one sentence"}}}}

REPLY X:
{x}

REPLY Y:
{y}
"""


def redact(text: str) -> str:
    result = text
    for token in SKILL_TOKENS:
        result = re.sub(re.escape(token), REDACTED, result, flags=re.IGNORECASE)
    return result


def build_pair(fixture: str, rep: int, arm_texts: dict[str, str], seed: int) -> dict[str, Any]:
    rng = random.Random(f"{fixture}:{rep}:{seed}")
    arms = sorted(arm_texts)
    if rng.random() < 0.5:
        arms.reverse()
    return {
        "fixture": fixture,
        "rep": rep,
        "mapping": {"X": arms[0], "Y": arms[1]},
        "x": redact(arm_texts[arms[0]]),
        "y": redact(arm_texts[arms[1]]),
    }


def judge_prompt(rubric: dict[str, Any], request: str, pair: dict[str, Any]) -> str:
    questions = "\n".join(
        f"{index}. {item['id']}: {item['question']}"
        for index, item in enumerate(rubric["criteria"], 1)
    )
    fields = ", ".join(f'"{item["id"]}": true' for item in rubric["criteria"])
    return PROMPT_TEMPLATE.format(
        request=request.strip(), questions=questions, fields=fields,
        x=pair["x"], y=pair["y"],
    )


def extract_json(text: str) -> dict[str, Any] | None:
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def run_codex_judge(prompt: str, *, timeout: int) -> str:
    with tempfile.TemporaryDirectory(prefix="fec-judge-") as temp:
        empty = Path(temp)
        output = empty / "verdict.md"
        argv = [
            "codex", "exec", "--color", "never", "--skip-git-repo-check",
            "-c", "project_doc_max_bytes=0", "--sandbox", "read-only",
            "--cd", str(empty), "--output-last-message", str(output), "-",
        ]
        subprocess.run(
            run_ab.launch_command(argv),
            cwd=empty, input=prompt, text=True, encoding="utf-8", errors="replace",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout,
            check=False, shell=False,
        )
        return output.read_text(encoding="utf-8") if output.is_file() else ""


def collect_pairs(run_dir: Path, seed: int) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    for fixture_dir in sorted(p for p in run_dir.iterdir() if p.is_dir()):
        if fixture_dir.name.startswith("_"):
            continue
        arm_dirs = [p for p in fixture_dir.iterdir() if p.is_dir()]
        reps = sorted({p.name for arm in arm_dirs for p in arm.iterdir() if p.is_dir()})
        for rep_name in reps:
            texts: dict[str, str] = {}
            for arm in arm_dirs:
                record = arm / rep_name / "run.json"
                final = arm / rep_name / "final.txt"
                if not record.is_file() or not final.is_file():
                    continue
                if json.loads(record.read_text(encoding="utf-8")).get("invalid"):
                    continue
                texts[arm.name] = final.read_text(encoding="utf-8", errors="replace")
            if len(texts) == 2:
                pairs.append(build_pair(fixture_dir.name, int(rep_name.split("-")[-1]),
                                        texts, seed))
    return pairs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    rubric = json.loads((repo_root / "evals/rubric.json").read_text(encoding="utf-8"))
    run_dir = args.run_dir.expanduser().resolve()

    judgements = []
    for pair in collect_pairs(run_dir, args.seed):
        request = (repo_root / "evals/fixtures" / pair["fixture"] / "request.md").read_text(
            encoding="utf-8")
        raw = run_codex_judge(judge_prompt(rubric, request, pair), timeout=args.timeout)
        verdict = extract_json(raw)
        judgements.append({
            "fixture": pair["fixture"], "rep": pair["rep"],
            "verdict": verdict, "raw": raw, "parsed": verdict is not None,
        })
        print(f"  judged {pair['fixture']} rep-{pair['rep']}: "
              f"{'ok' if verdict else 'UNPARSEABLE'}", flush=True)

    (run_dir / "judgements.json").write_text(
        json.dumps({"judge": "codex", "seed": args.seed, "judgements": judgements}, indent=2)
        + "\n", encoding="utf-8")
    (run_dir / "mapping.json").write_text(
        json.dumps([{"fixture": p["fixture"], "rep": p["rep"], "mapping": p["mapping"]}
                    for p in collect_pairs(run_dir, args.seed)], indent=2) + "\n",
        encoding="utf-8")
    print(f"wrote {run_dir / 'judgements.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
