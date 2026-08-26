"""KIỂM BÁO CÁO — dò số liệu cũ còn sót trong PDF sau khi sửa metric.

CHẠY: python3 pipeline/report/verify_reports.py [niche_path]
      (chạy CUỐI CÙNG trong run_all.sh, sau khi sinh hết PDF)

VÌ SAO CÓ FILE NÀY (bài học T27, phát hiện 2026-08-17):
  Điểm T3 đổi 4.4 → 4.25 (sửa bẫy L5), tổng 12.20 → 12.05. Nhưng
  `build_report03.py` **ghi cứng** "T3 = 4,4/5" trong HTML nên PDF vẫn in số cũ
  — mâu thuẫn với scoring_engine mà không ai biết, vì PDF không được đọc lại.

  Sửa gốc: builder đọc điểm từ `scores.json`.
  Sửa phòng ngừa: file này dò lại PDF sau mỗi lần dựng.

CÁCH HOẠT ĐỘNG: đọc điểm THẬT từ scores.json, rồi tìm trong PDF những con số
điểm KHÁC nó. Bỏ qua khi con số nằm trong ngữ cảnh kể lại lỗi đã sửa
("bản trước", "số cũ", "đã sửa"…) — vì đó là cố ý.
"""
import json, re, sys, glob, os
from pathlib import Path

try:
    import fitz
except ImportError:
    sys.exit("Cần: pip install pymupdf")

N = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--")
         else "niches/christian-blues")
SC = N/"_state/scores.json"
if not SC.exists():
    sys.exit(f"Thiếu {SC}")
sc = json.load(open(SC))

total = sc["total_score"]
axes = {k: v["score"] for k, v in sc["axes"].items()}

# Ngữ cảnh cho phép một con số KHÁC điểm hiện tại xuất hiện.
# Hai loại hợp lệ:
#   (a) kể lại lỗi đã sửa — "trước đây 12,20, nay 12,05"
#   (b) KỊCH BẢN GIẢ ĐỊNH — "nếu M2.4 sai thì rơi xuống 9,20/20"
# Thiếu (b) thì hồ sơ ngách bị báo động giả: nó CỐ Ý in các kịch bản
# để cấp duyệt thấy độ nhạy của kết luận (T51).
EXCUSE = re.compile(
    r"sửa|trước đây|bản trước|số cũ|cũ \(SAI\)|đã sửa|lệch|từ\s+\d"
    r"|nếu|kịch bản|rơi xuống|giả định|sai thì|khi đó|trường hợp",
    re.I)


def vn(x):
    return f"{x:g}".replace(".", ",")


def check(pdf):
    doc = fitz.open(pdf)
    t = "".join(p.get_text() for p in doc)
    bad = []

    # 1. tổng điểm sai
    for m in re.finditer(r"(\d{1,2})[,.](\d{1,2})\s*/\s*20", t):
        val = float(f"{m.group(1)}.{m.group(2)}")
        if abs(val - total) > 0.01:
            ctx = t[max(0, m.start()-110):m.start()]
            if not EXCUSE.search(ctx):
                bad.append(f"tổng {m.group(0)} ≠ {vn(total)}/20")

    # 2. điểm trục sai
    for ax, real in axes.items():
        for m in re.finditer(rf"{ax}\s*=?\s*(\d[,.]?\d?)\s*/\s*5", t):
            val = float(m.group(1).replace(",", "."))
            if abs(val - real) > 0.01:
                ctx = t[max(0, m.start()-110):m.start()]
                if not EXCUSE.search(ctx):
                    bad.append(f"{ax}={m.group(1)} ≠ {vn(real)}")
    return sorted(set(bad))


# Quét cả _phu-luc/ — từ 2026-08-26 phụ lục nằm trong thư mục con.
pdfs = sorted(glob.glob(str(N/"99_report/*.pdf"))
              + glob.glob(str(N/"99_report/_phu-luc/*.pdf")))
if not pdfs:
    sys.exit(f"Không thấy PDF nào trong {N}/99_report/")

print(f"KIỂM {len(pdfs)} BÁO CÁO · điểm chuẩn {vn(total)}/20")
fails = 0
for f in pdfs:
    bad = check(f)
    name = os.path.basename(f).replace(".pdf", "")
    if bad:
        fails += 1
        print(f"  ❌ {name}")
        for b in bad:
            print(f"       {b}")
    else:
        print(f"  ✅ {name}")

if fails:
    print(f"\n⚠ {fails} báo cáo còn số liệu cũ. Nguyên nhân thường gặp:")
    print("   · builder ghi cứng điểm thay vì đọc scores.json")
    print("   · PDF chưa dựng lại sau khi metric thay đổi")
    sys.exit(1)
print("\n✅ Mọi báo cáo khớp điểm hiện tại.")
