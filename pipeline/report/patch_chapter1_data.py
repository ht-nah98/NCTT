#!/usr/bin/env python3
"""Bổ sung dữ liệu cho chương I của _web/ho-so.html.

Sáu việc, sinh ra từ đợt review chương I:
  1. dur_split  — bảng độ dài: view/ngày vs doanh thu-tương-đối, và kiểm
                  trong-từng-kênh. Việc #3 hiện khuyên 1–3 giờ mà không nói
                  video ngắn ăn view gấp 2,15x.
  2. pen_split  — tách khoản phạt −2 thành hai nửa. Chỉ nửa «trùng lặp» gỡ
                  được; nửa «chủ đề tôn giáo» thì không.
  3. dup_ch     — tên 5 kênh có ≥30% video trùng, để tra tận nơi.

Chạy sau inject_positioning_web.py.
"""
import json, pathlib, re
import numpy as np, pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
N = ROOT / "niches/christian-blues"
WEB = ROOT / "_web/ho-so.html"
CRAWL = pd.Timestamp("2026-08-13", tz="UTC")


def load():
    P = N / "00_input/processed"
    v = pd.read_parquet(P / "videos.parquet")
    s = pd.read_parquet(P / "video_stats.parquet")
    ch = pd.read_parquet(P / "channels.parquet")
    v = v.merge(s[["video_id", "view_count"]], on="video_id", how="left")
    v = v.merge(ch[["channel_id", "handle"]], on="channel_id", how="left")
    v["age"] = (CRAWL - v.published_at).dt.days.clip(lower=1)
    v["vpd"] = v.view_count / v.age
    v["min"] = v.duration_sec / 60
    return v[v.age >= 60].copy(), v


def dur_split(M):
    """Ngắn ăn view, dài ăn doanh thu — hai mục tiêu khác nhau."""
    bands = [(0, 10, "Dưới 10 phút"), (10, 60, "10–60 phút"),
             (60, 1e9, "Trên 1 giờ")]
    rows = []
    for lo, hi, nm in bands:
        g = M[(M["min"] >= lo) & (M["min"] < hi)]
        # YouTube cho ~1 điểm chèn quảng cáo mỗi 8 phút với video trên 8 phút
        slots = np.maximum(1, g["min"] // 8)
        rows.append(dict(nm=nm, n=int(len(g)),
                         vpd=round(float(g.vpd.median()), 2),
                         slot=int(slots.median()),
                         rel=round(float((g.vpd * slots).median()), 1)))
    # kiểm trong từng kênh: cùng một kênh, ngắn có thắng dài không
    pairs = []
    for _, g in M.groupby("channel_id"):
        s = g[g["min"] < 10]
        l = g[g["min"] >= 60]
        if len(s) >= 5 and len(l) >= 5 and l.vpd.median() > 0:
            pairs.append(s.vpd.median() / l.vpd.median())
    return dict(bands=rows, n_ch=len(pairs),
                n_better=int(sum(1 for x in pairs if x > 1)),
                within=round(float(np.median(pairs)), 2) if pairs else None,
                ratio=round(rows[0]["vpd"] / rows[2]["vpd"], 2),
                rev_ratio=round(rows[2]["rel"] / rows[0]["rel"], 1))


def pen_split():
    """Khoản phạt −2 gồm hai nửa, chỉ một nửa gỡ được."""
    df = pd.read_csv(N / "07_monetization/02_risk_register.csv")
    out = []
    for x in df[df.penalty != 0].itertuples():
        fixable = "trùng lặp" in x.risk.lower() or "reused" in x.risk.lower()
        out.append(dict(nm=str(x.risk), p=int(x.penalty),
                        ev=str(x.evidence), why=str(x.detail),
                        fix=bool(fixable)))
    return out


def dup_channels(all_v):
    """5 kênh có ≥30% video trùng tiêu đề chéo kênh — nêu tên để tra được."""
    v = all_v.copy()
    v["tn"] = v.title.astype(str).str.lower().str.strip()
    g = v.groupby("tn").channel_id.nunique()
    v["dup"] = v.tn.isin(set(g[g >= 2].index))
    r = v.groupby("handle").agg(n=("video_id", "size"), d=("dup", "sum"))
    r["pct"] = 100 * r.d / r.n
    hi = r[(r.pct >= 30) & (r.n >= 10)].sort_values("pct", ascending=False)
    return [dict(ch=str(x.Index), d=int(x.d), n=int(x.n),
                 pct=round(float(x.pct), 1)) for x in hi.itertuples()]


def main():
    M, allv = load()
    extra = dict(dur=dur_split(M), pen=pen_split(), dupch=dup_channels(allv))

    html = WEB.read_text(encoding="utf-8")
    m = re.search(r'<script id="P4" type="application/json">(.*?)</script>',
                  html, re.S)
    P = json.loads(m.group(1))
    P["x"] = extra                      # gom vào một khoá, không đụng khoá cũ
    blob = json.dumps(P, ensure_ascii=False).replace("</", "<\\/")
    html = html[:m.start(1)] + blob + html[m.end(1):]
    WEB.write_text(html, encoding="utf-8")

    d = extra["dur"]
    print(f"✓ dur: ngắn {d['bands'][0]['vpd']} vs dài {d['bands'][2]['vpd']} "
          f"= {d['ratio']}× view · doanh thu ngược lại {d['rev_ratio']}×")
    print(f"      trong từng kênh {d['n_better']}/{d['n_ch']} kênh ngắn thắng, "
          f"trung vị {d['within']}×")
    print(f"✓ pen: {len(extra['pen'])} khoản phạt, "
          f"{sum(1 for x in extra['pen'] if x['fix'])} gỡ được")
    print(f"✓ dupch: {len(extra['dupch'])} kênh trùng nặng")


if __name__ == "__main__":
    main()
