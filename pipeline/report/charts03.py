import pandas as pd, numpy as np, matplotlib, warnings
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
warnings.filterwarnings("ignore")
N=Path("niches/christian-blues"); OUT=N/"03_competitor"
plt.rcParams.update({"font.size":9,"axes.spines.top":False,"axes.spines.right":False,
 "figure.dpi":150,"axes.grid":True,"grid.alpha":.25,"grid.linewidth":.6})
INK="#1A1614";ACC="#8C3A2B";OK="#2F6B4F";WARN="#B8860B";MUTE="#9A8E85"
c=pd.read_csv(OUT/"02_channel_table.csv")

# 1. Lorenz curve
x=np.sort(c.tot_view.values); cum=np.cumsum(x)/x.sum()
p=np.arange(1,len(x)+1)/len(x)
fig,ax=plt.subplots(figsize=(4.6,3.4))
ax.plot([0,1],[0,1],"--",color=MUTE,lw=1,label="Bình đẳng tuyệt đối")
ax.plot(np.insert(p,0,0),np.insert(cum,0,0),color=ACC,lw=2.2,label="Christian Blues (Gini 0.626)")
ax.fill_between(np.insert(p,0,0),np.insert(cum,0,0),np.insert(p,0,0),color=ACC,alpha=.12)
ax.set_xlabel("% số kênh (từ nhỏ đến lớn)");ax.set_ylabel("% tổng lượt xem")
ax.set_title("Phân bố view giữa các kênh",fontweight="bold",fontsize=10)
ax.legend(frameon=False,fontsize=7.5,loc="upper left")
plt.tight_layout();plt.savefig(OUT/"c1_lorenz.png",bbox_inches="tight");plt.close()

# 2. Tuổi kênh vs views/tháng
fig,ax=plt.subplots(figsize=(5.6,3.4))
col={"ai-first":ACC,"hybrid":WARN,"artist/rebroadcast":MUTE}
for m,g in c.groupby("model"):
    ax.scatter(g.channel_age_months,g.views_per_month/1000,s=26,alpha=.8,
               color=col.get(m,MUTE),label=m,edgecolors="white",linewidths=.5)
ax.axhline(100,ls="--",color=OK,lw=1.2)
ax.text(0.5,112,"ngưỡng 100k view/tháng",fontsize=7,color=OK)
ax.set_xscale("log");ax.set_yscale("log")
ax.set_xlabel("Tuổi kênh (tháng, thang log)");ax.set_ylabel("Nghìn view/tháng (log)")
ax.set_title("Kênh trẻ vẫn đạt traction — không cần thâm niên",fontweight="bold",fontsize=10)
ax.legend(frameon=False,fontsize=7.5)
plt.tight_layout();plt.savefig(OUT/"c2_age_vs_reach.png",bbox_inches="tight");plt.close()

# 3. Nhịp đăng: đánh đổi
a=c[c.n_vid>=20].copy()
q=pd.qcut(a.per_month,4,labels=["Q1 thưa","Q2","Q3","Q4 dày"])
g=a.groupby(q).agg(vpv=("view_per_vid","median"),vpm=("views_per_month","median"))
fig,ax=plt.subplots(1,2,figsize=(8.4,2.9))
ax[0].bar(g.index.astype(str),g.vpv/1000,color=WARN,alpha=.85)
ax[0].set_title("View mỗi video (nghìn)",fontsize=9,fontweight="bold");ax[0].set_ylabel("nghìn view")
ax[1].bar(g.index.astype(str),g.vpm/1000,color=OK,alpha=.85)
ax[1].set_title("Tổng view mỗi tháng (nghìn)",fontsize=9,fontweight="bold")
for a_ in ax: a_.tick_params(labelsize=8)
plt.suptitle("Đăng dày: chất lượng/video GIẢM nhưng tổng tiếp cận TĂNG",fontsize=10,fontweight="bold",y=1.06)
plt.tight_layout();plt.savefig(OUT/"c3_cadence_tradeoff.png",bbox_inches="tight");plt.close()

# 4. Phân tầng
t=c.tier.value_counts().sort_index()
cols=[OK,OK,WARN,MUTE,"#C9BFB6"]
fig,ax=plt.subplots(figsize=(5.4,2.7))
ax.barh(t.index,t.values,color=cols[:len(t)],alpha=.9)
for i,val in enumerate(t.values): ax.text(val+.3,i,str(val),va="center",fontsize=8)
ax.invert_yaxis();ax.set_title("Phân tầng 53 kênh",fontweight="bold",fontsize=10)
ax.tick_params(labelsize=8)
plt.tight_layout();plt.savefig(OUT/"c4_tiers.png",bbox_inches="tight");plt.close()
print("charts03 OK")
