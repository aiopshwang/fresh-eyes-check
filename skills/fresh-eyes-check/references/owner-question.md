# Owner question

The carried instruction is the user's. When the fresh-eyes reply shows that
the instruction, and not a missing fact, caused the difference, put one
question to the user. Then record the answer as a scope.

## Form

- Tell it as a short story: when they said it, what it was about, what has
  come up now, and what applying it here would cost.
- No file paths, function names, or flag names. The user is deciding about
  their own words, not about code.
- Two or three options, numbered. Include "apply" and "exception this
  time"; add "retire the instruction" when that is a real option.
- One recommendation with one sentence of reason. The reason names the
  difference between then and now.
- Ask once and wait. Do not act on the decision in the meantime.

## Example (English)

> Six hours ago, after the outage, you said "no more schema changes —
> handle things in application code". The new notification preferences
> would fit best as two new columns via a migration; keeping them in the
> metadata JSON works but loses validation and clean queries. Apply that
> instruction here too?
> ① Apply (store in metadata JSON)
> ② Exception this time (one migration, two columns)
> ③ Retire the instruction
> — recommendation ②: the outage was about renaming a column on the live
> orders table; this adds new columns on users.

## Example (Korean)

> 여섯 시간 전 장애 직후에 "스키마 변경은 이제 그만, 애플리케이션 코드에서
> 처리하자"고 하셨습니다. 이번 알림 설정은 마이그레이션으로 컬럼 두 개를 새로
> 두는 쪽이 가장 잘 맞고, metadata JSON에 넣어도 동작은 하지만 검증과 깔끔한
> 조회를 잃습니다. 그 지시를 여기에도 적용할까요?
> ① 적용 (metadata JSON에 저장)
> ② 이번만 예외 (마이그레이션 하나, 컬럼 두 개)
> ③ 그 지시는 앞으로 폐기
> — 추천 ②: 그때 장애는 운영 중인 orders 테이블의 컬럼 이름을 바꿔서 난
> 것이고, 이번 건은 users에 새 컬럼을 더하는 것입니다.

## Recording the answer

Write the resolution next to where the instruction lives: the memory rule
it came from, the project instruction file, or, for a session-only
instruction, the session log or the report. The format:

```text
carried instruction: "<verbatim>" (said <when>, about <original scope>)
resolution <date>: applies to <scope>; exception for <scope>; [retired]
```

For the example above, answered ②:

```text
carried instruction: "No more schema changes — handle things in
application code from now on." (said 2026-08-27 10:31, about the
orders column-rename outage)
resolution 2026-08-27: applies to changes on live, populated tables;
exception for additive columns on users through a numbered migration
```

In a memory file the same record goes under the rule it narrows, so the
next session reads the scope together with the rule:

```markdown
## Schema changes go through application code

**How to apply:** changes on live, populated tables, especially orders.
Additive columns through a numbered migration are an agreed exception
(2026-08-27, notification preferences).
```

Do not ask again for the same instruction and the same kind of situation.
The record is what you consult next time; the question was asked once.
