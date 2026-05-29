# B-0 착수 현황

> 생성: 2026-05-29 · 갱신: 2026-05-29 (3차, Hermes 설치 검증 반영) · 브랜치 `claude/vvs-hermes-rebuild-KHOJ9`

## 사전 확인 결과

| 항목 | 결과 | 비고 |
|------|------|------|
| betplay-mvp / vvs-handoff 읽기 | ❌ **불가** | 외부 GitHub 인증 불가 + 로컬 프록시에 해당 repo 없음. |
| VVS-AI-CO push | ✅ **가능** | 푸시·remote ref 검증 완료. 영구 보존 충족. |
| 외부 GitHub 접근 (Hermes) | ✅ **가능** | full clone 성공 (4189 파일). |

## B-0 가드 체크리스트

| 가드 | 상태 |
|------|------|
| 헤르메스 설치 (import 검증) | ✅ **완료** — `hermes-agent 0.15.1`, CLI "hermes OK 0.15.1" |
| batch_runner 동작 | ✅ **완료** — `import batch_runner` OK, `BatchRunner` 클래스 노출 |
| sandbox.py 생성 (절대선 #2 뿌리) | ✅ **완료** — `ai_pm/sandbox.py`, pytest 13/13 |
| 절대선 5개 import 성공 | ⛔ **차단** — sandbox 1개만 확보, 나머지 4개 코드 부재 |
| 20개 전체 복사 + import 검증 | ⛔ **차단** — 로직 17~19개 코드 부재 |
| VVS-AI-CO 커밋 (영구 보존) | ✅ **완료** |

## ✅ 완료 사항

### 1. 헤르메스 설치 (격리) — 검증 완료
- `git clone https://github.com/NousResearch/hermes-agent` → **4189 파일, clone 성공**.
- 핀: `689ef5e233980f5d5a32080e959f44c8991dd03a` (기본 브랜치 main), 버전 **hermes-agent 0.15.1**.
- `bash scripts/install.sh` (uv venv 격리 + editable 설치 + 스모크) → **RC=0 성공**.
  - venv: `/home/user/hermes-agent/venv` (주의: `.venv` 아님).
  - CLI 스모크: `hermes` → **`hermes OK 0.15.1`**, `importlib.metadata.version('hermes-agent')` = **0.15.1**.
  - **batch_runner 검증:** `venv/bin/python -c "import batch_runner"` → **OK**
    (`/home/user/hermes-agent/batch_runner.py`, 1099줄, `BatchRunner` 클래스 노출).
    ※ `batch_runner`는 pyproject `py-modules`의 **최상위 모듈** — `hermes.batch` 아님.
- **B-1 배선 대상 실재 확인:** repo 내 `send_message` 18개 파일 · `_finalize` 10개 파일.
  (정확한 배선 지점은 B-1에서 확정)
- **영구 보존 방식:** 거대 트리(4189파일)를 벤더링하지 않고 `ops/hermes-bootstrap.sh`로
  핀 고정 clone+`install.sh` 재현 가능하게 보존. (설치물 venv는 ephemeral 컨테이너 한정)

### 2. sandbox.py (절대선 #2 뿌리)
- `ai_pm/sandbox.py` — 핸드오프 C(핵심 함수) + 명시 계약대로 `Sandbox` 경로격리 클래스.
- `python3 -c "import ai_pm.sandbox"` → OK (`SYNTHETIC_MARK=[SYNTHETIC]`).
- `tests/test_sandbox.py` → **pytest 13/13 통과**.

### 3. 구조 (영구 보존)
- `skills/{absolute-line,block,persona,rubric}/` · `tools/` · `plugins/memory/` · `ops/` · `tests/` · `ai_pm/`

## ⛔ 차단: 로직 17~19개 코드 부재 (유일한 잔여 차단)

핸드오프 자료목록은 "B. 20개 로직 전체 코드"를 포함한다고 하나, **이 세션 컨텍스트에는
실제 코드 본문이 없다.** 실제로 전달된 것:
- ✅ sandbox.py 핵심 함수 (자료 C) — 사용함
- ✅ 파일명 20개 · 의존 순서 · import 치환표 (자료 D)
- ❌ doc_types·fact_verifier·banned_phrases·banned_phrase_filter·disclaimer_injector·
  legal_safety_router·block_library·quality_rubric·persona_generator·sqlite_db·pattern_db·
  Ops 7개·hermes_h3_enforcement_poc 의 **본문 코드 — 부재**

"전체 코드 출력 완료"는 이전 세션에서 이뤄졌고, 새 세션인 본 세션에 붙여넣어지지 않았다.
betplay/vvs-handoff 도 이 세션에서 접근 불가.

**절대선 5개는 헌법이므로 원본 정확성이 절대적이다. 코드 없이 임의로 재구성하지 않는다.**

## 차단 해제에 필요한 것 (단 하나)

**로직 코드 본문** — 17~19개 모듈 전체 코드를 (a) 메시지로 붙여넣기, 또는
(b) 이 세션이 접근 가능한 위치로 제공.

> 의존 순서대로 1~3개씩 나눠 붙여넣어도 됨. 받는 즉시 import 치환 → 검증 → 커밋한다.

## 후속 우선순위 (코드 도착 시)

1. doc_types → fact_verifier → banned_phrases → banned_phrase_filter → disclaimer_injector
   → legal_safety_router (import 치환: `agents._core.*`/`agents.*`/`ai_pm.*` → `.`)
2. block_library → quality_rubric → persona_generator
3. sqlite_db → pattern_db → Ops 7개
4. 각 단계 `python3 -c "import ..."` + 단위 테스트 → 커밋
5. **B-1: hermes_h3_enforcement_poc 패턴으로 send_message 래퍼 + base.send 서브클래스
   + batch_runner `_finalize` 절대선 게이트 배선 (최우선, 헌법 강제점).**
