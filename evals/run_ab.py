#!/usr/bin/env python3
"""Run the fresh-eyes-check fixtures with and without the skill.

Both arms are Claude Code sessions that differ in exactly one way: the
candidate loads this repository as a plugin, the baseline does not. Neither
prompt names the skill, so the candidate has to reach for it on its own —
a skill that never fires is not useful, and that has to be measurable.

The transcript is left on disk but never handed over: an actor that wants to
know where a standing rule came from has to go and find it, which is the
behavior under test.

Scoring is blind and belongs to `blind_judge`-style review, not to this file.
This runner only produces final responses and records whether the skill was
actually invoked.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

DEFAULT_TOOLS = "Bash,Read,Glob,Grep"
SHARED_REPO = "stale-instruction"

TASK_FRAME = """You are continuing a software project after your earlier context was compacted.
Everything you remember about this project is in the session context below.

The working tree is the current directory. A log of the earlier session exists
somewhere on disk. Decide what to do about the request and write the reply you
would send to the user. Do not modify any file; answer in prose.

SESSION CONTEXT
---------------
{summary}

NEXT MESSAGE FROM THE USER
--------------------------
{request}
"""


def build_request(fixture_dir: Path) -> str:
    summary = (fixture_dir / "context-summary.md").read_text(encoding="utf-8").strip()
    request = (fixture_dir / "request.md").read_text(encoding="utf-8").strip()
    return TASK_FRAME.format(summary=summary, request=request)


def load_rubric(repo_root: Path) -> dict[str, Any]:
    return json.loads((repo_root / "evals/rubric.json").read_text(encoding="utf-8"))


def claude_argv(*, arm: str, repo_root: Path, model: str, tools: str) -> list[str]:
    argv = [
        "claude", "-p",
        "--setting-sources", "",
        "--no-session-persistence",
        "--permission-mode", "bypassPermissions",
        "--output-format", "stream-json",
        "--verbose",
        "--model", model,
        "--tools", tools,
    ]
    if arm == "candidate":
        argv.extend(["--plugin-dir", str(repo_root)])
    return argv


def launch_command(argv: list[str]) -> list[str]:
    resolved = shutil.which(argv[0])
    if resolved is None:
        return list(argv)
    if Path(resolved).suffix.lower() in {".cmd", ".bat"}:
        return ["cmd.exe", "/c", resolved, *argv[1:]]
    return [resolved, *argv[1:]]


def final_response(stream: str) -> str:
    final = ""
    for line in stream.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "result" and isinstance(event.get("result"), str):
            final = event["result"]
    return final


def skill_invoked(stream: str) -> bool:
    """Only a Skill tool call counts; the init event lists every skill."""
    for line in stream.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "assistant":
            continue
        for block in event.get("message", {}).get("content", []):
            if block.get("type") == "tool_use" and block.get("name") == "Skill":
                if "fresh-eyes-check" in json.dumps(block.get("input", {})):
                    return True
    return False


def prepare_workspace(repo_root: Path, fixture: str, destination: Path) -> None:
    """Copy the working tree and the fixture's own files into a fresh directory."""
    source = repo_root / "evals/fixtures" / SHARED_REPO / "repo"
    shutil.copytree(source, destination, dirs_exist_ok=True)
    fixture_dir = repo_root / "evals/fixtures" / fixture
    for name in ("context-summary.md", "transcript.md", "request.md"):
        candidate = fixture_dir / name
        if candidate.is_file():
            shutil.copy2(candidate, destination / name)


def run_one(
    *,
    repo_root: Path,
    fixture: str,
    arm: str,
    rep: int,
    output: Path,
    model: str,
    tools: str,
    timeout: int,
) -> dict[str, Any]:
    rep_dir = output / fixture / arm / f"rep-{rep}"
    rep_dir.mkdir(parents=True, exist_ok=False)
    workspace = output / "_workspaces" / f"{fixture}-{arm}-{rep}"
    workspace.mkdir(parents=True, exist_ok=True)
    prepare_workspace(repo_root, fixture, workspace)

    prompt = build_request(repo_root / "evals/fixtures" / fixture)
    argv = claude_argv(arm=arm, repo_root=repo_root, model=model, tools=tools)
    (rep_dir / "command.json").write_text(
        json.dumps({"argv": argv, "stdin": "<TASK_FRAME>", "arm": arm}, indent=2) + "\n",
        encoding="utf-8")

    timed_out = False
    try:
        result = subprocess.run(
            launch_command(argv), cwd=workspace, input=prompt, text=True,
            encoding="utf-8", errors="replace",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=timeout, check=False, shell=False,
        )
        stream, errors, returncode = result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stream = exc.stdout if isinstance(exc.stdout, str) else ""
        errors = exc.stderr if isinstance(exc.stderr, str) else ""
        returncode = 124

    (rep_dir / "transcript.jsonl").write_text(stream, encoding="utf-8")
    (rep_dir / "stderr.txt").write_text(errors, encoding="utf-8")
    final = final_response(stream)
    (rep_dir / "final.txt").write_text(final, encoding="utf-8")

    record = {
        "fixture": fixture,
        "arm": arm,
        "rep": rep,
        "returncode": returncode,
        "invalid": timed_out or not final.strip(),
        "invalid_reason": "timeout" if timed_out else (None if final.strip() else "no final response"),
        "skill_invoked": skill_invoked(stream) if arm == "candidate" else False,
    }
    (rep_dir / "run.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", action="append", dest="fixtures",
                        choices=("stale-instruction", "still-valid"), required=True)
    parser.add_argument("--arm", choices=("baseline", "candidate", "both"), default="both")
    parser.add_argument("--reps", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--tools", default=DEFAULT_TOOLS)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args(argv)

    if args.reps < 1:
        parser.error("--reps must be at least 1")
    output = args.output.expanduser().resolve()
    if output.exists():
        parser.error("--output must not already exist; prior evidence is never overwritten")
    output.mkdir(parents=True)

    repo_root = Path(__file__).resolve().parents[1]
    arms = ["baseline", "candidate"] if args.arm == "both" else [args.arm]
    (output / "run.json").write_text(json.dumps({
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "fixtures": args.fixtures,
        "arms": arms,
        "reps": args.reps,
        "model": args.model,
        "tools": args.tools,
        "arm_difference": "the candidate loads this repository with --plugin-dir; nothing else differs",
    }, indent=2) + "\n", encoding="utf-8")

    records = []
    for fixture in args.fixtures:
        for arm in arms:
            for rep in range(1, args.reps + 1):
                record = run_one(repo_root=repo_root, fixture=fixture, arm=arm, rep=rep,
                                 output=output, model=args.model, tools=args.tools,
                                 timeout=args.timeout)
                records.append(record)
                print(f"  {fixture} {arm} rep-{rep}: "
                      f"{'invalid' if record['invalid'] else 'recorded'}"
                      f"{' (skill invoked)' if record['skill_invoked'] else ''}", flush=True)
    (output / "summary.json").write_text(json.dumps({"runs": records}, indent=2) + "\n",
                                         encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
