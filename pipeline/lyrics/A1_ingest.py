"""A1 · NHẬN AUDIO ĐÃ CẮT — quét thư mục track rời, ghi sổ, chuyển wav16.

VÌ SAO CÓ NHÁNH A: L2 tải audio bằng yt-dlp đã chết vì 403 theo độ dài
(xem README, đo 2026-08-19) — 5/5 video thất bại, chỉ 1 transcript ra đời.
Nhánh A đi vòng qua bức tường đó: audio lấy sẵn từ ngoài, và tốt hơn L2 định
làm — đã CẮT SẴN THEO TỪNG BÀI, có tên bài, thay vì cả video dài 2 tiếng.

KHÁC BIỆT CỐT LÕI SO VỚI L3:
    L3  1 wav = 1 video → phiên âm cả video → cắt đoạn về track bằng chapter
    A2  1 wav = 1 BÀI   → phiên âm từng bài → không phải đoán ranh giới
Ranh giới do người cắt đặt, không phải thuật toán dò. Theo kỷ luật dữ liệu ở
L4 thì đây là hạng `gold`: tin được cho cả phân tích âm thanh.

THAM CHIẾU TẠI CHỖ, KHÔNG CHÉP: file gốc 1,2GB nằm nguyên ở thư mục nguồn.
Ta chỉ ghi wav16 (~600MB) vào ngách và lưu `src_path` + `sha1` để truy vết.
Xoá thư mục nguồn thì wav16 vẫn dùng được; `A1 --verify` sẽ báo file gốc mất.

BỎ QUA `audio_cache/`: đó là video nguồn CHƯA cắt, 2,5GB, trùng nội dung với
`tracks/`. Đưa vào chỉ tổ nhân đôi dữ liệu và gây lẫn cấp phân tích.

Đầu ra: <N>/00_input/lyrics/audio/wav16/<track_key>.wav
        <N>/00_input/lyrics/track_audio.parquet
"""
import argparse, hashlib, json, subprocess, sys, time
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import niche_paths

N, P, _ = niche_paths("00_input")
BASE = N / "00_input" / "lyrics"
WAV = BASE / "audio" / "wav16"
LEDGER = BASE / "track_audio.parquet"
WAV.mkdir(parents=True, exist_ok=True)

SHA_BYTES = 1 << 20   # băm 1MB đầu — đủ phân biệt file, khỏi đọc hết 1,2GB
MIN_SEC = 60          # dưới mức này là intro/outro, không phải bài hát


def track_key(track_id: str) -> str:
    """`_ycC4y-4sYo#02` → `_ycC4y-4sYo__02`. Dấu # hỏng glob và tên file."""
    return track_id.replace("#", "__")


def sha1_head(p: Path) -> str:
    h = hashlib.sha1()
    with p.open("rb") as f:
        h.update(f.read(SHA_BYTES))
    return h.hexdigest()[:16]


def probe(p: Path) -> dict:
    """Độ dài THẬT đo từ file, không tin số trong _index.json."""
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration,bit_rate", "-of", "json", str(p)],
        capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        return {}
    fm = json.loads(r.stdout).get("format", {})
    return {"duration_s": round(float(fm.get("duration", 0)), 1),
            "bit_rate": int(fm.get("bit_rate") or 0)}


def to_wav16(src: Path, dst: Path) -> bool:
    """→ wav 16kHz mono, đúng định dạng Whisper mong đợi (khỏi resample lại)."""
    r = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
         "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(dst)],
        capture_output=True, text=True, timeout=900)
    return dst.exists() and dst.stat().st_size > 1000 and r.returncode == 0


def load_index(share: Path) -> list[dict]:
    """_index.json là nguồn sự thật cho track_id/title/video_id."""
    idx = share / "tracks" / "_index.json"
    if not idx.exists():
        sys.exit(f"Không thấy {idx} — thư mục nguồn có đúng cấu trúc không?")
    return json.loads(idx.read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--share", default=str(Path.home() / "Downloads/audio-dna-share"),
                    help="thư mục chứa tracks/_index.json")
    ap.add_argument("--limit", type=int, default=0, help="0 = tất cả")
    ap.add_argument("--verify", action="store_true",
                    help="chỉ kiểm tra sổ cũ, không chuyển gì")
    a, _rest = ap.parse_known_args()

    share = Path(a.share).expanduser()
    rows_idx = load_index(share)

    if a.verify:
        if not LEDGER.exists():
            sys.exit("chưa có track_audio.parquet — chạy A1 trước")
        L = pd.read_parquet(LEDGER)
        miss_src = [r for r in L.itertuples() if not Path(r.src_path).exists()]
        miss_wav = [r for r in L.itertuples() if not Path(r.wav_path).exists()]
        print(f"sổ có {len(L)} track")
        print(f"  file gốc mất : {len(miss_src)}")
        print(f"  wav16 mất    : {len(miss_wav)}")
        for r in miss_wav[:5]:
            print(f"    ✗ {r.track_id}")
        if not miss_src and not miss_wav:
            print("✅ toàn vẹn")
        return

    done = {}
    if LEDGER.exists():
        done = {r.track_id: r for r in pd.read_parquet(LEDGER).itertuples()}

    todo = [r for r in rows_idx
            if r["track_id"] not in done
            or not (WAV / f"{track_key(r['track_id'])}.wav").exists()]
    if a.limit:
        todo = todo[:a.limit]

    print(f"index {len(rows_idx)} track · đã có {len(rows_idx)-len(todo)} · làm {len(todo)}")

    out, skipped = [], 0
    for i, r in enumerate(todo, 1):
        tid = r["track_id"]
        src = share / "tracks" / r["file"]
        if not src.exists():
            print(f"  [{i}/{len(todo)}] ✗ {tid} — không thấy file gốc")
            skipped += 1
            continue
        t0 = time.time()
        meta = probe(src)
        dur = meta.get("duration_s", 0)
        key = track_key(tid)
        dst = WAV / f"{key}.wav"
        ok = dst.exists() or to_wav16(src, dst)
        out.append({
            "track_id": tid, "track_key": key,
            "video_id": r["video_id"], "channel_id": r.get("channel_id"),
            "title": r.get("title"),
            "src_path": str(src), "src_bytes": src.stat().st_size,
            "src_sha1": sha1_head(src),
            "wav_path": str(dst) if ok else None,
            "duration_s": dur,
            "index_duration_s": r.get("duration_s"),
            "bit_rate": meta.get("bit_rate"),
            # ranh giới do người cắt đặt sẵn → tin được, khác hẳn dò tự động
            "boundary_source": "pre_split", "tier": "gold",
            "is_song": dur >= MIN_SEC,
            "ok": bool(ok),
        })
        mark = "✓" if ok else "✗"
        print(f"  [{i}/{len(todo)}] {mark} {tid:24s} {dur/60:5.1f}ph "
              f"{time.time()-t0:5.1f}s  {str(r.get('title'))[:34]}")

    # gộp với sổ cũ, bản mới thắng
    New = pd.DataFrame(out)
    if LEDGER.exists() and len(New):
        Old = pd.read_parquet(LEDGER)
        Old = Old[~Old.track_id.isin(New.track_id)]
        New = pd.concat([Old, New], ignore_index=True)
    elif not len(New):
        New = pd.read_parquet(LEDGER) if LEDGER.exists() else New
    if len(New):
        New = New.sort_values("track_id").reset_index(drop=True)
        New.to_parquet(LEDGER, index=False)

    good = New[New.ok] if "ok" in New else New
    drift = New[(New.index_duration_s.notna()) &
                ((New.duration_s - New.index_duration_s).abs() > 2)] if len(New) else New
    print(f"\n✅ {LEDGER}  ({len(New)} track)")
    print(f"   wav16 dựng được : {len(good)} · lỗi/thiếu {len(New)-len(good)+skipped}")
    print(f"   tổng thời lượng : {good.duration_s.sum()/3600:.1f} giờ")
    print(f"   là bài hát (≥{MIN_SEC}s): {int(good.is_song.sum())}")
    if len(drift):
        print(f"   ⚠ {len(drift)} track lệch >2s so với _index.json — dùng số đo thật")


if __name__ == "__main__":
    main()
