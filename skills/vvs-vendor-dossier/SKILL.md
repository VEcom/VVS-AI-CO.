---
name: vvs-vendor-dossier
description: VVS L2 공사지명원(vendor dossier) 제작 스킬. 반도체 협력사의 공사지명원/협력사 등록 서류 초안을 block_library 블록으로 조립하고, 반드시 ai_pm 절대선 게이트(production_pipeline)를 거쳐 전달한다. 공사지명원·협력사 등록·vendor dossier 요청 시 사용.
---

# vvs-vendor-dossier (L2 공사지명원)

반도체 협력사용 **공사지명원** 초안을 제작한다.

## 절대 규칙 (헌법)

- 산출물은 **반드시** `ai_pm.production_pipeline` 을 거쳐 전달한다.
- 파이프라인이 절대선 게이트(`guarded_send`)를 강제 → 위반 산출물은 실제
  송출 함수 미도달(`real_fn_called=False`).
- 헤르메스 직접 수정 금지. 제작=PRODUCTION 채널, 고객 전달=CUSTOMER 채널만.

## 구성

- `scripts/assemble.py` — 입력 → block_library 블록 스펙 → 파이프라인.
- `templates/vendor_dossier.blocks.json` — 블록 구성.
