"""Chấm điểm cuối theo rubric v1.0 — chỉ file này được ghi scores.json."""
import json, sys
from pathlib import Path
N=Path(sys.argv[1] if len(sys.argv)>1 else "niches/christian-blues")
m=json.load(open(N/"_state/metrics.json"))
mon=json.load(open(N/"07_monetization/_metrics_raw.json"))

W={"T1":0.20,"T2":0.25,"T3":0.25,"T4":0.15,"T5":0.10}
S={"T1":m["market"]["T1_score"],"T2":m["momentum"]["T2_score"],
   "T3":m["entry"]["T3_score"],"T4":m["ai_fit"]["T4_score"],
   "T5":mon["T5_score"]}
pen=mon["T6_penalty"]
raw=sum(S[k]*W[k] for k in W)
total=raw*20/5+pen

EV={
 "T1":{"metric":"M1.1 = 7,450,227 view/tháng","threshold":"3tr ≤ M1.1 < 8tr → 2đ",
       "confidence":"high","source":"videos_enriched.parquet"},
 "T2":{"metric":"M2.1=1.618, M2.4=1.305","threshold":"M2.1≥1.5 AND M2.4≥1.0 → 4đ",
       "confidence":"medium","source":"cửa sổ 150-60d vs 240-150d (đều đã chín)",
       "caveat":"Chỉ 1 snapshot; nếu dùng cửa sổ chưa chín ra M2.4=0.447 → 0đ"},
 "T3":{"metric":"M3.2=61.5%, Gini=0.626","threshold":"0.5×5 + 0.3×3 + 0.2×5 = 4.4đ",
       "confidence":"high","source":"channels_enriched.parquet",
       "caveat":"Thiên lệch sống sót — kênh đã xóa không có trong dữ liệu"},
 "T4":{"metric":"M4.1=65% top20 là AI-first","threshold":"M4.1≥60% AND audience tolerance=Cao → 5đ",
       "confidence":"medium","source":"suy luận từ nhịp đăng + thumbnail + tuổi kênh"},
 "T5":{"metric":"RPM ước tính $3.0 (khoảng $1.5-6.0)","threshold":"$3 ≤ RPM < $5 → 3đ",
       "confidence":"low","source":"ƯỚC TÍNH, không đo được từ dữ liệu",
       "caveat":"RPM không có trong YouTube API. Đây là giả định dựa trên geo+tuổi+định dạng."},
 "T6":{"metric":f"penalty = {pen}","threshold":"reused content -1, chủ đề tôn giáo -1",
       "confidence":"medium","source":"07_monetization/02_risk_register.csv"},
}
out={"niche":"christian-blues","rubric_version":"1.0","scored_at":"2026-08-15",
 "axes":{k:{"score":S[k],"weight":W[k],**EV[k]} for k in W},
 "T6":{"penalty":pen,**EV["T6"]},
 "raw_weighted":round(raw,3),"total_score":round(total,2),"max_score":20,
 "verdict":("Ưu tiên cao" if total>=16 else "Tiềm năng" if total>=13 else
            "Theo dõi" if total>=10 else "Bỏ qua")}
json.dump(out,open(N/"_state/scores.json","w"),indent=2,ensure_ascii=False)
print(f"{'Trục':6}{'Điểm':>7}{'Trọng số':>10}{'Đóng góp':>10}")
for k in W: print(f"{k:6}{S[k]:>7.1f}{W[k]*100:>9.0f}%{S[k]*W[k]*20/5:>10.2f}")
print(f"{'T6':6}{pen:>7}{'—':>10}{pen:>10.2f}")
print(f"\nTỔNG: {total:.2f} / 20  →  {out['verdict']}")
