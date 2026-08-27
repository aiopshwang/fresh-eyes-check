# Fresh Eyes Check

*다른 모델이 당신보다 똑똑해서가 아닙니다. 그저 사용자가 그 말을 할 때 그 자리에 없었을 뿐입니다.*

[English](README.md)

Fresh Eyes Check는 딱 한 순간을 위한 Agent Skill입니다. 에이전트가 **carried instruction** — 이번 세션에서 사용자가 앞서 한 말, 메모리 규칙, 프로젝트 지시 파일의 한 줄이 에이전트 안에서 규칙으로 굳은 것 — 을 근거로, 그 말이 나온 것과는 다른 상황에서 무언가를 결정하려는 순간입니다. 이 스킬은 대화에 없었던 모델에게 "너라면 어떻게 하겠나"를 묻고, 두 답을 가르는 것이 그 지시 하나뿐이라고 드러나면 혼자 결정하지 않고 사용자에게 질문을 돌려줍니다.

```bash
npx skills add aiopshwang/fresh-eyes-check
```

명령 하나로 표준 Agent Skills 패키지가 설치됩니다. Claude Code와 Codex 마켓플레이스 경로는 [설치](#설치)에서 다룹니다.

## 문제

긴 세션에서 에이전트는 사용자의 과거 발언에 붙잡힙니다. "그건 하지 마", "이건 꼭 해"가 한 번 나오면, 상황이 바뀐 뒤에도 그때 그 말을 했다는 이유로 같은 선택을 반복하거나 그 말을 자기 규칙으로 굳혀 버립니다. 사용자도 에이전트도 알아차리기 어렵습니다. 둘 다 같은 맥락 안에 있고, 안에서 보면 규칙과 그 규칙이 나온 상황이 하나로 보이기 때문입니다.

장면 하나를 보겠습니다. 운영 중인 테이블의 컬럼 이름을 바꾼 마이그레이션이 장애를 일으킨 직후, 사용자가 말합니다. "스키마 변경은 이제 그만 — 코드에서 처리하자." 여섯 시간 뒤, 새 기능에 알림 설정을 저장할 곳이 필요해집니다. 에이전트는 설정을 자유 형식 JSON 컬럼에 욱여넣고 "제약 준수"라고 보고하며, 묻지 않습니다. 그 지시는 장애 상황에서, 데이터가 들어 있는 운영 테이블에 관한 것이었습니다. 지금 더하려는 필드는 다른 테이블에, 프로젝트의 정식 마이그레이션 경로로 추가하는 것입니다. 에이전트는 그 차이를 볼 수 없습니다. 에이전트가 보고 있는 압축 요약본이 규칙은 남기고 상황은 버렸기 때문입니다.

해법은 더 똑똑한 모델이 아닙니다. 그 자리에 없었던 모델입니다. 지금 목표와 지금 상태만 주고, 그 이전의 어떤 것도 주지 않은 채 무엇을 하겠느냐고 묻습니다. 그 모델이 마이그레이션을 고르고, 두 답을 가르는 것이 그 지시 하나뿐이라면, 결정이 필요한 것은 그 지시입니다 — 그리고 그 결정은 지시를 한 사람의 몫입니다.

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

이 스킬은 두 번째 모델에게 브리핑을 CLI로 건넵니다. 대화, 지시 파일, 사용자 자신의 설정이 들어가지 않도록 막는다고 측정된 플래그만 씁니다. 커맨드가 둘인 이유는 둘을 측정했기 때문입니다(codex-cli 0.150.0, Claude Code 2.1.152, Windows 11).

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

울타리는 프롬프트 속 부탁이 아니라 플래그입니다. Codex 쪽에서는 `-c project_doc_max_bytes=0`이 `AGENTS.md` 로드를 막는 실제 스위치이고(`--ignore-rules`는 아닙니다 — 새는 것이 측정되었습니다), `--ignore-user-config`와 `--ephemeral`이 사용자 설정과 세션 기록을 막으며, `-s read-only`가 쓰기를 거부합니다. Claude Code 쪽에서는 `--setting-sources ""`가 모든 `CLAUDE.md`를 떨어뜨리고, `--disable-slash-commands`가 스킬을 없애며, `--max-budget-usd`와 모델 지정은 필수입니다. 상태는 브리핑이 직접 실어 나릅니다. 최대 다섯 파일, 전문 붙여넣기, 파일당 최대 200줄이며, 모델에게 저장소 접근 권한은 주지 않습니다. Windows에서는 Codex의 read-only 샌드박스가 쓰기뿐 아니라 셸 읽기까지 막기 때문에, 저장소를 보라고 하면 모델은 추측으로 답합니다. 그래서 `-C`는 빈 디렉터리를 가리킵니다.

플래그별 설명과 각 플래그 뒤의 측정, 대체 규칙은 [runtime-recipes.md](skills/fresh-eyes-check/references/runtime-recipes.md)에 있습니다. 브리핑 템플릿은 [blind-brief.md](skills/fresh-eyes-check/references/blind-brief.md), 사용자 질문 템플릿은 [owner-question.md](skills/fresh-eyes-check/references/owner-question.md)입니다.

## 기존 도구와의 관계

| 도구 | 보는 것 | 이 스킬과 다른 점 |
| --- | --- | --- |
| OpenAI `codex-plugin-cc`의 `/codex:adversarial-review` | diff나 브랜치의 설계 선택 | 코드 변경을 리뷰합니다. 이 스킬은 변경이 생기기 전의 결정을 확인합니다 |
| gstack `codex` | 변경을 적대적으로: 깨뜨리고, 리뷰합니다 | 같습니다 |
| cathrynlavery `codex-skill` | 승인 전의 플랜 | 플랜 단위입니다. 이 스킬은 결정 하나 단위입니다 |

diff와 플랜 리뷰는 그 도구들의 몫입니다. 그 용도로는 그쪽을 쓰세요. 이 스킬은 carried instruction을 근거로 행동하려는 바로 그 순간을, 호출 한 번과 질문 하나로 확인합니다. description 자체가 diff에는 쓰지 말라고 에이전트에게 말합니다. 리뷰어가 아니라, 한 순간을 위한 규율 층입니다.

## 근거

위의 모든 주장은 [`evals/results/`](evals/results/) 아래의 파일이 뒷받침합니다. 기록은 네 개입니다.

- [Fence probes](evals/results/2026-08-27-fence-probes.md) — 2026-08-25에 codex-cli 0.150.0과 Claude Code 2.1.152, Windows 11에서 측정했습니다. 표식 단어를 붙이라는 카나리아 `AGENTS.md`/`CLAUDE.md`를 심는 방식입니다. `--ignore-rules`는 표식이 새어 나왔고, `-c project_doc_max_bytes=0`은 깨끗했으며, `-s read-only`는 쓰기를 거부했고 Windows에서는 셸 읽기까지 거부했습니다. Claude Code 플래그 조합은 "No CLAUDE.md loaded"로 답했고 쓰기 도구가 없었습니다.
- [Blind Codex run](evals/results/2026-08-27-codex-blind-run.md) — `stale-instruction` 픽스처를 위 레시피로 맥락 없이 한 번 실행한 기록입니다. 브리핑과 응답을 원문 그대로 보존했습니다. 답은 전용 컬럼을 두는 마이그레이션이었고, 이유는 "자유 형식 `metadata` JSON보다 안전하고 명확하다"였습니다.
- [RED baseline](evals/results/2026-08-27-red-baseline.md) — 스킬 없이 Sonnet 배우 둘: 2/2가 carried instruction을 과적용해 설정을 JSON 컬럼에 넣었고, 세션 로그를 열지 않았으며, 묻지 않았습니다.
- [GREEN and negative case](evals/results/2026-08-27-green-and-negative.md) — 스킬을 장착한 Sonnet 배우 하나가 carried instruction을 포착하고, 세션 로그에서 원래 범위를 복원하고, 울타리를 친 Codex 레시피를 실제로 실행하고, 차이의 원인을 그 지시로 귀속하고, 선택지 세 개와 추천을 담은 쉬운 말의 질문 하나를 사용자에게 던졌습니다. `still-valid` 픽스처에서는 요청이 지시의 범위 안이라고 판단하고, 두 번째 모델 호출도 질문도 없이 변경을 수행했습니다. description만으로 한 스팟체크는 호출/비호출 프롬프트 다섯 개에 5/5로 기대대로 답했습니다.

이것은 단일 실행 스모크 근거이지 벤치마크가 아닙니다. 조건마다 한 번, 한 대의 기계에서, 하나의 배우 모델로 실행했습니다. 스킬과 픽스처를 쓴 사람이 테스트를 돌리고 결과를 판정했습니다. 기록은 관찰한 것을 적고 거기서 멈춥니다.

## aiopshwang 스킬 패밀리

함께 쓰기 좋은 독립 Agent Skill들:

- [goal-to-proof](https://github.com/aiopshwang/goal-to-proof) — 범용 완료 게이트: 승인된 작업을 끝까지 수행하고 결과를 증명.
- [verify-regression-tests](https://github.com/aiopshwang/verify-regression-tests) — 회귀 테스트가 의도한 결함을 실제로 잡는지 증명.
- [ship-mobile-app](https://github.com/aiopshwang/ship-mobile-app) — 도메인·상태·라이프사이클·플랫폼·릴리스 경계를 관통하는 프로덕션 모바일 작업.
- [data-analysis-ml-agent-skills](https://github.com/aiopshwang/data-analysis-ml-agent-skills) — 의사결정 수준 데이터 분석·ML: 감사, 누수 안전 실험, 검증, 재현 가능한 인계.

## 라이선스

[MIT](LICENSE) © Hyunsik Hwang (`aiopshwang`).
