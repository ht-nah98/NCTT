"""L5 · ĐẶC TRƯNG LỜI HÁT — gộp transcript thành parquet ghép được với audio_dna.

HAI TẦNG DỮ LIỆU, CÓ CHỦ ĐÍCH:
  lyrics_raw.parquet      văn bản đầy đủ — NỘI BỘ, để tính toán
  lyrics_features.parquet chỉ THÔNG SỐ — thứ duy nhất đi vào báo cáo

Vì sao tách: lời bài hát là tác phẩm có bản quyền. Lưu nội bộ để phân tích thì
bình thường, nhưng chép nguyên văn vào báo cáo hay bản brief sản xuất thì vừa
rủi ro vừa VÔ DỤNG — chép lời kênh khác không tái tạo được gì, chỉ đạo nhái.
Nguyên tắc y hệt phần audio: đưa nhạc sĩ KHOẢNG BPM và tỷ lệ stem, không đưa
file mp3 của bản thắng.

THÔNG SỐ ĐO ĐƯỢC (mô tả cách viết lời, không phải nội dung):
  mật độ chữ, độ dài dòng, tỷ lệ lặp, độ phong phú từ vựng, ngôi kể

`repeat_ratio` là thông số đáng giá nhất cho ngách này: nhạc worship dựa nhiều
vào điệp khúc lặp, và mức lặp thì tái tạo được, khác với nội dung cụ thể.

Đầu ra: <N>/00_input/processed/lyrics_raw.parquet
        <N>/00_input/processed/lyrics_features.parquet
"""
import json, re, sys
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import niche_paths

N, P, _ = niche_paths("00_input")
BASE = N / "00_input" / "lyrics"
TR = BASE / "transcripts"

MIN_WORDS = 20        # dưới mức này không đủ để tính thống kê ổn định
WORD = re.compile(r"[a-zA-ZÀ-ỹ']+")
I_ME = {"i", "i'm", "me", "my", "mine", "i've", "i'll", "i'd"}
WE_US = {"we", "we're", "us", "our", "ours", "we've", "we'll"}
YOU = {"you", "your", "you're", "yours", "you'll", "you've"}


def feats(segs: list[dict], dur: float) -> dict:
    """Thông số MÔ TẢ CÁCH VIẾT, không giữ nội dung."""
    lines = [s["text"].strip() for s in segs if s.get("text", "").strip()]
    words = [w.lower() for l in lines for w in WORD.findall(l)]
    if len(words) < MIN_WORDS:
        return {"n_words": len(words), "enough_data": False}

    wl = [len(WORD.findall(l)) for l in lines]
    norm = [" ".join(WORD.findall(l.lower())) for l in lines]
    cnt = Counter(n for n in norm if n)
    rep = sum(c - 1 for c in cnt.values() if c > 1)

    return {
        "n_words": len(words),
        "n_lines": len(lines),
        "enough_data": True,
        # mật độ: chữ trên mỗi phút hát
        "words_per_min": round(len(words) / (dur / 60), 1) if dur else None,
        "words_per_line": round(float(np.mean(wl)), 1),
        "line_len_sd": round(float(np.std(wl)), 1),
        # lặp: phần dòng bị lặp lại / tổng dòng
        "repeat_ratio": round(rep / len(lines), 3),
        "unique_line_ratio": round(len(cnt) / len(lines), 3),
        # phong phú từ vựng
        "vocab_size": len(set(words)),
        "ttr": round(len(set(words)) / len(words), 3),
        # ngôi kể — "tôi" hay "chúng ta" đổi hẳn cảm giác bài hát
        "pct_first_sing": round(sum(w in I_ME for w in words) / len(words) * 100, 2),
        "pct_first_plur": round(sum(w in WE_US for w in words) / len(words) * 100, 2),
        "pct_second": round(sum(w in YOU for w in words) / len(words) * 100, 2),
    }


def main():
    files = sorted(TR.glob("*.json"))
    if not files:
        print("⏭  chưa có transcript nào — chạy L3 trước"); return

    tracks = pd.read_parquet(BASE / "tracks.parquet") if (BASE/"tracks.parquet").exists() else None
    raw, feat = [], []

    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        vid, segs = d["video_id"], d.get("segments", [])
        by = {}
        for s in segs:
            by.setdefault(s.get("track_id") or f"{vid}#00", []).append(s)

        for tid, ss in by.items():
            ss.sort(key=lambda x: x["start"])
            dur = ss[-1]["end"] - ss[0]["start"] if ss else 0
            # tầng 1: văn bản đầy đủ, chỉ nằm nội bộ
            raw.append({"track_id": tid, "video_id": vid,
                        "text": "\n".join(s["text"].strip() for s in ss),
                        "n_segments": len(ss),
                        "start_s": round(ss[0]["start"], 1),
                        "end_s": round(ss[-1]["end"], 1),
                        "mean_logprob": round(float(np.mean(
                            [s.get("avg_logprob", 0) for s in ss])), 3)})
            # tầng 2: chỉ thông số
            feat.append({"track_id": tid, "video_id": vid,
                         "model": d.get("model"), "duration_s": round(dur, 1),
                         **feats(ss, dur)})

    R, F = pd.DataFrame(raw), pd.DataFrame(feat)
    if tracks is not None:
        meta = tracks[["track_id", "handle", "video_views", "tier",
                       "boundary_source", "title"]]
        F = F.merge(meta, on="track_id", how="left")

    out = P
    R.to_parquet(out / "lyrics_raw.parquet", index=False)
    F.to_parquet(out / "lyrics_features.parquet", index=False)

    ok = F[F.enough_data] if "enough_data" in F else F
    print(f"✅ {out/'lyrics_raw.parquet'}  ({len(R)} track, NỘI BỘ)")
    print(f"✅ {out/'lyrics_features.parquet'}  ({len(F)} track)")
    print(f"   đủ dữ liệu thống kê: {len(ok)}/{len(F)} track")
    if len(ok):
        print(f"   chữ/phút: TV {ok.words_per_min.median():.0f}"
              f" · tỷ lệ lặp: TV {ok.repeat_ratio.median():.2f}"
              f" · TTR: TV {ok.ttr.median():.2f}")


if __name__ == "__main__":
    main()
