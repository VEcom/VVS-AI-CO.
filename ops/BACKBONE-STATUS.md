# 백본 연결 현황 — 조직도 v4 (검증 완료)

> 생성: 2026-05-30 · 브랜치 `claude/vvs-hermes-rebuild-KHOJ9`
> 4/4 백본 라이브 호출 성공. 작성≠채점 계열분리 코드 강제.

## 조직도 v4 대비 백본 현황표

| 역할 | 조직도 백본 | .env 모델 ID | provider | 모델명 검증 | 라이브 호출 |
|------|-------------|--------------|----------|-------------|-------------|
| AI PM (총괄/Graduation) | Claude Opus 4.8 | claude-opus-4-8 | Anthropic | ✅ 정확 | ✅ OK |
| 작성 Core | Claude Opus 4.8 | claude-opus-4-8 | Anthropic | ✅ 정확 | ✅ (AI PM과 동일) |
| 작성 기본 (L1/L2) | Claude Sonnet 4.6 | claude-sonnet-4-6 | Anthropic | ✅ 정확 | ✅ OK |
| 작성 L4 (1페이지) | Claude Haiku 4.5 | claude-haiku-4-5-20251001 | Anthropic | △ 교정(날짜suffix) | ✅ (계열 동일) |
| 페르소나 | Claude Sonnet 4.6 | claude-sonnet-4-6 | Anthropic | ✅ 정확 | ✅ (계열 동일) |
| 채점 (Scoring, 독립) ★ | GPT-5.5 | gpt-5.5 | OpenAI | ✅ 정확 | ✅ OK |
| 디자인 검수 | Gemini 3.1 Pro | gemini-3.1-pro-preview | Google | △ 교정(배포명) | ✅ OK |

> 모델명 교정 2건: 역할 배치는 유지하고 호출 가능한 정확한 문자열로만 교정.
> - claude-haiku-4-5 → claude-haiku-4-5-20251001 (Anthropic 실제 ID는 날짜 포함)
> - gemini-3.1-pro → gemini-3.1-pro-preview (Google 실제 배포명)

## ★ 작성≠채점 독립성 (편향 방지)

- 작성 계열 = **Claude(Anthropic)** 전부 (AI PM·Core·L1/L2·L4·페르소나)
- 채점 계열 = **GPT(OpenAI)** — 다른 provider → **독립 확보**
- `ai_pm/backbone.py::assert_writer_scorer_separation`: 작성 계열이 채점도
  맡으면 `BackboneSeparationError` 차단 (코드 강제).
- `separation_ok()` = True. 단위 테스트로 "같은 계열 채점 시 차단" 검증.
- → B-3 빈페이지 91점류 편향 재발 방지 장치 코드화.

## API 키 연결 상태

| provider | 키 | 연결 |
|----------|-----|------|
| Anthropic | ANTHROPIC_API_KEY | ✅ SET (라이브 호출 성공) |
| OpenAI | OPENAI_API_KEY | ✅ SET (라이브 호출 성공) |
| Google | GEMINI_API_KEY | ✅ SET (빌링 회복 후 호출 성공) |

- 키는 `.env`(gitignore 차단, 미추적). 값 출력/커밋 없음.
- 헤르메스는 멀티 provider 구조이며, 본 레이어는 stdlib urllib 어댑터로
  3개 provider 직접 호출(SDK 불필요).

## 라이브 호출 결과 (최종)

```
[aipm   ] anthropic claude-opus-4-8          OK
[writer ] anthropic claude-sonnet-4-6        OK
[scoring] openai    gpt-5.5                  OK
[design ] google    gemini-3.1-pro-preview   OK
성공 4/4 · 비용 누적 token_cost_monitor 기록
```

## 검수 체크리스트

| 항목 | 상태 |
|------|------|
| AI PM = claude-opus-4-8 (GPT-5.5→Opus 변경 반영) | ✅ |
| 3개 키 .env 연결 (커밋 X, 미추적) | ✅ |
| .gitignore 에 .env (커밋 차단) | ✅ |
| 모델명 실제 호출 가능 (2건 교정) | ✅ |
| 4개 백본 호출 성공 (4/4) | ✅ |
| 작성=Claude / 채점=GPT 분리 (코드+테스트) | ✅ |
| 절대선 게이트 회귀 0 (126 passed) | ✅ |

## 다음 (B-4)
- 학습 루프: persona_generator 궤적 + trajectory_gate 환각 제외 +
  채점(GPT 독립) + 디자인(Gemini) + vision_review 실연결 + Graduation(AI PM=Opus).
- ⚠️ 보안: 대화 노출 키 3개 rotate 권장(특히 OpenAI).
