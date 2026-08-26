"""STEP_03b · CHUẨN SẢN XUẤT — lấp ba dòng trống ở §5.5 của hồ sơ ngách.

VÌ SAO CÓ BƯỚC NÀY: template hồ sơ yêu cầu bảng «công thức đang thắng» 7 dòng.
Ta đã có 4 (độ dài, thumbnail, tiêu đề, có lời). Ba dòng còn thiếu — TẦN SUẤT
ĐĂNG, TRACKLIST, CẤU TRÚC ĐỘ DÀI — đều tính được từ dữ liệu sẵn có, chỉ là
chưa ai tính.

QUY TẮC: mỗi chỉ số ở đây phải RÀNG BUỘC MỘT QUYẾT ĐỊNH sản xuất. Chỉ số chỉ
để biết thì không đưa vào (nguyên tắc số 1 của template).

BẪY ĐÃ CHẶN — độ dài video:
  Gộp toàn ngách: video <10 phút có VPD 15,7 vs 30-60 phút 7,6 → tưởng như
  "làm video ngắn thắng gấp đôi". Kiểm trong từng kênh (bỏ Shorts <1,1 phút):
  **12/24 kênh dài tốt hơn, lift trung vị 0,95** — chia đôi, không có quy luật.
  Con số 15,7 là hiệu ứng GỘP KÊNH, không phải tác dụng của độ dài (T47).

Đầu ra: <N>/03_competitor/PRODUCTION_NORMS.json
"""
import json, sys
import numpy as np
import pandas as pd

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
from _common import niche_paths

N, P, OUT = niche_paths("03_competitor")

MATURE_DAYS = 60      # video chưa chín thì VPD chưa ổn định
SHORTS_MIN = 1.1      # dưới mức này là Shorts — luật phân phối khác hẳn
TOP_K = 10            # số kênh coi là "nhóm dẫn đầu"
MIN_PER_SIDE = 5      # mỗi bên cần ≥5 video mới so trong kênh được


def within_channel_split(df, mask_col, val_col="vpd", ch_col="handle"):
    """So hai nhóm TRONG từng kênh. Trả (n_kênh, n_kênh_nhóm-True-tốt-hơn, lift TV)."""
    lifts = []
    for _, g in df.groupby(ch_col):
        a = g[g[mask_col]][val_col]
        b = g[~g[mask_col]][val_col]
        if len(a) >= MIN_PER_SIDE and len(b) >= MIN_PER_SIDE:
            mb = b.median()
            lifts.append(a.median() / mb if mb > 0 else np.nan)
    lifts = [x for x in lifts if np.isfinite(x)]
    if not lifts:
        return 0, 0, None
    return len(lifts), int(sum(1 for x in lifts if x > 1)), float(np.median(lifts))


def main():
    v = pd.read_parquet(P/"videos_enriched.parquet")
    v["published_at"] = pd.to_datetime(v.published_at, errors="coerce", utc=True)
    v["min"] = v.duration_sec / 60
    v["desc"] = v.description.fillna("")
    # tracklist = mô tả có ≥3 mốc thời gian dạng 0:00
    v["n_ts"] = v.desc.str.count(r"\b\d{1,2}:\d{2}\b")
    v["has_tracklist"] = v.n_ts >= 3

    top = v.groupby("handle").view_count.sum().nlargest(TOP_K).index
    v["is_top"] = v.handle.isin(top)
    mature = v[v.age_days >= MATURE_DAYS].copy()
    no_shorts = mature[mature["min"] >= SHORTS_MIN].copy()

    # ── 1. TẦN SUẤT ĐĂNG (90 ngày gần nhất) ──
    cut = v.published_at.max() - pd.Timedelta(days=90)
    recent = v[v.published_at >= cut]
    per_wk = recent.groupby("handle").size() / (90 / 7)
    cadence = {
        "median_all": round(float(per_wk.median()), 2),
        "median_top": round(float(per_wk[per_wk.index.isin(top)].median()), 2),
        "median_rest": round(float(per_wk[~per_wk.index.isin(top)].median()), 2),
        "p25": round(float(per_wk.quantile(.25)), 2),
        "p75": round(float(per_wk.quantile(.75)), 2),
        "n_channels": int(len(per_wk)),
        "window_days": 90,
    }

    # ── 2. TRACKLIST ──
    k, better, lift = within_channel_split(mature, "has_tracklist")
    tl = {
        "pct_all": round(float(v.has_tracklist.mean() * 100), 1),
        "pct_top": round(float(v[v.is_top].has_tracklist.mean() * 100), 1),
        "pct_rest": round(float(v[~v.is_top].has_tracklist.mean() * 100), 1),
        "vpd_with": round(float(mature[mature.has_tracklist].vpd.median()), 2),
        "vpd_without": round(float(mature[~mature.has_tracklist].vpd.median()), 2),
        "within_channel": {"n_channels": k, "n_better": better,
                           "median_lift": round(lift, 2) if lift else None},
        # nhóm dẫn đầu dùng ÍT hơn phần còn lại → không phải yếu tố thắng
        "verdict": ("KHÔNG PHẢI YẾU TỐ THẮNG"
                    if lift is None or lift <= 1.05 else "ĐÁNG THỬ"),
    }

    # ── 3. ĐỘ DÀI ──
    bands = [0, SHORTS_MIN, 10, 30, 60, 120, 9999]
    labels = ["Shorts (<1,1ph)", "1–10 phút", "10–30 phút", "30–60 phút",
              "1–2 giờ", "trên 2 giờ"]
    mature["band"] = pd.cut(mature["min"], bands, labels=labels)
    by_band = (mature.groupby("band", observed=True)
               .agg(n=("vpd", "size"), vpd_median=("vpd", "median"),
                    view_median=("view_count", "median")).reset_index())
    no_shorts["is_long"] = no_shorts["min"] >= 30
    kL, bL, liftL = within_channel_split(no_shorts, "is_long")
    duration = {
        "by_band": [{"band": str(r.band), "n": int(r.n),
                     "vpd_median": round(float(r.vpd_median), 2),
                     "view_median": int(r.view_median)}
                    for r in by_band.itertuples()],
        "median_min_all": round(float(mature["min"].median()), 1),
        "median_min_top": round(float(mature[mature.is_top]["min"].median()), 1),
        "long_vs_short_within": {"n_channels": kL, "n_better_long": bL,
                                 "median_lift": round(liftL, 2) if liftL else None},
        # Gộp thì ngắn thắng đậm; trong kênh thì hòa → là hiệu ứng kênh
        "verdict": ("KHÔNG CÓ QUY LUẬT — chọn độ dài theo định vị, "
                    "không theo kỳ vọng thuật toán"
                    if liftL and 0.8 <= liftL <= 1.25 else "CÓ XU HƯỚNG"),
        "naive_trap": {
            "short_vpd": round(float(mature[mature["min"] < 10].vpd.median()), 2),
            "long_vpd": round(float(mature[mature["min"] >= 30].vpd.median()), 2),
            "note": "chênh này BIẾN MẤT khi kiểm trong từng kênh",
        },
    }

    res = {"niche": N.name, "cadence": cadence, "tracklist": tl,
           "duration": duration,
           "_meta": {
               "mature_days": MATURE_DAYS, "shorts_threshold_min": SHORTS_MIN,
               "top_k_channels": TOP_K,
               "method": "so trong từng kênh (chống nghịch lý Simpson); "
                         "VPD = view/ngày trên video đã chín ≥60 ngày",
               "limits": ["tracklist nhận diện bằng đếm mốc thời gian trong mô tả — "
                          "có thể sót định dạng lạ",
                          "tần suất đăng tính trên 90 ngày, chưa phản ánh mùa vụ"],
           }}
    (OUT/"PRODUCTION_NORMS.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ {OUT/'PRODUCTION_NORMS.json'}")
    print(f"   nhịp đăng: {cadence['median_top']} video/tuần (top) vs "
          f"{cadence['median_rest']} (còn lại)")
    print(f"   tracklist: {tl['pct_top']}% top vs {tl['pct_rest']}% còn lại "
          f"→ {tl['verdict']}")
    print(f"   độ dài: {bL}/{kL} kênh dài tốt hơn, lift {duration['long_vs_short_within']['median_lift']} "
          f"→ {duration['verdict']}")


if __name__ == "__main__":
    main()
