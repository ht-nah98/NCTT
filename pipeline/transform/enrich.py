"""STEP_01.2+3 — Kiểm toán chất lượng + Làm giàu 8 cột."""
import pandas as pd, numpy as np, sys, json, warnings
from pathlib import Path
warnings.filterwarnings("ignore")

NICHE=Path(sys.argv[1] if len(sys.argv)>1 else "niches/christian-blues")
P=NICHE/"00_input/processed"
# Tạo thư mục output nếu chưa có — ngách mới không có sẵn (bài học T22)
P.mkdir(parents=True, exist_ok=True)
# Mốc crawl = thời điểm video mới nhất trong dữ liệu (chính xác hơn nửa đêm)
CRAWL=pd.read_parquet(P/"videos.parquet").published_at.max().ceil("h")

ch=pd.read_parquet(P/"channels.parquet")
vi=pd.read_parquet(P/"videos.parquet")
st=pd.read_parquet(P/"video_stats.parquet")
cm=pd.read_parquet(P/"comments.parquet")

# ---------- QUALITY AUDIT ----------
Q=[]
def chk(name,val,ok,note=""):
    Q.append({"check":name,"value":val,"pass":bool(ok),"note":note})

chk("Trùng video_id trong videos", int(vi.video_id.duplicated().sum()), vi.video_id.duplicated().sum()==0)
chk("Trùng channel_id trong channels", int(ch.channel_id.duplicated().sum()), ch.channel_id.duplicated().sum()==0)
neg=int((st.view_count<0).sum()+st.view_count.isna().sum())
chk("view_count âm/null", neg, neg==0)
fut=int((vi.published_at>CRAWL).sum())
chk("published_at ở tương lai", fut, fut==0)
nsnap=int(st.groupby("video_id").size().max())
chk("Số snapshot video_stats", nsnap, nsnap>=2, "1 snapshot -> hạ tin cậy trục T2 xuống 'vừa'")
cov_cm=cm.video_id.nunique()/len(vi)*100
chk("Phủ comments (% video)", round(cov_cm,1), cov_cm>=30)
th=pd.read_parquet(P/"thumbnails.parquet")
cov_th=th.video_id.nunique()/len(vi)*100
chk("Phủ thumbnails (% video)", round(cov_th,1), cov_th>=30)
mp=pd.read_parquet(P/"media_probe.parquet")
cov_mp=mp.video_id.nunique()/len(vi)*100
chk("Phủ media_probe (% video)", round(cov_mp,1), cov_mp>=30, "Dưới 30% -> KHÔNG dùng để kết luận")

nulls={c: round(vi[c].isna().sum()/len(vi)*100,1) for c in vi.columns if vi[c].isna().any()}
for c,pct in nulls.items():
    chk(f"Null: videos.{c}", f"{pct}%", pct<30, "Trên 30% -> không dùng làm kết luận chính")

# ---------- ENRICH ----------
v=vi.merge(st[["video_id","view_count","like_count","comment_count"]],on="video_id",how="left")
v=v.merge(ch[["channel_id","handle","published_at","subscriber_count","country"]]
          .rename(columns={"published_at":"ch_published_at"}),on="channel_id",how="left")

v["age_days"]=(CRAWL-v.published_at).dt.days.clip(lower=1)
v["vpd"]=v.view_count/v.age_days
v["is_matured"]=v.age_days>=60
v["engagement_rate"]=(v.like_count.fillna(0)+v.comment_count.fillna(0))/v.view_count.replace(0,np.nan)
v["channel_age_months"]=(CRAWL-v.ch_published_at).dt.days/30.44

def band(s):
    if pd.isna(s): return None
    s=float(s)
    if s<60: return "Shorts"
    if s<360: return "1-6m"
    if s<1800: return "6-30m"
    if s<3600: return "30-60m"
    if s<10800: return "1-3h"
    return "3h+"
v["duration_band"]=v.duration_sec.map(band)

# outlier_ratio: baseline = median of MATURED videos of that channel
base=(v[v.is_matured].groupby("channel_id").view_count.median()
        .rename("channel_median_view"))
v=v.merge(base,on="channel_id",how="left")
v["outlier_ratio"]=v.view_count/v.channel_median_view.replace(0,np.nan)

v.to_parquet(P/"videos_enriched.parquet",index=False)

ch2=ch.copy()
ch2["channel_age_months"]=(CRAWL-ch2.published_at).dt.days/30.44
ch2["views_per_month"]=ch2.view_count/ch2.channel_age_months.replace(0,np.nan)
ch2.to_parquet(P/"channels_enriched.parquet",index=False)

qdf=pd.DataFrame(Q)
qdf.to_csv(P/"quality_audit.csv",index=False)
print(qdf.to_string(index=False))
print(f"\nEnriched: {len(v)} videos, {len(ch2)} channels")
print(f"matured: {int(v.is_matured.sum())} ({v.is_matured.mean()*100:.1f}%)")
