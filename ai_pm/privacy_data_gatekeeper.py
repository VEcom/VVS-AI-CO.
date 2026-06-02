"""ai_pm/privacy_data_gatekeeper.py — 개인정보(PII) 게이트키퍼.

텍스트에서 주민등록번호·전화번호·이메일 등 개인정보를 탐지한다.
sandbox 격리(절대선 #2)와 함께, 합성이 아닌 실데이터 유출을 차단하는 1차선.
"""

from __future__ import annotations

import re

# PII 탐지 패턴 (한국 맥락)
_PATTERNS: dict[str, re.Pattern] = {
    # 주민등록번호: 6자리-7자리
    "rrn": re.compile(r"\b\d{6}-\d{7}\b"),
    # 전화번호: 010-1234-5678 / 02-123-4567 등
    "phone": re.compile(r"\b0\d{1,2}-\d{3,4}-\d{4}\b"),
    # 이메일
    "email": re.compile(r"\b[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
}


def scan(data: str) -> dict:
    """텍스트에서 PII 를 탐지.

    반환: {"has_pii": bool, "types": list[str]}
    """
    data = "" if data is None else str(data)
    types = [name for name, pat in _PATTERNS.items() if pat.search(data)]
    return {"has_pii": bool(types), "types": types}
