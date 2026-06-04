# B-1 현황 — 절대선 3강제점 (헌법의 심장)

> 생성: 2026-05-30 · 브랜치 `claude/vvs-hermes-rebuild-KHOJ9`

## 핵심 결과

**위반 산출물은 실제 송출 함수에 도달하지 못한다 (real_fn_called=False) — 코드+테스트로 증명.**

- 전체 테스트: **pytest 70 passed** (B-0 53 + B-1 강제점 17).
- 강제점은 모두 VVS-AI-CO 안(`ai_pm/`)에 있어 **영구 보존**된다. 헤르메스 트리는
  벤더링하지 않고 bootstrap 으로 재현하므로, 헤르메스 파일을 직접 수정하지 않고
  **래핑(H-3 패턴)** 으로 배선한다.

## 배선 지점 최종 확정 (헤르메스 0.15.1 실측)

| 강제점 | 헤르메스 지점 | VVS 래퍼 |
|--------|--------------|----------|
| 고객 전달 #1·#3·#4 | `tools/send_message_tool.py::send_message_tool(args)` @149 → `_handle_send` @168 → `_send_to_platform` @557 | `ai_pm/enforcement.py::guard_send_message_tool` / `guarded_send` / `wrap_send` |
| 외부발송 #2 | `gateway/platforms/base.py::BasePlatformAdapter.send(chat_id, content, reply_to, metadata)` @2001 | `ai_pm/external_send_guard.py::GuardedExternalSendMixin` / `guard_external_send` |
| 학습 궤적 | `batch_runner.py::_process_batch_worker` 궤적 기록(@487 부근), `BatchRunner.run()` @810 / `main()` @1147 | `ai_pm/trajectory_gate.py::finalize_trajectories` / `is_hallucinated` |
| 제작채널≠고객채널 | (정책) 에이전트 기본 산출 vs 명시적 send | `ai_pm/channels.py::ChannelRouter` |

> 참고: 명세의 `_finalize` 라는 이름은 0.15.1 batch_runner 에 없다. 실제 궤적 확정
> 지점은 `_process_batch_worker` 에서 `result["success"] and result["trajectory"]`
> 검사 후 jsonl 기록(@487). `finalize_trajectories` 를 그 기록 직전에 호출하는 것이
> B-2 배선 계획.

## 구현 (ai_pm/)

- **enforcement.py** — `AbsoluteLineGate`(절대선 게이트), `guarded_send`(H-3),
  `wrap_send`, `guard_send_message_tool`.
  - #1 fact: 미검증 주장 → 차단
  - #3 banned: 금지표현 hard hit → 차단
  - #3 disclaimer: 부재 시 자동주입(기본) 또는 차단(strict 모드)
  - #4 legal: 법무 트리거 → 플래그(비차단)
- **external_send_guard.py** — `GuardedExternalSendMixin`(base.send 서브클래스용),
  `guard_external_send`(함수형). 학습모드 시 `sandbox.no_external_send` 로 차단.
- **trajectory_gate.py** — `finalize_trajectories`/`is_hallucinated`. 학습 궤적은
  fact/banned 만 강제(면책/법무는 전달 단계 관심사).
- **channels.py** — `ChannelRouter`. 에이전트 기본 산출은 production sink(고객 미도달),
  고객 전달은 `deliver_to_customer`(게이트 경유)가 유일 경로.

## B-1 검수 체크리스트

| 검수 항목 | 상태 | 증명 테스트 |
|-----------|------|-------------|
| send_message 래퍼: 위반 산출물 real_fn_called=False | ✅ | `test_banned_blocks_real_fn_not_called`, `test_fact_unverified_blocks_real_fn_not_called` |
| LLM 우회(도구 미호출) 시 고객 전달 0 | ✅ | `test_llm_bypass_zero_customer_delivery`, `test_customer_delivery_only_via_gated_send` |
| base.send 서브클래스: 외부발송 차단 | ✅ | `test_guarded_mixin_blocks_super_send`, `test_external_send_func_blocked_in_learning` |
| batch_runner 궤적: 환각 궤적 제외 | ✅ | `test_finalize_excludes_hallucinated`, `test_trajectory_hallucination_detection` |
| 제작채널≠고객채널 강제 | ✅ | `test_llm_bypass_zero_customer_delivery` (production sink 격리) |
| 절대선 5개 게이트 각각 작동 | ✅ | `test_gate_fact_line1`/`_banned_line3`/`_disclaimer_inject_vs_block`/`_legal_line4_nonblocking`/`_all_pass` |
| 절대선 테스트 보존·강화 | ✅ | B-0 `test_absolute_line.py` 보존(통과) + B-1 강제점 통합 검증 추가 |

## real_fn_called=False 증명 요지

`guarded_send`(enforcement.py) 안에서 `real_send` 호출문은 **단 한 곳**, `verdict.passed`
통과 이후에만 존재한다. 위반 시 함수는 그 이전에 `{"delivered": False,
"real_fn_called": False, ...}` 로 **조기 반환**하므로 real_send 호출문에 도달이 불가능하다.
테스트의 `SendSpy.called` 가 위반 케이스에서 `False` 임을 단언해 이를 증명한다.

## 미해결 / 다음 (B-1 범위 밖)

- 실제 헤르메스 런타임에 래퍼를 **자동 주입**하는 부트스트랩 통합은 B-2(제작 스킬 배선)
  에서 함께 처리. 현재는 래퍼 레이어 + 계약 테스트까지(요청대로 강제점 배선).
- `persona_generator` 미구현 (B-4 대상).
- 로직은 명세 기반 신규 구현 — 원본 확보 시 "세 약점" 대조 권장.
