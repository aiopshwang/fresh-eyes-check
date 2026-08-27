# Carried instruction

Fill this in before the fresh-eyes call. If the last line says "yes",
follow the instruction and skip the call.

```text
Words:                        "<verbatim, as the user said it>"
When:                         <timestamp or turn; relative time if that
                              is all you have>
Original situation and scope: <what was happening when it was said, and
                              what the words were about>
Where it lives now:           session | memory rule <file> | CLAUDE.md
                              or AGENTS.md
Current situation:            <what you are deciding now, one sentence>
Inside original scope?        yes -> follow it and stop
                              no  -> run the check
```

If "Original situation and scope" is blank because you only have a
compaction summary, that blank is the finding: the words survived and the
situation did not. Open the session log or the memory file the words came
from before you answer the last line. If the source is gone (a memory rule
without its how-to-apply, a rotated log), treat the scope as unknown and
run the check.

Worked example, from the `stale-instruction` fixture:

```text
Words:                        "No more schema changes — handle things in
                              application code from now on."
When:                         10:31 today, six hours ago
Original situation and scope: production outage after a migration renamed
                              a column on the live orders table; schema
                              changes on live, populated tables
Where it lives now:           session (compaction summary: "Do not change
                              the database schema")
Current situation:            store notification preferences for users
Inside original scope?        no -> run the check
```
