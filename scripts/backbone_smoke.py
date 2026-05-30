#!/usr/bin/env python3
"""백본 라이브 호출 스모크 — 4개 백본 1회 호출 + 비용 기록.

실행: python3 scripts/backbone_smoke.py
필요: .env 에 ANTHROPIC/OPENAI/GEMINI 키. 키 값은 출력하지 않는다.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai_pm import backbone as bb  # noqa: E402
from ai_pm.token_cost_monitor import get_total, reset, track  # noqa: E402


def main() -> int:
    reset()
    print("=== 작성≠채점 계열분리 ===")
    print("  separation_ok():", bb.separation_ok())

    tests = [
        (bb.Role.AIPM, "Reply with the single word: READY"),
        (bb.Role.WRITER, "Reply with the single word: WRITE"),
        (bb.Role.SCORING, "Reply with exactly: SCORE"),
        (bb.Role.DESIGN, "Reply with the single word: DESIGN"),
    ]
    print("\n=== 백본 1회 호출 ===")
    ok = 0
    for role, prompt in tests:
        r = bb.call(role, prompt, max_tokens=256)
        tok = r.input_tokens + r.output_tokens
        if r.ok:
            ok += 1
            track(tok, r.model)
            print(f"  [{role.value:11}] {r.provider.value:9} {r.model:30} OK tok={tok}")
        else:
            print(f"  [{role.value:11}] {r.provider.value:9} {r.model:30} FAIL {r.error[:120]}")

    print("\n=== 비용 누적 ===")
    print(" ", get_total())
    print(f"\n=== 성공 {ok}/{len(tests)} ===")
    return 0 if ok == len(tests) else 1


if __name__ == "__main__":
    raise SystemExit(main())
