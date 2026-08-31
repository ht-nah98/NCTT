#!/usr/bin/env python3
"""Bổ sung dữ liệu cho chương III · Nội dung.

Sinh ra từ đợt review chương III. Bốn việc:

  1. prayer   — phía cung THẬT của khoảng trống «nhạc có lời cho cầu nguyện».
                Trang đang viết «chỉ 1,03% video làm nội dung CÓ LỜI», nhưng
                nguồn _synthesis.json viết «1,03% video làm INSTRUMENTAL và
                thất bại». Con số bị lật ngược nghĩa. Đo lại cho đúng.

  2. within   — kiểm trong-từng-kênh cho 16 chủ đề. Chương III mới chỉ dùng
                lift thô để chấm «tránh», nên scripture bị chấm TRÁNH ở đây
                mà lại là «KHÓ nhưng làm được» ở Phần V. Cùng một phép kiểm
                phải áp cho cả hai phía.

  3. dupcheck — 24 tiêu đề sinh ra có trùng cụm dài với thị trường không.
                Trang 09 có cảnh báo trùng lặp nhưng chưa bao giờ kiểm.

  4. overlap  — 16 chủ đề chồng lấn nhau, tổng share > 100%.

Chạy sau patch_chapter2_data.py.
"""
import json, pathlib, re, sys
from collections import Counter
import numpy as np
from scipy import stats

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_positioning_cards as B

WEB = pathlib.Path(__file__).resolve().parent.parent.parent / "_web/ho-so.html"

# Khuôn nhận diện chủ đề — bám theo 06_keyword/02_theme_scores.csv
THEME_PAT = {
    "old_school": r"old[- ]school|vintage|1950|1960|1970|classic gospel|old time",
    "thanks": r"\bthank(?:ful|s|sgiving)?\b|\bgrateful\b|\bgratitude\b",
    "testimony": r"\btestimon|\bmy story\b|\bwitness\b",
    "presence": r"\bpresence\b|\bholy spirit\b|\banointing\b",
    "peace_rest": r"\bpeace\b|\brest\b|\bcalm\b|\bstill\b",
    "deliverance": r"\bdeliver|\bbreakthrough\b|\bset free\b",
    "grace_mercy": r"\bgrace\b|\bmercy\b|\bforgiv",
    "sorrow_pain": r"\bsorrow\b|\bpain\b|\bhurt\b|\bbroken\b|\btears\b",
    "prayer": r"\bprayer\b|\bpray\b|\bdevotion|\bquiet time\b|\bworship\b",
    "hope_faith": r"\bhope\b|\bfaith\b|\btrust\b|\bbelieve\b",
    "morning": r"\bmorning\b|\bsunrise\b|\bdawn\b",
    "healing": r"\bheal(?:ing|ed)?\b|\brestor",
    "strength": r"\bstrength\b|\bstrong\b|\bcourage\b|\bovercome\b",
    "scripture": r"\bpsalm|\bproverb|\bscripture\b|\bword of god\b|\bbible\b",
    "night_sleep": r"\bnight\b|\bsleep\b|\bmidnight\b|\binsomnia\b",
    "instrumental": r"\binstrumental\b|\bno lyrics\b|\bno vocal|\bkaraoke\b",
}
NOLYRIC = r"\binstrumental\b|\bno lyrics\b|\bno vocal|\bkaraoke\b"


def f(x, nd=2):
    if x is None:
        return None
    x = float(x)
    return None if (np.isnan(x) or np.isinf(x)) else round(x, nd)


def prayer_supply():
    """Phía cung thật: bao nhiêu % video đã làm nhạc CÓ LỜI cho cầu nguyện."""
    M = B.M
    t = M.title.astype(str).str.lower()
    ins = t.str.contains(NOLYRIC, regex=True)
    pray = t.str.contains(THEME_PAT["prayer"], regex=True)
    a, b = M[pray & ~ins], M[pray & ins]
    rest = M[~pray]
    return dict(
        n_all=int(len(M)),
        lyric_n=int(len(a)), lyric_pct=f(100 * len(a) / len(M)),
        lyric_vpd=f(a.vpd.median()),
        ins_n=int(len(b)), ins_pct=f(100 * len(b) / len(M)),
        ins_vpd=f(b.vpd.median()) if len(b) >= 5 else None,
        ins_all_n=int(ins.sum()), ins_all_pct=f(100 * ins.mean()),
        rest_vpd=f(rest.vpd.median()),
        ratio=f(a.vpd.median() / b.vpd.median()) if len(b) >= 5 else None)


def within_channel():
    """Kiểm trong từng kênh cho cả 16 chủ đề — cùng phép kiểm cho mọi phía."""
    out = {}
    for k, pat in THEME_PAT.items():
        m = B.M.copy()
        m["hit"] = m.title.astype(str).str.lower().str.contains(pat, regex=True)
        ratios = []
        for _, g in m.groupby("channel_id"):
            if g.hit.sum() >= 5 and (~g.hit).sum() >= 5:
                base = g[~g.hit].vpd.median()
                if base > 0:
                    ratios.append(g[g.hit].vpd.median() / base)
        if not ratios:
            out[k] = dict(n_ch=0, within=None, n_better=0)
            continue
        out[k] = dict(n_ch=len(ratios), within=f(np.median(ratios)),
                      n_better=int(sum(1 for x in ratios if x > 1)))
    return out


def dup_check(ideas):
    """24 tiêu đề sinh ra có chứa cụm 4–6 từ đã có trên thị trường không."""
    norm = lambda s: re.sub(r"[^a-z0-9 ]", "", str(s).lower()).strip()
    titles = B.V.title.astype(str).map(norm)
    grams = Counter()
    for t in titles:
        w = t.split()
        for k in (4, 5, 6):
            for j in range(len(w) - k + 1):
                grams[" ".join(w[j:j + k])] += 1
    market = set(titles)
    out = []
    for it in ideas:
        n = norm(it["t"])
        exact = n in market
        best = None
        w = n.split()
        for k in (6, 5, 4):
            for j in range(len(w) - k + 1):
                g = " ".join(w[j:j + k])
                c = grams.get(g, 0)
                if c >= 3 and (best is None or c > best[1]):
                    best = (g, c)
            if best:
                break
        out.append(dict(n=it["n"], exact=exact,
                        gram=best[0] if best else None,
                        cnt=best[1] if best else 0))
    return out


def main():
    html = WEB.read_text(encoding="utf-8")
    m = re.search(r'<script id="P4" type="application/json">(.*?)</script>',
                  html, re.S)
    P = json.loads(m.group(1))

    dups = dup_check(P["ideas"])
    P["x3"] = dict(
        prayer=prayer_supply(),
        within=within_channel(),
        dups=dups,
        n_dup=sum(1 for d in dups if d["gram"]),
        n_exact=sum(1 for d in dups if d["exact"]),
        overlap=f(sum(t["sh"] for t in P["themes"]), 1),
        base_vpd=f(B.BASE_VPD))

    blob = json.dumps(P, ensure_ascii=False).replace("</", "<\\/")
    html = html[:m.start(1)] + blob + html[m.end(1):]
    WEB.write_text(html, encoding="utf-8")

    p = P["x3"]["prayer"]
    print("KHOẢNG TRỐNG «nhạc có lời cho cầu nguyện» — phía cung THẬT:")
    print(f"  có lời      : {p['lyric_n']:5} video = {p['lyric_pct']}%  "
          f"VPD {p['lyric_vpd']}")
    print(f"  instrumental: {p['ins_n']:5} video = {p['ins_pct']}%  "
          f"VPD {p['ins_vpd']}")
    print(f"  -> trang đang viết «chỉ 1,03% làm có lời». Thật là "
          f"{p['lyric_pct']}%.")
    print()
    print("KIỂM TRONG TỪNG KÊNH — nhóm bị chấm «tránh»:")
    for k in ("scripture", "instrumental", "night_sleep", "healing"):
        w = P["x3"]["within"][k]
        print(f"  {k:14} {w['n_ch']:3} kênh · trong kênh {w['within']} · "
              f"{w['n_better']}/{w['n_ch']} tốt hơn")
    print()
    print(f"24 TIÊU ĐỀ: {P['x3']['n_exact']} trùng nguyên văn · "
          f"{P['x3']['n_dup']} chứa cụm dài đã có")
    print(f"16 CHỦ ĐỀ chồng lấn: tổng {P['x3']['overlap']}%")


if __name__ == "__main__":
    main()
