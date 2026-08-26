"""STEP_03 — Bản đồ đối thủ: phân loại mô hình (T4), cửa gia nhập (T3)."""
import pandas as pd, numpy as np, json, warnings
import sys
from pathlib import Path
warnings.filterwarnings("ignore")

N=Path(sys.argv[1] if len(sys.argv)>1 else "niches/christian-blues"); P=N/"00_input/processed"; OUT=N/"03_competitor"
OUT.mkdir(exist_ok=True)
ch=pd.read_parquet(P/"channels_enriched.parquet")
v =pd.read_parquet(P/"videos_enriched.parquet")
th=pd.read_parquet(P/"thumbnails.parquet")
CRAWL=v.published_at.max().ceil("h")
R={}

# ---------- đặc trưng theo kênh ----------
g=v.groupby("channel_id").agg(
    n_vid=("video_id","size"), med_view=("view_count","median"),
    med_vpd=("vpd","median"), tot_view=("view_count","sum"),
    med_dur=("duration_sec","median"),
    last_pub=("published_at","max"), first_pub=("published_at","min"),
    med_eng=("engagement_rate","median"))
c=ch.set_index("channel_id").join(g)
c["per_month"]=c.n_vid/c.channel_age_months
c["view_per_vid"]=c.tot_view/c.n_vid
c["days_since_last"]=(CRAWL-c.last_pub).dt.days
c["active"]=c.days_since_last<=90

# đa dạng thumbnail: đếm cluster khác nhau / số video
tc=th.drop(columns=["channel_id"],errors="ignore").merge(v[["video_id","channel_id"]],on="video_id")
tdiv=tc.groupby("channel_id").agg(n_clu=("cluster","nunique"),n_th=("cluster","size"))
tdiv["thumb_diversity"]=tdiv.n_clu/tdiv.n_th
c=c.join(tdiv[["thumb_diversity"]])

# ---------- PHÂN LOẠI MÔ HÌNH (T4) ----------
# Dấu hiệu ai-first: nhịp đăng dày + thumbnail đồng nhất + kênh trẻ
def classify(r):
    sig=[]
    if r.per_month>=12: sig.append("nhịp đăng dày (≥12 video/tháng)")
    if pd.notna(r.thumb_diversity) and r.thumb_diversity<0.15: sig.append("thumbnail đồng nhất")
    if r.channel_age_months<18: sig.append("kênh trẻ (<18 tháng)")
    if pd.notna(r.med_dur) and r.med_dur>=3600: sig.append("thiên mix dài")
    score=len(sig)
    if r.per_month>=20 and score>=2: lab="ai-first"
    elif r.per_month>=8 and score>=2: lab="ai-first"
    elif r.per_month<3 and r.channel_age_months>24: lab="artist/rebroadcast"
    elif score>=2: lab="hybrid"
    else: lab="hybrid"
    return pd.Series({"model":lab,"signals":" · ".join(sig) if sig else "—","sig_count":score})
c=c.join(c.apply(classify,axis=1))

top20=c.nlargest(20,"tot_view")
R["M4_1_ai_first_top20_pct"]=float((top20.model=="ai-first").mean()*100)
R["model_dist"]={k:int(x) for k,x in c.model.value_counts().items()}

# ---------- CỬA GIA NHẬP (T3) ----------
def gini(x):
    x=np.sort(np.array(x,dtype=float)); n=len(x)
    if n==0 or x.sum()==0: return np.nan
    return float((2*np.sum((np.arange(1,n+1))*x)/(n*x.sum()))-(n+1)/n)
R["M3_1_gini"]=gini(c.tot_view.values)

young=c[c.channel_age_months<12]
R["M3_2_newcomer_success_pct"]=float((young.views_per_month>=100000).mean()*100)
R["_young_n"]=int(len(young)); R["_young_success_n"]=int((young.views_per_month>=100000).sum())

# M3.3 — KHÔNG đo được "time to traction" thật với dữ liệu 1 snapshot.
# view_count là tích lũy ĐẾN NGÀY CRAWL, không phải view tại thời điểm đăng,
# nên cumsum luôn vượt 100k sau vài video -> con số vô nghĩa.
# THAY BẰNG: tuổi kênh của nhóm đã đạt traction (đo được, có ý nghĩa tương đương).
R["M3_3_status"]="KHÔNG ĐO ĐƯỢC — cần ≥2 snapshot"
succ=c[c.views_per_month>=100000]
R["M3_3_alt_median_age_of_successful"]=float(succ.channel_age_months.median())
R["M3_3_alt_fastest_success"]=[{"handle":r.handle,"age_m":float(r.channel_age_months),
  "vpm":float(r.views_per_month)} for _,r in succ.nsmallest(5,"channel_age_months").iterrows()]
c["months_to_100k"]=np.nan

# tập trung
R["top1_share"]=float(c.tot_view.max()/c.tot_view.sum()*100)
R["top5_share"]=float(c.nlargest(5,"tot_view").tot_view.sum()/c.tot_view.sum()*100)
R["top20pct_share"]=float(c.nlargest(int(len(c)*.2),"tot_view").tot_view.sum()/c.tot_view.sum()*100)

# ---------- PHÂN TẦNG ----------
def tier(r):
    if r.views_per_month>=500000: return "1-Dẫn đầu"
    if r.views_per_month>=200000: return "2-Thách thức"
    if r.views_per_month>=50000:  return "3-Đang lên"
    if r.active:                  return "4-Hụt hơi"
    return "5-Ngừng hoạt động"
c["tier"]=c.apply(tier,axis=1)
R["tier_dist"]={k:int(x) for k,x in c.tier.value_counts().sort_index().items()}

# ---------- HIỆU SUẤT/VIDEO CAO NHẤT ----------
eff=c[c.n_vid>=20].nlargest(8,"view_per_vid")
R["top_efficiency"]=[{"handle":r.handle,"view_per_vid":float(r.view_per_vid),
  "n_vid":int(r.n_vid),"age_m":float(r.channel_age_months),
  "med_dur_min":float(r.med_dur/60) if pd.notna(r.med_dur) else None,
  "per_month":float(r.per_month),"model":r.model} for _,r in eff.iterrows()]

# xuất
cols=["handle","title","country","channel_age_months","subscriber_count","tot_view",
      "n_vid","per_month","view_per_vid","med_view","med_vpd","views_per_month",
      "months_to_100k","thumb_diversity","model","signals","tier","active","days_since_last"]
c.reset_index()[["channel_id"]+cols].sort_values("tot_view",ascending=False)\
 .to_csv(OUT/"02_channel_table.csv",index=False)
json.dump(R,open(OUT/"_metrics_raw.json","w"),indent=2,default=str)

print("=== T3 CỬA GIA NHẬP ===")
print(f"M3.1 Gini                 {R['M3_1_gini']:.3f}")
print(f"M3.2 Kênh mới thành công  {R['M3_2_newcomer_success_pct']:.1f}%  ({R['_young_success_n']}/{R['_young_n']} kênh <12 tháng đạt ≥100k view/tháng)")
print(f"M3.3 {R['M3_3_status']}")
print(f"     (thay thế) Tuổi trung vị kênh đã đạt ≥100k view/tháng: {R['M3_3_alt_median_age_of_successful']:.1f} tháng")
for e in R["M3_3_alt_fastest_success"]:
    print(f"       {e['handle']:26} {e['age_m']:5.1f} tháng  {e['vpm']:>12,.0f} view/tháng")
print(f"\nTập trung: top1={R['top1_share']:.1f}%  top5={R['top5_share']:.1f}%  top20%={R['top20pct_share']:.1f}%")
print("\n=== T4 MÔ HÌNH KÊNH ===")
print(f"M4.1 AI-first trong top20: {R['M4_1_ai_first_top20_pct']:.1f}%")
for k,x in R["model_dist"].items(): print(f"  {k:20} {x}")
print("\n=== PHÂN TẦNG ===")
for k,x in R["tier_dist"].items(): print(f"  {k:22} {x}")
print("\n=== HIỆU SUẤT/VIDEO CAO NHẤT (≥20 video) ===")
print(eff[["handle","view_per_vid","n_vid","channel_age_months","per_month","model"]].to_string())
