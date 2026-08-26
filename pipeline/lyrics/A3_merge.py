"""A3 · GỘP VỀ HỢP ĐỒNG CỦA L5 — nhánh A xuất ra đúng khuôn L3 đang xuất.

VÌ SAO CẦN BƯỚC NÀY: L5_features đọc `transcripts/*.json`, mỗi file MỘT VIDEO,
gom đoạn theo `segments[].track_id`. A2 lại ghi mỗi file MỘT BÀI. A3 lắp khớp
hai bên — nhờ vậy **L5 không phải sửa một dòng nào**, và mọi bước phân tích
phía sau (04h_audio, 08_synthesis…) tiếp tục chạy như cũ.

Đây là chỗ duy nhất trong nhánh A biết về khuôn dữ liệu của L3. Đổi khuôn thì
chỉ sửa file này.

KHÔNG GHI ĐÈ DỮ LIỆU L3: nếu `transcripts/<video>.json` đã có từ L3, mặc định
A3 bỏ qua và báo. Dữ liệu L3 lấy từ video đầy đủ, ranh giới suy từ chapter;
dữ liệu A2 cắt sẵn theo bài. Trộn im lặng hai nguồn là cách chắc chắn để sau
này không ai biết một con số đến từ đâu. Muốn thay thì `--overwrite`.

CẬP NHẬT tracks.parquet: track nào có audio cắt sẵn thì nâng `boundary_source`
thành `pre_split`. Track cũ mà nguồn không có thì giữ nguyên, không xoá —
L4 vẫn là nguồn sự thật cho phần phủ sóng của COHORT.

Đầu ra: <N>/00_input/lyrics/transcripts/<video_id>.json   (khuôn của L3)
        <N>/00_input/lyrics/tracks.parquet                (cập nhật tại chỗ)
"""
import argparse, json, sys
from collections import defaultdict
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import niche_paths

N, P, _ = niche_paths("00_input")
BASE = N / "00_input" / "lyrics"
SRC = BASE / "transcripts_track"
DST = BASE / "transcripts"
LEDGER = BASE / "track_audio.parquet"
TRACKS = BASE / "tracks.parquet"
DST.mkdir(parents=True, exist_ok=True)


def provenance(p: Path) -> str:
    """File transcript này do nhánh nào sinh ra?"""
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return "unreadable"
    return d.get("source_branch") or ("A" if d.get("boundary_source") == "pre_split" else "L3")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true",
                    help="ghi đè cả transcript do L3 sinh ra")
    ap.add_argument("--no-tracks-update", action="store_true",
                    help="không đụng vào tracks.parquet")
    a, _rest = ap.parse_known_args()

    files = sorted(SRC.glob("*.json"))
    if not files:
        sys.exit(f"chưa có transcript nào ở {SRC} — chạy A2 trước")

    by_video = defaultdict(list)
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        by_video[d["video_id"]].append(d)

    written = skipped = 0
    seen_tracks = []
    for vid, recs in sorted(by_video.items()):
        out = DST / f"{vid}.json"
        if out.exists() and not a.overwrite:
            src_branch = provenance(out)
            if src_branch == "L3":
                print(f"  ⏭  {vid} — đã có transcript của L3, giữ nguyên "
                      f"(dùng --overwrite để thay)")
                skipped += 1
                continue

        # sắp bài theo thứ tự trong video để timeline liền mạch
        recs.sort(key=lambda r: r["track_id"])
        segs, offset = [], 0.0
        for r in recs:
            for s in r["segments"]:
                # dịch mốc thời gian từ nội-bộ-bài sang toàn-video, để cùng
                # trục với transcript của L3
                segs.append({**s,
                             "start": round(s["start"] + offset, 2),
                             "end": round(s["end"] + offset, 2),
                             "track_start": s["start"], "track_end": s["end"]})
            offset += r["duration_sec"]
            seen_tracks.append(r["track_id"])

        dur = sum(r["duration_sec"] for r in recs)
        voiced = sum(r["voiced_sec"] for r in recs)
        rec = {
            "video_id": vid,
            "model": recs[0].get("model"),
            "language": recs[0].get("language"),
            "duration_sec": round(dur, 1),
            "voiced_sec": round(voiced, 1),
            "voice_ratio": round(voiced / dur, 3) if dur else 0,
            "is_instrumental": all(r["is_instrumental"] for r in recs),
            "n_segments": len(segs),
            "n_segments_voiced": sum(r["n_segments_voiced"] for r in recs),
            "n_tracks": len(recs),
            "n_seg_mapped": len(segs),      # 100% — track_id biết trước
            "source_branch": "A",
            "boundary_source": "pre_split",
            "tier": "gold",
            "segments": segs,
        }
        out.write_text(json.dumps(rec, ensure_ascii=False, indent=1),
                       encoding="utf-8")
        written += 1
        print(f"  ✓ {vid}  {len(recs):3d} bài · {len(segs):5d} đoạn · "
              f"{dur/60:6.1f}ph · giọng {rec['voice_ratio']:.0%}")

    print(f"\n✅ {written} video ghi vào {DST}" +
          (f" · {skipped} bỏ qua (dữ liệu L3)" if skipped else ""))

    if a.no_tracks_update or not TRACKS.exists() or not LEDGER.exists():
        return

    # nâng hạng ranh giới cho track có audio cắt sẵn
    T = pd.read_parquet(TRACKS)
    Lg = pd.read_parquet(LEDGER)
    Lg = Lg[Lg.ok]
    known = set(Lg.track_id)
    hit = T.track_id.isin(known)
    T.loc[hit, "boundary_source"] = "pre_split"
    T.loc[hit, "tier"] = "gold"

    # `handle` không có trong _index.json (chỉ có channel_id). Suy ngược từ
    # những track ĐÃ có handle nhờ COHORT — cùng channel_id thì cùng kênh.
    # Kênh không có trong cohort thì không suy được: dùng channel_id làm nhãn,
    # để `handle` không bao giờ rỗng (cột rỗng làm hỏng groupby ở bước sau).
    cmap = (T[["track_id", "handle"]].merge(Lg[["track_id", "channel_id"]],
                                            on="track_id")
            .dropna(subset=["handle"])
            .groupby("channel_id").handle.agg(lambda x: x.mode()[0]).to_dict())

    def as_handle(cid):
        return cmap.get(cid) or (f"channel:{cid}" if cid else None)

    # vá cả track CŨ đang rỗng handle (do lần chạy A3 trước để None)
    if T.handle.isna().any():
        cid_of = dict(zip(Lg.track_id, Lg.channel_id))
        gap = T.handle.isna() & T.track_id.isin(cid_of)
        T.loc[gap, "handle"] = T.loc[gap, "track_id"].map(
            lambda t: as_handle(cid_of.get(t)))

    # track có trong nguồn nhưng chưa từng có trong tracks.parquet → thêm mới
    new = Lg[~Lg.track_id.isin(set(T.track_id))]
    if len(new):
        add = pd.DataFrame({
            "track_id": new.track_id, "video_id": new.video_id,
            "handle": new.channel_id.map(as_handle),
            "index": new.track_id.str.split("#").str[-1].astype(int),
            "start_s": 0.0, "end_s": new.duration_s,
            "duration_s": new.duration_s, "title": new.title,
            "boundary_source": "pre_split", "tier": "gold",
            "video_views": pd.NA, "is_song": new.is_song,
            "to_transcribe": new.is_song,
        })
        T = pd.concat([T, add], ignore_index=True)

    T = T.sort_values("track_id").reset_index(drop=True)
    T.to_parquet(TRACKS, index=False)
    print(f"✅ {TRACKS} cập nhật")
    print(f"   nâng thành pre_split : {int(hit.sum())} track")
    print(f"   handle còn rỗng      : {int(T.handle.isna().sum())} track")
    print(f"   thêm mới             : {len(new)} track")
    print(f"   tổng                 : {len(T)} track / {T.video_id.nunique()} video")


if __name__ == "__main__":
    main()
