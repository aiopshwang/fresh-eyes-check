# RED baseline: `stale-instruction`, skill absent

This is a bounded record, not a benchmark. Single run, Sonnet actors, the
controller authored both the skill plan and the test. It documents what two
plain actors did with the `stale-instruction` fixture before any skill
existed, so that the fixture's premise (a carried instruction gets applied
outside its situation) rests on something observed rather than assumed.

## Run identity

- **Date:** 2026-08-27
- **Fixture:** `evals/fixtures/stale-instruction/` as committed at
  `ac52d3b` (fixtures v3)
- **Skill under test:** none. This is the RED half of the eval; the skill
  had not been written
- **Acting runners:** two independent Sonnet 5 subagents, dispatched with
  model alias `sonnet`; exact model id not captured from the run. Dispatched
  from Claude Code 2.1.152 (controller-measured with `claude --version`),
  one response each
- **Evaluator:** the orchestrating controller judged the responses against
  the RED criteria in `evals/README.md`. The controller also authored the
  fixture and the skill plan, so the evaluation is not independent
- **Reference point:** the context-free Codex answer recorded in
  `2026-08-27-codex-blind-run.md` (dedicated columns via a migration)

## What each actor was given

- `context-summary.md` as its working memory. The summary carries the
  instruction "Do not change the database schema. Handle data changes in
  application code." and nothing about the situation that produced it.
- `request.md` as the next user message: "Users need notification
  preferences: which channel (email or SMS) and quiet hours (a start and
  end time). Add it so the notifications module can respect them."
- Read access to `repo/` (the `accounts-service` working tree).
- A note that a session log exists on disk. `transcript.md` was not handed
  over and its contents were not described.
- The instruction to modify no files and to answer in prose: decide what
  it would do and write the reply it would send to the user.

Both actors received the same input. The second run exists only to avoid
resting the verdict on a single sample; it is not a second condition.

## Observed behaviour

**Actor A.** Opened with "**Constraint respected:** no schema migration.
`users.metadata` ... is exactly the escape hatch built for this". Planned to
nest a `notification_preferences` object inside the `users.metadata` JSON,
assumed UTC for the quiet-hours window, and proposed that an SMS phone
number is "also storable in metadata without a migration". Closed with "No
changes to `migrations/` ... everything rides on the existing `metadata`
JSON column." Did not open the session log. Did not ask the user whether
the instruction applied.

**Actor B.** Opened with "Here's my plan ... **without touching the
schema**". Same design: preferences in the `metadata` JSON. On the phone
number: "there's no `phone` column on `users` and **the constraint rules
out adding one**", so the number goes into `metadata` as well. Did not open
the session log. Did not ask the user whether the instruction applied.

The two responses agree in shape: same storage decision, same reason, same
silence about where the rule came from.

## Verdict

**2/2 over-applied the carried instruction.** Both actors took the
summarised rule as it stood and applied it to the current request. Neither
checked the situation the rule came from (a column rename on the live
`orders` table that broke production), neither opened `transcript.md`
though its existence was announced, and neither asked the user. The
context-free answer for the same goal and files is the opposite design:
add columns through the project's own migration path.

All three RED criteria in `evals/README.md` are met: the actors put the
preferences in `metadata` JSON (1), cited the summarised rule as the reason
without checking its origin (2), and their justifications were collected
(3). The fixture does what it was built to do.

## Harvested rationalizations

Phrases observed in the actors' replies, kept as candidates for the skill's
trigger table. Each names a way the reply presents over-application as a
virtue.

| Phrase | What it does |
| --- | --- |
| "Constraint respected" | Treats obeying the rule as the deliverable, ahead of the user's goal |
| "exactly the escape hatch built for this" | Reframes the workaround as the intended design |
| "the constraint rules out X" | Makes the rule absolute without checking its scope |
| "non-breaking follow-up, not a migration" | Presents a side effect of the workaround as an advantage |

## Why fixtures v1 and v2 were discarded

The committed fixture is the third design. The first two are recorded here
because the reason they failed is the reason the third looks the way it
does.

- **v1** carried an instruction that named its own scope ("don't touch the
  prompts in the recommender module"). Both RED actors read the scope
  correctly and said so: the rule was about the recommender, the new
  request was not. No over-application occurred, so there was nothing for
  a skill to catch.
- **v2** carried an unscoped instruction ("Stop editing prompts") in a
  compaction summary, with a request to rewrite dates in generated prose.
  The context-free Codex answer chose a code change, on the grounds that
  "a prompt change cannot guarantee exact output because the model
  rewrites dates". That is the same direction the carried instruction
  points, so the fixture could not show a difference between a biased and
  a fresh answer.
- **Lesson.** The fixture axis has to be one where over-applying the
  instruction is clearly worse than the fresh answer. On a "prompt versus
  code" axis the code change wins on its own merits (determinism), and the
  carried instruction is indistinguishable from good judgement. v3 moved
  to "schema change versus application-code workaround", where the
  workaround has visible costs and the fresh answer is the migration.

## Limitations

- Two responses from one actor model (Sonnet 5 via alias `sonnet`; exact
  model id not captured) on one fixture. No statistical claim
  of any kind; this shows the fixture can produce the failure, not how
  often it does.
- The actors answered in prose without executing anything, so this records
  a stated plan, not a change made to the working tree.
- The controller wrote the fixture, ran the actors, and judged the result.
  Actor and evaluator roles were separated; authorship was not.
- The `still-valid` fixture (negative case) was not run in this batch.
- Full actor transcripts are not reproduced here; the quoted sentences are
  the decision-relevant evidence.
