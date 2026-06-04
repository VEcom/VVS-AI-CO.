---
name: vvs-deliverable-doc
description: VVS 산출물 문서를 실제 PDF/PPTX 파일로 렌더하고, 반드시 ai_pm 절대선 게이트(document_pipeline)를 거쳐 as_document 로 전달한다. L1 회사소개서·L2 공사지명원·L4 1페이지를 PDF/PPT 파일로 만들 때 사용. PDF·PPT·슬라이드·deck·파일 산출 요청 시.
---

# vvs-deliverable-doc (PDF/PPT 산출물)

VVS 제작 산출물(L1/L2/L4)을 **실제 PDF/PPTX 파일**로 렌더한다.

## 절대 규칙 (헌법)

- 렌더 산출물(PDF/PPT)도 **반드시** 절대선 게이트를 거친다(텍스트와 동일).
  게이트는 렌더 **이전**에 원본 텍스트를 검증하므로, 렌더물이 게이트를
  우회할 수 없다.
- 위반 시: 렌더가 일어나지 않고 as_document 전달도 없다
  (`real_fn_called=False`, `rendered=False`).
- 게이트가 정제한 텍스트(면책 자동주입 포함)로만 렌더 → 렌더물도 면책 포함.
- 헤르메스 직접 수정 금지. 강제는 `ai_pm.document_pipeline` 레이어.
- 전달은 게이트 통과 후 `as_document`(원본 그대로, 재압축 X).

## 구성

- `scripts/build_pptx.py` — 입력 → 블록 → 게이트 → .pptx → as_document.
- `scripts/build_pdf.py`  — 입력 → 블록 → 게이트 → .pdf → as_document.
- `templates/deliverable.blocks.json` — 레벨별 블록 구성.

## 사용 (런타임)

```python
from build_pptx import run as build_pptx
result = build_pptx(data={...}, level="L1", real_send_document=as_document_fn, claims=[...])
# result.real_fn_called 는 게이트 통과 시에만 True
# result.render.path 가 .pptx 경로 (게이트 통과 시)
```

## 디자인 검수 (점수 산출)

렌더 후 `ai_pm.vision_review.review_design(result.render, text=...)` 로
가독성·정렬·여백·브랜딩 4기준(각 25점) 채점. B-4 학습에서 rubric visual
항목으로 연결된다. 실제 비전 분석은 헤르메스 `tools/vision_tools.vision_analyze`
를 `vision_fn` 으로 주입(B-4).
