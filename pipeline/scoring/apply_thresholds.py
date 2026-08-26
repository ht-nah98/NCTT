"""ÁP NGƯỠNG RUBRIC — biến metric thành điểm trục (T1…T6).

CHẠY: python3 pipeline/scoring/apply_thresholds.py [niche_path]
      (chạy SAU collect_metrics.py, TRƯỚC scoring_engine.py)

VÌ SAO CÓ FILE NÀY (bài học T24, phát hiện 2026-08-17):
  `scoring_engine.py` đọc `T1_score`…`T6_penalty` từ metrics.json và nhân
  trọng số. Nhưng **KHÔNG script nào tính các điểm đó** — ở ngách đầu tiên
  chúng được điền TAY theo bảng ngưỡng trong tài liệu.

  Hệ quả: hệ thống trông như tự động (chạy lại vẫn ra 12.20) nhưng thực chất
  **đứt một mắt xích**. Thử pipeline trên ngách trống mới lộ ra.

  Đây cũng là vi phạm ngầm quy tắc **R2** (agent không tự chấm điểm) và **R3**
  (mọi điểm phải truy vết được) — chấm tay thì không truy vết được.

NGUỒN NGƯỠNG: framework/00_system/03_SCORING_RUBRIC.md §4.
Sửa ngưỡng ở tài liệu thì phải sửa ở đây — `verify_rubric.py` kiểm tính khớp.
"""
import json, sys
from pathlib import Path

N = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--")
         else "niches/christian-blues")
MET = N/"_state/metrics.json"
if not MET.exists():
    sys.exit(f"Thiếu {MET} — chạy collect_metrics.py trước.")
m = json.load(open(MET))


def band(value, bands):
    """bands: [(ngưỡng_dưới, điểm), …] giảm dần. Trả điểm đầu tiên value ≥ ngưỡng."""
    if value is None:
        return None
    for lo, sc in bands:
        if value >= lo:
            return sc
    return 0


def g(group, key, default=None):
    return m.get(group, {}).get(key, default)


notes = []

# ── T1 · QUY MÔ (views/tháng, thang ~2.5×) ──────────────────────────
T1 = band(g("market", "M1_1_views_per_month"),
          [(50e6, 5), (20e6, 4), (8e6, 3), (3e6, 2), (1e6, 1)])
notes.append(f"T1 ← M1.1 = {g('market','M1_1_views_per_month')}")

# ── T2 · ĐỘNG LƯỢNG (điều kiện kép M2.1 + M2.4) ─────────────────────
m21, m24 = g("momentum", "M2_1_view_growth"), g("momentum", "M2_4_demand_supply_gap")
if m21 is None:
    T2 = None
elif m21 >= 2.0 and (m24 or 0) >= 1.2: T2 = 5
elif m21 >= 1.5 and (m24 or 0) >= 1.0: T2 = 4
elif m21 >= 1.2: T2 = 3
elif m21 >= 0.9: T2 = 2
elif m21 >= 0.7: T2 = 1
else:            T2 = 0
notes.append(f"T2 ← M2.1={m21} M2.4={m24}")

# ── T3 · CỬA GIA NHẬP (M3.2 trọng số 0.5, Gini 0.5) ─────────────────
# M3.2 ghi dưới dạng PHẦN TRĂM (61.5) → đổi về tỷ lệ để so ngưỡng
m32 = g("entry", "M3_2_newcomer_success_pct")
m32 = None if m32 is None else m32/100
m31 = g("entry", "M3_1_gini")
s32 = band(m32, [(0.40, 5), (0.25, 4), (0.15, 3), (0.08, 2), (0.03, 1)])
# Gini NGƯỢC chiều: càng thấp càng tốt
s31 = None if m31 is None else next(
    (sc for hi, sc in [(0.45, 5), (0.55, 4), (0.65, 3), (0.75, 2), (0.85, 1)] if m31 <= hi), 0)

# Công thức rubric: T3 = 0.3×score(M3.1) + 0.5×score(M3.2) + 0.2×score(M3.3)
# M3.3 (thời gian đạt 100k view) KHÔNG đo được với 1 snapshot — bẫy L5.
#
# ⚠ Ở lần chấm tay đầu tiên, M3.3 được cho **5/5 điểm tối đa** dù ghi rõ
#   "KHÔNG ĐO ĐƯỢC". Điều đó đẩy T3 từ 4.0 lên 4.4 — thưởng điểm cho một
#   chỉ số không có dữ liệu. Xem lessons_learned T25.
#
# Cách xử lý đúng: bỏ thành phần thiếu và CHIA LẠI trọng số cho phần đo được,
# thay vì gán giá trị mặc định.
m33_ok = g("entry", "M3_3_status") not in (None,) and \
         "KHÔNG ĐO ĐƯỢC" not in str(g("entry", "M3_3_status", ""))
if s32 is None or s31 is None:
    T3 = None
elif m33_ok:
    s33 = band(g("entry", "M3_3_months_to_100k"), [(0, 5)])  # ngưỡng cụ thể khi có dữ liệu
    T3 = round(0.3*s31 + 0.5*s32 + 0.2*(s33 or 0), 2)
else:
    T3 = round((0.3*s31 + 0.5*s32)/0.8, 2)     # chia lại trọng số 0.3:0.5 → tổng 1.0
notes.append(f"T3 ← M3.2={m32}→{s32}đ · Gini={m31}→{s31}đ"
             + ("" if m33_ok else " · M3.3 KHÔNG ĐO ĐƯỢC → chia lại trọng số"))

# ── T4 · PHÙ HỢP AI ─────────────────────────────────────────────────
m41 = g("ai_fit", "M4_1_ai_first_top20_pct")   # ghi dạng phần trăm
m41 = None if m41 is None else m41/100
T4 = band(m41, [(0.60, 5), (0.40, 4), (0.25, 3), (0.10, 2), (0.03, 1)])
notes.append(f"T4 ← M4.1 = {m41}")

# ── T5 · KIẾM TIỀN (RPM ước tính) ───────────────────────────────────
# RPM ghi dạng khoảng [thấp, giữa, cao] → lấy giá trị GIỮA (thận trọng)
_r = g("money", "M5_2_rpm_range")
rpm = _r[1] if isinstance(_r, list) and len(_r) >= 2 else _r
T5 = band(rpm, [(8, 5), (5, 4), (3, 3), (1.5, 2), (0.7, 1)])
notes.append(f"T5 ← RPM = {rpm}")

# ── T6 · RỦI RO (điểm TRỪ, tối đa 5) ────────────────────────────────
pen, why = 0, []
dup = g("risk", "cross_title_pct")            # % video trùng tiêu đề giữa kênh
if dup is not None and dup >= 5:
    pen += 2; why.append(f"trùng nội dung {dup:.1f}% (−2)")
if g("risk", "copyright_flag"):
    pen += 1; why.append("bản quyền (−1)")
top_share = g("entry", "top1_share")           # kênh lớn nhất chiếm bao nhiêu view
if top_share is not None:
    ts = top_share/100 if top_share > 1 else top_share
    if ts > 0.40:
        pen += 1; why.append(f"phụ thuộc kênh top {ts:.0%} (−1)")
if m24 is not None and m24 < 0.8:
    pen += 1; why.append(f"cung vượt cầu M2.4={m24} (−1)")
T6 = -min(pen, 5)      # ghi số ÂM cho khớp quy ước metrics.json (T6_penalty = −2)
notes.append(f"T6 ← {', '.join(why) if why else 'không phát hiện rủi ro'}")

# ── GHI LẠI — chỉ ghi khi TÍNH ĐƯỢC, không ghi đè điểm đã có ────────
computed = {"market": ("T1_score", T1), "momentum": ("T2_score", T2),
            "entry": ("T3_score", T3), "ai_fit": ("T4_score", T4),
            "money": ("T5_score", T5), "risk": ("T6_penalty", T6)}

wrote, kept, cannot = [], [], []
for grp, (key, val) in computed.items():
    old = m.get(grp, {}).get(key)
    if val is None:
        cannot.append(f"{grp}.{key}")
        continue
    if old is not None and abs(float(old) - float(val)) > 0.01:
        kept.append(f"{grp}.{key}: có sẵn {old} ≠ tính được {val}")
    m.setdefault(grp, {})[key] = val
    wrote.append(f"{key}={val}")

m["_meta"] = {**m.get("_meta", {}), "thresholds_applied": True,
              "threshold_source": "framework/00_system/03_SCORING_RUBRIC.md §4",
              "derivation": notes}
json.dump(m, open(MET, "w"), indent=2, ensure_ascii=False, default=str)

print("ÁP NGƯỠNG RUBRIC → điểm trục")
for n in notes:
    print(f"  {n}")
print(f"\n  đã ghi: {' · '.join(wrote)}")
if kept:
    print("\n  ⚠ LỆCH so với điểm đã có (đã GHI ĐÈ bằng giá trị tính được):")
    for k in kept:
        print(f"      {k}")
    print("      → nếu điểm cũ đúng thì metric đang sai, kiểm lại bước phân tích.")
if cannot:
    print(f"\n  ⚠ KHÔNG tính được {len(cannot)} trục (thiếu metric nguồn):")
    for c in cannot:
        print(f"      {c}")
