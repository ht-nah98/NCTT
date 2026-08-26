"""L1 · CHỌN MẪU — khoá danh sách video sẽ tải, ghi ra JSON để các bước sau bám vào.

VÌ SAO TÁCH RIÊNG: nếu để mỗi bước tự chọn top-N thì dữ liệu videos_enriched
đổi một lần là cả luồng lệch mẫu, và bước 3 sẽ phiên âm video mà bước 2 không
tải. Khoá danh sách một lần, mọi bước sau đọc từ file này.

TIÊU CHÍ (người dùng chốt 2026-08-19): top view thuần tuý, KHÔNG chặn trần kênh.
Đã đo: 22/53 kênh, kênh lớn nhất 12% → không có kênh nào áp đảo.

Đầu ra: <N>/00_input/lyrics/COHORT.json
"""
import json, sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import niche_paths

N, P, _ = niche_paths("00_input")
OUT = N / "00_input" / "lyrics"
OUT.mkdir(parents=True, exist_ok=True)

TOP_N = 50


def main():
    v = pd.read_parquet(P / "videos_enriched.parquet")
    t = v.nlargest(TOP_N, "view_count").copy()

    # đánh dấu video nào ghép được với audio_dna (cấp track)
    dna = P / "audio_dna.parquet"
    have_dna = set()
    if dna.exists():
        have_dna = set(pd.read_parquet(dna).video_id.unique())
    t["has_audio_dna"] = t.video_id.isin(have_dna)

    vids = [{"video_id": r.video_id, "handle": r.handle, "title": r.title,
             "view_count": int(r.view_count), "duration_sec": int(r.duration_sec),
             "has_audio_dna": bool(r.has_audio_dna)}
            for r in t.itertuples()]

    res = {
        "niche": N.name,
        "criteria": f"top {TOP_N} theo view_count, không chặn trần kênh",
        "n_videos": len(vids),
        "n_channels": int(t.handle.nunique()),
        "total_hours": round(float(t.duration_sec.sum()) / 3600, 1),
        "n_with_audio_dna": int(t.has_audio_dna.sum()),
        "view_range": [int(t.view_count.min()), int(t.view_count.max())],
        "videos": vids,
        "_limits": [
            "top view thuần tuý → lệch về video CŨ đã tích luỹ view, "
            "không phản ánh thị hiếu hiện tại",
            f"chỉ {int(t.has_audio_dna.sum())}/{len(vids)} video ghép được với audio_dna",
        ],
    }
    f = OUT / "COHORT.json"
    f.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ {f}")
    print(f"   {len(vids)} video / {res['n_channels']} kênh / {res['total_hours']} giờ")
    print(f"   ghép được audio_dna: {res['n_with_audio_dna']}/{len(vids)}")


if __name__ == "__main__":
    main()
