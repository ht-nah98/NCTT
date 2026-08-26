"""BÁO CÁO CHI TIẾT — gộp 7 báo cáo STEP rời thành một bản tra cứu.

VÌ SAO CÓ FILE NÀY (phản hồi người dùng 2026-08-26):
  99_report có 18 PDF / 188 trang. Mỗi báo cáo STEP tự mở bằng "Tóm tắt điều
  hành" và tự đóng bằng "Độ tin cậy và điều chưa biết" — 7 lần lặp cùng một
  cấu trúc, cùng một bộ số nền (53 kênh / 7.193 video / 12,05 điểm xuất hiện
  ở 6-7 file khác nhau). Người đọc phải mở 7 file mới ghép được bức tranh.

  Bản này gộp lại: tham số mẫu nói MỘT LẦN ở đầu, mọi cảnh báo độ tin cậy gom
  về MỘT mục cuối, phần thân chỉ còn kết quả theo trình tự nghiên cứu.

Mọi số đọc động từ metrics.json / scores.json / _synthesis.json (T27).
"""
import json
import sys
from pathlib import Path

import pandas as pd
from weasyprint import HTML

N = Path(sys.argv[1] if len(sys.argv) > 1 else "niches/christian-blues")
D = N / "99_report"
D.mkdir(parents=True, exist_ok=True)
NICHE_LABEL = N.name.replace("-", " ").title()

M = json.loads((N / "_state/metrics.json").read_text())
S = json.loads((N / "_state/scores.json").read_text())
SYN = json.loads((D / "_synthesis.json").read_text())

MK, MO, EN, AI = M["market"], M["momentum"], M["entry"], M["ai_fit"]
AU, MN, FO = M["audience"], M["money"], M["formula"]
META = M.get("_meta", {})

_v = pd.read_parquet(N / "00_input/processed/videos_enriched.parquet")
_c = pd.read_parquet(N / "00_input/processed/channels_enriched.parquet")
N_VIDEO, N_CHANNEL = len(_v), len(_c)
N_COMMENT = len(pd.read_parquet(N / "00_input/processed/comments.parquet"))
TOTAL = S.get("total", S.get("total_score"))


def vn(x, nd=0):
    """Số kiểu VN: phẩy thập phân, chấm ngăn nghìn."""
    s = f"{x:,.{nd}f}"
    a, *b = s.split(".")
    return a.replace(",", ".") + ("," + b[0] if b else "")


def vnf(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def pct(x, nd=1):
    return vnf(x, nd) + "%"


def money(x, nd=0):
    return "$" + vn(x, nd)


# ═══════ 1 · Quy mô & động lượng (STEP_01-02) ═══════
_rpm_lo, _rpm_mid, _rpm_hi = MN["M5_2_rpm_range"]
_band = sorted(MN["M5_3_band"], key=lambda b: -b["ad_slots"])
_band_rows = "\n".join(
    f'<tr><td>{b["duration_band"]}</td><td class="n">{vn(b["n"])}</td>'
    f'<td class="n">{vn(b["med_sec"] / 60, 0)} phút</td>'
    f'<td class="n">{vn(b["med_view"])}</td>'
    f'<td class="n"><b>{vnf(b["ad_slots"], 1)}</b></td></tr>'
    for b in _band
)

# ═══════ 2 · Đối thủ & cửa vào (STEP_03) ═══════
_fast = EN.get("M3_3_alt_fastest_success", [])[:5]
_fast_rows = "\n".join(
    f'<tr><td class="n">{i}</td><td><code>{f["handle"]}</code></td>'
    f'<td class="n">{vnf(f["age_m"], 1)} tháng</td>'
    f'<td class="n">{vn(f["vpm"])}</td></tr>'
    for i, f in enumerate(_fast, 1)
)
_model = AI["model_dist"]
_model_tot = sum(_model.values())
_model_rows = "\n".join(
    f'<tr><td>{k}</td><td class="n">{v}</td><td class="n">{pct(v / _model_tot * 100)}</td></tr>'
    for k, v in sorted(_model.items(), key=lambda kv: -kv[1])
)

# ═══════ 3 · Khán giả (STEP_05) ═══════
_pers = AU["personas"]
_PLAB = {
    "p_healing": "Người tìm chữa lành / an ủi",
    "p_elder": "Người cao tuổi hoài niệm",
    "p_convert": "Người mới trở lại đức tin",
    "p_music": "Người nghe vì âm nhạc",
}
_pers_rows = "\n".join(
    f'<tr><td>{_PLAB.get(k, k)}</td><td class="n">{vn(p["n"])}</td>'
    f'<td class="n">{pct(p["pct"], 2)}</td><td class="n">{vnf(p["med_likes"], 1)}</td></tr>'
    for k, p in sorted(_pers.items(), key=lambda kv: -kv[1]["n"])
)

# ═══════ 4 · Khoảng trống & ý tưởng (STEP_06 + 08) ═══════
_gaps = SYN.get("gaps", [])
_SC = {"CAO": "ok", "VỪA": "wa", "THẤP": "no"}


def _demand_cell(g):
    """CẦU là danh sách claim có nguồn — lấy 2 claim đầu (bỏ trích dẫn dài)."""
    items = [d for d in g.get("demand", []) if len(d.get("claim", "")) < 130][:2]
    return "<br>".join(
        f'{d["claim"]}<br><span class="note">{d.get("id", "")}</span>' for d in items
    ) or "—"


_gap_rows = "\n".join(
    f'<tr><td class="n">{i}</td>'
    f'<td><b>{g.get("gap", "")}</b><br>'
    f'<span class="note">Khả thi: {g.get("feasible", "—")}</span></td>'
    f'<td>{_demand_cell(g)}</td>'
    f'<td>{g.get("supply", "—")}</td>'
    f'<td class="ph">{g.get("perf", "—")}</td>'
    f'<td class="c"><span class="{_SC.get(g.get("score"), "")}">{g.get("score", "—")}</span>'
    f'<br><span class="note">tin: {g.get("conf", "—")}</span></td></tr>'
    for i, g in enumerate(_gaps, 1)
)

_ideas = SYN.get("ideas", [])
_idea_rows = "\n".join(
    f'<tr><td class="n">{x.get("n", i)}</td><td>{x.get("title", "")}</td>'
    f'<td class="note">{x.get("basis", "")}</td>'
    f'<td class="c">{x.get("len", "—")}</td></tr>'
    for i, x in enumerate(_ideas, 1)
)

# ═══════ 5 · Điểm số theo trục ═══════
_TLAB = {
    "T1": "Quy mô thị trường", "T2": "Động lượng tăng trưởng",
    "T3": "Cửa gia nhập", "T4": "Phù hợp sản xuất AI",
    "T5": "Khả năng kiếm tiền", "T6": "Rủi ro / phạt",
}
_axes = S["axes"]
_axis_rows = "\n".join(
    f'<tr><td><b>{k}</b> — {_TLAB.get(k, "")}</td>'
    f'<td class="n">{vnf(a["score"], 2)}</td>'
    f'<td class="n">{pct(a["weight"] * 100, 0)}</td>'
    f'<td class="ph">{a.get("metric", "")}</td>'
    f'<td class="c">{a.get("confidence", "—")}</td></tr>'
    for k, a in _axes.items()
)

# ═══════ 6 · Độ tin cậy — GOM VỀ MỘT CHỖ ═══════
# Mỗi báo cáo STEP cũ có mục "Độ tin cậy" riêng; gom lại tránh lặp 7 lần.
_caveats = [
    (a.get("caveat"), k) for k, a in _axes.items() if a.get("caveat")
]
_cav_rows = "\n".join(
    f'<tr><td class="c"><b>{k}</b></td><td>{c}</td></tr>' for c, k in _caveats
)

CSS = """
@page { size:A4; margin:16mm 14mm 18mm;
 @bottom-center { content: counter(page) " / " counter(pages);
  font-family:"DejaVu Sans"; font-size:8pt; color:#9A8E85; } }
body { font-family:"DejaVu Sans",sans-serif; font-size:9.5pt; line-height:1.5; color:#1A1614; }
h1 { font-size:21pt; margin:0 0 4pt; letter-spacing:-.4pt; }
h2 { font-size:13pt; margin:17pt 0 7pt; padding-bottom:4pt;
 border-bottom:1.5pt solid #1A1614; page-break-after:avoid; }
h3 { font-size:10.5pt; margin:12pt 0 5pt; color:#8C3A2B; page-break-after:avoid; }
p { margin:5pt 0; }
.sub { color:#6B615A; font-size:10.5pt; margin:0 0 10pt; }
.meta { font-size:8pt; color:#7A6F68; border-top:.6pt solid #E2DAD1;
 border-bottom:.6pt solid #E2DAD1; padding:6pt 0; margin-bottom:13pt; }
table { border-collapse:collapse; width:100%; font-size:8.5pt; margin:7pt 0; }
th { background:#F2EEE8; text-align:left; padding:5pt 7pt; font-size:7.3pt;
 text-transform:uppercase; letter-spacing:.4pt; color:#5A514B;
 border-bottom:1pt solid #CFC4B8; }
td { padding:5.5pt 7pt; border-bottom:.6pt solid #EDE7E0; vertical-align:top; }
tr { page-break-inside:avoid; }
td.n { text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
td.c { text-align:center; white-space:nowrap; }
td.ph { font-size:7.8pt; color:#5A514B; }
.note { font-size:7.6pt; color:#7A6F68; }
.box { border-left:2.5pt solid #8C3A2B; background:#F9F4F2; padding:8pt 11pt;
 margin:9pt 0; page-break-inside:avoid; }
.box.warn { border-left-color:#B5731F; background:#FBF3E8; }
.box.crit { border-left-color:#9B2C2C; background:#FBEEEE; }
.box.ok { border-left-color:#2F6B4F; background:#EFF5F1; }
.box .l { font-size:7.3pt; text-transform:uppercase; letter-spacing:.7pt;
 font-weight:bold; color:#8C3A2B; display:block; margin-bottom:4pt; }
.box.warn .l { color:#B5731F; } .box.crit .l { color:#9B2C2C; } .box.ok .l { color:#2F6B4F; }
.box p { margin:0 0 5pt; font-size:9pt; } .box p:last-child { margin-bottom:0; }
.kpi { display:flex; gap:7pt; margin:9pt 0; }
.kpi div { flex:1; border:.6pt solid #E2DAD1; padding:8pt 9pt; }
.kpi .k { font-size:6.6pt; text-transform:uppercase; letter-spacing:.5pt;
 color:#7A6F68; margin-bottom:4pt; }
.kpi .v { font-size:16pt; font-weight:bold; letter-spacing:-.3pt; }
.kpi .c2 { font-size:6.8pt; color:#7A6F68; margin-top:3pt; line-height:1.3; }
code { background:#F2EEE8; padding:.5pt 3pt; font-size:8pt; }
.ok { color:#2F6B4F; font-weight:bold; } .wa { color:#B5731F; font-weight:bold; }
.no { color:#9B2C2C; font-weight:bold; }
.verdict { color:#8C3A2B; font-weight:bold; font-size:8.6pt; }
.pb { page-break-before:always; }
.toc { font-size:9pt; column-count:2; column-gap:18pt; }
.toc div { margin:2.5pt 0; break-inside:avoid; }
"""

DOC = f"""<!doctype html><html><head><meta charset="utf-8">
<style>{CSS}</style></head><body>

<h1>{NICHE_LABEL} &mdash; Phân tích chi tiết</h1>
<p class="sub">Bản tra cứu đầy đủ. Gộp từ 7 báo cáo theo bước, bỏ phần lặp.</p>
<div class="meta">
{vn(N_CHANNEL)} kênh &middot; {vn(N_VIDEO)} video &middot; {vn(N_COMMENT)} bình luận
&nbsp;&middot;&nbsp; Dữ liệu crawl 13/08/2026 &nbsp;&middot;&nbsp;
Điểm ngách <b>{vnf(TOTAL)}/20</b> &nbsp;&middot;&nbsp;
Nguồn số: <code>_state/metrics.json</code>, <code>_state/scores.json</code>
</div>

<div class="box">
<span class="l">Cách dùng bản này</span>
<p>Đây là bản TRA CỨU, không phải bản trình bày. Bản trình bày là
<b>BAO-CAO_{NICHE_LABEL.replace(" ", "-")}.pdf</b> &mdash; đọc bản đó trước.</p>
<p>Tham số mẫu và giới hạn dữ liệu chỉ nói MỘT LẦN: tham số ở dòng trên, giới hạn ở mục 6 cuối bản.
Các mục 1&ndash;5 chỉ chứa kết quả.</p>
</div>

<h3>Mục lục</h3>
<div class="toc">
<div>1 &middot; Quy mô &amp; động lượng thị trường</div>
<div>2 &middot; Đối thủ &amp; cửa gia nhập</div>
<div>3 &middot; Chân dung khán giả</div>
<div>4 &middot; Khoảng trống &amp; ý tưởng nội dung</div>
<div>5 &middot; Điểm số 6 trục</div>
<div>6 &middot; Độ tin cậy &mdash; mọi cảnh báo gom về đây</div>
</div>

<h2 class="pb">1 &middot; Quy mô &amp; động lượng thị trường</h2>
<div class="kpi">
<div><div class="k">View/tháng ngách</div><div class="v">{vn(MK["M1_1_views_per_month"] / 1e6, 2)}tr</div>
<div class="c2">Trung vị mỗi video {vn(MK["M1_3_median_view"])} view</div></div>
<div><div class="k">Kênh đang hoạt động</div><div class="v">{MK["M1_2_active_channels"]}</div>
<div class="c2">trên tổng {MK["M1_2_total_channels"]} kênh khảo sát</div></div>
<div><div class="k">Cầu / Cung</div><div class="v" style="color:#2F6B4F">{vnf(MO["M2_4_demand_supply_gap"])}×</div>
<div class="c2">View tăng {vnf(MO["M2_1_view_growth"])}× &mdash; nguồn cung chỉ {vnf(MO["M2_2_supply_growth"])}×</div></div>
<div><div class="k">Kênh mới gia nhập</div><div class="v">{pct(MO["M2_3_new_channel_rate"])}</div>
<div class="c2">Thị trường đang được bổ sung nhanh</div></div>
</div>
<p class="verdict">=> Cầu tăng nhanh hơn cung {vnf(MO["M2_4_demand_supply_gap"])} lần &mdash; còn chỗ cho nguồn cung mới,
nhưng quy mô tuyệt đối chỉ {vn(MK["M1_1_views_per_month"] / 1e6, 1)} triệu view/tháng nên không đủ nuôi một kênh lớn duy nhất.</p>

<h3>1.1 &middot; Độ dài video &mdash; nơi quyết định doanh thu</h3>
<table>
<thead><tr><th>Dải độ dài</th><th>Số video</th><th>Trung vị</th><th>View trung vị</th><th>Ad-slot/video</th></tr></thead>
<tbody>{_band_rows}</tbody>
</table>
<p class="verdict">=> Chênh lệch ad-slot giữa dải dài nhất và ngắn nhất là
{vnf(_band[0]["ad_slots"] / _band[-1]["ad_slots"], 1)}×. Đây là đòn bẩy doanh thu lớn nhất đo được.</p>

<h2>2 &middot; Đối thủ &amp; cửa gia nhập</h2>
<div class="kpi">
<div><div class="k">Kênh mới thành công</div><div class="v" style="color:#2F6B4F">{pct(EN["M3_2_newcomer_success_pct"])}</div>
<div class="c2">Kênh &lt;12 tháng đạt ≥100k view/tháng</div></div>
<div><div class="k">Hệ số Gini</div><div class="v">{vnf(EN["M3_1_gini"], 3)}</div>
<div class="c2">Mức tập trung trung bình &mdash; không ai độc chiếm</div></div>
<div><div class="k">Kênh lớn nhất chiếm</div><div class="v">{pct(EN["top1_share"])}</div>
<div class="c2">Top 20% kênh chiếm {pct(EN["top20pct_share"])}</div></div>
<div><div class="k">AI-first trong top 20</div><div class="v">{pct(AI["M4_1_ai_first_top20_pct"], 0)}</div>
<div class="c2">Mô hình sản xuất AI đã được chứng minh ở đây</div></div>
</div>

<h3>2.1 &middot; 5 kênh lên nhanh nhất &mdash; mốc thời gian tham chiếu</h3>
<table>
<thead><tr><th style="width:5%">#</th><th>Kênh</th><th>Tuổi khi đạt ngưỡng</th><th>View/tháng</th></tr></thead>
<tbody>{_fast_rows}</tbody>
</table>
<p class="verdict">=> Kênh nhanh nhất đạt ngưỡng sau {vnf(_fast[0]["age_m"], 1)} tháng.
Đây là mốc kỳ vọng thực tế, không phải trường hợp cá biệt &mdash; có {len(_fast)} kênh cùng dải.</p>

<h3>2.2 &middot; Mô hình sản xuất của {_model_tot} kênh</h3>
<table>
<thead><tr><th>Mô hình</th><th>Số kênh</th><th>Tỷ lệ</th></tr></thead>
<tbody>{_model_rows}</tbody>
</table>

<h2 class="pb">3 &middot; Chân dung khán giả</h2>
<div class="kpi">
<div><div class="k">Bình luận phân tích</div><div class="v">{vn(AU["n_analyzed"])}</div>
<div class="c2">Đã lọc {vn(AU.get("n_noise", 0))} bình luận nhiễu</div></div>
<div><div class="k">Tuổi tự khai (trung vị)</div><div class="v">{vn(AU["age_median"])}</div>
<div class="c2">{pct(AU["age_60plus_pct"])} từ 60 tuổi trở lên &middot; n={vn(AU["age_n"])}</div></div>
<div><div class="k">Bối cảnh nghe hàng đầu</div><div class="v" style="font-size:12pt">{AU["top_context"]}</div>
<div class="c2">{pct(AU["top_context_pct"])} số bình luận nêu bối cảnh</div></div>
<div><div class="k">Thuật toán / Tìm kiếm</div><div class="v">{vnf(AU["discovery_algo_vs_search"], 1)}×</div>
<div class="c2">Khán giả đến từ đề xuất, không phải gõ tìm</div></div>
</div>
<p class="verdict">=> Khán giả cao tuổi, đến qua đề xuất chứ không tìm kiếm.
Hệ quả: tối ưu tiêu đề cho SEO ít giá trị hơn tối ưu thumbnail và thời lượng giữ chân.</p>

<h3>3.1 &middot; Bốn nhóm khán giả nhận diện được</h3>
<table>
<thead><tr><th>Nhóm</th><th>Số bình luận</th><th>Tỷ lệ</th><th>Like trung vị</th></tr></thead>
<tbody>{_pers_rows}</tbody>
</table>
<p class="note">Tỷ lệ tính trên {vn(AU["n_analyzed"])} bình luận đã lọc. Phần còn lại không nêu đủ
tín hiệu để xếp nhóm &mdash; đây là giới hạn của phương pháp gắn nhãn theo từ khoá, không phải
bằng chứng rằng nhóm khác không tồn tại.</p>

<h2>4 &middot; Khoảng trống &amp; ý tưởng nội dung</h2>
<h3>4.1 &middot; {len(_gaps)} khoảng trống thị trường</h3>
<table>
<thead><tr><th style="width:4%">#</th><th style="width:17%">Khoảng trống</th>
<th style="width:26%">Cầu &mdash; bằng chứng</th><th style="width:15%">Cung hiện tại</th>
<th style="width:29%">Hiệu quả đo được</th><th style="width:9%">Điểm</th></tr></thead>
<tbody>{_gap_rows}</tbody>
</table>
<p class="note">Cột "Điểm" là mức ưu tiên, cột "tin" là độ tin cậy của bằng chứng &mdash;
hai thứ khác nhau. Một khoảng trống điểm CAO nhưng độ tin THẤP nghĩa là đáng thử nghiệm nhỏ,
không phải đáng dồn lực.</p>

<h3 class="pb">4.2 &middot; {len(_ideas)} tiêu đề sẵn dùng</h3>
<table>
<thead><tr><th style="width:4%">#</th><th style="width:47%">Tiêu đề</th>
<th style="width:37%">Dựa trên khoảng trống nào</th><th style="width:12%">Độ dài</th></tr></thead>
<tbody>{_idea_rows}</tbody>
</table>

<h2>5 &middot; Điểm số 6 trục</h2>
<table>
<thead><tr><th>Trục</th><th>Điểm</th><th>Trọng số</th><th>Chỉ số quyết định</th><th>Độ tin</th></tr></thead>
<tbody>{_axis_rows}</tbody>
</table>
<p class="verdict">=> Tổng {vnf(TOTAL)}/20 &mdash; xếp loại {S.get("verdict", S.get("rating", "Theo dõi"))}.</p>

<h2 class="pb">6 &middot; Độ tin cậy &mdash; mọi cảnh báo gom về đây</h2>
<div class="box crit">
<span class="l">Đọc mục này trước khi trích số ra ngoài</span>
<p>Bảy báo cáo bước trước đây mỗi bản có một mục "Độ tin cậy" riêng, nên cùng một cảnh báo
bị lặp nhiều lần và người đọc dễ bỏ qua. Toàn bộ gom về đây.</p>
</div>

<h3>6.1 &middot; Cảnh báo gắn với từng trục điểm</h3>
<table>
<thead><tr><th style="width:8%">Trục</th><th>Cảnh báo</th></tr></thead>
<tbody>{_cav_rows}</tbody>
</table>

<h3>6.2 &middot; Giới hạn chung của bộ dữ liệu</h3>
<div class="box warn">
<span class="l">Bốn giới hạn ảnh hưởng tới mọi con số ở trên</span>
<p><b>1. Chỉ có một lần chụp số liệu.</b> Mọi chỉ số tăng trưởng suy ra từ so sánh hai cửa sổ
thời gian trong cùng một lần crawl (13/08/2026), không phải theo dõi liên tục.
Trục T2 đặc biệt nhạy với lựa chọn cửa sổ &mdash; xem cảnh báo T2 ở bảng trên.</p>
<p><b>2. Công thức nội dung: {FO["features_confirmed"]}/{FO["features_tested"]} đặc trưng được xác nhận.</b>
Đã kiểm {FO["features_tested"]} đặc trưng trên {FO["paired_channels"]} kênh ghép cặp;
không đặc trưng nào vượt được kiểm định trong-kênh. Nghĩa là <b>chưa tìm ra "bí quyết" nào
đo được</b> &mdash; yếu tố quyết định nằm ngoài thứ dữ liệu này chạm tới.</p>
<p><b>3. Nghịch lý Simpson đã loại nhiều tín hiệu trông mạnh.</b> Ví dụ chủ đề Kinh Thánh:
{FO["bible_verdict"]}</p>
<p><b>4. Bình luận không đại diện cho người xem.</b> Chỉ người chủ động viết mới được đếm
({vn(AU["n_analyzed"])} trên {vn(N_COMMENT)} bình luận thô, và bình luận vốn chỉ từ một phần rất nhỏ
người xem). Chân dung khán giả ở mục 3 mô tả <b>người bình luận</b>, không phải toàn bộ khán giả.</p>
</div>

<div class="box">
<span class="l">Nguồn số &mdash; truy ngược được</span>
<p>Mọi con số trong bản này đọc trực tiếp từ <code>_state/metrics.json</code>,
<code>_state/scores.json</code> và <code>99_report/_synthesis.json</code> lúc dựng file,
không gõ tay. Chạy lại <code>bash pipeline/run_all.sh</code> thì bản này tự cập nhật theo.</p>
</div>

</body></html>"""

out = D / "CHI-TIET_Phan-tich-day-du.pdf"
HTML(string=DOC).write_pdf(out)
print(f"OK  {out}")
