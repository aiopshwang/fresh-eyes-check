# Changelog

All notable changes to Fresh Eyes Check are documented in this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## 0.1.0 — 2026-08-27

### Added

- The `fresh-eyes-check` skill: `SKILL.md` with the trigger signals and
  excuse table, the context-free ask, the comparison table, and the owner
  question; three references (`blind-brief.md`, `runtime-recipes.md`,
  `owner-question.md`) and the `carried-instruction.md` asset.
- Two synthetic evaluation fixtures, `stale-instruction` and `still-valid`,
  with the judging criteria recorded in `evals/README.md`.
- Evaluation records under `evals/results/`: the RED baseline (skill absent,
  two actors), the blind Codex run that supplies the reference answer with
  its brief verbatim, the fence probes that measured the runtime isolation
  flags, and the GREEN and negative-case run with the description
  spot-check.
- Claude Code and Codex plugin manifests for `fresh-eyes-check` (0.1.0).
- Repository scaffold: MIT license, `scripts/validate.py` (dependency-free
  checks for skill frontmatter, relative Markdown links, manifest agreement,
  and commit hygiene), Markdown lint configuration, and CI validation
  workflow.
- English and Korean READMEs.
