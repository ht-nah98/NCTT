#!/usr/bin/env python3
"""TỰ KIỂM TÀI LIỆU HỆ THỐNG — tài liệu có còn khớp code không?

VÌ SAO CÓ FILE NÀY (bài học T90, 2026-08-28):
  Hệ thống đã có `verify_rubric.py` kiểm điểm số và `verify_reports.py` kiểm
  số trong PDF. Nhưng KHÔNG có gì kiểm chính `framework/00_system/` — nên sau
  49 vòng cải tiến, 4 chỗ trong tài liệu đã lệch khỏi thực tế mà không ai biết:

    · 05_FILE_CONTRACTS thiếu 4 builder T1.x
    · 02_DATA_MODEL + 05_ không nhắc `source_class` dù 10_ bắt buộc
    · 06_REPORT_STANDARDS không nhắc mã nguồn
    · 01_ARCHITECTURE §8.2 mô tả quy ước tên đã archive

  Người sửa code không có lý do gì để nhớ sửa tài liệu — trừ khi có thứ báo cho
  họ. File này là thứ đó.

TRIẾT LÝ: chỉ kiểm những gì kiểm được BẰNG MÁY (file tồn tại, tên khớp, khái
niệm được nhắc tới). Không cố kiểm ngữ nghĩa — việc đó vẫn phải soát tay, và
script sẽ nói rõ chỗ nào nó không kiểm được.

    python3 pipeline/scoring/verify_system_docs.py [niche_path]

Thoát mã 0 nếu mọi kiểm tra đạt, 1 nếu có lệch.
"""
import json
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SYS = ROOT / "framework/00_system"
REPORT = ROOT / "pipeline/report"

N = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--")
                 else ROOT / "niches/christian-blues")

issues = []      # lệch thật — phải sửa
notes = []       # không kiểm được bằng máy — soát tay


def read(p):
    return p.read_text(encoding="utf-8") if p.exists() else ""


# ── 1 · MỌI TÀI LIỆU HỆ THỐNG PHẢI CÓ SỐ PHIÊN BẢN ─────────────────────────
# Không có phiên bản thì không biết tài liệu ứng với trạng thái code nào.
for f in sorted(SYS.glob("*.md")):
    head = read(f).split("\n")[:15]      # phải ở ĐẦU file, không lẫn giữa thân
    if not any(ln.startswith("> Phiên bản:") for ln in head):
        if "Phiên bản:" in read(f):
            issues.append(f"{f.name}: dòng 'Phiên bản:' nằm lẫn trong thân tài "
                          f"liệu — phải ở khối mở đầu (15 dòng đầu)")
        else:
            issues.append(f"{f.name}: thiếu dòng 'Phiên bản:' — không truy được "
                          f"tài liệu này ứng với trạng thái code nào")


# ── 2 · BUILDER TRONG report/ PHẢI CÓ TRONG FILE_CONTRACTS ─────────────────
# Builder ghi ra file mà hợp đồng không khai = bước sau không biết nó tồn tại.
contracts = read(SYS / "05_FILE_CONTRACTS.md")
for f in sorted(REPORT.glob("build_T1*.py")):
    doc_code = f.stem.replace("build_T1", "T1.").split("_")[0]
    if doc_code not in contracts:
        issues.append(f"05_FILE_CONTRACTS.md: thiếu hợp đồng cho {f.name} "
                      f"({doc_code}) — builder ghi PDF mà hợp đồng không khai")


# ── 3 · BUILDER TRONG run_all PHẢI TỒN TẠI THẬT ────────────────────────────
# Sau khi archive file, run_all trỏ vào chỗ trống -> pipeline gãy ngầm.
run_all = read(ROOT / "pipeline/run_all.sh")
for line in run_all.splitlines():
    line = line.strip()
    if line.startswith("#") or "pipeline/report/" not in line:
        continue
    for tok in line.split():
        if tok.startswith("pipeline/report/") and tok.endswith(".py"):
            if not (ROOT / tok).exists():
                issues.append(f"run_all.sh gọi {tok} nhưng file không tồn tại")


# ── 4 · KHÁI NIỆM source_class PHẢI XUYÊN SUỐT ─────────────────────────────
# 10_ đặt ra quy tắc; nếu 02_/05_/06_ không nhắc thì quy tắc chỉ nằm trên giấy.
if (SYS / "10_SOURCE_CLASSES.md").exists():
    for name, what in (("02_DATA_MODEL.md", "mô tả trường"),
                       ("05_FILE_CONTRACTS.md", "quy tắc ghi"),
                       ("06_REPORT_STANDARDS.md", "chuẩn trình bày")):
        if "source_class" not in read(SYS / name) and "mã nguồn" not in read(SYS / name):
            issues.append(f"{name}: không nhắc `source_class` dù "
                          f"10_SOURCE_CLASSES.md bắt buộc — thiếu {what}")


# ── 5 · source_class PHẢI CÓ THẬT TRONG DỮ LIỆU ────────────────────────────
# Đây là chỗ quan trọng nhất: tài liệu nói bắt buộc mà dữ liệu trống thì quy
# tắc là hư cấu. Lỗi này đã thực sự xảy ra (0/24 chỉ số) khi mới viết 10_.
mpath = N / "_state/metrics.json"
if mpath.exists():
    m = json.loads(mpath.read_text(encoding="utf-8"))
    meta = m.get("_meta", {})
    entries = [v for v in meta.values() if isinstance(v, dict)]
    tagged = [v for v in entries if "source_class" in v]
    if entries and not tagged:
        issues.append(f"metrics.json: 0/{len(entries)} chỉ số có `source_class` — "
                      f"quy tắc N1 trong 10_SOURCE_CLASSES.md chưa được thực thi")
    elif entries and len(tagged) < len(entries) * 0.9:
        issues.append(f"metrics.json: chỉ {len(tagged)}/{len(entries)} chỉ số có "
                      f"`source_class` — dưới 90%")


# ── 6 · TÀI LIỆU KHÔNG ĐƯỢC TRỎ VÀO FILE ĐÃ XOÁ/ARCHIVE ────────────────────
for f in sorted(SYS.glob("*.md")) + [ROOT / "pipeline/run_all.sh"]:
    s = read(f)
    for tok in s.replace("`", " ").replace("(", " ").replace(")", " ").split():
        if tok.startswith("pipeline/") and tok.endswith(".py"):
            if not (ROOT / tok).exists():
                notes.append(f"{f.name}: nhắc `{tok}` — file không còn ở đó "
                             f"(có thể đã archive; sửa đường dẫn hoặc ghi rõ)")


# ── 7 · BỐN TÀI LIỆU T1.x PHẢI DỰNG RA ĐƯỢC ────────────────────────────────
for code, fname in (("T1.1", "T1-1_Ho-so-ngach.pdf"),
                    ("T1.2", "T1-2_Mo-hinh-khan-gia.pdf"),
                    ("T1.3", "T1-3_Dac-ta-dong-nhac.pdf"),
                    ("T1.4", "T1-4_The-doi-thu.pdf")):
    if not (N / "99_report" / fname).exists():
        notes.append(f"{code}: chưa có {fname} — chạy run_all.sh để dựng")


# ── điều script NÀY không kiểm được ────────────────────────────────────────
notes.append("Không kiểm được bằng máy: nội dung tài liệu có ĐÚNG không, "
             "sơ đồ mermaid có khớp luồng thật không, ngưỡng trong "
             "03_SCORING_RUBRIC có khớp code không (dùng verify_rubric.py)")

# ── in kết quả ─────────────────────────────────────────────────────────────
print(f"KIỂM TÀI LIỆU HỆ THỐNG · {len(list(SYS.glob('*.md')))} file trong framework/00_system/")

if issues:
    print(f"\n  ✗ {len(issues)} CHỖ LỆCH — tài liệu không khớp code:")
    for x in issues:
        print(f"      · {x}")
else:
    print("\n  ✅ Tài liệu khớp code ở mọi điểm kiểm được bằng máy.")

if notes:
    print(f"\n  ⓘ {len(notes)} ghi chú:")
    for x in notes:
        print(f"      · {x}")

sys.exit(1 if issues else 0)
