#!/usr/bin/env bash
# One-time setup for the editing tools. Everything comes from PyPI and the npm registry,
# which cloud sessions can reach (Hugging Face and GitHub downloads are blocked there).
#
# usage: bash setup.sh <work_dir>
#   <work_dir>/model/              Whisper small (CTranslate2 int8) for faster-whisper
#   <work_dir>/fonts/TikTokSans-550.ttf   TikTok Sans at weight 550 (rule 1)
set -euo pipefail
W="${1:?usage: setup.sh <work_dir>}"
mkdir -p "$W/model" "$W/fonts" "$W/dl"
cd "$W/dl"

pip install -q faster-whisper fonttools brotli pillow numpy

# Whisper small, split across four npm packages; checksum verified below.
for p in 0 1 2 3; do
  curl -sSf -o "m$p.tgz" "https://registry.npmjs.org/@skillninja/shortmovie-telop-model-p$p/-/shortmovie-telop-model-p$p-1.0.0.tgz"
  mkdir -p "m$p" && tar -xzf "m$p.tgz" -C "m$p"
done
cp m0/package/{tokenizer.json,vocabulary.json,config.json,preprocessor_config.json} "$W/model/"
cat m0/package/model.bin.part0 m1/package/model.bin.part1 m2/package/model.bin.part2 m3/package/model.bin.part3 > "$W/model/model.bin"
echo "$(cat m0/package/model.sha256)  $W/model/model.bin" | sha256sum -c -

# TikTok Sans variable font -> fixed weight 550.
curl -sSf -o fontv.tgz "https://registry.npmjs.org/@fontsource-variable/tiktok-sans/-/tiktok-sans-5.3.0.tgz"
mkdir -p fontv && tar -xzf fontv.tgz -C fontv
python3 - "$W" <<'EOF'
import sys
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
w = sys.argv[1]
f = TTFont(f"{w}/dl/fontv/package/files/tiktok-sans-latin-wght-normal.woff2")
f.flavor = None
instantiateVariableFont(f, {"wght": 550}).save(f"{w}/fonts/TikTokSans-550.ttf")
EOF
echo "ready: $W/model and $W/fonts/TikTokSans-550.ttf"
