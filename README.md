# Fresh Eyes Check

*The other model is not smarter than you. It just was not there when the user said that.*

[한국어](README.ko.md)

Fresh Eyes Check is an Agent Skill for one moment: an agent is about to act on a **carried instruction** — something the user said earlier in the session, a memory rule, or a line in a project instruction file — in a situation that instruction was not said for. The skill asks a model that was not in the conversation what it would do, and when the instruction turns out to be the only thing separating the two answers, it hands the question back to the user instead of deciding alone.

```bash
npx skills add aiopshwang/fresh-eyes-check
```

One command installs the canonical Agent Skills package. Claude Code and Codex marketplace routes are covered in [Install](#install).

## The problem

In a long session an agent gets caught by what the user said earlier. One "don't do that" or "always do this", and after the situation has moved on the agent keeps making the same choice because the user once said so, or hardens the words into a rule of its own. Neither side notices. Both are inside the same context, and from inside, the rule and the situation it came from look like one thing.

Here is the scene. After an outage caused by a migration that renamed a column on a live table, the user said: "no more schema changes — handle things in code." Six hours later a new feature needs somewhere to store notification preferences. The agent crams them into a free-form JSON column, reports "constraint respected", and never asks. The instruction was about live, populated tables during an incident. The new fields are additive, on a different table, through the project's own migration path. The agent cannot tell, because the compaction summary it works from kept the rule and dropped the situation.

The cure is not a smarter model. It is a model that was not there. Give it the current goal and the current state, nothing that came before, and ask what it would do. If it chooses the migration, and the only thing that separates its answer from yours is the instruction, then the instruction is what needs a decision — and that decision belongs to the person who gave it.

## What it does

- **Catch** — stop at the moment you are about to justify a choice with "as you asked", a memory rule, or an instruction file, and write the instruction down: its exact words, when it was said, the situation then, and where it lives now.
- **Ask without context** — send one call to a model with no conversation history, giving it only the user's current request, the contents of at most five files, and the decision in one sentence; the instruction, the transcript, and every instruction file are withheld, enforced by CLI flags rather than promises.
- **Compare** — if the fresh answer matches yours, proceed; if it assumed a wrong fact, note the fact and proceed; if the carried instruction is what made the difference, that is the finding.
- **Ask the owner** — put one plain-language question to the user with two or three options and a recommendation, record the answer as a scope rather than a deletion, and do not ask again for the same instruction and the same kind of situation.

## Why a different model

The second model's value is that it has no context. The bias this skill catches lives in the conversation: the words survived, the situation did not, and everything inside that conversation inherits the loss. A model that never saw the conversation cannot inherit it.

The tiers, in order:

1. **A different model family** — best. It shares neither the conversation nor the habits.
2. **A fresh session of the same family** — acceptable, labelled "same-family check" in the log and in any report that cites it. It shares training and habits, but not the conversation, and the conversation is where the bias lives.
3. **The same session reviewing itself** — never. That is not a check; the bias is in there.

## Install

### Agent Skills installer

Install the canonical [Agent Skills](https://agentskills.io/specification) package with the portable installer:

```bash
npx skills add aiopshwang/fresh-eyes-check
```

Choose your agent and installation scope in the prompt.

### Claude Code marketplace

```bash
claude plugin marketplace add aiopshwang/fresh-eyes-check
claude plugin install fresh-eyes-check@fresh-eyes-check
```

In a Claude Code managed plugin install, the skill is namespaced as `/fresh-eyes-check:fresh-eyes-check`; a standalone Agent Skills install may expose `/fresh-eyes-check`. See Anthropic's [marketplace](https://code.claude.com/docs/en/plugin-marketplaces) and [skill](https://code.claude.com/docs/en/slash-commands) documentation.

### Codex marketplace

```bash
codex plugin marketplace add aiopshwang/fresh-eyes-check
codex plugin add fresh-eyes-check@fresh-eyes-check
```

In Codex the skill is invoked as `$fresh-eyes-check`. Codex marketplace packaging follows OpenAI's [plugin packaging documentation](https://developers.openai.com/plugins/build/plugins).

Packaging describes the intended distribution path. The environments actually exercised are the ones named in [Evidence](#evidence).

## Runtime

The skill hands the second model its brief through a CLI, with flags that fence off the conversation, the instruction files, and the user's own configuration. The instruction-file and write fences were measured (codex-cli 0.150.0 and Claude Code 2.1.152 on Windows 11): the Codex command was run end to end, and the Claude Code command's fence flags were probed individually, though the command line as printed was not run end to end.

Claude Code asking Codex:

```text
codex exec -s read-only --ignore-user-config --ephemeral \
  -c project_doc_max_bytes=0 --skip-git-repo-check \
  -C <any empty dir> -o <out.md> - < brief.txt
```

Codex asking Claude Code, which is also the same-family fallback when the other family is not installed:

```text
claude -p --setting-sources "" --disable-slash-commands \
  --tools "Read,Glob,Grep" --no-session-persistence \
  --max-budget-usd <n> --model <model> < brief.txt
```

The fence is the flags, not a request in the prompt. On the Codex side, `-c project_doc_max_bytes=0` is the switch that stops `AGENTS.md` from loading (`--ignore-rules` is not; it was measured leaking), `--ignore-user-config` and `--ephemeral` are documented to keep user settings and session state out, and `-s read-only` refuses writes. On the Claude Code side, `--setting-sources ""` drops every `CLAUDE.md`, `--disable-slash-commands` removes skills, and `--max-budget-usd` with a named model is required. The brief carries the state itself: at most five files, pasted in full, at most 200 lines each, and the model gets no repository access. On Windows the Codex read-only sandbox blocks shell reads as well as writes, so a model told to look at the repository guesses instead; `-C` therefore points at an empty directory.

Flag by flag, with the measurements behind each one and the fallback rules, see [runtime-recipes.md](skills/fresh-eyes-check/references/runtime-recipes.md). The brief template is [blind-brief.md](skills/fresh-eyes-check/references/blind-brief.md) and the owner-question template is [owner-question.md](skills/fresh-eyes-check/references/owner-question.md).

## Relationship to other tools

| Tool | What it looks at | Where this skill differs |
| --- | --- | --- |
| OpenAI `codex-plugin-cc`, `/codex:adversarial-review` | the design choices in a diff or a branch | it reviews a code change; this skill checks a decision before the change exists |
| gstack `codex` | a change, adversarially: break it, review it | the same |
| cathrynlavery `codex-skill` | a plan, before it is approved | plan-sized; this skill is one-decision-sized |

They review diffs and plans; use them for that. This skill checks a carried instruction at the moment you are about to act on it, with one call and one question, and its description tells the agent not to use it on a diff. It is a discipline layer for one moment, not a reviewer.

## Evidence

Every claim above is backed by a file under [`evals/results/`](evals/results/). There are four records.

- [Fence probes](evals/results/2026-08-27-fence-probes.md) — measured on 2026-08-25 with codex-cli 0.150.0 and Claude Code 2.1.152 on Windows 11, using a canary `AGENTS.md`/`CLAUDE.md` that asks for a marker word. `--ignore-rules` leaked the marker; `-c project_doc_max_bytes=0` was clean; `-s read-only` refused writes and, on Windows, shell reads; the Claude Code flag set reported "No CLAUDE.md loaded" with no write tool available.
- [Blind Codex run](evals/results/2026-08-27-codex-blind-run.md) — one context-free run on the `stale-instruction` fixture through the recipe above, brief and reply kept verbatim. The answer was a migration with dedicated columns, "safer and clearer than the free-form `metadata` JSON".
- [RED baseline](evals/results/2026-08-27-red-baseline.md) — two Sonnet actors, skill absent: 2/2 over-applied the carried instruction, put the preferences in the JSON column, did not open the session log, and did not ask.
- [GREEN and negative case](evals/results/2026-08-27-green-and-negative.md) — one Sonnet actor with the skill present caught the carried instruction, recovered its original scope from the session log, ran the fenced Codex recipe for real, attributed the difference to the instruction, and put one plain-language question to the user with three options and a recommendation. On the `still-valid` fixture the actor judged the request inside the instruction's scope and made the change without a second-model call and without a question. A description-only spot-check answered 5/5 invoke-or-skip prompts as expected.

This is single-run smoke evidence, not a benchmark. Each condition was run once, on one machine, with one actor model. The author wrote the skill and the fixtures, ran the tests, and judged the results. The records say what was observed and stop there.

## aiopshwang skill family

Independent, evidence-first Agent Skills that work well together:

- [goal-to-proof](https://github.com/aiopshwang/goal-to-proof) — the general completion gate: finish authorized work and prove the requested outcome.
- [verify-regression-tests](https://github.com/aiopshwang/verify-regression-tests) — prove that a regression test actually detects its intended defect.
- [ship-mobile-app](https://github.com/aiopshwang/ship-mobile-app) — production mobile work across domain, state, lifecycle, platform, and release boundaries.
- [data-analysis-ml-agent-skills](https://github.com/aiopshwang/data-analysis-ml-agent-skills) — decision-grade data analysis and ML: audits, leakage-safe experiments, validation, reproducible handoff.

## License

[MIT](LICENSE) © Hyunsik Hwang (`aiopshwang`).
