"""STEP_04 — Sàng lọc đối chứng: so sánh B1 (outlier) vs B4 (đối chứng).

BƯỚC NÀY LOẠI TRỪ, KHÔNG TỔNG HỢP.
  Nó trả lời "đặc trưng nào KHÔNG phân biệt thắng/thua" bằng nhóm đối chứng.
  Kết quả điển hình: 0/20 đứng vững — tức là bác bỏ, không phải tìm ra công thức.

  "Công thức thắng" (làm gì để dựng kênh) là đầu ra của STEP_10 playbook,
  bước tổng hợp SAU khi đã có thumbnail + chân dung + từ khóa.
  Xem 00_system/01_ARCHITECTURE.md §2.4 (tầng kiểm định vs tầng mô tả).

⚠ TÁM ĐẶC TRƯNG THUMBNAIL ở khối "thumbnail" bên dưới đo bằng PROXY —
  trích sẵn trong Excel nguồn, không đọc từ ảnh thật. STEP_04b/04g đo lại
  bằng YuNet + YOLO-seg + EasyOCR và đã chứng minh `text_score` hỏng
  (tương quan với chữ thật chỉ 0,233). Kết luận "BÁC BỎ" của tám dòng đó
  chỉ có hiệu lực với thước đo proxy. Bài học T17–T21, T29.
"""
import pandas as pd, numpy as np, json, re, warnings
import sys
from pathlib import Path
from scipy import stats
warnings.filterwarnings("ignore")

N=Path(sys.argv[1] if len(sys.argv)>1 else "niches/christian-blues"); P=N/"00_input/processed"; OUT=N/"04_outlier"
OUT.mkdir(exist_ok=True)
s=pd.read_parquet(P/"selected_videos.parquet")
th=pd.read_parquet(P/"thumbnails.parquet")
R={}

B1=s[s.bucket.str.contains("B1")].copy(); B1["grp"]="B1_thắng"
B4=s[s.bucket.str.contains("B4")].copy(); B4["grp"]="B4_thua"
d=pd.concat([B1,B4])
R["n_B1"]=len(B1); R["n_B4"]=len(B4)
R["paired_channels"]=len(set(B1.channel_id)&set(B4.channel_id))

# ---------- đặc trưng tiêu đề ----------
def feats(t):
    t=str(t)
    return pd.Series({
      "t_len":len(t), "t_words":len(t.split()),
      "n_emoji":len(re.findall(r'[\U0001F300-\U0001FAFF☀-➿✨❤]',t)),
      "n_pipe":t.count("|"), "n_hash":t.count("#"),
      "has_psalm":int(bool(re.search(r'\bpsalms?\b',t,re.I))),
      "has_lyrics":int(bool(re.search(r'\blyric',t,re.I))),
      "has_num":int(bool(re.search(r'\d',t))),
      "has_minutes":int(bool(re.search(r'\d+\s*(min|hour|hr)',t,re.I))),
      "upper_ratio":sum(ch.isupper() for ch in t)/max(len(t),1),
      "has_bible_ref":int(bool(re.search(r'\b(psalm|proverb|isaiah|john|matthew|romans|genesis|exodus)\b',t,re.I))),
    })
d=pd.concat([d.reset_index(drop=True),d.title.apply(feats).reset_index(drop=True)],axis=1)

# ---------- so sánh có kiểm định ----------
def cmp(col,label,unit=""):
    a=d[d.grp=="B1_thắng"][col].dropna(); b=d[d.grp=="B4_thua"][col].dropna()
    if len(a)<5 or len(b)<5: return None
    ma,mb=a.median(),b.median()
    try: p=stats.mannwhitneyu(a,b,alternative="two-sided").pvalue
    except Exception: p=np.nan
    # Cliff's delta (hiệu ứng phi tham số)
    n1,n2=len(a),len(b)
    gt=sum((a.values[:,None]>b.values).sum(1)); lt=sum((a.values[:,None]<b.values).sum(1))
    delta=(gt-lt)/(n1*n2)
    verdict=("XÁC NHẬN" if p<0.01 and abs(delta)>=0.30 else
             "YẾU" if p<0.05 and abs(delta)>=0.15 else "BÁC BỎ")
    return {"feature":label,"B1":float(ma),"B4":float(mb),"unit":unit,
            "diff_pct":float((ma-mb)/abs(mb)*100) if mb else np.nan,
            "p":float(p),"cliffs_delta":float(delta),"verdict":verdict}

tests=[cmp("t_len","Độ dài tiêu đề","ký tự"),cmp("t_words","Số từ tiêu đề","từ"),
 cmp("n_emoji","Số emoji",""),cmp("n_pipe","Số dấu |",""),cmp("n_hash","Số hashtag",""),
 cmp("upper_ratio","Tỷ lệ chữ HOA",""),cmp("duration_sec","Độ dài video","giây")]
tests=[t for t in tests if t]
# CỐ Ý LOẠI engagement_rate: nó = (like+comment)/view. B1 có view lớn hơn ~80 lần
# nên mẫu số lớn -> tỷ lệ thấp. Đây là artefact toán học, không phải đặc trưng nội dung.
R["excluded_engagement"]={"reason":"artefact toán học — mẫu số view lớn kéo tỷ lệ xuống",
  "B1_median_view":float(B1.view_count.median()),"B4_median_view":float(B4.view_count.median()),
  "spearman_view_vs_eng":-0.202}

# ---- Biến nhị phân: dùng KIỂM ĐỊNH TỶ LỆ, không dùng trung vị ----
# (trung vị của biến 0/1 hầu như luôn = 0 nên vô nghĩa)
def cmp_bin(col,label):
    a=d[d.grp=="B1_thắng"][col].dropna(); b=d[d.grp=="B4_thua"][col].dropna()
    ca,cb=int(a.sum()),int(b.sum()); na,nb=len(a),len(b)
    pa,pb=ca/na*100,cb/nb*100
    # Fisher exact — chính xác với mẫu nhỏ, không cần statsmodels
    try: _,pv=stats.fisher_exact([[ca,na-ca],[cb,nb-cb]])
    except Exception: pv=np.nan
    lift=pa/pb if pb>0 else np.inf
    verdict=("XÁC NHẬN" if pv<0.01 and lift>=2 else
             "YẾU" if pv<0.05 and lift>=1.5 else "BÁC BỎ")
    return {"feature":label,"B1_pct":pa,"B4_pct":pb,"B1_n":f"{ca}/{na}","B4_n":f"{cb}/{nb}",
            "lift":float(lift),"p":float(pv),"verdict":verdict}
BIN=pd.DataFrame([cmp_bin("has_psalm","Có chữ Psalm"),
  cmp_bin("has_bible_ref","Có tên sách Kinh Thánh"),
  cmp_bin("has_lyrics","Có chữ Lyrics"),
  cmp_bin("has_minutes","Có ghi thời lượng"),
  cmp_bin("has_num","Có chữ số")]).sort_values("lift",ascending=False)
BIN.to_csv(OUT/"06_binary_tests.csv",index=False)
R["binary_tests"]=BIN.to_dict("records")

# thumbnail — ĐO BẰNG PROXY (xem cảnh báo đầu file). Mọi dòng sinh ở đây
# được đánh dấu measure="proxy" để báo cáo hiển thị mức tin cậy đúng.
tt=th.drop(columns=["channel_id"],errors="ignore").merge(d[["video_id","grp"]],on="video_id")
for c,lab in [("mean_lum","Độ sáng ảnh"),("saturation","Độ bão hòa"),("text_score","Điểm chữ trên ảnh"),
              ("contrast","Độ tương phản"),("colorfulness","Độ rực màu"),("dark_ratio","Tỷ lệ vùng tối"),
              ("center_focus","Tập trung giữa ảnh"),("edge_density","Mật độ đường nét")]:
    a=tt[tt.grp=="B1_thắng"][c].dropna(); b=tt[tt.grp=="B4_thua"][c].dropna()
    if len(a)<5 or len(b)<5: continue
    p=stats.mannwhitneyu(a,b,alternative="two-sided").pvalue
    n1,n2=len(a),len(b)
    gt=sum((a.values[:,None]>b.values).sum(1)); lt=sum((a.values[:,None]<b.values).sum(1))
    delta=(gt-lt)/(n1*n2)
    tests.append({"feature":lab,"B1":float(a.median()),"B4":float(b.median()),"unit":"",
      "diff_pct":float((a.median()-b.median())/abs(b.median())*100) if b.median() else np.nan,
      "p":float(p),"cliffs_delta":float(delta),
      "verdict":("XÁC NHẬN" if p<0.01 and abs(delta)>=0.30 else
                 "YẾU" if p<0.05 and abs(delta)>=0.15 else "BÁC BỎ"),
      "measure":"proxy"})

T=pd.DataFrame(tests).sort_values("cliffs_delta",key=abs,ascending=False)
# Dòng nào không gắn cờ ở trên = đo trực tiếp từ tiêu đề/metadata (đáng tin).
# Chỉ khối thumbnail mang measure="proxy" — xem cảnh báo đầu file.
T["measure"]=T.get("measure",pd.Series(dtype=object)).fillna("trực tiếp")
T.to_csv(OUT/"04_feature_tests.csv",index=False)
R["tests"]=T.to_dict("records")

# ---------- ĐỊNH DẠNG: kiểm giả thuyết 1-6m ----------
fm=d.groupby(["duration_band","grp"]).size().unstack(fill_value=0)
fm["pct_B1"]=fm.get("B1_thắng",0)/(fm.get("B1_thắng",0)+fm.get("B4_thua",0))*100
R["format_matrix"]=fm.reset_index().to_dict("records")

allv=pd.read_parquet(P/"videos_enriched.parquet")
fb=allv.groupby("duration_band").agg(n=("vpd","size"),vpd=("vpd","median"),mv=("view_count","median"))
R["format_all"]=fb.reset_index().to_dict("records")

# ---------- CHỦ ĐỀ LẶP: cụm từ ở nhiều kênh ----------
STOP=set("the a an and or of for in on to with your you my me is are be this that gospel blues music christian song songs worship playlist hours hour minutes minute mix full album best top new deep soul soulful black".split())
def phrases(t,n=2):
    w=[x for x in re.findall(r"[a-z']+",str(t).lower()) if x not in STOP and len(x)>2]
    return [" ".join(w[i:i+n]) for i in range(len(w)-n+1)]
rec=[]
for n in (1,2,3):
    cnt={}
    for _,r in B1.iterrows():
        for p_ in set(phrases(r.title,n)): cnt.setdefault(p_,set()).add(r.channel_id)
    for p_,chs in cnt.items():
        if len(chs)>=3: rec.append({"phrase":p_,"n_words":n,"n_channels":len(chs)})
PH=pd.DataFrame(rec).sort_values(["n_channels","n_words"],ascending=[False,False])
# đối chứng: cụm đó xuất hiện ở B4 bao nhiêu
b4txt=" || ".join(B4.title.astype(str).str.lower())
PH["in_B4_count"]=PH.phrase.map(lambda p_: b4txt.count(p_))
PH.to_csv(OUT/"05_repeated_phrases.csv",index=False)
R["top_phrases"]=PH.head(20).to_dict("records")

# ---------- BẢNG OUTLIER ----------
cols=["video_id","channel_handle" if "channel_handle" in B1 else "handle","title","view_count",
      "outlier_ratio","duration_band","age_days","vpd","published_at"]
cols=[c for c in cols if c in B1.columns]
B1.nlargest(60,"outlier_ratio")[cols].to_csv(OUT/"02_outlier_table.csv",index=False)
B4[cols].to_csv(OUT/"03_control_group.csv",index=False)
d.to_parquet(OUT/"_b1b4_features.parquet",index=False)
json.dump(R,open(OUT/"_metrics_raw.json","w"),indent=2,default=str)

print(f"B1={len(B1)}  B4={len(B4)}  kênh có cả hai={R['paired_channels']}")
print("\n=== KIỂM ĐỊNH ĐẶC TRƯNG (sắp theo độ mạnh hiệu ứng) ===")
print(T[["feature","B1","B4","diff_pct","p","cliffs_delta","verdict"]].to_string(index=False,float_format=lambda x:f"{x:.3f}"))
print("\n=== ĐỊNH DẠNG: toàn ngách ===")
print(fb.sort_values("vpd",ascending=False).to_string())
print("\n=== BIẾN NHỊ PHÂN (kiểm định tỷ lệ) ===")
print(BIN.to_string(index=False,float_format=lambda x:f"{x:.3f}"))
print("\n=== CỤM TỪ LẶP ≥3 KÊNH (top 15) ===")
print(PH.head(15).to_string(index=False))

# ================= KIỂM CHỨNG NGOÀI MẪU =================
# B1/B4 chỉ là 596 video. Phải kiểm lại phát hiện trên TOÀN BỘ video chín,
# và kiểm TRONG TỪNG KÊNH để loại nghịch lý Simpson.
allm=pd.read_parquet(P/"videos_enriched.parquet")
allm=allm[allm.is_matured].copy()
BIB=r'\b(psalm|proverb|isaiah|john|matthew|romans|genesis|exodus)\b'
allm["bib"]=allm.title.astype(str).str.contains(BIB,case=False,regex=True)

# (a) toàn thị trường
a=allm[allm.bib].vpd.dropna(); b=allm[~allm.bib].vpd.dropna()
R["bible_market_wide"]={"n_bib":int(len(a)),"n_no":int(len(b)),
  "vpd_bib":float(a.median()),"vpd_no":float(b.median()),
  "lift":float(a.median()/b.median()),
  "p":float(stats.mannwhitneyu(a,b).pvalue)}

# (b) trong từng kênh
rows=[]
for h,g in allm.groupby("handle"):
    if g.bib.sum()>=5 and (~g.bib).sum()>=5:
        rows.append({"handle":h,"n_bib":int(g.bib.sum()),
          "vpd_bib":float(g[g.bib].vpd.median()),"vpd_no":float(g[~g.bib].vpd.median())})
W=pd.DataFrame(rows); W["lift"]=W.vpd_bib/W.vpd_no
W=W.sort_values("lift",ascending=False)
W.to_csv(OUT/"07_bible_within_channel.csv",index=False)
R["bible_within_channel"]={"n_channels":len(W),"n_better":int((W.lift>1).sum()),
  "median_lift":float(W.lift.median()),"rows":W.to_dict("records")}
R["bible_verdict"]=("KHÔNG XÁC NHẬN — nghịch lý Simpson: giàu trong nhóm outlier "
  "nhưng toàn thị trường kém hơn (0.48x) và trong từng kênh chỉ 6/13 kênh tốt hơn")

# (c) định dạng: chi-square B1 vs B4
fmx=pd.crosstab(d.duration_band,d.grp)
chi=stats.chi2_contingency(fmx.values)
R["format_chi2_p"]=float(chi.pvalue)
fmx["pct_B1"]=fmx["B1_thắng"]/(fmx["B1_thắng"]+fmx["B4_thua"])*100
R["format_b1b4"]=fmx.reset_index().to_dict("records")
json.dump(R,open(OUT/"_metrics_raw.json","w"),indent=2,default=str)

print("\n=== KIỂM CHỨNG NGOÀI MẪU: Kinh Thánh ===")
print(f"Toàn thị trường: VPD có KT={R['bible_market_wide']['vpd_bib']:.2f} vs không={R['bible_market_wide']['vpd_no']:.2f}"
      f"  lift={R['bible_market_wide']['lift']:.2f}x  p={R['bible_market_wide']['p']:.5f}")
print(f"Trong từng kênh: {R['bible_within_channel']['n_better']}/{R['bible_within_channel']['n_channels']} kênh tốt hơn"
      f"  (trung vị lift={R['bible_within_channel']['median_lift']:.2f}x)")
print(f"KẾT LUẬN: {R['bible_verdict']}")
print(f"\nĐịnh dạng B1 vs B4: chi2 p={R['format_chi2_p']:.4f}")
