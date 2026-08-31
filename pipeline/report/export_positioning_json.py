#!/usr/bin/env python3
"""Xuất dữ liệu 7 định vị ra JSON để trang web dùng.

Vì sao có file này: bản PDF (build_positioning_cards.py) và trang web phải nói
CÙNG một con số. Nếu chép tay sang HTML thì sớm muộn hai bên lệch nhau. Nên ở
đây import thẳng module PDF, lấy đúng kết quả đo của nó, rồi ghi ra JSON.

Sửa số liệu hay bản thi công -> sửa ở build_positioning_cards.py, chạy lại file
này, web tự cập nhật theo.

KHỬ ĐỊNH DANH: repo public. Trích dẫn bình luận giữ nguyên văn nhưng KHÔNG kèm
comment_id (tra ngược ra tài khoản thật qua YouTube API chỉ bằng một lệnh) và
không kèm tên tác giả. @-nhắc tài khoản thật bị xoá.
"""
import json, re, sys, pathlib
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_positioning_cards as B

OUT = B.N / "99_report/_dinh-vi/positioning.json"
MENTION = re.compile(r'@[A-Za-z0-9_.\-]{3,}[0-9]{3,}')


def f(x, nd=2):
    """float an toàn cho JSON — NaN/inf thành None."""
    if x is None:
        return None
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return None if (np.isnan(x) or np.isinf(x)) else round(x, nd)


def videos_of(r, n=14):
    """Bảng video đối chứng — chỉ trường công khai của YouTube."""
    if r["kind"] == "title":
        top = r["videos"].nlargest(n, "vpd")
        worst = r["videos"].nsmallest(6, "vpd")
        pick = lambda df: [
            dict(id=str(x.video_id), t=str(x.title)[:120], ch=str(x.handle),
                 view=int(x.view_count), vpd=f(x.vpd, 1),
                 out=f(x.outlier_ratio, 1))
            for x in df.itertuples()]
        return dict(top=pick(top), worst=pick(worst), sig=False)
    good = r["vids"][r["vids"].n_sig >= 2].head(n)
    return dict(top=[
        dict(id=str(x.video_id), t=str(x.title)[:120], ch=str(x.handle),
             view=int(x.view_count), vpd=f(x.vpd, 1),
             out=f(x.outlier_ratio, 1), sig=int(x.n_sig))
        for x in good.itertuples()],
        worst=[], sig=True, n_all=int(len(r["vids"])), n_good=int(len(good)))


def channels_of(r, n=8):
    src = r["videos"] if r["kind"] == "title" else r["vids"]
    g = (src.groupby("handle")
            .agg(n=("video_id", "size"), vpd=("vpd", "median"),
                 view=("view_count", "sum"))
            .nlargest(n, "vpd").reset_index())
    return [dict(ch=str(x.handle), n=int(x.n), vpd=f(x.vpd, 1),
                 view=int(x.view))
            for x in g.itertuples()]


def quotes_of(r):
    """Trích dẫn đã khử định danh: bỏ comment_id, bỏ tên, xoá @-nhắc."""
    if r["kind"] != "signal":
        return []
    out = []
    for q in r["quotes"]:
        t = " ".join(str(q["text"]).split())[:230]
        out.append(dict(t=MENTION.sub("@—", t), like=int(q["like_count"])))
    return out


def spread_of(df):
    """Biên độ giỏi–dở: cùng định vị nhưng thực thi khác nhau."""
    v = df.vpd.dropna()
    if len(v) < 8:
        return None
    return dict(p10=f(v.quantile(.10), 1), p25=f(v.quantile(.25), 1),
                p50=f(v.median(), 1), p75=f(v.quantile(.75), 1),
                p90=f(v.quantile(.90), 1), max=f(v.max(), 1),
                ratio=f(v.quantile(.90) / max(v.quantile(.10), .01), 1))


# ── KIỂM CHỨNG NỀN GIẢ ───────────────────────────────────────────────────────
# Vì sao cần: định vị 02/03/04 đo bằng LIKE bình luận, còn 01/05/06/07 đo bằng
# VPD video. Hai thang khác nhau, không được xếp cạnh nhau như thể so được.
#
# Trước khi tin thang LIKE, phải hỏi: một cụm từ VÔ NGHĨA — không mang định vị
# nào — thì lift bao nhiêu? Nếu cụm vô nghĩa cũng cho 5x thì con số 5x của định
# vị thật chẳng chứng minh điều gì.
#
# Đã thử ngược lại với VPD: video có bình luận trong mẫu đã cao hơn 14,7x video
# không có, TRƯỚC KHI xét định vị. Ghép cặp theo số bình luận thì DV-04 còn
# 3,5x — không phân biệt được với "amen" 4,3x. Nên VPD KHÔNG dùng để xếp hạng
# nhóm signal. Chỉ LIKE mới qua được kiểm chứng này.
PLACEBO = [("amen", r"\bamen\b"), ("beautiful", r"\bbeautiful\b"),
           ("thank you", r"\bthank you\b"), ("god bless", r"\bgod bless\b"),
           ("love this", r"\blove this\b")]


def placebo_band():
    """Dải lift của các cụm trung tính — mốc để biết bao nhiêu mới là thật."""
    out = []
    for nm, pat in PLACEBO:
        h = B.CM[B.CM.text.str.lower().str.contains(pat, regex=True)]
        if len(h) < 20:
            continue
        out.append(dict(nm=nm, n=int(len(h)),
                        like=f(h.like_count.median(), 1),
                        lift=f(h.like_count.median() / B.BASE_LIKE)))
    lifts = [x["lift"] for x in out if x["lift"] is not None]
    return dict(items=out, lo=min(lifts), hi=max(lifts))


def comment_bias():
    """Thiên lệch chọn mẫu bình luận — vì sao không so định vị bằng VPD."""
    ids = set(B.CM.video_id)
    a, b = B.M[B.M.video_id.isin(ids)], B.M[~B.M.video_id.isin(ids)]
    return dict(n_with=int(len(a)), n_without=int(len(b)),
                vpd_with=f(a.vpd.median(), 1), vpd_without=f(b.vpd.median(), 1),
                ratio=f(a.vpd.median() / b.vpd.median(), 1))


def sheet_rows(pos, r, n=6):
    """Hàng cho bảng tổng quan: ảnh · link video · link kênh · view.

    Lấy video tiêu biểu nhất của mỗi định vị (theo view/ngày) — đủ để nhìn
    lướt là nhận ra hướng đó trông như thế nào trên YouTube.
    """
    src = r["videos"] if r["kind"] == "title" else r["vids"]
    top = src.nlargest(n, "vpd")
    ids = list(top.video_id)
    thumb = (B.V.set_index("video_id").thumbnail_url.reindex(ids)
              .fillna("").to_dict())
    ch = B.pd.read_parquet(
        B.N / "00_input/processed/channels.parquet")[["handle", "channel_id",
                                                      "subscriber_count"]]
    ch = ch.drop_duplicates("handle").set_index("handle")
    out = []
    for x in top.itertuples():
        h = str(x.handle)
        out.append(dict(
            vid=str(x.video_id), t=str(x.title)[:110],
            th=thumb.get(str(x.video_id), ""),
            ch=h, cid=str(ch.channel_id.get(h, "")),
            subs=int(ch.subscriber_count.get(h, 0) or 0),
            view=int(x.view_count), vpd=f(x.vpd, 1),
            out=f(x.outlier_ratio, 1)))
    return out


def main():
    rows, skipped = [], []
    for p in B.POS:
        d = B.build(p)
        if not d:
            skipped.append(p["id"])
            continue
        r, b = d["r"], B.BUILD[p["id"]]
        vdf = r["videos"] if r["kind"] == "title" else r["vids"]
        spec = B.spec_of(vdf)
        cad = B.cadence_of(vdf)

        rows.append(dict(
            id=p["id"], grp=p["grp"], code=p["code"], name=p["name"],
            need=p["need"], verdict=d["verdict"], vcls=d["vcls"],
            label=d["label"], accent=d["accent"], soft=d["soft"],
            grp_desc=d["grp_desc"],
            # ── số đo ──
            kind=r["kind"], n=int(r["n"]), lift=f(r["lift"]), p=r["p"],
            share=f(r.get("share"), 1),
            vpd=f(r.get("vpd")), vpd_other=f(r.get("vpd_other")),
            within=f(r.get("within")), n_ch=int(r.get("n_ch") or 0),
            n_better=int(r.get("n_better") or 0),
            n_channels=int(r.get("n_channels") or 0),
            like=f(r.get("like"), 1), base=f(r.get("base"), 1),
            n_videos=int(r.get("n_videos") or 0),
            # ── quy cách sản xuất, đo riêng cho định vị này ──
            spec=dict(n=spec["n"], n_ch=spec["n_ch"], dur=f(spec["dur"], 1),
                      d25=f(spec["d25"], 0), d75=f(spec["d75"], 0),
                      tlen=f(spec["tlen"], 0), pct_num=f(spec["pct_num"], 0),
                      pct_emoji=f(spec["pct_emoji"], 0),
                      pct_pipe=f(spec["pct_pipe"], 0)),
            cadence=f(cad, 1),
            spread=spread_of(vdf),
            # ── bản thi công ──
            build=dict(idea=b["idea"], customer=b["customer"],
                       persona=b["persona"], thumb=b["thumb"],
                       music=b["music"], struct=b["struct"],
                       title=b["title"], avoid=b["avoid"],
                       first10=b.get("first10")),
            vids=videos_of(r), chans=channels_of(r), quotes=quotes_of(r),
            sheet=sheet_rows(p, r),
        ))

    doc = dict(
        niche="Christian Blues",
        base_vpd=f(B.BASE_VPD), base_like=f(B.BASE_LIKE, 1),
        n_matured=int(len(B.M)), n_comments=int(len(B.CM)),
        crawl="13/08/2026", pos=rows, skipped=skipped,
        placebo=placebo_band(), cmt_bias=comment_bias())

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    print(f"✓ {len(rows)} định vị -> {OUT.name} "
          f"({OUT.stat().st_size/1024:.0f} KB)")
    if skipped:
        print(f"  ⚠ bỏ qua: {skipped}")
    for r in rows:
        print(f"  {r['id']} {r['grp']} {r['verdict']:26} lift {r['lift']}")


if __name__ == "__main__":
    main()
