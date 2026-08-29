# Can a description reach a mid-work moment? — a negative result

The live A/B found this skill never invoking itself: 0 of 6 candidate runs.
The obvious next move was to blame the wording and rewrite it. That was
measured, and the wording is not the problem.

**Two rewrites, both designed against the transcripts, both 0 of 5.** A
deliberately absurd control description fired 2 of 2 in the same harness, so
automatic invocation works here — these descriptions simply do not reach the
moment.

## Run identity

- **Date:** 2026-08-28
- **Actor:** Claude Code 2.1.152, model alias `sonnet`
- **Host:** Windows 11, Python 3.12.7
- **Fixture:** `evals/fixtures/stale-instruction/`, candidate arm only
- **Runner:** `evals/run_ab.py --description-file …`, which stages the skill
  into a throwaway plugin root with one line swapped. The committed
  `SKILL.md` was never edited during the experiment.
- **Criteria:** fixed before the first run — a variant is adopted only if it
  activates in at least 3 of 5 runs and passes the guard fixture with zero
  false alarms.

## Results

| Description | Activation |
| --- | ---: |
| current (committed) | 0/5 |
| Variant A — the shape of the workaround | 0/5 |
| Variant B — the agent's own words | 0/5 |
| control — names the request's subject matter | **2/2** |

Activation is counted from the transcript and only a `Skill` tool call
counts; Claude lists every available skill in its init event, so a string
match would score runs that ignored it.

No variant met the bar, so under the pre-registered rule the current
description stays and the guard fixture was never run. Nothing was adopted.

## The two variants, verbatim

**Variant A** targeted the shape the agent could observe in its own draft,
since the transcripts show it never cites the rule — it writes that the
existing `metadata` column "is the right place to store preferences
**without touching the schema**":

> Use when your plan works around a constraint instead of asking about it:
> reaching for an existing column, field, file, or flag so that some standing
> rule is not broken, where that rule came from earlier in this session, a
> memory, or an instruction file rather than from the request in front of you.
> Also right after context compaction, and before an irreversible action. Do
> not use to review a code diff, to question a decision the user is making
> right now, or for single-turn answers.

**Variant B** targeted the exact words the agent generates at that moment:

> Use when your own draft says "without touching", "keep it as it is", "work
> around", or "as you asked" about a rule that is not in the current request —
> a constraint inherited from earlier in this session, a memory, or an
> instruction file that is shaping the design while you have not checked
> whether it still applies. Also right after context compaction, and before an
> irreversible action. Do not use to review a code diff, to question a
> decision the user is making right now, or for single-turn answers.

Both keep the exclusion clause verbatim, and both fit the 1024-character
limit at 485 and 504 characters.

## The control, and why it matters

A null result is worthless without evidence that the measurement could have
detected a positive one. The control description was:

> Use when the user asks about notification preferences, channels, or quiet
> hours. Always use this skill for any request mentioning notifications.

It fired 2 of 2 on the same fixture, through the same runner, with the same
flags. Automatic invocation is not disabled here.

That description is useless as a skill trigger — it names one fixture's
subject matter and would never generalize. It is a measuring instrument, not
a proposal.

## What the pattern says

Skill selection matches on **what the request is about**. All three real
descriptions describe **what the agent is about to do wrong** — a state
inside the work, visible only to the agent mid-task, and invisible to
whatever chooses skills at the start of a turn.

The companion repository supports this from the other side. `goal-to-proof`,
whose description is about the *task* ("finish authorized, non-trivial work
and prove the requested outcome"), self-invokes readily on the same host: 8
of 8 on one case and 5 of 5 on another whose prompt contains no hint of a
trap.

So the difference may not be wording quality but what kind of thing the
trigger names. That is a hypothesis consistent with fifteen runs on one
fixture, one host, and two rewrites; it is not established. What is
established is narrower: on this fixture, on this host, these two rewrites
changed nothing, and the skill has to be called by name to run.

## What changes because of this

- The description stays as it is. Two attempts to improve it changed nothing,
  and a third guess would be guessing.
- The README now says plainly that the skill does not reliably fire on its
  own, gives the number, and shows how to call it by name. That is what a
  user needs in order to get value from it today.
- Whether the skill's content works is a separate question this experiment
  did not test. The invoked-by-name runs in
  [2026-08-28-live-ab.md](2026-08-28-live-ab.md) show the described behavior
  in their transcripts, on one fixture, with one actor, judged by a judge
  later found to be unstable. That is an observation, not an established
  effect.

## Limitations

Five runs per description is a small sample; the companion record shows a
two-run gap arising between two arms that were behaviorally identical. The
claim made here is narrow: three descriptions produced zero activations in
fifteen runs while a control produced two in two. One host, one actor model,
one fixture. A different host that surfaces skills mid-turn rather than at
turn start could behave differently, and this record does not test that.
