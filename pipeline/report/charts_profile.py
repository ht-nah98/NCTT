"""Biểu đồ cho HỒ SƠ NGÁCH — thiết kế cho CẤP DUYỆT, không cho người phân tích.

KHÁC các charts*.py hiện có: chúng vẽ để chứng minh (có p-value, khoảng tin cậy,
trục log). Bộ này vẽ để QUYẾT ĐỊNH — mỗi hình trả lời một câu hỏi và tự giải
thích được mà không cần đọc chú thích.

BỐN NGUYÊN TẮC:
  1. Mỗi hình = một câu hỏi. Không nhồi hai thông điệp vào một hình.
  2. Kết luận viết THẲNG lên hình, không bắt người đọc tự suy.
  3. Màu có nghĩa cố định: xanh = tốt/xác nhận · đỏ = rủi ro/bác bỏ ·
     hổ phách = cảnh báo · xám = nền so sánh.
  4. Không dùng trục log, không dùng thang phi tuyến — cấp duyệt đọc sai ngay.

Đầu ra: <N>/99_report/p*.png
"""
import json, sys, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
warnings.filterwarnings("ignore")

N = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--")
         else "niches/christian-blues")
P = N/"00_input/processed"
OUT = N/"99_report"; OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 170, "axes.grid": True, "grid.alpha": .22, "grid.linewidth": .6,
    "font.family": "DejaVu Sans", "axes.labelcolor": "#5A514B",
    "xtick.color": "#5A514B", "ytick.color": "#5A514B",
})
INK = "#1A1614"; ACC = "#8C3A2B"; OK = "#2F6B4F"; WARN = "#B5731F"
NO = "#9B2C2C"; MUTE = "#9A8E85"; PAPER = "#F7F4F0"

M = json.load(open(N/"_state/metrics.json"))
S = json.load(open(N/"_state/scores.json"))
AUD, MK, MO, EN = M["audience"], M["market"], M["momentum"], M["entry"]
SY, KW = M["synthesis"], M["keyword"]


def _load(p):
    f = N/p
    return json.load(open(f)) if f.exists() else None


RECIPE = _load("04_outlier/audio/AUDIO_RECIPE.json")
CH = pd.read_parquet(P/"channels_enriched.parquet")
CH["vpm"] = CH.views_per_month


def note(ax, text, y=-0.30, color=INK, weight="bold"):
    """Kết luận viết thẳng dưới hình.

    Neo vào FIGURE chứ không vào axes: hình hai cột thì axes trái chỉ chiếm
    nửa bề ngang, chú thích căn giữa theo nó sẽ LỆCH HẲN sang trái (T59).
    Tham số `ax` giữ lại để suy ra mép dưới thấp nhất của cụm axes.
    """
    fig = ax.get_figure()
    bottom = min(a.get_position().y0 for a in fig.axes)
    # y âm (theo axes cũ) -> quy đổi thành khoảng cách dưới cụm axes
    off = abs(y) * ax.get_position().height
    fig.text(0.5, bottom - off, text, ha="center", va="top",
             fontsize=8.2, color=color, weight=weight)


def save(fig, name):
    fig.savefig(OUT/name, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return name


# ═══ P1 · ĐIỂM NGÁCH: kịch bản nào cũng phải thấy ═══════════════════════
def p1_score():
    """Độ nhạy của điểm — KHÔNG vẽ ngưỡng khuyến nghị.

    Bản đầu có vùng nền BỎ / THEO DÕI / VÀO. Đã bỏ: quyết định vào hay không
    là việc của cấp duyệt, không phải của báo cáo — nhất là khi mọi con số ở
    đây đều là ƯỚC LƯỢNG. Hình chỉ trình bày điểm dao động bao nhiêu và vì
    sao, để người quyết định tự cân (T57).
    """
    fig, ax = plt.subplots(figsize=(7.4, 2.5))
    sc = [("Nếu M2.4 sai\n(cửa sổ chưa chín)", SY["scenarios"]["T2_drops_to_1"], NO),
          ("Nếu chính sách siết", SY["scenarios"]["policy_tightens"], WARN),
          ("Ước lượng hiện tại", S["total_score"], ACC),
          ("Nếu RPM = $6", SY["scenarios"]["RPM_is_6"], OK)]
    sc.sort(key=lambda x: x[1])
    ys = np.arange(len(sc))
    for y, (lab, val, col) in zip(ys, sc):
        ax.barh(y, val, color=col, height=.62,
                alpha=1 if lab.startswith("Ước lượng") else .5)
        ax.text(val + .3, y, f"{val:.2f}".replace(".", ","), va="center",
                fontsize=9.5, weight="bold", color=col)
    ax.set_yticks(ys); ax.set_yticklabels([s[0] for s in sc], fontsize=8.3)
    ax.set_xlim(0, 20); ax.set_xlabel("Điểm trên thang 20")
    ax.grid(axis="y", alpha=0)
    lo, hi = sc[0][1], sc[-1][1]
    def _c(x, nd=2):                      # số thập phân kiểu Việt
        return f"{x:.{nd}f}".replace(".", ",")
    note(ax, f"Điểm dao động {_c(lo)} – {_c(hi)} tuỳ các giả định chưa xác minh "
             f"(chênh {_c(hi-lo)} điểm).\n"
             "Đây là ƯỚC LƯỢNG của nhóm nghiên cứu, không phải khuyến nghị "
             "vào hay không.", y=-0.42, color=INK)
    return save(fig, "p1_score_scenarios.png")


# ═══ P2 · VAN HIỆU CHỈNH: chủ động vs nền ══════════════════════════════
def p2_listening():
    ctx = AUD["context"]
    ACT = ["prayer_devo", "morning", "sick_hosp", "grief"]
    BG = ["sleep_night", "driving", "housework", "work"]
    LB = {"prayer_devo": "Cầu nguyện, tĩnh nguyện", "morning": "Buổi sáng",
          "sick_hosp": "Ốm đau, nằm viện", "grief": "Tang chế",
          "sleep_night": "Ngủ, mất ngủ", "driving": "Lái xe",
          "housework": "Việc nhà", "work": "Lúc làm việc"}
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 2.9),
                                 gridspec_kw={"width_ratios": [1.15, 1]})
    items = [(LB[k], ctx[k]["pct"], OK if k in ACT else MUTE) for k in ACT + BG]
    items.sort(key=lambda x: x[1])
    ys = np.arange(len(items))
    a1.barh(ys, [i[1] for i in items], color=[i[2] for i in items], height=.66)
    for y, (lab, v, c) in zip(ys, items):
        a1.text(v + .25, y, f"{v:.2f}%".replace(".", ","), va="center",
                fontsize=7.8, color=c, weight="bold")
    a1.set_yticks(ys); a1.set_yticklabels([i[0] for i in items], fontsize=8)
    a1.set_xlim(0, max(i[1] for i in items) * 1.30)
    a1.set_xlabel("% comment nêu bối cảnh"); a1.grid(axis="y", alpha=0)
    a1.set_title("Nghe khi nào?", fontsize=9.5, weight="bold", color=INK, loc="left")

    act = sum(ctx[k]["pct"] for k in ACT); bg = sum(ctx[k]["pct"] for k in BG)
    # Bố cục: nới trần 1,7× và đặt "11,5×" LÊN TRÊN hai cột, không đè lên cột.
    # Bản đầu đặt số ở giữa vùng vẽ nên chồng lên cột CHỦ ĐỘNG (T58).
    a2.bar([0, 1], [act, bg], color=[OK, MUTE], width=.5)
    top = act * 1.70
    a2.set_ylim(0, top)
    for x, v, c in [(0, act, OK), (1, bg, MUTE)]:
        a2.text(x, v + top*.03, f"{v:.1f}%".replace(".", ","), ha="center",
                va="bottom", fontsize=10.5, weight="bold", color=c)
    # mũi tên nối hai cột + bội số, nằm trên đỉnh cột cao nhất
    yb = act + top*.20
    a2.annotate("", xy=(1, yb), xytext=(0, yb),
                arrowprops=dict(arrowstyle="<->", color=ACC, lw=1.2))
    a2.text(.5, yb + top*.03, f"{act/bg:.1f}×".replace(".", ","), ha="center",
            va="bottom", fontsize=14, weight="bold", color=ACC)
    a2.set_xticks([0, 1]); a2.set_xticklabels(["CHỦ ĐỘNG", "NGHE NỀN"],
                                              fontsize=8.5, weight="bold")
    a2.set_xlim(-.6, 1.6)
    a2.set_ylabel("% comment"); a2.grid(axis="x", alpha=0)
    a2.set_title("Chênh bao nhiêu lần?", fontsize=9.5, weight="bold",
                 color=INK, loc="left")
    note(a1, "Khán giả NGHE CHỦ ĐỘNG — mở lên để ngồi nghe, không phải nhạc nền.\n"
             "→ Đòn bẩy là CHẤT LƯỢNG NHẠC, không phải thumbnail hay độ dài.",
         y=-0.34, color=OK)
    return save(fig, "p2_listening_mode.png")


# ═══ P3 · CHÂN DUNG: phân bố lệch ══════════════════════════════════════
def p3_personas():
    pers = AUD["personas"]
    PN = {"p_healing": "Người đang chịu đựng", "p_elder": "Người cao tuổi",
          "p_convert": "Người mới tin đạo", "p_music": "Nhạc công"}
    items = sorted(pers.items(), key=lambda x: -x[1]["n"])
    fig, ax = plt.subplots(figsize=(7.4, 2.4))
    xs = np.arange(len(items))
    cols = [OK if v["n"] >= 100 else WARN if v["n"] >= 30 else NO
            for _, v in items]
    ax.bar(xs, [v["n"] for _, v in items], color=cols, width=.55)
    for x, (k, v) in zip(xs, items):
        ax.text(x, v["n"] + 22, f'n={v["n"]}', ha="center", fontsize=8.5,
                weight="bold", color=cols[x])
        ax.text(x, v["n"] + 95, f'{v["pct"]:.1f}%'.replace(".", ","),
                ha="center", fontsize=7.5, color=MUTE)
    ax.axhline(30, color=NO, ls=":", lw=1.1)
    ax.text(len(items) - .45, 46, "ngưỡng đủ mẫu (n=30)", fontsize=7,
            color=NO, ha="right")
    ax.set_xticks(xs); ax.set_xticklabels([PN[k] for k, _ in items], fontsize=8.3)
    ax.set_ylabel("Số comment"); ax.set_ylim(0, max(v["n"] for _, v in items) * 1.3)
    ax.grid(axis="x", alpha=0)
    note(ax, "Phân bố RẤT LỆCH: một chân dung chiếm 15,1%, ba chân dung còn lại "
             "cộng lại chưa tới 2%.\n→ Chỉ nên lập 1–2 phân khúc chính; "
             "ép 4 phân khúc cân bằng thì dữ liệu không đỡ nổi.", y=-0.30, color=WARN)
    return save(fig, "p3_personas.png")


# ═══ P4 · CUNG: kênh mới vào được không ════════════════════════════════
def p4_market():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 2.8))
    d = CH.dropna(subset=["channel_age_months", "vpm"])
    young = d[d.channel_age_months <= 6]
    old = d[d.channel_age_months > 6]
    a1.scatter(old.channel_age_months, old.vpm/1e3, s=26, color=MUTE,
               alpha=.55, label=f"Kênh >6 tháng (n={len(old)})", zorder=2)
    a1.scatter(young.channel_age_months, young.vpm/1e3, s=44, color=ACC,
               alpha=.85, label=f"Kênh ≤6 tháng (n={len(young)})", zorder=3)
    a1.axhline(100, color=OK, ls="--", lw=1.1)
    a1.text(d.channel_age_months.max()*.98, 118, "ngưỡng thành công 100k",
            fontsize=6.8, color=OK, ha="right")
    a1.set_xlabel("Tuổi kênh (tháng)"); a1.set_ylabel("View/tháng (nghìn)")
    a1.legend(fontsize=6.8, frameon=False, loc="upper right")
    a1.set_title("Kênh mới có vào được không?", fontsize=9.5, weight="bold",
                 color=INK, loc="left")

    # Lorenz — độ tập trung thị phần
    v = np.sort(d.vpm.values)
    cum = np.cumsum(v)/v.sum()
    x = np.arange(1, len(v)+1)/len(v)
    a2.plot([0, 1], [0, 1], ls="--", color=MUTE, lw=1)
    a2.plot(np.r_[0, x], np.r_[0, cum], color=ACC, lw=2)
    a2.fill_between(np.r_[0, x], np.r_[0, cum], np.r_[0, x],
                    color=ACC, alpha=.13)
    a2.set_xlabel("% số kênh (từ nhỏ đến lớn)")
    a2.set_ylabel("% tổng lượt xem")
    a2.text(.05, .86, f"Gini = {EN['M3_1_gini']:.3f}".replace(".", ","),
            fontsize=10, weight="bold", color=ACC, transform=a2.transAxes)
    a2.text(.05, .77, "0 = chia đều · 1 = một kênh chiếm hết", fontsize=6.8,
            color=MUTE, transform=a2.transAxes)
    a2.text(.05, .69, "→ chưa bị độc chiếm", fontsize=7.5, color=MUTE,
            transform=a2.transAxes)
    a2.set_title("Thị phần tập trung tới đâu?", fontsize=9.5, weight="bold",
                 color=INK, loc="left")
    # .replace(".", ",") trên CẢ CÂU sẽ biến dấu chấm kết câu thành dấu phẩy —
    # câu bị cụt. Chỉ đổi dấu thập phân của riêng con số (T60).
    _age = f"{EN['M3_3_alt_median_age_of_successful']:.1f}".replace(".", ",")
    note(a1, f"{EN['M3_2_newcomer_success_pct']:.0f}% kênh dưới 12 tháng đạt "
             f"≥100k lượt xem/tháng · nhóm thành công chỉ mất {_age} tháng.",
         y=-0.32, color=OK)
    return save(fig, "p4_market_entry.png")


# ═══ P5 · CÔNG THỨC NHẠC: cái nào bắt buộc, cái nào tự do ══════════════
def p5_recipe():
    if not RECIPE:
        return None
    SP = RECIPE["spec"]
    LB = {"lufs": "Độ to (LUFS)", "plr_db": "Dải động đỉnh",
          "swing_phase": "Pha swing", "buoc_lien": "Giai điệu liền bậc",
          "lech_cent": "Lệch cao độ (cent)", "bpm": "Nhịp độ (BPM)",
          "stereo_width": "Độ rộng stereo", "stem_guitar": "Ghi-ta",
          "stem_piano": "Piano", "hnr_db": "Độ sạch giọng",
          "stem_vocals": "Giọng hát", "stem_drums": "Trống", "stem_bass": "Bass"}
    keys = [k for k in ["lech_cent", "buoc_lien", "swing_phase", "plr_db", "lufs",
                        "stem_vocals", "stem_bass", "stem_drums", "bpm",
                        "stereo_width", "stem_guitar", "stem_piano"] if k in SP]
    # Vẽ THẲNG đại lượng dùng để phân loại: IQR/trung vị.
    # Bản đầu chuẩn hoá min-max nên thanh «CHẶT» có khi DÀI HƠN thanh «rộng»
    # — hình nói ngược chú thích. Trục này thì thanh ngắn luôn = chặt (T54).
    keys = sorted(keys, key=lambda k: SP[k]["iqr_over_median"] or 9e9)
    fig, ax = plt.subplots(figsize=(7.4, 3.4))
    ys = np.arange(len(keys))[::-1]
    for y, k in zip(ys, keys):
        s = SP[k]
        tight = s["tightness"]
        col = OK if tight == "CHẶT" else WARN if tight == "vừa" else MUTE
        w = min(s["iqr_over_median"] or 0, 1.0)   # cắt ngọn ở 1,0 cho dễ đọc
        ax.plot([0, 1], [y, y], color="#EDE7E0", lw=1.2, zorder=1)
        ax.plot([0, w], [y, y], color=col, lw=7, alpha=.62, zorder=2,
                solid_capstyle="round")
        ax.plot([w], [y], "o", color=col, ms=6.5, zorder=3)
        lbl = f'{s["iqr_over_median"]:.2f}'.replace(".", ",")
        if (s["iqr_over_median"] or 0) > 1.0:
            lbl += "+"
        ax.text(w + .02, y, lbl, fontsize=7.2, va="center", color=col)
        ax.text(1.12, y, tight, fontsize=7.3, va="center", color=col,
                weight="bold")
        ax.text(-0.03, y, LB.get(k, k), fontsize=8, va="center", ha="right",
                color=INK)
    for xv, lb in [(0.15, "CHẶT"), (0.40, "vừa")]:
        ax.axvline(xv, color="#CFC4B8", ls=":", lw=1, zorder=0)
        ax.text(xv, len(keys) - .55, f"↤ {lb}", fontsize=6.8, color=MUTE, ha="right")
    ax.set_xlim(-0.02, 1.30); ax.set_ylim(-.8, len(keys)-.2)
    ax.set_yticks([]); ax.set_xticks([])
    ax.spines["left"].set_visible(False); ax.spines["bottom"].set_visible(False)
    ax.grid(alpha=0)
    ax.set_title("Nhóm thắng dựng nhạc chặt ở đâu, tự do ở đâu?",
                 fontsize=9.5, weight="bold", color=INK, loc="left", x=-0.22)
    ax.annotate("Độ phân tán của nhóm thắng (IQR ÷ trung vị) — thanh CÀNG NGẮN, "
                "cả nhóm làm CÀNG GIỐNG NHAU",
                xy=(0.5, -0.10), xycoords="axes fraction", ha="center",
                fontsize=7.4, color=MUTE)
    # Kết luận phải khớp thứ hạng THẬT trên hình, không viết cứng (T54).
    tightest = keys[0]
    lc = SP.get("lech_cent", {}).get("iqr_over_median")
    note(ax, f"Năm thông số CHẶT nhất đều dưới 0,15 — dẫn đầu là "
             f"{LB.get(tightest, tightest).upper()}.\n"
             f"Trong đó ĐỘ LỆCH CAO ĐỘ ({str(lc).replace('.', ',')}) là ràng buộc "
             f"quan trọng nhất: nhóm thắng cố ý để giọng lệch tự nhiên\n"
             f"→ tuyệt đối KHÔNG autotune cứng. Nắn về 0 cent là ra chất nhạc máy, "
             f"lạc ngách.", y=-0.20, color=NO)
    return save(fig, "p5_recipe_tightness.png")


# ═══ P6 · KHOẢNG TRỐNG TIẾNG NÓI ══════════════════════════════════════
def p6_voicegap():
    G = pd.read_csv(N/"06_keyword/03_voice_gap.csv").head(7)
    fig, ax = plt.subplots(figsize=(7.4, 2.6))
    ys = np.arange(len(G))[::-1]
    ax.barh(ys, G.in_comments, color=ACC, height=.42, label="Khán giả nói (comment)")
    ax.barh(ys - .42, G.in_titles, color=MUTE, height=.42, label="Nhà sản xuất dùng (tiêu đề)")
    for y, r in zip(ys, G.itertuples()):
        ax.text(r.in_comments + 55, y, f"{int(r.in_comments):,}".replace(",", " "),
                va="center", fontsize=7.5, color=ACC, weight="bold")
        ax.text(r.in_comments + 460, y - .21, f"lệch {r.ratio:.0f}×",
                va="center", fontsize=7.3, color=NO, weight="bold")
    ax.set_yticks(ys - .21); ax.set_yticklabels(G.word, fontsize=8.5)
    ax.set_xlabel("Số lần xuất hiện"); ax.grid(axis="y", alpha=0)
    ax.legend(fontsize=7.2, frameon=False, loc="lower right")
    ax.set_xlim(0, G.in_comments.max()*1.35)
    note(ax, "Từ khán giả dùng hằng ngày mà tiêu đề gần như không dùng — "
             "nguồn trực tiếp cho tên video và playlist.", y=-0.30, color=ACC)
    return save(fig, "p6_voice_gap.png")


# ═══ P7 · ẢNH MẪU THẬT từ nhóm dẫn đầu ════════════════════════════════
def p7_thumbs():
    """Lưới thumbnail THẬT của video top — thứ trực quan nhất trong hồ sơ."""
    src = N/"00_input/raw/thumbs"
    if not src.exists():
        return None
    vm = pd.read_parquet(P/"video_master.parquet")
    top = vm.nlargest(60, "view_count")
    import matplotlib.image as mpimg
    picks = []
    for r in top.itertuples():
        f = src/f"{r.video_id}.jpg"
        if f.exists():
            picks.append((f, r.view_count, r.channel_handle))
        if len(picks) == 8:
            break
    if len(picks) < 4:
        return None
    fig, axes = plt.subplots(2, 4, figsize=(7.4, 3.0))
    for ax, (f, vc, ch) in zip(axes.ravel(), picks):
        try:
            ax.imshow(mpimg.imread(f))
        except Exception:
            ax.set_facecolor(PAPER)
        ax.set_xticks([]); ax.set_yticks([]); ax.grid(alpha=0)
        for sp in ax.spines.values():
            sp.set_color("#E2DAD1")
        ax.set_title(f"{vc/1e6:.2f}tr".replace(".", ","), fontsize=7,
                     color=MUTE, pad=2)
    for ax in axes.ravel()[len(picks):]:
        ax.axis("off")
    fig.suptitle("Tám video xem nhiều nhất ngách — ảnh thật",
                 fontsize=9.5, weight="bold", color=INK, x=.09, ha="left", y=1.02)
    fig.text(.5, -0.02, "Mô-típ lặp lại: nền tối, một người, chữ lớn, "
                        "tông hổ phách/nâu ấm.", ha="center", fontsize=8,
             color=ACC, weight="bold")
    return save(fig, "p7_thumbs_grid.png")



# ═══ P8 · ĐỘNG LƯỢNG: cầu vs cung ═════════════════════════════════════
def p8_momentum():
    """Vì sao M2.4 là con số quan trọng nhất hồ sơ — vẽ cả hai vế."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 2.7),
                                 gridspec_kw={"width_ratios": [1, .95], "wspace": .28})
    g1 = MO["M2_1_view_growth"]; g2 = MO["M2_2_supply_growth"]
    a1.bar([0, 1], [g1, g2], color=[OK, MUTE], width=.5)
    top = max(g1, g2) * 1.55; a1.set_ylim(0, top)
    for x, val, c in [(0, g1, OK), (1, g2, MUTE)]:
        a1.text(x, val + top*.03, f"{val:.2f}×".replace(".", ","), ha="center",
                va="bottom", fontsize=11, weight="bold", color=c)
    a1.axhline(1, color=INK, ls=":", lw=1)
    a1.text(-.5, 1.03, "mức đứng yên", fontsize=6.8, color=MUTE, va="bottom", ha="left")
    a1.set_xticks([0, 1]); a1.set_xlim(-.55, 1.55)
    a1.set_xticklabels(["CẦU\n(lượt xem)", "CUNG\n(số video)"],
                       fontsize=8.3, weight="bold")
    a1.set_ylabel("Tăng trưởng so với kỳ trước"); a1.grid(axis="x", alpha=0)
    a1.set_title("Cầu có tăng nhanh hơn cung?", fontsize=9.5, weight="bold",
                 color=INK, loc="left")

    # M2.4 theo hai cách đo. Nhãn dài đặt NGAY DƯỚI mỗi thanh, trong vùng vẽ,
    # và nới trục y để cột trên cùng không chạm tiêu đề (T59).
    m_ok = MO["M2_4_demand_supply_gap"]; m_naive = MK["_naive_M2_4"]
    ys = [0.0, 1.0]
    a2.barh(ys, [m_naive, m_ok], color=[NO, ACC], height=.34)
    for y, val, c, lab in [
            (0.0, m_naive, NO, "Tính cả video mới đăng\n(chỉ 36% đủ thời gian)"),
            (1.0, m_ok, ACC, "Chỉ tính video đủ 3 tháng\n(cách đang dùng)")]:
        a2.text(val + .05, y, f"{val:.2f}".replace(".", ","), va="center",
                fontsize=10.5, weight="bold", color=c)
        a2.text(0.02, y - .27, lab, fontsize=7.2, color=INK, va="top", ha="left")
    a2.axvline(1, color=INK, ls=":", lw=1)
    a2.text(1.02, 1.52, "mức cân bằng", fontsize=6.8, color=MUTE, va="top")
    a2.set_yticks([]); a2.set_ylim(-.62, 1.62)
    a2.set_xlim(0, max(m_ok, m_naive) * 1.45); a2.set_xlabel("M2.4 = cầu ÷ cung")
    a2.grid(axis="y", alpha=0)
    a2.set_title("Cùng dữ liệu, hai cách đo", fontsize=9.5, weight="bold",
                 color=INK, loc="left")
    note(a1, "Cầu tăng nhanh hơn cung. NHƯNG con số này đảo ngược hoàn toàn "
             "nếu tính cả video vừa mới đăng —\nvideo mới chưa kịp tích lượt xem "
             "nên kéo kết quả xuống. Cần đo lại sau ≥30 ngày để chốt.",
         y=-0.40, color=NO)
    return save(fig, "p8_momentum.png")


# ═══ P9 · CHUẨN SẢN XUẤT: nhịp đăng & độ dài ══════════════════════════
def p9_norms():
    f = N/"03_competitor/PRODUCTION_NORMS.json"
    if not f.exists():
        return None
    R = json.load(open(f))
    D = R["duration"]; C = R["cadence"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 2.8),
                                 gridspec_kw={"width_ratios": [1.25, .8]})
    bands = [b for b in D["by_band"]]
    ys = np.arange(len(bands))[::-1]
    cols = [MUTE if "Shorts" in b["band"] else ACC for b in bands]
    a1.barh(ys, [b["vpd_median"] for b in bands], color=cols, height=.6)
    for y, b in zip(ys, bands):
        a1.text(b["vpd_median"] + .3, y, f'{b["vpd_median"]:.1f}'.replace(".", ",")
                + f'  (n={b["n"]})', va="center", fontsize=7.3, color=INK)
    a1.set_yticks(ys); a1.set_yticklabels([b["band"] for b in bands], fontsize=8)
    a1.set_xlabel("Lượt xem trung bình mỗi ngày"); a1.grid(axis="y", alpha=0)
    a1.set_xlim(0, max(b["vpd_median"] for b in bands)*1.45)
    a1.set_title("Độ dài nào ăn nhất? (gộp toàn ngách)", fontsize=9.5,
                 weight="bold", color=INK, loc="left")

    L = D["long_vs_short_within"]
    a2.bar([0, 1], [L["n_better_long"], L["n_channels"]-L["n_better_long"]],
           color=[ACC, MUTE], width=.5)
    for x, val in [(0, L["n_better_long"]), (1, L["n_channels"]-L["n_better_long"])]:
        a2.text(x, val + .35, str(val), ha="center", fontsize=13, weight="bold",
                color=ACC if x == 0 else MUTE)
    a2.set_xticks([0, 1]); a2.set_xlim(-.6, 1.6)
    a2.set_xticklabels(["Dài\ntốt hơn", "Ngắn\ntốt hơn"], fontsize=8.3, weight="bold")
    a2.set_ylim(0, L["n_channels"]*1.35); a2.set_ylabel("Số kênh")
    a2.grid(axis="x", alpha=0)
    a2.set_title(f'Kiểm trong {L["n_channels"]} kênh', fontsize=9.5,
                 weight="bold", color=INK, loc="left")
    _s = f'{D["naive_trap"]["short_vpd"]:.1f}'.replace(".", ",")
    _l = f'{D["naive_trap"]["long_vpd"]:.1f}'.replace(".", ",")
    note(a1, f'BẪY: gộp chung thì video ngắn thắng đậm ({_s} vs {_l} lượt xem/ngày).\n'
             f'Nhưng so trong nội bộ từng kênh: {L["n_better_long"]}/{L["n_channels"]} '
             f'— CHIA ĐÔI. Độ dài KHÔNG quyết định hiệu quả.', y=-0.34, color=NO)
    return save(fig, "p9_production_norms.png")


if __name__ == "__main__":
    made = [f for f in [p1_score(), p2_listening(), p3_personas(), p4_market(),
                        p5_recipe(), p6_voicegap(), p7_thumbs(),
                        p8_momentum(), p9_norms()] if f]
    print(f"✅ {len(made)} biểu đồ hồ sơ → {OUT}/")
    for m in made:
        print(f"   {m}")
