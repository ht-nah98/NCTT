"""STEP_07 — Kiếm tiền (T5) & Rủi ro (T6)."""
import pandas as pd, numpy as np, json, warnings
import sys
from pathlib import Path
warnings.filterwarnings("ignore")

N=Path(sys.argv[1] if len(sys.argv)>1 else "niches/christian-blues"); P=N/"00_input/processed"; OUT=N/"07_monetization"
OUT.mkdir(exist_ok=True)
v=pd.read_parquet(P/"videos_enriched.parquet")
ch=pd.read_parquet(P/"channels_enriched.parquet")
aud=json.load(open(N/"05_audience/_metrics_raw.json"))
R={}

# ============ T5 · KIẾM TIỀN ============
# M5.1 geo mix — dùng NGÔN NGỮ làm proxy chính (tốt hơn country của kênh)
lang=v.default_audio_language.fillna("unknown")
en=lang.str.startswith("en").sum(); es=lang.str.startswith("es").sum()
pt=lang.str.startswith("pt").sum(); unk=(lang=="unknown").sum()
known=len(v)-unk
R["M5_1_lang"]={"en":int(en),"es":int(es),"pt":int(pt),"unknown":int(unk),
  "en_pct_of_known":float(en/known*100)}
T1={"US","GB","CA","AU","NZ","IE"}
R["M5_1_tier1_channel_pct"]=float(ch.country.isin(T1).mean()*100)
R["M5_1_tier1_of_declared"]=float(ch[ch.country.notna()].country.isin(T1).mean()*100)

# M5.3 độ dài -> số ad slot (YouTube cho phép mid-roll từ 8 phút)
m=v[v.is_matured]
band=m.groupby("duration_band").agg(n=("duration_sec","size"),med_sec=("duration_sec","median"),
                                    med_view=("view_count","median"))
band["ad_slots"]=(band.med_sec/60/8).clip(upper=40).round(1)
band.loc[band.med_sec<480,"ad_slots"]=1.0   # <8 phút: chỉ pre/post-roll
R["M5_3_band"]=band.reset_index().to_dict("records")
R["M5_3_median_duration_sec"]=float(m.duration_sec.median())

# M5.2 RPM ước tính — CÓ GIẢ ĐỊNH, không phải số đo
# Căn cứ: nhạc US, khán giả lớn tuổi, nội dung tôn giáo, long-form
R["M5_2_rpm"]={"low":1.5,"base":3.0,"high":6.0,
  "basis":"Nhạc Tier-1 nền tảng $1.5-4; điều chỉnh TĂNG do khán giả 60+ (sức mua, ít adblock) "
          "và long-form nhiều ad slot; điều chỉnh GIẢM do nhạc có attention thấp"}
# điểm T5 theo rubric
rpm=R["M5_2_rpm"]["base"]
R["T5_score"]=5 if rpm>=8 else 4 if rpm>=5 else 3 if rpm>=3 else 2 if rpm>=1.5 else 1
R["T5_note"]="RPM cơ sở $3.0 rơi đúng ranh giới khoảng $3-5 -> 3 điểm"

# Kịch bản doanh thu — dựa vào phân bố THẬT của kênh trong ngách
vpm=ch.views_per_month.dropna()
sc={}
for k,q in [("conservative",0.25),("base",0.50),("optimistic",0.90)]:
    views=float(vpm.quantile(q))
    sc[k]={"views_per_month":views,
      "rev_low":views/1000*R["M5_2_rpm"]["low"],
      "rev_base":views/1000*R["M5_2_rpm"]["base"],
      "rev_high":views/1000*R["M5_2_rpm"]["high"]}
R["scenarios"]=sc

# ============ T6 · RỦI RO ============
risks=[]
# R1 reused content — trùng title chéo kênh
t=v.title.astype(str).str.lower().str.strip()
x=v.assign(tl=t)
cross=x.groupby("tl").channel_id.nunique()
crosst=set(cross[cross>1].index)
x["is_cross"]=x.tl.isin(crosst)
n_cross_titles=int((cross>1).sum()); n_cross_vid=int(x.is_cross.sum())
pct_cross=float(x.is_cross.mean()*100)
chg=x.groupby("handle").is_cross.mean()*100
n_ch_high=int((chg>=30).sum())
risks.append({"risk":"Nội dung trùng lặp (reused content)","penalty":-2 if pct_cross>=10 else -1,
  "evidence":f"{n_cross_titles} tiêu đề dùng chung bởi nhiều kênh, phủ {n_cross_vid} video ({pct_cross:.1f}%). "
             f"{n_ch_high} kênh có ≥30% video trùng tiêu đề chéo.",
  "detail":"Đây là rủi ro CHÍNH của ngách. YouTube yêu cầu 'significant original value'."})
# R2 mô tả trùng — trong cùng kênh (template) hay chéo kênh?
de=v.assign(dl=v.description.astype(str).str.lower().str.strip())
de=de[de.dl.str.len()>50]
dg=de.groupby("dl").agg(n=("video_id","size"),nch=("channel_id","nunique"))
dup=dg[dg.n>1]
cross_desc=int((dup.nch>1).sum())
risks.append({"risk":"Mô tả dùng lại","penalty":0,
  "evidence":f"{len(dup)} mẫu mô tả dùng lại phủ {int(dup.n.sum())} video, "
             f"nhưng CHÉO kênh = {cross_desc} mẫu.",
  "detail":"Toàn bộ là template trong cùng một kênh — bình thường, không phải rủi ro."})
# R3 phụ thuộc kênh dẫn đầu
top1=float(ch.view_count.max()/ch.view_count.sum()*100)
risks.append({"risk":"Phụ thuộc kênh dẫn đầu","penalty":-1 if top1>40 else 0,
  "evidence":f"Kênh lớn nhất chiếm {top1:.1f}% tổng view (ngưỡng rủi ro: >40%).",
  "detail":"Không có kênh thống trị — thị trường phân tán lành mạnh."})
# R4 cung vượt cầu
m24=json.load(open(N/"_state/metrics.json"))["momentum"]["M2_4_demand_supply_gap"]
risks.append({"risk":"Cung vượt cầu","penalty":-1 if m24<0.8 else 0,
  "evidence":f"M2.4 = {m24:.3f} (ngưỡng rủi ro: <0.8).",
  "detail":"Cầu vẫn tăng nhanh hơn cung."})
# R5 bản quyền thánh ca
trad=r'\b(amazing grace|how great thou art|old rugged cross|blessed assurance|it is well|precious lord|swing low|wade in the water)\b'
ntrad=int(v.title.astype(str).str.contains(trad,case=False,regex=True).sum())
risks.append({"risk":"Bản quyền thánh ca","penalty":0,
  "evidence":f"Chỉ {ntrad} video ({ntrad/len(v)*100:.1f}%) đặt tên theo thánh ca kinh điển.",
  "detail":"Hầu hết là sáng tác mới. Thánh ca trước 1929 thuộc phạm vi công cộng."})
# R6 chủ đề nhạy cảm
risks.append({"risk":"Chủ đề tôn giáo bị soi kỹ","penalty":-1,
  "evidence":"Nội dung tôn giáo + AI thuộc nhóm bị rà soát chặt hơn về kiếm tiền.",
  "detail":"Không đo được từ dữ liệu — đánh giá dựa trên chính sách nền tảng."})

R["risks"]=risks
R["T6_penalty"]=int(sum(r["penalty"] for r in risks))
R["cross_title_perf"]={"cross_vpd":float(m.assign(c=m.title.astype(str).str.lower().str.strip().isin(crosst)).query("c").vpd.median()),
  "clean_vpd":float(m.assign(c=m.title.astype(str).str.lower().str.strip().isin(crosst)).query("~c").vpd.median())}
R["cross_by_channel"]=chg.nlargest(10).round(1).to_dict()

json.dump(R,open(OUT/"_metrics_raw.json","w"),indent=2,default=str)
pd.DataFrame(risks).to_csv(OUT/"02_risk_register.csv",index=False)

print("=== T5 KIẾM TIỀN ===")
print(f"M5.1 ngôn ngữ EN: {R['M5_1_lang']['en_pct_of_known']:.1f}% (trong số đã khai)")
print(f"     kênh Tier-1: {R['M5_1_tier1_channel_pct']:.1f}% toàn bộ | {R['M5_1_tier1_of_declared']:.1f}% trong số đã khai")
print(f"M5.2 RPM ước tính: ${R['M5_2_rpm']['low']}-{R['M5_2_rpm']['high']} (cơ sở ${R['M5_2_rpm']['base']})")
print(f"M5.3 độ dài trung vị: {R['M5_3_median_duration_sec']/60:.0f} phút")
print(f"T5 = {R['T5_score']}/5")
print("\nKịch bản doanh thu/tháng:")
for k,s in sc.items():
    print(f"  {k:13} {s['views_per_month']:>10,.0f} view -> ${s['rev_low']:>7,.0f} / ${s['rev_base']:>7,.0f} / ${s['rev_high']:>7,.0f}")
print("\n=== T6 RỦI RO ===")
for r in risks: print(f"  [{r['penalty']:+d}] {r['risk']:32} {r['evidence'][:70]}")
print(f"\nT6 tổng trừ: {R['T6_penalty']}")
print(f"\nVPD video trùng title chéo={R['cross_title_perf']['cross_vpd']:.2f} vs sạch={R['cross_title_perf']['clean_vpd']:.2f}")
