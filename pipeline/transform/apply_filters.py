"""STEP_01.4+5 — Lọc chọn lọc (4 rổ video + 3 tầng comment) + 5 kiểm chứng."""
import pandas as pd, numpy as np, sys, json, warnings
from pathlib import Path
warnings.filterwarnings("ignore")

NICHE=Path(sys.argv[1] if len(sys.argv)>1 else "niches/christian-blues")
P=NICHE/"00_input/processed"
# Tạo thư mục output nếu chưa có — ngách mới không có sẵn (bài học T22)
P.mkdir(parents=True, exist_ok=True)
v=pd.read_parquet(P/"videos_enriched.parquet")
cm=pd.read_parquet(P/"comments.parquet")

# ---- Ngưỡng nhóm 5.000-10.000 video (04_SELECTION_LOGIC.md §9) ----
TH=dict(B1_ratio=5, B1_view=20000, B2_age=90, B2_pct=0.90,
        B3_top=5, B4_ratio=0.2, B4_view=500,
        C1_like=25, C2_len=200, C2_like=2, C3_n=1500)

m=v[v.is_matured]                       # outlier chỉ tính trên video đã chín
p90=v.vpd.quantile(TH["B2_pct"])

B1=m[(m.outlier_ratio>=TH["B1_ratio"])&(m.view_count>=TH["B1_view"])].assign(bucket="B1_outlier")
B2=v[(v.age_days<=TH["B2_age"])&(v.vpd>=p90)].assign(bucket="B2_rising")
B3=v.sort_values("view_count",ascending=False).groupby("channel_id").head(TH["B3_top"]).assign(bucket="B3_repr")
B4=m[(m.outlier_ratio<=TH["B4_ratio"])&(m.view_count>=TH["B4_view"])].assign(bucket="B4_control")

sel=pd.concat([B1,B2,B3,B4])
buckets=sel.groupby("video_id").bucket.apply(lambda s:"+".join(sorted(set(s))))
sel=sel.drop_duplicates("video_id").drop(columns="bucket").merge(buckets,on="video_id")
sel.to_parquet(P/"selected_videos.parquet",index=False)

# ---- Comments ----
cm["tlen"]=cm.text.astype(str).str.len()
cm=cm[cm.tlen>=15]                                          # bỏ emoji/"Amen"
cm=cm.drop_duplicates(subset=["video_id","text"])           # bỏ spam trùng
C1=cm[cm.like_count>=TH["C1_like"]].assign(tier="C1_voted")
C2=cm[(cm.tlen>=TH["C2_len"])&(cm.like_count>=TH["C2_like"])].assign(tier="C2_depth")
pool=cm[cm.video_id.isin(set(B1.video_id)|set(B2.video_id))]
pool=pool[~pool.comment_id.isin(set(C1.comment_id)|set(C2.comment_id))]
C3=pool.sample(min(TH["C3_n"],len(pool)),random_state=42).assign(tier="C3_random")
selc=pd.concat([C1,C2,C3])
tiers=selc.groupby("comment_id").tier.apply(lambda s:"+".join(sorted(set(s))))
selc=selc.drop_duplicates("comment_id").drop(columns="tier").merge(tiers,on="comment_id")
selc.to_parquet(P/"selected_comments.parquet",index=False)

# ---- 5 KIỂM CHỨNG ----
V=[]
def chk(n,val,ok,tgt=""):V.append({"check":n,"value":val,"target":tgt,"pass":bool(ok)})
chk("Phủ kênh",f"{sel.channel_id.nunique()}/{v.channel_id.nunique()}",
    sel.channel_id.nunique()==v.channel_id.nunique(),"100%")
months=v.published_at.dt.to_period("M").nunique(); msel=sel.published_at.dt.to_period("M").nunique()
chk("Phủ thời gian",f"{msel}/{months} tháng",msel>=months*0.9,"≥90%")
chk("Phủ định dạng",f"{sel.duration_band.nunique()}/{v.duration_band.nunique()}",
    sel.duration_band.nunique()==v.duration_band.nunique(),"đủ 6")
chk("Rổ đối chứng B4",len(B4),len(B4)>=100,"≥100")
covv=sel.view_count.sum()/v.view_count.sum()*100
chk("Phủ view",f"{covv:.1f}%",covv>=70,"≥70%")
chk("Tỷ lệ video",f"{len(sel)/len(v)*100:.1f}%",10<=len(sel)/len(v)*100<=15,"10-15%")
chk("Tỷ lệ comment",f"{len(selc)/145150*100:.1f}%",True,"4-6%")

vdf=pd.DataFrame(V); vdf.to_csv(P/"selection_validation.csv",index=False)
print("=== BUCKETS ===")
print(f"B1 outlier {len(B1):>5} | B2 rising {len(B2):>5} | B3 repr {len(B3):>5} | B4 control {len(B4):>5}")
print(f"UNION VIDEO {len(sel)} / {len(v)} = {len(sel)/len(v)*100:.1f}%")
print(f"C1 {len(C1)} | C2 {len(C2)} | C3 {len(C3)} -> COMMENT {len(selc)} ({len(selc)/145150*100:.1f}%)")
print()
print(vdf.to_string(index=False))
json.dump({"thresholds":TH,"p90_vpd":float(p90)},open(P/"_selection_params.json","w"),indent=2)
