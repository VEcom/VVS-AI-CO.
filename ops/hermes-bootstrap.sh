#!/usr/bin/env bash
# ops/hermes-bootstrap.sh — 헤르메스 에이전트 격리 설치 (재현 가능, 핀 고정).
#
# VVS-AI-CO는 거대한 Hermes 트리(4189 파일)를 벤더링하지 않고, 이 스크립트로
# 핀 고정된 커밋을 clone + 격리(venv) 설치한다. B-0에서 검증된 절차이다.
#
# 검증 결과(2026-05-29): hermes-agent 0.15.1, 최상위 모듈 `import batch_runner` OK
# (batch_runner 는 pyproject py-modules 의 최상위 모듈이다 — hermes.batch 아님).
#
# 사용법:
#   bash ops/hermes-bootstrap.sh [설치경로]
#   (기본 설치경로: $HOME/hermes-agent)
set -euo pipefail

HERMES_REPO="https://github.com/NousResearch/hermes-agent"
HERMES_PIN="689ef5e233980f5d5a32080e959f44c8991dd03a"   # 검증된 핀
DEST="${1:-$HOME/hermes-agent}"

echo "[bootstrap] Hermes -> ${DEST} (pin ${HERMES_PIN:0:7})"

if [ ! -d "${DEST}/.git" ]; then
  git clone "${HERMES_REPO}" "${DEST}"
fi
git -C "${DEST}" fetch --depth 1 origin "${HERMES_PIN}" || git -C "${DEST}" fetch origin
git -C "${DEST}" checkout -q "${HERMES_PIN}"

# 격리 설치 + import 스모크 테스트 (Hermes 자체 install.sh 사용)
cd "${DEST}"
bash scripts/install.sh

# install.sh 는 venv 를 ${DEST}/venv 에 만든다 (.venv 아님).
echo "[bootstrap] done — venv: ${DEST}/venv"
echo "[bootstrap] verify: (cd ${DEST} && venv/bin/python -c 'import batch_runner; print(\"batch_runner OK\")')"
( cd "${DEST}" && venv/bin/python -c "import batch_runner; print('[bootstrap] batch_runner import OK')" )
