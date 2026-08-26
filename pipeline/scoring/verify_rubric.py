"""Tự kiểm: ngưỡng trong tài liệu rubric có khớp điểm đã chấm không?
Chạy sau mỗi lần sửa rubric hoặc chấm lại ngách."""
import json, sys
from pathlib import Path

N=Path(sys.argv[1] if len(sys.argv)>1 else "niches/christian-blues")
sc=json.load(open(N/"_state/scores.json")); m=json.load(open(N/"_state/metrics.json"))
W={"T1":.20,"T2":.25,"T3":.25,"T4":.15,"T5":.10}
fails=[]

def chk(axis,expected,label):
    got=sc["axes"][axis]["score"]
    ok=abs(expected-got)<0.01
    if not ok: fails.append(f"{axis}: công thức={expected} nhưng scores.json={got}")
    print(f"  {axis}  {label:52} {'✅' if ok else '❌ LỆCH'}")

v=m["market"]["M1_1_views_per_month"]
chk("T1", 5 if v>=50e6 else 4 if v>=20e6 else 3 if v>=8e6 else 2 if v>=3e6 else 1 if v>=1e6 else 0,
    f"{v:,.0f} view/tháng")
a,b=m["momentum"]["M2_1_view_growth"],m["momentum"]["M2_4_demand_supply_gap"]
chk("T2", 5 if(a>=2 and b>=1.2)else 4 if(a>=1.5 and b>=1)else 3 if a>=1.2 else 2 if a>=.9 else 1 if a>=.7 else 0,
    f"M2.1={a:.3f} M2.4={b:.3f}")
p,g=m["entry"]["M3_2_newcomer_success_pct"],m["entry"]["M3_1_gini"]
s1=5 if p>=40 else 4 if p>=25 else 3 if p>=15 else 2 if p>=8 else 1 if p>=3 else 0
s2=5 if g<=.45 else 4 if g<=.55 else 3 if g<=.65 else 2 if g<=.75 else 1 if g<=.85 else 0
# M3.3 không đo được với 1 snapshot → CHIA LẠI trọng số 0.3:0.5, KHÔNG gán 5đ.
# (Bản đầu viết `0.2*5` — thưởng điểm tối đa cho chỉ số không có dữ liệu, bẫy L5.
#  Phải khớp với apply_thresholds.py. Xem lessons_learned T25.)
m33_ok = "KHÔNG ĐO ĐƯỢC" not in str(m["entry"].get("M3_3_status", ""))
t3 = (0.5*s1+0.3*s2+0.2*5) if m33_ok else round((0.3*s2+0.5*s1)/0.8, 2)
chk("T3", t3, f"M3.2={p:.1f}%({s1}đ) Gini={g:.3f}({s2}đ)"
    + ("" if m33_ok else " · M3.3 thiếu → chia lại trọng số"))
q=m["ai_fit"]["M4_1_ai_first_top20_pct"]
chk("T4", 5 if q>=60 else 4 if q>=40 else 3 if q>=25 else 2 if q>=10 else 1, f"M4.1={q:.1f}%")
# RPM là ước tính do người phân tích nhập (STEP_07) — ngách mới có thể chưa có
_rr = m.get("money", {}).get("M5_2_rpm_range")
if _rr is None:
    print(f"  {'T5':3} {'CHƯA CÓ RPM — nhập ở STEP_07':50} ⏭")
else:
    r = _rr[1] if isinstance(_rr, list) else _rr
    chk("T5", 5 if r>=8 else 4 if r>=5 else 3 if r>=3 else 2 if r>=1.5 else 1, f"RPM=${r}")

tot=sum(sc["axes"][k]["score"]*W[k] for k in W)*4+sc["T6"]["penalty"]
ok=abs(tot-sc["total_score"])<0.01
if not ok: fails.append(f"TỔNG: {tot:.2f} vs {sc['total_score']}")
print(f"  TỔNG {tot:.2f} / 20{'':40}{'✅' if ok else '❌ LỆCH'}")

# kiểm _meta bắt buộc (quy tắc R3)
print("\n  Kiểm truy vết (_meta bắt buộc):")
miss=[k for k in ["T1","T2","T3","T4","T5"]
      if not all(f in sc["axes"][k] for f in ("metric","threshold","confidence","source"))]
if miss: fails.append(f"thiếu trường truy vết: {miss}")
print(f"  {'tất cả trục có metric/threshold/confidence/source':56}{'✅' if not miss else '❌'}")

print()
if fails:
    print("❌ KHÔNG ĐẠT:"); [print("   -",f) for f in fails]; sys.exit(1)
# ⚠ KHÔNG nói "tài liệu khớp code" — script này KHÔNG đọc file .md nào.
#   Nó chỉ tính lại điểm từ metrics.json và so với scores.json.
#   Việc tài liệu §4 có mô tả đúng ngưỡng trong apply_thresholds.py hay không
#   vẫn phải kiểm bằng mắt (bài học T36: §T6 từng ghi thiếu ngưỡng 5%).
print("✅ Điểm nhất quán: code tính lại khớp scores.json.")
print("   ⓘ Chưa kiểm tài liệu 03_SCORING_RUBRIC.md §4 có khớp code không — soát tay.")
