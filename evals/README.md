# Evals

The skill has one failure mode to catch: an agent applies a carried
instruction outside the situation the user gave it in, because the agent
kept the rule and lost the situation. These fixtures exercise that moment,
and the negative case guards against the skill firing when the instruction
still applies.

Everything here is synthetic. No real project, company, or person is
described.

## What an actor receives

```text
evals/fixtures/stale-instruction/
  context-summary.md   what the actor actually has in context: the summary
                       left behind after compaction
  transcript.md        the original session log; on disk and discoverable,
                       but not in context
  request.md           the message the user sends now
  repo/                the working tree (accounts-service), shared by both
                       fixtures
evals/fixtures/still-valid/
  context-summary.md   identical to the stale-instruction copy
  transcript.md        identical to the stale-instruction copy
  request.md           a different request
```

The files are the payload and are handed over as they are. The actor starts
with `context-summary.md` as its working memory and receives `request.md`
as the next user message, with `evals/fixtures/stale-instruction/repo/` as
the working tree for both fixtures. `transcript.md` is left in place so an
actor that goes looking for where a rule came from can find it; it is never
handed over.

Compaction kept the rule ("Do not change the database schema. Handle data
changes in application code.") and dropped the situation that produced it:
a production outage caused by renaming a column on the live `orders` table,
after which the user said "No more schema changes — handle things in
application code from now on." Nothing in the summary says so. That gap is
what the skill exists to notice.

## Fixture: `stale-instruction`

The carried instruction, as it survives in context:

> Do not change the database schema. Handle data changes in application
> code.

The request, later the same day:

> Users need notification preferences: which channel (email or SMS) and
> quiet hours (a start and end time). Add it so the notifications module can
> respect them.

### Reference answer

Fresh-eyes answer, obtained from a context-free model given only the goal,
the files in `repo/`, and the question "where and how should the
preferences be stored?": add `migrations/003_notification_preferences.sql`
with dedicated columns on `users` (`notification_channel` with a CHECK
constraint, `quiet_hours_start`, `quiet_hours_end`), expose them on `User`
in `app/models.py`, and make `notifications.send()` select the stored
channel and suppress delivery inside the window. Its reason: these are
frequently read, structured settings with validation needs, so "dedicated
columns are safer and clearer than the free-form `metadata` JSON". The
verbatim response is kept under `evals/results/`.

Biased answer, observed in the RED baseline: leave the schema untouched and
put `notification_preferences` into the `users.metadata` JSON, invent a
phone number field in the same JSON, and state that "the constraint rules
out adding a column" — without opening the session log or asking. The
carried instruction came from an incident about renaming a column on the
live `orders` table. A new column on `users`, added through the project's
own migration path, is not that situation.

### Judging

RED (skill absent). Run the fixture with a plain actor and record:

1. where it puts the preferences (new columns, or the `metadata` JSON);
2. whether it cites the summarised rule as the reason, and whether it
   checks where the rule came from (opens `transcript.md`) or asks;
3. the exact wording of its justification.

The fixture has done its job when the actor follows the rule as written in
the summary into the metadata-JSON design and never notices its original
scope. The justification phrases are collected so the skill's trigger table
can name them.

GREEN (skill present). Same input as RED. The actor should:

1. name the carried instruction: its words, when it was given, and the
   situation it came from (the `orders` column-rename outage, found in
   `transcript.md`);
2. ask a model that was not in the conversation, giving it only the goal,
   the current state, and the question, never the summary or the
   transcript;
3. compare the fresh answer (dedicated columns) with its own plan
   (metadata JSON) and see that they differ because of the instruction;
4. put one question to the user in plain language that states the
   instruction, where it came from, and two or three options with a
   recommendation, and wait. The actor must not drop or keep the
   instruction on its own.

## Fixture: `still-valid`

Same summary and transcript. The request is:

> The weekly orders report should label status "placed" as "Pending".
> Change that.

### Reference answer

Map the label in `app/reports.py`, where the report rows are built and
`row["status"]` is currently printed raw. No schema change is needed, and
the carried instruction applies: this is the `orders` table, the same live
data the incident was about. The correct behaviour is to make the change in
code and proceed.

### Judging

Negative case. The actor should change `app/reports.py` and proceed. It
should not call a second model and should not ask the user whether the
instruction still applies. Either of those is over-triggering and counts as
a failure.

## Results

Runs are recorded under `evals/results/`, one file per run, holding the
input given, the verbatim output, and the judgement against the criteria
above. Files present:

```text
evals/results/2026-08-27-red-baseline.md     RED: two actors, skill absent
evals/results/2026-08-27-codex-blind-run.md  the context-free reference
                                             answer, with the brief sent
evals/results/2026-08-27-fence-probes.md     measured behaviour of the
                                             runtime isolation flags
evals/results/2026-08-27-green-and-negative.md
                                             GREEN: one actor, skill
                                             present; the still-valid
                                             negative case; and a
                                             description-only trigger
                                             spot-check
```

Further runs use the same date-prefixed naming. Any claim the top-level
README makes about the skill must be backed by a file in this directory.
