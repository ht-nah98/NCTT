"""STEP_08.1 — Backtest rubric trên 24 dòng nhạc trong bảng FMG cũ.
Mục đích: kiểm rubric có cho kết quả hợp lý trên ngách đã biết không."""
import pandas as pd, numpy as np, csv, json, re, warnings
from pathlib import Path
warnings.filterwarnings("ignore")

SRC=Path("niches/_backtest/FMG_phan-tich-dong-nhac.csv")
OUT=Path("niches/christian-blues/99_report"); OUT.mkdir(parents=True,exist_ok=True)

rows=list(csv.reader(open(SRC,encoding="utf8")))
def num(s):
    if not s: return np.nan
    s=str(s).replace(",","").replace("%","").replace(".","",0) if False else str(s).replace(",","").replace("%","")
    try: return float(s)
    except Exception: return np.nan

rec=[]
for r in rows[3:]:
    if len(r)<22 or not r[1].strip() or r[1].strip() in ("Các dòng nhạc ngách",): continue
    name=r[1].strip()
    views=num(r[4]); nch=num(r[3])
    top20=str(r[13]).replace(",",".").replace("%","").strip()
    try: top20=float(top20)
    except Exception: top20=np.nan
    old_total=num(r[21])
    rec.append({"genre":name,"channels":nch,"views_month":views,"top20_pct":top20,
                "old_score":old_total,"age":r[6].strip(),
                "old_scale":num(r[8]),"old_ai":num(r[11]),"old_entry":num(r[16]),"old_taste":num(r[19])})
D=pd.DataFrame(rec).dropna(subset=["views_month"])

# --- Áp rubric mới (phần đo được từ bảng cũ) ---
def s_T1(v):
    if v>=50e6: return 5
    if v>=20e6: return 4
    if v>=8e6:  return 3
    if v>=3e6:  return 2
    if v>=1e6:  return 1
    return 0
def s_gini_proxy(top20):
    # top20% share -> proxy cho độ mở. Thấp = mở
    if np.isnan(top20): return np.nan
    if top20<=55: return 5
    if top20<=62: return 4
    if top20<=70: return 3
    if top20<=80: return 2
    if top20<=88: return 1
    return 0
D["T1_new"]=D.views_month.map(s_T1)
D["T3_proxy"]=D.top20_pct.map(s_gini_proxy)
D["T1_old"]=D.old_scale
D["T3_old"]=D.old_entry
D["dT1"]=D.T1_new-D.T1_old
D["dT3"]=D.T3_proxy-D.T3_old

D=D.sort_values("views_month",ascending=False)
D.to_csv(OUT/"backtest_rubric.csv",index=False)

print("=== BACKTEST: T1 QUY MÔ (rubric mới vs bảng cũ) ===")
print(D[["genre","views_month","T1_old","T1_new","dT1"]].to_string(index=False,
      float_format=lambda x:f"{x:,.0f}"))
print(f"\nSai lệch trung bình |dT1| = {D.dT1.abs().mean():.2f} điểm")
print(f"Số ngách lệch ≥2 điểm: {(D.dT1.abs()>=2).sum()}/{len(D)}")

print("\n=== BACKTEST: T3 CỬA GIA NHẬP ===")
d3=D.dropna(subset=["T3_proxy","T3_old"])
print(d3[["genre","top20_pct","T3_old","T3_proxy","dT3"]].to_string(index=False,
      float_format=lambda x:f"{x:.1f}"))
print(f"\nSai lệch trung bình |dT3| = {d3.dT3.abs().mean():.2f} điểm")

# Kiểm tính nhất quán: cùng top20% có ra cùng điểm không?
print("\n=== KIỂM NHẤT QUÁN (lỗi L1 của bảng cũ) ===")
grp=d3.groupby(pd.cut(d3.top20_pct,[55,62,70,80,90]))
for k,g in grp:
    if len(g)>1:
        print(f"  top20% {k}: điểm cũ = {sorted(g.T3_old.dropna().tolist())} | điểm mới = {sorted(g.T3_proxy.tolist())}")
json.dump({"mean_abs_dT1":float(D.dT1.abs().mean()),
           "mean_abs_dT3":float(d3.dT3.abs().mean()),
           "n_genres":len(D)},open(OUT/"backtest_summary.json","w"),indent=2)
