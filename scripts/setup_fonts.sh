#!/usr/bin/env bash
# scripts/setup_fonts.sh — 한글 폰트(NanumGothic) 확보.
#
# 폰트는 repo 의 assets/fonts/ 에 보존된다(OFL, 재배포 가능). 이 스크립트는
# 누락 시 시스템 폰트에서 복사하거나 apt 로 설치해 채운다. 정상 보존 시 no-op.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/assets/fonts"
mkdir -p "$DIR"
SYS="/usr/share/fonts/truetype/nanum"

have() { [ -s "$DIR/NanumGothic.ttf" ] && [ -s "$DIR/NanumGothicBold.ttf" ]; }

if have; then
  echo "fonts ok (present): $DIR"
  exit 0
fi

# 1) 시스템에 이미 있으면 복사
if [ -s "$SYS/NanumGothic.ttf" ]; then
  cp "$SYS/NanumGothic.ttf" "$SYS/NanumGothicBold.ttf" "$DIR/"
  echo "fonts copied from system: $DIR"; exit 0
fi

# 2) apt 로 설치 후 복사
if command -v apt-get >/dev/null 2>&1; then
  apt-get update -y >/dev/null 2>&1 || true
  apt-get install -y fonts-nanum >/dev/null 2>&1 || true
  if [ -s "$SYS/NanumGothic.ttf" ]; then
    cp "$SYS/NanumGothic.ttf" "$SYS/NanumGothicBold.ttf" "$DIR/"
    echo "fonts installed via apt: $DIR"; exit 0
  fi
fi

echo "ERROR: could not obtain NanumGothic fonts" >&2
exit 1
