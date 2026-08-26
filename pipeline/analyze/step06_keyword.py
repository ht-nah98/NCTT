"""STEP_06 — Từ khóa & Đóng gói. Trọng tâm: CHỌN ĐỀ TÀI (không phải SEO).
Lý do đổi trọng tâm: STEP_05 cho thấy đề xuất thắng tìm kiếm 7:1."""
import pandas as pd, numpy as np, json, re, ast, warnings
import sys
from pathlib import Path
from scipy import stats
warnings.filterwarnings("ignore")

N=Path(sys.argv[1] if len(sys.argv)>1 else "niches/christian-blues"); P=N/"00_input/processed"; OUT=N/"06_keyword"
OUT.mkdir(exist_ok=True)
v=pd.read_parquet(P/"videos_enriched.parquet")
s=pd.read_parquet(P/"selected_videos.parquet")
aud=json.load(open(N/"05_audience/_metrics_raw.json"))
R={}

B1=s[s.bucket.str.contains("B1")]; B4=s[s.bucket.str.contains("B4")]
m=v[v.is_matured].copy()
R["n_B1"]=len(B1); R["n_B4"]=len(B4)

# ---------- 1. TAG ----------
def parse_tags(x):
    if pd.isna(x): return []
    try:
        t=ast.literal_eval(x) if isinstance(x,str) else x
        return [str(i).lower().replace("u0026","&").strip() for i in t]
    except Exception: return []
v["tag_list"]=v.tags.map(parse_tags)
R["tag_coverage"]=float(v.tags.notna().mean()*100)
allt=[t for L in v.tag_list for t in L]
R["tag_total"]=len(allt); R["tag_unique"]=len(set(allt))
tf=pd.Series(allt).value_counts()
R["tag_top"]={k:int(x) for k,x in tf.head(25).items()}

# tag khác biệt: B1 có, B4 không
b1t=set(t for L in v[v.video_id.isin(B1.video_id)].tag_list for t in L)
b4t=set(t for L in v[v.video_id.isin(B4.video_id)].tag_list for t in L)
only=sorted(b1t-b4t, key=lambda t:-tf.get(t,0))[:20]
R["tags_only_in_winners"]=[{"tag":t,"freq":int(tf.get(t,0))} for t in only]

# ---------- 2. HASHTAG ----------
hash_all=re.findall(r"#(\w+)"," ".join((v.title.fillna("").astype(str)+" "+v.description.fillna("").astype(str)).tolist()).lower())
hf=pd.Series(hash_all).value_counts()
R["hashtag_top"]={k:int(x) for k,x in hf.head(20).items()}
R["hashtag_total"]=len(hash_all)

# ---------- 3. CHỦ ĐỀ: đo hiệu quả THẬT trên toàn thị trường ----------
# Đây là phần trọng tâm mới — chọn đề tài, không phải SEO
THEME={
 "prayer":      r"\bpray(?:er|ing)?\b",
 "healing":     r"\bheal(?:ing|ed)?\b|\brestor",
 "peace_rest":  r"\bpeace\b|\brest\b|\bcalm\b|\bstill\b",
 "grace_mercy": r"\bgrace\b|\bmercy\b",
 "strength":    r"\bstrength\b|\bstrong\b|\bcourage\b",
 "hope_faith":  r"\bhope\b|\bfaith\b|\bbeliev",
 "sorrow_pain": r"\bsorrow\b|\bpain\b|\bbroken\b|\bweary\b|\btears?\b|\blonely\b",
 "morning":     r"\bmorning\b|\bsunrise\b|\bdawn\b",
 "night_sleep": r"\bnight\b|\bsleep\b|\bmidnight\b|\binsomnia\b",
 "thanks":      r"\bthank(?:ful|s|sgiving)?\b|\bgrateful\b|\bblessing",
 "deliverance": r"\bdeliver|\bfreedom\b|\bbreakthrough\b|\bvictory\b",
 "presence":    r"\bpresence\b|\bholy spirit\b|\banoint",
 "scripture":   r"\bpsalm|\bproverb|\bscripture\b|\bword of god\b|\bbible\b",
 "testimony":   r"\btestimony\b|\bstory\b|\bjourney\b",
 "old_school":  r"\bold(?:-| )school\b|\bvintage\b|\bclassic\b|\b19\d0s\b|\bblack gospel\b",
 "instrumental":r"\binstrumental\b|\bno lyrics\b|\bbackground\b|\bbgm\b",
}
rows=[]
base_vpd=m.vpd.median()
for k,p_ in THEME.items():
    m[k]=m.title.astype(str).str.lower().str.contains(p_,regex=True)
    a=m[m[k]]; b=m[~m[k]]
    if len(a)<20: continue
    pv=float(stats.mannwhitneyu(a.vpd.dropna(),b.vpd.dropna(),alternative="two-sided").pvalue)
    lift=float(a.vpd.median()/b.vpd.median())
    # kiểm trong từng kênh (chống Simpson) — bài học STEP_04
    wc=[]
    for h,g in m.groupby("handle"):
        if g[k].sum()>=5 and (~g[k]).sum()>=5:
            va,vb=g[g[k]].vpd.median(),g[~g[k]].vpd.median()
            if vb and vb>0: wc.append(va/vb)
    rows.append({"theme":k,"n":int(len(a)),"share_pct":float(len(a)/len(m)*100),
      "vpd_theme":float(a.vpd.median()),"vpd_other":float(b.vpd.median()),
      "lift":lift,"p":pv,"n_ch_tested":len(wc),
      "n_ch_better":int(sum(1 for x in wc if x>1)),
      "within_median_lift":float(np.median(wc)) if wc else np.nan})
TH=pd.DataFrame(rows)
def verdict(r):
    if r.p>=0.05: return "BÁC BỎ"
    if r.n_ch_tested>=5 and r.within_median_lift<1: return "BÁC BỎ (Simpson)"
    if r.lift>=1.3 and (r.n_ch_tested<5 or r.within_median_lift>=1.1): return "XÁC NHẬN"
    if r.lift>=1.15: return "YẾU"
    if r.lift<=0.8: return "TRÁNH"
    return "BÁC BỎ"
TH["verdict"]=TH.apply(verdict,axis=1)
TH=TH.sort_values("lift",ascending=False)
TH.to_csv(OUT/"02_theme_scores.csv",index=False)
R["themes"]=TH.to_dict("records")
R["base_vpd"]=float(base_vpd)

# ---------- 4. ĐỐI CHIẾU NGÔN NGỮ KHÁCH HÀNG ----------
vocab=aud["vocab_top"]
title_words=pd.Series(re.findall(r"[a-z']{3,}"," ".join(v.title.astype(str).str.lower()))).value_counts()
STOP=set("the a an and or of for in on to with your you my me is are be this that it was were""".split())
gap=[]
for w,cf in list(vocab.items())[:40]:
    if w in STOP or len(w)<4: continue
    tc=int(title_words.get(w,0))
    gap.append({"word":w,"in_comments":int(cf),"in_titles":tc,
      "ratio":float(cf/max(tc,1))})
G=pd.DataFrame(gap).sort_values("ratio",ascending=False)
G.to_csv(OUT/"03_voice_gap.csv",index=False)
R["voice_gap"]=G.head(15).to_dict("records")

# ---------- 5. MẪU TIÊU ĐỀ TỪ VIDEO THẮNG ----------
def struct(t):
    t=str(t)
    return {"n_seg":t.count("|")+1,"len":len(t),
            "has_dur":bool(re.search(r"\d+\s*(hour|hr|min)",t,re.I)),
            "has_emoji":bool(re.search(r'[\U0001F300-\U0001FAFF✝️🙏❤✨]',t))}
b1s=pd.DataFrame([struct(t) for t in B1.title])
b4s=pd.DataFrame([struct(t) for t in B4.title])
R["title_struct"]={"B1":{"med_seg":float(b1s.n_seg.median()),"med_len":float(b1s["len"].median()),
   "pct_dur":float(b1s.has_dur.mean()*100),"pct_emoji":float(b1s.has_emoji.mean()*100)},
 "B4":{"med_seg":float(b4s.n_seg.median()),"med_len":float(b4s["len"].median()),
   "pct_dur":float(b4s.has_dur.mean()*100),"pct_emoji":float(b4s.has_emoji.mean()*100)}}
R["top_titles"]=B1.nlargest(15,"outlier_ratio")[["title","view_count","outlier_ratio","duration_band"]].to_dict("records")

json.dump(R,open(OUT/"_metrics_raw.json","w"),indent=2,default=str)
print(f"tag phủ {R['tag_coverage']:.0f}% | {R['tag_unique']:,} tag khác nhau | {R['hashtag_total']:,} hashtag")
print(f"\n=== CHỦ ĐỀ: hiệu quả THẬT trên {len(m):,} video chín (VPD nền={base_vpd:.2f}) ===")
print(TH[["theme","n","share_pct","vpd_theme","lift","p","n_ch_better","n_ch_tested","within_median_lift","verdict"]]
      .to_string(index=False,float_format=lambda x:f"{x:.2f}"))
print("\n=== TAG chỉ có ở video THẮNG (top 12) ===")
for t in R["tags_only_in_winners"][:12]: print(f"  {t['freq']:>4}× {t['tag']}")
print("\n=== KHOẢNG TRỐNG NGÔN NGỮ (khách nói nhiều, title dùng ít) ===")
print(G.head(12).to_string(index=False))
