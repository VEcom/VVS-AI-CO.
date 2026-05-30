# B-3 현황 — PDF/PPT 렌더 + 디자인 검수 + 렌더물 절대선 게이트

> 생성: 2026-05-30 · 브랜치 `claude/vvs-hermes-rebuild-KHOJ9`

## 핵심 결과 (★ 렌더물도 게이트)

**렌더된 PDF/PPT 도 절대선 게이트를 거치며, 위반 시 real_fn_called=False
그리고 rendered=False(렌더조차 미실행) — 렌더물이 게이트를 우회하지 못함.**

- 전체 테스트: **pytest 103 passed** (B-0 53 + B-1 17 + B-2 18 + B-3 15).
- 실제 .pptx / .pdf 파일 생성(python-pptx / reportlab). soffice·node 도 가용.

## 렌더물 게이트 우회 차단 구조 (가장 중요)

게이트는 렌더 **이전**에 원본 텍스트를 검증한다. 렌더+as_document 전달은
게이트 통과 후에만 도달하는 클로저 안에 있다:

```
build_pptx/pdf.run
  → document_pipeline.render_and_deliver_document
      → assemble(text)                       # PRODUCTION 채널
      → DocumentPipeline.deliver_as_document
          → production_pipeline.deliver
              → guarded_send(원본 텍스트)      # 절대선 게이트 (B-1)
                  → (통과 시에만) _render_and_send 클로저
                        → render(정제텍스트)   # 렌더는 여기서 처음 실행
                        → real_send_document   # as_document 전달
```

- 위반 시 guarded_send 가 `_render_and_send` 를 호출하지 않음 → 렌더 미실행
  (`rendered=False`) + as_document 미전달(`real_fn_called=False`).
- 게이트가 정제한 텍스트(면책 자동주입 포함)로만 렌더 → 렌더물에도 면책 포함
  (pptx 직접 파싱으로 검증).
- 헤르메스 직접수정 0. guarded_send/production_pipeline 재사용.

## 구현

### ai_pm/document_renderer.py (순수 렌더)
- `render_pptx` / `render_pdf` — VVS 브랜딩(네이비/액센트 바)·레벨 레이아웃.
- `split_sections` — 본문 → (heading, body) 분해.
- 라이브러리 부재 시 `RendererUnavailable` 우아 비활성화(게이트는 무영향).

### ai_pm/document_pipeline.py (B-3 심장)
- `DocumentPipeline.deliver_as_document` — 게이트 통과 후에만 렌더+as_document.
- `render_and_deliver_document` — 조립+게이트+렌더+전달 원샷(스킬 진입점).
- `DocumentDelivery(delivered, real_fn_called, rendered, render, violations, flags)`.

### ai_pm/vision_review.py (디자인 점수)
- 4기준(가독성·정렬·여백·브랜딩, 각 25점) 결정론 휴리스틱 채점.
- `vision_fn` 주입 훅 — 헤르메스 `tools/vision_tools.vision_analyze` 연결(B-4).
- 비전 실패 시 휴리스틱으로 우아 강등.

### skills/vvs-deliverable-doc/
- `scripts/build_pptx.py` / `build_pdf.py` — 게이트 경유 렌더+전달.
- `scripts/_common.py` — 레벨별 블록 조립.
- `templates/deliverable.blocks.json` — L1/L2/L4 블록 구성.

## B-3 검수 체크리스트

| 검수 항목 | 상태 | 증명 |
|-----------|------|------|
| L1/L2/L4 PDF/PPT 렌더 성공 | ✅ | `test_pptx/pdf_render_success_all_levels` (실제 파일 생성 확인) |
| 비전 디자인 검수 작동(점수 산출) | ✅ | `test_design_review_scores`, vision_fn 주입/실패 우아강등 |
| ★ PDF/PPT도 guarded_send 거침 (real_fn_called=False) | ✅ | `test_pptx_banned_blocks_render_and_delivery` 등 |
| 렌더 산출물도 절대선 게이트 (fact/면책/금지어) | ✅ | banned/fact 차단 + 면책 자동주입 렌더물 반영 |
| as_document 전달 (게이트 통과 후, 원본 경로) | ✅ | `test_as_document_delivers_original_path` |
| 테스트 유지·추가 | ✅ | 103 passed (회귀 0) |

## real_fn_called=False — 렌더물 증명 요지

`test_pptx_banned_blocks_render_and_delivery`: 회사소개에 금지표현 주입 →
`build_pptx.run` → 게이트 차단 → `real_fn_called=False` + `rendered=False` +
`spy.called=False`(as_document 미전달). 렌더 자체가 일어나지 않으므로 렌더물이
게이트를 우회할 경로가 없다.

## 제약 준수
- B-3 = 렌더 + 검수 + 게이트. 학습 루프는 B-4.
- 디자인 검수는 점수 산출까지(실제 vision_analyze 연결·학습은 B-4).
- 헤르메스 bootstrap 재현 유지(직접수정 0).
- 의존성: requirements.txt(python-pptx/reportlab/Pillow). 코어 게이트는 stdlib만.

## 다음 (B-3 범위 밖)
- B-4: 학습 루프 — persona_generator 궤적 + trajectory_gate 환각 제외 +
  vision_review 를 rubric visual 항목으로 연결(vision_fn 실연결).
