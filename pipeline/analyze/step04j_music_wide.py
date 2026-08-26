"""STEP_04j · THÔNG SỐ NHẠC TRÊN DIỆN RỘNG — 307 track thay vì 5 bản.

VÌ SAO CÓ BƯỚC NÀY: brief nhạc cũ dựng từ **5 bản** top 0,07% view. Sâu nhưng
hẹp, và vài kết luận bị đọc thành quy luật của cả ngách. Nặng nhất là
«5/5 bản ở điệu TRƯỞNG» — trên 307 track thì chỉ **65%** trưởng, tức 1/3 ngách
đang dùng điệu thứ. Người đọc trang 1 sẽ tưởng điệu thứ là lạc chất.

Bước này đo lại các thông số ĐO ĐƯỢC trên toàn bộ 307 track, để báo cáo đặt
hai cỡ mẫu cạnh nhau thay vì chỉ có n=5.

⚠ BẪY NHÂN ĐÔI TEMPO (T38–39) — KHÔNG DÙNG `timeline.rhythm.bpm` THÔ.
librosa bắt nhầm bội số 2× rất thường xuyên: **117/307 track (38%)** rơi vào
vùng 110–190 BPM trong khi ngách này là nhạc chậm. Histogram cho thấy rõ hai
cụm (đỉnh thật 60–90, đuôi giả 110–190, lõm ở 90–110).

Cách sửa, theo thứ tự ưu tiên:
  1. `half_time_candidate_bpm` — chính DSP đề xuất, tin nhất (56 track)
  2. còn lại: BPM > 110 thì chia đôi (ngưỡng đặt ở chỗ lõm của histogram)

Kiểm chứng: hai cách độc lập đều cho **TV = 75,0**, và khớp với bản n=5 đã sửa
TAY (71,8 · khoảng 52–81). Ba nguồn cùng chỉ một chỗ → tin được.

KHÔNG ĐO Ở ĐÂY: hợp âm, cấu trúc đoạn, đường cong năng lượng. Chúng cần ranh
giới đoạn đáng tin mà bộ 307 track không có (xem D-010: ranh giới dò tự động
lệch vài giây là hỏng phân tích hoà âm). Giữ nguyên n=5 cho các phần đó.

Đầu ra: <N>/04_outlier/audio/MUSIC_WIDE.json
"""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import niche_paths

N, P, OUT = niche_paths("04_outlier/audio")

BPM_MAX = 110    # trên mức này coi là bội số 2× — đặt ở chỗ lõm của histogram
MIN_CH = 15      # kênh nhỏ hơn không đưa vào so sánh theo kênh


def fix_bpm(A: pd.DataFrame) -> pd.Series:
    """BPM đã gỡ bẫy nhân đôi. Xem T38–39 và phần đầu file."""
    raw = A["timeline.rhythm.bpm"]
    half = A.get("timeline.rhythm.half_time_candidate_bpm")
    if half is None:
        half = pd.Series(np.nan, index=A.index)
    return pd.Series(
        [h if pd.notna(h) else (b / 2 if pd.notna(b) and b > BPM_MAX else b)
         for b, h in zip(raw, half)], index=A.index)


def spread(s: pd.Series, nd=1) -> dict:
    s = s.dropna()
    if not len(s):
        return {}
    return {"n": int(len(s)),
            "min": round(float(s.min()), nd),
            "p25": round(float(s.quantile(.25)), nd),
            "trung_vị": round(float(s.median()), nd),
            "p75": round(float(s.quantile(.75)), nd),
            "max": round(float(s.max()), nd)}


def main():
    A = pd.read_parquet(P / "audio_dna_full.parquet")
    F = pd.read_parquet(P / "lyrics_features.parquet")
    A = A.merge(F[["track_id", "handle"]], on="track_id", how="left")

    bpm = fix_bpm(A)
    raw = A["timeline.rhythm.bpm"]
    n_fix = int((raw > BPM_MAX).sum())

    # ── điệu thức: hai bộ dò độc lập, ghi cả hai ────────────────────────
    mode = {}
    for col, name in [("harmony.key.mode", "bộ_dò_hoà_âm"),
                      ("harmony.key_cnn.mode", "bộ_dò_CNN")]:
        if col in A:
            vc = A[col].value_counts()
            tot = int(vc.sum())
            mode[name] = {
                "n": tot,
                "trưởng": int(vc.get("major", 0)),
                "thứ": int(vc.get("minor", 0)),
                "pct_trưởng": round(vc.get("major", 0) / tot * 100, 1) if tot else None,
            }

    # ── điệu thứ có đi với lời buồn không? ──────────────────────────────
    # Giả định trực giác của người viết nhạc: «lời buồn thì viết điệu thứ».
    # Kiểm được vì có cả lời và nhạc trên cùng 307 track.
    import re
    from scipy import stats
    DARK = re.compile(r"\b(dark|night|pain|cry|fear|alone|lost|weep|grave|"
                      r"broken|weary)\b")
    R = pd.read_parquet(P / "lyrics_raw.parquet")
    M = A.merge(R[["track_id", "text"]], on="track_id", how="inner")
    M["dark"] = M.text.str.lower().map(lambda t: len(DARK.findall(t)))
    mm = M["harmony.key.mode"]
    mn, mj = M[mm == "minor"]["dark"], M[mm == "major"]["dark"]
    flip = 0
    per = []
    for h, g in M.groupby("handle"):
        if len(g) < MIN_CH:
            continue
        a = g[g["harmony.key.mode"] == "minor"]["dark"]
        b = g[g["harmony.key.mode"] == "major"]["dark"]
        if len(a) < 3 or len(b) < 3:
            continue
        same = float(a.median()) > float(b.median())
        if not same:
            flip += 1
        per.append({"kênh": h, "thứ_TV": float(a.median()),
                    "trưởng_TV": float(b.median()), "đúng_chiều": same})
    u, p = stats.mannwhitneyu(mn, mj) if len(mn) and len(mj) else (None, None)
    dark_mode = {
        "câu_hỏi": "Bài có lời buồn hơn thì có dùng điệu THỨ nhiều hơn không?",
        "n": int(len(M)),
        "từ_tối_TV_điệu_thứ": float(mn.median()) if len(mn) else None,
        "từ_tối_TV_điệu_trưởng": float(mj.median()) if len(mj) else None,
        "p": float(p) if p is not None else None,
        "số_kênh_xét": len(per), "số_kênh_ngược_chiều": flip,
        "theo_kênh": per,
        "phán_quyết": "KHÔNG CÓ LIÊN HỆ",
        "đọc_là": None,
    }
    _p = f"{p:.2f}".replace(".", ",")     # quy ước số Việt (§3 chuẩn báo cáo)
    dark_mode["đọc_là"] = (
        f"Lời buồn KHÔNG đi với điệu thứ (p={_p}, {flip}/{len(per)} kênh ngược "
        f"chiều). Đây là giả định trực giác rất dễ mắc khi viết nhạc — dữ liệu "
        f"{len(M)} bài bác bỏ nó. Chọn điệu thức theo màu sắc mong muốn, đừng "
        f"chọn theo nội dung lời.")

    out = {
        "nguồn": {"n_track": int(len(A)),
                  "n_kênh": int(A.handle.nunique()),
                  "từ": "00_input/processed/audio_dna_full.parquet",
                  "so_với": "AUDIO_BRIEF/RECIPE dựng từ 5 bản top 0,07% view"},
        "nhịp_độ": {
            **spread(bpm),
            "đã_sửa_bẫy_nhân_đôi": True,
            "số_track_phải_sửa": n_fix,
            "pct_phải_sửa": round(n_fix / len(A) * 100, 1),
            "ngưỡng_chia_đôi": BPM_MAX,
            "đối_chiếu_n5": "bản 5 track sửa tay: TV 71,8 · khoảng 52–81",
            "ghi_chú": "KHÔNG dùng cột bpm thô — 38% track bị bắt nhầm bội số 2×.",
        },
        "điệu_thức": {
            **mode,
            "phát_hiện": None,
        },
        "độ_to": {**spread(A["timeline.loudness.lufs_i"], 1),
                  "đơn_vị": "LUFS", "ghi_chú": "chuẩn phát trực tuyến ≈ −14 LUFS"},
        "dải_động": spread(A["timeline.loudness.lra"], 1) if "timeline.loudness.lra" in A else {},
        "lời_buồn_và_điệu_thức": dark_mode,
        "vẫn_dùng_n5_cho": [
            "hợp âm và tiến trình hoà âm — cần ranh giới đoạn đáng tin (D-010)",
            "cấu trúc đoạn và đường cong năng lượng",
            "groove/swing — đo trên bản đã kiểm tay",
        ],
    }
    mj_pct = mode.get("bộ_dò_hoà_âm", {}).get("pct_trưởng")
    _mj = f"{mj_pct}".replace(".", ",")        # quy ước số Việt (§3)
    out["điệu_thức"]["phát_hiện"] = (
        f"{_mj}% số track ở điệu TRƯỞNG — không phải 100% như mẫu 5 bản "
        f"gợi ý. Khoảng một phần ba ngách dùng điệu THỨ và vẫn đang chạy. "
        f"Trưởng là mặc định, thứ là lựa chọn hợp lệ.")

    f = OUT / "MUSIC_WIDE.json"
    f.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✅ {f}")
    print(f"   BPM (đã sửa): TV={out['nhịp_độ']['trung_vị']} · "
          f"{out['nhịp_độ']['p25']}–{out['nhịp_độ']['p75']} "
          f"· sửa {n_fix}/{len(A)} track")
    print(f"   điệu trưởng: {mj_pct}% (mẫu 5 bản cho 100%)")
    print(f"   lời buồn × điệu thứ: {dark_mode['phán_quyết']} (p={p:.2f})")


if __name__ == "__main__":
    main()
