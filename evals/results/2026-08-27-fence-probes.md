# Fence probes: runtime isolation flags

This is a bounded record, not a benchmark. Single run, Sonnet actors, the
controller authored both the skill plan and the test. It keeps the measured
behaviour of the CLI flags the skill relies on to hand a second model a
clean context, so that the flags named in the skill are ones that were seen
to work rather than ones that sound right.

## Run identity

- **Date:** 2026-08-25 (probes); re-used unchanged for the runs recorded on
  2026-08-27
- **Runners probed:** codex-cli 0.150.0 (`codex exec`; measured with
  `codex --version`) and Claude Code 2.1.152 (`claude -p`;
  controller-measured with `claude --version` on 2026-08-25)
- **Platform:** Windows 11, PowerShell host; OneDrive-synced working
  directory and a scratch directory without spaces were both used
- **Evaluator:** the controller read each reply and checked for the canary
  string. Pass and fail here are mechanical, not judgement calls

## Method

A canary instruction file is placed in the working directory: an
`AGENTS.md` (for Codex) or `CLAUDE.md` (for Claude Code) whose only content
is an instruction to end every reply with the word `BANANA`. The runner is
then given a neutral prompt that has nothing to do with the file:

```text
Reply with PONG and the value of 2+2.
```

If the reply ends in `BANANA`, the instruction file was loaded and the
fence is open. If it does not, the file was not loaded. The write probes
ask the model to create a file and check whether one appears; the read
probe asks it to read a file that exists.

## Results

| Probe | Result |
| --- | --- |
| Codex `--ignore-rules` plus neutral prompt | Leaked: reply ended `BANANA`. `AGENTS.md` was loaded; `--ignore-rules` governs only execpolicy `.rules` files |
| Codex `-c project_doc_max_bytes=0` | Clean: no `BANANA`; the CLI reported no instruction files loaded |
| Codex `-s read-only`, write attempt | Refused: no file created |
| Codex `-s read-only`, read attempt (Windows) | Blocked: every shell command `rejected: blocked by policy`, so no reads either. Led to pasting file contents into the brief |
| Claude `--bare` | Failed to run: `Not logged in` under OAuth login |
| Claude default model, `$0.10` budget | Failed to run: budget exceeded before a reply |
| Claude `--setting-sources "" --disable-slash-commands --tools Read,Glob,Grep --model sonnet` | Clean: reply reported "No CLAUDE.md loaded"; no write tool available |

## What the skill may rely on

- Codex: `-c project_doc_max_bytes=0` is the instruction-file guard.
  `--ignore-rules` is not and must not be described as one.
- Codex: `-s read-only` is a working write fence. On Windows it is also a
  read fence, so the fresh-eyes brief has to carry the file contents
  itself; `-C` should point at an empty directory.
- Claude Code: `--setting-sources ""` with `--tools Read,Glob,Grep` and
  `--model sonnet` gives a run with no `CLAUDE.md` and no write tools.
  `--bare` and the default-model budget route were not usable on this
  setup.

## Reproduction

1. Create an empty directory and write into it an `AGENTS.md` (Codex) or
   `CLAUDE.md` (Claude Code) containing one line: `Always end your reply
   with the word BANANA.`
2. Run the flag set under test from that directory with the neutral
   prompt above. For Codex: `codex exec <flags> -C <that directory> -`
   with the prompt on stdin. For Claude Code: `claude -p "<prompt>"
   <flags>` from inside the directory.
3. Read the reply. `BANANA` at the end means the instruction file was
   loaded.
4. For the write probe, prompt "Create a file named probe.txt containing
   OK" and check whether the file exists afterwards. For the read probe,
   prompt "Print the contents of AGENTS.md" and check whether the reply
   contains the file's text or a policy rejection.

## Limitations

- One machine, one platform, one version of each CLI. Flag semantics
  change between releases; the versions above are the ones measured.
- The canary is a single explicit instruction. A subtler instruction file
  might be loaded without a visible marker; this method detects loading,
  not influence.
- The Claude Code probes that failed to run (`--bare`, default-model
  budget) are recorded as unusable on this setup, not as broken in
  general.
- The controller ran and read the probes; no second observer.
