# Runtime recipes

Only flags that were measured to work are listed. The measurements are in
[2026-08-27-fence-probes.md](../../../evals/results/2026-08-27-fence-probes.md);
the run that used the Codex recipe end to end is in
[2026-08-27-codex-blind-run.md](../../../evals/results/2026-08-27-codex-blind-run.md).
Versions probed: codex-cli 0.150.0 and Claude Code 2.1.152 on Windows 11.
Flag semantics move between releases; re-run the probe in that file before
trusting a newer version.

Write the brief from [blind-brief.md](blind-brief.md) to a file first. Both
recipes read it from stdin, so the shell never has to quote it.

## Claude Code asks Codex

```text
codex exec -s read-only --ignore-user-config --ephemeral \
  -c project_doc_max_bytes=0 --skip-git-repo-check \
  -C <any empty dir> -o <out.md> - < brief.txt
```

| Flag | What it does |
| --- | --- |
| `-s read-only` | The sandbox refuses writes. On Windows it refuses shell reads as well, which is why the brief carries the files |
| `--ignore-user-config` | `$CODEX_HOME/config.toml` is not loaded: no user settings, no user skills |
| `--ephemeral` | No session record is kept |
| `-c project_doc_max_bytes=0` | The switch that stops `AGENTS.md` from loading. Without it the canary file was loaded |
| `--skip-git-repo-check` | Lets the run start in a directory that is not a repository |
| `-C <any empty dir>` | Nothing to find, even if the model looks |
| `-o <out.md>` | The final message goes to a file you can parse |
| `-` | The brief comes from stdin |

`--ignore-rules` is not an instruction-file switch. It governs execpolicy
`.rules` files only. In the probe, `--ignore-rules` without
`project_doc_max_bytes=0` still loaded the `AGENTS.md` canary. Do not
describe it as blocking `AGENTS.md`.

## Codex asks Claude Code

This is also the fallback when the other model family is not installed.

```text
claude -p --setting-sources "" --disable-slash-commands \
  --tools "Read,Glob,Grep" --no-session-persistence \
  --max-budget-usd <n> --model <model> < brief.txt
```

| Flag | What it does |
| --- | --- |
| `--setting-sources ""` | No user, project, or local settings, so no `CLAUDE.md`. The probe reply said "No CLAUDE.md loaded" |
| `--disable-slash-commands` | No skills |
| `--tools "Read,Glob,Grep"` | Read tools only; no write tool exists in the run. The brief still carries the files; the tools are a backstop, not the channel |
| `--no-session-persistence` | No session record is kept |
| `--max-budget-usd <n>` | Required. The default model under a `$0.10` cap stopped before replying, on system-prompt cost alone |
| `--model <model>` | Name a smaller model; `sonnet` was measured |

`--bare` needs an API key and fails under OAuth login ("Not logged in"). It
is an option for API-key environments, not part of the recipe.

## When the other family is not available

Run the recipe for your own family from a new process with the same brief.
Label the result "same-family check" in the log and in any report that
cites it. The bias this check targets lives in the conversation, not in the
model family, so a session with no conversation is still a check; it is a
weaker one because the two runs share training and habits.

The same session asking itself is not a fallback.

## Cost guard

- One call per decision. Do not re-ask to close an information gap; note
  the fact and proceed.
- At most five files in the brief, at most 200 lines each.
- Always pass `--max-budget-usd` to Claude Code and name a model.
- Expect zero to three calls in a normal session. More than that means the
  trigger is firing on decisions that do not change outcome, scope, risk,
  or cost.
