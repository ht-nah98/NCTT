#!/usr/bin/env bash
# Dựng lại _web/ho-so.html từ đầu.
#
# QUAN TRỌNG: mọi script dưới đây vá vào chuỗi gốc của ho-so.html. Chạy chúng
# trên file ĐÃ vá sẽ hỏng (assert sẽ bắt được, không âm thầm sai). Nên luôn
# khôi phục về bản gốc trước — bản trước khi thêm Phần V.
#
#   faab48f = commit cuối cùng còn bản ho-so.html chưa vá
#
# Nếu về sau sửa thẳng vào ho-so.html thì phải cập nhật mốc này, hoặc tốt hơn
# là chuyển hẳn phần nội dung gốc thành script sinh ra được.
set -euo pipefail
cd "$(dirname "$0")/../.."

BASE=faab48f
echo "→ khôi phục ho-so.html từ $BASE"
git checkout $BASE -- _web/ho-so.html

echo "→ Phần V · chọn hướng"
python3 pipeline/report/export_positioning_json.py
python3 pipeline/report/inject_positioning_web.py

echo "→ chương I · phán quyết"
python3 pipeline/report/patch_chapter1_data.py
python3 pipeline/report/patch_chapter1_web.py

echo "→ chương II · khán giả"
python3 pipeline/report/patch_chapter2_data.py
python3 pipeline/report/patch_chapter2_web.py

echo "→ kiểm cú pháp"
node pipeline/report/verify_web.js
echo "✅ xong · $(du -h _web/ho-so.html | cut -f1)"
