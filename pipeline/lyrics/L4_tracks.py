"""L4 · RANH GIỚI TRACK — lấy chapter YouTube trực tiếp, tự đứng độc lập.

VÌ SAO CẦN: chỉ 20,7% video trong ngách có tracklist trong mô tả, nên không
cắt được lyrics về từng bài. Chapter của YouTube giải được việc này và lấy
được BẰNG METADATA — không tải luồng audio nên KHÔNG dính 403.

KHÔNG PHỤ THUỘC REPO NGOÀI: bản trước đọc p1_tracks.jsonl của repo audio-dna.
Bỏ hẳn. Repo đó chỉ còn là tài liệu tham chiếu, không phải đầu vào. Hệ thống
phải chạy được với bất kỳ danh sách kênh nào, không chỉ corpus có sẵn.

KỶ LUẬT DỮ LIỆU (học từ D-010 của repo): ranh giới từ chapter là tin được;
ranh giới dò bằng thuật toán thì KHÔNG dùng cho phân tích âm thanh vì lệch
vài giây là hỏng BPM/hoà âm. Với LYRICS thì lệch vài giây chỉ làm một hai
dòng rơi nhầm bài — chấp nhận được. Nên ta vẫn ghi cả hai, đánh dấu bằng
`tier`, và để bước sau tự chọn.

Đầu ra: <N>/00_input/lyrics/tracks.parquet
        <N>/00_input/lyrics/chapters_raw.json  (đệm, khỏi gọi mạng lại)
"""
import argparse, json, subprocess, sys, time
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import niche_paths

N, P, _ = niche_paths("00_input")
BASE = N / "00_input" / "lyrics"
CACHE = BASE / "chapters_raw.json"

MIN_SEC = 60          # dưới mức này là intro/outro, không phải bài hát


def fetch_chapters(vid: str) -> dict | None:
    """Metadata thôi — không tải audio nên không dính giới hạn fragment."""
    r = subprocess.run(
        [sys.executable, "-m", "yt_dlp", "--skip-download", "--dump-single-json",
         "--no-warnings", "--no-playlist", f"https://www.youtube.com/watch?v={vid}"],
        capture_output=True, text=True, timeout=180)
    if r.returncode != 0 or not r.stdout.strip():
        return None
    d = json.loads(r.stdout)
    return {"chapters": d.get("chapters") or [],
            "duration": d.get("duration"),
            "title": d.get("title")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="gọi lại mạng, bỏ đệm")
    a = ap.parse_args()

    cohort = json.loads((BASE / "COHORT.json").read_text(encoding="utf-8"))
    cv = {v["video_id"]: v for v in cohort["videos"]}

    cache = {} if a.refresh or not CACHE.exists() else json.loads(
        CACHE.read_text(encoding="utf-8"))
    todo = [v for v in cv if v not in cache]
    if todo:
        print(f"lấy chapter cho {len(todo)} video …")
        for i, vid in enumerate(todo, 1):
            got = fetch_chapters(vid)
            cache[vid] = got or {"chapters": [], "duration": None, "error": True}
            n = len(cache[vid]["chapters"])
            print(f"  [{i}/{len(todo)}] {vid} → {n} chapter"
                  + ("  (lỗi)" if got is None else ""))
            CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
            time.sleep(1)

    rows = []
    for vid, meta in cache.items():
        if vid not in cv:
            continue
        v, chs = cv[vid], meta.get("chapters") or []
        if chs:
            for i, c in enumerate(chs, 1):
                st, en = float(c["start_time"]), float(c["end_time"])
                rows.append({
                    "track_id": f"{vid}#{i:02d}", "video_id": vid,
                    "handle": v["handle"], "index": i,
                    "start_s": round(st, 1), "end_s": round(en, 1),
                    "duration_s": round(en - st, 1),
                    "title": c.get("title"), "boundary_source": "chapter",
                    "tier": "gold", "video_views": v["view_count"],
                })
        else:
            # không có chapter → coi cả video là một đơn vị, đánh dấu weak
            rows.append({
                "track_id": f"{vid}#01", "video_id": vid, "handle": v["handle"],
                "index": 1, "start_s": 0.0,
                "end_s": float(v["duration_sec"]),
                "duration_s": float(v["duration_sec"]),
                "title": None, "boundary_source": "whole_video",
                "tier": "weak", "video_views": v["view_count"],
            })

    T = pd.DataFrame(rows)
    T["is_song"] = T.duration_s >= MIN_SEC
    T["to_transcribe"] = T.is_song            # lyrics chịu được ranh giới lệch
    T.to_parquet(BASE / "tracks.parquet", index=False)

    has_ch = T[T.tier.eq("gold")].video_id.nunique()
    print(f"\n✅ {BASE/'tracks.parquet'}")
    print(f"   {len(T)} track / {T.video_id.nunique()} video")
    print(f"   có chapter: {has_ch} video → {int(T.tier.eq('gold').sum())} track")
    print(f"   không chapter: {T.video_id.nunique()-has_ch} video "
          f"(để nguyên cả video làm 1 đơn vị)")
    print(f"   sẽ phiên âm: {int(T.to_transcribe.sum())} track · "
          f"{T[T.to_transcribe].duration_s.sum()/3600:.1f} giờ")


if __name__ == "__main__":
    main()
