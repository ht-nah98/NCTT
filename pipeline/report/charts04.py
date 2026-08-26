import pandas as pd,numpy as np,matplotlib,warnings,json
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
warnings.filterwarnings("ignore")
N=Path("niches/christian-blues"); OUT=N/"04_outlier"
plt.rcParams.update({"font.size":9,"axes.spines.top":False,"axes.spines.right":False,
 "figure.dpi":150,"axes.grid":True,"grid.alpha":.25,"grid.linewidth":.6})
ACC="#8C3A2B";OK="#2F6B4F";WARN="#B8860B";MUTE="#9A8E85";CRIT="#9B2C2C"
T=pd.read_csv(OUT/"04_feature_tests.csv")
W=pd.read_csv(OUT/"07_bible_within_channel.csv")
R=json.load(open(OUT/"_metrics_raw.json"))

# 1. Effect size — hầu hết bị bác bỏ
T2=T.sort_values("cliffs_delta",key=abs,ascending=True).tail(14)
cols=[OK if v=="XÁC NHẬN" else WARN if v=="YẾU" else MUTE for v in T2.verdict]
fig,ax=plt.subplots(figsize=(6.4,4.2))
ax.barh(T2.feature,T2.cliffs_delta,color=cols,alpha=.9)
for x in (-.3,.3): ax.axvline(x,ls="--",color=CRIT,lw=1)
ax.axvline(0,color="#1A1614",lw=.8)
ax.text(.31,.4,"ngưỡng\nhiệu ứng\nđáng kể",fontsize=6.5,color=CRIT,va="bottom")
ax.set_xlabel("Cliff's delta (độ mạnh hiệu ứng)");ax.set_xlim(-.75,.75)
ax.set_title("Hầu hết đặc trưng KHÔNG phân biệt được thắng/thua",fontweight="bold",fontsize=10)
ax.tick_params(labelsize=7.5)
plt.tight_layout();plt.savefig(OUT/"c1_effects.png",bbox_inches="tight");plt.close()

# 2. Simpson paradox
fig,ax=plt.subplots(1,2,figsize=(9,3.2))
ax[0].bar(["Trong nhóm\noutlier (B1)","Nhóm đối\nchứng (B4)"],[10.1,1.2],color=[OK,MUTE],alpha=.9)
ax[0].set_ylabel("% video có tên sách Kinh Thánh")
ax[0].set_title("Nhìn trong mẫu B1/B4:\n'Kinh Thánh thắng' (8.1×)",fontsize=9,fontweight="bold",color=OK)
bm=R["bible_market_wide"]
ax[1].bar(["Có tên\nKinh Thánh","Không có"],[bm["vpd_bib"],bm["vpd_no"]],color=[CRIT,MUTE],alpha=.9)
ax[1].set_ylabel("VPD trung vị (view/ngày)")
ax[1].set_title("Nhưng toàn thị trường:\nkém hơn 52%",fontsize=9,fontweight="bold",color=CRIT)
for a in ax: a.tick_params(labelsize=8)
plt.suptitle("Nghịch lý Simpson — vì sao phải kiểm ngoài mẫu",fontsize=10.5,fontweight="bold",y=1.05)
plt.tight_layout();plt.savefig(OUT/"c2_simpson.png",bbox_inches="tight");plt.close()

# 3. Within-channel
W=W.sort_values("lift")
cols=[OK if l>1 else CRIT for l in W.lift]
fig,ax=plt.subplots(figsize=(6.2,3.4))
ax.barh(W.handle,W.lift,color=cols,alpha=.9)
ax.axvline(1,ls="--",color="#1A1614",lw=1.2)
ax.text(1.05,-.6,"= không khác biệt",fontsize=7,color="#1A1614")
ax.set_xlabel("VPD có Kinh Thánh ÷ VPD không có")
ax.set_title("Trong từng kênh: chỉ 6/13 kênh có lợi",fontweight="bold",fontsize=10)
ax.tick_params(labelsize=7.5)
plt.tight_layout();plt.savefig(OUT/"c3_within.png",bbox_inches="tight");plt.close()

# 4. Format
fb=pd.DataFrame(R["format_all"]).set_index("duration_band")
order=["Shorts","1-6m","6-30m","30-60m","1-3h","3h+"]
fb=fb.reindex(order)
fig,ax=plt.subplots(1,2,figsize=(9,2.9))
c1=[ACC if i in("Shorts","1-6m") else MUTE for i in fb.index]
ax[0].bar(fb.index,fb.n,color=MUTE,alpha=.8);ax[0].set_title("Thị trường ĐANG LÀM (số video)",fontsize=9,fontweight="bold")
ax[1].bar(fb.index,fb.vpd,color=c1,alpha=.9);ax[1].set_title("HIỆU QUẢ (VPD trung vị)",fontsize=9,fontweight="bold")
for a in ax: a.tick_params(axis="x",rotation=35,labelsize=7.5)
plt.tight_layout();plt.savefig(OUT/"c4_format.png",bbox_inches="tight");plt.close()
print("charts04 OK")
