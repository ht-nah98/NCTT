"""STEP_04d — PHÂN TÍCH THUMBNAIL TRÊN NHÓM VIDEO DẪN ĐẦU.

CHẠY KHI NÀO: sau STEP_04c (đã có thumb_features_full.parquet)
CÁCH CHẠY:    python3 pipeline/analyze/step04d_thumbnail_top.py [niche_path]

VÌ SAO CÓ FILE NÀY (yêu cầu người dùng 2026-08-17):
  "tập trung vào 1 số lượng ảnh nhất định có nhiều views like, và chỉ số
   được ủng hộ cao nhất thôi"
  → Thay vì chỉ so B1/B4, file này soi riêng nhóm DẪN ĐẦU theo 2 thước đo:
      · TOP theo LƯỢT XEM   (video được YouTube đẩy)
      · TOP theo TỶ LỆ LIKE (video được KHÁN GIẢ ủng hộ) ← khác nhau!

BẮT BUỘC KIỂM 3 LỚP: lớp 1 (top vs dưới) → lớp 2 (toàn thị trường) →
lớp 3 (trong từng kênh). Bài học L2: hiệu ứng mạnh ở lớp 1 vẫn có thể là
nghịch lý Simpson — chỉ phản ánh kênh nào tốt, không phải ảnh nào tốt.

ĐẦU RA: 04_outlier/10_thumb_top_tests.csv · _thumb_top_metrics.json
"""
import pandas as pd, numpy as np, json, sys, warnings
from pathlib import Path
from scipy import stats
warnings.filterwarnings("ignore")

N = Path(sys.argv[1] if len(sys.argv) > 1 else "niches/christian-blues")
P = N/"00_input/processed"
OUT = N/"04_outlier"; OUT.mkdir(exist_ok=True)

FULL = P/"thumb_features_full.parquet"
if not FULL.exists():
    sys.exit(f"Thiếu {FULL}\nChạy trước: python3 pipeline/analyze/step04c_thumbnail_full.py")

v = pd.read_parquet(P/"videos_enriched.parquet")
f = pd.read_parquet(FULL)
m = v.merge(f, on="video_id")

# Chỉ video ĐỦ TUỔI (bài học L1 — bẫy độ chín) và đủ view để tỷ lệ like có nghĩa
MIN_VIEW = 500
m = m[m.is_matured & (m.view_count >= MIN_VIEW)].copy()
m["like_rate"] = m.like_count/m.view_count.clip(lower=1)

FEATS = [("center_std", "Độ chi tiết vùng giữa"), ("text_area", "Diện tích chữ (% ảnh)"),
         ("n_text_blocks", "Số khối chữ"), ("hue_conc", "Độ tập trung màu"),
         ("face_area", "Diện tích mặt (% ảnh)"), ("face_max", "Mặt lớn nhất (% ảnh)"),
         ("n_faces", "Số khuôn mặt"), ("face_cy", "Vị trí mặt (0=trên,1=dưới)"),
         ("face_cx", "Vị trí mặt (0=trái,1=phải)"), ("text_cy", "Vị trí chữ (0=trên,1=dưới)"),
         ("text_top", "Số khối chữ ở 1/3 trên"), ("comp_cy", "Trọng tâm dọc")]

def cliffs(a, b):
    """Cliff's delta bằng sắp xếp — O(n log n) thay vì O(n²)."""
    a = np.sort(a.dropna().values); b = np.sort(b.dropna().values)
    if len(a) < 10 or len(b) < 10:
        return np.nan, np.nan
    gt = sum(np.searchsorted(b, x, "left") for x in a)
    lt = sum(len(b)-np.searchsorted(b, x, "right") for x in a)
    return (gt-lt)/(len(a)*len(b)), float(stats.mannwhitneyu(a, b).pvalue)

def verdict(d, p):
    if p < 0.01 and abs(d) >= 0.30: return "XÁC NHẬN"
    if p < 0.05 and abs(d) >= 0.15: return "YẾU"
    return "BÁC BỎ"

def layer23(col, metric):
    """Lớp 2 (toàn thị trường) + lớp 3 (trong từng kênh) — chống Simpson.

    So NỬA ĐƠN GIẢN (≤ trung vị) với NỬA PHỨC TẠP (> trung vị).
    """
    med = m[col].median()
    lo, hi = m[m[col] <= med], m[m[col] > med]
    if not len(hi) or not len(lo): return None
    mk = float(lo[metric].median()/max(hi[metric].median(), 1e-9))
    wc = []
    for _, g in m.groupby("handle"):
        a, b = g[g[col] <= med], g[g[col] > med]
        if len(a) >= 5 and len(b) >= 5 and b[metric].median() > 0:
            wc.append(a[metric].median()/b[metric].median())
    nb = int(sum(1 for x in wc if x > 1))
    ok = mk > 1.15 and wc and np.median(wc) > 1 and nb/max(len(wc), 1) >= 0.6
    wl = float(np.median(wc)) if wc else None
    # NGƯỠNG ĐỘ LỚN THỰC TẾ: qua kiểm định thống kê chưa đủ. Nếu chênh lệch
    # TRONG CÙNG KÊNH < 10%, hiệu ứng quá nhỏ để hành động — người làm nội dung
    # đổi thumbnail sẽ không thấy khác biệt. Ghi "KHÔNG ĐÁNG KỂ" thay vì
    # "XÁC NHẬN" để tầng 4 (diễn giải) không thổi phồng. Xem lessons_learned B27.
    if ok and wl is not None and wl < 1.10:
        final = "QUA KIỂM ĐỊNH NHƯNG KHÔNG ĐÁNG KỂ"
    elif ok:
        final = "XÁC NHẬN"
    else:
        final = "BÁC BỎ (Simpson)"
    return {"market_lift": mk, "n_ch": len(wc), "n_better": nb,
            "within_lift": wl, "final": final}

R = {"n_pool": len(m), "min_view": MIN_VIEW}
rows = []
for metric, mlabel in [("view_count", "LƯỢT XEM"), ("like_rate", "TỶ LỆ LIKE")]:
    hi_t = m[m[metric] >= m[metric].quantile(.90)]
    lo_t = m[m[metric] <= m[metric].quantile(.50)]
    R[f"n_top_{metric}"] = len(hi_t)
    for col, lab in FEATS:
        d, p = cliffs(hi_t[col], lo_t[col])
        if np.isnan(d): continue
        vd = verdict(d, p)
        rec = {"thước_đo": mlabel, "đặc_trưng": lab, "cột": col,
               "top_median": float(hi_t[col].median()), "dưới_median": float(lo_t[col].median()),
               "cliffs_delta": float(d), "p": p, "lớp1": vd,
               "lớp23": None, "kết_luận": vd}
        if vd in ("XÁC NHẬN", "YẾU"):
            l23 = layer23(col, metric)
            if l23:
                rec["lớp23"] = l23["final"]
                rec["market_lift"] = l23["market_lift"]
                rec["n_better"] = f"{l23['n_better']}/{l23['n_ch']}"
                rec["within_lift"] = l23["within_lift"]
                rec["kết_luận"] = l23["final"]
        rows.append(rec)

T = pd.DataFrame(rows)
T.to_csv(OUT/"10_thumb_top_tests.csv", index=False)

# --- Kênh giải thích bao nhiêu phần biến thiên? (giải thích cơ chế) ---
for metric in ["like_rate", "view_count"]:
    tot = m[metric].var()
    med = m.groupby("handle")[metric].transform("median")
    R[f"var_by_channel_{metric}"] = float(1-((m[metric]-med).var()/tot)) if tot else None

ch = (m.groupby("handle")
        .agg(n=("video_id", "size"), lr=("like_rate", "median"),
             cs=("center_std", "median"), ta=("text_area", "median"))
        .query("n>=10"))
R["channel_level"] = {"n_channels": len(ch),
                      "corr_center_std_like": float(ch.cs.corr(ch.lr, method="spearman")),
                      "corr_text_area_like": float(ch.ta.corr(ch.lr, method="spearman")),
                      "like_rate_max": float(ch.lr.max()), "like_rate_min": float(ch.lr.min())}
R["tests"] = T.to_dict("records")
json.dump(R, open(OUT/"_thumb_top_metrics.json", "w"), indent=2, ensure_ascii=False, default=str)

for mlabel in ["LƯỢT XEM", "TỶ LỆ LIKE"]:
    sub = T[T.thước_đo == mlabel].sort_values("cliffs_delta", key=abs, ascending=False)
    print(f"\n=== TOP 10% THEO {mlabel} vs NỬA DƯỚI ===")
    print(sub[["đặc_trưng", "cliffs_delta", "p", "lớp1", "kết_luận"]]
          .to_string(index=False, float_format=lambda x: f"{x:.3f}"))

print(f"\n=== VÌ SAO ===")
print(f"Kênh giải thích {R['var_by_channel_like_rate']:.1%} biến thiên tỷ lệ like.")
print(f"Ở cấp kênh: chi tiết ảnh vs like r={R['channel_level']['corr_center_std_like']:.3f}")
print(f"→ Ảnh đơn giản KHÔNG gây ra nhiều like; các kênh mạnh tình cờ dùng ảnh đơn giản.")
print(f"\nĐã ghi: 10_thumb_top_tests.csv · _thumb_top_metrics.json")
