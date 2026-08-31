#!/usr/bin/env python3
"""Bổ sung dữ liệu cho chương II · Khán giả.

Sinh ra từ đợt review chương II. Ba việc:

  1. wordtest — kiểm 7 từ trong bảng «khoảng cách ngôn ngữ» bằng LIKE.
     Chỉ số khoảng cách hiện đo «khán giả viết bao nhiêu lần ÷ tiêu đề dùng
     bao nhiêu». Từ đệm như «amen» tự động được tỉ lệ cao mà không mang
     sức mạnh nào. Phải kiểm bằng like mới biết từ nào thật.

  2. sig_words — đối chứng: từ ĐÃ qua kiểm định ở trang 04 thì bao nhiêu.

  3. cover — độ phủ của 4 nhóm khán giả và 8 bối cảnh. Con số «13,5% nghe
     lúc cầu nguyện» là 13,5% TỔNG bình luận, nhưng chỉ 22,2% bình luận có
     nêu bối cảnh -> trong nhóm có nêu, cầu nguyện chiếm 61%.

Chạy sau patch_chapter1_data.py.
"""
import json, pathlib, re, sys
import numpy as np
from scipy import stats

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_positioning_cards as B

WEB = pathlib.Path(__file__).resolve().parent.parent.parent / "_web/ho-so.html"


def like_test(pat, regex=True):
    h = B.CM[B.CM.text.str.lower().str.contains(pat, regex=regex)]
    if len(h) < 15:
        return None
    rest = B.CM[~B.CM.index.isin(h.index)]
    p = float(stats.mannwhitneyu(h.like_count, rest.like_count).pvalue)
    med = float(h.like_count.median())
    return dict(n=int(len(h)), like=round(med, 1),
                lift=round(med / B.BASE_LIKE, 2), p=p)


def title_test(word):
    """Video có từ đó trong tiêu đề chạy thế nào — mẫu thường rất nhỏ."""
    m = B.M.copy()
    m["hit"] = m.title.astype(str).str.lower().str.contains(
        r"\b" + word + r"\b", regex=True)
    a, b = m[m.hit], m[~m.hit]
    if len(a) < 8:
        return dict(n=int(len(a)), vpd=None, lift=None, p=None)
    p = float(stats.mannwhitneyu(a.vpd.dropna(), b.vpd.dropna()).pvalue)
    return dict(n=int(len(a)), vpd=round(float(a.vpd.median()), 2),
                lift=round(float(a.vpd.median() / b.vpd.median()), 2), p=p)


def main():
    html = WEB.read_text(encoding="utf-8")
    m = re.search(r'<script id="P4" type="application/json">(.*?)</script>',
                  html, re.S)
    P = json.loads(m.group(1))

    # 1) kiểm 7 từ của bảng khoảng cách ngôn ngữ
    words = []
    for v in P["voice"][:7]:
        w = str(v["w"])
        lt = like_test(r"\b" + w + r"\b")
        if not lt:
            continue
        words.append(dict(w=w, c=int(v["c"]), t=int(v["t"]),
                          r=round(float(v["r"])), **lt,
                          title=title_test(w)))

    # 2) đối chứng: tín hiệu đã qua kiểm định
    sigw = []
    for w, label in [("finally", "finally / at last"),
                     ("never heard", "never heard"),
                     ("first time i", "first time I heard")]:
        lt = like_test(w, regex=False)
        if lt:
            sigw.append(dict(w=label, **lt))

    # 3) độ phủ
    pers_cov = round(sum(x["p"] for x in P["pers"]), 1)
    ctx = sorted(P["ctx"], key=lambda x: -x["n"])
    ctx_cov = round(sum(x["p"] for x in ctx), 1)
    ctx_n = sum(x["n"] for x in ctx)
    top = ctx[0]

    P["x2"] = dict(
        words=words, sigw=sigw,
        cover=dict(pers=pers_cov, ctx=ctx_cov, ctx_n=ctx_n,
                   top_k=top["k"], top_n=int(top["n"]),
                   top_share=round(100 * top["n"] / ctx_n, 1),
                   second=ctx[1]["k"], second_n=int(ctx[1]["n"])),
        base_like=B.BASE_LIKE)

    blob = json.dumps(P, ensure_ascii=False).replace("</", "<\\/")
    html = html[:m.start(1)] + blob + html[m.end(1):]
    WEB.write_text(html, encoding="utf-8")

    print("Bảng «khoảng cách ngôn ngữ» — kiểm lại bằng LIKE:")
    for w in words:
        print(f"  {w['w']:12} khoảng cách {w['r']:4}× · like {w['like']:5} "
              f"= {w['lift']}× nền · p={w['p']:.1e}")
    print("\nĐối chứng — tín hiệu đã qua kiểm định:")
    for w in sigw:
        print(f"  {w['w']:20} n={w['n']:4} like {w['like']:5} = {w['lift']}×")
    c = P["x2"]["cover"]
    print(f"\n4 nhóm phủ {c['pers']}% · 8 bối cảnh phủ {c['ctx']}%")
    print(f"  trong số có nêu bối cảnh, {c['top_k']} chiếm {c['top_share']}%")


if __name__ == "__main__":
    main()
