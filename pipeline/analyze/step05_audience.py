"""STEP_05 — Chân dung khách hàng từ bình luận. Chỉ ghi thuộc tính TỰ KHAI."""
import pandas as pd, numpy as np, json, re, warnings
import sys
from pathlib import Path
warnings.filterwarnings("ignore")

N=Path(sys.argv[1] if len(sys.argv)>1 else "niches/christian-blues"); P=N/"00_input/processed"; OUT=N/"05_audience"
OUT.mkdir(exist_ok=True)
c=pd.read_parquet(P/"selected_comments.parquet")
R={}
c["t"]=c.text.astype(str)
c["low"]=c.t.str.lower()

# ---- loại nhiễu: lời cầu nguyện dài, chép lyrics, spam kinh ----
noise=(c.low.str.count(r'\n')>=6) | c.low.str.contains(r'purgatory|st\. gertrude|prayer for (venezuela|the dead)',regex=True)
lyric=c.low.str.contains(r'verse\s*:|chorus\s*:|\d+:\d{2}\s*-',regex=True)
c["is_noise"]=noise|lyric
R["n_total"]=len(c); R["n_noise"]=int(c.is_noise.sum())
d=c[~c.is_noise].copy()
R["n_analyzed"]=len(d)

# ================= 1. THUỘC TÍNH TỰ KHAI =================
AGE=re.compile(r"\bi(?:'m| am)\s+(\d{2})\b|\b(\d{2})\s*(?:years?\s*old|yrs?\s*old|yo)\b",re.I)
def age_of(t):
    m=AGE.search(t)
    if not m: return np.nan
    a=int(m.group(1) or m.group(2))
    return a if 13<=a<=99 else np.nan
d["age"]=d.t.map(age_of)
ages=d.age.dropna()
R["age"]={"n":int(len(ages)),"median":float(ages.median()),
 "mean":float(ages.mean()),"min":int(ages.min()),"max":int(ages.max()),
 "dist":{k:int(v) for k,v in pd.cut(ages,[12,29,44,59,74,99],
   labels=["13-29","30-44","45-59","60-74","75+"]).value_counts().sort_index().items()}}

PAT={
 "retired":     r"\bi(?:'m| am)\s+retired\b|\bsince i retired\b|\bin my retirement\b",
 "musician":    r"\bi(?:'m| am)\s+a\s+(?:musician|guitar|bass|drummer|singer|songwriter|lyricist)|\bi\s+play\s+(?:guitar|bass|drums|piano)\b",
 "trucker":     r"\bi(?:'m| am)\s+a\s+truck|\btrucker\b|\bon the road\b.*\bdriv",
 "veteran":     r"\bi(?:'m| am)\s+a\s+(?:veteran|vet)\b|\bserved in the (?:army|navy|military)\b",
 "disabled":    r"\bi(?:'m| am)\s+(?:disabled|handicapped)\b|\bmy disability\b",
 "nurse_care":  r"\bi(?:'m| am)\s+a\s+(?:nurse|caregiver|caretaker)\b",
 "widow":       r"\bi(?:'m| am)\s+a\s+widow|\bmy (?:late )?(?:husband|wife) (?:passed|died)\b",
 "recovery":    r"\b(?:in|my) recovery\b|\bsober\b|\bsobriety\b|\baddiction\b|\bAA\b",
 "new_convert": r"\b(?:got|been) saved\b|\bgave my life to (?:christ|jesus)\b|\bborn again\b|\bcame to (?:christ|the lord)\b",
 "longtime_faith": r"\b(?:walking|walked) with the lord for\b|\b\d+\s*years? (?:in|of) (?:the )?(?:faith|christ|ministry)\b",
}
for k,p_ in PAT.items(): d[k]=d.low.str.contains(p_,regex=True)
R["attributes"]={k:{"n":int(d[k].sum()),"pct":float(d[k].mean()*100)} for k in PAT}

# ================= 2. NỖI ĐAU / KHOẢNG TRỐNG =================
PAIN={
 "finally":   r"\bfinally\b|\bat last\b|\bbeen (?:looking|searching) for\b",
 "cant_stand":r"\bcan'?t stand\b|\btired of\b|\bsick of\b|\bhate the lyrics\b",
 "never_heard":r"\bnever heard\b|\bnever found\b|\bnever knew\b|\bfirst time i(?:'ve)? heard\b",
 "struggling":r"\bstrugglin|\bgoing through\b|\bhard time\b|\bdark (?:place|time|season)\b",
 "better_than":r"\bbetter than\b|\bmore than (?:any|most)\b|\bnothing (?:else )?compares\b",
 "healing":   r"\bheal(?:ed|ing|s)?\b|\bcomfort(?:ed|ing)?\b|\bpeace\b.*\bsoul\b|\bballed?\b|\btears\b|\bcrying\b",
}
for k,p_ in PAIN.items(): d[k]=d.low.str.contains(p_,regex=True)
R["pain"]={k:{"n":int(d[k].sum()),"pct":float(d[k].mean()*100),
  "med_likes":float(d[d[k]].like_count.median()) if d[k].sum() else 0} for k in PAIN}

# ================= 3. BỐI CẢNH NGHE =================
CTX={
 "driving":   r"\bdriv(?:e|ing)\b|\bin (?:my|the) (?:car|truck)\b|\broad trip\b|\bcommut",
 "housework": r"\b(?:clean|cook|dishes|chores|around the house|housework)\b",
 "work":      r"\bat work\b|\bwhile (?:i )?work\b|\bon the job\b|\bin (?:my )?office\b",
 "sleep_night":r"\b(?:fall(?:ing)? asleep|bedtime|at night|can'?t sleep|insomnia|3 ?am)\b",
 "prayer_devo":r"\b(?:pray(?:er|ing)?|devotion|quiet time|bible study|meditat)\b",
 "morning":   r"\b(?:every )?morning\b|\bstart (?:my|the) day\b",
 "sick_hosp": r"\b(?:hospital|chemo|cancer|surgery|in pain|hospice)\b",
 "grief":     r"\b(?:passed away|funeral|lost my|grie(?:f|ving)|miss (?:him|her) so)\b",
}
for k,p_ in CTX.items(): d[k]=d.low.str.contains(p_,regex=True)
R["context"]={k:{"n":int(d[k].sum()),"pct":float(d[k].mean()*100)} for k in CTX}

# ================= 4. ĐƯỜNG ĐẾN VIDEO =================
DISC={
 "algorithm": r"\balgorithm\b|\byoutube (?:brought|sent|recommend)|\bpopped up\b|\bshowed up (?:in|on) my\b|\bcame across\b|\bstumbled (?:up)?on\b",
 "searched":  r"\bi (?:was )?(?:searching|looking) for\b|\bgoogled\b|\bsearched for\b",
 "shared":    r"\b(?:my|a) (?:friend|wife|husband|daughter|son|sister|brother|pastor) (?:sent|shared|told)\b|\bshared (?:this|it) with\b",
 "subscribed":r"\bjust subscribed\b|\bnew subscriber\b|\bsubscribed\b",
 "repeat":    r"\bon repeat\b|\bevery day\b|\blisten (?:to this )?(?:daily|every)\b|\bcome back to this\b",
}
for k,p_ in DISC.items(): d[k]=d.low.str.contains(p_,regex=True)
R["discovery"]={k:{"n":int(d[k].sum()),"pct":float(d[k].mean()*100)} for k in DISC}

# ================= 5. NGÔN NGỮ KHÁCH HÀNG =================
STOP=set("""the a an and or of for in on to with your you my me is are be this that it i we he she they
them his her its was were been being have has had do does did will would can could should may might must
so but if then than as at by from up out no not all any some more most other into over after before
very just too also only own same such own now here there when where who whom which what why how""".split())
words=re.findall(r"[a-z']{3,}"," ".join(d.low))
wf=pd.Series([w for w in words if w not in STOP]).value_counts()
R["vocab_top"]={k:int(v) for k,v in wf.head(40).items()}

# ================= 6. NGÂN HÀNG TRÍCH DẪN =================
def score(r):
    s=np.log1p(r.like_count)*2
    for k in PAIN: s+= 3 if r[k] else 0
    for k in PAT:  s+= 2 if r[k] else 0
    for k in CTX:  s+= 1 if r[k] else 0
    if 80<=r.tlen<=600: s+=2
    return s
d["qscore"]=d.apply(score,axis=1)
QB=d.nlargest(120,"qscore")[["comment_id","video_id","like_count","tlen","t"]+list(PAIN)+list(PAT)+list(CTX)]
QB=QB.rename(columns={"t":"text"})
QB.to_csv(OUT/"03_quote_bank.csv",index=False)

# ================= 7. PHÂN CỤM PERSONA =================
d["p_elder"]   = (d.age>=60) | d.retired | d.widow
d["p_music"]   = d.musician
d["p_healing"] = d.struggling | d.healing | d.grief | d.sick_hosp | d.recovery
d["p_convert"] = d.new_convert | d.cant_stand
seg={k:{"n":int(d[k].sum()),"pct":float(d[k].mean()*100),
        "med_likes":float(d[d[k]].like_count.median()) if d[k].sum() else 0}
     for k in ["p_elder","p_music","p_healing","p_convert"]}
R["personas"]=seg

# ---- KIỂM ĐỊNH: tín hiệu nào được cộng đồng đồng tình thật? ----
from scipy import stats as st
base=float(d.like_count.median())
sig=[]
for k in ["finally","never_heard","cant_stand","better_than","struggling","healing",
          "p_elder","p_music","p_convert","p_healing"]:
    a=d[d[k]].like_count; b=d[~d[k]].like_count
    if len(a)<3: continue
    pv=float(st.mannwhitneyu(a,b,alternative="greater").pvalue)
    sig.append({"signal":k,"n":int(len(a)),"like_median":float(a.median()),
      "vs_baseline":float(a.median()/base) if base else np.nan,"p":pv,
      "verdict":"XÁC NHẬN" if pv<0.001 and a.median()>=base*2 else
                "YẾU" if pv<0.05 else "BÁC BỎ"})
SIG=pd.DataFrame(sig).sort_values("vs_baseline",ascending=False)
SIG.to_csv(OUT/"04_signal_tests.csv",index=False)
R["baseline_likes"]=base
R["signal_tests"]=SIG.to_dict("records")
d.to_parquet(OUT/"_comments_tagged.parquet",index=False)
json.dump(R,open(OUT/"_metrics_raw.json","w"),indent=2,default=str)

print(f"Tổng {R['n_total']} | loại nhiễu {R['n_noise']} | phân tích {R['n_analyzed']}")
print(f"\n=== TUỔI TỰ KHAI (n={R['age']['n']}) trung vị {R['age']['median']:.0f} ===")
for k,v in R["age"]["dist"].items(): print(f"  {k:8} {v:>3}")
print("\n=== THUỘC TÍNH TỰ KHAI ===")
for k,v in sorted(R["attributes"].items(),key=lambda x:-x[1]["n"]):
    print(f"  {k:18} {v['n']:>4}  {v['pct']:>5.2f}%")
print("\n=== NỖI ĐAU ===")
for k,v in sorted(R["pain"].items(),key=lambda x:-x[1]["n"]):
    print(f"  {k:14} {v['n']:>4}  {v['pct']:>5.2f}%  like TV={v['med_likes']:.0f}")
print("\n=== BỐI CẢNH NGHE ===")
for k,v in sorted(R["context"].items(),key=lambda x:-x[1]["n"]):
    print(f"  {k:14} {v['n']:>4}  {v['pct']:>5.2f}%")
print("\n=== ĐƯỜNG ĐẾN VIDEO ===")
for k,v in sorted(R["discovery"].items(),key=lambda x:-x[1]["n"]):
    print(f"  {k:12} {v['n']:>4}  {v['pct']:>5.2f}%")
print("\n=== PERSONA ===")
for k,v in sorted(R["personas"].items(),key=lambda x:-x[1]["n"]):
    print(f"  {k:12} {v['n']:>4}  {v['pct']:>5.2f}%  like TV={v['med_likes']:.0f}")
