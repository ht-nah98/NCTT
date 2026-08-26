#!/usr/bin/env bash
# Mở bản mô phỏng sản phẩm trên trình duyệt máy này.
cd "$(dirname "$0")" || exit 1
PORT="${1:-8080}"
while lsof -i:"$PORT" >/dev/null 2>&1; do PORT=$((PORT+1)); done
URL="http://localhost:$PORT/"
echo "  Bàn dữ liệu + Ba trạm  →  $URL"
echo "  Dừng: Ctrl + C"
( sleep 1; xdg-open "$URL" >/dev/null 2>&1 || true ) &
exec python3 -m http.server "$PORT" --bind 127.0.0.1
