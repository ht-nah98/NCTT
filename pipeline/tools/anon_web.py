#!/usr/bin/env python3
"""Khử định danh bảng `comment` trong _web/*.html trước khi deploy công khai.

Chỉ động vào bảng comment. Mọi bảng khác (channel/video/thumb/audio/lyrics)
là dữ liệu công khai của YouTube -> giữ nguyên.

  id  : comment_id thật (tra ngược ra tài khoản qua YouTube API) -> c0001...
  par : parent comment_id -> ánh xạ theo CÙNG bảng để giữ cây trả lời
  t   : giữ nguyên văn, chỉ xoá @-nhắc tài khoản thật bên trong
"""
import re, json, sys, pathlib

WEB = pathlib.Path(__file__).resolve().parent.parent.parent / "_web"
# @-nhắc: handle YouTube thật. Cần >=3 chữ số cuối để không đụng "@2x", "@God".
MENTION = re.compile(r'@[A-Za-z0-9_.\-]{3,}[0-9]{3,}')

def scrub_text(s):
    """Xoá @-nhắc tài khoản thật, giữ phần còn lại nguyên vẹn."""
    if not isinstance(s, str):
        return s, 0
    out, n = MENTION.subn('@—', s)
    return out, n

def process(path):
    html = path.read_text(encoding='utf-8')
    m = re.search(r'(<script id="D" type="application/json">)(.*?)(</script>)', html, re.S)
    if not m:
        print(f"  !! {path.name}: không thấy <script id=D>"); return False
    D = json.loads(m.group(2))
    rows = D.get('comment') or []

    # Vòng 1: dựng ánh xạ id thật -> id tổng hợp.
    # Dữ liệu gốc CÓ id lặp (cùng bình luận nằm nhiều dòng). Đánh số theo
    # id-duy-nhất chứ không theo chỉ số dòng, nếu không hai dòng khác nhau
    # sẽ nhận cùng một mã.
    idmap = {}
    for r in rows:
        real = r.get('id')
        if isinstance(real, str) and real and real not in idmap:
            idmap[real] = f"c{len(idmap)+1:04d}"

    n_id = n_par = n_par_orphan = n_mention = 0
    # Vòng 2: thay thế
    for r in rows:
        if isinstance(r.get('id'), str) and r['id'] in idmap:
            r['id'] = idmap[r['id']]; n_id += 1
        p = r.get('par')
        if isinstance(p, str) and p:
            if p in idmap:
                r['par'] = idmap[p]; n_par += 1
            else:
                # cha nằm ngoài mẫu -> vẫn là ID thật, phải bỏ
                r['par'] = ''; n_par_orphan += 1
        for f in ('t', 'vt'):
            if f in r:
                r[f], k = scrub_text(r[f]); n_mention += k

    # Quét toàn bộ JSON: @-nhắc còn sót ở các mảng bình luận KHÔNG có cột id
    # (ba-tram dùng dạng {"t":..,"l":..,"len":..}). Bỏ qua chuỗi base64 ảnh.
    extra = [0]
    def deep(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str):
                    if v.startswith('data:image'):
                        continue
                    o[k], n = scrub_text(v); extra[0] += n
                else:
                    deep(v)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                if isinstance(v, str):
                    if v.startswith('data:image'):
                        continue
                    o[i], n = scrub_text(v); extra[0] += n
                else:
                    deep(v)
    deep(D)
    n_mention += extra[0]

    new = json.dumps(D, ensure_ascii=False, separators=(',', ':'))
    html = html[:m.start(2)] + new + html[m.end(2):]
    path.write_text(html, encoding='utf-8')
    print(f"  ok {path.name}: {n_id} id -> tổng hợp | {n_par} par ánh xạ, "
          f"{n_par_orphan} par mồ côi bỏ | {n_mention} @-nhắc xoá")
    return True

if __name__ == '__main__':
    for name in sys.argv[1:]:
        process(WEB / name)
