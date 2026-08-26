import pandas as pd,numpy as np,matplotlib,warnings,json
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
warnings.filterwarnings("ignore")
N=Path("niches/christian-blues"); OUT=N/"06_keyword"
plt.rcParams.update({"font.size":9,"axes.spines.top":False,"axes.spines.right":False,
 "figure.dpi":150,"axes.grid":True,"grid.alpha":.25,"grid.linewidth":.6})
ACC="#8C3A2B";OK="#2F6B4F";WARN="#B8860B";MUTE="#9A8E85";CRIT="#9B2C2C"
R=json.load(open(OUT/"_metrics_raw.json"))
TH=pd.read_csv(OUT/"02_theme_scores.csv"); G=pd.read_csv(OUT/"03_voice_gap.csv")

LBL={"old_school":"Old-school / vintage","thanks":"Tạ ơn / biết ơn","testimony":"Lời chứng",
"presence":"Sự hiện diện","peace_rest":"Bình an / nghỉ ngơi","deliverance":"Giải thoát",
"grace_mercy":"Ân điển / thương xót","sorrow_pain":"Đau buồn","prayer":"Cầu nguyện",
"hope_faith":"Hy vọng / đức tin","morning":"Buổi sáng","healing":"Chữa lành",
"strength":"Sức mạnh","scripture":"Kinh Thánh","night_sleep":"Đêm / ngủ","instrumental":"Không lời"}

# 1. Theme lift
T=TH.sort_values("lift")
cols=[OK if v=="XÁC NHẬN" else WARN if v=="YẾU" else CRIT if v=="TRÁNH" else MUTE for v in T.verdict]
fig,ax=plt.subplots(figsize=(6.4,4.2))
ax.barh([LBL.get(x,x) for x in T.theme],T.lift,color=cols,alpha=.9)
ax.axvline(1,ls="--",color="#1A1614",lw=1.2)
ax.text(1.03,-.7,"= mức trung bình",fontsize=7)
ax.set_xlabel("VPD chủ đề ÷ VPD các video khác")
ax.set_title("Chủ đề nào thật sự hiệu quả",fontweight="bold",fontsize=10)
ax.tick_params(labelsize=8)
plt.tight_layout();plt.savefig(OUT/"c1_themes.png",bbox_inches="tight");plt.close()

# 2. Thị phần vs hiệu quả
fig,ax=plt.subplots(figsize=(6.2,3.8))
for _,r in TH.iterrows():
    c=OK if r.verdict=="XÁC NHẬN" else WARN if r.verdict=="YẾU" else CRIT if r.verdict=="TRÁNH" else MUTE
    ax.scatter(r.share_pct,r.lift,s=60,color=c,alpha=.85,edgecolors="white",linewidths=.6)
    ax.annotate(LBL.get(r.theme,r.theme),(r.share_pct,r.lift),fontsize=6.5,
                xytext=(4,3),textcoords="offset points")
ax.axhline(1,ls="--",color="#1A1614",lw=1)
ax.set_xlabel("% video trong ngách dùng chủ đề này (mức cạnh tranh)")
ax.set_ylabel("Hiệu quả (lift)")
ax.set_title("Khoảng trống: hiệu quả cao + ít người làm",fontweight="bold",fontsize=10)
plt.tight_layout();plt.savefig(OUT/"c2_gap_map.png",bbox_inches="tight");plt.close()

# 3. Voice gap
g=G.head(10).sort_values("ratio")
fig,ax=plt.subplots(figsize=(5.8,3.2))
ax.barh(g.word,g.ratio,color=ACC,alpha=.85)
ax.set_xscale("log")
ax.set_xlabel("Số lần trong bình luận ÷ số lần trong tiêu đề (thang log)")
ax.set_title("Từ khách hàng nói nhiều nhưng tiêu đề ít dùng",fontweight="bold",fontsize=10)
ax.tick_params(labelsize=8)
plt.tight_layout();plt.savefig(OUT/"c3_voice_gap.png",bbox_inches="tight");plt.close()

# 4. Tag winners
tw=pd.DataFrame(R["tags_only_in_winners"][:12]).sort_values("freq")
fig,ax=plt.subplots(figsize=(5.8,3.2))
ax.barh(tw.tag,tw.freq,color=OK,alpha=.85)
ax.set_xlabel("số lần xuất hiện trong ngách")
ax.set_title("Tag chỉ xuất hiện ở video thắng",fontweight="bold",fontsize=10)
ax.tick_params(labelsize=7.5)
plt.tight_layout();plt.savefig(OUT/"c4_tags.png",bbox_inches="tight");plt.close()
print("charts06 OK")
