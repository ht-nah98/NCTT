"""Tiện ích dùng chung cho mọi script trong pipeline.

VÌ SAO CÓ FILE NÀY: mỗi script trước đây tự viết lại 3 dòng giống nhau
(đọc sys.argv, dựng đường dẫn, tạo thư mục) — và **6/15 script quên tạo
thư mục**, khiến ngách mới chết ngay bước đầu. Xem lessons_learned T22.

CÁCH DÙNG:
    from _common import niche_paths
    N, P, OUT = niche_paths("02_market")     # OUT được mkdir sẵn
"""
import sys
from pathlib import Path

# Thư mục output chuẩn của từng bước — dùng để dựng khung ngách mới
STEP_DIRS = ["00_input/raw", "00_input/raw/audio", "00_input/processed",
             "02_market", "03_competitor",
             "04_outlier", "05_audience", "06_keyword", "07_monetization",
             "04_outlier/audio", "09_playbook", "99_report", "_state"]


def niche_root(argv=None):
    """Lấy đường dẫn ngách từ tham số dòng lệnh, mặc định christian-blues."""
    a = argv if argv is not None else sys.argv
    p = Path(a[1] if len(a) > 1 and not a[1].startswith("--") else "niches/christian-blues")
    if not p.exists():
        sys.exit(f"Không thấy ngách: {p}")
    return p


def niche_paths(out_subdir=None, argv=None):
    """Trả về (N, P, OUT). OUT đã được tạo sẵn nếu truyền out_subdir.

    N   = gốc ngách          niches/<tên>
    P   = dữ liệu đã xử lý   niches/<tên>/00_input/processed
    OUT = thư mục ghi kết quả (None nếu không truyền out_subdir)
    """
    N = niche_root(argv)
    P = N/"00_input/processed"
    P.mkdir(parents=True, exist_ok=True)
    OUT = None
    if out_subdir:
        OUT = N/out_subdir
        OUT.mkdir(parents=True, exist_ok=True)
    return N, P, OUT


def scaffold(niche_path):
    """Dựng khung thư mục cho ngách mới."""
    root = Path(niche_path)
    for d in STEP_DIRS:
        (root/d).mkdir(parents=True, exist_ok=True)
    return root


if __name__ == "__main__":
    # python3 pipeline/_common.py niches/<ngách-mới>   → dựng khung thư mục
    r = scaffold(sys.argv[1] if len(sys.argv) > 1 else "niches/ngach-moi")
    print(f"Đã dựng khung: {r}")
    for d in STEP_DIRS:
        print(f"  {d}/")
