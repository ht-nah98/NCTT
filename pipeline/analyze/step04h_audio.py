"""STEP_04h — BRIEF ÂM NHẠC: nhóm dẫn đầu dựng nhạc thế nào?

CHẠY: python3 pipeline/analyze/step04h_audio.py [niche_path]
ĐỌC : 00_input/processed/audio_features.parquet + audio_sections.parquet
GHI : 04_outlier/audio/AUDIO_BRIEF.json  ·  _audio_data.json  ·  _metrics_raw.json

═══════════════════════════════════════════════════════════════════
TẦNG MÔ TẢ, KHÔNG PHẢI TẦNG KIỂM ĐỊNH
═══════════════════════════════════════════════════════════════════
Với n=5 **không thể** kiểm định "đặc điểm âm nhạc nào GÂY RA thành công" —
không có nhóm đối chứng, mẫu quá nhỏ. Đừng thử; sẽ ra kết luận giả.

Câu hỏi đúng, giống STEP_04g (brief ảnh):
    "Năm bản nhạc top 0,07% đang được dựng NHƯ THẾ NÀO?"
→ trả lời được chính xác, và tái tạo được.

Xem 00_system/01_ARCHITECTURE.md §2.4.
"""
import sys, json, warnings
import pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import niche_paths                                   # noqa: E402
warnings.filterwarnings("ignore")

N, P, OUT = niche_paths("04_outlier/audio")
FA, FS = P/"audio_features.parquet", P/"audio_sections.parquet"
if not FA.exists():
    sys.exit(f"Thiếu {FA} — chạy pipeline/extract/normalize_audio.py trước.")

F = pd.read_parquet(FA)
S = pd.read_parquet(FS)

# Gắn view/like để biết đây có thật là nhóm dẫn đầu không
V = pd.read_parquet(P/"videos_enriched.parquet")
F = F.merge(V[["video_id", "title", "view_count", "like_count", "duration_sec"]]
            .rename(columns={"duration_sec": "dur_meta"}),
            on="video_id", how="left")

R = {}
n = len(F)


def rng(col, nd=1):
    """Khoảng [nhỏ nhất – lớn nhất] + trung vị. Với n=5, KHOẢNG trung thực hơn
    trung bình — trung bình giấu mất độ phân tán."""
    s = F[col].dropna()
    if s.empty: return None
    return {"min": round(float(s.min()), nd), "median": round(float(s.median()), nd),
            "max": round(float(s.max()), nd)}


# ── 1. NHỊP ĐỘ ──────────────────────────────────────────────────────
R["tempo"] = {
    "bpm": rng("bpm"),
    "bpm_raw_before_fix": rng("bpm_raw"),
    "n_corrected": int(F.bpm_halved.sum()),
    "ghi_chú": ("librosa bắt nhầm bội số 2× của tempo. Đã chia đôi sau khi "
                "đối chiếu nhịp hòa âm + mật độ onset. Xem normalize_audio.py"),
    "khuyến_nghị": "Đặt BPM trong khoảng dưới đây khi sinh nhạc",
}

# ── 2. ĐIỆU THỨC ────────────────────────────────────────────────────
mode_ct = F["mode"].value_counts().to_dict()
R["key"] = {
    "mode_distribution": {k: int(v) for k, v in mode_ct.items()},
    "tonic_list": sorted(F.tonic.dropna().unique().tolist()),
    "key_confidence": rng("key_conf", 2),
    "phát_hiện": (f"{mode_ct.get('major',0)}/{n} bản ở điệu TRƯỞNG — "
                  "trái với trực giác «blues phải buồn nên dùng thứ»"),
}

# ── 3. HÒA ÂM ───────────────────────────────────────────────────────
R["harmony"] = {
    "distinct_chords": rng("distinct_chords", 0),
    "sec_per_chord": rng("sec_per_chord"),
    "chord_palette_pct": {"min": rng("pct_min"), "maj": rng("pct_maj"),
                          "dim": rng("pct_dim")},
    "chord_confidence": rng("chord_conf", 2),
    # ⚠ KHÔNG khái quát hóa ở đây. Tỷ lệ hợp âm thứ trải từ 7,6% đến 91,9%
    #   — chỉ 2/5 bản thiên về thứ. Nói "hợp âm thứ chiếm đa số" là SAI với
    #   3 bản còn lại. Với n=5, hãy báo cáo ĐỘ PHÂN TÁN, đừng ép ra quy luật.
    "phát_hiện": (f"Bảng màu hợp âm RẤT KHÁC NHAU: thứ chiếm từ "
                  f"{F.pct_min.min():.1f}% đến {F.pct_min.max():.1f}%. "
                  f"{int((F.pct_min > 50).sum())}/{n} bản thiên về hợp âm thứ. "
                  "Không có một bảng màu chuẩn — đây là chỗ để chọn phong cách."),
}

# ── 4. GROOVE ───────────────────────────────────────────────────────
sw = F[F.swing_pct > 5]
R["groove"] = {
    "swing_pct": rng("swing_pct"),
    "n_swing": int(len(sw)), "n_straight": int(n - len(sw)),
    "syncopation": rng("syncopation", 3),
    "onsets_per_sec": rng("onsets_per_sec", 2),
    "pulse_feel": F.pulse_feel.value_counts().to_dict(),
    "phát_hiện": (f"{len(sw)}/{n} bản có swing rõ (>5%); "
                  f"{n-len(sw)}/{n} chơi thẳng. Cả hai đều thắng — "
                  "không có công thức duy nhất."),
}

# ── 5. CẤU TRÚC ─────────────────────────────────────────────────────
sec_stats = S.groupby("video_id").agg(n_sec=("index", "count"),
                                      med_dur=("dur_sec", "median"),
                                      med_energy=("energy_pct", "median")).reset_index()
R["structure"] = {
    "n_sections": {"min": int(sec_stats.n_sec.min()),
                   "median": float(sec_stats.n_sec.median()),
                   "max": int(sec_stats.n_sec.max())},
    "section_dur_sec": {"min": round(float(S.dur_sec.min()), 1),
                        "median": round(float(S.dur_sec.median()), 1),
                        "max": round(float(S.dur_sec.max()), 1)},
    "energy_pct": {"min": int(S.energy_pct.min()), "median": float(S.energy_pct.median()),
                   "max": int(S.energy_pct.max())},
    "ghi_chú": ("Đoạn được ĐÁNH SỐ, không đặt tên Verse/Chorus — "
                "tín hiệu DSP không mang thông tin đó. Đừng bịa nhãn."),
}

# Đường cong năng lượng: nhạc dài có "lên đỉnh" hay giữ đều?
curves = {}
for vid, gdf in S.groupby("video_id"):
    g = gdf.sort_values("index")
    e = g.energy_pct.tolist()
    if len(e) >= 3:
        first, mid, last = e[0], e[len(e)//2], e[-1]
        shape = ("giữ đều" if max(e)-min(e) <= 20 else
                 "lên đỉnh giữa" if mid >= max(first, last) else
                 "tăng dần" if last > first else "giảm dần")
    else:
        shape = "quá ít đoạn"
    curves[vid] = {"shape": shape, "energy_seq": e,
                   "range": [int(min(e)), int(max(e))] if e else None}
shape_ct = {}
for c in curves.values():
    shape_ct[c["shape"]] = shape_ct.get(c["shape"], 0) + 1
R["energy_curve"] = {
    "per_track": curves,
    "shape_distribution": shape_ct,
    "phát_hiện": (f"{len(shape_ct)} kiểu đường cong khác nhau trên {n} bản — "
                  "KHÔNG có dạng chuẩn. Đừng ép nhạc theo một khuôn dựng sẵn."),
}

# ── 6. HAI MÔ HÌNH THEO ĐỘ DÀI ──────────────────────────────────────
# Giống STEP_10: ngách này có hai chiến lược đối lập, nhạc cũng khác nhau.
F["model"] = F.dur_meta.apply(lambda d: "ngắn (<15p)" if (d or 0) < 900 else "dài (≥15p)")
by_model = []
for mdl, g in F.groupby("model"):
    by_model.append({
        "model": mdl, "n": int(len(g)),
        "bpm_median": round(float(g.bpm.median()), 1),
        "sec_per_chord_median": round(float(g.sec_per_chord.median()), 1),
        "distinct_chords_median": float(g.distinct_chords.median()),
        "n_sections_median": float(g.n_sections.median()),
        "view_median": int(g.view_count.median()),
    })
R["by_model"] = by_model

# ── 7. BẢNG TỪNG BẢN (truy vết) ─────────────────────────────────────
R["tracks"] = [{
    "video_id": r.video_id, "title": r.title,
    "view_count": int(r.view_count) if pd.notna(r.view_count) else None,
    "duration_sec": float(r.dur_meta) if pd.notna(r.dur_meta) else None,
    "bpm": r.bpm, "bpm_raw": r.bpm_raw,
    "key": f"{r.tonic} {r['mode']}", "key_conf": r.key_conf,
    "swing_pct": r.swing_pct, "syncopation": r.syncopation,
    "distinct_chords": int(r.distinct_chords), "sec_per_chord": r.sec_per_chord,
    "pct_min": r.pct_min, "pct_maj": r.pct_maj,
    "n_sections": int(r.n_sections),
    "energy_shape": curves.get(r.video_id, {}).get("shape"),
} for _, r in F.sort_values("view_count", ascending=False).iterrows()]

# ── 8. CÔNG THỨC TÁI TẠO — đầu vào cho workflow sinh nhạc ───────────
# Đây là mục tiêu cuối: máy đọc được, nạp thẳng vào Suno/Udio/prompt.
bpm_r, spc = R["tempo"]["bpm"], R["harmony"]["sec_per_chord"]
R["recipe"] = {
    "cách_dùng": "Nạp vào công cụ sinh nhạc, hoặc dịch thành prompt tiếng Anh",
    "tempo_bpm": {"range": [bpm_r["min"], bpm_r["max"]], "target": bpm_r["median"]},
    "mode": "major" if mode_ct.get("major", 0) >= n/2 else "minor",
    "mode_ghi_chú": f"{mode_ct.get('major',0)}/{n} bản ở điệu trưởng — "
                    "giai điệu sáng, màu tối đến từ hợp âm thứ xen vào, không từ điệu thức",
    "harmonic_rhythm_sec": {"range": [spc["min"], spc["max"]], "target": spc["median"]},
    "chord_vocabulary": {"range": [R["harmony"]["distinct_chords"]["min"],
                                   R["harmony"]["distinct_chords"]["max"]],
                         "ghi_chú": "bản ngắn ~9-13 hợp âm, bản dài ~24-25"},
    "groove": {"swing": "cả hai đều dùng được",
               "swing_pct_when_used": [float(sw.swing_pct.min()), float(sw.swing_pct.max())]
                                      if len(sw) else None,
               "syncopation": [R["groove"]["syncopation"]["min"],
                               R["groove"]["syncopation"]["max"]],
               "ghi_chú": "syncopation thấp (<0,2) — nhịp đơn giản, không giật"},
    "section_dur_sec": {"target": R["structure"]["section_dur_sec"]["median"],
                        "range": [R["structure"]["section_dur_sec"]["min"],
                                  R["structure"]["section_dur_sec"]["max"]],
                        "ghi_chú": f"đổi không khí mỗi ~"
                                   f"{R['structure']['section_dur_sec']['median']:.0f} giây"},
    "prompt_en": (
        f"slow gospel blues, {int(bpm_r['min'])}-{int(bpm_r['max'])} BPM, "
        f"major key with frequent minor-chord colouring, "
        f"chord changes every {spc['min']:.0f}-{spc['max']:.0f} seconds, "
        f"low syncopation, warm analog production, "
        f"soulful lead vocal, hammond organ and clean electric guitar, "
        f"reverent and consoling mood"),
    "vocal": "CÓ LỜI — bắt buộc. Xem khối vocal_decision (bằng chứng 3 lớp).",
    "prompt_ghi_chú": ("«có lời» là kết luận CÓ BẰNG CHỨNG (vocal_decision). "
                       "Nhưng LOẠI giọng và nhạc cụ cụ thể trong prompt là GỢI Ý "
                       "theo thể loại, KHÔNG đo được từ dữ liệu hiện có — xem limits."),
}

# ── 8b. CÓ LỜI HAY KHÔNG LỜI — câu hỏi sản xuất đầu tiên ────────────
# Câu này KHÔNG trả lời được từ 5 file DSP (chúng không tách được giọng hát).
# Nhưng ngách ĐÃ có câu trả lời, nằm rải ở STEP_05 và STEP_06 — gom về đây
# vì đây là nơi người ta hỏi (bài học T42).
#
# Đây là một trong RẤT ÍT kết luận đứng vững cả 3 lớp chống Simpson.
_vocal = {"kết_luận": "CÓ LỜI", "độ_tin_cậy": "Cao",
          "vì_sao_ở_đây": "5 file DSP không tách được giọng hát; bằng chứng đến từ "
                          "STEP_06 (hiệu quả) và STEP_05 (bối cảnh nghe)"}
try:
    _TH = pd.read_csv(N/"06_keyword/02_theme_scores.csv")
    _i = _TH[_TH.theme == "instrumental"]
    if len(_i):
        _i = _i.iloc[0]
        _vocal["bằng_chứng_hiệu_quả"] = {
            "chủ_đề": "instrumental / no lyrics / background",
            "lift_toàn_thị_trường": round(float(_i.lift), 3),
            "xếp_hạng": f"thấp nhất trong {len(_TH)} chủ đề",
            "p": float(_i.p),
            "trong_từng_kênh": round(float(_i.within_median_lift), 3),
            "số_kênh_tốt_hơn": f"{int(_i.n_ch_better)}/{int(_i.n_ch_tested)}",
            "phán_quyết": str(_i.verdict),
            "nguồn": "06_keyword/02_theme_scores.csv",
            "đọc_là": (f"Video gắn nhãn không lời đạt VPD bằng "
                       f"{float(_i.lift)*100:.0f}% video còn lại — "
                       "và vẫn kém khi so TRONG CÙNG một kênh, nên không phải "
                       "hiệu ứng kênh yếu (đã qua kiểm 3 lớp, bẫy L2)"),
        }
except Exception as e:
    _vocal["bằng_chứng_hiệu_quả"] = {"lỗi": str(e)}

try:
    _A5 = json.load(open(N/"05_audience/_metrics_raw.json"))
    _c = _A5.get("context", {})
    _act = sum(_c.get(k, {}).get("pct", 0) for k in ("prayer_devo", "morning", "sick_hosp", "grief"))
    _bg = sum(_c.get(k, {}).get("pct", 0) for k in ("sleep_night", "driving", "housework", "work"))
    _vocal["bằng_chứng_bối_cảnh"] = {
        "nghe_chủ_động_pct": round(_act, 2),
        "nghe_nền_pct": round(_bg, 2),
        "tỷ_lệ": round(_act/_bg, 1) if _bg else None,
        "nguồn": "05_audience/_metrics_raw.json → context",
        "đọc_là": (f"Bối cảnh nghe CHỦ ĐỘNG (cầu nguyện, sáng sớm, bệnh tật, tang chế) "
                   f"chiếm {_act:.1f}%; bối cảnh NHẠC NỀN (ngủ, lái xe, việc nhà, làm việc) "
                   f"chỉ {_bg:.1f}%. Nhạc không lời phục vụ nhóm nhỏ hơn ~{_act/_bg:.0f} lần."
                   if _bg else ""),
    }
except Exception as e:
    _vocal["bằng_chứng_bối_cảnh"] = {"lỗi": str(e)}

_vocal["bằng_chứng_định_tính"] = {
    "comment_được_thích_nhất_ngách": 1444,
    "nội_dung": "Finally something for those of us who love the music but "
                "can't stand the lyrics of the blues",
    "đọc_là": "Nỗi đau lõi của ngách nằm ở LỜI HÁT — không phải ở phần nhạc. "
              "Bỏ lời là bỏ đúng thứ khiến khán giả tìm đến.",
    "nguồn": "05_audience/03_quote_bank.csv",
}
_vocal["ngoại_lệ"] = ("Nếu nhắm riêng nhóm nghe lúc ngủ/thiền (~1,4% comment) thì "
                      "không lời hợp lý — nhưng đó là ngách con rất nhỏ, và đang "
                      "cạnh tranh với toàn bộ thị trường 'sleep music' ngoài ngách này.")
R["vocal_decision"] = _vocal

# ── 9. GIỚI HẠN — nói thẳng, đừng để người đọc tự đoán ──────────────
R["limits"] = [
    {"thiếu": "Nhóm đối chứng",
     "hệ_quả": "KHÔNG kết luận được đặc điểm nào GÂY RA thành công. "
               "Đây là MÔ TẢ nhóm thắng, không phải bằng chứng nhân quả.",
     "khắc_phục": "Phân tích thêm ~30 bản nhóm thua (B4) rồi so sánh"},
    {"thiếu": f"Cỡ mẫu (n={n})",
     "hệ_quả": "Mọi con số là KHOẢNG quan sát được, không phải chuẩn ngành.",
     "khắc_phục": "Chạy DSP cho ≥30 bản top"},
    {"thiếu": "Nhạc cụ / âm sắc / giọng hát",
     "hệ_quả": "Không biết dùng guitar gì, giọng nam hay nữ, có organ không — "
               "những thứ quyết định 'nghe giống hay không'.",
     "khắc_phục": "Cần tách stem (Demucs) + phân loại nhạc cụ"},
    {"thiếu": "Lời bài hát",
     "hệ_quả": "Không biết nội dung hát gì.",
     "khắc_phục": "Whisper transcribe"},
    {"thiếu": "Chất lượng thu / master (LUFS, dải động)",
     "hệ_quả": "Không biết chuẩn âm lượng thị trường.",
     "khắc_phục": "Đo LUFS bằng pyloudnorm trên file gốc"},
]

R["generated_from"] = {"n_tracks": n, "n_sections": int(len(S)),
                       "view_min": int(F.view_count.min()),
                       "view_max": int(F.view_count.max()),
                       "percentile": "top 0,07% lượt xem của ngách"}

json.dump(R, open(OUT/"AUDIO_BRIEF.json", "w"), ensure_ascii=False, indent=2)
json.dump(R, open(OUT/"_audio_data.json", "w"), ensure_ascii=False, indent=2)

# metrics cho collect_metrics
json.dump({"A1_n_tracks": n,
           "A2_bpm_median": float(F.bpm.median()),
           "A3_major_ratio": round(mode_ct.get("major", 0)/n, 3),
           "A4_swing_ratio": round(len(sw)/n, 3),
           "A5_sec_per_chord_median": float(F.sec_per_chord.median()),
           "_meta": {"tầng": "MÔ TẢ (không kiểm định)",
                     "nguồn": "00_input/raw/audio/*.yaml (librosa DSP)",
                     "cảnh_báo": "n=5, không có nhóm đối chứng"}},
          open(OUT/"_metrics_raw.json", "w"), ensure_ascii=False, indent=2)

print(f"STEP_04h · BRIEF ÂM NHẠC · {n} bản top 0,07%")
print(f"  BPM        {R['tempo']['bpm']['min']}–{R['tempo']['bpm']['max']} "
      f"(trung vị {R['tempo']['bpm']['median']})   ← đã sửa bẫy nhân đôi")
print(f"  Điệu thức  {mode_ct.get('major',0)}/{n} TRƯỞNG")
print(f"  Hợp âm     đổi mỗi {R['harmony']['sec_per_chord']['min']}–"
      f"{R['harmony']['sec_per_chord']['max']}s")
print(f"  Groove     {len(sw)}/{n} swing · {n-len(sw)}/{n} thẳng")
print(f"  → {OUT/'AUDIO_BRIEF.json'}")
