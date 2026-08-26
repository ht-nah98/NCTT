import pandas as pd,numpy as np,matplotlib,warnings,json
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
warnings.filterwarnings("ignore")
N=Path("niches/christian-blues"); OUT=N/"99_report"
plt.rcParams.update({"font.size":9,"axes.spines.top":False,"axes.spines.right":False,
 "figure.dpi":150,"axes.grid":True,"grid.alpha":.25,"grid.linewidth":.6})
ACC="#8C3A2B";OK="#2F6B4F";WARN="#B8860B";MUTE="#9A8E85";CRIT="#9B2C2C"
B=pd.read_csv(OUT/"backtest_rubric.csv"); S=json.load(open(OUT/"_synthesis.json"))
SC=json.load(open(N/"_state/scores.json"))

# 1. Backtest: nhất quán
d=B.dropna(subset=["T3_proxy","T3_old"]).sort_values("top20_pct")
fig,ax=plt.subplots(figsize=(6.4,3.4))
ax.scatter(d.top20_pct,d.T3_old,s=45,color=CRIT,alpha=.75,label="Bảng thủ công cũ",zorder=3)
ax.plot(d.top20_pct,d.T3_proxy,color=OK,lw=2,marker="o",ms=4,label="Rubric mới (có ngưỡng)",zorder=2)
ax.set_xlabel("Tỷ trọng view của top 20% kênh (%)");ax.set_ylabel("Điểm cửa gia nhập")
ax.set_title("Backtest: rubric mới cho điểm nhất quán, bảng cũ thì không",fontweight="bold",fontsize=10)
ax.legend(frameon=False,fontsize=8)
ax.annotate("cùng ~60% nhưng\ncũ cho 2,3,4,5 điểm",xy=(60,3.5),xytext=(64,4.6),
  fontsize=7,color=CRIT,arrowprops=dict(arrowstyle="->",color=CRIT,lw=.8))
plt.tight_layout();plt.savefig(OUT/"s1_backtest.png",bbox_inches="tight");plt.close()

# 2. Hành trình điểm số qua các bước
steps=["T1\nQuy mô","T2\nĐộng lượng","T3\nCửa vào","T4\nPhù hợp AI","T5\nKiếm tiền","T6\nRủi ro"]
vals=[SC["axes"][k]["score"] for k in ["T1","T2","T3","T4","T5"]]+[SC["T6"]["penalty"]]
cols=[MUTE if v<3 else WARN if v<4 else OK for v in vals[:5]]+[CRIT]
fig,ax=plt.subplots(figsize=(6.4,2.9))
bars=ax.bar(steps,vals,color=cols,alpha=.9)
ax.axhline(0,color="#1A1614",lw=.8)
for b_,v in zip(bars,vals): ax.text(b_.get_x()+b_.get_width()/2,v+(.15 if v>=0 else -.35),
  f"{v:g}",ha="center",fontsize=8.5,fontweight="bold")
ax.set_ylabel("điểm (0-5)");ax.set_ylim(-2.8,5.6)
ax.set_title("Điểm 6 trục — mạnh ở cửa vào & AI, yếu ở quy mô & rủi ro",fontweight="bold",fontsize=10)
ax.tick_params(labelsize=7.5)
plt.tight_layout();plt.savefig(OUT/"s2_axes.png",bbox_inches="tight");plt.close()

# 3. Mốc chuẩn — kênh mới cần đạt gì
b=S["benchmarks"]
lv=["P25\n(yếu)","P50\n(trung vị)","P75\n(khá)","P90\n(top)"]
vv=[b["p25_vpm"],b["p50_vpm"],b["p75_vpm"],b["p90_vpm"]]
fig,ax=plt.subplots(figsize=(5.6,2.9))
cols=[MUTE,ACC,OK,OK]
ax.bar(lv,[x/1000 for x in vv],color=cols,alpha=.9)
ax.axhline(100,ls="--",color=CRIT,lw=1.2)
ax.text(-.45,108,"ngưỡng thành công 100k",fontsize=7,color=CRIT)
for i,x in enumerate(vv): ax.text(i,x/1000+12,f"{x/1000:,.0f}k",ha="center",fontsize=8)
ax.set_ylabel("nghìn view / tháng")
ax.set_title("Mốc chuẩn từ 53 kênh thật trong ngách",fontweight="bold",fontsize=10)
plt.tight_layout();plt.savefig(OUT/"s3_benchmarks.png",bbox_inches="tight");plt.close()
print("charts08 OK")
