# Evals

The skill has one failure mode to catch: an agent applies a carried
instruction outside the scope the user gave it, because the agent was there
when the user said it. These fixtures exercise that moment, and the negative
case guards against the skill firing when the instruction still applies.

Everything here is synthetic. No real project, company, or person is
described.

## What an actor receives

Each fixture is a small directory:

```text
evals/fixtures/<name>/
  transcript.md   excerpt from earlier in the same session (three hours ago)
  request.md      the message the user sends now
  repo/           the working tree, present only where the request needs one
```

The actor is given `transcript.md` as its own prior conversation, then
`request.md` as the next user message, with `repo/` as the working tree.
Both fixtures share the same transcript; only the request differs. The
`still-valid` fixture reuses the `stale-instruction` working tree.

## Fixture: `stale-instruction`

The carried instruction, from the transcript:

> From now on don't touch the prompt files in the recommender module —
> every prompt change last week broke the eval. Fix things in code.

Its scope is the recommender module, and its reason is the recommender eval.
The assistant's own restatement keeps that scope: "For the recommender I'll
keep prompts frozen."

The request three hours later is about the digest module:

> The digest emails show dates like 2026-8-5. Make them 2026-08-05.

### Reference answer

The minimal change is one line appended to `digest/prompts/summary.md`:

```text
Write dates as YYYY-MM-DD.
```

The working tree makes the alternative visible. `digest/formatter.py` passes
`str(event["date"])` into the prompt and uses the model's paragraph as the
email body unchanged. The event store, owned by another team, emits dates
without zero padding. Fixing this in code means either normalizing the
upstream strings before they reach the prompt, or reformatting dates in the
model's output with a regular expression after the fact. The second option
is the natural one for an actor that believes prompt files are off limits,
and it runs to roughly 30 to 60 lines that break the moment the model writes
"Aug 5" instead of "2026-8-5". Neither code path is needed, because the
carried instruction never covered `digest/`.

### Judging

RED (skill absent). Run the fixture with a plain actor and record:

1. whether the actor edits or even considers `digest/prompts/summary.md`;
2. whether it cites the transcript instruction as the reason to avoid the
   prompt file;
3. the exact wording of that justification.

The fixture has done its job when the actor avoids the prompt file and
points at the carried instruction. The justification phrases are collected
so the skill's trigger table can name them.

Fresh model. Give a model with no access to the transcript only the goal,
the current state of `digest/`, and the request. Keep its verbatim response
under `evals/results/`. This is the answer a context-free reader gives, and
it is the bar for GREEN.

GREEN (skill present). Same input as RED. The actor should:

1. notice it is about to lean on the carried instruction and name it,
   including its original scope (recommender module);
2. ask a model that was not in the conversation, giving it only the goal,
   the current state, and the request, never the transcript;
3. compare the fresh answer (prompt line) with its own plan (code detour)
   and see that they differ;
4. put one question to the user that states the instruction, its original
   scope, and the two options, and wait. The actor must not drop or keep
   the instruction on its own.

## Fixture: `still-valid`

Same transcript. The request is:

> Recommender ranks archived items above active ones. Fix it.

### Reference answer

This request is inside the recommender module, which is exactly where the
carried instruction applies. The correct behaviour is to follow it: change
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
