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

# install.sh 의 설치 위치(venv)는 레이아웃에 따라 다르다:
#   - 비루트(기본):  ${DEST}/venv
#   - 루트(리눅스 FHS): /usr/local/lib/hermes-agent/venv  (이때 코드/venv가 거기로 감)
# 두 후보를 모두 확인해 실제 venv python 을 찾는다.
VPY=""
for cand in "${DEST}/venv/bin/python" "/usr/local/lib/hermes-agent/venv/bin/python"; do
  if [ -x "$cand" ]; then VPY="$cand"; break; fi
done

if [ -z "$VPY" ]; then
  echo "[bootstrap] WARN: venv python 을 못 찾음 — hermes --version 으로만 확인" >&2
  hermes --version || true
  exit 0
fi

echo "[bootstrap] venv python: ${VPY}"
# batch_runner 는 최상위 모듈이므로 설치 디렉터리에서 import 검증한다.
( cd "$(dirname "$(dirname "$(dirname "$VPY")")")" \
    && "$VPY" -c "import batch_runner; print('[bootstrap] batch_runner import OK ('+batch_runner.__file__+')')" )
