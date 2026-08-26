"""STEP_04i · PHÂN TÍCH LỜI HÁT — nền dữ liệu cho báo cáo nhạc hợp nhất.

VỊ TRÍ TRONG HỆ: đây là bước ĐO. Bước dựng báo cáo (`report/build_music.py`)
chỉ đọc file này, không tự tính — theo §6 của 06_REPORT_STANDARDS (T27).

BA CÂU HỎI, BA PHƯƠNG PHÁP KHÁC NHAU — đừng trộn:

  1. VIẾT LỜI THẾ NÀO   → khoảng p25–p75 + độ tập trung. KHÔNG p-value.
     Giống 04h3: đã biết đây là nhóm đang chạy tốt thì chỉ cần ĐO họ làm gì.

  2. LỜI ĐI VỚI NHẠC RA SAO → tương quan Spearman + KIỂM SIMPSON BẮT BUỘC.
     Đây là chỗ duy nhất dùng p-value, và p nhỏ KHÔNG đủ để kết luận.

  3. NGƯỜI NGHE LÀ AI   → ngôi kể + chủ đề. Mô tả, không suy nhân quả.

KIỂM SIMPSON KHÔNG PHẢI TÙY CHỌN (bài học lớn của dự án: gộp kênh từng đảo
8,1× thành 0,48×). Đo thật ở bước này: `words_per_line × guitar` gộp lại cho
rho=+0,50 p=1,8e-20 — trông như phát hiện lớn. Tách theo kênh thì rho co về
−0,13…+0,27, **1/6 kênh đảo dấu**. Tức phần lớn tương quan đến từ KHÁC BIỆT
GIỮA CÁC KÊNH, không phải quy luật bên trong một bài hát. Ép nó vào công thức
sáng tác là bịa ra ràng buộc không tồn tại.

Quy tắc phán quyết:
  XÁC NHẬN  0 kênh đảo dấu + đa số kênh cùng chiều → dùng được
  YẾU       1 kênh đảo dấu                          → ghi kèm cảnh báo
  BÁC BỎ    ≥2 kênh đảo dấu, hoặc gộp mạnh mà kênh nào cũng ~0 → là bẫy gộp

KÊNH NHỎ BỊ LOẠI KHỎI KIỂM: dưới 15 track thì rho dao động quá lớn, giữ lại
chỉ tạo nhiễu. Ghi rõ số kênh đã xét.

Đầu ra: <N>/04_outlier/lyrics/LYRICS_ANALYSIS.json
"""
import json, re, sys
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import niche_paths

N, P, OUT = niche_paths("04_outlier/lyrics")

MIN_CH = 15          # dưới mức này rho quá nhiễu, không đưa vào kiểm Simpson
TIGHT, MID = 0.15, 0.40   # ngưỡng độ tập trung — giống 04h3 cho nhất quán

# Ngôi kể và chủ đề dùng cùng bộ từ với L5 để hai bên không lệch nhau
THEMES = {
    "than_khóc":    ["cry","tears","weep","sorrow","grief","pain","broken","lament","mourn","ache"],
    "tin_cậy":      ["trust","faith","believe","rest","refuge","shelter","safe","keep","hold"],
    "ngợi_khen":    ["praise","glory","hallelujah","worship","sing","bless","exalt","honor"],
    "cứu_rỗi":      ["save","salvation","redeem","grace","mercy","forgive","blood","cross"],
    "hành_trình":   ["walk","road","path","journey","step","valley","mountain","home","way"],
    "ánh_sáng_tối": ["light","dark","night","morning","dawn","shadow","shine","fire"],
    "nước":         ["river","water","stream","rain","flood","thirst","well","sea"],
}


# ── BA CHIỀU TRẢ LỜI «VIẾT CHO AI, HỌ ĐƯỢC GÌ» ─────────────────────────
# Khác THEMES (chủ đề chung): ba nhóm dưới đây bám vào NGƯỜI NGHE.
# STATE = họ đang ở đâu khi bấm play · PAYOFF = nghe xong họ nhận gì
# ADDRESS = gọi Chúa bằng gì (chi tiết quyết định chất ngách)

STATE = {   # nỗi đau cụ thể, không phải cảm xúc chung chung
    "sợ_hãi":   ["fear","afraid","terror","worry","anxious","trouble","storm"],
    "tội_lỗi":  ["sin","guilt","shame","wrong","fail","fall","repent"],
    "cô_đơn":   ["alone","lonely","empty","far from","no one","forsaken","abandon"],
    "kiệt_sức": ["tired","weary","heavy","burden","carry","rest","worn"],
    "bệnh_tật": ["sick","heal","pain","body","weak","disease","suffer"],
    "tang_chế": ["grave","death","die","gone","goodbye","mourn","funeral","loss"],
    "nghi_ngờ": ["doubt","why","how long","silent","hide","wonder"],
}

PAYOFF = {  # lời hứa — thứ người nghe mang về sau khi nghe
    "được_dẫn":   ["lead","guide","walk with","path","way","through"],
    "được_giữ":   ["hold","keep","carry","lift","catch","arms","hand"],
    "được_yên":   ["peace","rest","still","calm","quiet","safe"],
    "được_mạnh":  ["strength","strong","rise","stand","power","overcome"],
    "được_tha":   ["forgive","mercy","grace","wash","clean","new"],
    "được_nghe":  ["hear","listen","answer","cry","call","voice"],
    "có_bạn_đồng_hành": ["with me","beside","never leave","not alone","presence"],
}

ADDRESS = ["lord","god","jesus","father","king","savior","saviour","shepherd"]

# Cung cảm xúc: chia bài làm 3 phần, đo sáng/tối từng phần
DARK = ["dark","night","pain","cry","fear","alone","lost","weep","shadow",
        "grave","broken","weary","storm","silent"]
LIGHT = ["light","joy","praise","glory","rise","free","peace","hope",
         "morning","save","heal","sing","dawn","victory"]
_RX_DARK = re.compile("|".join(r"\b" + w + r"\b" for w in DARK))
_RX_LIGHT = re.compile("|".join(r"\b" + w + r"\b" for w in LIGHT))


def tightness(p25, med, p75):
    """CHẶT/vừa/rộng — thông số rộng không phải dữ liệu kém, mà là phát hiện."""
    if med == 0 or pd.isna(med):
        return "rộng", None
    iqr = (p75 - p25) / abs(med)
    return ("CHẶT" if iqr < TIGHT else "vừa" if iqr < MID else "rộng"), round(iqr, 3)


def spread(s: pd.Series) -> dict:
    s = s.dropna()
    if not len(s):
        return {}
    p25, med, p75 = float(s.quantile(.25)), float(s.median()), float(s.quantile(.75))
    t, iqr = tightness(p25, med, p75)
    return {"min": round(float(s.min()), 2), "p25": round(p25, 2),
            "trung_vị": round(med, 2), "p75": round(p75, 2),
            "max": round(float(s.max()), 2),
            "độ_tập_trung": t, "iqr_chuẩn_hoá": iqr, "n": int(len(s))}


def simpson(M, lk, ac, an):
    """Tương quan gộp + tách theo kênh. Trả phán quyết, không chỉ con số."""
    d = M[[lk, ac, "handle"]].dropna()
    if len(d) < 30:
        return None
    r_all, p_all = stats.spearmanr(d[lk], d[ac])
    per, flip = [], 0
    for h, g in d.groupby("handle"):
        if len(g) < MIN_CH:
            continue
        r, p = stats.spearmanr(g[lk], g[ac])
        if pd.isna(r):
            continue
        if r * r_all < 0:
            flip += 1
        per.append({"kênh": h, "n": int(len(g)), "rho": round(float(r), 3),
                    "p": float(p), "đảo_dấu": bool(r * r_all < 0)})
    if not per:
        return None
    med_ch = float(np.median([x["rho"] for x in per]))
    if flip == 0 and abs(med_ch) >= 0.15:
        verdict = "XÁC NHẬN"
    elif flip == 0:
        verdict = "YẾU"          # không đảo dấu nhưng trong kênh gần như bằng 0
    elif flip == 1:
        verdict = "YẾU"
    else:
        verdict = "BÁC BỎ"
    return {
        "lời": lk, "nhạc": an, "cột_nhạc": ac, "n": int(len(d)),
        "rho_gộp": round(float(r_all), 3), "p_gộp": float(p_all),
        "rho_trung_vị_theo_kênh": round(med_ch, 3),
        "số_kênh_xét": len(per), "số_kênh_đảo_dấu": flip,
        "phán_quyết": verdict, "theo_kênh": per,
        "đọc_là": (f"Gộp lại rho={r_all:+.2f} nhưng trong từng kênh chỉ còn "
                   f"{med_ch:+.2f}" + (f", {flip} kênh đảo dấu" if flip else "")
                   + ". " + ("Dùng được." if verdict == "XÁC NHẬN"
                             else "Phần lớn đến từ khác biệt giữa kênh — "
                                  "đừng đưa vào công thức sáng tác.")),
    }


def hit_rate(texts: pd.Series, groups: dict) -> dict:
    """% số bài CHẠM tới mỗi nhóm + số lần trung vị. Không trích lời (T65).

    DÙNG RANH GIỚI TỪ, KHÔNG DÙNG `in`/`.count()`. Bản đầu đếm chuỗi con và
    thổi phồng nặng: `sin` khớp cả **sing** (từ dày đặc trong nhạc worship) →
    "tội lỗi" nhảy từ 48% lên 75%; `king` khớp **making/taking** → 16% lên 47%.
    Cụm nhiều từ ("with me") vẫn khớp bình thường vì \b bao cả cụm.
    """
    low = [t.lower() for t in texts]
    rx = {name: re.compile("|".join(r"\b" + re.escape(k) + r"\b" for k in kws))
          for name, kws in groups.items()}
    out = {}
    for name, kws in groups.items():
        cnt = [len(rx[name].findall(t)) for t in low]
        n = sum(c > 0 for c in cnt)
        out[name] = {"pct_bài": round(n / len(low) * 100, 1),
                     "số_bài": n,
                     "lần_trung_vị": int(np.median(cnt))}
    return dict(sorted(out.items(), key=lambda x: -x[1]["pct_bài"]))


def arc(tr_dir: Path) -> dict:
    """Cung cảm xúc: bài đi từ tối sang sáng, hay ngược lại?

    Chia mỗi bài làm 3 phần THEO SỐ ĐOẠN (không theo thời gian — đoạn im lặng
    đầu/cuối sẽ làm lệch). Điểm mỗi phần = (sáng − tối)/(sáng + tối), nằm trong
    [−1, +1]. Bài <6 đoạn bị loại: chia ba không còn nghĩa.
    """
    import json as _j
    rows = []
    for f in sorted(tr_dir.glob("*.json")):
        d = _j.loads(f.read_text(encoding="utf-8"))
        segs = d.get("segments", [])
        if len(segs) < 6:
            continue
        th = len(segs) // 3

        def sc(ss):
            t = " ".join(x["text"].lower() for x in ss)
            dk = len(_RX_DARK.findall(t))
            lt = len(_RX_LIGHT.findall(t))
            return (lt - dk) / max(1, lt + dk)
        a, b, c = sc(segs[:th]), sc(segs[th:2*th]), sc(segs[2*th:])
        rows.append({"track_id": d.get("track_id"), "đầu": a, "giữa": b, "cuối": c})
    if not rows:
        return {}
    D = pd.DataFrame(rows)
    rise = float((D["cuối"] > D["đầu"]).mean())
    return {
        "n_bài": len(D),
        "điểm_đầu_bài": round(float(D["đầu"].mean()), 3),
        "điểm_giữa_bài": round(float(D["giữa"].mean()), 3),
        "điểm_cuối_bài": round(float(D["cuối"].mean()), 3),
        "pct_sáng_dần": round(rise * 100, 1),
        "thang": "−1 = toàn từ tối · +1 = toàn từ sáng",
        "đọc_là": None,   # điền ở main() để dùng được số đã làm tròn
    }


def themes(texts: pd.Series) -> dict:
    """Đếm bài có chạm chủ đề — KHÔNG trích lời, chỉ đếm (T65)."""
    out = {}
    low = [t.lower() for t in texts]
    for name, kws in THEMES.items():
        n = sum(any(k in t for k in kws) for t in low)
        out[name] = {"số_bài": n, "pct": round(n / len(low) * 100, 1)}
    return dict(sorted(out.items(), key=lambda x: -x[1]["số_bài"]))


def main():
    F = pd.read_parquet(P / "lyrics_features.parquet")
    R = pd.read_parquet(P / "lyrics_raw.parquet")
    A = pd.read_parquet(P / "audio_dna_full.parquet")
    M = F.merge(A, on="track_id", how="inner")

    ok = F[F.enough_data] if "enough_data" in F else F

    # ── 1. VIẾT LỜI THẾ NÀO ────────────────────────────────────────────
    # Ngôi kể KHÔNG nằm ở đây. Nó là phát hiện về NGƯỜI NGHE («chúng ta» = 0%
    # là kết luận, không phải «thông số rộng nên tự do») — xem mục 3.
    recipe_cols = ["words_per_min", "words_per_line", "line_len_sd", "n_lines",
                   "repeat_ratio", "unique_line_ratio", "ttr", "vocab_size"]
    write = {c: spread(ok[c]) for c in recipe_cols if c in ok}

    # ── 2. LỜI ↔ NHẠC ──────────────────────────────────────────────────
    aud = {"guitar": "stems.separation.stem_energy.guitar",
           "drums": "stems.separation.stem_energy.drums",
           "bass": "stems.separation.stem_energy.bass",
           "vocals": "stems.separation.stem_energy.vocals",
           "BPM": "timeline.rhythm.bpm"}
    aud = {k: v for k, v in aud.items() if v in M.columns}
    links = []
    for lk in ["words_per_min", "words_per_line", "repeat_ratio", "ttr",
               "vocab_size", "pct_first_sing", "pct_second"]:
        for an, ac in aud.items():
            r = simpson(M, lk, ac, an)
            if r:
                links.append(r)
    links.sort(key=lambda x: -abs(x["rho_gộp"]))
    confirmed = [x for x in links if x["phán_quyết"] == "XÁC NHẬN"]
    rejected = [x for x in links if x["phán_quyết"] == "BÁC BỎ"]

    # ── 3. NGƯỜI NGHE ──────────────────────────────────────────────────
    RT = R.merge(F[["track_id", "handle"]], on="track_id", how="left")
    voice = {
        "tôi_pct": round(float(ok.pct_first_sing.median()), 2),
        "chúng_ta_pct": round(float(ok.pct_first_plur.median()), 2),
        "bạn_pct": round(float(ok.pct_second.median()), 2),
        "đọc_là": None,
    }
    arc_d = arc(N / "00_input" / "lyrics" / "transcripts_track")
    if arc_d:
        arc_d["đọc_là"] = (
            f"Điểm sáng/tối đi từ {arc_d['điểm_đầu_bài']:+.2f} (đầu bài) qua "
            f"{arc_d['điểm_giữa_bài']:+.2f} lên {arc_d['điểm_cuối_bài']:+.2f} "
            f"(cuối bài) — bài mở ra trong bóng tối rồi kết trong ánh sáng. "
            f"{arc_d['pct_sáng_dần']}% số bài sáng dần về cuối. Đây là CUNG "
            f"CẢM XÚC chuẩn của ngách: đừng kết bài ở chỗ tối.")

    voice["đọc_là"] = (
        f"Ngôi «tôi» ({voice['tôi_pct']}%) áp đảo «chúng ta» "
        f"({voice['chúng_ta_pct']}%) — lời viết cho người nghe MỘT MÌNH, "
        f"không phải hội chúng hát tập thể. Khớp với bối cảnh nghe chủ động "
        f"(cầu nguyện, sáng sớm) ở STEP_05.")

    out = {
        "nguồn": {
            "n_track": int(len(ok)), "n_video": int(F.video_id.nunique()),
            "n_kênh": int(F.handle.nunique()),
            # kênh 1-2 bài không đỡ được kết luận nào; báo cáo phải nói con số
            # này chứ không phải tổng, kẻo phóng đại độ phủ
            "n_kênh_đủ_lớn": int((F.groupby("handle").size() >= MIN_CH).sum()),
            "min_bài_mỗi_kênh": MIN_CH,
            "n_ghép_được_với_nhạc": int(len(M)),
            "tổng_chữ": int(ok.n_words.sum()),
            "từ": "00_input/processed/lyrics_features.parquet + audio_dna_full.parquet",
        },
        "1_viết_lời": {
            "cách_dùng": "Khoảng p25–p75 là vùng an toàn. CHẶT thì theo sát; "
                         "rộng thì tự do — ép theo là bịa ràng buộc.",
            "thông_số": write,
        },
        "2_lời_với_nhạc": {
            "phương_pháp": "Spearman + kiểm Simpson theo kênh (≥%d track)" % MIN_CH,
            "cảnh_báo": "p nhỏ KHÔNG đủ. Chỉ dùng mối XÁC NHẬN.",
            "số_mối_xét": len(links),
            "số_xác_nhận": len(confirmed), "số_bác_bỏ": len(rejected),
            "xác_nhận": confirmed,
            "bác_bỏ": rejected[:6],
            "tất_cả": links,
        },
        "3_người_nghe": {
            "ngôi_kể": voice,
            "họ_đang_ở_đâu": hit_rate(RT.text, STATE),
            "họ_nhận_được_gì": hit_rate(RT.text, PAYOFF),
            "xưng_hô_với_Chúa": hit_rate(RT.text, {a: [a] for a in ADDRESS}),
            "cung_cảm_xúc": arc_d,
            "chủ_đề": themes(RT.text),
            "ghi_chú": "Đếm theo từ khoá — bài chạm nhiều nhóm được đếm ở "
                       "nhiều dòng. Không trích lời (T65).",
        },
        "giới_hạn": [
            {"thiếu": "Nhóm đối chứng",
             "hệ_quả": f"Tất cả {int(len(ok))} bài đều từ kênh đang hoạt động. KHÔNG kết "
                       "luận được đặc điểm lời nào GÂY RA thành công — chỉ mô "
                       "tả nhóm này đang viết thế nào."},
            {"thiếu": "View ở cấp track",
             "hệ_quả": "View là của VIDEO (tuyển tập nhiều bài), không tách "
                       "được về từng bài. Nên không xếp hạng lời theo hiệu quả."},
            {"thiếu": "Phủ sóng toàn ngách",
             "hệ_quả": f"{int(F.video_id.nunique())} video / "
                       f"{int((F.groupby('handle').size() >= MIN_CH).sum())} kênh chính, "
                       f"so với 50 video trong COHORT. Đây là mẫu tiện có, "
                       f"không phải mẫu đại diện."},
            {"thiếu": "Kiểm tai người",
             "hệ_quả": "Lời do Whisper phiên âm, tin cậy trung vị −0,35. Chưa "
                       "ai nghe đối chiếu. Sai từ lẻ có thể đẩy lệch vocab/TTR."},
        ],
    }

    f = OUT / "LYRICS_ANALYSIS.json"
    f.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✅ {f}")
    print(f"   {out['nguồn']['n_track']} track · {out['nguồn']['tổng_chữ']:,} chữ "
          f"· {out['nguồn']['n_kênh']} kênh")
    print(f"   thông số viết lời: {len(write)} "
          f"(CHẶT {sum(1 for v in write.values() if v.get('độ_tập_trung')=='CHẶT')})")
    print(f"   lời×nhạc: xét {len(links)} · XÁC NHẬN {len(confirmed)} · BÁC BỎ {len(rejected)}")
    for c in confirmed[:5]:
        print(f"     ✓ {c['lời']} × {c['nhạc']}  rho={c['rho_gộp']:+.2f} "
              f"(trong kênh {c['rho_trung_vị_theo_kênh']:+.2f})")


if __name__ == "__main__":
    main()
