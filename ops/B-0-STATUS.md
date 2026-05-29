# B-0 착수 현황

> 생성: 2026-05-29 · 갱신: 2026-05-29 (2차) · 브랜치 `claude/vvs-hermes-rebuild-KHOJ9`

## 사전 확인 결과

| 항목 | 결과 | 비고 |
|------|------|------|
| betplay-mvp / vvs-handoff 읽기 | ❌ **불가** | 외부 GitHub 인증 불가 + 로컬 프록시에 해당 repo 없음. |
| VVS-AI-CO push | ✅ **가능** | remote 도달, 푸시·remote ref 검증 완료. 영구 보존 충족. |
| 외부 GitHub 일반 접근 | ⚠️ **제한적** | curl HTTP 200·`ls-remote` refs는 되지만, full `git clone`(pack fetch)은 차단(username 프롬프트). |

## B-0 가드 체크리스트

| 가드 | 상태 |
|------|------|
| 헤르메스 설치 (또는 네트워크 제약 보고) | ⚠️ **네트워크/소스 제약 보고** (아래 상세) |
| sandbox.py 생성 (절대선 #2 뿌리) | ✅ **완료** — `ai_pm/sandbox.py` |
| 절대선 5개 import 성공 | ⛔ **차단** — sandbox 1개만 확보, 나머지 4개(fact_verifier·banned_phrases·disclaimer_injector·legal_safety_router) 코드 부재 |
| 20개 전체 복사 + import 검증 | ⛔ **차단** — 코드 부재 (아래 상세) |
| VVS-AI-CO 커밋 (영구 보존) | ✅ **완료** — sandbox.py·테스트·구조 커밋 |

## ✅ 완료 사항

### 1. sandbox.py (절대선 #2 뿌리)
- `ai_pm/sandbox.py` 생성 — 핸드오프 C(핵심 함수) + 명시 계약대로 `Sandbox` 경로격리 클래스 구현.
- `python3 -c "import ai_pm.sandbox"` → **OK** (`SYNTHETIC_MARK=[SYNTHETIC]`).
- `tests/test_sandbox.py` → **pytest 14/14 통과**.
  - 검증: production 미접근·외부발송 차단(절대선 #2)·합성 마킹 검증·무효 식별자·경로 탈출 차단.

### 2. 구조 (영구 보존)
- `skills/{absolute-line,block,persona,rubric}/` · `tools/` · `plugins/memory/` · `ops/` · `tests/` · `ai_pm/`

## ⚠️ 헤르메스 — 네트워크/소스 제약 보고

| 시도 | 결과 |
|------|------|
| `git ls-remote https://github.com/NousResearch/hermes-agent` | ✅ refs 광고됨, 기본 브랜치 `main` |
| `git clone --depth 1` | ❌ 차단 — `could not read Username`(pack fetch에서 네트워크 정책이 401/인증 요구) |
| codeload tarball (main) | ⚠️ **완전한 아카이브이나 파일 8개(38KB)뿐** — `README.md`·`agent.py`·`config.yaml` 등 |
| 받은 tarball 내 `batch_runner` 존재? | ❌ **없음** (`grep -rl batch_runner` = 0) |

**결론:** `NousResearch/hermes-agent` 의 `main` 은 batch_runner 없는 ~8파일 stub 이다.
핸드오프가 전제하는 Hermes(= `batch_runner`·`send_message` 래핑·`base.send` 서브클래스·`scripts/install.sh` 보유)와 **일치하지 않는다.** 또한 full clone 자체가 네트워크 정책으로 차단된다.
→ **올바른 Hermes 소스 위치(또는 설치 패키지)** 확인 필요.

## ⛔ 차단: 로직 17~19개 코드 부재

핸드오프 자료목록은 "B. 20개 로직 전체 코드"를 포함한다고 하나, **이 세션 컨텍스트에는
실제 전체 코드가 없다.** 실제로 전달된 것은:
- ✅ sandbox.py 핵심 함수 (자료 C) — 사용함
- ✅ 파일명 20개 목록 · 의존 순서 · import 치환표 (자료 D)
- ❌ doc_types·fact_verifier·banned_phrases·banned_phrase_filter·disclaimer_injector·
  legal_safety_router·block_library·quality_rubric·persona_generator·sqlite_db·pattern_db·
  Ops 7개·hermes_h3_enforcement_poc 의 **본문 코드 — 부재**

"전체 코드 출력 완료"는 이전 세션에서 이뤄졌고, 새 세션인 본 세션에는 붙여넣어지지 않았다.

**절대선 5개는 헌법이므로 원본 정확성이 절대적이다. 코드 없이 임의로 재구성하지 않는다.**

## 차단 해제에 필요한 것

1. **로직 코드 본문** — 17~19개 모듈 전체 코드를 (a) 메시지로 붙여넣기, 또는
   (b) 이 세션이 접근 가능한 위치(로컬 프록시 repo 등)로 제공.
2. **올바른 Hermes 소스** — batch_runner/send_message/base.send/install.sh 를 가진
   실제 저장소 위치 또는 설치 패키지. (현 URL의 main은 stub)

## 후속 우선순위 (차단 해제 후)

1. doc_types → fact_verifier → banned_phrases → banned_phrase_filter → disclaimer_injector
   → legal_safety_router (import 치환: `agents._core.*`/`agents.*` → `.`)
2. block_library → quality_rubric → persona_generator
3. sqlite_db → pattern_db → Ops 7개
4. 각 단계 `python3 -c "import ..."` + 단위 테스트 → 커밋
5. **B-1: hermes_h3_enforcement_poc 패턴으로 send_message 래퍼 + base.send 서브클래스
   + batch_runner `_finalize` 절대선 게이트 배선 (최우선, 헌법 강제점).**
