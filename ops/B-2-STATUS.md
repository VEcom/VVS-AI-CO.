# B-2 현황 — 제작 스킬 + 절대선 래퍼 런타임 주입

> 생성: 2026-05-30 · 브랜치 `claude/vvs-hermes-rebuild-KHOJ9`

## 핵심 결과 (★ 주입 최우선)

**제작 스킬 산출물이 실제 제작 흐름에서 guarded_send 를 거치며, 위반 시
real_fn_called=False — 계약 테스트가 아닌 "실제 제작 흐름"에서 증명.**

- 전체 테스트: **pytest 88 passed** (B-0 53 + B-1 17 + B-2 18).
- B-1 미해결("래퍼 실제 런타임 주입")을 B-2 에서 해소: 제작 산출물이 반드시
  절대선 게이트를 거치도록 ai_pm 레이어에서 강제(헤르메스 직접수정 0).

## 런타임 주입 구조 (가장 중요)

제작 스킬은 송출 함수를 **직접 호출하지 않는다.** 대신:

```
스킬 scripts/assemble.py
  → ai_pm.production_pipeline.produce_and_deliver(real_send, blocks, ...)
      → ProductionPipeline.assemble()   # block_library 조립 → PRODUCTION 채널만
      → ProductionPipeline.deliver()    # ChannelRouter.deliver_to_customer
          → guarded_send()              # 절대선 게이트 (B-1)
              → (통과 시에만) real_send  # 헤르메스 송출 함수
```

- `produce_and_deliver` 안에서 고객 전달 경로는 `deliver()` 단 하나, 그 안의
  `guarded_send` 호출도 게이트 통과 후 단 하나뿐 → 위반 시 real_send 도달 불가.
- 헤르메스를 수정하지 않으므로 bootstrap 재현과 양립. 강제는 ai_pm 레이어.

## 구현

### 1. 제작 스킬 (L1/L2/L4)
| 레벨 | 스킬 | doc_type | 블록 |
|------|------|----------|------|
| L1 | `skills/vvs-company-profile/` | 회사소개서 | header·company_intro·footer |
| L2 | `skills/vvs-vendor-dossier/` | 기술문서 | header·company_intro·terms·footer |
| L4 | `skills/vvs-onepager/` | 회사소개서 | header·company_intro·footer |

- 각: `SKILL.md` + `scripts/assemble.py` + `templates/*.blocks.json`.
- `assemble.py` 는 입력 데이터 → `block_library` 블록 스펙 → `produce_and_deliver`.
- 송출 직접 호출 없음(파이프라인이 게이트 강제).

### 2. ai_pm/production_pipeline.py (주입 레이어, B-2 심장)
- `ProductionPipeline.assemble()` — 조립물을 PRODUCTION 채널에만 적재(고객 미도달).
- `ProductionPipeline.deliver()` — 유일 고객 경로, guarded_send 게이트 강제.
- `produce_and_deliver()` — 스킬 표준 진입점(조립+전달 원샷).

### 3. ai_pm/persona_generator.py (invariant 가드)
- 0-based `_ym` (0~11, 범위 밖 거부), 시작<종료, 미래 종료 차단.
- 식별자 무효(전부 0/-) 강제 + synthetic=True/[SYNTHETIC] 재검증.
- B-4 학습 준비.

## B-2 검수 체크리스트

| 검수 항목 | 상태 | 증명 테스트 |
|-----------|------|-------------|
| L1/L2/L4 스킬 산출물 생성 (fact_ok) | ✅ | `test_L1/L2/L4_clean_flows_through_gate_and_delivers` |
| ★ 래퍼 런타임 주입: 산출물이 실제로 guarded_send 거침 | ✅ | 위 + 면책 자동주입이 송출 본문에 포함됨으로 게이트 경유 증명 |
| ★ 주입 후에도 real_fn_called=False (실제 흐름) | ✅ | `test_L1/L2/L4_*_blocks_real_fn_in_real_flow`, `test_all_levels_block_on_violation` |
| persona_generator (invariant 가드) | ✅ | `test_persona_ym/start_before_end/future_blocked/identifier_void` |
| 제작채널≠고객채널 (청크 노출 0) | ✅ | `test_assembly_stays_in_production_channel_not_customer`, `test_llm_bypass_zero_customer_delivery_in_production` |
| 절대선 5개 실제 제작 흐름에서 작동 | ✅ | `test_gate_disclaimer_autoinject_in_pipeline`, `test_gate_legal_flag_nonblocking_in_pipeline`, fact/banned 차단 테스트 |
| 테스트 유지·추가 | ✅ | 88 passed (회귀 0) |

## real_fn_called=False — 실제 흐름 증명 요지

`test_L1_banned_blocks_real_fn_in_real_flow`: L1 스킬의 회사소개에 금지표현을
주입하고 `L1.run(...)` 호출 → 실제 제작 흐름(assemble→deliver→guarded_send)에서
게이트가 차단 → `res["real_fn_called"] is False` + `spy.called is False`.
이는 B-1 의 계약 테스트(직접 guarded_send 호출)와 달리, **스킬 진입점을 통한
실제 제작 흐름**에서 송출 함수 미도달을 증명한다.

## 제약 준수
- PDF/PPT 렌더링은 B-3 (현재는 텍스트 산출물).
- 헤르메스 bootstrap 재현 유지(직접 수정 0).
- betplay 계약 동일: fact_ok, [SYNTHETIC], 무효 식별자, 면책 자동주입.

## 다음 (B-2 범위 밖)
- B-3: PDF/PPT 렌더링.
- B-4: persona_generator 기반 학습 궤적 생성(trajectory_gate 로 환각 제외).
