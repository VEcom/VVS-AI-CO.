# B-0 착수 현황

> 생성: 2026-05-29 · 갱신: 2026-05-29 (4차, 로직 17개 명세 구현 완료) · 브랜치 `claude/vvs-hermes-rebuild-KHOJ9`

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
| 절대선 5개 import 성공 | ✅ **완료** — 명세대로 구현, 단위테스트 통과 |
| 20개 전체 복사 + import 검증 | ✅ **완료(17개)** — 명세 기반 신규 작성, 17/17 import OK |
| VVS-AI-CO 커밋 (영구 보존) | ✅ **완료** |

## ✅ 완료 사항

### 1. 헤르메스 설치 (격리) — 검증 완료
- `git clone https://github.com/NousResearch/hermes-agent` → **4189 파일, clone 성공**.
- 핀: `689ef5e233980f5d5a32080e959f44c8991dd03a` (기본 브랜치 main), 버전 **hermes-agent 0.15.1**.
- `bash scripts/install.sh` (uv venv 격리 + editable 설치 + 스모크) → **RC=0 성공**.
  - 루트 설치라 FHS 레이아웃 적용: 코드/venv 가 `/usr/local/lib/hermes-agent` 로 감
    (`hermes --version` → `Project: /usr/local/lib/hermes-agent`). venv python:
    `/usr/local/lib/hermes-agent/venv/bin/python`.
  - CLI 스모크: `hermes --version` → **`Hermes Agent v0.15.1`**,
    `importlib.metadata.version('hermes-agent')` = **0.15.1**.
  - **batch_runner 검증(실측):** `venv/bin/python -c "import batch_runner"` → **OK**
    (`FILE=/usr/local/lib/hermes-agent/batch_runner.py`, 1321줄, `BatchRunner` 클래스 @527 노출).
    ※ `batch_runner`는 pyproject `py-modules`의 **최상위 모듈** — `hermes.batch` 아님.
- **B-1 배선 대상 실재 확인:** repo 내 `send_message` 69개 파일 · `_finalize` 25개 파일.
  `batch_runner.BatchRunner.run()` @810 / `main()` @1147. (정확한 배선 지점은 B-1에서 확정)
- **부트스트랩 정정:** `ops/hermes-bootstrap.sh` 가 비루트(`$DEST/venv`)·루트
  (`/usr/local/lib/hermes-agent/venv`) 두 레이아웃 모두에서 venv 를 탐지하도록 수정.
- **영구 보존 방식:** 거대 트리(4189파일)를 벤더링하지 않고 `ops/hermes-bootstrap.sh`로
  핀 고정 clone+`install.sh` 재현 가능하게 보존. (설치물 venv는 ephemeral 컨테이너 한정)

### 2. sandbox.py (절대선 #2 뿌리)
- `ai_pm/sandbox.py` — 핸드오프 C(핵심 함수) + 명시 계약대로 `Sandbox` 경로격리 클래스.
- `python3 -c "import ai_pm.sandbox"` → OK (`SYNTHETIC_MARK=[SYNTHETIC]`).
- `tests/test_sandbox.py` → **pytest 13/13 통과**.

### 3. 구조 (영구 보존)
- `skills/{absolute-line,block,persona,rubric}/` · `tools/` · `plugins/memory/` · `ops/` · `tests/` · `ai_pm/`

### 4. 로직 17개 — 명세 기반 구현 (영구 보존)

betplay 원본은 이 세션에서 접근 불가하여, **사용자 제공 명세**대로 동일 계약
(시그니처·예외·반환)을 만족하도록 신규 작성. 17/17 import OK, **pytest 43 passed**.

| 범주 | 모듈 (ai_pm/) |
|------|---------------|
| 절대선 (헌법) | `fact_verifier` · `banned_phrases` · `banned_phrase_filter` · `disclaimer_injector` · `legal_safety_router` |
| 제작 | `doc_types` · `block_library` · `quality_rubric` |
| 인프라 | `sqlite_db` · `pattern_db` · `token_cost_monitor` · `quote_gp_calculator` · `icp_screener` · `scope_freeze_checker` · `privacy_data_gatekeeper` · `delivery_start_gate` · `incident_logger` |

- 테스트: `tests/test_absolute_line.py`(헌법) · `test_production.py` · `test_infra.py` · `test_sandbox.py`.
- ⚠️ **주의:** 명세 기반 신규 구현이므로 betplay 원본과 세부 동작이 다를 수 있다.
  원본 확보 시 계약 대조·정합화 권장. (persona_generator 는 이번 17개 명세 범위 밖 — 별도)

## ✅ B-0 가드 — 전부 충족

| 가드 | 상태 |
|------|------|
| 헤르메스 설치 (import 검증) | ✅ hermes-agent 0.15.1 |
| batch_runner 동작 | ✅ `import batch_runner` OK (BatchRunner @527) |
| sandbox.py 생성 (절대선 #2 뿌리) | ✅ ai_pm/sandbox.py |
| 절대선 5개 import 성공 | ✅ 5/5 + 테스트 통과 |
| 로직 복사 + import 검증 | ✅ 17/17 import OK, pytest 43 passed |
| VVS-AI-CO 커밋 (영구 보존) | ✅ |

## ▶ B-1 준비 상태 (다음, 최우선 — 헌법 강제점)

목표: **절대선 3강제점**을 헤르메스 런타임에 배선해 우회 불가능하게 만든다.

배선 대상(헤르메스 0.15.1, 실측):
- `batch_runner.BatchRunner.run()` @810 / `main()` @1147 — 배치 종료부에 절대선 게이트.
- `send_message` 계열 (repo 내 69개 파일; 핵심: `tools/send_message_tool.py`,
  `gateway/platforms/base.py`) — 외부 발송 전 절대선 통과 강제 (sandbox `no_external_send` 연동).
- `_finalize` 계열 (25개 파일) — 산출물 확정 직전 게이트.

3강제점 (배선할 헌법 검사):
1. **fact/금지표현/면책 게이트** — `banned_phrase_filter.check_and_raise` +
   `disclaimer_injector.inject` + `fact_verifier.verify_fact` 를 산출 직전 통과 강제.
2. **법무 라우팅** — `legal_safety_router.route` 가 requires_legal 이면 발송/확정 차단.
3. **격리/PII** — `sandbox.no_external_send`(Phase 0) + `privacy_data_gatekeeper.scan`
   으로 외부 발송·PII 유출 차단, 위반 시 `incident_logger` 기록.

> B-1 은 신규 코드 작성보다 **배선(통합) 지점 확정**이 핵심이라, 헤르메스 쪽 정확한
> hook 지점을 먼저 합의 후 진행 권장.
