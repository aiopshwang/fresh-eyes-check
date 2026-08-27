# Notification service

Builds daily digest emails from events.

Modules:

- `recommender/` (ranking prompt + scorer): picks and orders the items that
  go into a user's feed. The ranking eval runs in CI on every change.
- `digest/` (summary prompt + formatter): the formatter puts the day's event
  list into the digest prompt; the model composes the email body as free
  prose, and the formatter sends that prose as-is.

Layout:

```text
recommender/
  prompts/rank.md      ranking prompt
  scorer.py            candidate scoring and ordering
digest/
  prompts/summary.md   digest prompt
  events.py            upstream event fetch
  formatter.py         prompt assembly and email body
```
