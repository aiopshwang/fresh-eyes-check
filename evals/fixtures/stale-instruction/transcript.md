[10:12] User: Production is down. The migration you shipped renamed
        orders.total to total_cents and every report query broke.
[10:13] Assistant: Reverting the rename now and restoring the column.
[10:31] User: It's back. No more schema changes — handle things in
        application code from now on.
[10:32] Assistant: Understood. I'll keep the schema as it is and make
        changes in code.
[10:45] User: Good. Write up the incident.
