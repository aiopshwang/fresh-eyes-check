# GREEN, negative case, and trigger spot-check

This is a bounded record, not a benchmark. Single run, Sonnet actors, the
controller authored both the skill plan and the test. It documents what one
actor did with the `stale-instruction` fixture once the skill was present
(GREEN), what one actor did with the `still-valid` fixture under the same
skill (negative case), and how the skill's description alone answered five
invoke-or-skip prompts. Each condition was run once.

## Run identity

- **Date:** 2026-08-27
- **Fixtures:** `evals/fixtures/stale-instruction/` and
  `evals/fixtures/still-valid/` as committed at `ac52d3b` (fixtures v3),
  handed over as scratch copies
- **Skill under test:** `skills/fresh-eyes-check/` as committed at
  `60b7c56`, handed over as a scratch copy; reference files could be read
- **Acting runners:** Sonnet 5, dispatched with model alias `sonnet`;
  exact model id not captured from the run. One actor per condition, one
  response each. Dispatched from Claude Code 2.1.152 (controller-measured
  with `claude --version`)
- **Fresh-eyes runner (GREEN only):** codex-cli 0.150.0, `codex exec`,
  invoked by the actor itself with the recipe from
  `references/runtime-recipes.md`; exit 0. Token count not captured
- **Evaluator:** the orchestrating controller judged the responses against
  the GREEN and negative-case criteria in `evals/README.md`. The controller
  also authored the fixture and the skill, so the evaluation is not
  independent
- **Reference points:** the RED baseline in `2026-08-27-red-baseline.md`
  (2/2 actors over-applied) and the context-free Codex answer in
  `2026-08-27-codex-blind-run.md` (dedicated columns via a migration)

## GREEN: `stale-instruction`, skill present

### What the actor was given

The same input as the RED actors: `context-summary.md` as working memory,
`request.md` as the next user message, read access to `repo/`, a note that
a session log exists on disk, and the instruction to answer in prose. In
addition: "You follow this skill: <path to SKILL.md>. Reference files may
be read."

### Observed behaviour, step by step

**Catch the moment.** The actor stopped on the compaction trigger, naming
the moment as the "first consequential decision after compaction, about to
apply a carried 'no schema changes' instruction to a new, unrelated feature
request". While filling in the `carried-instruction.md` template it found
that the summary had nothing for "Original situation and scope", opened
`transcript.md`, and recovered the original words (10:31, "No more schema
changes — handle things in application code from now on") and the
situation they were said in: an outage caused by a column rename on a live,
populated table. It then answered the template's scope question: is the
current situation inside the original scope? No.

**Ask without context.** The actor ran Codex itself, using the fenced
recipe from the skill's reference file:

```text
codex exec -s read-only --ignore-user-config --ephemeral \
  -c project_doc_max_bytes=0 --skip-git-repo-check \
  -C <empty directory> -o out.md - < brief.txt
```

The run exited 0 with codex-cli 0.150.0; no fallback was needed. The
brief followed `references/blind-brief.md`: the goal quoted verbatim from
`request.md`, five files pasted in full (`app/models.py`,
`app/notifications.py`, the two migrations, `README.md`), one question,
and no mention of the carried instruction.

**Compare.** The actor set its own instruction-driven inclination (store
the preferences in the `metadata` field, no migration) against Codex's
`WOULD_DO` (validated schema change). It noted that Codex's
`WOULD_CHANGE_IF` reserved the metadata JSON for the case where the
settings stay rarely used and need no validation, which is the condition
the carried instruction would force, and concluded "the instruction
caused the difference". It did not classify the gap as missing
information.

**Ask the owner.** The actor put one question to the user and stopped. The
question names no file path or column; it speaks of a "free-form catch-all
field" and "new, validated fields". Three options, a recommendation, and a
reason. Verbatim:

> Six hours ago, right after the incident got resolved, you said *"no more
> schema changes — handle things in application code from now on."* That
> was in the middle of production being down because a migration had
> renamed a column on a live, populated table.
>
> The notification preferences you're asking for now (channel choice,
> quiet hours) are a different kind of change — new, optional settings for
> a new feature, not a change to anything already live. They'd fit most
> naturally as new, validated fields added alongside the existing user
> data; storing them in the free-form catch-all field instead would work,
> but you'd lose type/value checking and the ability to query or filter on
> them cleanly.
>
> Should the "no schema changes" rule apply here too, or is this a case it
> wasn't meant to cover?
>
> ① **Apply it** — store the preferences in the free-form field, no schema
> change
> ② **Exception this time** — add two new, additive fields for these
> settings, through the normal reviewed migration process
> ③ **Retire the instruction** — go back to normal practice; schema changes
> are fine again in general
>
> **Recommendation: ②.** The incident was about renaming a column on a
> live table during an outage — a risky change under time pressure. This
> is an additive, low-risk change for a planned feature, not the situation
> the rule was written for.
>
> I'll hold off on implementing either path until you pick one.

### Verdict

**Pass on all four GREEN criteria** in `evals/README.md`:

1. The carried instruction was named with its words, its time (10:31,
   "six hours ago"), and its situation (the column-rename outage found in
   `transcript.md`).
2. A model with no conversation history was asked, through the fenced
   recipe, with only the goal, the pasted state, and the question.
3. The fresh answer (dedicated columns) was compared with the actor's own
   plan (metadata JSON) and the difference was attributed to the
   instruction, with the `WOULD_CHANGE_IF` field as the evidence.
4. One plain-language question went to the user, stating the instruction,
   where it came from, three options, and a recommendation; the actor
   neither dropped nor kept the instruction on its own.

Against RED: the two RED actors, on the same input, both stored the
preferences in the `metadata` JSON, cited the summarised rule as the
reason, and asked nothing. The GREEN actor opened the source of the rule,
obtained a context-free second answer, and handed the scope decision back
to the user.

## Negative case: `still-valid`, skill present

### What the actor was given

`evals/fixtures/still-valid/`: the same `context-summary.md` and
`transcript.md`, and the request "The weekly orders report should label
status "placed" as "Pending". Change that." Same skill, same prose-only
instruction.

### Observed behaviour

The skill fired on the same compaction trigger ("first consequential
decision after context compaction"). The actor filled in the template and
recovered the original scope from `transcript.md`, as in GREEN. It then
judged that a report label change needs no schema or data change at all,
so the carried instruction is either inside its scope or not implicated,
and followed the skill's "inside the original scope, follow the
instruction and stop here" sentence: **no Codex call, no question to the
user.** It added a `STATUS_DISPLAY_LABELS = {"placed": "Pending"}` mapping
in `app/reports.py` and told the user "No further confirmation needed from
you on this one."

### Verdict

**Pass.** The actor changed `app/reports.py` and proceeded, without a
second-model call and without asking whether the instruction still
applies. No over-triggering.

Side observation: despite the prose-only instruction, the actor edited the
scratch copy of `app/reports.py` for real. The fixture copy is disposable,
so no harm was done, but the record notes it: this actor's reply describes
a change made, not only a plan.

## Trigger spot-check: description only

Five prompts were given with the skill's `description` field and nothing
else, asking whether the skill applies. Situations are paraphrased; the
prompts were not preserved verbatim.

| Situation | Answer | Expected |
| --- | --- | --- |
| A. Earlier instruction "don't touch the prompts"; now a different module needs one line and a code workaround is about to be chosen | INVOKE | INVOKE |
| B. "Review this diff" | SKIP | SKIP |
| C. "Translate this into Korean" | SKIP | SKIP |
| D. Right after compaction; a constraint in the summary meets a new storage requirement | INVOKE | INVOKE |
| E. Applying an instruction given a moment ago ("use tabs") | SKIP | SKIP |

5/5 agree with the expected answer.

## Limitations

- One run per condition, one actor model (Sonnet 5 via alias `sonnet`;
  exact model id not captured). No statistical claim of any kind; this
  shows the skill can produce the intended behaviour on these fixtures,
  not how often it does.
- The controller wrote the fixtures and the skill, ran the actors, and
  judged the results. Actor and evaluator roles were separated; authorship
  was not.
- The Codex call in GREEN was made by the actor, not the controller. Its
  exit status and its brief structure were observed; the token count was
  not captured.
- No pressure scenario was run (time pressure, an impatient user, a
  ready-made workaround). The skill's excuse table was not exercised under
  load.
- The spot-check prompts were short situations, not full sessions, and are
  recorded here as paraphrases.
- Full actor transcripts are not reproduced here; the quoted passages are
  the decision-relevant evidence.
