---
name: vvs-company-profile
description: VVS L1 회사소개서 제작 스킬. 반도체 협력사의 회사소개서 초안을 block_library 블록으로 조립하고, 반드시 ai_pm 절대선 게이트(production_pipeline)를 거쳐 고객에게 전달한다. 회사소개서·회사 프로필·company profile 요청 시 사용.
---

# vvs-company-profile (L1 회사소개서)

반도체 협력사용 **회사소개서** 초안을 제작한다.

## 절대 규칙 (헌법)

- 산출물은 **반드시** `ai_pm.production_pipeline` 을 거쳐 전달한다.
  스킬이 송출 함수를 직접 호출하지 않는다.
- 파이프라인이 절대선 게이트(`guarded_send`)를 강제하므로, 위반 산출물은
  실제 송출 함수에 도달하지 못한다(`real_fn_called=False`).
- 헤르메스를 직접 수정하지 않는다. 강제는 ai_pm 레이어에서만.
- 제작(조립)은 PRODUCTION 채널, 고객 전달은 CUSTOMER 채널(명시 호출)로만.

## 구성

- `scripts/assemble.py` — 입력 데이터 → block_library 블록 스펙 → 파이프라인.
- `templates/company_profile.blocks.json` — 블록 구성(순서).

## 사용 (런타임)

```python
from skills_runtime import run_skill  # 예시
result = run_skill(
    "vvs-company-profile",
    data={...},          # 회사 정보
    claims=[...],        # [SYNTHETIC] 검증 대상 주장
    real_send=adapter_send,
)
# result["real_fn_called"] 가 게이트 통과 시에만 True
```

스크립트 직접 호출은 `scripts/assemble.py` 의 `build_blocks(data)` 참고.
