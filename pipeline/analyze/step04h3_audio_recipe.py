"""STEP_04h3 · CÔNG THỨC TÁI TẠO NHẠC — nhóm thắng dựng nhạc theo thông số nào?

MỤC TIÊU: TÁI TẠO, không so sánh. Câu hỏi là *"dựng lại nhạc giống video
thắng thì đặt thông số gì"* — KHÔNG phải *"thông số nào phân biệt thắng/thua"*.

VÌ SAO KHÁC 04h2: 04h2 đi tìm yếu tố phân biệt (cần nhóm đối chứng, cần
p-value, và với mẫu toàn kênh-đang-thắng thì độ lớn tác dụng chỉ ~4% → không
dùng cho sản xuất được). Bước này bỏ hẳn câu hỏi đó. Đã biết nhóm thắng là ai
thì chỉ cần ĐO xem họ làm gì, rồi chép lại.

=> Không dùng p-value. Dùng KHOẢNG (p25–p75) và ĐỘ TẬP TRUNG.

ĐỘ TẬP TRUNG là thứ quyết định giá trị của mỗi thông số:
  CHẶT (IQR/trung vị < 0,15) → cả nhóm thắng làm giống nhau → BẮT BUỘC theo
  vừa  (< 0,40)              → có xu hướng chung → nên theo
  rộng (≥ 0,40)              → mỗi bản một kiểu → TỰ DO, đừng ép

Thông số "rộng" KHÔNG phải dữ liệu kém — nó là phát hiện: nhóm thắng không
thống nhất ở đó, nên ép theo một con số là bịa ra ràng buộc không có thật.

Đầu ra: <N>/04_outlier/audio/AUDIO_RECIPE.json
"""
import json, re, sys
import numpy as np
import pandas as pd

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
from _common import niche_paths

N, P, OUT = niche_paths("04_outlier/audio")

# Ngưỡng lọt nhóm thắng. Tuyệt đối, KHÔNG so trong kênh: mục tiêu là tái tạo
# bản thắng của cả ngách, không phải bản khá nhất của một kênh yếu.
WIN_VIEWS = 500_000
MIN_TRACKS = 20

NUM = ["bpm", "lufs", "plr_db", "lra", "stereo_width", "stem_vocals", "stem_bass",
       "stem_drums", "stem_guitar", "stem_piano", "swing_phase", "dao_phach",
       "four_on_floor", "tempo_cv", "hop_am_moi_o_nhip", "so_hop_am_rieng",
       "quang_semitone", "buoc_lien", "not_moi_giay", "vibrato_hz", "hnr_db",
       "jitter", "lech_cent", "bam_luoi_semitone", "phut", "do_tre_ms"]
CAT = ["truong_thu", "nhip", "quang_giong", "ho_the_loai", "the_loai_chinh",
       "nhip_nhap_nhang", "tong"]

# Nhóm thông số theo KHÂU SẢN XUẤT — người dựng nhạc đọc theo khâu, không
# đọc theo tên cột. Thứ tự này là thứ tự làm việc thật trong phòng thu.
STAGE = {
    "1_sang_tac": ["bpm", "nhip", "truong_thu", "tong", "so_hop_am_rieng",
                   "hop_am_moi_o_nhip", "phut"],
    "2_giai_dieu": ["buoc_lien", "not_moi_giay", "quang_semitone"],
    "3_groove": ["swing_phase", "dao_phach", "four_on_floor", "tempo_cv",
                 "do_tre_ms", "nhip_nhap_nhang"],
    "4_phoi_khi": ["stem_vocals", "stem_bass", "stem_drums", "stem_guitar",
                   "stem_piano"],
    "5_giong_hat": ["quang_giong", "vibrato_hz", "hnr_db", "jitter",
                    "lech_cent", "bam_luoi_semitone"],
    "6_mix_master": ["lufs", "plr_db", "lra", "stereo_width"],
}


# Trường CHẨN ĐOÁN của công cụ đo, KHÔNG phải tham số sản xuất. Nhạc sĩ không
# "đặt" độ tin cậy của bộ dò tông hay số ô nhịp — chúng mô tả phép đo, không
# mô tả bản nhạc. Để lọt vào brief thì brief bảo người dựng chỉnh một con số
# vô nghĩa. Bắt được 2 trường như vậy lọt thẳng vào nhóm BẮT BUỘC (T66).
DIAGNOSTIC = re.compile(
    r"confidence|coverage|__len|check|passed|agrees|insufficient"
    r"|unknown_ratio|ambiguous|dropped|reconstruction|entropy"
    r"|\bn_(beats|bars|notes|chords)\b|raw_|_cv$", re.I)


def is_production_param(col: str) -> bool:
    """Chỉ giữ trường mà người dựng nhạc THAY ĐỔI ĐƯỢC."""
    return not DIAGNOSTIC.search(col)


def tightness(p25, med, p75):
    """CHẶT/vừa/rộng — quyết định thông số là ràng buộc hay tự do."""
    if med == 0 or not np.isfinite(med):
        return "rộng", None
    rel = (p75 - p25) / abs(med)
    return ("CHẶT" if rel < 0.15 else "vừa" if rel < 0.40 else "rộng"), round(float(rel), 3)


def main():
    # Ưu tiên bản ĐẦY ĐỦ (594 trường). Bản gọn 45 cột chỉ là dự phòng —
    # giai điệu/hoà âm/stem ở đó gần như trống, không đủ dựng công thức.
    full = P / "audio_dna_full.parquet"
    src = full if full.exists() else P / "audio_dna.parquet"
    if not src.exists():
        print("⏭  Bỏ qua 04h3: chưa có", src)
        return
    T = pd.read_parquet(src)
    USING_FULL = src == full
    vm = pd.read_parquet(P / "video_master.parquet")
    j = T.merge(vm[["video_id", "view_count", "channel_handle"]], on="video_id")
    if j.empty:
        print("⏭  Bỏ qua 04h3: không nối được với video_master")
        return

    vid = j.groupby("video_id").view_count.first()
    win = vid[vid >= WIN_VIEWS].index
    W = j[j.video_id.isin(win)].copy()
    if len(W) < MIN_TRACKS:
        # hạ ngưỡng về p75 thay vì bỏ cuộc — ngách nhỏ vẫn phải có công thức
        cut = float(vid.quantile(0.75))
        win = vid[vid >= cut].index
        W = j[j.video_id.isin(win)].copy()
        used = cut
    else:
        used = float(WIN_VIEWS)

    # Bản đầy đủ: lấy MỌI trường số dùng được, không chỉ 26 trường tay.
    # Lọc: ≥80% track có dữ liệu và >3 giá trị khác nhau — cột gần như hằng
    # số không ràng buộc được quyết định sản xuất nào.
    num_cols = list(NUM)
    if USING_FULL:
        cand = W.select_dtypes("number").columns
        auto = [c for c in cand
                if is_production_param(c)
                and W[c].notna().mean() >= 0.8 and W[c].nunique() > 3
                and c not in ("view_count",)]
        num_cols = sorted(set(num_cols) | set(auto))

    for c in num_cols:
        if c in W:
            W[c] = pd.to_numeric(W[c], errors="coerce")

    spec, free, must = {}, [], []
    for c in num_cols:
        if c not in W:
            continue
        d = W[c].dropna()
        if len(d) < MIN_TRACKS:
            continue
        p25, med, p75 = (float(d.quantile(.25)), float(d.median()), float(d.quantile(.75)))
        tag, rel = tightness(p25, med, p75)
        spec[c] = {"p25": round(p25, 3), "median": round(med, 3), "p75": round(p75, 3),
                   "min": round(float(d.min()), 3), "max": round(float(d.max()), 3),
                   "n": int(len(d)), "tightness": tag, "iqr_over_median": rel}
        (must if tag == "CHẶT" else free if tag == "rộng" else []).append(c)

    cats = {}
    for c in CAT:
        if c not in W:
            continue
        vc = W[c].value_counts(normalize=True)
        if vc.empty:
            continue
        top = vc.index[0]
        cats[c] = {"dominant": str(top), "share_pct": round(float(vc.iloc[0]) * 100, 1),
                   "distribution": {str(k): round(float(v) * 100, 1)
                                    for k, v in vc.head(5).items()},
                   # >=60% = quy ước rõ; <60% = nhóm thắng không thống nhất
                   "is_convention": bool(vc.iloc[0] >= 0.60)}

    res = {
        "niche": N.name,
        "goal": "TÁI TẠO — dựng lại nhạc giống nhóm video thắng",
        "cohort": {
            "view_threshold": used,
            "n_videos": int(len(win)),
            "n_tracks": int(len(W)),
            "n_channels": int(W.channel_handle.nunique()),
            "view_min": int(vid[win].min()), "view_max": int(vid[win].max()),
        },
        "by_stage": {k: [c for c in v if c in spec or c in cats]
                     for k, v in STAGE.items()},
        "source": src.name,
        "n_fields": len(spec),
        "n_diagnostic_excluded": int(sum(
            1 for c in W.select_dtypes("number").columns
            if not is_production_param(c))) if USING_FULL else 0,
        "spec": spec,
        "categorical": cats,
        "must_follow": must,      # CHẶT — cả nhóm thắng làm giống nhau
        "free_choice": free,      # rộng — nhóm thắng không thống nhất
        "_meta": {
            "method": "phân vị của nhóm thắng; KHÔNG kiểm định giả thuyết",
            "why_no_pvalue": "mục tiêu là tái tạo, không phải so sánh thắng/thua",
            "tightness_rule": "CHẶT <0,15 · vừa <0,40 · rộng ≥0,40 (IQR/trung vị)",
            "limits": [
                f"{len(W)} track nhưng chỉ {len(win)} video / "
                f"{W.channel_handle.nunique()} kênh — khoảng có thể hẹp hơn thực tế",
                "công thức MÔ TẢ nhóm thắng, không đảm bảo làm theo sẽ thắng",
                "cột prompt Suno bị loại: dữ liệu thô sai (người dùng xác nhận)",
            ],
        },
    }
    (OUT / "AUDIO_RECIPE.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ {OUT/'AUDIO_RECIPE.json'}  (nguồn: {src.name}, {len(spec)} thông số)")
    print(f"   nhóm thắng: {len(W)} track / {len(win)} video / "
          f"{W.channel_handle.nunique()} kênh (≥{used:,.0f} view)")
    print(f"   BẮT BUỘC theo ({len(must)}): {', '.join(must)}")
    print(f"   TỰ DO ({len(free)}): {', '.join(free[:6])}"
          + (" …" if len(free) > 6 else ""))


if __name__ == "__main__":
    main()
