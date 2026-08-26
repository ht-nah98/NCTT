"""STEP_04b — Phân tích ẢNH THUMBNAIL THẬT (bổ sung cho STEP_04).

CHẠY KHI NÀO: khi đã có file ảnh trong <niche>/00_input/raw/thumbs/*.jpg
CÁCH CHẠY:    python3 pipeline/analyze/step04b_thumbnail.py [niche_path]

KHÁC GÌ STEP_04: STEP_04 chỉ dùng 22 đặc trưng SỐ đã trích sẵn (độ sáng, bão hòa...).
File này phân tích ẢNH THẬT → bắt được thứ số liệu không bắt được:
  - Có mặt người không, bao nhiêu mặt, mặt to hay nhỏ
  - Bố cục: chủ thể ở đâu (trái/giữa/phải, trên/dưới)
  - Chữ: chiếm bao nhiêu diện tích, nằm ở đâu
  - Mức độ giống nhau giữa các kênh (đạo nhái hình ảnh)

VẪN GIỮ NGUYÊN PHƯƠNG PHÁP: so sánh B1 (thắng) vs B4 (đối chứng), kiểm 3 lớp chống Simpson.
"""
import pandas as pd, numpy as np, json, sys, warnings
from pathlib import Path
warnings.filterwarnings("ignore")
try:
    import cv2
    from PIL import Image
except ImportError:
    sys.exit("Cần: pip install opencv-python pillow")
from scipy import stats

N = Path(sys.argv[1] if len(sys.argv) > 1 else "niches/christian-blues")
P = N/"00_input/processed"
THUMBS = N/"00_input/raw/thumbs"
OUT = N/"04_outlier"; OUT.mkdir(exist_ok=True)

if not THUMBS.exists() or not any(THUMBS.glob("*.jpg")):
    sys.exit(f"CHƯA CÓ ẢNH tại {THUMBS}\n"
             f"Đặt file .jpg vào đó (tên file = video_id.jpg) rồi chạy lại.")

s = pd.read_parquet(P/"selected_videos.parquet")
v = pd.read_parquet(P/"videos_enriched.parquet")
B1 = s[s.bucket.str.contains("B1")].assign(grp="B1_thắng")
B4 = s[s.bucket.str.contains("B4")].assign(grp="B4_thua")
d = pd.concat([B1, B4])

# Dùng CHUNG bộ trích đặc trưng của STEP_04c (YuNet + MSER).
# Bản đầu file này dùng Haar cascade → bỏ sót 64% khuôn mặt trên ảnh nghiêng/
# thiếu sáng, và Canny+dilate báo chữ chiếm 90% ảnh. Cả hai đều sai.
# Không nhân bản logic ở hai nơi — sửa một chỗ, cả hai cùng đúng.
import importlib.util as _il
_sp = _il.spec_from_file_location("_t4c", Path(__file__).with_name("step04c_thumbnail_full.py"))
_t4c = _il.module_from_spec(_sp); _sp.loader.exec_module(_t4c)

def analyze(vid):
    """Ủy quyền cho STEP_04c (nguồn sự thật duy nhất của việc trích đặc trưng)."""
    r = _t4c.analyze(vid)
    return None if (r is None or "_error" in r) else r

print(f"Đang phân tích {len(d)} ảnh...")
res = [r for r in (analyze(x) for x in d.video_id) if r]
F = pd.DataFrame(res)
if F.empty: sys.exit("Không đọc được ảnh nào.")
d = d.merge(F, on="video_id", how="inner")
nb1=int((d.grp=="B1_thắng").sum()); nb4=int((d.grp=="B4_thua").sum())
print(f"Đọc thành công {len(d)}/{len(B1)+len(B4)} ảnh (B1={nb1}, B4={nb4})\n")
if nb1 < 30 or nb4 < 30:
    sys.exit(f"DỪNG: cần ≥30 ảnh mỗi nhóm để so sánh có ý nghĩa "
             f"(hiện B1={nb1}, B4={nb4}).\n"
             f"Nguyên nhân thường gặp: thiếu file ảnh, hoặc tên file không khớp video_id.")

R = {"n_analyzed": len(d), "n_B1": int((d.grp=="B1_thắng").sum()),
     "n_B4": int((d.grp=="B4_thua").sum())}

# ================= LỚP 1: so sánh B1 vs B4 =================
def cmp(col, label):
    a = d[d.grp=="B1_thắng"][col].dropna(); b = d[d.grp=="B4_thua"][col].dropna()
    if len(a) < 10 or len(b) < 10: return None
    p = float(stats.mannwhitneyu(a, b, alternative="two-sided").pvalue)
    n1, n2 = len(a), len(b)
    gt = sum((a.values[:,None] > b.values).sum(1)); lt = sum((a.values[:,None] < b.values).sum(1))
    delta = (gt-lt)/(n1*n2)
    return {"feature":label, "B1":float(a.median()), "B4":float(b.median()),
            "p":p, "cliffs_delta":float(delta),
            "verdict":("XÁC NHẬN" if p<0.01 and abs(delta)>=0.30
                       else "YẾU" if p<0.05 and abs(delta)>=0.15 else "BÁC BỎ")}

tests = [t for t in [
    cmp("n_faces","Số khuôn mặt"), cmp("face_area","Diện tích mặt (% ảnh)"),
    cmp("face_cx","Vị trí mặt (0=trái, 1=phải)"),
    cmp("text_area","Diện tích chữ (% ảnh)"), cmp("n_text_blocks","Số khối chữ"),
    cmp("text_cy","Vị trí chữ (0=trên, 1=dưới)"),
    cmp("comp_cx","Trọng tâm ngang"), cmp("comp_cy","Trọng tâm dọc"),
    cmp("center_std","Độ chi tiết vùng giữa"), cmp("hue_conc","Độ tập trung màu"),
    cmp("face_max","Mặt lớn nhất (% ảnh)"), cmp("face_cy","Vị trí mặt (0=trên, 1=dưới)"),
    cmp("text_top","Số khối chữ ở 1/3 trên"),
] if t]
if not tests:
    sys.exit("DỪNG: không đặc trưng nào đủ mẫu để kiểm định (cần ≥10 ảnh mỗi nhóm mỗi đặc trưng).")
T = pd.DataFrame(tests).sort_values("cliffs_delta", key=abs, ascending=False)
T.to_csv(OUT/"08_thumb_visual_tests.csv", index=False)
R["visual_tests"] = T.to_dict("records")

# có mặt hay không — kiểm định tỷ lệ
d["has_face"] = d.n_faces > 0
ca, cb = int(d[d.grp=="B1_thắng"].has_face.sum()), int(d[d.grp=="B4_thua"].has_face.sum())
na, nb = int((d.grp=="B1_thắng").sum()), int((d.grp=="B4_thua").sum())
_, pf = stats.fisher_exact([[ca,na-ca],[cb,nb-cb]])
R["has_face"] = {"B1_pct":ca/na*100, "B4_pct":cb/nb*100, "p":float(pf),
                 "lift": (ca/na)/max(cb/nb,1e-9)}

# ================= LỚP 2+3: kiểm ngoài mẫu & trong từng kênh =================
# (bài học L2 — nghịch lý Simpson)
conf = T[T.verdict=="XÁC NHẬN"].feature.tolist()
R["layer23"] = []
if conf:
    allv = v[v.is_matured].copy()
    # Dùng lại đặc trưng đã trích sẵn cho TOÀN NGÁCH (STEP_04c) nếu có —
    # nhanh hơn và phủ hết video thay vì cắt còn 2500.
    _full = P/"thumb_features_full.parquet"
    if _full.exists():
        fa = pd.read_parquet(_full)
    else:
        fa = pd.DataFrame([r for r in (analyze(x) for x in allv.video_id.head(2500)) if r])
    if len(fa) > 200:
        allv = allv.merge(fa, on="video_id", how="inner")
        for feat, col in [("Số khuôn mặt","n_faces"), ("Diện tích chữ (% ảnh)","text_area"),
                          ("Diện tích mặt (% ảnh)","face_area")]:
            if feat not in conf or col not in allv: continue
            hi = allv[allv[col] > allv[col].median()]; lo = allv[allv[col] <= allv[col].median()]
            lift = float(hi.vpd.median()/max(lo.vpd.median(), 1e-9))
            wc = []
            for h, g in allv.groupby("handle"):
                a2 = g[g[col] > allv[col].median()]; b2 = g[g[col] <= allv[col].median()]
                if len(a2) >= 5 and len(b2) >= 5 and b2.vpd.median() > 0:
                    wc.append(a2.vpd.median()/b2.vpd.median())
            R["layer23"].append({"feature":feat, "market_lift":lift,
                "n_ch":len(wc), "n_better":int(sum(1 for x in wc if x>1)),
                "within_lift":float(np.median(wc)) if wc else None,
                "final":("XÁC NHẬN" if lift>1.15 and wc and np.median(wc)>1
                         else "BÁC BỎ (Simpson)")})

# ================= TRÙNG LẶP HÌNH ẢNH (rủi ro T6) =================
def ham(a,b): return sum(c1!=c2 for c1,c2 in zip(a,b))
ph = d[["video_id","channel_id","phash64","grp"]].dropna()
dup_cross = 0; pairs = []
arr = ph.to_dict("records")
for i in range(len(arr)):
    for j in range(i+1, len(arr)):
        if arr[i]["channel_id"] != arr[j]["channel_id"]:
            if ham(arr[i]["phash64"], arr[j]["phash64"]) <= 6:
                dup_cross += 1
                if len(pairs) < 40:
                    pairs.append({"v1":arr[i]["video_id"], "v2":arr[j]["video_id"]})
R["visual_dup_cross_channel"] = dup_cross
R["visual_dup_pairs"] = pairs
if pairs: pd.DataFrame(pairs).to_csv(OUT/"09_thumb_duplicates.csv", index=False)

d.to_parquet(OUT/"_thumb_features.parquet", index=False)
json.dump(R, open(OUT/"_thumb_metrics.json","w"), indent=2, ensure_ascii=False, default=str)

print("=== LỚP 1: B1 (thắng) vs B4 (thua) ===")
print(T[["feature","B1","B4","p","cliffs_delta","verdict"]]
      .to_string(index=False, float_format=lambda x:f"{x:.3f}"))
print(f"\nCó khuôn mặt: B1={R['has_face']['B1_pct']:.1f}% vs B4={R['has_face']['B4_pct']:.1f}%  "
      f"lift={R['has_face']['lift']:.2f}×  p={R['has_face']['p']:.4f}")
if R["layer23"]:
    print("\n=== LỚP 2+3: kiểm ngoài mẫu & trong từng kênh ===")
    for x in R["layer23"]:
        print(f"  {x['feature']:28} lift toàn TT={x['market_lift']:.2f}× "
              f"kênh tốt hơn {x['n_better']}/{x['n_ch']} → {x['final']}")
print(f"\n=== TRÙNG LẶP HÌNH ẢNH ===")
print(f"  {dup_cross} cặp ảnh gần giống nhau GIỮA CÁC KÊNH (Hamming ≤6/64)")
print(f"\nĐã ghi: 08_thumb_visual_tests.csv · _thumb_features.parquet · _thumb_metrics.json")
