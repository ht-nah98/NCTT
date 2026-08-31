#!/usr/bin/env python3
"""Sinh MỘT PDF RIÊNG cho mỗi định vị kênh.

Khác build_positioning_pdf.py (bản tổng 8 trang, 4 hướng): file này sinh 7 tài
liệu độc lập, mỗi tài liệu 8-10 trang cho MỘT định vị, gồm:

  1. Bằng chứng định lượng — vì sao tin được (hoặc vì sao không)
  2. Danh sách VIDEO ĐỐI CHỨNG có video_id để tra tận nơi
  3. Kênh đang làm định vị này, xếp theo hiệu quả
  4. Bản thi công (nếu định vị đạt) hoặc phân tích vì sao hỏng (nếu không đạt)
  5. Cách tự kiểm chứng lại

Tên định vị theo chiều: NỘI DUNG NHẠC ↔ NHU CẦU NGƯỜI NGHE.

    python3 pipeline/report/build_positioning_cards.py [niche_path]
"""
import sys
import json
import pathlib
import re
import numpy as np
import pandas as pd
from scipy import stats
from weasyprint import HTML

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from _common import niche_root                                    # noqa: E402

N = niche_root()
OUT = N / "99_report" / "_dinh-vi"
OUT.mkdir(parents=True, exist_ok=True)
CRAWL = pd.Timestamp("2026-08-13", tz="UTC")


def vn(x, d=0):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    return f"{x:,.{d}f}".replace(",", "\x00").replace(".", ",").replace("\x00", ".")


# ── nạp và làm giàu ─────────────────────────────────────────────────────────
def load():
    P = N / "00_input/processed"
    v = pd.read_parquet(P / "videos.parquet")
    s = pd.read_parquet(P / "video_stats.parquet")
    ch = pd.read_parquet(P / "channels.parquet")
    v = v.merge(s[["video_id", "view_count"]], on="video_id", how="left")
    v = v.merge(ch[["channel_id", "handle"]], on="channel_id", how="left")
    v["age_days"] = (CRAWL - v.published_at).dt.days.clip(lower=1)
    v["vpd"] = v.view_count / v.age_days
    v["is_matured"] = v.age_days >= 60
    base = v[v.is_matured].groupby("channel_id").view_count.median()
    v["outlier_ratio"] = v.view_count / v.channel_id.map(base)
    cm = pd.read_parquet(P / "selected_comments.parquet")
    cm = cm[cm.text.astype(str).str.len() >= 15]
    return v, cm


V, CM = load()
M = V[V.is_matured].copy()
BASE_VPD = float(M.vpd.median())
BASE_LIKE = float(CM.like_count.median())


# ── ĐỊNH NGHĨA 7 ĐỊNH VỊ ────────────────────────────────────────────────────
# Tên theo chiều: NỘI DUNG NHẠC ↔ NHU CẦU NGƯỜI NGHE
POS = [
    dict(id="01", grp="A", code="P1",
         name="Nhạc tạ ơn sau biến cố",
         need="cho người vừa đi qua chuyện khó và muốn nói lời cảm ơn",
         title_pat=r"\bthank(?:ful|s|sgiving)?\b|\bgrateful\b|\bblessing",
         sig_pat=None),
    dict(id="02", grp="A", code="P2",
         name="Blues thật giữ nguyên đức tin",
         need="cho người mê Blues nhưng thấy lời Blues đời nghịch đức tin mình",
         title_pat=None,
         sig_pat=r"\bfinally\b|\bat last\b|\bbeen (?:looking|searching) for\b"),
    dict(id="03", grp="A", code="P2b",
         name="Kinh Thánh nghe lần đầu theo cách này",
         need="cho người mộ đạo lâu năm muốn nghe điều quen theo cách chưa từng nghe",
         title_pat=None,
         sig_pat=r"\bnever heard\b|\bnever found\b|\bfirst time i(?:'ve)? heard\b"),
    dict(id="04", grp="A", code="P3",
         name="Bài ca của một đời đã sống",
         need="cho người 60+ muốn nhìn lại cả chặng đường đức tin đã đi",
         title_pat=None,
         sig_pat=r"\bi(?:'m| am)\s+(?:6\d|7\d|8\d|9\d)\b|\b(?:6\d|7\d|8\d|9\d)\s*(?:years?\s*old|yrs)\b"),
    dict(id="05", grp="B", code="N1",
         name="Thánh Vịnh phổ nhạc Blues",
         need="cho người muốn nghe lời Kinh Thánh dưới dạng dễ tiếp nhận",
         title_pat=r"\bpsalm|\bproverb|\bscripture\b|\bword of god\b|\bbible\b",
         sig_pat=None),
    dict(id="06", grp="C", code="N2",
         name="Nhạc chữa lành chung chung",
         need="cho người đang buồn, đang đau — nhưng không nói rõ đau vì gì",
         title_pat=r"\bheal(?:ing|ed)?\b|\brestor",
         sig_pat=None),
    dict(id="07", grp="C", code="N3N4",
         name="Nhạc nền để ngủ và thư giãn",
         need="cho người cần âm thanh nền lúc ngủ, không nghe chủ động",
         title_pat=r"\bnight\b|\bsleep\b|\bmidnight\b|\binsomnia\b|\binstrumental\b|\bno lyrics\b|\bbackground\b",
         sig_pat=None),
]

GRP_META = {
    "A": ("NÊN LÀM", "#2D6A4F", "#E4EFE8",
          "Bằng chứng nội bộ ủng hộ. Đây là hướng đáng đầu tư."),
    "B": ("KHÓ — AI LÀM GIỎI THÌ ĂN", "#9A6700", "#FAF6EC",
          "Mặt bằng kém nhưng trong từng kênh lại tốt. Nghĩa là hướng này "
          "KHÔNG dễ, nhưng kênh nào làm đúng thì vẫn thắng."),
    "C": ("NÊN TRÁNH", "#8C2F39", "#F7EFEF",
          "Dữ liệu nói hướng này kém hơn mặt bằng rõ rệt, và kém cả trong "
          "từng kênh. Đông người làm không có nghĩa là ăn."),
}


# ── ĐO ĐẠC ──────────────────────────────────────────────────────────────────
def measure_title(pat):
    """Đo định vị theo TIÊU ĐỀ: lift VPD + kiểm Simpson trong từng kênh."""
    m = M.copy()
    m["hit"] = m.title.astype(str).str.lower().str.contains(pat, regex=True)
    a, b = m[m.hit], m[~m.hit]
    if len(a) < 20:
        return None
    p = float(stats.mannwhitneyu(a.vpd.dropna(), b.vpd.dropna()).pvalue)
    lift = float(a.vpd.median() / b.vpd.median())
    wc = []
    for _, g in m.groupby("channel_id"):
        if g.hit.sum() >= 5 and (~g.hit).sum() >= 5:
            vb = g[~g.hit].vpd.median()
            if vb > 0:
                wc.append(g[g.hit].vpd.median() / vb)
    return dict(kind="title", n=len(a), share=100 * len(a) / len(m),
                vpd=float(a.vpd.median()), vpd_other=float(b.vpd.median()),
                lift=lift, p=p, n_ch=len(wc),
                n_better=sum(1 for x in wc if x > 1),
                within=float(np.median(wc)) if wc else np.nan,
                n_channels=int(a.channel_id.nunique()),
                dur=float(a.duration_sec.median() / 60),
                tlen=float(a.title.str.len().median()),
                pct_num=100 * float(a.title.str.contains(r"\d").mean()),
                videos=a)


def measure_signal(pat):
    """Đo định vị theo TÍN HIỆU BÌNH LUẬN: like lift so nền."""
    h = CM[CM.text.str.lower().str.contains(pat, regex=True)]
    if len(h) < 30:
        return None
    rest = CM[~CM.index.isin(h.index)]
    p = float(stats.mannwhitneyu(h.like_count, rest.like_count).pvalue)
    vids = (h.groupby("video_id")
              .agg(n_sig=("comment_id", "size"), sig_likes=("like_count", "sum"))
              .reset_index()
              .merge(M[["video_id", "title", "handle", "view_count", "vpd",
                        "outlier_ratio", "duration_sec"]], on="video_id")
              .sort_values("n_sig", ascending=False))
    return dict(kind="signal", n=len(h),
                like=float(h.like_count.median()), base=BASE_LIKE,
                lift=float(h.like_count.median() / BASE_LIKE), p=p,
                n_videos=int(h.video_id.nunique()), vids=vids,
                quotes=h.nlargest(3, "like_count")[["text", "like_count"]]
                        .to_dict("records"))


def verdict_of(r):
    if r["kind"] == "signal":
        if r["p"] < 0.01 and r["lift"] >= 3:
            return "XÁC NHẬN", "ok"
        if r["p"] < 0.05 and r["lift"] >= 1.5:
            return "YẾU", "wa"
        return "BÁC BỎ", "no"
    if r["p"] >= 0.05:
        return "BÁC BỎ", "no"
    if r["n_ch"] >= 5 and r["within"] < 1:
        return "BÁC BỎ (Simpson)", "no"
    if r["lift"] >= 1.3 and (r["n_ch"] < 5 or r["within"] >= 1.1):
        return "XÁC NHẬN", "ok"
    if r["lift"] >= 1.15:
        return "YẾU", "wa"
    if r["lift"] <= 0.8:
        # mặt bằng kém NHƯNG trong-kênh tốt -> không phải "tránh"
        if r["n_ch"] >= 5 and r["within"] >= 1.1:
            return "KHÓ — TRONG KÊNH VẪN TỐT", "wa"
        return "TRÁNH", "no"
    return "BÁC BỎ", "no"


# ── DỰNG BẢNG VIDEO ĐỐI CHỨNG ───────────────────────────────────────────────
def video_table(df, n=14, sig_col=False):
    rows = []
    for _, r in df.head(n).iterrows():
        extra = f'<td class="n">{int(r.n_sig)}</td>' if sig_col else ""
        rows.append(
            f'<tr><td class="vid">{r.video_id}</td>{extra}'
            f'<td class="n">{vn(r.view_count)}</td>'
            f'<td class="n">{vn(r.vpd, 1)}</td>'
            f'<td class="n">{vn(r.outlier_ratio, 1)}×</td>'
            f'<td class="small">@{r.handle}</td>'
            f'<td class="ttl">{str(r.title)[:70]}</td></tr>')
    head = ("<th>video_id</th>"
            + ("<th class='n'>tín hiệu</th>" if sig_col else "")
            + "<th class='n'>view</th><th class='n'>vpd</th>"
              "<th class='n'>vs kênh</th><th>kênh</th><th>tiêu đề</th>")
    return (f'<div class="scroll"><table class="vt"><thead><tr>{head}</tr>'
            f'</thead><tbody>{"".join(rows)}</tbody></table></div>')


def channel_table(df, n=8):
    g = (df.groupby("handle")
           .agg(n=("video_id", "size"), vpd=("vpd", "median"),
                view=("view_count", "median"))
           .query("n >= 3").nlargest(n, "vpd"))
    rows = "".join(
        f'<tr><td class="w">@{i}</td><td class="n">{int(r.n)}</td>'
        f'<td class="n">{vn(r.vpd, 1)}</td><td class="n">{vn(r.view)}</td></tr>'
        for i, r in g.iterrows())
    return (f'<table><thead><tr><th>Kênh</th><th class="n">Số video</th>'
            f'<th class="n">VPD trung vị</th><th class="n">View trung vị</th>'
            f'</tr></thead><tbody>{rows}</tbody></table>')


# ── CSS chung ───────────────────────────────────────────────────────────────
def css(accent, soft):
    return f"""
@page {{ size:A4; margin:18mm 16mm 20mm;
  @bottom-left {{ content:"Định vị {{}} · christian-blues"; font-family:"DejaVu Sans";
    font-size:7pt; color:#9A8E85; }}
  @bottom-right {{ content counter(page) " / " counter(pages);
    font-family:"DejaVu Sans"; font-size:7.5pt; color:#9A8E85; }} }}
@page :first {{ @bottom-left {{ content:""; }} @bottom-right {{ content:""; }} }}
body {{ font-family:"DejaVu Sans",sans-serif; font-size:9.5pt; line-height:1.55;
  color:#1C1917; }}
h1 {{ font-size:23pt; line-height:1.14; margin:0 0 6pt; letter-spacing:-.4pt; }}
h2 {{ font-size:10.5pt; margin:19pt 0 8pt; padding-bottom:4pt; color:{accent};
  border-bottom:1.5pt solid #1C1917; page-break-after:avoid;
  text-transform:uppercase; letter-spacing:.6pt; }}
h3 {{ font-size:10pt; margin:12pt 0 4pt; page-break-after:avoid; }}
p {{ margin:6pt 0; }} i {{ font-style:italic; }}
.cover {{ padding-top:44mm; page-break-after:always; }}
.eyebrow {{ font-size:8pt; letter-spacing:1.4pt; text-transform:uppercase;
  color:#78716C; margin-bottom:10pt; }}
.need {{ font-size:12pt; color:#57534E; font-style:italic; margin:8pt 0 0;
  max-width:120mm; line-height:1.5; }}
.badge {{ display:inline-block; background:{soft}; color:{accent};
  border:1pt solid {accent}; border-radius:3pt; padding:4pt 10pt;
  font-size:9pt; font-weight:bold; letter-spacing:.5pt; margin:14pt 0 0; }}
.rule {{ border:0; border-top:1.5pt solid #1C1917; margin:14pt 0; width:66mm; }}
.covmeta {{ font-size:8.5pt; color:#78716C; line-height:1.8; }}
.covmeta b {{ color:#1C1917; }}
table {{ border-collapse:collapse; width:100%; font-size:8.5pt; margin:7pt 0; }}
table tr {{ page-break-inside:avoid; }}
th {{ background:#F5F2ED; text-align:left; padding:5pt 6pt; font-size:7.5pt;
  text-transform:uppercase; letter-spacing:.4pt; color:#57534E;
  border-bottom:1pt solid #D6CEC4; }}
td {{ padding:4.5pt 6pt; border-bottom:.6pt solid #EDE7E0; vertical-align:top; }}
td.n {{ text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }}
td.w {{ font-weight:bold; }}
td.vid {{ font-family:"DejaVu Sans Mono",monospace; font-size:7.5pt; }}
td.ttl {{ font-size:8pt; color:#44403C; }}
td.small, .small {{ font-size:8pt; color:#78716C; }}
.scroll {{ margin:7pt 0; }}
.ok {{ color:#2D6A4F; font-weight:bold; }}
.no {{ color:#8C2F39; font-weight:bold; }}
.wa {{ color:#9A6700; font-weight:bold; }}
.box {{ border-left:2.5pt solid {accent}; background:{soft}; padding:8pt 11pt;
  margin:9pt 0; page-break-inside:avoid; }}
.box.plain {{ border-left-color:#A8A29E; background:#F7F5F2; }}
.box h4 {{ font-size:9.5pt; margin:0 0 4pt; }}
.box p {{ margin:4pt 0 0; }}
.kpi {{ display:table; width:100%; margin:8pt 0; border-collapse:separate;
  border-spacing:5pt 0; }}
.kpi > div {{ display:table-cell; width:25%; background:#F7F5F2;
  border-radius:3pt; padding:8pt 9pt; text-align:center; }}
.kpi .v {{ font-size:15pt; font-weight:bold; font-variant-numeric:tabular-nums; }}
.kpi .l {{ font-size:7pt; letter-spacing:.5pt; text-transform:uppercase;
  color:#78716C; margin-top:2pt; }}
.q {{ border-left:2pt solid {accent}; padding:5pt 0 5pt 9pt; margin:7pt 0 0;
  font-size:8.5pt; font-style:italic; color:#44403C; page-break-inside:avoid; }}
.q .a {{ display:block; margin-top:3pt; font-style:normal; font-size:7.5pt;
  color:#9A8E85; }}
/* page-break-inside:avoid để chân trang không tràn sang trang mới chỉ vì
   thiếu vài dòng — bài học T88 */

/* ── KHUNG CHO TỪNG MỤC ──────────────────────────────────────────────
   Mỗi mục là một thẻ có viền. KHÔNG dùng page-break-inside:avoid cho
   .sect vì thẻ cao hơn nửa trang sẽ sinh trang trắng (bài học T88);
   chỉ giữ tiêu đề dính với dòng đầu. */
.sect {{ border:.7pt solid #E3DDD5; border-radius:3pt; background:#FEFDFB;
  margin:11pt 0; }}
.stitle {{ background:{soft}; color:{accent}; font-size:9pt; font-weight:bold;
  letter-spacing:.7pt; text-transform:uppercase; padding:6pt 12pt;
  border-bottom:.7pt solid #E3DDD5; border-radius:3pt 3pt 0 0;
  page-break-after:avoid; }}
.sbody {{ padding:9pt 12pt 11pt; }}
.sbody > table {{ margin-top:0; }}
.sbody > p:first-child {{ margin-top:0; }}
.sbody > p:last-child {{ margin-bottom:0; }}
.idea {{ background:{soft}; border-radius:2pt; padding:8pt 10pt; margin:0 0 8pt;
  font-size:9.5pt; line-height:1.55; }}
.warnbox {{ background:#FAF6EC; border-left:2.5pt solid #9A6700;
  border-radius:0 2pt 2pt 0; padding:7pt 10pt; margin:9pt 0 0; font-size:8.5pt; }}
.divider {{ border-top:2pt solid #1C1917; margin:18pt 0 11pt; padding-top:9pt;
  page-break-after:avoid; }}
.dtitle {{ font-size:11pt; font-weight:bold; letter-spacing:.6pt;
  text-transform:uppercase; color:#1C1917; margin-bottom:3pt; }}
.divider p {{ font-size:8.5pt; color:#78716C; margin:0; }}
.tf {{ font-size:9pt; line-height:1.7; }}
.foot {{ margin-top:15pt; padding-top:8pt; border-top:1.5pt solid #1C1917;
  font-size:7.5pt; color:#78716C; line-height:1.65;
  page-break-inside:avoid; }}
.foot code {{ font-family:"DejaVu Sans Mono",monospace; font-size:7pt;
  color:#44403C; }}
"""


def kpi(items):
    return ('<div class="kpi">' + "".join(
        f'<div><div class="v">{v}</div><div class="l">{l}</div></div>'
        for v, l in items) + '</div>')


# ── DỰNG MỘT TÀI LIỆU ───────────────────────────────────────────────────────
def build(pos):
    label, accent, soft, grp_desc = GRP_META[pos["grp"]]
    r = (measure_title(pos["title_pat"]) if pos["title_pat"]
         else measure_signal(pos["sig_pat"]))
    if r is None:
        print(f"   ⚠ bỏ qua {pos['id']}: không đủ mẫu")
        return None
    verdict, vcls = verdict_of(r)

    # ── §1 BẰNG CHỨNG ───────────────────────────────────────────────────
    if r["kind"] == "title":
        k = kpi([(vn(r["n"]), "video"), (f'{vn(r["lift"],2)}×', "so mặt bằng"),
                 (vn(r["n_channels"]), "kênh đang làm"),
                 (f'{vn(r["within"],2)}×', "trong từng kênh")])
        ev = f"""{k}
<table><thead><tr><th>Phép đo</th><th class="n">Giá trị</th><th>Đọc là</th></tr></thead><tbody>
<tr><td class="w">Số video mang định vị</td><td class="n">{vn(r['n'])}</td>
    <td>{vn(r['share'],1)}% thị trường ({vn(r['n_channels'])} kênh)</td></tr>
<tr><td class="w">VPD nhóm này</td><td class="n">{vn(r['vpd'],2)}</td>
    <td>view mỗi ngày, tính trên video đã đủ 60 ngày</td></tr>
<tr><td class="w">VPD nhóm còn lại</td><td class="n">{vn(r['vpd_other'],2)}</td>
    <td>mặt bằng để so</td></tr>
<tr><td class="w">Chênh lệch (lift)</td><td class="n"><b>{vn(r['lift'],2)}×</b></td>
    <td class="{vcls}">{'cao hơn' if r['lift']>1 else 'THẤP HƠN'} mặt bằng</td></tr>
<tr><td class="w">p-value</td><td class="n">{r['p']:.2e}</td>
    <td>{'có ý nghĩa thống kê' if r['p']<0.05 else 'KHÔNG có ý nghĩa'}</td></tr>
<tr><td class="w">Kiểm trong từng kênh</td>
    <td class="n"><b>{vn(r['within'],2)}×</b></td>
    <td>{r['n_better']}/{r['n_ch']} kênh làm định vị này tốt hơn chính mình</td></tr>
</tbody></table>

<div class="box"><h4>Vì sao phải kiểm trong từng kênh</h4>
<p>Chỉ số lift thô có thể đánh lừa: nếu vài kênh mạnh tình cờ hay làm định vị
này, con số sẽ đẹp dù bản thân định vị không có tác dụng. Kiểm trong từng kênh
hỏi câu khác: <i>"cùng một kênh, khi làm định vị này có thắng chính mình không?"</i></p>
<p>Ở đây: <b>{r['n_better']}/{r['n_ch']} kênh</b> tốt hơn, trung vị
<b>{vn(r['within'],2)}×</b>.
{'Hiệu ứng nhất quán — tin được.' if not np.isnan(r['within']) and r['within']>=1.1
 else 'Hiệu ứng KHÔNG nhất quán — phần lớn lift thô đến từ việc kênh nào làm, không phải từ định vị.'}</p></div>"""
    else:
        k = kpi([(vn(r["n"]), "bình luận"), (f'{vn(r["lift"],1)}×', "so nền"),
                 (vn(r["like"],0), "like trung vị"),
                 (vn(r["n_videos"]), "video dính")])
        ev = f"""{k}
<table><thead><tr><th>Phép đo</th><th class="n">Giá trị</th><th>Đọc là</th></tr></thead><tbody>
<tr><td class="w">Bình luận mang tín hiệu</td><td class="n">{vn(r['n'])}</td>
    <td>trên {vn(len(CM))} bình luận đã lọc</td></tr>
<tr><td class="w">Like trung vị nhóm này</td><td class="n"><b>{vn(r['like'],1)}</b></td>
    <td>người khác đọc và đồng tình</td></tr>
<tr><td class="w">Like nền của ngách</td><td class="n">{vn(r['base'],1)}</td>
    <td>mốc để so</td></tr>
<tr><td class="w">Chênh lệch</td><td class="n"><b>{vn(r['lift'],1)}×</b></td>
    <td class="{vcls}">gấp {vn(r['lift'],1)} lần nền</td></tr>
<tr><td class="w">p-value</td><td class="n">{r['p']:.2e}</td>
    <td>{'có ý nghĩa thống kê' if r['p']<0.05 else 'KHÔNG có ý nghĩa'}</td></tr>
<tr><td class="w">Số video dính tín hiệu</td><td class="n">{vn(r['n_videos'])}</td>
    <td>xem danh sách ở mục 9</td></tr>
</tbody></table>

<div class="box"><h4>Vì sao đo bằng LIKE chứ không đếm số lần xuất hiện</h4>
<p>Tần suất chỉ đo <i>"có người nói"</i>. Like đo <i>"người khác đọc và gật đầu"</i>.
Hai thứ khác nhau, và thứ hai mới đáng tin.</p>
<p class="small">Ví dụ đối chứng trong chính ngách này: cụm về «chữa lành» xuất
hiện nhiều gấp hàng chục lần cụm «finally», nhưng like trung vị chỉ 3 so với nền
4 — nói nhiều mà không ai đồng tình đặc biệt.</p></div>"""

    # ── §2 VIDEO ĐỐI CHỨNG ──────────────────────────────────────────────
    if r["kind"] == "title":
        top = r["videos"].nlargest(14, "vpd")
        worst = r["videos"].nsmallest(6, "vpd")
        vids = f"""<p>Đây là các video <b>đang làm đúng định vị này</b>, xếp theo
VPD (view mỗi ngày). Tra bằng <code>youtube.com/watch?v=&lt;video_id&gt;</code>.</p>
{video_table(top, 14)}
<h3>Và đây là nhóm làm cùng định vị nhưng THẤT BẠI</h3>
<p class="small">Quan trọng ngang danh sách trên: cùng định vị, cùng ngách, nhưng
VPD rất thấp. So hai nhóm để thấy định vị đúng chưa đủ — thực thi mới quyết định.</p>
{video_table(worst, 6)}"""
    else:
        good = r["vids"][r["vids"].n_sig >= 2]
        vids = f"""<p>Đây là video <b>có khán giả để lại bình luận mang đúng tín
hiệu này</b> — bằng chứng trực tiếp rằng định vị chạm đúng nhu cầu. Cột «tín hiệu»
là số bình luận khớp. Tra bằng <code>youtube.com/watch?v=&lt;video_id&gt;</code>.</p>
{video_table(good, 14, sig_col=True)}
<p class="small">Có <b>{len(r['vids'])}</b> video dính tín hiệu này;
<b>{len(good)}</b> video có từ 2 bình luận trở lên.</p>"""

    # ── §3 KÊNH ─────────────────────────────────────────────────────────
    src = r["videos"] if r["kind"] == "title" else r["vids"]
    chans = f"""<p>Kênh nào đang làm định vị này hiệu quả nhất — dùng để tham
khảo cách họ đóng gói.</p>
{channel_table(src)}"""

    # ── §4 TRÍCH DẪN (chỉ cho định vị theo tín hiệu) ────────────────────
    quotes = ""
    if r["kind"] == "signal":
        qs = "".join(
            f'<div class="q">“{" ".join(str(q["text"]).split())[:230]}”'
            f'<span class="a">{vn(q["like_count"])} lượt thích</span></div>'
            for q in r["quotes"])
        quotes = card("13 · Khán giả nói gì",
                      '<p class="small">Trích dẫn đã bỏ định danh. Bằng chứng '
                      'định tính đi kèm số liệu ở mục 8.</p>' + qs)

    return dict(pos=pos, r=r, verdict=verdict, vcls=vcls, label=label,
                accent=accent, soft=soft, grp_desc=grp_desc,
                ev=ev, vids=vids, chans=chans, quotes=quotes)


# ── §5 BẢN THI CÔNG / PHÂN TÍCH VÌ SAO HỎNG ─────────────────────────────────
# ── BẢN KHỞI TẠO KÊNH — đủ 7 định vị ────────────────────────────────────────
# Mỗi định vị là một bản thi công hoàn chỉnh: ý tưởng · khách hàng · thumbnail ·
# âm nhạc · cấu trúc · tiêu đề · lịch đăng · 10 video đầu · điều kiện dừng.
# Định vị TRÁNH cũng có bản thi công — dưới dạng "nếu vẫn muốn test thì làm sao".

BUILD = {
"01": dict(
 idea="Bài hát viết cho người <b>đã qua</b> chuyện khó, không phải người "
      "<b>đang ở trong</b> chuyện khó.<br><br>"
      "Cùng một người bệnh nặng, có hai thời điểm khác nhau: lúc còn nằm viện "
      "thì họ cần được an ủi — đó là loại nhạc thị trường đang làm rất nhiều. "
      "Lúc đã khỏi và nhìn lại, họ cần một chỗ để <b>nói lời cảm ơn</b> — đó là "
      "chỗ gần như còn trống.<br><br>"
      "Khác biệt nghe được ngay trong lời: "
      "<i>«Lạy Chúa, con đang đau, xin ở cùng con»</i> (đang trong) so với "
      "<i>«Cảm ơn Chúa đã đưa con qua»</i> (đã qua). "
      "Hướng này làm vế thứ hai.",
 customer="Người vừa đi qua chuyện khó (bệnh, mất mát, khủng hoảng) và đã ổn "
          "hơn. Họ không cần được an ủi nữa — họ cần một chỗ để nói cảm ơn.",
 persona="Nam/nữ 50–75, đã qua biến cố, đức tin được củng cố chính nhờ biến cố đó.",
 thumb=[("Nhân vật","Nhánh «ông già blues» nhưng <b>đổi biểu cảm</b>: mắt MỞ, "
        "ngẩng nhìn lên, mỉm cười nhẹ. Đây là điểm khác biệt cốt lõi — phần còn "
        "lại của thị trường dùng mắt nhắm đau đớn."),
        ("Đạo cụ","Micro cổ điển Shure 55, hoặc hai bàn tay mở ngửa. Bỏ guitar nếu đã có micro."),
        ("Ánh sáng","Chiaroscuro nhưng <b>nâng sáng hơn chuẩn ngách</b>: vùng tối "
        "~50% thay vì 61%. Nguồn hổ phách xiên từ trên cao, gợi ánh sáng cửa sổ nhà thờ."),
        ("Màu","Nền đen #000000 · sáng hổ phách #E8B84B · <b>tuyệt đối tránh xanh lạnh</b> "
        "(nhóm thua dùng 10,3%, nhóm top chỉ 0,7%)"),
        ("Bố cục","Một người, chiếm 21–35% khung, lệch 1/3 trái hoặc phải. Mặt rõ, nửa trên."),
        ("Chữ","3 dòng, tổng 12–25% khung. Dòng 1 là <b>câu cảm tạ</b>, không phải tên thể loại.")],
 music=[("Điệu thức","<b>Trưởng</b> — thị trường đã 201/307 bài là trưởng; hướng này đẩy hẳn về trưởng, bỏ thứ"),
        ("Tempo","88 BPM (trung vị ngách). Có thể nhích 92–100 cho cảm giác nhẹ nhõm"),
        ("Swing","1,32 — giữ chất blues shuffle, đừng làm thẳng nhịp"),
        ("Nhạc cụ","Guitar + bass + trống + <b>piano</b>. Tổ hợp <i>bass·drums·guitar·piano·vocals</i> dày nhất nhóm dẫn đầu"),
        ("Điểm nhấn","Organ Hammond hoặc bè hợp xướng nhỏ ở đoạn cuối — choir chỉ 5% bài, chỗ trống dễ tạo dấu ấn"),
        ("Độ ồn","−13,8 LUFS · LRA 6,6 — chuẩn ngách, đừng nén chặt hơn")],
 struct=[("Độ dài bài","3:54 · khoảng 3:22–4:40"),
        ("Mở đầu","Khối đầu ~21 giây. Guitar đơn hoặc piano đơn vào trước"),
        ("Giọng vào","<b>Giây thứ 4</b> — trung vị ngách. Intro quá 20 giây đã là chậm"),
        ("Số khối","13 khối, mỗi khối ~19,5 giây (khoảng 8 nhịp)"),
        ("Cao trào","Ở <b>71% bài</b> — khoảng phút 2:45 của bài 3:54")],
 title=("<b>Dòng 1 — câu cảm tạ, viết như lời người nghe nói:</b><br>"
        "“THANK YOU LORD FOR BRINGING ME THROUGH” · “HE DID IT AGAIN” · “I MADE IT OVER”<br><br>"
        "<b>Dòng 2:</b> “Gospel Blues” · “Songs of Thanksgiving”<br>"
        "<b>Dòng 3:</b> tên kênh, chữ nghiêng, góc dưới"),
 avoid="Đừng làm mặt đau khổ mắt nhắm nghiền — đó là hình ngôn của hướng «than "
       "thở» đã bão hoà. Đừng dùng điệu thứ. Đừng đặt tiêu đề bắt đầu bằng «Sad» hay «Broken»."),

"02": dict(
 idea="Bán cảm giác <b>«cuối cùng cũng tìm thấy»</b>, không bán nỗi buồn.<br><br>"
      "Có một nhóm người yêu nhạc Blues thật — tiếng guitar điện, harmonica, "
      "nhịp shuffle nặng. Nhưng lời Blues đời thường nói về rượu, phản bội, dục "
      "vọng, nên họ nghe mà thấy nghịch với đức tin mình. Ngược lại, nhạc "
      "Christian trên radio thì lời hợp nhưng nhạc quá nhẹ, không đủ chất.<br><br>"
      "Họ kẹt giữa hai bên và <b>không tìm được thứ vừa ý</b>. Hướng này làm "
      "đúng thứ đó: nhạc Blues thật, lời giữ đức tin. Bằng chứng nằm ngay trong "
      "bình luận — 65 người dùng cụm «finally», «at last» khi tìm thấy, và những "
      "bình luận đó được thích gấp 5,2 lần mức thường.",
 customer="Người yêu Blues/Soul thật, khó tính về chất nhạc, nhưng thấy lời "
          "Blues đời (rượu, phản bội, dục vọng) không hợp đức tin mình.",
 persona="Nam 45–70, từng chơi nhạc hoặc nghe Blues lâu năm, mộ đạo.",
 thumb=[("Nhân vật","<b>Nhạc công thật</b>, không phải ca sĩ thờ phượng. Nam da đen "
        "50–70, ôm guitar bán rỗng (hollow-body), ngón tay đang bấm phím rõ nét."),
        ("Đạo cụ","Guitar là <b>nhân vật chính</b> — để nó chiếm chỗ ngang người. "
        "Harmonica, ampli đèn cũ. Thánh giá nhỏ ở nền, không phô."),
        ("Ánh sáng","Chuẩn ngách 61% tối, thêm <b>khói và đèn sân khấu</b> — "
        "không gian quán blues, không phải nhà thờ."),
        ("Màu","Nền đen · hổ phách đậm · <b>1/6 số ảnh làm đen trắng hoàn toàn</b> "
        "(16,6% ngách đã làm vậy — hợp hướng này nhất)"),
        ("Bố cục","Cận trung, thấy được tay và mặt. Bokeh mạnh (nét giữa gấp ~2× nét biên)."),
        ("Chữ","Sans-serif đậm viền đen, IN HOA. Hoặc chữ khối kim loại vàng kiểu retro.")],
 music=[("Điệu thức","<b>Thứ</b> — hướng DUY NHẤT nên dùng thứ, vì chất Blues thật đòi hỏi. Thang blues có nốt xanh rõ"),
        ("Tempo","76–88 BPM, chậm. Slow blues 12 ô nhịp"),
        ("Swing","Đẩy lên <b>trên 1,32</b> — shuffle nặng, đây là dấu hiệu phân biệt Blues thật với worship nhẹ đội lốt"),
        ("Nhạc cụ","<b>Guitar điện</b> (chỉ 5% ngách dùng — chỗ trống rõ) + bass + trống thật + harmonica + organ. Tránh synth pad"),
        ("Điểm nhấn","Slide guitar (4% ngách). <b>Solo guitar thật</b> giữa bài — thị trường gần như không ai làm"),
        ("Độ ồn","−13,8 LUFS nhưng để LRA rộng hơn 6,6 — nhạc thật cần dải động")],
 struct=[("Độ dài bài","4:30–6:00, dài hơn chuẩn vì cần chỗ cho solo"),
        ("Mở đầu","<b>Guitar đơn 15–20 giây</b> — tổ hợp mở đầu phổ biến nhất ngách (41/307 bài). Đây là chỗ khoe chất"),
        ("Giọng vào","Chậm hơn chuẩn: giây 15–20, sau khi guitar đã nói xong câu đầu"),
        ("Số khối","13–16. Chèn 1 khối instrumental làm solo ở khoảng 60% bài"),
        ("Cao trào","71% bài — sau solo, giọng quay lại mạnh nhất")],
 title=("<b>Dòng 1 — khoảnh khắc tìm thấy:</b><br>"
        "“THE BLUES I'VE BEEN LOOKING FOR” · “REAL BLUES, CLEAN HEART” · “BLUES THAT HONORS HIM”<br><br>"
        "<b>Dòng 2:</b> “Slow Blues” · “Delta Gospel” — dùng từ chuyên môn để báo hiệu chất thật<br><br>"
        "<b>Thẻ tag bắt buộc:</b> <i>slow blues · delta blues · blues guitar</i> — "
        "ba thẻ chỉ xuất hiện ở nhóm thắng"),
 avoid="Đừng làm nhạc nền ambient hay «relaxing». Đừng dùng trống máy — nhóm này "
       "nghe ra ngay. Đừng đặt tiêu đề kiểu playlist («3 Hours of…»)."),

"03": dict(
 idea="Lấy thứ khán giả đã thuộc lòng (Kinh Thánh) và trình bày theo cách họ "
      "chưa từng nghe. Điểm bán không phải nội dung — mà là <b>góc nhìn mới trên "
      "nội dung quen</b>.",
 customer="Người mộ đạo lâu năm, thuộc Kinh Thánh, đã nghe hàng nghìn bài "
          "worship. Họ không cần biết thêm nội dung — họ cần một cảm giác mới.",
 persona="Nam/nữ 55–80, đi nhà thờ đều, đọc Kinh Thánh hằng ngày.",
 thumb=[("Nhân vật","Nhạc công ôm guitar, đa dạng sắc tộc và tuổi. Hoặc không cần "
        "nhân vật — cuốn Kinh Thánh cũ dưới ánh sáng cửa sổ kính màu."),
        ("Bối cảnh","<b>NGOÀI TRỜI</b> — nhà thờ gỗ, đồng cỏ, vườn ô-liu, mưa. "
        "Đây là công thức của @holygrooveofficial, kênh dẫn đầu hướng này."),
        ("Ánh sáng","Tự nhiên, ngả chiều. Không cần chiaroscuro gắt như hướng 02."),
        ("Màu","Nền tối vừa, hổ phách. Tránh xanh lạnh."),
        ("Bố cục","Cảnh rộng hơn các hướng khác — bối cảnh cũng là nhân vật."),
        ("Chữ","Trắng viền đen, IN HOA, chiếm nguyên dải trên. "
        "<b>Gạch chân đỏ</b> dưới một phần tiêu đề (dấu hiệu nhận diện của kênh dẫn đầu).")],
 music=[("Điệu thức","Trưởng hoặc thứ đều được — khác biệt nằm ở <b>cách trình bày</b>, không ở điệu thức"),
        ("Tempo","76–95 BPM"),
        ("Nhạc cụ","Guitar + organ + bè. Giữ chất Blues nhưng không cần solo dài như hướng 02"),
        ("Điểm mấu chốt","Lời phải bám <b>nguyên văn hoặc sát nghĩa</b> đoạn Kinh Thánh — "
        "khán giả nhóm này thuộc lòng và sẽ nhận ra ngay nếu chế"),
        ("Độ ồn","−13,8 LUFS chuẩn ngách")],
 struct=[("Độ dài bài","4:00–6:00"),
        ("Cấu trúc","Nếu là Thánh Vịnh: giữ đúng thứ tự câu, đừng đảo"),
        ("Giọng vào","Giây 10–15"),
        ("Cao trào","71% bài")],
 title=("<b>Công thức đã kiểm chứng — câu hỏi giả định:</b><br>"
        "“What If David Played Guitar Instead of Harp?”<br>"
        "“The Book of Isaiah sung in Blues will shock you!”<br>"
        "“This Psalm Sounds Like It Was Born in the Blues”<br><br>"
        "<b>Vì sao công thức này thắng:</b> nó biến điều quen thành câu hỏi. "
        "Nhóm đáy của cùng hướng đặt tiêu đề mô tả trần trụi («Psalm 23 Lyrics») "
        "và có VPD thấp hơn hàng chục lần."),
 avoid="Đừng đặt tiêu đề dạng tra cứu («Psalm 91 | Lyrics | 1 Hour»). Đừng đọc "
       "nguyên văn trên nền nhạc — phải là bài hát thật."),

"04": dict(
 idea="Bài hát kể lại <b>cả một đời đã sống</b>, ở ngôi thứ nhất.<br><br>"
      "Đây là chỗ trống rõ nhất của ngách. Thumbnail thị trường đầy hình người "
      "già — 91% ảnh nhóm dẫn đầu có mặt người, phần lớn là ông cụ da đen tóc "
      "bạc. Nhưng <b>lời bài hát</b> lại không viết cho họ: vẫn là những câu "
      "cầu xin chung chung, không phải lời của người đã đi hết chặng đường.<br><br>"
      "Nói ngắn gọn: thị trường đã <b>vẽ</b> đúng người nghe nhưng chưa <b>nói</b> "
      "đúng tiếng của họ. Bằng chứng: 65 bình luận có người tự khai tuổi 60–90, "
      "và nhóm này được thích gấp 4 lần mức thường.",
 customer="Người 60–90 tuổi, đức tin lâu năm, muốn nhìn lại cả chặng đường đã đi. "
          "Đây là nhóm tương tác mạnh nhất ngách (like gấp 4× nền).",
 persona="Nam/nữ 65–85, đã nghỉ hưu, con cháu đã lớn, nhiều thời gian nghe nhạc.",
 thumb=[("Nhân vật","Nhánh A nhưng <b>già hơn và tĩnh hơn</b>: 70–85, ngồi, tay "
        "đặt trên Kinh Thánh cũ hoặc thành ghế. Không hát — đang <b>nhớ lại</b>."),
        ("Đạo cụ","Kinh Thánh sờn gáy · ảnh gia đình cũ · ghế bập bênh gỗ · kính lão. "
        "<b>Bỏ micro và guitar</b> — đây không phải cảnh biểu diễn."),
        ("Ánh sáng","Ánh chiều muộn qua cửa sổ, hổ phách rất ấm. Giữ 61% tối nhưng "
        "bóng mềm hơn, ít tương phản gắt."),
        ("Màu","<b>Nâu hổ phách #402000 làm chủ đạo</b> thay vì đen tuyền — tông ảnh cũ, ngả sepia."),
        ("Bố cục","Toàn thân hoặc bán thân, nhân vật nhỏ hơn chuẩn (21–27%), "
        "chừa không gian trống gợi sự tĩnh lặng."),
        ("Chữ","<b>Serif cổ điển</b>, không phải sans đậm. Chữ nhỏ hơn chuẩn, khiêm nhường.")],
 music=[("Điệu thức","Trưởng, nhưng chậm và trầm. Hoà âm đơn giản, ít biến đổi"),
        ("Tempo","<b>70–80 BPM</b>, chậm hơn chuẩn ngách. Nhịp đi bộ của người già"),
        ("Swing","Nhẹ, khoảng 1,2 — đừng shuffle nặng, không hợp giọng kể chuyện"),
        ("Nhạc cụ","<b>Guitar thùng</b> (12% ngách) + piano + bass đứng (12%). "
        "Bỏ trống hoặc chỉ dùng brush rất nhẹ"),
        ("Giọng hát","Giọng khàn, có tuổi. Đây là hướng mà chất giọng già là <b>ưu điểm</b>"),
        ("Độ ồn","−14 LUFS, để dải động rộng cho những đoạn thì thầm")],
 struct=[("Độ dài bài","4:00–5:00, thong thả"),
        ("Mở đầu","Guitar thùng đơn hoặc piano đơn, 20–25 giây. Chậm rãi"),
        ("Giọng vào","Giây 15–22 — chậm, để người nghe kịp lắng xuống"),
        ("Số khối","10–12, ít hơn chuẩn. Cấu trúc đơn giản, lặp lại nhiều"),
        ("Cao trào","Nhẹ, ở 71% bài — hướng này <b>không</b> cần cao trào mạnh")],
 title=("<b>Lời chứng ở ngôi thứ nhất:</b><br>"
        "“I'VE COME THIS FAR BY FAITH” · “EIGHTY YEARS OF MERCY” · “HE NEVER LEFT ME”<br><br>"
        "<b>Dùng con số tuổi trong tiêu đề</b> — 33% tiêu đề nhóm này đã có chứa số, "
        "và với hướng này con số là bằng chứng của một đời."),
 avoid="Đừng làm nhạc sôi động. Đừng dùng nhân vật trẻ. Đừng đặt tiêu đề kiểu "
       "khích lệ («Rise Up», «Victory») — nhóm này đang nhìn lại, không đang chiến đấu."),

"05": dict(
 idea="Thánh Vịnh phổ nhạc Blues. Hướng ĐÔNG THỨ HAI toàn ngách (652 video, 30 kênh) "
      "và mặt bằng kém — nhưng <b>13/18 kênh làm tốt hơn chính mình</b>. Nghĩa là "
      "hướng này không xấu, nó chỉ <b>khó</b>: bạn phải giỏi hơn mức trung bình.",
 customer="Người muốn nghe lời Kinh Thánh dưới dạng dễ tiếp nhận. Nhóm này rộng "
          "nhưng đã bị phục vụ nhiều — muốn vào phải khác biệt rõ.",
 persona="Nam/nữ 50–75, đọc Kinh Thánh, thích nghe khi lái xe hoặc làm việc nhà.",
 thumb=[("Cảnh báo","Đây là hướng đông kênh nhất sau «chữa lành». Thumbnail giống "
        "phần còn lại = chìm ngay."),
        ("Nhân vật","Nhạc công ôm guitar ngoài trời (công thức @holygrooveofficial), "
        "hoặc cuốn Kinh Thánh cũ dưới ánh sáng cửa sổ."),
        ("Bối cảnh","<b>Ngoài trời</b> — điểm khác biệt với đa số làm trong nhà thờ."),
        ("Màu","Nền tối vừa, hổ phách. Tránh xanh lạnh."),
        ("Chữ","Trắng viền đen IN HOA, gạch chân đỏ dưới một phần tiêu đề.")],
 music=[("Điệu thức","Trưởng hoặc thứ. Chất lượng sản xuất quan trọng hơn điệu thức ở hướng này"),
        ("Tempo","76–95 BPM"),
        ("Nhạc cụ","Guitar + organ + bè hợp xướng"),
        ("Điểm mấu chốt","Lời bám sát nguyên văn. Khán giả thuộc lòng, chế là bị phát hiện"),
        ("Độ ồn","−13,8 LUFS")],
 struct=[("Độ dài bài","4:00–6:00"),
        ("Thời lượng video","<b>Trung vị nhóm này chỉ 8 phút</b> — ngắn nhất trong 7 định vị. "
        "Nhưng dải &gt;120 phút lại có VPD cao nhất (23,4). Hai cực đều được, khoảng giữa thì không"),
        ("Cấu trúc","Giữ đúng thứ tự câu Kinh Thánh")],
 title=("<b>KHÔNG đặt tiêu đề mô tả trần trụi.</b> 71% tiêu đề nhóm này có chứa số "
        "(số chương/câu) — cao nhất trong mọi định vị, và đó là dấu hiệu đóng gói "
        "kiểu tra cứu.<br><br>"
        "<b>Thay bằng câu hỏi giả định:</b><br>"
        "“What If David Played Guitar Instead of Harp?”<br>"
        "“The Psalms In Blues Hit So Deep It's Unreal”"),
 avoid="Đừng đặt «Psalm 23 (Lyrics) | 1 Hour». Đừng đọc nguyên văn trên nền nhạc. "
       "Đừng vào hướng này nếu chưa có công thức tiêu đề riêng — sẽ chìm giữa 30 kênh."),

"06": dict(
 idea="<b>KHÔNG khuyến nghị làm kênh theo hướng này.</b> Nhưng nếu vẫn muốn test, "
      "phải <b>cụ thể hoá nỗi đau</b> thay vì nói chung chung. «Chữa lành» chung "
      "chung là thứ 41 kênh đang cùng nói và không ai nổi bật.",
 customer="Người đang buồn, đang đau — nhưng không nói rõ đau vì gì. Chính sự "
          "mơ hồ này làm nội dung không chạm được ai cụ thể.",
 persona="Không xác định được — và đó chính là vấn đề của định vị này.",
 thumb=[("Nếu vẫn test","Phải khác hẳn 41 kênh đang làm. Đừng dùng ảnh «người buồn "
        "ngồi một mình» — đó là ảnh ai cũng dùng."),
        ("Hướng khác biệt","Cụ thể hoá bối cảnh: hành lang bệnh viện, ghế trống bên "
        "bàn ăn, ảnh người đã khuất. Cụ thể mới chạm được."),
        ("Màu","Giữ chuẩn ngách, nhưng cân nhắc tông sáng hơn — 41 kênh đều tối.")],
 music=[("Nếu vẫn test","Giữ chuẩn ngách: 88 BPM, trưởng, −13,8 LUFS"),
        ("Điểm cần khác","Đừng làm nhạc «buồn». Cung cảm xúc của ngách đi từ tối "
        "sang sáng — 51% bài sáng dần về cuối"),
        ("Nhạc cụ","Guitar + piano + organ")],
 struct=[("Thời lượng","Dải &lt;10 phút có VPD 11,8 — cao nhất trong nhóm. "
        "Dải 60–120 phút đông nhất (307 video) nhưng VPD chỉ 7,4"),
        ("Kết luận format","Nếu test thì làm <b>bài lẻ ngắn</b>, đừng làm mix dài")],
 title=("<b>Đừng dùng từ «healing» trần trụi.</b> Thay bằng nỗi đau cụ thể:<br>"
        "“For The One Who Just Lost Someone”<br>"
        "“Music For The Hospital Waiting Room”<br><br>"
        "Định vị 01 và 04 chính là hai cách cụ thể hoá đã CÓ bằng chứng — "
        "cân nhắc làm chúng thay vì hướng này."),
 avoid="Đừng làm «chữa lành» chung chung. 733 video, 41 kênh, VPD 0,74× mặt bằng, "
       "và kém cả trong từng kênh (0,88×). Cả hai lớp kiểm đều nói cùng một điều."),

"07": dict(
 idea="<b>KHÔNG khuyến nghị.</b> Đây là hướng kém nhất toàn ngách — chỉ đạt "
      "0,24× mức trung bình.<br><br>"
      "Lý do gốc nằm ở <b>cách người ta nghe</b>. Có hai kiểu: nghe nền (mở lên "
      "rồi làm việc khác, ngủ) và nghe chăm chú (ngồi nghe lời, hát theo, khóc). "
      "Ngách Christian Blues thuộc kiểu thứ hai — bối cảnh nghe phổ biến nhất "
      "trong bình luận là lúc cầu nguyện và tĩnh nguyện.<br><br>"
      "Nhạc ngủ phục vụ kiểu thứ nhất. Nó bỏ đi phần lời — mà lời chính là thứ "
      "khiến khán giả ngách này ở lại.",
 customer="Người cần âm thanh nền lúc ngủ. Họ không nghe lời, không tương tác, "
          "và thường tắt sau khi ngủ.",
 persona="Không phải khán giả cốt lõi của ngách này.",
 thumb=[("Nếu vẫn test","Cảnh đêm, bầu trời sao, phòng ngủ tối. Nhưng lưu ý: "
        "thumbnail không cứu được định vị sai."),
        ("Thực tế","32% tiêu đề nhóm này có emoji — cao nhất trong 7 định vị. "
        "Đó là dấu hiệu cạnh tranh bằng hình thức thay vì nội dung.")],
 music=[("Nếu vẫn test","Ambient, ít lời, tempo dưới 70 BPM"),
        ("Vấn đề gốc","Bỏ lời đi là bỏ đúng thứ tạo giá trị trong ngách này. "
        "Bối cảnh nghe áp đảo là cầu nguyện và tĩnh nguyện — người ta CHÚ Ý tới lời"),
        ("Bằng chứng","Nhánh instrumental thuần: VPD 1,69 · lift 0,17× · 0/2 kênh tốt hơn")],
 struct=[("Thời lượng","Nhóm này trung vị 71,6 phút — dài nhất trong 7 định vị"),
        ("Cái bẫy","Người mới hay nghĩ «dài thì nhiều điểm quảng cáo». Nhưng nếu "
        "không ai xem thì độ dài vô nghĩa. Kiểm định về độ dài trong ngách này: "
        "chênh lệch giữa video ngắn và dài <b>biến mất</b> khi so trong từng kênh "
        "(12/24 kênh, trung vị 0,95×)")],
 title=("Nếu vẫn test: “Sleep in Peace | 100 Mins of Nighttime Rest”<br><br>"
        "<b>Nhưng cân nhắc lại:</b> có 1 video nhạc ngủ đạt VPD 2.548 (xem mục 9) — "
        "cao gấp hàng nghìn lần trung vị nhóm. Một ngoại lệ không làm nên quy luật: "
        "281/283 video còn lại đều dưới mặt bằng."),
 avoid="Đừng vào hướng này để «lấy giờ xem». Ngách này thưởng nội dung nghe chủ động. "
       "Nếu muốn làm nhạc ngủ, hãy làm ở ngách khác."),
}


def card(title, inner):
    """Bọc một mục trong khung có viền.

    Vì sao: người đọc theo dõi dễ hơn khi mắt biết mỗi phần bắt đầu và kết thúc
    ở đâu. Đọc trôi tuột thì các mục dính vào nhau.
    """
    return (f'<div class="sect"><div class="stitle">{title}</div>'
            f'<div class="sbody">{inner}</div></div>')


def spread_table(df):
    """Phân bố VPD — khoảng cách giữa làm dở và làm giỏi.

    Đây là thứ trung vị KHÔNG nói được: một định vị có thể trung vị thấp nhưng
    đuôi trên rất cao, nghĩa là làm đúng thì vẫn ăn đậm.
    """
    q = {k: df.vpd.quantile(v) for k, v in
         [("p10", .10), ("p25", .25), ("trung vị", .50),
          ("p75", .75), ("p90", .90)]}
    rows = "".join(
        f'<tr><td class="w">{k}</td><td class="n">{vn(v, 1)}</td>'
        f'<td class="n">{vn(v / BASE_VPD, 2)}×</td></tr>' for k, v in q.items())
    rows += (f'<tr><td class="w">cao nhất</td>'
             f'<td class="n">{vn(df.vpd.max(), 0)}</td>'
             f'<td class="n">{vn(df.vpd.max() / BASE_VPD, 0)}×</td></tr>')
    ratio = q["p90"] / max(q["p10"], 0.01)
    return f"""<table><thead><tr><th>Phân vị</th><th class="n">VPD</th>
<th class="n">so mặt bằng</th></tr></thead><tbody>{rows}</tbody></table>
<p class="small">Khoảng cách giữa nhóm dưới (p10) và nhóm trên (p90) là
<b>{vn(ratio, 0)} lần</b>. Định vị đúng chưa đủ — thực thi quyết định phần lớn.</p>"""


def format_table(df):
    """VPD theo dải độ dài video — gợi ý format nên làm."""
    d = df.copy()
    d["band"] = pd.cut(d.duration_sec / 60, [0, 10, 30, 60, 120, 9999],
                       labels=["dưới 10 phút", "10–30 phút", "30–60 phút",
                               "60–120 phút", "trên 120 phút"])
    g = d.groupby("band", observed=True).agg(
        n=("video_id", "size"), vpd=("vpd", "median"),
        view=("view_count", "median"))
    if g.empty:
        return ""
    best = g.vpd.idxmax()
    rows = "".join(
        f'<tr><td class="w">{i}</td><td class="n">{int(r.n)}</td>'
        f'<td class="n">{vn(r.vpd, 1)}</td><td class="n">{vn(r.view)}</td>'
        f'<td>{"← tốt nhất" if i == best else ""}</td></tr>'
        for i, r in g.iterrows())
    return f"""<table><thead><tr><th>Dải độ dài</th><th class="n">Số video</th>
<th class="n">VPD trung vị</th><th class="n">View trung vị</th><th></th>
</tr></thead><tbody>{rows}</tbody></table>
<p class="small">Dải có ít video thì con số không ổn định. Chỉ đọc dải có n ≥ 20.</p>"""


EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF]")


def spec_of(df):
    """Thông số đóng gói ĐO RIÊNG cho định vị này, không dùng số chung ngách."""
    d = df.duration_sec / 60
    t = df.title.astype(str)
    return dict(
        n=len(df), n_ch=int(df.handle.nunique()),
        dur=float(d.median()), d25=float(d.quantile(.25)), d75=float(d.quantile(.75)),
        tlen=float(t.str.len().median()),
        pct_num=100 * float(t.str.contains(r"[0-9]", regex=True).mean()),
        pct_emoji=100 * float(t.map(lambda x: bool(EMOJI.search(x))).mean()),
        pct_pipe=100 * float(t.str.contains(r"\|", regex=True).mean()))


def cadence_of(df, top_n=3):
    """Nhịp đăng THẬT của nhóm kênh dẫn đầu định vị này (video/tuần).

    Đo trên toàn bộ video của kênh đó, không chỉ video thuộc định vị — vì
    lịch đăng là thuộc tính của kênh, không của một nhóm video.
    """
    g = (df.groupby("handle").agg(n=("video_id", "size"), vpd=("vpd", "median"))
           .query("n >= 3").nlargest(top_n, "vpd"))
    rates = []
    for hd in g.index:
        vv = V[V.handle == hd]
        span = (vv.published_at.max() - vv.published_at.min()).days
        if span > 30:
            rates.append(len(vv) / (span / 7))
    return float(np.median(rates)) if rates else None


def build_section(pid, spec_row, cadence):
    """Dựng mục BẢN KHỞI TẠO KÊNH — chung khuôn cho cả 7 định vị."""
    b = BUILD[pid]

    def tbl(rows):
        return ("<table><tbody>" + "".join(
            f'<tr><td class="w" style="width:32mm">{k}</td><td>{v}</td></tr>'
            for k, v in rows) + "</tbody></table>")

    n10 = ("Làm <b>10 video đầu theo đúng một công thức</b>, không đổi giữa chừng. "
           "Đổi liên tục thì không biết cái gì hiệu quả. Sau 10 video, đo VPD trung "
           "vị và so với mốc dưới đây.")

    return f"""
{card("1 · Kênh này là gì",
      f'<div class="idea">{b["idea"]}</div>'
      + tbl([("Khách hàng", b["customer"]), ("Chân dung khách", b["persona"])]))}

{card("2 · Thumbnail", tbl(b["thumb"]))}

{card("3 · Âm nhạc", tbl(b["music"]))}

{card("4 · Cấu trúc bài &amp; thời lượng",
      tbl(b["struct"])
      + f'<p class="small">Đo riêng cho định vị này: thời lượng video trung vị '
        f'<b>{vn(spec_row["dur"],1)} phút</b> '
        f'(khoảng {vn(spec_row["d25"],0)}&ndash;{vn(spec_row["d75"],0)}), '
        f'tiêu đề {vn(spec_row["tlen"],0)} ký tự, '
        f'{vn(spec_row["pct_num"],0)}% có chứa số, '
        f'{vn(spec_row["pct_emoji"],0)}% có emoji, '
        f'{vn(spec_row["pct_pipe"],0)}% dùng dấu |.</p>')}

{card("5 · Công thức tiêu đề", f'<div class="tf">{b["title"]}</div>')}

{card("6 · Lịch đăng &amp; 10 video đầu",
      tbl([("Nhịp đăng",
            f'<b>{vn(cadence,1)} video/tuần</b> — nhịp thật của nhóm kênh dẫn '
            f'đầu định vị này' if cadence else "chưa đo được"),
           ("Số kênh đang làm",
            f'{spec_row["n_ch"]} kênh · {spec_row["n"]} video'),
           ("10 video đầu", n10)]))}

{card("7 · Điều kiện dừng hoặc đổi hướng",
      f'<table><tbody>'
      f'<tr><td class="w" style="width:32mm">Sau 10 video</td><td>Nếu VPD trung '
      f'vị dưới <b>{vn(BASE_VPD,1)}</b> (mặt bằng ngách) thì dừng lại soát công '
      f'thức, đừng đăng tiếp.</td></tr>'
      f'<tr><td class="w">Sau 30 video</td><td>Nếu chưa có video nào vượt '
      f'<b>{vn(BASE_VPD*5,0)}</b> VPD (gấp 5 lần mặt bằng) thì định vị hoặc '
      f'thực thi có vấn đề.</td></tr>'
      f'<tr><td class="w">Dấu hiệu đúng</td><td>Tỷ lệ bình luận trên view tăng '
      f'dần, và bình luận bắt đầu mang đúng tín hiệu của định vị này.</td></tr>'
      f'</tbody></table>'
      f'<div class="warnbox"><b>Tránh trong hướng này.</b> {b["avoid"]}</div>')}"""

# ── RÁP TÀI LIỆU ────────────────────────────────────────────────────────────
def render(d):
    p, r = d["pos"], d["r"]
    # video nguồn: nhóm khớp tiêu đề, hoặc nhóm video dính tín hiệu bình luận
    vsrc = r["videos"] if r["kind"] == "title" else r["vids"]
    spread = spread_table(vsrc)
    fmt = format_table(vsrc)

    # BẢN KHỞI TẠO KÊNH — đủ 7 định vị, kể cả định vị nên tránh
    build_sec = build_section(p["id"], spec_of(vsrc), cadence_of(vsrc))

    if r["kind"] == "title":
        how = (f"Lọc video đã đủ 60 ngày tuổi, tìm tiêu đề khớp mẫu, so VPD "
               f"trung vị của nhóm khớp với nhóm không khớp, rồi lặp lại phép so "
               f"đó <b>bên trong từng kênh</b> để loại nghịch lý Simpson.")
        repro = f"""<pre>m = videos[videos.is_matured]
m["hit"] = m.title.str.lower().str.contains(PATTERN)
lift = m[m.hit].vpd.median() / m[~m.hit].vpd.median()
# lift = {vn(r['lift'],2)}

# kiểm trong từng kênh
for _, g in m.groupby("channel_id"):
    if g.hit.sum() &gt;= 5 and (~g.hit).sum() &gt;= 5:
        wc.append(g[g.hit].vpd.median() / g[~g.hit].vpd.median())
# trung vị = {vn(r['within'],2)} · {r['n_better']}/{r['n_ch']} kênh &gt; 1</pre>"""
    else:
        how = ("Tìm bình luận khớp mẫu trong 6.794 bình luận đã lọc 3 tầng, "
               "so <b>số like trung vị</b> của nhóm khớp với nền của ngách. "
               "Dùng like chứ không dùng tần suất — xem giải thích ở mục 8.")
        repro = f"""<pre>c = comments[comments.text.str.len() &gt;= 15]
h = c[c.text.str.lower().str.contains(PATTERN)]
lift = h.like_count.median() / c.like_count.median()
# {vn(r['like'],1)} / {vn(r['base'],1)} = {vn(r['lift'],1)}x
# p = {r['p']:.2e} · n = {vn(r['n'])}</pre>"""

    body = f"""
{build_sec}

<div class="divider">
  <div class="dtitle">Phần chứng minh</div>
  <p>Từ đây trở đi là <b>bằng chứng</b> cho mọi con số ở trên. Nếu bạn chỉ cần
  bắt tay làm thì phần trên đã đủ; phần này dành cho lúc cần kiểm lại hoặc
  thuyết phục người khác.</p>
</div>

{card("8 · Bằng chứng — vì sao tin (hoặc không tin) được",
      f'<p class="small">Mọi số đo trên video đã đủ 60 ngày tuổi. Mặt bằng ngách: '
      f'VPD {vn(BASE_VPD,2)} · like nền {vn(BASE_LIKE,1)}.</p>' + d['ev'])}

{card("9 · Video đối chứng — tra tận nơi", d['vids'])}

{card("10 · Khoảng cách giữa làm dở và làm giỏi",
      '<p>Trung vị chỉ nói mức trung bình. Bảng này cho biết <b>biên độ</b> — '
      'làm đúng thì trần ở đâu, làm sai thì đáy ở đâu.</p>' + spread)}

{card("11 · Nên làm format nào — số liệu",
      '<p>VPD theo dải độ dài video, tính riêng cho định vị này.</p>' + fmt)}

{card("12 · Kênh đang làm định vị này",
      '<p>Tham khảo cách họ đóng gói.</p>' + d['chans'])}

{d['quotes']}

{card("14 · Tự kiểm chứng lại",
      f'<p><b>Cách đo:</b> {how}</p>' + repro
      + '<p class="small">Chạy lại: '
        '<code>python3 pipeline/report/build_positioning_cards.py</code></p>')}

{card("15 · Giới hạn của kết luận này", f'''
<table><tbody>
<tr><td class="w" style="width:26mm">Nguồn dữ liệu</td><td>Toàn bộ từ <b>Y</b>
  (YouTube). Câu «định vị này còn trống không» chỉ suy gián tiếp được — YouTube
  chỉ thấy cung đã tồn tại.</td></tr>
<tr><td class="w">Số lần đo</td><td>Chỉ <b>1 snapshot</b> (13/08/2026). Không đo
  được tốc độ tăng trưởng thật của từng video.</td></tr>
<tr><td class="w">Thiên lệch mẫu</td><td>Dữ liệu chỉ chứa kênh <b>còn tồn tại</b>.
  Kênh đã thất bại và bị xoá không xuất hiện — mọi tỷ lệ thành công đều lạc quan
  hơn thực tế.</td></tr>
{'<tr><td class="w">Kiểm Simpson</td><td>Chỉ dựa trên <b>' + str(r['n_ch']) + ' kênh</b> đủ mẫu. Dưới 5 kênh thì chưa loại trừ được hiệu ứng gộp kênh.</td></tr>' if r['kind']=='title' and r['n_ch']<5 else ''}
</tbody></table>''')}"""

    foot = f"""<b>Nguồn.</b> <code>00_input/processed/videos.parquet</code> ·
<code>video_stats.parquet</code> · <code>selected_comments.parquet</code>.
Đo ngày 13/08/2026 trên {vn(len(M))} video đã chín / {vn(len(V))} video thu thập,
{vn(V.channel_id.nunique())} kênh.<br><br>
<b>Phán quyết.</b> {d['verdict']} — {d['grp_desc']}<br><br>
<b>Quy tắc R6.</b> Trích dẫn đã bỏ định danh. Không suy đoán tuổi/sắc tộc/tôn
giáo từ tên hay ảnh đại diện; chỉ ghi nhận khi người viết tự khai công khai."""

    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{css(d['accent'], d['soft']).replace('Định vị {}', 'Định vị ' + p['id'])}
pre {{ background:#F7F5F2; border-radius:3pt; padding:8pt 10pt; font-size:7.5pt;
  font-family:"DejaVu Sans Mono",monospace; line-height:1.5; white-space:pre-wrap;
  page-break-inside:avoid; }}
code {{ font-family:"DejaVu Sans Mono",monospace; font-size:8pt; }}
</style></head><body>
<div class="cover">
  <div class="eyebrow">Định vị {p['id']} · Ngách Christian Blues</div>
  <h1>{p['name']}</h1>
  <p class="need">{p['need']}</p>
  <div class="badge">{d['label']} · {d['verdict']}</div>
  <hr class="rule">
  <div class="covmeta">
    <b>Cỡ mẫu</b> &nbsp; {vn(r['n'])} {'video' if r['kind']=='title' else 'bình luận'}
      · {vn(r.get('n_channels') or r.get('n_videos'))} {'kênh' if r['kind']=='title' else 'video dính'}<br>
    <b>Chênh lệch</b> &nbsp; {vn(r['lift'],2)}× so mặt bằng · p = {r['p']:.2e}<br>
    <b>Đo ngày</b> &nbsp; 13/08/2026 · {vn(len(M))} video đã đủ 60 ngày<br>
    <b>Dựng lúc</b> &nbsp; 29/08/2026
  </div>
</div>
{body}
<div class="foot">{foot}</div>
</body></html>"""


if __name__ == "__main__":
    print(f"Mặt bằng: VPD {BASE_VPD:.2f} · like nền {BASE_LIKE:.1f} · "
          f"{len(M)} video đã chín\n")
    made = []
    for p in POS:
        d = build(p)
        if not d:
            continue
        out = OUT / f"DV-{p['id']}_{p['name'].replace(' ', '-')}.pdf"
        HTML(string=render(d), base_url=".").write_pdf(out)
        made.append((p, d, out))
        print(f"  {p['id']} · {d['verdict']:24} {out.name}  "
              f"({out.stat().st_size/1024:.0f} KB)")
    print(f"\n{len(made)} tài liệu -> {OUT.relative_to(N.parent.parent)}/")
