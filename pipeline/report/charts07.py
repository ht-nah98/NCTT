import pandas as pd,numpy as np,matplotlib,warnings,json
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
warnings.filterwarnings("ignore")
N=Path("niches/christian-blues"); OUT=N/"07_monetization"
plt.rcParams.update({"font.size":9,"axes.spines.top":False,"axes.spines.right":False,
 "figure.dpi":150,"axes.grid":True,"grid.alpha":.25,"grid.linewidth":.6})
ACC="#8C3A2B";OK="#2F6B4F";WARN="#B8860B";MUTE="#9A8E85";CRIT="#9B2C2C"
R=json.load(open(OUT/"_metrics_raw.json"))
SC=json.load(open(N/"_state/scores.json"))

# 1. Kịch bản doanh thu
sc=R["scenarios"]; ks=["conservative","base","optimistic"]
lbl=["Thận trọng\n(phân vị 25)","Cơ sở\n(trung vị)","Lạc quan\n(phân vị 90)"]
lo=[sc[k]["rev_low"] for k in ks]; ba=[sc[k]["rev_base"] for k in ks]; hi=[sc[k]["rev_high"] for k in ks]
x=np.arange(3); w=.26
fig,ax=plt.subplots(figsize=(6.2,3.2))
ax.bar(x-w,lo,w,label="RPM $1.5",color=MUTE,alpha=.85)
ax.bar(x,ba,w,label="RPM $3.0",color=ACC,alpha=.9)
ax.bar(x+w,hi,w,label="RPM $6.0",color=OK,alpha=.85)
ax.set_xticks(x);ax.set_xticklabels(lbl,fontsize=8)
ax.set_ylabel("USD / tháng");ax.legend(frameon=False,fontsize=7.5)
ax.set_title("Doanh thu ước tính theo kịch bản",fontweight="bold",fontsize=10)
for i,vv in enumerate(ba): ax.text(i,vv+40,f"${vv:,.0f}",ha="center",fontsize=7.5,color=ACC,fontweight="bold")
plt.tight_layout();plt.savefig(OUT/"c1_revenue.png",bbox_inches="tight");plt.close()

# 2. Ad slot theo định dạng
b=pd.DataFrame(R["M5_3_band"]).set_index("duration_band")
b=b.reindex(["Shorts","1-6m","6-30m","30-60m","1-3h","3h+"])
fig,ax=plt.subplots(1,2,figsize=(9,2.9))
c1=[CRIT if s<=1 else OK for s in b.ad_slots]
ax[0].bar(b.index,b.ad_slots,color=c1,alpha=.9);ax[0].set_title("Số điểm chèn quảng cáo (ước tính)",fontsize=9,fontweight="bold")
ax[0].set_ylabel("ad slot")
ax[1].bar(b.index,b.med_view,color=MUTE,alpha=.85);ax[1].set_title("View trung vị",fontsize=9,fontweight="bold")
for a in ax: a.tick_params(axis="x",rotation=35,labelsize=7.5)
plt.tight_layout();plt.savefig(OUT/"c2_adslots.png",bbox_inches="tight");plt.close()

# 3. Rủi ro trùng lặp theo kênh
cb=pd.Series(R["cross_by_channel"]).sort_values()
fig,ax=plt.subplots(figsize=(5.8,3))
cols=[CRIT if v>=30 else WARN if v>=15 else MUTE for v in cb.values]
ax.barh(cb.index,cb.values,color=cols,alpha=.9)
ax.axvline(30,ls="--",color=CRIT,lw=1.1);ax.text(31,.2,"ngưỡng rủi ro",fontsize=7,color=CRIT)
ax.set_xlabel("% video có tiêu đề trùng với kênh khác")
ax.set_title("Rủi ro nội dung trùng lặp theo kênh",fontweight="bold",fontsize=10)
ax.tick_params(labelsize=7.5)
plt.tight_layout();plt.savefig(OUT/"c3_dup_risk.png",bbox_inches="tight");plt.close()

# 4. Radar 5 trục
ax_lbl=["T1 Quy mô","T2 Động lượng","T3 Cửa vào","T4 Phù hợp AI","T5 Kiếm tiền"]
vals=[SC["axes"][k]["score"] for k in ["T1","T2","T3","T4","T5"]]
ang=np.linspace(0,2*np.pi,len(vals),endpoint=False).tolist()
vals2=vals+vals[:1]; ang2=ang+ang[:1]
fig,ax=plt.subplots(figsize=(4.4,4),subplot_kw=dict(polar=True))
ax.plot(ang2,vals2,color=ACC,lw=2);ax.fill(ang2,vals2,color=ACC,alpha=.2)
ax.set_xticks(ang);ax.set_xticklabels(ax_lbl,fontsize=8)
ax.set_ylim(0,5);ax.set_yticks([1,2,3,4,5]);ax.set_yticklabels(["1","2","3","4","5"],fontsize=7)
ax.set_title("Điểm 5 trục (thang 0-5)",fontweight="bold",fontsize=10,pad=16)
plt.tight_layout();plt.savefig(OUT/"c4_radar.png",bbox_inches="tight");plt.close()
print("charts07 OK")
