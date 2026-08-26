"""Sinh biểu đồ cho báo cáo STEP_01+02."""
import pandas as pd, numpy as np, matplotlib, warnings, sys
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
warnings.filterwarnings("ignore")

NICHE=Path("niches/christian-blues"); P=NICHE/"00_input/processed"
OUT=NICHE/"02_market"; OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.size":9,"axes.spines.top":False,"axes.spines.right":False,
                     "figure.dpi":150,"axes.grid":True,"grid.alpha":.25,"grid.linewidth":.6})
INK="#1A1614"; ACC="#8C3A2B"; OK="#2F6B4F"; WARN="#B8860B"; MUTE="#9A8E85"

v=pd.read_parquet(P/"videos_enriched.parquet")
ch=pd.read_parquet(P/"channels_enriched.parquet")
m=v[v.is_matured].copy(); m["ym"]=m.published_at.dt.to_period("M")
top20=set(ch.nlargest(20,"view_count").channel_id)

# ---- 1. Bẫy maturation: view thô vs VPD ----
g=m.groupby("ym").agg(n=("view_count","size"),med=("view_count","median"),vpd=("vpd","median"))
g=g[g.index>=pd.Period("2025-07")]
x=[str(i) for i in g.index]
fig,ax=plt.subplots(1,2,figsize=(10,3.4))
ax[0].bar(x,g["med"],color=WARN,alpha=.85)
ax[0].set_title("View trung vị (THÔ) — có vẻ sụp",color=WARN,fontweight="bold",fontsize=10)
ax[0].set_ylabel("view/video")
ax[1].bar(x,g["vpd"],color=OK,alpha=.85)
ax[1].set_title("VPD chuẩn hóa tuổi — THỰC TẾ ổn định",color=OK,fontweight="bold",fontsize=10)
ax[1].set_ylabel("view/ngày")
for a in ax: a.tick_params(axis="x",rotation=60,labelsize=7)
plt.tight_layout(); plt.savefig(OUT/"c1_maturation_trap.png",bbox_inches="tight"); plt.close()

# ---- 2. VPD theo 3 phân khúc ----
fig,ax=plt.subplots(figsize=(9,3.4))
for lbl,d,c in [("Toàn ngách",m,MUTE),("Top 20 kênh",m[m.channel_id.isin(top20)],ACC),
                ("Kênh còn lại",m[~m.channel_id.isin(top20)],OK)]:
    s=d.groupby("ym").vpd.median(); s=s[s.index>=pd.Period("2025-07")]
    ax.plot([str(i) for i in s.index],s.values,marker="o",ms=4,label=lbl,color=c,lw=2)
ax.set_title("VPD trung vị theo tháng đăng — cả 3 phân khúc đều ĐI LÊN",fontweight="bold",fontsize=10)
ax.set_ylabel("view/ngày"); ax.legend(frameon=False,fontsize=8)
ax.tick_params(axis="x",rotation=60,labelsize=7)
plt.tight_layout(); plt.savefig(OUT/"c2_vpd_segments.png",bbox_inches="tight"); plt.close()

# ---- 3. Cung vs cầu ----
sup=m.groupby("ym").size(); dem=m.groupby("ym").view_count.sum()/1e6
sup=sup[sup.index>=pd.Period("2025-07")]; dem=dem[dem.index>=pd.Period("2025-07")]
fig,ax=plt.subplots(figsize=(9,3.2))
ax.bar([str(i) for i in sup.index],sup.values,color=MUTE,alpha=.55,label="Cung: số video")
ax.set_ylabel("số video",color=MUTE)
a2=ax.twinx(); a2.plot([str(i) for i in dem.index],dem.values,color=ACC,marker="o",ms=4,lw=2.2,label="Cầu: triệu view")
a2.set_ylabel("triệu view",color=ACC); a2.grid(False)
ax.set_title("Cung vs Cầu — cầu tăng nhanh hơn cung (M2.4 = 1.305)",fontweight="bold",fontsize=10)
ax.tick_params(axis="x",rotation=60,labelsize=7)
ax.legend(loc="upper left",frameon=False,fontsize=8); a2.legend(loc="upper right",frameon=False,fontsize=8)
plt.tight_layout(); plt.savefig(OUT/"c3_supply_demand.png",bbox_inches="tight"); plt.close()

# ---- 4. Tuổi kênh ----
bins=[0,6,12,24,60,999]; lbl=["<6th","6-12th","1-2n","2-5n",">5n"]
cnt=pd.cut(ch.channel_age_months,bins,labels=lbl).value_counts().reindex(lbl)
fig,ax=plt.subplots(figsize=(5,2.9))
cols=[OK if i<2 else MUTE for i in range(len(lbl))]
ax.bar(lbl,cnt.values,color=cols,alpha=.9)
for i,val in enumerate(cnt.values): ax.text(i,val+.6,str(val),ha="center",fontsize=8,color=INK)
ax.set_title("Tuổi kênh — 74% dưới 12 tháng",fontweight="bold",fontsize=10); ax.set_ylabel("số kênh")
plt.tight_layout(); plt.savefig(OUT/"c4_channel_age.png",bbox_inches="tight"); plt.close()

# ---- 5. Định dạng ----
b=v.groupby("duration_band").agg(n=("vpd","size"),vpd=("vpd","median")).reindex(
    ["Shorts","1-6m","6-30m","30-60m","1-3h","3h+"])
fig,ax=plt.subplots(1,2,figsize=(9,2.9))
ax[0].barh(b.index,b["n"],color=MUTE,alpha=.8); ax[0].set_title("Thị trường ĐANG LÀM (số video)",fontsize=9,fontweight="bold")
cols=[ACC if i in("Shorts","1-6m") else MUTE for i in b.index]
ax[1].barh(b.index,b["vpd"],color=cols,alpha=.9); ax[1].set_title("HIỆU QUẢ (VPD trung vị)",fontsize=9,fontweight="bold")
for a in ax: a.invert_yaxis(); a.tick_params(labelsize=8)
plt.tight_layout(); plt.savefig(OUT/"c5_format_gap.png",bbox_inches="tight"); plt.close()
print("charts OK")
