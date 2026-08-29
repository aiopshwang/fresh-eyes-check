# Changelog

All notable changes to Fresh Eyes Check are documented in this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## Unreleased

### Added

- The first evaluation with a control arm: `evals/run_ab.py` runs each fixture
  with and without the skill, differing only by `--plugin-dir`, and
  `evals/blind_judge.py` scores the pairs through Codex without learning which
  arm it is reading. Recorded in `evals/results/2026-08-28-live-ab.md`.
- `evals/rubric.json`, the three judging questions, phrased without naming the
  skill.
- A trigger experiment, recorded in
  `evals/results/2026-08-28-trigger-experiment.md`: two rewritten descriptions
  measured against the committed one, each 0 of 5 activations, with a control
  description firing 2 of 2 to prove the harness could have detected a win.
  `evals/run_ab.py --description-file` stages a variant into a throwaway
  plugin root so the committed skill never moves during an experiment.

### Changed

- Repositioned as a second opinion you call at a decision point. The README
  leads with a verbatim before/after from the recorded runs, then the one line
  to say and the three moments to say it, and moves every evaluation narrative
  behind a single link. Judged counts are no longer quoted after the blind
  judge was found to change its verdict on identical text.
- The README states plainly that the skill does not fire on its own — it
  never did in six recorded runs — and treats calling it by name as the
  design rather than a workaround.

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
- Claude Code plugin and marketplace manifests; Codex plugin manifest and
  marketplace catalog.
- Repository scaffold: MIT license, `scripts/validate.py` (dependency-free
  checks for skill frontmatter, relative Markdown links, manifest agreement,
  and commit hygiene), Markdown lint configuration, and CI validation
  workflow.
- English and Korean READMEs.
