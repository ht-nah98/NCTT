"""L3 · PHIÊN ÂM — faster-whisper trên CPU, lọc VAD trước để bỏ nhạc không lời.

CHẠY TRÊN CPU (người dùng chốt: GPU đang bận). Ba quyết định để CPU chịu nổi
39,7 giờ audio:

  1. faster-whisper (CTranslate2) thay openai-whisper — cùng model, nhanh ~4×
  2. lượng tử hoá int8 — nhanh thêm ~2×, sai số không đáng kể ở tác vụ này
  3. KHÔNG dùng VAD của Silero (T62). Đã thử và nó hỏng nặng: một video có
     giọng suốt 98% thời lượng bị Silero loại sạch còn 0 đoạn. Silero được
     huấn luyện cho GIỌNG NÓI — giọng HÁT có cao độ kéo dài và nhạc đệm chồng
     lên nên bị phân loại thành "không phải speech". Nguy hiểm ở chỗ nó không
     báo lỗi: video bị đánh dấu nhầm "nhạc nền" trông y hệt dữ liệu hợp lệ.
     Thay bằng no_speech_prob của chính Whisper — đo trên nội dung đã phiên âm
     thật, không phải đoán trước.

MODEL: mặc định 'small'. Với giọng hát, 'medium' chính xác hơn rõ rệt nhưng
chậm ~3×. Đổi bằng --model. Trên 20 nhân, 'small' ≈ 1,5-2,5× thời gian thật.

CHECKPOINT: mỗi video ghi 1 file JSON riêng. Chạy lại bỏ qua file đã có.

GÁN VỀ TRACK: phiên âm cả video một lần (rẻ hơn cắt file rồi chạy 216 lần),
rồi dùng ranh giới chapter trong tracks.parquet để gán từng đoạn về đúng
track_id. Nhờ vậy lyrics ghép được với audio_dna vốn ở cấp track.

Đầu ra: <N>/00_input/lyrics/transcripts/<video_id>.json
"""
import argparse, json, sys, time
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import niche_paths

N, P, _ = niche_paths("00_input")
BASE = N / "00_input" / "lyrics"
WAV = BASE / "audio" / "wav16"
TR = BASE / "transcripts"
TR.mkdir(parents=True, exist_ok=True)

TRACKS = None
VOICE_MIN = 0.15      # dưới mức này coi là nhạc không lời
NO_SPEECH_MAX = 0.60  # đoạn có no_speech_prob cao hơn mức này không tính là lời
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
    a = ap.parse_args()

    global TRACKS
    tf = BASE / "tracks.parquet"
    TRACKS = pd.read_parquet(tf) if tf.exists() else None
    if TRACKS is None:
        print("⚠ chưa có tracks.parquet — chạy L4 trước để gán lyrics về track")

    wavs = sorted(WAV.glob("*.wav"))
    todo = [w for w in wavs if not (TR / f"{w.stem}.json").exists()]
    if a.limit:
        todo = todo[:a.limit]
    print(f"wav có {len(wavs)} · đã phiên âm {len(wavs)-len([w for w in wavs if not (TR/f'{w.stem}.json').exists()])} · làm {len(todo)}")
    if not todo:
        print("không còn gì để làm"); return

    print(f"nạp model '{a.model}' int8 / {a.threads} luồng …")
    model = load_model(a.model, a.threads)

    for i, w in enumerate(todo, 1):
        vid, t0 = w.stem, time.time()
        segs, info = model.transcribe(
            str(w), language=a.lang, beam_size=BEAM,
            vad_filter=False,                      # xem T62 ở đầu file
            condition_on_previous_text=False,      # lời hát lặp → tránh trôi
            word_timestamps=True,
        )
        rows = []
        for s in segs:
            rows.append({"start": round(s.start, 2), "end": round(s.end, 2),
                         "text": s.text.strip(),
                         "avg_logprob": round(getattr(s, "avg_logprob", 0), 3),
                         "no_speech_prob": round(getattr(s, "no_speech_prob", 0), 3)})
        dur = float(info.duration)
        # chỉ tính đoạn Whisper thực sự tin là có tiếng người
        sung = [r for r in rows if r["no_speech_prob"] <= NO_SPEECH_MAX]
        voiced = sum(r["end"] - r["start"] for r in sung)
        ratio = voiced / dur if dur else 0
        rec = {
            "video_id": vid, "model": a.model, "language": info.language,
            "duration_sec": round(dur, 1),
            "voiced_sec": round(voiced, 1),
            "voice_ratio": round(ratio, 3),
            "is_instrumental": bool(ratio < VOICE_MIN),
            "n_segments": len(rows),
            "n_segments_voiced": len(sung),
            "runtime_sec": round(time.time() - t0, 1),
            "rtf": round((time.time() - t0) / dur, 2) if dur else None,
            "segments": rows,
        }
        # gán từng đoạn về track theo điểm giữa đoạn — đoạn nằm vắt qua ranh
        # giới thì thuộc về track chiếm phần lớn nó
        tk = TRACKS[TRACKS.video_id == vid] if TRACKS is not None else None
        if tk is not None and len(tk):
            for r in rows:
                mid = (r["start"] + r["end"]) / 2
                hit = tk[(tk.start_s <= mid) & (mid < tk.end_s)]
                r["track_id"] = hit.iloc[0].track_id if len(hit) else None
            rec["n_tracks"] = int(tk.shape[0])
            rec["n_seg_mapped"] = sum(1 for r in rows if r.get("track_id"))

        (TR / f"{vid}.json").write_text(
            json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
        tag = "NHẠC NỀN" if rec["is_instrumental"] else f"{len(rows):4d} đoạn"
        print(f"  [{i}/{len(todo)}] {vid} {dur/60:5.1f}ph → {tag} "
              f"· giọng {ratio:.0%} · {rec['runtime_sec']:.0f}s (×{rec['rtf']})")

    print(f"\n✅ {len(list(TR.glob('*.json')))} bản phiên âm tại {TR}")


if __name__ == "__main__":
    main()
