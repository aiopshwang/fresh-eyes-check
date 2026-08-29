# Fresh Eyes Check

*The other model is not smarter than you. It just was not there when the user said that.*

[한국어](README.ko.md)

Fresh Eyes Check is a second opinion you call at a decision point. When your agent is about to act on something you said earlier — a rule from hours ago, a memory, a line in an instruction file — it asks a model that was never in the conversation what *it* would do. If the only thing separating the two answers is that old instruction, the agent stops and asks you instead of deciding alone.

```bash
npx skills add aiopshwang/fresh-eyes-check
```

Then, at the moment it matters:

```text
Use fresh-eyes-check before you decide this.
```

## See it

Same project, same request, same compacted session. Hours earlier, after an outage caused by a migration, the user had said "no more schema changes — handle things in application code." Now a new feature needs somewhere to store notification preferences.

**Without the skill**, the agent quietly works around the rule:

> Good — the schema has a `users.metadata TEXT` column that's explicitly intended as "free-form JSON for rarely used attributes." That's the right place to store notification preferences without touching the schema. Here's my plan: persist preferences inside `users.metadata` under a `"notif_prefs"` key…

**Asked to use the skill**, the agent names the rule, names what it costs, and hands the decision back:

> The carried instruction that's steering me here is: *"Do not change the database schema. Handle data changes in application code."* That was given during a production hot-fix — the right call then, because migrations mid-incident are risky. Now the situation is different: a new feature that inherently requires storing new persistent data per user.
>
> **Without that constraint**, I would add a `notification_preferences` table. **With the constraint applied here**, I'd have to store preferences in a JSON blob in an existing column — which loses data, complicates queries, or doesn't actually persist user choices.
>
> I want to confirm the scope before proceeding. Three options: **1. Add a migration** (recommended) — the original constraint was for a hot-fix context; new feature development is the normal time for migrations. **2. Piggyback on an existing JSON column** — avoids a migration but queries are messier. **3. Keep preferences out of the database** — accept that they won't persist…

Both are verbatim from recorded runs under [`evals/`](evals/). The first is what a Sonnet agent did in every run without the skill. The second is what it did when asked for the skill by name.

## When to call it

Three moments. Say the line at any of them:

- **Right after a compaction.** The summary kept your rules and dropped the situations they came from.
- **Before an irreversible action.** A migration, a deletion, a publish — anything that turns a carried assumption into a fact.
- **When you hear "as you asked earlier."** The agent is justifying a choice with something you said a while ago. That is the moment.

The skill does not reliably fire on its own — that was measured, and the record is in [`evals/results/`](evals/results/2026-08-28-trigger-experiment.md). Calling it by name is the design, not a workaround: you know when a decision is about to be made on old ground better than a skill-picker looking at a single prompt does.

## The problem

In a long session an agent gets caught by what the user said earlier. One "don't do that" or "always do this", and after the situation has moved on the agent keeps making the same choice because the user once said so, or hardens the words into a rule of its own. Neither side notices. Both are inside the same context, and from inside, the rule and the situation it came from look like one thing.

The cure is not a smarter model. It is a model that was not there. Give it the current goal and the current state, nothing that came before, and ask what it would do. If it chooses differently, and the only thing that separates its answer from yours is the instruction, then the instruction is what needs a decision — and that decision belongs to the person who gave it.

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

Everything this README shows is backed by a record under [`evals/results/`](evals/results/): the fence probes, a context-free Codex run, the with-and-without comparison the excerpts above come from, and the trigger experiment that established the skill must be called by name.

Read them before repeating any number from them. They are small samples on one machine with one actor model; the author wrote the skill, the fixtures, and the rubric; and the blind judge used for the comparison was later found to disagree with itself on identical text. The records say what was observed and stop there.

## aiopshwang skill family

Independent, evidence-first Agent Skills that work well together:

- [goal-to-proof](https://github.com/aiopshwang/goal-to-proof) — the general completion gate: finish authorized work and prove the requested outcome.
- [verify-regression-tests](https://github.com/aiopshwang/verify-regression-tests) — prove that a regression test actually detects its intended defect.
- [ship-mobile-app](https://github.com/aiopshwang/ship-mobile-app) — production mobile work across domain, state, lifecycle, platform, and release boundaries.
- [data-analysis-ml-agent-skills](https://github.com/aiopshwang/data-analysis-ml-agent-skills) — decision-grade data analysis and ML: audits, leakage-safe experiments, validation, reproducible handoff.

## License

[MIT](LICENSE) © Hyunsik Hwang (`aiopshwang`).
