#!/usr/bin/env python3
"""Trích BẰNG CHỨNG cho từng track có điểm khớp hymn PD > 0.

Mục đích: người đọc báo cáo phải NGHE ĐỐI CHỨNG được, không phải tin con số.
Với mỗi track khớp, xuất ra:
  - video_id + link YouTube nhảy thẳng tới giây bắt đầu track (start_s)
  - cụm 4 từ CỤ THỂ trùng với incipit hymn (bằng chứng nguyên văn, ngắn)
  - vị trí ký tự của cụm trùng đầu tiên trong lời track -> ước lượng giây
  - điểm khớp và ngưỡng, để thấy rõ track nằm trên hay dưới ranh giới

Dùng lại nguyên hàm norm()/ngrams() của step_pd_classify.py để bằng chứng
khớp đúng với con số đã báo cáo — không cài lại logic lần hai (T27).

Lưu ý bản quyền/nội bộ: chỉ xuất CỤM 4 TỪ trùng, không xuất toàn văn lời hát.
Toàn văn ở lại lyrics_raw.parquet.

Output: niches/<niche>/02_analysis/pd_evidence.csv (+ .parquet)
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipeline/analyze"))
from step_pd_classify import load_corpus, ngrams, norm  # noqa: E402

# Cụm 4 từ chỉ gồm từ chức năng/phổ thông ("when this life is") trùng nhau do
# tiếng Anh thông dụng, KHÔNG phải do trích dẫn hymn. Cụm mang từ đặc hiệu
# ("amazing", "foretaste", "faithfulness") mới là bằng chứng trích dẫn thật.
# Chặn dương tính giả kiểu T78 ở tầng bằng chứng, không chỉ tầng điểm số.
COMMON = {
    "a", "am", "an", "and", "are", "as", "at", "be", "been", "but", "by", "can",
    "come", "day", "do", "down", "for", "from", "get", "go", "god", "going",
    "gonna", "had", "has", "have", "he", "her", "here", "him", "his", "how",
    "i", "if", "ill", "im", "in", "is", "it", "its", "ive", "know", "let",
    "life", "like", "long", "lord", "love", "make", "man", "me", "more", "my",
    "no", "not", "now", "of", "oh", "on", "one", "or", "our", "out", "over",
    "say", "see", "shall", "she", "so", "some", "still", "take", "tell", "that",
    "the", "their", "them", "then", "there", "they", "this", "through", "time",
    "to", "up", "us", "was", "we", "well", "were", "what", "when", "where",
    "who", "will", "with", "yes", "you", "your", "youre",
}

def is_distinctive(gram: str) -> bool:
    """True nếu cụm chứa ít nhất 1 từ đặc hiệu — dấu hiệu trích dẫn thật."""
    return any(w not in COMMON for w in gram.split())

N = Path(sys.argv[1] if len(sys.argv) > 1 else "niches/christian-blues")
ANA = N / "02_analysis"
RAW = N / "00_input/processed"

cls = pd.read_parquet(ANA / "pd_classification.parquet")
lyr = pd.read_parquet(RAW / "lyrics_raw.parquet")[
    ["track_id", "text", "start_s", "end_s"]
]
corpus = {h["title"]: h for h in load_corpus()}

# cls.title là tên TRACK bên trong compilation, không phải tên video trên
# YouTube — người đối chứng cần cả hai mới tìm đúng chỗ.
vid = (pd.read_parquet(RAW / "videos_enriched.parquet")[["video_id", "title"]]
       .drop_duplicates("video_id").rename(columns={"title": "yt_title"}))

df = cls[cls.match_score > 0].merge(lyr, on="track_id", how="left").merge(
    vid, on="video_id", how="left")
df = df.sort_values("match_score", ascending=False)

rows = []
for r in df.itertuples():
    hymn = corpus[r.matched_hymn]
    inc_w = norm(hymn["incipit"]).split()
    inc_grams = ngrams(inc_w)
    txt_norm = norm(r.text)
    txt_grams = ngrams(txt_norm.split())
    shared = inc_grams & txt_grams

    # Cụm trùng xuất hiện SỚM NHẤT trong lời track -> chỗ cần tua tới.
    pos = {g: txt_norm.find(g) for g in shared}
    ordered = sorted(shared, key=lambda g: pos[g])
    distinctive = [g for g in ordered if is_distinctive(g)]
    # Tua tới cụm ĐẶC HIỆU đầu tiên; không có thì lấy cụm đầu tiên bất kỳ.
    anchor = distinctive[0] if distinctive else (ordered[0] if ordered else None)
    first_pos = pos[anchor] if anchor else -1

    # Ước lượng giây: nội suy tuyến tính theo vị trí ký tự trong track.
    # Thô (nhịp hát không đều) nhưng đủ để tua đúng khổ nhạc.
    if first_pos >= 0 and len(txt_norm) > 0 and pd.notna(r.start_s):
        frac = first_pos / len(txt_norm)
        at_s = int(r.start_s + frac * (r.end_s - r.start_s))
    else:
        at_s = int(r.start_s) if pd.notna(r.start_s) else 0

    rows.append({
        "track_id": r.track_id,
        "video_id": r.video_id,
        "handle": r.handle,
        "track_title": r.title,
        "youtube_title": r.yt_title,
        "matched_hymn": r.matched_hymn,
        "hymn_year": hymn["year"],
        "hymn_status": hymn.get("status", "pd"),
        "match_score": r.match_score,
        "pd_class": r.pd_class,
        "over_threshold": r.match_score >= 0.40,
        "n_shared_grams": len(shared),
        "n_incipit_grams": len(inc_grams),
        "n_distinctive": len(distinctive),
        # Không có cụm đặc hiệu nào => trùng do tiếng Anh thông dụng, KHÔNG
        # phải trích dẫn hymn. Đây là dương tính giả, phải loại khi đối chứng.
        "verdict": ("TRÍCH DẪN THẬT" if distinctive else "TRÙNG NGẪU NHIÊN"),
        "shared_phrases": " | ".join(ordered),
        "distinctive_phrases": " | ".join(distinctive),
        "track_start_s": None if pd.isna(r.start_s) else int(r.start_s),
        "track_end_s": None if pd.isna(r.end_s) else int(r.end_s),
        "match_at_s": at_s,
        "url_track": f"https://youtu.be/{r.video_id}?t={int(r.start_s) if pd.notna(r.start_s) else 0}",
        "url_match": f"https://youtu.be/{r.video_id}?t={at_s}",
        "hymn_source": hymn.get("source_url", ""),
    })

out = pd.DataFrame(rows)
out.to_csv(ANA / "pd_evidence.csv", index=False)
out.to_parquet(ANA / "pd_evidence.parquet", index=False)

n_over = int(out.over_threshold.sum())
n_real = int((out.verdict == "TRÍCH DẪN THẬT").sum())
print(f"OK  {ANA/'pd_evidence.csv'}")
print(f"    {len(out)} track có điểm khớp > 0 — {n_over} vượt ngưỡng 0,40, {len(out)-n_over} dưới ngưỡng")
print(f"    {n_real} trích dẫn thật, {len(out)-n_real} trùng ngẫu nhiên (chỉ từ thông dụng)")
print(f"    {out.video_id.nunique()} video, {out.handle.nunique()} kênh")
