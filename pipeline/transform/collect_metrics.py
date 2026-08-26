"""GOM CHỈ SỐ — hợp nhất `_metrics_raw.json` của từng bước vào `_state/metrics.json`.

CHẠY: python3 pipeline/transform/collect_metrics.py [niche_path]
      (chạy SAU step02→08, TRƯỚC scoring_engine.py)

VÌ SAO CÓ FILE NÀY (bài học T23, phát hiện 2026-08-17):
  Mỗi bước phân tích ghi `<thư-mục-bước>/_metrics_raw.json`. Nhưng KHÔNG bước nào
  gom chúng vào `_state/metrics.json` — file mà `scoring_engine` đọc để chấm điểm.
  Ở ngách đầu tiên tôi đã **chép tay**, nên nó chạy được mà không ai nhận ra.
  Thử pipeline trên ngách trống thì lộ ngay: step07 chết vì không thấy metrics.json.

  Đây đúng là loại lỗi mà "chạy lại được" che giấu: file cũ vẫn còn nên
  mọi lần chạy lại đều thành công — cho tới khi gặp ngách mới.

NGUYÊN TẮC: file này chỉ **gom và đổi tên khóa**, tuyệt đối không tính toán lại.
Tính toán là việc của các bước phân tích (giữ tách bạch tầng FACT/METRIC).
"""
import json, sys
from pathlib import Path

N = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--")
         else "niches/christian-blues")
STATE = N/"_state"; STATE.mkdir(parents=True, exist_ok=True)
OUT = STATE/"metrics.json"

# thư mục bước → nhóm khóa trong metrics.json.
# Các bước ghi `_metrics_raw.json` PHẲNG (M1_*, M2_*… cùng một cấp), nên khi một
# bước nuôi NHIỀU nhóm thì phải tách theo tiền tố khóa. `prefix` khai báo việc đó.
SOURCES = [
    ("02_market",       {"market": "M1_", "momentum": "M2_"}),
    ("03_competitor",   {"entry": "M3_", "ai_fit": "M4_"}),
    ("04_outlier",      {"formula": None}),
    ("05_audience",     {"audience": None}),
    ("06_keyword",      {"keyword": None}),
    ("07_monetization", {"money": "M5_", "risk": "M6_"}),
]

merged = {}
if OUT.exists():                       # giữ metadata đã có (niche, rubric_version…)
    merged = json.load(open(OUT))

found, missing = [], []
for sub, groups in SOURCES:
    f = N/sub/"_metrics_raw.json"
    if not f.exists():
        missing.append(sub)
        continue
    raw = json.load(open(f))
    found.append(sub)
    for g, prefix in groups.items():
        if g in raw:                      # bước đã tự nhóm sẵn → lấy nguyên
            merged.setdefault(g, {}).update(raw[g])
        elif prefix:                      # file phẳng → tách theo tiền tố khóa
            merged.setdefault(g, {}).update(
                {k: v for k, v in raw.items() if k.startswith(prefix)})
        else:                             # một bước ↔ một nhóm → lấy cả file
            merged.setdefault(g, {}).update(raw)
    # khóa không khớp tiền tố nào (geo, lang, dilution_verdict…) → về nhóm đầu
    if len(groups) > 1:
        first = next(iter(groups))
        claimed = {k for g in groups for k in merged.get(g, {})}
        merged.setdefault(first, {}).update(
            {k: v for k, v in raw.items()
             if k not in claimed and not isinstance(v, dict)})

merged.setdefault("niche", N.name)
merged["_meta"] = {**merged.get("_meta", {}),
                   "collected_from": found,
                   "missing_sources": missing}

json.dump(merged, open(OUT, "w"), indent=2, ensure_ascii=False, default=str)

print(f"Gom chỉ số → {OUT}")
print(f"  nguồn có   : {len(found)}/{len(SOURCES)}  ({', '.join(found)})")
if missing:
    print(f"  ⚠ thiếu    : {', '.join(missing)}")
print(f"  nhóm khóa  : {len([k for k in merged if not k.startswith('_')])}")

# ── CẢNH BÁO KHOẢNG TRỐNG CHẤM ĐIỂM (bài học T24) ────────────────────
# `scoring_engine` đọc các khóa `T*_score`, nhưng KHÔNG script phân tích nào
# tính chúng — ở ngách đầu tiên chúng được điền TAY. Ngách mới sẽ thiếu.
NEED = {"market": "T1_score", "momentum": "T2_score", "entry": "T3_score",
        "ai_fit": "T4_score", "money": "T5_score", "risk": "T6_penalty"}
gaps = [f"{g}.{k}" for g, k in NEED.items() if k not in merged.get(g, {})]
if gaps:
    print(f"\n  ⚠ THIẾU {len(gaps)}/{len(NEED)} ĐIỂM TRỤC — phải chấm thủ công")
    print(f"    theo ngưỡng trong framework/00_system/03_SCORING_RUBRIC.md:")
    for g in gaps:
        print(f"      · {g}")
    print(f"    (đây là khoảng trống đã biết của hệ thống — xem lessons_learned T24)")

if missing:
    sys.exit(f"\nDỪNG: thiếu {len(missing)} nguồn — chạy các bước đó trước khi chấm điểm.")
