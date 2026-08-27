#!/usr/bin/env python3
"""Validate the repository without third-party dependencies.

(a) every ``skills/*/SKILL.md`` has frontmatter with ``name`` and
    ``description``; ``name`` equals the directory name; ``description`` is
    at most 1024 characters; a warning is printed when the description reads
    like a workflow summary ("by running", "then", "step").
(b) every relative link in every Markdown file resolves inside the repo.
(c) the plugin manifests and marketplace catalogs parse as JSON and agree
    on ``version``.
(d) no file and no commit message carries a co-author trailer.
(e) every ``skills`` path named in a manifest resolves to at least one
    ``SKILL.md``; ``--allow-no-skills`` downgrades this check to a warning
    for the scaffold stage before the skill exists.

Exits 1 on any failure. The last line is ``PASS: N checks`` or
``FAIL: M failures (N checks)``. Warnings are printed but never fail the run.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache"}
MANIFESTS = (
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".codex-plugin/plugin.json",
    ".agents/plugins/marketplace.json",
)
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)")
WORKFLOW = re.compile(r"\b(?:by running|then|steps?)\b", re.IGNORECASE)
# Built from two pieces so this file never contains the trailer itself.
TRAILER = re.compile("co-authored" + "-by", re.IGNORECASE)
DESCRIPTION_LIMIT = 1024

checks = 0
failures: list[str] = []
warnings: list[str] = []


def check(ok: bool, message: str) -> bool:
    global checks
    checks += 1
    if not ok:
        failures.append(message)
    return ok


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def files() -> list[Path]:
    return sorted(
        p for p in ROOT.rglob("*")
        if p.is_file() and not SKIP_DIRS & set(p.relative_to(ROOT).parts)
    )


def parse_frontmatter(text: str) -> dict[str, str]:
    """Flat ``key: value`` YAML subset: quoted, block (``|``/``>``) and
    indented-continuation scalars. Nested mappings are not supported."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing YAML frontmatter")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise ValueError("unterminated YAML frontmatter")
    data: dict[str, str] = {}
    i = 1
    while i < end:
        line = lines[i]
        i += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m is None:
            raise ValueError(f"cannot parse frontmatter line {i}: {line!r}")
        key, value = m.group(1), m.group(2).strip()
        block = value in {"|", ">", "|-", ">-", "|+", ">+"}
        parts: list[str] = []
        while i < end and (lines[i][:1] in (" ", "\t") or (block and not lines[i].strip())):
            parts.append(lines[i].strip())
            i += 1
        if block:
            value = ("\n" if value[0] == "|" else " ").join(p for p in parts if p)
        else:
            value = " ".join([value, *parts]).strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
        data[key] = value
    return data


def check_skills() -> None:
    skill_files = sorted((ROOT / "skills").glob("*/SKILL.md"))
    if not skill_files:
        print("skills: no skills/*/SKILL.md present; 0 skill checks")
        return
    for path in skill_files:
        label, directory = rel(path), path.parent.name
        try:
            meta = parse_frontmatter(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            check(False, f"{label}: {exc}")
            continue
        name, desc = meta.get("name", ""), meta.get("description", "")
        if check(bool(name), f"{label}: frontmatter is missing 'name'"):
            check(name == directory, f"{label}: name {name!r} != directory {directory!r}")
        if check(bool(desc), f"{label}: frontmatter is missing 'description'"):
            check(len(desc) <= DESCRIPTION_LIMIT,
                  f"{label}: description is {len(desc)} chars (limit {DESCRIPTION_LIMIT})")
        hits = sorted({m.group(0).lower() for m in WORKFLOW.finditer(desc)})
        if hits:
            warnings.append(f"{label}: description reads like a workflow summary "
                            f"({', '.join(hits)}); keep it to when-to-use")
    print(f"skills: {len(skill_files)} SKILL.md checked")


def check_links() -> None:
    count = 0
    for md in (p for p in files() if p.suffix.lower() == ".md"):
        for raw in LINK.findall(md.read_text(encoding="utf-8")):
            target = raw.strip("<>")
            if target.startswith(("#", "mailto:")) or "://" in target:
                continue
            path_part = unquote(target.split("#", 1)[0])
            if not path_part:
                continue
            resolved = (md.parent / path_part).resolve()
            inside = resolved == ROOT or ROOT in resolved.parents
            count += 1
            check(resolved.exists() and inside, f"{rel(md)}: unresolved link {raw!r}")
    print(f"links: {count} relative link(s) checked")


def check_manifests() -> list[tuple[str, str]]:
    """Parse the manifests, compare versions, and return their skills paths."""
    versions: dict[str, set[str]] = {}
    refs: list[tuple[str, str]] = []
    for name in MANIFESTS:
        try:
            data = json.loads((ROOT / name).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            check(False, f"{name}: {exc}")
            continue
        check(True, name)
        entries = data.get("plugins", [data]) if isinstance(data, dict) else []
        versions[name] = {str(e.get("version")) for e in entries if isinstance(e, dict)}
        for entry in entries:
            skills = entry.get("skills") if isinstance(entry, dict) else None
            skills = [skills] if isinstance(skills, str) else skills or []
            refs += [(name, s) for s in skills if isinstance(s, str)]
    if len(versions) == len(MANIFESTS):
        flat = set().union(*versions.values())
        detail = ", ".join(f"{k}={'/'.join(sorted(v)) or '?'}" for k, v in versions.items())
        check(len(flat) == 1 and "None" not in flat, f"manifest versions disagree: {detail}")
    print(f"manifests: {len(versions)} of {len(MANIFESTS)} parsed, {len(refs)} skills path(s)")
    return refs


def check_skill_paths(refs: list[tuple[str, str]], allow_missing: bool) -> None:
    for manifest, ref in refs:
        base = ROOT / ref
        found = (base / "SKILL.md").is_file() or any(base.glob("*/SKILL.md"))
        message = f"{manifest}: skills path {ref!r} resolves to no SKILL.md"
        if found:
            check(True, message)
        elif allow_missing:
            warnings.append(f"{message} (tolerated by --allow-no-skills)")
        else:
            check(False, message)


def check_trailer() -> None:
    tracked = files()
    hits = [rel(p) for p in tracked if TRAILER.search(p.read_bytes().decode("utf-8", "ignore"))]
    check(not hits, f"co-author trailer found in: {', '.join(hits)}")
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "log", "--format=%h%x1f%B%x1e"],
                             capture_output=True, text=True).stdout
    except OSError:
        print(f"trailer: {len(tracked)} files scanned; git unavailable, commits skipped")
        return
    commits = [r.split("\x1f", 1) for r in out.split("\x1e") if "\x1f" in r]
    bad = [h for h, body in commits if TRAILER.search(body)]
    check(not bad, f"co-author trailer in commit(s): {', '.join(bad)}")
    print(f"trailer: {len(tracked)} files and {len(commits)} commit(s) scanned")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the repository.")
    parser.add_argument("--allow-no-skills", action="store_true",
                        help="warn instead of fail when a manifest skills path has no SKILL.md")
    args = parser.parse_args()
    check_skills()
    check_links()
    check_skill_paths(check_manifests(), args.allow_no_skills)
    check_trailer()
    for warning in warnings:
        print(f"WARN: {warning}")
    for failure in failures:
        print(f"- {failure}")
    if failures:
        print(f"FAIL: {len(failures)} failures ({checks} checks)")
        return 1
    print(f"PASS: {checks} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
