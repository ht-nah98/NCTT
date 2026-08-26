"""Nạp DNA âm thanh BẢN ĐẦY ĐỦ (595 trường) → parquet.

VÌ SAO CÓ BƯỚC NÀY: `audio_dna.xlsx` chỉ là bản xuất gọn 45 cột để xem bằng
mắt. Bản gốc `audio_dna_full.jsonl` có **595 trường trên cùng 307 track đó** —
136 trường số dùng được đang nằm không. Nhóm bị bỏ phí nhiều nhất:

  giai điệu  4 → 35 trường  (stepwise_ratio, phrase_len, motif.repetition_ratio)
  hoà âm     2 → 10 trường  (chords_per_bar, quality_share, hai nguồn dò tông)
  stem       5 → 87 trường  (attack_ms, decay_ms, crest_db từng stem)
  nhịp             + swing_ratio, subdivision_hits — thiếu hẳn ở bản gọn

KHÔNG THAY THẾ normalize_audio_dna.py: bản gọn vẫn chạy, vẫn sinh
audio_dna.parquet cho các bước cũ. File này ghi ra parquet RIÊNG. Hai nguồn
song song, không đè nhau — đổi một chỗ không làm gãy báo cáo đang có.

CẢNH BÁO CỠ MẪU: nhiều trường hơn KHÔNG làm mẫu lớn hơn. Vẫn 307 track /
29 video / 6 kênh. Với MÔ TẢ và TÁI TẠO thì thêm trường là lợi thế thật (ta
đo nhóm thắng làm gì). Với KIỂM ĐỊNH thắng/thua thì đây là bẫy: 181 trường
trên n=29 video thì gần như chắc chắn tìm ra tương quan giả. Vì vậy parquet
này chỉ nối vào step04h3 (tái tạo), KHÔNG nối vào step04h2 (kiểm định).

Cột prompt Suno: repo có `p7_prompts.jsonl` nhưng KHÔNG nạp — người dùng xác
nhận dữ liệu thô sai.

Đầu ra: <N>/00_input/processed/audio_dna_full.parquet
"""
import json, sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import niche_paths

N, P, _ = niche_paths()
SRC = N / "00_input/raw/audio_dna_full.jsonl"

# Danh sách dài (đường bao năng lượng, chuỗi hợp âm…) không đưa vào bảng phẳng:
# mỗi phần tử là một mốc thời gian, độ dài khác nhau từng track. Giữ độ dài để
# biết có dữ liệu, còn nội dung thì bước nào cần sẽ tự đọc lại từ jsonl.
MAX_LIST_KEEP = 0


def flatten(d: dict, prefix: str = "") -> dict:
    """Làm phẳng, BỎ tiền tố lặp: mỗi phase gói dữ liệu trong khối trùng tên
    phase, nên nối thẳng sẽ ra `melody.melody.x`, `stems.stems.drums.y`.
    Tên dài vô ích và dễ gõ nhầm."""
    out = {}
    for k, v in d.items():
        name = f"{prefix}{k}"
        if prefix.rstrip(".").endswith(k):   # melody.melody → melody
            name = prefix.rstrip(".")
        if isinstance(v, dict):
            out.update(flatten(v, name + "."))
            continue
        if isinstance(v, list):
            out[name + "__len"] = len(v)
        else:
            out[name] = v
    return out


def main():
    if not SRC.exists():
        print(f"⏭  Bỏ qua: chưa có {SRC}")
        return

    rows = [json.loads(l) for l in SRC.read_text(encoding="utf-8").splitlines() if l.strip()]
    T = pd.DataFrame([flatten(r) for r in rows])

    # ép kiểu số ở đâu ép được, giữ nguyên phần còn lại
    n_num = 0
    for c in T.columns:
        if T[c].dtype == object:
            conv = pd.to_numeric(T[c], errors="coerce")
            if conv.notna().mean() >= 0.8:      # đa số là số → đúng là cột số
                T[c] = conv
                n_num += 1

    before = len(T)
    T = T[T.video_id.notna()] if "video_id" in T else T
    if len(T) < before:
        print(f"   ⚠ bỏ {before-len(T)} track thiếu video_id")

    T.to_parquet(P / "audio_dna_full.parquet", index=False)

    num = T.select_dtypes("number")
    usable = [c for c in num.columns
              if num[c].notna().mean() >= 0.8 and num[c].nunique() > 3]
    print(f"✅ {P/'audio_dna_full.parquet'}")
    print(f"   {len(T)} track / {T.video_id.nunique()} video / "
          f"{T.channel_id.nunique() if 'channel_id' in T else '?'} kênh")
    print(f"   {T.shape[1]} trường · {len(usable)} trường số dùng được "
          f"(≥80% có dữ liệu, >3 giá trị)")
    grp = {}
    for c in usable:
        grp[c.split(".")[0]] = grp.get(c.split(".")[0], 0) + 1
    print("   theo nhóm: " + " · ".join(f"{k}={v}" for k, v in
                                        sorted(grp.items(), key=lambda x: -x[1])))


if __name__ == "__main__":
    main()
