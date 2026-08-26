"""A4 · ĐỌC & XUẤT LỜI HÁT — tra cứu lyrics đã phiên âm.

DÙNG ĐỂ LÀM GÌ: `lyrics_raw.parquet` là định dạng máy đọc. Bước này lôi lời
ra dạng người đọc được, để KIỂM ĐỊNH bản phiên âm — đối chiếu tai người với
máy, tìm chỗ Whisper nghe nhầm.

⚠ RANH GIỚI PHÁT TÁN (T65): lời hát là tác phẩm có bản quyền. Bản xuất từ đây
là TÀI LIỆU NỘI BỘ để kiểm định và phân tích. KHÔNG chép vào báo cáo, brief
sản xuất, hay bất cứ thứ gì rời khỏi nhóm. Thứ đi vào báo cáo là
`lyrics_features.parquet` — mật độ chữ, tỷ lệ lặp, ngôi kể.
Vì thế bản xuất mặc định ghi vào `_local/` (đã bị .gitignore chặn).

Lý do không phải cẩn thận thừa: chép lời kênh khác vào brief thì vừa rủi ro
pháp lý vừa VÔ DỤNG — nó chỉ đạo người viết nhái lại, không tái tạo được cách
viết. Muốn tái tạo thì cần thông số, không cần bản sao.

CÁCH DÙNG:
    A4 <ngách>                        # danh sách 308 bài
    A4 <ngách> --id 04j-ZQskFJM#01    # in lời một bài
    A4 <ngách> --search "shepherd"    # tìm theo tên bài
    A4 <ngách> --export csv           # xuất toàn bộ ra _local/lyrics_all.csv
    A4 <ngách> --export md            # bản đọc cho người
    A4 <ngách> --export txt --id ...  # xuất một bài
    A4 <ngách> --review 20            # 20 bài máy nghe kém tin nhất
"""
import argparse, sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import niche_paths

N, P, _ = niche_paths("00_input")
RAW = P / "lyrics_raw.parquet"
TRACKS = N / "00_input" / "lyrics" / "tracks.parquet"
OUT = N / "_local"


def load() -> pd.DataFrame:
    if not RAW.exists():
        sys.exit(f"chưa có {RAW} — chạy L5_features.py trước")
    R = pd.read_parquet(RAW)
    if TRACKS.exists():
        T = pd.read_parquet(TRACKS)[["track_id", "title", "handle", "tier"]]
        R = R.merge(T, on="track_id", how="left")
    R["n_words"] = R.text.str.split().str.len()
    return R.sort_values("track_id").reset_index(drop=True)


def show(r) -> str:
    head = f"{r.track_id}  ·  {r.get('title') or '(không tên)'}"
    meta = (f"{r.get('handle') or '?'} · {r.n_words} chữ · "
            f"{r.end_s - r.start_s:.0f}s · tin cậy {r.mean_logprob:+.2f}")
    return f"{head}\n{meta}\n{'─'*len(head)}\n{r.text}\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", help="track_id cụ thể, vd 04j-ZQskFJM#01")
    ap.add_argument("--search", help="tìm trong TÊN BÀI")
    ap.add_argument("--grep", help="tìm trong LỜI (nội bộ — đừng dán ra ngoài)")
    ap.add_argument("--review", type=int, default=0,
                    help="N bài có tin cậy thấp nhất, để soát tay")
    ap.add_argument("--export", choices=["csv", "md", "txt"],
                    help="csv = dữ liệu thô cho bước xử lý sau")
    ap.add_argument("--limit", type=int, default=0)
    a, _rest = ap.parse_known_args()

    R = load()

    sel = R
    if a.id:
        sel = R[R.track_id == a.id]
        if not len(sel):
            sys.exit(f"không thấy track_id '{a.id}' — bỏ --id để xem danh sách")
    elif a.search:
        sel = R[R.title.fillna("").str.contains(a.search, case=False, regex=False)]
    elif a.grep:
        sel = R[R.text.str.contains(a.grep, case=False, regex=False)]
    elif a.review:
        sel = R.nsmallest(a.review, "mean_logprob")
    if a.limit:
        sel = sel.head(a.limit)

    if not len(sel):
        print("không có bài nào khớp"); return

    if a.export:
        OUT.mkdir(parents=True, exist_ok=True)
        stem = a.id.replace("#", "__") if a.id else "lyrics_all"
        f = OUT / f"{stem}.{a.export}"
        parts = []
        if a.export == "csv":
            # DỮ LIỆU THÔ cho bước xử lý sau — một dòng một bài, lời nguyên vẹn
            # ở cột `text` (giữ \n giữa các dòng hát).
            # utf-8-sig để Excel mở tiếng Việt không vỡ dấu.
            cols = ["track_id", "video_id", "handle", "title", "tier",
                    "n_words", "n_segments", "start_s", "end_s",
                    "mean_logprob", "text"]
            C = sel[[c for c in cols if c in sel.columns]].copy()
            C.to_csv(f, index=False, encoding="utf-8-sig", lineterminator="\n")
            print(f"✅ {f}  ({len(C)} bài · {C.n_words.sum():,} chữ)")
            print(f"   cột: {', '.join(C.columns)}")
            print("   ⚠ nội bộ — không dán vào báo cáo/brief (T65)")
            return
        if a.export == "md":
            parts.append("# Lời hát đã phiên âm — TÀI LIỆU NỘI BỘ\n")
            parts.append("> Tác phẩm có bản quyền. Chỉ dùng để kiểm định và "
                         "phân tích. **Không chép vào báo cáo hay brief** — "
                         "báo cáo dùng `lyrics_features.parquet`.\n")
            for r in sel.itertuples():
                parts.append(f"\n## {r.track_id} · {r.title or '(không tên)'}\n")
                parts.append(f"*{r.handle or '?'} · {r.n_words} chữ · "
                             f"tin cậy {r.mean_logprob:+.2f}*\n")
                parts.append("```\n" + r.text + "\n```\n")
        else:
            for r in sel.itertuples():
                parts.append(show(r) + "\n")
        f.write_text("\n".join(parts), encoding="utf-8")
        print(f"✅ {f}  ({len(sel)} bài)")
        print("   ⚠ nội bộ — không dán vào báo cáo/brief (T65)")
        return

    if a.id or a.grep or a.review or (a.search and len(sel) <= 3):
        for r in sel.itertuples():
            print(show(r))
        if a.review:
            print("↑ tin cậy thấp nhất — nên mở audio nghe đối chiếu")
        return

    # mặc định: danh sách
    print(f"{len(sel)} bài · {sel.n_words.sum():,} chữ\n")
    for r in sel.itertuples():
        print(f"  {r.track_id:22s} {r.n_words:4d} chữ  {str(r.title or '')[:46]}")
    print(f"\nxem lời một bài:  --id <track_id>")
    print(f"xuất ra file:     --export md")


if __name__ == "__main__":
    main()
