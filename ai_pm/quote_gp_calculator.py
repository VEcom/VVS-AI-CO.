"""ai_pm/quote_gp_calculator.py — 견적 매출총이익(GP) 계산.

원가·판매가로 GP 금액과 GP율을 계산하고 음수 마진을 경고한다.
"""

from __future__ import annotations


def calc_gp(cost: float, price: float) -> dict:
    """GP 금액·GP율을 계산.

    GP율 = (price - cost) / price
    반환: {"gp_amount": float, "gp_rate": float, "warning": str|None}
    """
    cost = float(cost)
    price = float(price)
    if price <= 0:
        raise ValueError("price must be positive")

    gp_amount = round(price - cost, 4)
    gp_rate = round(gp_amount / price, 4)

    warning = None
    if gp_amount < 0:
        warning = "negative margin: cost exceeds price"
    elif gp_rate < 0.1:
        warning = "low margin: GP rate below 10%"

    return {"gp_amount": gp_amount, "gp_rate": gp_rate, "warning": warning}
