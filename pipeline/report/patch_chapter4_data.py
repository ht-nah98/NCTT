#!/usr/bin/env python3
"""Bổ sung dữ liệu cho chương IV · Công thức tái tạo.

Sinh ra từ đợt review chương IV. Bốn việc:

  1. entry   — TỶ LỆ VÀO TOP theo dải thời lượng. Trang 14 đang chứng minh
               «cả 4 dải thành công tương đương» bằng view trung vị CỦA NHÓM
               ĐÃ LỌT TOP — tức đã lọc theo view rồi mới so view (thiên lệch
               sống sót). Kết luận đúng nhưng phép đo sai. Phép đo đúng là:
               trong toàn bộ video mỗi dải, bao nhiêu % lọt được vào top.

  2. cadence — «đăng dày gấp 5,3x tổng view» phần lớn là phép nhân: đăng
               nhiều video hơn thì tổng view cao hơn. Tách ra hai con số:
               tổng view (hệ quả) và view mỗi video (đòn bẩy thật).

  3. mature  — % video đã đủ 60 ngày của 8 kênh tham chiếu. Kênh trẻ có
               nhiều video chưa kịp tích view -> view/video bị tính THIẾU
               (bẫy maturation, bài học L1).

  4. sample  — cỡ mẫu của mô hình kênh (12/53) và của playbook (41/53).

Chạy sau patch_chapter3_data.py.
"""
import json, pathlib, re, sys
import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_positioning_cards as B

WEB = pathlib.Path(__file__).resolve().parent.parent.parent / "_web/ho-so.html"


def f(x, nd=2):
    if x is None:
        return None
    x = float(x)
    return None if (np.isnan(x) or np.isinf(x)) else round(x, nd)


def entry_rate(bands, thresh):
    """Tỷ lệ video mỗi dải lọt được vào top — phép đo KHÔNG bị thiên lệch.

    Khác với «view trung vị của nhóm đã lọt top»: phép đo đó lọc theo view
    trước rồi mới so view, nên mọi nhóm đều trông giống nhau.
    """
    M = B.M.copy()
    M["min"] = M.duration_sec / 60
    out = []
    for lo, hi, nm in bands:
        g = M[(M["min"] >= lo) & (M["min"] < hi)]
        if not len(g):
            continue
        w = g[g.view_count >= thresh]
        out.append(dict(nm=nm, n=int(len(g)), n_top=int(len(w)),
                        rate=f(100 * len(w) / len(g)),
                        vpd=f(g.vpd.median(), 1),
                        view_top=int(w.view_count.median()) if len(w) else None))
    rates = [x["rate"] for x in out]
    return dict(bands=out, thresh=int(thresh),
                lo=min(rates), hi=max(rates),
                spread=f(max(rates) / min(rates)))


def cadence_split():
    """Tách «tổng view» (hệ quả của số lượng) khỏi «view mỗi video» (đòn bẩy)."""
    rows = []
    for cid, g in B.V.groupby("channel_id"):
        span = (g.published_at.max() - g.published_at.min()).days
        if span < 90 or len(g) < 10:
            continue
        mm = B.M[B.M.channel_id == cid]
        if len(mm) < 5:
            continue
        rows.append((len(g) / (span / 7), mm.view_count.sum(),
                     mm.vpd.median(), len(mm)))
    df = pd.DataFrame(rows, columns=["rate", "tot", "vpd", "n"])
    q25, q75 = df.rate.quantile(.25), df.rate.quantile(.75)
    lo, hi = df[df.rate <= q25], df[df.rate >= q75]
    return dict(
        n_ch=int(len(df)), q25=f(q25, 1), q75=f(q75, 1),
        tot_lo=int(lo.tot.median()), tot_hi=int(hi.tot.median()),
        tot_ratio=f(hi.tot.median() / lo.tot.median(), 1),
        vpd_lo=f(lo.vpd.median(), 1), vpd_hi=f(hi.vpd.median(), 1),
        vpd_ratio=f(hi.vpd.median() / lo.vpd.median()),
        n_lo=int(lo.n.median()), n_hi=int(hi.n.median()))


def maturity(eff):
    """% video đã đủ 60 ngày — kênh trẻ bị tính thiếu view/video."""
    out = {}
    for e in eff:
        h = str(e["h"])
        tot = int((B.V.handle == h).sum())
        mat = int((B.M.handle == h).sum())
        out[h] = dict(n=tot, mat=mat,
                      pct=f(100 * mat / tot, 0) if tot else None)
    return out


def main():
    html = WEB.read_text(encoding="utf-8")
    m = re.search(r'<script id="P4" type="application/json">(.*?)</script>',
                  html, re.S)
    P = json.loads(m.group(1))

    th = P["pb"]["from"]["view_threshold"]
    bands = [(0, 10, "ngắn <10p"), (10, 40, "vừa 10-40p"),
             (40, 80, "dài 40-80p"), (80, 1e9, "rất dài >80p")]
    prof = P["pb"]["strategy"]["profiles"]

    P["x4"] = dict(
        entry=entry_rate(bands, th),
        cad=cadence_split(),
        mature=maturity(P["eff"]),
        n_ch_all=int(P["kpi"]["ch"]),
        n_ch_pb=int(P["pb"]["from"]["n_channels"]),
        n_ch_prof=int(sum(p.get("n_kênh_trong_top12", 0) for p in prof)),
        prof_gap=f(prof[0]["view_mỗi_video"] / prof[1]["view_mỗi_video"]))

    blob = json.dumps(P, ensure_ascii=False).replace("</", "<\\/")
    html = html[:m.start(1)] + blob + html[m.end(1):]
    WEB.write_text(html, encoding="utf-8")

    e = P["x4"]["entry"]
    print(f"TỶ LỆ VÀO TOP (>= {e['thresh']:,} view):")
    for b in e["bands"]:
        print(f"  {b['nm']:14} {b['n']:5} video · {b['n_top']:3} lọt top "
              f"= {b['rate']}%  (vpd toàn dải {b['vpd']})")
    print(f"  -> dải {e['lo']}–{e['hi']}%, chênh {e['spread']}× "
          f"— gần như bằng nhau")
    c = P["x4"]["cad"]
    print(f"\nNHỊP ĐĂNG ({c['n_ch']} kênh):")
    print(f"  thưa ≤{c['q25']}/tuần: tổng {c['tot_lo']:,} · "
          f"vpd {c['vpd_lo']} · {c['n_lo']} video")
    print(f"  dày ≥{c['q75']}/tuần: tổng {c['tot_hi']:,} · "
          f"vpd {c['vpd_hi']} · {c['n_hi']} video")
    print(f"  -> tổng {c['tot_ratio']}× (phần lớn là phép nhân) · "
          f"mỗi video {c['vpd_ratio']}× (đòn bẩy thật)")
    print("\nĐỘ CHÍN 8 kênh tham chiếu:")
    for h, v in P["x4"]["mature"].items():
        flag = "  ⚠ view/video bị tính thiếu" if v["pct"] < 60 else ""
        print(f"  @{h:24} {v['mat']:4}/{v['n']:4} = {v['pct']}%{flag}")
    print(f"\nCỠ MẪU: playbook {P['x4']['n_ch_pb']}/{P['x4']['n_ch_all']} kênh · "
          f"mô hình {P['x4']['n_ch_prof']}/{P['x4']['n_ch_all']} kênh · "
          f"hai mô hình chênh {P['x4']['prof_gap']}×")


if __name__ == "__main__":
    main()
