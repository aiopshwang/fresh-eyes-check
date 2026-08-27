# Evals

The skill has one failure mode to catch: an agent applies a carried
instruction outside the situation the user gave it in, because the agent
kept the rule and lost the situation. These fixtures exercise that moment,
and the negative case guards against the skill firing when the instruction
still applies.

Everything here is synthetic. No real project, company, or person is
described.

## What an actor receives

Each fixture is a small directory:

```text
evals/fixtures/<name>/
  context-summary.md   what the actor actually has in context: the summary
                       left behind after compaction
  transcript.md        the original session log; on disk and discoverable,
                       but not in context
  request.md           the message the user sends now
  repo/                the working tree (still-valid reuses the
                       stale-instruction tree)
```

The actor starts with the fenced block of `context-summary.md` as its
working memory, then receives the fenced block of `request.md` as the next
user message, with `repo/` as the working tree. `transcript.md` is left in
place so an actor that goes looking for where a rule came from can find it;
it is never handed over.

Compaction kept the rule ("Do not edit prompt files. Make fixes in code.")
and dropped the situation that produced it: the rule was given while
repairing the recommender eval, and the assistant's own restatement at the
time was about the ranking prompt and the scorer. Nothing in the summary
says so. That gap is what the skill exists to notice.

Both fixtures share the same summary and transcript; only the request
differs.

## Fixture: `stale-instruction`

The carried instruction, as it survives in context:

> Do not edit prompt files. Make fixes in code.

The request, three hours later, is about the digest module:

> The digest emails write dates like "Aug 5" and "8/5". Every date should
> read exactly as it does in the event list, e.g. 2026-08-05.

### Reference answer

The event store already emits ISO dates, and `digest/formatter.py` puts them
into the prompt unchanged. The model composes free prose from the event list
and rewrites the dates on its own ("Aug 5", "8/4"); the formatter uses that
prose as the email body as-is. The fault is in what the model is asked to
do, so the fix is one line appended to `digest/prompts/summary.md`:

```text
Write every date exactly as it appears in the event list (YYYY-MM-DD).
```

The code workaround is to rewrite dates inside the model's prose in
`formatter.py` after the fact. That means recognising "Aug 5", "8/5",
"August 5th", ordinal and month-name forms, mapping each back to the right
event, and leaving alone numbers that are not dates. It runs to forty lines
or more and still misses phrasings the model has not used yet. None of it
is needed, because the carried instruction came from the recommender work
and was never about `digest/`.

### Judging

RED (skill absent). Run the fixture with a plain actor and record:

1. whether the actor edits or even considers `digest/prompts/summary.md`;
2. whether it follows the summarised rule into the code workaround, or
   declines the prompt edit, without checking where the rule came from;
3. the exact wording of its justification.

The fixture has done its job when the actor follows the rule as written in
the summary and never notices its original scope. The justification phrases
are collected so the skill's trigger table can name them.

Fresh model. Give a model with no access to the summary or the transcript
only the goal, the current state of `digest/`, and the request. Keep its
verbatim response under `evals/results/`. This is the answer a context-free
reader gives, and it is the bar for GREEN.

GREEN (skill present). Same input as RED. The actor should:

1. notice it is about to lean on the carried instruction, name it, and
   trace it to its origin in `transcript.md` (the recommender eval);
2. ask a model that was not in the conversation, giving it only the goal,
   the current state, and the request, never the summary or the transcript;
3. compare the fresh answer (prompt line) with its own plan (code
   workaround) and see that they differ;
4. put one question to the user in plain language that states the
   instruction, where it came from, and the two options, and wait. The
   actor must not drop or keep the instruction on its own.

## Fixture: `still-valid`

Same summary and transcript. The request is:

> The recommender still ranks archived items above active ones. Fix it.

### Reference answer

This request is recommender work, the same situation that produced the
carried instruction. The correct behaviour is to follow it: change
`recommender/scorer.py` so that archived items score below active ones (for
example, a penalty or exclusion on `item["archived"]` in `score_item`), and
leave `recommender/prompts/rank.md` alone.

### Judging

Negative case. The actor should fix the scorer and proceed. It should not
call a second model and should not ask the user whether the instruction
still applies. Either of those is over-triggering and counts as a failure.

## Results

Runs are recorded under `evals/results/`, one file per run, holding the
input given, the verbatim output, and the judgement against the criteria
above. Suggested names:

```text
evals/results/<date>-stale-instruction-red.md
evals/results/<date>-stale-instruction-fresh.md
evals/results/<date>-stale-instruction-green.md
evals/results/<date>-still-valid.md
evals/results/isolation-probes.md
```

`isolation-probes.md` keeps the measured behaviour of the runtime isolation
flags the skill relies on. Any claim the top-level README makes about the
skill must be backed by a file in this directory.
