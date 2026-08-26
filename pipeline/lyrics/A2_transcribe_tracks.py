"""A2 · PHIÊN ÂM TỪNG BÀI — faster-whisper trên CPU, mỗi wav là một bài hát.

KHÁC L3 Ở ĐÂU: L3 phiên âm cả video rồi gán đoạn về track bằng ranh giới
chapter — đoạn nằm vắt qua ranh giới phải đoán thuộc bài nào. A2 không có
việc đó: đầu vào đã là một bài, `track_id` biết trước từ tên file.

GIỮ NGUYÊN BA QUYẾT ĐỊNH ĐÃ TRẢ GIÁ Ở L3:
  1. faster-whisper (CTranslate2) + int8 — nhanh ~8× openai-whisper trên CPU
  2. KHÔNG dùng VAD Silero (T62). Đã thử ở L3 và hỏng nặng: video có giọng
     suốt 98% thời lượng bị loại sạch còn 0 đoạn. Silero huấn luyện cho giọng
     NÓI; giọng HÁT ngân dài + nhạc đệm chồng lên bị xếp "không phải speech".
     Nguy hiểm nhất là NÓ KHÔNG BÁO LỖI — track bị gắn nhãn "nhạc nền" trông
     y hệt dữ liệu hợp lệ. Thay bằng no_speech_prob đo trên nội dung thật.
  3. condition_on_previous_text=False — lời hát lặp nhiều, bật lên thì model
     trôi vào vòng lặp tự sinh.

T69 · KHÔNG PHÂN LOẠI NHẠC NỀN BẰNG `no_speech_prob`. Bản đầu của A2 bê
nguyên ngưỡng của L3 (`no_speech_prob<=0,60` → `voice_ratio<0,15` là nhạc nền)
và **gắn nhãn sai 7/25 track đầu tiên** — cả bảy đều hát đầy đủ 99-189 chữ.
Đo trên 533 đoạn của ngách này: `no_speech_prob` trung vị = **0,57**, tức
ngưỡng 0,60 cắt ngang giữa vùng giọng hát BÌNH THƯỜNG. Whisper vốn không chắc
chắn về giọng HÁT — đúng gốc rễ của T62, chỉ đổi lớp vỏ từ Silero sang ngưỡng
số. Cùng một cạm bẫy: dữ liệu sai trông y hệt dữ liệu đúng, không có lỗi nào
được ném ra.

Thay bằng MẬT ĐỘ CHỮ — thứ thật sự phân biệt hát với nhạc đệm. Nhạc không lời
cho ra rất ít chữ; bài hát thật trong ngách này thấp nhất là 32 chữ/phút.
Ngưỡng 12 chữ/phút nằm giữa hai vùng, không sát mép bên nào.

ĐO THẬT trên máy này (20 nhân, model `small`, int8): RTF ≈ 0,043 →
21,1 giờ audio ≈ 55 phút. Nhanh hơn con số 0,06 ghi trong README vì bài lẻ
ngắn, không phải file 2 tiếng.

CHECKPOINT: mỗi track một file JSON. Chạy lại bỏ qua file đã có, nên đứt
giữa chừng không mất gì.

Đầu ra: <N>/00_input/lyrics/transcripts_track/<track_key>.json
"""
import argparse, json, sys, time
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import niche_paths

N, P, _ = niche_paths("00_input")
BASE = N / "00_input" / "lyrics"
LEDGER = BASE / "track_audio.parquet"
TR = BASE / "transcripts_track"
TR.mkdir(parents=True, exist_ok=True)

# NGƯỠNG — ĐO TRÊN CHÍNH NGÁCH NÀY, ĐỪNG ĐOÁN LẠI (xem T69 ở đầu file)
NO_SPEECH_MAX = 0.85  # chỉ để ĐẾM đoạn "chắc chắn có giọng", KHÔNG dùng phân loại
WPM_MIN = 12          # dưới mức này mới là nhạc không lời — bài hát thật ≥32
MIN_WORDS = 25        # quá ít chữ thì mật độ không đáng tin
BEAM = 1              # beam=1 nhanh gấp đôi beam=5, khác biệt nhỏ trên lời hát


def load_model(name, threads):
    from faster_whisper import WhisperModel
    return WhisperModel(name, device="cpu", compute_type="int8",
                        cpu_threads=threads, num_workers=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="small")
    ap.add_argument("--threads", type=int, default=16)
    ap.add_argument("--limit", type=int, default=0, help="0 = tất cả")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--songs-only", action="store_true",
                    help="bỏ qua track <60s (intro/outro)")
    a, _rest = ap.parse_known_args()

    if not LEDGER.exists():
        sys.exit("chưa có track_audio.parquet — chạy A1_ingest.py trước")
    L = pd.read_parquet(LEDGER)
    L = L[L.ok & L.wav_path.notna()]
    if a.songs_only:
        L = L[L.is_song]

    todo = [r for r in L.itertuples()
            if not (TR / f"{r.track_key}.json").exists()]
    if a.limit:
        todo = todo[:a.limit]

    have = len(list(TR.glob("*.json")))
    print(f"track dùng được {len(L)} · đã phiên âm {have} · làm {len(todo)}")
    if not todo:
        print("không còn gì để làm"); return
    print(f"   ước tính ~{sum(r.duration_s for r in todo)*0.05/60:.0f} phút "
          f"(RTF ~0,05 · {sum(r.duration_s for r in todo)/3600:.1f} giờ audio)")

    print(f"nạp model '{a.model}' int8 / {a.threads} luồng …")
    model = load_model(a.model, a.threads)

    t_all = time.time()
    for i, r in enumerate(todo, 1):
        t0 = time.time()
        segs, info = model.transcribe(
            r.wav_path, language=a.lang, beam_size=BEAM,
            vad_filter=False,                    # xem T62 ở đầu file
            condition_on_previous_text=False,    # lời hát lặp → tránh trôi
            word_timestamps=True,
        )
        rows = [{"start": round(s.start, 2), "end": round(s.end, 2),
                 "text": s.text.strip(),
                 "avg_logprob": round(getattr(s, "avg_logprob", 0), 3),
                 "no_speech_prob": round(getattr(s, "no_speech_prob", 0), 3),
                 # đầu vào ĐÃ là một bài → gán thẳng, không phải đoán ranh giới
                 "track_id": r.track_id}
                for s in segs]
        dur = float(info.duration)
        # `sung` chỉ để THỐNG KÊ mô tả — không dùng để phân loại (T69)
        sung = [x for x in rows if x["no_speech_prob"] <= NO_SPEECH_MAX]
        voiced = sum(x["end"] - x["start"] for x in sung)
        ratio = voiced / dur if dur else 0
        n_words = sum(len(x["text"].split()) for x in rows)
        wpm = n_words / (dur / 60) if dur else 0
        rec = {
            "track_id": r.track_id, "track_key": r.track_key,
            "video_id": r.video_id, "title": r.title,
            "model": a.model, "language": info.language,
            "duration_sec": round(dur, 1),
            "voiced_sec": round(voiced, 1),
            "voice_ratio": round(ratio, 3),
            "n_words": n_words,
            "words_per_min": round(wpm, 1),
            # phân loại bằng mật độ chữ, KHÔNG bằng no_speech_prob (T69)
            "is_instrumental": bool(n_words < MIN_WORDS or wpm < WPM_MIN),
            "n_segments": len(rows), "n_segments_voiced": len(sung),
            "boundary_source": "pre_split", "tier": "gold",
            "runtime_sec": round(time.time() - t0, 1),
            "rtf": round((time.time() - t0) / dur, 3) if dur else None,
            "segments": rows,
        }
        (TR / f"{r.track_key}.json").write_text(
            json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
        tag = "NHẠC NỀN" if rec["is_instrumental"] else f"{n_words:4d} chữ"
        el = time.time() - t_all
        eta = el / i * (len(todo) - i) / 60
        print(f"  [{i}/{len(todo)}] {r.track_id:22s} {dur/60:5.1f}ph → {tag}"
              f" · {wpm:5.1f} chữ/ph · {rec['runtime_sec']:5.1f}s"
              f" (×{rec['rtf']}) · còn ~{eta:.0f}ph")

    n = len(list(TR.glob("*.json")))
    print(f"\n✅ {n} bản phiên âm tại {TR}")
    print(f"   tổng {(time.time()-t_all)/60:.1f} phút")


if __name__ == "__main__":
    main()
