"""ai_pm/profile_blocks.py — 회사소개서 본문 빌더 (8섹션, 표 포함).

합성/실데이터(dict)를 원청 제출 수준의 마크다운 본문으로 조립한다. 표는
마크다운 테이블로 표현되어, 절대선 게이트(텍스트 검증)를 그대로 거치며
renderer 가 PDF/PPTX 의 실제 표로 렌더한다.

섹션(L1 회사소개서): 회사개요·연혁·조직·주요실적·인력현황·보유장비·안전관리·
연락처.
"""

from __future__ import annotations


def _kv_table(title: str, rows: dict, headers=("항목", "내용")) -> str:
    out = [f"## {title}", "", f"| {headers[0]} | {headers[1]} |", "|---|---|"]
    for k, v in rows.items():
        out.append(f"| {k} | {v} |")
    out.append("")
    return "\n".join(out)


def _rows_table(title: str, headers: list, rows: list) -> str:
    out = [f"## {title}", ""]
    out.append("| " + " | ".join(headers) + " |")
    out.append("|" + "|".join(["---"] * len(headers)) + "|")
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    out.append("")
    return "\n".join(out)


def _bullets(title: str, items: list) -> str:
    out = [f"## {title}", ""]
    out.extend(f"- {it}" for it in items)
    out.append("")
    return "\n".join(out)


def build_company_profile(data: dict) -> str:
    """회사소개서(L1) 8섹션 마크다운 본문을 조립한다."""
    data = data or {}
    parts: list[str] = []

    # 표지(H1)
    parts.append(f"# {data.get('title', '회사소개서')}")
    if data.get("company"):
        parts.append(data["company"])
    if data.get("tagline"):
        parts.append(data["tagline"])
    if data.get("date"):
        parts.append(f"작성일: {data['date']}")
    parts.append("")

    if data.get("overview"):
        parts.append(_kv_table("1. 회사 개요", data["overview"]))
    if data.get("history"):
        parts.append(_rows_table("2. 연혁", ["연도", "주요 내용"], data["history"]))
    if data.get("organization"):
        parts.append(_bullets("3. 조직 구성", data["organization"]))
    if data.get("track_record"):
        parts.append(_rows_table(
            "4. 주요 실적", ["연도", "발주처", "사업 내용", "규모"], data["track_record"]))
    if data.get("workforce"):
        parts.append(_rows_table("5. 인력 현황", ["구분", "인원", "비고"], data["workforce"]))
    if data.get("equipment"):
        parts.append(_rows_table("6. 보유 장비", ["장비명", "수량", "용도"], data["equipment"]))
    if data.get("safety"):
        parts.append(_bullets("7. 안전관리", data["safety"]))
    if data.get("contact"):
        parts.append(_kv_table("8. 연락처", data["contact"]))

    return "\n".join(parts).rstrip() + "\n"


# 레벨별 섹션 선택 (L2 공사지명원·L4 1페이지는 부분집합)
_L2_KEEP = {"1. 회사 개요", "2. 연혁", "4. 주요 실적", "5. 인력 현황", "6. 보유 장비", "8. 연락처"}
_L4_KEEP = {"1. 회사 개요", "4. 주요 실적", "8. 연락처"}


def build_profile(data: dict, level: str = "L1") -> str:
    """레벨별 회사소개서 본문. L1=전체, L2=핵심, L4=1페이지 요약."""
    full = build_company_profile(data)
    if level == "L1":
        return full
    keep = _L2_KEEP if level == "L2" else _L4_KEEP if level == "L4" else None
    if keep is None:
        return full
    blocks = full.split("\n## ")
    kept = [blocks[0]]  # 표지
    for b in blocks[1:]:
        sec_title = b.splitlines()[0].strip()
        if any(sec_title.startswith(k) for k in keep):
            kept.append("## " + b)
    return "\n".join(kept).rstrip() + "\n"
