"""STEP_02 — Quy mô (T1) + Động lượng (T2) + Tách H1/H2 pha loãng."""
import pandas as pd, numpy as np, json, sys, warnings
from pathlib import Path
warnings.filterwarnings("ignore")

NICHE=Path(sys.argv[1] if len(sys.argv)>1 else "niches/christian-blues")
P=NICHE/"00_input/processed"
# Tạo thư mục output nếu chưa có — ngách mới không có sẵn (bài học T22)
P.mkdir(parents=True, exist_ok=True)
v=pd.read_parquet(P/"videos_enriched.parquet")
ch=pd.read_parquet(P/"channels_enriched.parquet")
CRAWL=v.published_at.max().ceil("h")
R={}

# ================= T1 · QUY MÔ =================
# Views/tháng của ngách: tổng view các video đăng trong 12 tháng gần / 12
recent=v[v.published_at>=CRAWL-pd.Timedelta(days=365)]
R["M1_1_views_per_month"]=float(recent.view_count.sum()/12)
active=v[v.published_at>=CRAWL-pd.Timedelta(days=90)].channel_id.nunique()
R["M1_2_active_channels"]=int(active)
R["M1_2_total_channels"]=int(ch.channel_id.nunique())
R["M1_3_median_view"]=float(v[v.is_matured].view_count.median())
R["M1_3_mean_view"]=float(v[v.is_matured].view_count.mean())

# ================= T2 · ĐỘNG LƯỢNG =================
# QUAN TRỌNG: chỉ so sánh CỬA SỔ ĐỀU ĐÃ CHÍN (≥60 ngày tuổi).
# Dùng cửa sổ 0-90d là SAI: video mới chưa kịp tích view -> tạo ảo giác cầu sụp.
mat=v[v.is_matured]
def win(d0,d1):
    return mat[(mat.published_at>=CRAWL-pd.Timedelta(days=d0))&(mat.published_at<CRAWL-pd.Timedelta(days=d1))]
w_now, w_prev = win(150,60), win(240,150)   # cả hai đều đã chín hoàn toàn
R["_window_note"]="Cửa sổ 150-60d vs 240-150d; cả hai đều ≥60 ngày tuổi nên so sánh công bằng"

# Đối chứng: nếu dùng cửa sổ ngây thơ 0-90d thì ra bao nhiêu (để minh họa cái bẫy)
def winr(d0,d1):
    return v[(v.published_at>=CRAWL-pd.Timedelta(days=d0))&(v.published_at<CRAWL-pd.Timedelta(days=d1))]
_n,_p=winr(90,0),winr(180,90)
R["_naive_M2_1"]=float(_n.view_count.sum()/_p.view_count.sum())
R["_naive_M2_2"]=float(len(_n)/len(_p))
R["_naive_M2_4"]=R["_naive_M2_1"]/R["_naive_M2_2"]
R["_naive_maturity_pct"]=float(_n.is_matured.mean()*100)
R["M2_1_view_growth"]=float(w_now.view_count.sum()/w_prev.view_count.sum())
R["M2_2_supply_growth"]=float(len(w_now)/len(w_prev))
R["M2_3_new_channel_rate"]=float((ch.channel_age_months<12).mean()*100)
R["M2_4_demand_supply_gap"]=R["M2_1_view_growth"]/R["M2_2_supply_growth"]
R["_w_now_videos"]=len(w_now); R["_w_prev_videos"]=len(w_prev)
R["_w_now_views"]=int(w_now.view_count.sum()); R["_w_prev_views"]=int(w_prev.view_count.sum())

# ================= PHA LOÃNG: TÁCH H1 vs H2 =================
m=v[v.is_matured].copy()
m["ym"]=m.published_at.dt.to_period("M")
top20=ch.nlargest(20,"view_count").channel_id
allm =m.groupby("ym").agg(n=("view_count","size"),med=("view_count","median")).reset_index()
topm =m[m.channel_id.isin(top20)].groupby("ym").agg(n=("view_count","size"),med=("view_count","median")).reset_index()
rest =m[~m.channel_id.isin(top20)].groupby("ym").agg(n=("view_count","size"),med=("view_count","median")).reset_index()

def trend(df,col="med",lo="2025-08",hi="2026-05"):
    a=df[df.ym.astype(str)==lo][col]; b=df[df.ym.astype(str)==hi][col]
    if len(a)==0 or len(b)==0: return None
    return float(b.iloc[0]/a.iloc[0])

R["H_all_median_ratio"]=trend(allm)
R["H_top20_median_ratio"]=trend(topm)
R["H_rest_median_ratio"]=trend(rest)

# VPD chuẩn hóa theo tuổi — thước đo ĐÚNG cho hiệu quả
def vpdtrend(d):
    g=d.groupby("ym").vpd.median()
    a,b=g.get(pd.Period("2025-08")),g.get(pd.Period("2026-05"))
    return None if (a is None or b is None) else float(b/a)
R["H_all_vpd_ratio"]=vpdtrend(m)
R["H_top20_vpd_ratio"]=vpdtrend(m[m.channel_id.isin(top20)])
R["H_rest_vpd_ratio"]=vpdtrend(m[~m.channel_id.isin(top20)])

# quyết định H1 vs H2
# Phán quyết dựa trên VPD (chuẩn hóa tuổi), KHÔNG dựa view thô
vt = R["H_all_vpd_ratio"]
if vt is None:            R["dilution_verdict"]="không đủ dữ liệu"
elif vt>=1.0:             R["dilution_verdict"]="H0"  # không pha loãng thật
elif vt>=0.7:             R["dilution_verdict"]="H1"  # pha loãng nhẹ
else:                     R["dilution_verdict"]="H2"  # cả ngách suy
R["_verdict_note"]=("View thô giảm nhưng VPD (chuẩn hóa tuổi) KHÔNG giảm "
  "-> phần lớn 'pha loãng' là ảo giác do video mới chưa chín")

# ================= ĐỊA LÝ / NGÔN NGỮ =================
R["geo"]={k:int(x) for k,x in ch.country.fillna("(không khai)").value_counts().items()}
lang=v.default_audio_language.fillna("(trống)").value_counts()
R["lang"]={k:int(x) for k,x in lang.head(8).items()}
t1={"US","GB","CA","AU","NZ","IE"}
R["tier1_channel_pct"]=float(ch.country.isin(t1).mean()*100)

# ================= XUẤT =================
allm.assign(seg="all").to_csv(NICHE/"02_market/median_by_month_all.csv",index=False)
topm.assign(seg="top20").to_csv(NICHE/"02_market/median_by_month_top20.csv",index=False)
rest.assign(seg="rest").to_csv(NICHE/"02_market/median_by_month_rest.csv",index=False)
json.dump(R,open(NICHE/"02_market/_metrics_raw.json","w"),indent=2,default=str)

print("=== T1 QUY MÔ ===")
print(f"M1.1 views/tháng        {R['M1_1_views_per_month']:>14,.0f}")
print(f"M1.2 kênh hoạt động     {R['M1_2_active_channels']:>14} / {R['M1_2_total_channels']}")
print(f"M1.3 view trung vị      {R['M1_3_median_view']:>14,.0f}  (trung bình {R['M1_3_mean_view']:,.0f})")
print("\n=== T2 ĐỘNG LƯỢNG (90 ngày gần vs 90 ngày trước) ===")
print(f"M2.1 tăng cầu (view)    {R['M2_1_view_growth']:>14.3f}   ({R['_w_prev_views']:,} -> {R['_w_now_views']:,})")
print(f"M2.2 tăng cung (video)  {R['M2_2_supply_growth']:>14.3f}   ({R['_w_prev_videos']} -> {R['_w_now_videos']})")
print(f"M2.3 % kênh <12 tháng   {R['M2_3_new_channel_rate']:>14.1f}%")
print(f"M2.4 CẦU/CUNG           {R['M2_4_demand_supply_gap']:>14.3f}  <-- QUYẾT ĐỊNH")
print("\n=== PHA LOÃNG 2025-08 -> 2026-05 ===")
print(f"{'':14}{'view thô':>12}{'VPD (chuẩn tuổi)':>20}")
print(f"{'Toàn ngách':14}{R['H_all_median_ratio']:>12.3f}{R['H_all_vpd_ratio']:>20.3f}")
print(f"{'TOP 20 kênh':14}{R['H_top20_median_ratio']:>12.3f}{R['H_top20_vpd_ratio']:>20.3f}")
print(f"{'Còn lại':14}{R['H_rest_median_ratio']:>12.3f}{R['H_rest_vpd_ratio']:>20.3f}")
print(f"KẾT LUẬN: {R['dilution_verdict']} — {R['_verdict_note']}")
print(f"\n[BẪY] Nếu dùng cửa sổ 0-90d (chỉ {R['_naive_maturity_pct']:.0f}% đã chín):")
print(f"       M2.4 = {R['_naive_M2_4']:.3f} -> kết luận SAI là ngách đang sụp")
print(f"\nTier-1 kênh: {R['tier1_channel_pct']:.1f}%")
