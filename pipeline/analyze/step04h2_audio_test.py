"""STEP_04h2 · KIỂM ĐỊNH ÂM THANH — đặc trưng nào phân biệt thắng/thua?

KHÁC GÌ 04h: 04h là MÔ TẢ (nhóm top nghe như thế nào, n=5). Bước này là
KIỂM ĐỊNH — nối 307 track với view thật rồi hỏi: đặc trưng nào THẬT SỰ
tương quan với hiệu suất?

BA CÁI BẪY BƯỚC NÀY PHẢI CHẶN (đã gặp thật trên dữ liệu v2):

1. NGHỊCH LÝ SIMPSON. 307 track chỉ đến từ 6 kênh, kênh chênh nhau ~34 lần
   view trung vị. Tương quan gộp đo SỰ KHÁC NHAU GIỮA KÊNH chứ không phải
   tác dụng của đặc trưng. Ví dụ thật: stem_piano gộp cho rho=+0,36
   (p=7,6e-11, trông rất thuyết phục) nhưng tách theo kênh thì 2/6 kênh
   cho dấu NGƯỢC. => LUÔN kiểm trong từng kênh rồi mới gộp (Stouffer).

2. GIẢ ĐỘC LẬP. 307 track nhưng chỉ 29 video; 10 track cùng một video chia
   chung một con số view. Dùng track làm đơn vị sẽ thổi phồng n gấp ~10 lần.
   => Gộp track -> video (trung vị) TRƯỚC khi kiểm.

3. DỮ LIỆU HỢP THÀNH (compositional). 5 stem là TỈ LỆ, tổng ~0,91. Trống
   tăng thì thứ khác buộc phải giảm — corr(drums,guitar) = -0,75 là do ràng
   buộc chứ không phải quan hệ nhân quả. => Báo cả bản CLR và bản tỉ lệ
   trực tiếp (drums/vocals) để người đọc thấy hiệu ứng thật.

Đầu ra: <N>/04_outlier/audio/AUDIO_TEST.json
"""
import json, sys
import numpy as np
import pandas as pd
from scipy import stats as st

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
from _common import niche_paths

N, P, OUT = niche_paths("04_outlier/audio")

# ── đặc trưng số được kiểm. Bỏ cột định danh/phân loại. ──
NUM = ["bpm", "lufs", "plr_db", "lra", "stereo_width", "stem_vocals", "stem_bass",
       "stem_drums", "stem_guitar", "stem_piano", "swing_phase", "dao_phach",
       "four_on_floor", "tempo_cv", "do_tre_ms", "hop_am_moi_o_nhip",
       "so_hop_am_rieng", "quang_semitone", "buoc_lien", "not_moi_giay",
       "vibrato_hz", "hnr_db", "jitter", "lech_cent", "bam_luoi_semitone",
       "tuong_quan_LR", "tach_stem_dB", "phut"]
STEMS = ["stem_vocals", "stem_bass", "stem_drums", "stem_guitar", "stem_piano"]

MIN_VID_PER_CH = 4      # dưới mức này Spearman trong kênh vô nghĩa
MIN_CHANNELS = 4        # cần đủ kênh mới gộp Stouffer được


def stouffer(rs, ns):
    """Gộp nhiều rho thành một Z. Fisher-z có trọng số sqrt(n-3)."""
    zs = [np.arctanh(np.clip(r, -.999, .999)) * np.sqrt(max(n - 3, 1))
          for r, n in zip(rs, ns)]
    Z = np.sum(zs) / np.sqrt(len(zs))
    return Z, 2 * (1 - st.norm.cdf(abs(Z)))


def within_channel(V, col, ycol="lv"):
    """Spearman trong từng kênh -> gộp. Trả None nếu không đủ kênh."""
    rs, ns, per_ch = [], [], {}
    for ch, g in V.groupby("channel_handle"):
        d = g[[col, ycol]].dropna()
        if len(d) < MIN_VID_PER_CH or d[col].nunique() < 3:
            continue
        r, _ = st.spearmanr(d[col], d[ycol])
        if np.isnan(r):
            continue
        rs.append(r); ns.append(len(d)); per_ch[ch] = round(float(r), 3)
    if len(rs) < MIN_CHANNELS:
        return None
    Z, p = stouffer(rs, ns)
    return {"rho_mean": float(np.mean(rs)), "Z": float(Z), "p": float(p),
            "k_channels": len(rs), "k_positive": int(sum(1 for x in rs if x > 0)),
            "per_channel": per_ch}


def bh_qvalues(ps):
    """Benjamini-Hochberg. Kiểm 28 đặc trưng thì p<0,05 thô là chưa đủ."""
    order = np.argsort(ps); m = len(ps)
    q = np.empty(m)
    prev = 1.0
    for rank, i in enumerate(reversed(order), 1):
        prev = min(prev, ps[i] * m / (m - rank + 1))
        q[i] = prev
    return q


def load_tracks(path):
    """Đọc bảng track. Chấp nhận .parquet (đã nạp) hoặc .xlsx (thô)."""
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    rows = list(__import__("openpyxl").load_workbook(
        path, read_only=True, data_only=True)["307 track"].iter_rows(values_only=True))
    return pd.DataFrame(rows[1:], columns=rows[0])


def main():
    src = P / "audio_dna.parquet"
    if not src.exists():
        print("⏭  Bỏ qua 04h2: chưa có", src)
        return
    T = load_tracks(src)
    vm = pd.read_parquet(P / "video_master.parquet")

    j = T.merge(vm[["video_id", "view_count", "channel_handle"]], on="video_id")
    if j.empty:
        print("⏭  Bỏ qua 04h2: không track nào nối được với video_master")
        return
    for c in NUM:
        if c in j:
            j[c] = pd.to_numeric(j[c], errors="coerce")

    # ── BẪY 2: gộp track -> video. Đơn vị độc lập là VIDEO. ──
    cols = [c for c in NUM if c in j]
    V = (j.groupby(["video_id", "channel_handle"])
           .agg(**{c: (c, "median") for c in cols},
                views=("view_count", "first"), n_track=("track_id", "size"))
           .reset_index())
    V["lv"] = np.log10(V.views)

    # ── BẪY 3: CLR cho nhóm stem (dữ liệu hợp thành) ──
    have_stems = [c for c in STEMS if c in V]
    if len(have_stems) == len(STEMS):
        X = V[have_stems].clip(lower=1e-4)
        lg = np.log(X)
        for c in have_stems:
            V[c + "_clr"] = lg[c] - lg.mean(axis=1)
        V["drums_over_vocals"] = V.stem_drums / V.stem_vocals.clip(lower=1e-4)
        V["drums_over_guitar"] = V.stem_drums / V.stem_guitar.clip(lower=1e-4)

    tested = [c for c in cols] + [c for c in V.columns
                                  if c.endswith("_clr") or c.startswith("drums_over_")]

    # ── BẪY 1: kiểm TRONG kênh, không kiểm gộp ──
    rows_out, ps = [], []
    for c in tested:
        r = within_channel(V, c)
        if r:
            r["feature"] = c
            rows_out.append(r); ps.append(r["p"])
    if not rows_out:
        print("⏭  Bỏ qua 04h2: không đủ kênh để kiểm trong-kênh")
        return
    for r, q in zip(rows_out, bh_qvalues(np.array(ps))):
        r["q"] = float(q)
        # XÁC NHẬN đòi CẢ HAI: qua đa kiểm định VÀ mọi kênh cùng dấu
        all_same = r["k_positive"] in (0, r["k_channels"])
        r["verdict"] = ("XÁC NHẬN" if r["q"] < 0.05 and all_same
                        else "YẾU" if r["p"] < 0.05
                        else "BÁC BỎ")
    rows_out.sort(key=lambda x: x["p"])

    # ── ĐẶC TRƯNG PHÂN LOẠI: Kruskal trong từng kênh ──
    # Không gộp vào bảng trên được (Spearman cần số). Nhưng bỏ qua thì báo cáo
    # sẽ im lặng về điệu trưởng/thứ, quãng giọng, thể loại — toàn thứ người đọc
    # muốn biết. Ngoài ra thể loại là ca LẪN VỚI KÊNH điển hình, phải nêu rõ.
    # Đơn vị vẫn là VIDEO (bẫy 2): mỗi video lấy nhãn CHIẾM ĐA SỐ trong các track
    # của nó. Dùng thẳng track ở đây sẽ lặp lại đúng lỗi thổi phồng cỡ mẫu.
    cat_out = []
    for c in ["truong_thu", "quang_giong", "ho_the_loai", "nhip", "the_loai_chinh"]:
        if c not in j:
            continue
        mode = (j.groupby("video_id")[c]
                  .agg(lambda s: s.mode().iat[0] if not s.mode().empty else np.nan))
        Vc = V[["video_id", "channel_handle", "lv"]].copy()
        Vc[c] = Vc.video_id.map(mode)
        Vc = Vc.dropna(subset=[c])
        # lẫn với kênh tới mức nào? (tính trên track — đây là câu hỏi về PHÂN BỐ
        # nhãn giữa các kênh, không phải về hiệu suất, nên track là đơn vị đúng)
        ct = pd.crosstab(j.channel_handle, j[c])
        chi2, p_conf = st.chi2_contingency(ct)[:2] if ct.shape[1] > 1 else (np.nan, 1.0)
        per_ch, sig = {}, 0
        for ch, g in Vc.groupby("channel_handle"):
            grp = [x.lv.values for _, x in g.groupby(c) if len(x) >= 2]
            if len(grp) < 2:
                continue
            H, pp = st.kruskal(*grp)
            per_ch[ch] = round(float(pp), 4)
            sig += pp < 0.05
        if not per_ch:
            continue
        cat_out.append({
            "feature": c, "k_channels_tested": len(per_ch),
            "k_channels_significant": int(sig), "per_channel_p": per_ch,
            "confound_with_channel_chi2": float(chi2),
            "confound_p": float(p_conf),
            # Ở cỡ mẫu video (n≈29) thường chỉ 1–2 kênh đủ nhóm để kiểm.
            # "0/1 kênh có ý nghĩa" KHÔNG phải bằng chứng bác bỏ — nó là
            # thiếu mẫu. Gọi nhầm thành BÁC BỎ là khẳng định mạnh hơn dữ liệu.
            "verdict": ("KHÔNG ĐỦ MẪU" if len(per_ch) < 3
                        else "XÁC NHẬN" if sig == len(per_ch)
                        else "YẾU" if sig else "BÁC BỎ"),
            "note": ("lẫn nặng với kênh — thể loại gần như chỉ là biến thay cho kênh"
                     if p_conf < 0.01 else ""),
        })

    # ── đối chứng: tương quan GỘP, để lộ rõ bẫy Simpson ──
    naive = {}
    for c in tested:
        d = V[[c, "lv"]].dropna()
        if len(d) < 10:
            continue
        r, p = st.spearmanr(d[c], d.lv)
        naive[c] = {"rho": round(float(r), 3), "p": float(p)}

    # Cảnh báo Simpson: gộp CÓ ý nghĩa nhưng trong-kênh thì KHÔNG (hoặc đảo dấu).
    # Ngưỡng p<0,05 chứ không phải 0,01: sau khi gộp track→video, n tụt còn 29
    # nên p thô yếu đi. Ví dụ thật v2: stem_piano gộp rho=+0,39 p=0,038 —
    # trông như phát hiện — nhưng trong-kênh chỉ 3/6 cùng dấu, q=0,94 → BÁC BỎ.
    # Để ngưỡng 0,01 thì đúng ca kinh điển này lọt lưới.
    simpson = []
    for r in rows_out:
        nv = naive.get(r["feature"])
        if not nv or nv["p"] >= 0.05:
            continue
        naive_pos = nv["rho"] > 0
        flipped = r["k_positive"] not in (0, r["k_channels"])
        # đảo chiều hẳn: gộp dương mà trong-kênh âm (hoặc ngược lại)
        reversed_sign = (r["rho_mean"] > 0) != naive_pos
        if flipped or reversed_sign or r["q"] >= 0.05:
            simpson.append({"feature": r["feature"], "naive_rho": nv["rho"],
                            "naive_p": nv["p"], "within_rho": round(r["rho_mean"], 3),
                            "within_q": r["q"], "k_positive": r["k_positive"],
                            "k_channels": r["k_channels"],
                            "reversed_sign": bool(reversed_sign),
                            "verdict": r["verdict"]})

    res = {
        "niche": N.name,
        "n_tracks": int(len(j)),
        "n_videos": int(len(V)),
        "n_channels": int(V.channel_handle.nunique()),
        "unit_of_analysis": "video (track gộp bằng trung vị)",
        "view_span": {"min": int(V.views.min()), "median": int(V.views.median()),
                      "max": int(V.views.max()),
                      "ratio": round(float(V.views.max() / max(V.views.min(), 1)), 1)},
        "channel_spread_ratio": round(float(
            V.groupby("channel_handle").views.median().max() /
            V.groupby("channel_handle").views.median().min()), 1),
        "tests": rows_out,
        "categorical_tests": cat_out,
        "naive_pooled": naive,
        "simpson_warnings": simpson,
        "_meta": {
            "method": "Spearman trong từng kênh → gộp Stouffer → hiệu chỉnh BH",
            "min_videos_per_channel": MIN_VID_PER_CH,
            "verdict_rule": "XÁC NHẬN = q<0,05 VÀ mọi kênh cùng dấu",
            "limits": [
                f"n thật = {len(V)} video, không phải {len(j)} track",
                "chưa có nhóm kênh THẤT BẠI làm đối chứng",
                "stem là tỉ lệ hợp thành (tổng≈0,91) — đọc kèm bản CLR",
            ],
        },
    }
    (OUT / "AUDIO_TEST.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ {OUT/'AUDIO_TEST.json'}")
    print(f"   {len(j)} track → {len(V)} video / {res['n_channels']} kênh")
    for r in rows_out[:6]:
        print(f"   {r['feature']:22} rho={r['rho_mean']:+.3f} q={r['q']:.3f} "
              f"[{r['k_positive']}/{r['k_channels']}] {r['verdict']}")
    for c in cat_out:
        print(f"   [phân loại] {c['feature']:16} {c['k_channels_significant']}/"
              f"{c['k_channels_tested']} kênh có ý nghĩa → {c['verdict']}"
              + (f"  ⚠ {c['note']}" if c["note"] else ""))
    if simpson:
        print(f"   ⚠ {len(simpson)} đặc trưng dính bẫy Simpson (xem simpson_warnings)")


if __name__ == "__main__":
    main()
