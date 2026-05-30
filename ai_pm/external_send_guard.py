"""ai_pm/external_send_guard.py — 절대선 #2: 외부 발송 차단.

학습(Phase 0) 모드에서 외부 발송을 차단한다. Hermes
`gateway/platforms/base.py:BasePlatformAdapter.send(chat_id, content, ...)` 를
서브클래싱/믹스인해 학습 모드 시 sandbox.no_external_send 로 막는다.

VVS-AI-CO 안에 두어 영구 보존하며, 어떤 어댑터든 이 믹스인을 얹으면 학습
모드에서 실제 외부 send 에 도달하지 못한다.
"""

from __future__ import annotations

from .sandbox import ExternalSendBlocked, no_external_send  # noqa: F401


class GuardedExternalSendMixin:
    """플랫폼 어댑터용 믹스인.

    `learning_mode` 가 True 이면 send 가 외부로 나가기 전에 차단된다.
    MRO 상 실제 어댑터(super)의 send 보다 앞에 두어야 한다::

        class GuardedTelegram(GuardedExternalSendMixin, TelegramAdapter):
            learning_mode = True

    Hermes 의 send 는 async 이므로 async 로 정의한다.
    """

    learning_mode: bool = True

    async def send(self, chat_id, content, metadata=None, **kwargs):  # noqa: D401
        if self.learning_mode:
            # 절대선 #2 — Phase 0 외부 발송 금지. super().send 에 도달 불가.
            no_external_send(chat_id=chat_id, content=content)
        return await super().send(chat_id, content, metadata=metadata, **kwargs)


def guard_external_send(real_send, chat_id, content, *, learning_mode: bool = True, **kw) -> dict:
    """함수형 가드: 학습 모드 시 real_send 미호출.

    반환:
      차단: {"sent": False, "real_fn_called": False, "blocked_reason": str}
      발송: {"sent": True,  "real_fn_called": True, "result": ...}
    """
    if learning_mode:
        try:
            no_external_send(chat_id=chat_id, content=content)
        except ExternalSendBlocked as exc:
            return {
                "sent": False,
                "real_fn_called": False,
                "blocked_reason": str(exc),
            }
    result = real_send(chat_id, content, **kw)
    return {"sent": True, "real_fn_called": True, "result": result}
