"""Biểu đồ cho báo cáo STEP_04b — phân tích thumbnail."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8,
                     "axes.edgecolor": "#CFC4B8", "axes.linewidth": .6,
                     "figure.facecolor": "white"})
INK, ACC, GOOD, BAD, WARN = "#1A1614", "#8C3A2B", "#2F6B4F", "#9B2C2C", "#8A6410"

N = Path("niches/christian-blues"); D = N/"04_outlier"; P = N/"00_input/processed"
v = pd.read_parquet(P/"videos_enriched.parquet")
f = pd.read_parquet(P/"thumb_features_full.parquet")
m = v.merge(f, on="video_id"); m = m[m.is_matured & (m.view_count >= 500)].copy()
m["like_rate"] = m.like_count/m.view_count.clip(lower=1)
T = pd.read_csv(D/"10_thumb_top_tests.csv")

# ---------- H1: Haar vs YuNet — vì sao phải sửa công cụ ----------
fig, ax = plt.subplots(figsize=(6.4, 2.0))
bars = ax.barh(["Haar cascade\n(bản đầu — SAI)", "YuNet CNN\n(đã sửa)"], [35.8, 90.2],
               color=[BAD, GOOD], height=.55)
for b, val in zip(bars, [35.8, 90.2]):
    ax.text(val+1.5, b.get_y()+b.get_height()/2, f"{val:.1f}%", va="center",
            fontsize=9, fontweight="bold")
ax.set_xlim(0, 105); ax.set_xlabel("% ảnh được nhận là CÓ khuôn mặt (n=7.193)")
ax.spines[["top", "right"]].set_visible(False)
ax.set_title("Cùng một bộ ảnh, hai bộ dò cho kết quả lệch 2,5 lần",
             fontsize=9, loc="left", pad=8)
fig.tight_layout(); fig.savefig(D/"c1_detector.png", dpi=190); plt.close(fig)

# ---------- H2: hiệu ứng co lại qua 3 lớp kiểm ----------
sub = T[(T.thước_đo == "TỶ LỆ LIKE") & T.lớp23.notna()].copy()
sub = sub.reindex(sub.cliffs_delta.abs().sort_values(ascending=True).index)
fig, ax = plt.subplots(figsize=(6.4, 3.0))
y = np.arange(len(sub))
l1 = sub.cliffs_delta.abs().values
l3 = np.array([abs(x-1) for x in sub.within_lift.fillna(1)])
ax.barh(y+.19, l1, height=.34, color=ACC, label="Lớp 1 — so top vs dưới (|Cliff's δ|)")
ax.barh(y-.19, l3, height=.34, color="#B9AC9F",
        label="Lớp 3 — trong cùng kênh (|chênh lệch|)")
ax.set_yticks(y); ax.set_yticklabels(sub.đặc_trưng, fontsize=7.5)
ax.axvline(.30, color=BAD, ls="--", lw=.8)
ax.text(.305, len(sub)-.4, "ngưỡng XÁC NHẬN 0,30", fontsize=6.5, color=BAD)
ax.set_xlabel("Độ lớn hiệu ứng")
ax.spines[["top", "right"]].set_visible(False)
ax.legend(fontsize=6.8, loc="lower right", frameon=False)
ax.set_title("Hiệu ứng biến mất khi so trong cùng một kênh",
             fontsize=9, loc="left", pad=8)
fig.tight_layout(); fig.savefig(D/"c2_layers.png", dpi=190); plt.close(fig)

# ---------- H3: kênh mới là biến giải thích ----------
ch = (m.groupby("handle").agg(n=("video_id", "size"), lr=("like_rate", "median"),
                              cs=("center_std", "median")).query("n>=10"))
fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.6))
a = axes[0]
a.scatter(ch.cs, ch.lr*100, s=ch.n*1.6, color=ACC, alpha=.55, edgecolor="white", lw=.5)
z = np.polyfit(ch.cs, ch.lr*100, 1)
xs = np.linspace(ch.cs.min(), ch.cs.max(), 50)
a.plot(xs, np.polyval(z, xs), color=INK, lw=1, ls="--")
a.set_xlabel("Độ chi tiết ảnh (trung vị kênh)"); a.set_ylabel("Tỷ lệ like (%)")
a.set_title(f"Ở CẤP KÊNH: r = −0,55", fontsize=8, loc="left")
a.spines[["top", "right"]].set_visible(False)

b = axes[1]
_md = m.center_std.median()
parts = [(m.loc[m.center_std <= _md, "like_rate"]*100).dropna().values,
         (m.loc[m.center_std > _md, "like_rate"]*100).dropna().values]
bp = b.boxplot(parts, tick_labels=["ảnh\nđơn giản", "ảnh\nphức tạp"], widths=.5,
               showfliers=False, patch_artist=True, medianprops=dict(color=INK, lw=1.3))
for arr, x in zip(parts, [1, 2]):
    b.text(x, np.median(arr), f"  {np.median(arr):.2f}%", va="center",
           fontsize=7, color=INK)
for pc, c in zip(bp["boxes"], ["#D8CFC4", "#D8CFC4"]):
    pc.set_facecolor(c); pc.set_edgecolor("#CFC4B8")
b.set_ylabel("Tỷ lệ like (%)")
b.set_title("Ở CẤP VIDEO: phân bố chồng lấn nhiều", fontsize=8, loc="left")
b.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(D/"c3_channel.png", dpi=190); plt.close(fig)

# ---------- H4: phong cách ảnh của ngách ----------
fig, axes = plt.subplots(1, 3, figsize=(6.4, 2.1))
for a, (col, lab, xf) in zip(axes, [
        ("face_max", "Mặt lớn nhất (% ảnh)", 100),
        ("text_area", "Diện tích chữ (% ảnh)", 100),
        ("n_text_blocks", "Số khối chữ", 1)]):
    d = m[col]*xf
    a.hist(d[d < d.quantile(.98)], bins=28, color="#B9AC9F", edgecolor="white", lw=.4)
    a.axvline(d.median(), color=ACC, lw=1.2)
    a.text(d.median(), a.get_ylim()[1]*.92, f" trung vị {d.median():.1f}",
           fontsize=6.5, color=ACC)
    a.set_xlabel(lab, fontsize=7); a.set_yticks([])
    a.spines[["top", "right", "left"]].set_visible(False)
fig.suptitle("Chuẩn hình ảnh của ngách — 7.193 thumbnail", fontsize=9, x=.01, ha="left")
fig.tight_layout(); fig.savefig(D/"c4_norms.png", dpi=190); plt.close(fig)

print("Đã vẽ: c1_detector · c2_layers · c3_channel · c4_norms")
