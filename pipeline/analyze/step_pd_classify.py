#!/usr/bin/env python3
"""Phân loại từng track lyrics thành các nhóm theo mức độ rủi ro bản quyền.

Bằng chứng thực đo trên corpus christian-blues (308 track): KHÔNG có track
nào tái hiện đủ một hymn PD để coi là "hát lại nguyên bài" — điểm khớp cao
nhất quan sát được chỉ 0.444 (mượn 1-2 dòng mở đầu, phần còn lại viết mới).
Nhiều bài "Psalm N" trong tiêu đề cũng là PHÓNG TÁC (paraphrase) chứ không
trích nguyên văn KJV. Vì vậy phân loại theo 4 nhóm:

  HYMN_PARTIAL_PD         — mượn câu mở đầu (>=40% 4-gram) của 1 hymn PD xác
                            nhận (trước 1930). Chỉ phần mở đầu là PD thật;
                            phần lời còn lại + giai điệu vẫn là sáng tác mới.
  HYMN_PARTIAL_CHECK_YEAR — như trên nhưng hymn gốc sáng tác >=1930, CHƯA rõ
                            có PD hay không -> cần tra cứu riêng, không báo
                            là an toàn.
  SCRIPTURE_PARAPHRASE    — tiêu đề tự khai "Psalm N" / "Scripture". Nội
                            dung Kinh Thánh (KJV) là PD, nhưng đây là bản
                            phóng tác + giai điệu mới -> vẫn là sáng tác mới
                            về mặt âm nhạc, chỉ chủ đề/tứ thơ lấy từ PD.
  NEW_COMPOSITION         — không khớp hymn PD, tiêu đề không tự khai
                            Scripture. Sáng tác mới hoàn toàn (lời + giai điệu).

Đo trùng lặp hymn bằng tỷ lệ n-gram (n=4, từ thường, bỏ dấu câu) giữa toàn
văn track và câu mở đầu (incipit, <=10 từ) của mỗi hymn trong corpus.

Output: niches/<niche>/02_analysis/pd_classification.parquet + .csv
"""
import argparse
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CORPUS_PATH = ROOT / "framework/04_reference/pd_corpus/hymns_pd.json"

# Phần lớn track không trích nguyên văn KJV mà PHÓNG TÁC (paraphrase) — vd
# "The Lord's my shepherd" thay vì "The Lord is my shepherd". Vì vậy nhận diện
# Scripture bằng CHỦ ĐỀ/HÌNH ẢNH đặc trưng của Psalm, không phải cụm cố định.
SCRIPTURE_THEME_WORDS = re.compile(
    r"\bshepherd\b|\bstill waters?\b|\brod and staff\b|\bvalley\b|\bgoodness and mercy\b"
    r"|\bthirst(eth|s)? for\b|\bmy soul\b|\bcup (runneth|overflow)\b|\banoint",
    re.I,
)
TITLE_SCRIPTURE = re.compile(r"\bpsalm\s*\d+\b|\bscripture\b", re.I)

def norm(text: str) -> str:
    text = re.sub(r"[’']", "", str(text).lower())
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def ngrams(words: list[str], n: int = 4) -> set[str]:
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}

def load_corpus() -> list[dict]:
    data = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    return data["hymns"]

def match_hymn(track_text: str, corpus: list[dict]) -> tuple[str | None, float, str]:
    """Trả về (title, score, status) của hymn khớp cao nhất, hoặc (None, 0, '')."""
    track_words = norm(track_text).split()
    track_ngrams = ngrams(track_words, 4)
    if not track_ngrams:
        return None, 0.0, ""
    best = (None, 0.0, "")
    for h in corpus:
        inc_words = norm(h["incipit"]).split()
        inc_ngrams = ngrams(inc_words, 4)
        if not inc_ngrams:
            continue
        overlap = len(inc_ngrams & track_ngrams) / len(inc_ngrams)
        if overlap > best[1]:
            best = (h["title"], overlap, h.get("status", "pd"))
    return best

def classify_row(text: str, video_title: str, corpus: list[dict]) -> dict:
    title, score, status = match_hymn(text, corpus)

    # Ngưỡng khớp hymn: dữ liệu thực tế cho thấy score cao nhất quan sát được
    # là 0.444 (mượn 1-2 dòng mở đầu rồi viết lời mới hoàn toàn) — KHÔNG có
    # track nào tái hiện đủ để coi là "hát lại nguyên bài". Vì vậy dùng 2 mức:
    #   >=0.4  -> HYMN_PARTIAL: có mượn câu mở đầu hymn PD, phần còn lại là mới
    #   <0.4   -> không tính là liên quan hymn
    is_hymn_match = title is not None and score >= 0.4

    # Scripture: tin vào tiêu đề tự khai ("Psalm N") hơn là đoán qua từ khóa
    # nội dung, vì nội dung thường PHÓNG TÁC (paraphrase) chứ không trích
    # nguyên văn KJV -> khớp cụm cố định dễ bỏ sót, khớp từ khóa đơn dễ nhầm.
    title_says_scripture = bool(TITLE_SCRIPTURE.search(str(video_title)))
    content_theme_signal = bool(SCRIPTURE_THEME_WORDS.search(str(text)))

    if is_hymn_match and status == "pd":
        cls = "HYMN_PARTIAL_PD"
    elif is_hymn_match and status == "check":
        cls = "HYMN_PARTIAL_CHECK_YEAR"
    elif title_says_scripture:
        cls = "SCRIPTURE_PARAPHRASE"
    else:
        cls = "NEW_COMPOSITION"

    return {
        "pd_class": cls,
        "matched_hymn": title,
        "match_score": round(score, 3),
        "title_says_scripture": title_says_scripture,
        "content_theme_signal": content_theme_signal,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("niche_dir", help="vd: niches/christian-blues")
    a = ap.parse_args()

    niche = Path(a.niche_dir)
    lr_path = niche / "00_input/processed/lyrics_raw.parquet"
    lf_path = niche / "00_input/processed/lyrics_features.parquet"
    sel_path = niche / "00_input/processed/selected_videos.parquet"
    if not lr_path.exists():
        raise SystemExit(f"Không thấy {lr_path}")

    corpus = load_corpus()
    lr = pd.read_parquet(lr_path)
    lf = pd.read_parquet(lf_path)

    lr = lr.merge(lf[["track_id", "title"]], on="track_id", how="left")
    results = [classify_row(t, vt, corpus) for t, vt in zip(lr["text"], lr["title"])]
    res_df = pd.DataFrame(results)
    out = pd.concat(
        [lr[["track_id", "video_id", "n_segments", "title"]].reset_index(drop=True), res_df],
        axis=1,
    )
    out = out.merge(
        lf[["track_id", "handle", "n_words"]],
        on="track_id", how="left",
    )
    # video_views trong lyrics_features thiếu 130/308 dòng -> lấy view_count
    # đúng từ selected_videos.parquet (nguồn gốc, đầy đủ hơn) theo video_id.
    if sel_path.exists():
        sel = pd.read_parquet(sel_path)[["video_id", "view_count"]].drop_duplicates("video_id")
        out = out.merge(sel, on="video_id", how="left").rename(columns={"view_count": "video_views"})

    out_dir = niche / "02_analysis"
    out_dir.mkdir(parents=True, exist_ok=True)
    out.to_parquet(out_dir / "pd_classification.parquet", index=False)
    out.to_csv(out_dir / "pd_classification.csv", index=False)

    # tóm tắt cấp track
    print("=== Phân loại theo TRACK (n=%d) ===" % len(out))
    print(out["pd_class"].value_counts())
    print()

    # tóm tắt cấp video: ưu tiên nhóm có nhiều bằng chứng PD nhất nếu video
    # có nhiều track khác nhóm (1 video có thể gồm nhiều track/bài hát)
    _priority = ["HYMN_PARTIAL_PD", "HYMN_PARTIAL_CHECK_YEAR", "SCRIPTURE_PARAPHRASE", "NEW_COMPOSITION"]
    vid_summary = out.groupby("video_id")["pd_class"].apply(
        lambda s: next(c for c in _priority if (s == c).any())
    )
    print("=== Phân loại theo VIDEO (n=%d) ===" % len(vid_summary))
    print(vid_summary.value_counts())

    # ví dụ khớp hymn để soát thủ công (không in toàn văn, chỉ tên + điểm)
    hymn_hits = out[out["pd_class"].isin(["HYMN_PARTIAL_PD", "HYMN_PARTIAL_CHECK_YEAR"])]
    if len(hymn_hits):
        print()
        print("=== Các track khớp hymn (để soát thủ công) ===")
        print(hymn_hits[["title", "matched_hymn", "match_score", "pd_class"]].to_string(index=False))

if __name__ == "__main__":
    main()
