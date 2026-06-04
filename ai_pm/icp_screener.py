"""ai_pm/icp_screener.py — 이상적 고객 프로필(ICP) 판정.

반도체 협력사 기준으로 고객이 ICP 에 부합하는지 점수화한다.
"""

from __future__ import annotations

# 반도체 협력사 ICP 기준(각 가중치). 합 100.
_CRITERIA = {
    "industry_semiconductor": 40,  # 반도체 산업 여부
    "is_supplier": 25,             # 협력사(공급망) 여부
    "min_employees": 15,           # 일정 규모 이상
    "has_quality_cert": 20,        # 품질 인증 보유
}

_ICP_THRESHOLD = 60


def screen(customer: dict) -> dict:
    """고객을 ICP 기준으로 판정.

    customer 예: {"industry": "반도체", "is_supplier": True,
                  "employees": 120, "certs": ["ISO9001"]}
    반환: {"is_icp": bool, "score": int}
    """
    customer = customer or {}
    score = 0

    industry = str(customer.get("industry", ""))
    if "반도체" in industry or "semiconductor" in industry.lower():
        score += _CRITERIA["industry_semiconductor"]

    if customer.get("is_supplier"):
        score += _CRITERIA["is_supplier"]

    if int(customer.get("employees", 0)) >= 50:
        score += _CRITERIA["min_employees"]

    if customer.get("certs"):
        score += _CRITERIA["has_quality_cert"]

    return {"is_icp": score >= _ICP_THRESHOLD, "score": score}
