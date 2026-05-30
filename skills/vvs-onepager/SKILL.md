---
name: vvs-onepager
description: VVS L4 1페이지 요약서(one-pager) 제작 스킬. 반도체 협력사 핵심 정보를 1페이지로 압축한 요약서를 block_library 블록으로 조립하고, 반드시 ai_pm 절대선 게이트(production_pipeline)를 거쳐 전달한다. 1페이지·원페이저·one-pager·요약서 요청 시 사용.
---

# vvs-onepager (L4 1페이지 요약서)

반도체 협력사 핵심 정보를 **1페이지**로 압축한 요약서를 제작한다.

## 절대 규칙 (헌법)

- 산출물은 **반드시** `ai_pm.production_pipeline` 을 거쳐 전달한다.
- 파이프라인이 절대선 게이트(`guarded_send`)를 강제 → 위반 산출물은 실제
  송출 함수 미도달(`real_fn_called=False`).
- 헤르메스 직접 수정 금지. 제작=PRODUCTION 채널, 고객 전달=CUSTOMER 채널만.

## 구성

- `scripts/assemble.py` — 입력 → block_library 블록 스펙 → 파이프라인.
- `templates/onepager.blocks.json` — 블록 구성(간결: 머리말+소개+꼬리말).
