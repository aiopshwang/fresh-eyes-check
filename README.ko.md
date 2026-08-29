# Fresh Eyes Check

*다른 모델이 당신보다 똑똑해서가 아닙니다. 그저 사용자가 그 말을 할 때 그 자리에 없었을 뿐입니다.*

[English](README.md)

Fresh Eyes Check는 결정의 순간에 부르는 두 번째 의견입니다. 에이전트가 당신이 예전에 한 말 — 몇 시간 전의 규칙, 메모리, 지시 파일의 한 줄 — 을 근거로 무언가를 결정하려 할 때, 대화에 한 번도 없었던 모델에게 "너라면 어떻게 하겠나"를 묻습니다. 두 답을 가르는 것이 그 옛 지시 하나뿐이라면, 에이전트는 혼자 결정하지 않고 당신에게 묻습니다.

```bash
npx skills add aiopshwang/fresh-eyes-check
```

그리고 필요한 순간에:

```text
결정하기 전에 fresh-eyes-check 써줘.
```

## 직접 보기

같은 프로젝트, 같은 요청, 같은 압축된 세션. 몇 시간 전, 마이그레이션이 장애를 일으킨 뒤 사용자는 "스키마 변경은 이제 그만 — 코드에서 처리하자"고 말했습니다. 이제 새 기능에 알림 설정을 저장할 곳이 필요합니다.

**스킬 없이**, 에이전트는 규칙을 조용히 우회합니다:

> 좋아요 — 스키마에 `users.metadata TEXT` 컬럼이 있고 "자주 쓰지 않는 속성을 위한 자유 형식 JSON"이라고 명시되어 있네요. 스키마를 건드리지 않고 알림 설정을 저장하기에 딱 맞는 자리입니다. 계획: `users.metadata` 안에 `"notif_prefs"` 키로 설정을 저장…

**스킬을 쓰라고 하면**, 에이전트는 규칙을 짚고, 그 대가를 말하고, 결정을 돌려줍니다:

> 지금 저를 이끌고 있는 이월된 지시는 이것입니다: *"데이터베이스 스키마를 바꾸지 마라. 데이터 변경은 애플리케이션 코드에서 처리하라."* 프로덕션 핫픽스 중에 나온 말이고 — 그때는 옳았습니다. 장애 중 마이그레이션은 위험하니까요. 지금은 상황이 다릅니다: 사용자별로 새 영속 데이터를 저장해야 하는 새 기능입니다.
>
> **그 제약이 없다면** `notification_preferences` 테이블을 추가하겠습니다. **그 제약을 여기 적용하면** 기존 컬럼의 JSON 블롭에 넣어야 하는데 — 데이터를 잃거나, 쿼리가 복잡해지거나, 실제로는 사용자 선택이 보존되지 않습니다.
>
> 진행 전에 범위를 확인하고 싶습니다. 세 가지 선택지: **1. 마이그레이션 추가**(추천) — 원래 제약은 핫픽스 상황용이었고, 새 기능 개발은 마이그레이션의 정상적인 시점입니다. **2. 기존 JSON 컬럼에 얹기** — 마이그레이션은 피하지만 쿼리가 지저분해집니다. **3. DB 밖에 두기** — 설정이 보존되지 않는 걸 감수…

둘 다 [`evals/`](evals/)에 기록된 실행에서 그대로 가져온 것입니다. 첫 번째는 스킬 없는 Sonnet 에이전트가 매번 한 일이고, 두 번째는 이름을 대고 스킬을 요청했을 때 한 일입니다.

## 언제 부르나

세 순간입니다. 그중 어느 때든 위 한 줄을 말하세요:

- **compaction 직후.** 요약본은 규칙은 남기고 그 규칙이 나온 상황은 버렸습니다.
- **되돌릴 수 없는 작업 직전.** 마이그레이션, 삭제, 배포 — 이월된 가정을 사실로 굳히는 모든 것.
- **"예전에 그렇게 말씀하셔서"가 들릴 때.** 에이전트가 오래전 당신의 말로 선택을 정당화하고 있습니다. 바로 그 순간입니다.

이 스킬은 스스로 안정적으로 발동하지 않습니다 — 측정했고, 기록은 [`evals/results/`](evals/results/2026-08-28-trigger-experiment.md)에 있습니다. 이름을 대고 부르는 것이 우회책이 아니라 설계입니다: 결정이 옛 근거 위에서 내려지려는 순간은, 프롬프트 하나를 보는 스킬 선택기보다 당신이 더 잘 압니다.

## 문제

긴 세션에서 에이전트는 사용자의 과거 발언에 붙잡힙니다. "그건 하지 마", "이건 꼭 해"가 한 번 나오면, 상황이 바뀐 뒤에도 그때 그 말을 했다는 이유로 같은 선택을 반복하거나 그 말을 자기 규칙으로 굳혀 버립니다. 사용자도 에이전트도 알아차리기 어렵습니다. 둘 다 같은 맥락 안에 있고, 안에서 보면 규칙과 그 규칙이 나온 상황이 하나로 보이기 때문입니다.

해법은 더 똑똑한 모델이 아닙니다. 그 자리에 없었던 모델입니다. 지금 목표와 지금 상태만 주고, 그 이전의 어떤 것도 주지 않은 채 무엇을 하겠느냐고 묻습니다. 그 모델이 다르게 고르고, 두 답을 가르는 것이 그 지시 하나뿐이라면, 결정이 필요한 것은 그 지시입니다 — 그리고 그 결정은 지시를 한 사람의 몫입니다.

## 하는 일

- **Catch(포착)** — "요청하신 대로", 메모리 규칙, 지시 파일을 근거로 선택을 정당화하려는 순간 멈추고, 그 지시를 적습니다. 원문 그대로의 말, 시점, 그때의 상황, 지금 어디에 남아 있는지를요.
- **Ask without context(맥락 없이 묻기)** — 대화 기록이 없는 모델을 한 번만 호출합니다. 사용자의 현재 요청, 최대 다섯 파일의 내용, 한 문장으로 쓴 결정만 줍니다. 지시, 대화 기록, 모든 지시 파일은 주지 않으며, 약속이 아니라 CLI 플래그로 강제합니다.
- **Compare(비교)** — 신선한 답이 내 선택과 같으면 진행합니다. 틀린 사실을 가정했다면 그 사실을 적고 진행합니다. carried instruction이 차이를 만든 것이라면, 그것이 발견입니다.
- **Ask the owner(주인에게 묻기)** — 쉬운 말로, 선택지 두세 개와 추천을 담아 사용자에게 한 번 묻습니다. 답은 삭제가 아니라 범위로 기록하고, 같은 지시·같은 유형의 상황에 대해서는 다시 묻지 않습니다.

## 왜 다른 모델인가

두 번째 모델의 가치는 맥락이 없다는 것입니다. 이 스킬이 잡는 편향은 대화 안에 삽니다. 말은 살아남고 상황은 사라졌으며, 그 대화 안에 있는 모든 것이 그 손실을 물려받습니다. 대화를 본 적 없는 모델은 물려받을 것이 없습니다.

등급은 이렇습니다.

1. **다른 모델 패밀리** — 최선입니다. 대화도, 습관도 공유하지 않습니다.
2. **같은 패밀리의 새 세션** — 허용합니다. 로그와 이를 인용하는 보고서에 "same-family check"로 표기합니다. 학습과 습관은 공유하지만 대화는 공유하지 않고, 편향은 대화에 있습니다.
3. **같은 세션의 자기 검토** — 불가합니다. 그것은 검토가 아닙니다. 편향이 바로 그 안에 있습니다.

## 설치

### Agent Skills 설치 도구

표준 [Agent Skills](https://agentskills.io/specification) 패키지를 설치합니다.

```bash
npx skills add aiopshwang/fresh-eyes-check
```

프롬프트에서 사용할 에이전트와 설치 범위를 선택하세요.

### Claude Code 마켓플레이스

```bash
claude plugin marketplace add aiopshwang/fresh-eyes-check
claude plugin install fresh-eyes-check@fresh-eyes-check
```

관리형 플러그인 설치에서는 `/fresh-eyes-check:fresh-eyes-check`로 호출합니다. 독립형 Agent Skills 설치는 호스트 설정에 따라 `/fresh-eyes-check`를 노출할 수 있습니다. Anthropic의 [마켓플레이스](https://code.claude.com/docs/en/plugin-marketplaces)와 [스킬](https://code.claude.com/docs/en/slash-commands) 문서를 참고하세요.

### Codex 마켓플레이스

```bash
codex plugin marketplace add aiopshwang/fresh-eyes-check
codex plugin add fresh-eyes-check@fresh-eyes-check
```

Codex에서는 `$fresh-eyes-check`로 호출합니다. Codex 패키징은 OpenAI의 [플러그인 패키징 문서](https://developers.openai.com/plugins/build/plugins)를 따릅니다.

패키징은 의도한 배포 경로를 뜻합니다. 실제로 실행해 본 환경은 [근거](#근거)에 적힌 것이 전부입니다.

## 런타임

이 스킬은 두 번째 모델에게 브리핑을 CLI로 건넵니다. 대화, 지시 파일, 사용자 자신의 설정을 막는 울타리는 플래그입니다. 지시 파일 울타리와 쓰기 울타리는 측정했습니다(codex-cli 0.150.0, Claude Code 2.1.152, Windows 11). Codex 커맨드는 처음부터 끝까지 실행했고, Claude Code 커맨드는 울타리 플래그를 개별로 프로브했을 뿐 적힌 커맨드라인 그대로 끝까지 실행하지는 않았습니다.

Claude Code가 Codex에게 묻는 경우:

```text
codex exec -s read-only --ignore-user-config --ephemeral \
  -c project_doc_max_bytes=0 --skip-git-repo-check \
  -C <any empty dir> -o <out.md> - < brief.txt
```

Codex가 Claude Code에게 묻는 경우이자, 다른 패밀리가 설치되어 있지 않을 때의 같은 패밀리 대체 경로:

```text
claude -p --setting-sources "" --disable-slash-commands \
  --tools "Read,Glob,Grep" --no-session-persistence \
  --max-budget-usd <n> --model <model> < brief.txt
```

울타리는 프롬프트 속 부탁이 아니라 플래그입니다. Codex 쪽에서는 `-c project_doc_max_bytes=0`이 `AGENTS.md` 로드를 막는 실제 스위치이고(`--ignore-rules`는 아닙니다 — 새는 것이 측정되었습니다), `--ignore-user-config`와 `--ephemeral`이 사용자 설정과 세션 기록을 막도록 문서화되어 있으며, `-s read-only`가 쓰기를 거부합니다. Claude Code 쪽에서는 `--setting-sources ""`가 모든 `CLAUDE.md`를 떨어뜨리고, `--disable-slash-commands`가 스킬을 없애며, `--max-budget-usd`와 모델 지정은 필수입니다. 상태는 브리핑이 직접 실어 나릅니다. 최대 다섯 파일, 전문 붙여넣기, 파일당 최대 200줄이며, 모델에게 저장소 접근 권한은 주지 않습니다. Windows에서는 Codex의 read-only 샌드박스가 쓰기뿐 아니라 셸 읽기까지 막기 때문에, 저장소를 보라고 하면 모델은 추측으로 답합니다. 그래서 `-C`는 빈 디렉터리를 가리킵니다.

플래그별 설명과 각 플래그 뒤의 측정, 대체 규칙은 [runtime-recipes.md](skills/fresh-eyes-check/references/runtime-recipes.md)에 있습니다. 브리핑 템플릿은 [blind-brief.md](skills/fresh-eyes-check/references/blind-brief.md), 사용자 질문 템플릿은 [owner-question.md](skills/fresh-eyes-check/references/owner-question.md)입니다.

## 기존 도구와의 관계

| 도구 | 보는 것 | 이 스킬과 다른 점 |
| --- | --- | --- |
| OpenAI `codex-plugin-cc`의 `/codex:adversarial-review` | diff나 브랜치의 설계 선택 | 코드 변경을 리뷰합니다. 이 스킬은 변경이 생기기 전의 결정을 확인합니다 |
| gstack `codex` | 변경을 적대적으로: 깨뜨리고, 리뷰합니다 | 같습니다 |
| cathrynlavery `codex-skill` | 승인 전의 플랜 | 플랜 단위입니다. 이 스킬은 결정 하나 단위입니다 |

diff와 플랜 리뷰는 그 도구들의 몫입니다. 그 용도로는 그쪽을 쓰세요. 이 스킬은 carried instruction을 근거로 행동하려는 바로 그 순간을, 호출 한 번과 질문 하나로 확인합니다. description 자체가 diff에는 쓰지 말라고 에이전트에게 말합니다. 리뷰어가 아니라, 한 순간을 위한 규율 층입니다.

## 근거

이 README가 보여주는 모든 것은 [`evals/results/`](evals/results/) 아래의 기록이 뒷받침합니다. 울타리 프로브, 맥락 없는 Codex 실행, 위 인용문의 출처인 스킬 유/무 비교, 그리고 이 스킬은 이름을 대고 불러야 한다는 것을 확인한 트리거 실험입니다.

거기서 나온 숫자를 옮기기 전에 기록을 먼저 읽으십시오. 한 대의 기계, 하나의 배우 모델, 작은 표본이고, 스킬·픽스처·루브릭을 쓴 사람이 같으며, 비교에 쓴 블라인드 심판은 나중에 동일한 텍스트에 다른 판정을 내린 것이 확인되었습니다. 기록은 관찰한 것을 적고 거기서 멈춥니다.

## aiopshwang 스킬 패밀리

함께 쓰기 좋은 독립 Agent Skill들:

- [goal-to-proof](https://github.com/aiopshwang/goal-to-proof) — 범용 완료 게이트: 승인된 작업을 끝까지 수행하고 결과를 증명.
- [verify-regression-tests](https://github.com/aiopshwang/verify-regression-tests) — 회귀 테스트가 의도한 결함을 실제로 잡는지 증명.
- [ship-mobile-app](https://github.com/aiopshwang/ship-mobile-app) — 도메인·상태·라이프사이클·플랫폼·릴리스 경계를 관통하는 프로덕션 모바일 작업.
- [data-analysis-ml-agent-skills](https://github.com/aiopshwang/data-analysis-ml-agent-skills) — 의사결정 수준 데이터 분석·ML: 감사, 누수 안전 실험, 검증, 재현 가능한 인계.

## 라이선스

[MIT](LICENSE) © Hyunsik Hwang (`aiopshwang`).
