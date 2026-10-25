#!/usr/bin/env bash
# Screenshot slides.html (six 1080x1350 slides stacked) and cut it into slide-1.png ... slide-6.png.
set -euo pipefail
cd "$(dirname "$0")"
BROWSER=$(ls ~/.cache/hyperframes/chrome/*/*/*/chrome-headless-shell 2>/dev/null | head -1)
"$BROWSER" --headless --no-sandbox --hide-scrollbars --force-device-scale-factor=1 --allow-file-access-from-files \
  --virtual-time-budget=3000 --window-size=1080,8100 --screenshot="$PWD/_all.png" "file://$PWD/slides.html" 2>/dev/null
for i in 1 2 3 4 5 6; do
  ffmpeg -v error -y -i _all.png -vf "crop=1080:1350:0:$(( (i - 1) * 1350 ))" "slide-$i.png"
done
rm _all.png
echo "Wrote slide-1.png ... slide-6.png"
