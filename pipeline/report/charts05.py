import pandas as pd,numpy as np,matplotlib,warnings,json
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
warnings.filterwarnings("ignore")
N=Path("niches/christian-blues"); OUT=N/"05_audience"
plt.rcParams.update({"font.size":9,"axes.spines.top":False,"axes.spines.right":False,
 "figure.dpi":150,"axes.grid":True,"grid.alpha":.25,"grid.linewidth":.6})
ACC="#8C3A2B";OK="#2F6B4F";WARN="#B8860B";MUTE="#9A8E85";CRIT="#9B2C2C"
R=json.load(open(OUT/"_metrics_raw.json"))
d=pd.read_parquet(OUT/"_comments_tagged.parquet")
SIG=pd.read_csv(OUT/"04_signal_tests.csv")

# 1. Tuổi
ad=R["age"]["dist"]
fig,ax=plt.subplots(figsize=(5,2.9))
cols=[MUTE,MUTE,MUTE,ACC,ACC]
ax.bar(list(ad.keys()),list(ad.values()),color=cols,alpha=.9)
for i,v in enumerate(ad.values()): ax.text(i,v+.7,str(v),ha="center",fontsize=8)
ax.set_ylabel("số người tự khai");ax.set_xlabel("nhóm tuổi")
ax.set_title(f"Tuổi tự khai (n={R['age']['n']}) — trung vị {R['age']['median']:.0f}",fontweight="bold",fontsize=10)
plt.tight_layout();plt.savefig(OUT/"c1_age.png",bbox_inches="tight");plt.close()

# 2. Tín hiệu được đồng tình
S=SIG[SIG.n>=15].sort_values("vs_baseline")
lbl={"finally":"“finally / at last”","never_heard":"“never heard”","p_elder":"Người 60+ / nghỉ hưu",
 "struggling":"Đang khó khăn","better_than":"“better than”","cant_stand":"“can't stand”",
 "healing":"Chữa lành","p_healing":"Tìm chữa lành","p_convert":"Mới cải đạo"}
cols=[OK if v=="XÁC NHẬN" else WARN if v=="YẾU" else MUTE for v in S.verdict]
fig,ax=plt.subplots(figsize=(6.2,3.2))
ax.barh([lbl.get(x,x) for x in S.signal],S.vs_baseline,color=cols,alpha=.9)
ax.axvline(1,ls="--",color="#1A1614",lw=1.2)
ax.text(1.1,-.55,"= mức trung bình",fontsize=7)
ax.set_xlabel("Số like so với comment trung bình (lần)")
ax.set_title("Cộng đồng đồng tình mạnh nhất với điều gì",fontweight="bold",fontsize=10)
ax.tick_params(labelsize=8)
plt.tight_layout();plt.savefig(OUT/"c2_signals.png",bbox_inches="tight");plt.close()

# 3. Bối cảnh nghe
ctx=R["context"]; lblc={"prayer_devo":"Cầu nguyện / tĩnh tâm","morning":"Buổi sáng",
 "sick_hosp":"Bệnh tật / bệnh viện","grief":"Tang chế","driving":"Lái xe",
 "housework":"Việc nhà","work":"Nơi làm việc","sleep_night":"Đêm / khó ngủ"}
k=sorted(ctx.items(),key=lambda x:x[1]["n"])
fig,ax=plt.subplots(figsize=(5.6,3))
ax.barh([lblc.get(x[0],x[0]) for x in k],[x[1]["n"] for x in k],color=ACC,alpha=.85)
for i,(_,v) in enumerate(k): ax.text(v["n"]+8,i,f'{v["pct"]:.1f}%',va="center",fontsize=7.5)
ax.set_xlabel("số bình luận nhắc đến")
ax.set_title("Khán giả nghe trong bối cảnh nào",fontweight="bold",fontsize=10)
ax.tick_params(labelsize=8)
plt.tight_layout();plt.savefig(OUT/"c3_context.png",bbox_inches="tight");plt.close()

# 4. Đường đến video
disc=R["discovery"]; lbld={"repeat":"Nghe lặp lại / mỗi ngày","algorithm":"YouTube đề xuất",
 "subscribed":"Vừa đăng ký","shared":"Người quen chia sẻ","searched":"Chủ động tìm kiếm"}
k=sorted(disc.items(),key=lambda x:x[1]["n"])
fig,ax=plt.subplots(figsize=(5.6,2.6))
cols=[OK if x[0]=="algorithm" else MUTE for x in k]
ax.barh([lbld.get(x[0],x[0]) for x in k],[x[1]["n"] for x in k],color=cols,alpha=.85)
ax.set_xlabel("số bình luận")
ax.set_title("Khán giả đến với video bằng cách nào",fontweight="bold",fontsize=10)
ax.tick_params(labelsize=8)
plt.tight_layout();plt.savefig(OUT/"c4_discovery.png",bbox_inches="tight");plt.close()
print("charts05 OK")
