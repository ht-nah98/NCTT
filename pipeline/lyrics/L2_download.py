"""L2 · TẢI AUDIO — yt-dlp lấy audio từng video trong COHORT, chuẩn hoá bằng ffmpeg.

CHECKPOINT: mỗi video xong ghi một dòng vào MANIFEST.jsonl. Chạy lại thì bỏ qua
video đã có file. CPU/mạng chạy nhiều giờ, đứt giữa chừng là chuyện thường —
không có checkpoint thì mỗi lần lỗi là mất sạch.

HAI ĐỊNH DẠNG, HAI MỤC ĐÍCH:
  mp3 128k stereo  → nghe/kiểm tra thủ công, giữ lại phân tích audio sau này
  wav 16kHz mono   → đầu vào ASR (Whisper resample về 16k mono, làm sẵn thì
                     khỏi ffmpeg lại ở mỗi lần phiên âm)

Đầu ra: <N>/00_input/lyrics/audio/{mp3,wav16}/<video_id>.*
        <N>/00_input/lyrics/MANIFEST.jsonl
"""
import json, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import niche_paths

N, P, _ = niche_paths("00_input")
BASE = N / "00_input" / "lyrics"
MP3 = BASE / "audio" / "mp3"
WAV = BASE / "audio" / "wav16"
MANIFEST = BASE / "MANIFEST.jsonl"
for d in (MP3, WAV):
    d.mkdir(parents=True, exist_ok=True)

SLEEP = 3          # giãn cách giữa các video — tránh bị chặn tốc độ
RETRY = 2


def done_ids():
    if not MANIFEST.exists():
        return set()
    out = set()
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            if r.get("ok"):
                out.add(r["video_id"])
    return out


def fetch(vid):
    """Tải audio tốt nhất → mp3. Trả (ok, ghi chú)."""
    url = f"https://www.youtube.com/watch?v={vid}"
    tmp = MP3 / f"{vid}.%(ext)s"
    # gọi qua -m: lệnh `yt-dlp` trong PATH có thể là bản cũ đã bị YouTube từ chối
    cmd = [sys.executable, "-m", "yt_dlp",
           "-x", "--audio-format", "mp3", "--audio-quality", "128K",
           "-o", str(tmp), "--no-playlist", "--quiet", "--no-warnings",
           "--retries", "3", url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    f = MP3 / f"{vid}.mp3"
    if r.returncode != 0 or not f.exists():
        return False, (r.stderr or "")[-200:]
    return True, ""


def to_wav16(vid):
    """mp3 → wav 16kHz mono, định dạng ASR mong đợi."""
    src, dst = MP3 / f"{vid}.mp3", WAV / f"{vid}.wav"
    r = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
         "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(dst)],
        capture_output=True, text=True, timeout=900)
    return dst.exists() and r.returncode == 0


def main():
    cohort = json.loads((BASE / "COHORT.json").read_text(encoding="utf-8"))
    vids = cohort["videos"]
    skip = done_ids()
    todo = [v for v in vids if v["video_id"] not in skip]
    print(f"Tổng {len(vids)} · đã có {len(skip)} · cần tải {len(todo)}")

    ok = fail = 0
    with MANIFEST.open("a", encoding="utf-8") as mf:
        for i, v in enumerate(todo, 1):
            vid = v["video_id"]
            t0 = time.time()
            good, err = False, ""
            for attempt in range(RETRY):
                good, err = fetch(vid)
                if good:
                    break
                time.sleep(5)
            if good:
                good = to_wav16(vid)
                if not good:
                    err = "ffmpeg chuyển wav16 thất bại"
            rec = {"video_id": vid, "handle": v["handle"], "ok": good,
                   "sec": round(time.time() - t0, 1), "err": err,
                   "duration_sec": v["duration_sec"]}
            mf.write(json.dumps(rec, ensure_ascii=False) + "\n")
            mf.flush()
            ok, fail = ok + good, fail + (not good)
            mark = "✓" if good else "✗"
            print(f"  [{i}/{len(todo)}] {mark} {vid} {v['handle'][:24]:24s} "
                  f"{rec['sec']:6.1f}s" + (f"  {err[:60]}" if err else ""))
            time.sleep(SLEEP)

    print(f"\n✅ xong: {ok} thành công · {fail} lỗi")
    print(f"   mp3: {len(list(MP3.glob('*.mp3')))} file · wav16: {len(list(WAV.glob('*.wav')))} file")


if __name__ == "__main__":
    main()
