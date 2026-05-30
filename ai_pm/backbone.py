"""ai_pm/backbone.py — 멀티모델 백본 배치 + 호출 (조직도 v4).

각 역할에 백본 모델을 배치하고, **작성≠채점 계열분리**를 코드로 강제한다.
같은 계열(provider)이 자기 작품을 채점하면 편향(학습 오염)이므로, 작성 계열과
채점 계열이 같으면 BackboneSeparationError 를 던진다.

조직도 v4 배치:
  AI PM(총괄/Graduation) = Claude Opus 4.8   (GPT-5.5 → Opus 4.8 변경)
  작성 Core             = Claude Opus 4.8
  작성 기본(L1/L2)       = Claude Sonnet 4.6
  작성 L4(1페이지)       = Claude Haiku 4.5
  페르소나              = Claude Sonnet 4.6
  채점(Scoring, 독립) ★ = GPT-5.5            (작성과 다른 계열)
  디자인 검수           = Gemini 3.1 Pro

키/모델 ID 는 .env 에서 로드한다(커밋 금지). 절대선 게이트는 이 모듈에
의존하지 않는다(게이트는 stdlib 결정론).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_ENV = _REPO / ".env"


# ── .env 로더 (python-dotenv 불필요, stdlib) ──
def load_env(path: Path = _ENV) -> dict:
    """.env 를 파싱해 dict 반환(+ os.environ 에 주입). 값은 반환만, 로깅 X."""
    kv: dict[str, str] = {}
    if not path.exists():
        return kv
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip()
        kv[k] = v
        os.environ.setdefault(k, v)
    return kv


class Provider(Enum):
    ANTHROPIC = "anthropic"   # Claude — 작성·총괄·페르소나
    OPENAI = "openai"         # GPT — 채점(독립)
    GOOGLE = "google"         # Gemini — 디자인


class Role(Enum):
    AIPM = "aipm"                 # 총괄/Graduation
    WRITER_CORE = "writer_core"   # 작성 Core
    WRITER = "writer"             # 작성 기본 (L1/L2)
    WRITER_L4 = "writer_l4"       # 작성 L4
    PERSONA = "persona"           # 페르소나 생성
    SCORING = "scoring"           # 채점 (독립) ★
    DESIGN = "design"             # 디자인 검수


# 역할 → (provider, .env 모델키, 기본 모델ID)
ROLE_BACKBONE: dict[Role, tuple[Provider, str, str]] = {
    Role.AIPM:        (Provider.ANTHROPIC, "AIPM_MODEL", "claude-opus-4-8"),
    Role.WRITER_CORE: (Provider.ANTHROPIC, "WRITER_CORE_MODEL", "claude-opus-4-8"),
    Role.WRITER:      (Provider.ANTHROPIC, "WRITER_DEFAULT_MODEL", "claude-sonnet-4-6"),
    Role.WRITER_L4:   (Provider.ANTHROPIC, "WRITER_L4_MODEL", "claude-haiku-4-5-20251001"),
    Role.PERSONA:     (Provider.ANTHROPIC, "PERSONA_MODEL", "claude-sonnet-4-6"),
    Role.SCORING:     (Provider.OPENAI, "SCORING_MODEL", "gpt-5.5"),
    Role.DESIGN:      (Provider.GOOGLE, "DESIGN_MODEL", "gemini-3.1-pro-preview"),
}

# 작성 계열 역할 / 채점 역할 (계열분리 강제용)
WRITER_ROLES = {Role.WRITER_CORE, Role.WRITER, Role.WRITER_L4, Role.AIPM, Role.PERSONA}
SCORING_ROLES = {Role.SCORING}

PROVIDER_ENV_KEY = {
    Provider.ANTHROPIC: "ANTHROPIC_API_KEY",
    Provider.OPENAI: "OPENAI_API_KEY",
    Provider.GOOGLE: "GEMINI_API_KEY",
}


class BackboneSeparationError(Exception):
    """작성 계열이 채점도 맡으면(편향) 차단."""


class BackboneNotConfigured(Exception):
    """역할의 API 키/모델이 미설정."""


@dataclass
class Backbone:
    role: Role
    provider: Provider
    model: str

    @property
    def has_key(self) -> bool:
        return bool(os.environ.get(PROVIDER_ENV_KEY[self.provider]))


def resolve(role: Role, env: dict | None = None) -> Backbone:
    """역할 → Backbone(provider, model). 모델은 .env 우선, 없으면 기본값."""
    env = env if env is not None else load_env()
    provider, env_key, default = ROLE_BACKBONE[role]
    model = env.get(env_key) or os.environ.get(env_key) or default
    return Backbone(role=role, provider=provider, model=model)


def assert_writer_scorer_separation(writer_role: Role, scorer_role: Role) -> None:
    """★ 작성≠채점 계열분리 강제.

    작성 백본과 채점 백본의 provider 가 같으면(=같은 계열이 자기 작품 채점)
    BackboneSeparationError. B-3 빈페이지 91점류 편향 재발 방지.
    """
    w = resolve(writer_role)
    s = resolve(scorer_role)
    if w.provider is s.provider:
        raise BackboneSeparationError(
            f"작성({writer_role.value}={w.provider.value})과 "
            f"채점({scorer_role.value}={s.provider.value})이 같은 계열입니다. "
            f"독립 채점 위반 — 채점은 작성과 다른 provider 여야 합니다."
        )
    if scorer_role not in SCORING_ROLES:
        raise BackboneSeparationError(f"{scorer_role.value} 은 채점 역할이 아닙니다.")


def separation_ok() -> bool:
    """전체 배치가 작성≠채점 계열분리를 만족하는지(전 작성역할 vs 채점)."""
    scorer = resolve(Role.SCORING)
    for wr in WRITER_ROLES:
        if resolve(wr).provider is scorer.provider:
            return False
    return True


# ════════════════════════════════════════════════════════════════════
# 단일 호출 어댑터 (stdlib urllib — SDK 불필요)
# ════════════════════════════════════════════════════════════════════
@dataclass
class CallResult:
    role: Role
    provider: Provider
    model: str
    ok: bool
    text: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    error: str = ""


def _http_json(url: str, headers: dict, payload: dict, timeout: int = 60):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def call(role: Role, prompt: str, *, max_tokens: int = 64, env: dict | None = None) -> CallResult:
    """역할 백본을 1회 호출한다(최소 토큰). provider 별 엔드포인트 분기."""
    env = env if env is not None else load_env()
    bb = resolve(role, env)
    key = os.environ.get(PROVIDER_ENV_KEY[bb.provider]) or env.get(PROVIDER_ENV_KEY[bb.provider])
    if not key:
        return CallResult(role, bb.provider, bb.model, ok=False,
                          error=f"missing key {PROVIDER_ENV_KEY[bb.provider]}")
    try:
        if bb.provider is Provider.ANTHROPIC:
            base = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/")
            res = _http_json(
                f"{base}/v1/messages",
                {"x-api-key": key, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
                {"model": bb.model, "max_tokens": max_tokens,
                 "messages": [{"role": "user", "content": prompt}]},
            )
            text = "".join(b.get("text", "") for b in res.get("content", []))
            u = res.get("usage", {})
            return CallResult(role, bb.provider, bb.model, ok=True, text=text,
                              input_tokens=u.get("input_tokens", 0),
                              output_tokens=u.get("output_tokens", 0))
        if bb.provider is Provider.OPENAI:
            res = _http_json(
                "https://api.openai.com/v1/chat/completions",
                {"Authorization": f"Bearer {key}", "content-type": "application/json"},
                {"model": bb.model, "max_completion_tokens": max_tokens,
                 "messages": [{"role": "user", "content": prompt}]},
            )
            text = res["choices"][0]["message"]["content"]
            u = res.get("usage", {})
            return CallResult(role, bb.provider, bb.model, ok=True, text=text or "",
                              input_tokens=u.get("prompt_tokens", 0),
                              output_tokens=u.get("completion_tokens", 0))
        if bb.provider is Provider.GOOGLE:
            url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
                   f"{bb.model}:generateContent?key={key}")
            res = _http_json(url, {"content-type": "application/json"},
                             {"contents": [{"parts": [{"text": prompt}]}],
                              "generationConfig": {"maxOutputTokens": max_tokens}})
            cand = res.get("candidates", [{}])
            parts = cand[0].get("content", {}).get("parts", []) if cand else []
            text = "".join(p.get("text", "") for p in parts)
            u = res.get("usageMetadata", {})
            return CallResult(role, bb.provider, bb.model, ok=True, text=text,
                              input_tokens=u.get("promptTokenCount", 0),
                              output_tokens=u.get("candidatesTokenCount", 0))
    except urllib.error.HTTPError as e:
        return CallResult(role, bb.provider, bb.model, ok=False,
                          error=f"HTTP {e.code}: {e.read()[:200].decode(errors='replace')}")
    except Exception as e:
        return CallResult(role, bb.provider, bb.model, ok=False,
                          error=f"{type(e).__name__}: {str(e)[:200]}")
    return CallResult(role, bb.provider, bb.model, ok=False, error="unknown provider")
