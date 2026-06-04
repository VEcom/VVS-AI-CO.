"""vvs-deliverable-doc — PDF 빌드.

입력 → 블록 조립 → 절대선 게이트 → (통과 시) .pdf 렌더 → as_document 전달.
송출/렌더 함수를 직접 호출하지 않는다. document_pipeline 이 게이트를 강제하며,
위반 시 렌더·전달이 모두 일어나지 않는다(real_fn_called=False, rendered=False).
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ai_pm.document_pipeline import render_and_deliver_document  # noqa: E402

from _common import build_blocks  # noqa: E402


def run(data: dict, real_send_document, *, level: str = "L1", claims=None,
        out_dir=None, filename=None):
    """PDF 산출물을 조립+게이트+렌더+전달. DocumentDelivery 반환."""
    blocks, doc_type = build_blocks(data, level)
    return render_and_deliver_document(
        real_send_document,
        blocks,
        fmt="pdf",
        level=level,
        doc_type=doc_type,
        claims=claims,
        out_dir=out_dir,
        filename=filename,
    )
