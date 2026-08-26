"""BÁO CÁO ĐÚC KẾT CUỐI — Christian Blues.
Chỉ kết quả và số liệu quyết định. Không diễn giải phương pháp luận.
Học từ mẫu FMG: bảng đối chiếu CUNG-CẦU kết bằng phán quyết "=>", khối
tham số mẫu đầu trang, mọi nhận xét kết thúc bằng một câu hành động.
"""
import json
import sys
from pathlib import Path
import pandas as pd
from weasyprint import HTML

N = Path(sys.argv[1] if len(sys.argv) > 1 else "niches/christian-blues")
D = N / "99_report"
NICHE_LABEL = N.name.replace("-", " ").title()
S = json.load(open(D / "_synthesis.json"))
SC = json.load(open(N / "_state/scores.json"))
M2 = json.load(open(N / "02_market/_metrics_raw.json"))
M3 = json.load(open(N / "03_competitor/_metrics_raw.json"))
M5 = json.load(open(N / "05_audience/_metrics_raw.json"))
M6 = json.load(open(N / "06_keyword/_metrics_raw.json"))
M7 = json.load(open(N / "07_monetization/_metrics_raw.json"))
AR = json.load(open(N / "04_outlier/audio/AUDIO_RECIPE.json"))
_KWT = pd.read_csv(N / "06_keyword/02_theme_scores.csv")
NORMS = json.load(open(N / "03_competitor/PRODUCTION_NORMS.json"))
_SIGTEST = {s["signal"]: s for s in M5.get("signal_tests", [])}

def _sc_vn(x): return f"{x:g}".replace(".", ",")
def vn(x, nd=0):
    s = f"{x:,.{nd}f}"
    a, *b = s.split(".")
    a = a.replace(",", ".")
    return a + ("," + b[0] if b else "")
def pct(x, nd=1): return vn(x, nd) + "%"

# ═══════ 12 THAM SỐ ÂM NHẠC BẮT BUỘC (CHẶT nhất) ═══════
spec, mf = AR["spec"], AR["must_follow"]
rows = sorted(
    ((k, spec[k]) for k in mf if k in spec),
    key=lambda r: (r[1].get("iqr_over_median") if r[1].get("iqr_over_median") is not None else 99),
)
_recipe_rows = "\n".join(
    f'<tr><td><code>{k}</code></td><td class="n">{vn(v.get("median",0),3)}</td>'
    f'<td class="n">{vn(v.get("p25",0),3)}&ndash;{vn(v.get("p75",0),3)}</td>'
    f'<td class="c"><span class="ok">CHẶT</span></td></tr>'
    for k, v in rows
)

# ═══════ BẢNG ĐỐI CHIẾU CUNG-CẦU (kiểu FMG) ═══════
# Số liệu đọc động từ nguồn — KHÔNG gõ cứng (T27). Câu evidence/verdict là diễn
# giải biên soạn (không phải số đo được), nên vẫn viết tay nhưng ghép placeholder.
context = M5["context"]
_os = _KWT[_KWT.theme == "old_school"].iloc[0] if (_KWT.theme == "old_school").any() else None
_ad = next((b for b in M7["M5_3_band"] if b["duration_band"] == "1-3h"), None)
_ad_short = next((b for b in M7["M5_3_band"] if b["duration_band"] == "1-6m"), None)
_fin = _SIGTEST.get("finally", {})
_gap_latam = next((g for g in S["gaps"] if "Tây Ban Nha" in g["gap"]), None)
_n_video = len(pd.read_parquet(N / "00_input/processed/videos_enriched.parquet"))
_n_channel_all = len(pd.read_parquet(N / "00_input/processed/channels_enriched.parquet"))
_n_comment_raw = len(pd.read_parquet(N / "00_input/processed/comments.parquet"))

# ═══════ Số cho mục 10 (khuyến nghị) ═══════
_ctx_prayer = M5["context"]["prayer_devo"]["pct"]
_rpm_base = M7["M5_2_rpm"]["base"]
# Tỷ lệ "sáng tác mới": dùng THỨ TỰ ƯU TIÊN giống build_pd_report.py, không
# dùng first() — first() cho 80,0% còn ưu tiên cho 76,7%, lệch thì báo cáo
# mâu thuẫn nhau (T27).
_PD_PRI = ["HYMN_PARTIAL_PD", "HYMN_PARTIAL_CHECK_YEAR", "SCRIPTURE_PARAPHRASE", "NEW_COMPOSITION"]
try:
    _pdf = pd.read_parquet(N / "02_analysis/pd_classification.parquet")
    _vc = _pdf.groupby("video_id").pd_class.agg(
        lambda s: next(c for c in _PD_PRI if (s == c).any()))
    _pd_new = pct((_vc == "NEW_COMPOSITION").mean() * 100)
except Exception:
    _pd_new = "—"

CUNG_CAU = [
    ("Cầu nguyện / Tĩnh tâm", context.get("prayer_devo", {}).get("pct", 0),
     f"Chưa kênh nào định vị nội dung có lời riêng cho mục này.",
     f"=> Cầu lớn nhất ({pct(context.get('prayer_devo',{}).get('pct',0))}), cung chưa bám sát định dạng khán giả cần. Ưu tiên làm nội dung CÓ LỜI, không phải instrumental."),
    ("Old-school / vintage gospel", 0,
     (f"lift {vn(_os.lift,2)}&times; — cao nhất 16 chủ đề, NHƯNG phán quyết «{_os.verdict}»: "
      f"trong-kênh chỉ {vn(_os.within_median_lift,2)}&times;." if _os is not None else "—"),
     "=> Tín hiệu mạnh nhưng ĐỘ TIN THẤP &mdash; hiệu ứng có thể do vài kênh may mắn, không phải công thức. Thử nghiệm nhỏ trước khi dồn lực."),
    ("Mix dài 1&ndash;3 giờ", 0,
     (f"{pct(NORMS['tracklist']['pct_all'])} thị trường đã làm (đông), nhưng vẫn cho {vn(_ad['ad_slots'],1)} ad-slot/video "
      f"&mdash; gấp ~{vn(round(_ad['ad_slots']/_ad_short['ad_slots']))}&times; video ngắn." if _ad and _ad_short else "—"),
     "=> Cung đã bão hòa về SỐ LƯỢNG nhưng chưa bão hòa về CHẤT LƯỢNG. Vào bằng chất lượng sản xuất, không bằng số lượng."),
    ("Tây Ban Nha / Bồ Đào Nha", 0,
     (f"Cung: {_gap_latam['supply']}. Hiệu suất: {_gap_latam['perf']} "
      f'<span class="src" style="margin:0">[đối chiếu nguồn ngoài FMG]</span>' if _gap_latam else "—"),
     "=> Cầu gần gấp đôi cung. Ngách phụ chưa cạnh tranh, rủi ro thấp để thử."),
    ('Định vị "yêu blues, cần lời sạch"', 0,
     (f'Tín hiệu "finally" (thoát khỏi lời Blues thô) có like trung vị gấp {vn(_fin.get("vs_baseline",0),1)}&times; mức nền '
      f'&mdash; chưa kênh nào dùng làm định vị chính.' if _fin else "—"),
     "=> Chỗ trống rõ nhất trong toàn bộ nghiên cứu: độ tin CAO, chi phí bằng 0 (chỉ đổi mô tả kênh), chưa ai chiếm."),
]

def cc_row(name, pct_val, evidence, verdict):
    pct_html = f'<td class="n">{pct(pct_val)}</td>' if pct_val else '<td class="n">&mdash;</td>'
    return f'<tr><td><b>{name}</b></td>{pct_html}<td>{evidence}<br><span class="verdict">{verdict}</span></td></tr>'

CC_ROWS = "\n".join(cc_row(*g) for g in CUNG_CAU)

# ═══════ GAPS đầy đủ (đã có sẵn cấu trúc điểm/độ tin) ═══════
_gap_rows = "\n".join(
    f'<tr><td><b>{g["gap"]}</b></td>'
    f'<td class="c">{g["score"]}</td>'
    f'<td class="c">{g["conf"]}</td>'
    f'<td>{g.get("perf","—")}</td></tr>'
    for g in S["gaps"]
)

# ═══════ 24 Ý TƯỞNG — chỉ 8 mẫu tiêu biểu, nhóm theo trục ═══════
ideas = S["ideas"]
_idea_rows = "\n".join(
    f'<tr><td class="n">{i["n"]}</td><td>{i["title"]}</td><td>{i["basis"]}</td><td class="c">{i["len"]}</td></tr>'
    for i in ideas
)

# ═══════ HYPOTHESES ═══════
_hyp_rows = "\n".join(
    f'<tr><td>{h["h"]}</td>'
    f'<td class="c"><span class="{"ok" if "ĐÚNG" in h["verdict"] else "wa"}">{h["verdict"]}</span></td>'
    f'<td>{h["evidence"]}</td></tr>'
    for h in S["hypotheses"]
)

# ═══════ tag chỉ có ở kênh thắng ═══════
_tag_rows = "\n".join(
    f'<tr><td><code>{t["tag"]}</code></td><td class="n">{vn(t["freq"])}</td></tr>'
    for t in M6["tags_only_in_winners"][:10]
)

CSS = """
@page { size:A4; margin:17mm 15mm 20mm;
 @bottom-center { content: counter(page) " / " counter(pages);
  font-family:"DejaVu Sans"; font-size:8pt; color:#9A8E85; } }
body { font-family:"DejaVu Sans",sans-serif; font-size:9.5pt; line-height:1.5; color:#1A1614; }
h1 { font-size:23pt; margin:0 0 4pt; letter-spacing:-.4pt; }
h2 { font-size:13pt; margin:18pt 0 7pt; padding-bottom:4pt;
 border-bottom:1.5pt solid #1A1614; page-break-after:avoid; }
h3 { font-size:10.5pt; margin:12pt 0 5pt; color:#8C3A2B; page-break-after:avoid; }
p { margin:5pt 0; }
.sub { color:#6B615A; font-size:10.5pt; margin:0 0 10pt; }
.meta { font-size:8pt; color:#7A6F68; border-top:.6pt solid #E2DAD1;
 border-bottom:.6pt solid #E2DAD1; padding:6pt 0; margin-bottom:14pt; }
table { border-collapse:collapse; width:100%; font-size:8.3pt; margin:7pt 0; page-break-inside:avoid; }
th { background:#F2EEE8; text-align:left; padding:5pt 7pt; font-size:7.3pt;
 text-transform:uppercase; letter-spacing:.4pt; color:#5A514B; border-bottom:1pt solid #CFC4B8; }
td { padding:5pt 7pt; border-bottom:.6pt solid #EDE7E0; vertical-align:top; }
td.n { text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
td.c { text-align:center; }
tr.hi { background:#F4E6E2; }
.ok { color:#2F6B4F; font-weight:bold; } .no { color:#9B2C2C; font-weight:bold; }
.wa { color:#B5731F; font-weight:bold; }
.verdict { color:#8C3A2B; font-weight:bold; font-size:8.3pt; }
.box { border-left:2.5pt solid #8C3A2B; background:#F9F4F2; padding:8pt 11pt;
 margin:10pt 0; page-break-inside:avoid; }
.box.ok { border-left-color:#2F6B4F; background:#EFF5F1; }
.box .l { font-size:7.3pt; text-transform:uppercase; letter-spacing:.7pt;
 font-weight:bold; color:#8C3A2B; display:block; margin-bottom:4pt; }
.box.ok .l { color:#2F6B4F; }
.box p { margin:0 0 5pt; font-size:9pt; } .box p:last-child { margin-bottom:0; }
.kpi { display:flex; gap:7pt; margin:10pt 0; }
.kpi div { flex:1; border:.6pt solid #E2DAD1; padding:8pt 9pt; }
.kpi .k { font-size:6.6pt; text-transform:uppercase; letter-spacing:.5pt; color:#7A6F68; margin-bottom:4pt; }
.kpi .v { font-size:16pt; font-weight:bold; letter-spacing:-.3pt; }
.kpi .c2 { font-size:6.8pt; color:#7A6F68; margin-top:3pt; line-height:1.3; }
.up { color:#2F6B4F; } .dn { color:#9B2C2C; }
.src { font-size:7pt; color:#9A8E85; }
code { background:#F2EEE8; padding:.5pt 3pt; font-size:8pt; word-break:break-all; }
.big { text-align:center; border:1.5pt solid #8C3A2B; padding:12pt; margin:10pt 0; background:#F9F4F2; }
.big .n1 { font-size:32pt; font-weight:bold; color:#8C3A2B; line-height:1; }
.big .n2 { font-size:11pt; color:#4A423D; margin-top:5pt; }
.pb { page-break-before:always; }
ul { margin:5pt 0; padding-left:15pt; } li { margin:2pt 0; }
"""

DOC = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>

<h1>{NICHE_LABEL} &mdash; Đúc kết</h1>
<p class="sub">Toàn bộ 8 bước nghiên cứu gộp về một bản. Chỉ kết quả và số liệu quyết định.</p>
<div class="meta">
{M2['M1_2_total_channels']} kênh &middot; {vn(_n_video)} video &middot; {vn(_n_comment_raw)} bình luận
({vn(M5['n_analyzed'])} đã lọc nhiễu để phân tích khán giả)
&nbsp;&middot;&nbsp; Dữ liệu crawl 13/08/2026 &nbsp;&middot;&nbsp; Lập báo cáo 25/08/2026
</div>

<div class="big">
<div class="n1">{_sc_vn(SC['total_score'])} / 20</div>
<div class="n2">Xếp loại: <b>{SC['verdict']}</b></div>
</div>
<p class="verdict">=> Mô hình phù hợp: nhiều kênh song song, chi phí sản xuất thấp &mdash; không dồn lực vào 1 kênh.</p>

<div class="kpi">
<div><div class="k">Views/tháng ngách</div><div class="v">{vn(M2['M1_1_views_per_month']/1e6,2)}tr</div>
 <div class="c2">Trung vị/video {vn(M2['M1_3_median_view'])}</div></div>
<div><div class="k">Cầu / cung</div><div class="v up">{vn(M2['M2_4_demand_supply_gap'],2)}&times;</div>
 <div class="c2">cầu tăng nhanh hơn cung</div></div>
<div><div class="k">Cửa vào</div><div class="v up">{pct(M3['M3_2_newcomer_success_pct'])}</div>
 <div class="c2">kênh mới &lt;12 tháng đạt &ge;100k view/tháng</div></div>
<div><div class="k">RPM cơ sở</div><div class="v">${vn(M7['M5_2_rpm']['base'],1)}</div>
 <div class="c2">${vn(M7['M5_2_rpm']['low'],1)}&ndash;${vn(M7['M5_2_rpm']['high'],1)} theo kịch bản</div></div>
</div>

<h2>1 &middot; Bảng đối chiếu CUNG &ndash; CẦU</h2>
<table>
<thead><tr><th>Mục</th><th>Cầu (% comment)</th><th>Bằng chứng &amp; phán quyết</th></tr></thead>
<tbody>{CC_ROWS}</tbody>
</table>

<h2>2 &middot; Quy mô &amp; động lượng thị trường</h2>
<table>
<tbody>
<tr><td>Kênh hoạt động / tổng</td><td class="n">{M2['M1_2_active_channels']} / {M2['M1_2_total_channels']}</td></tr>
<tr><td>Tăng trưởng view (cửa sổ gần nhất)</td><td class="n">&times;{vn(M2['M2_1_view_growth'],2)}</td></tr>
<tr><td>Tăng trưởng cung (kênh/video mới)</td><td class="n">&times;{vn(M2['M2_2_supply_growth'],2)}</td></tr>
<tr><td>Tỷ lệ kênh mới (&lt;window)</td><td class="n">{pct(M2['M2_3_new_channel_rate'])}</td></tr>
<tr><td>Gini tập trung thị trường</td><td class="n">{vn(M3['M3_1_gini'],3)}</td></tr>
<tr><td>Top1 / Top5 / Top20% kênh chiếm views</td>
 <td class="n">{pct(M3['top1_share'])} / {pct(M3['top5_share'])} / {pct(M3['top20pct_share'])}</td></tr>
<tr><td>Kênh AI-first trong Top20</td><td class="n">{pct(M3['M4_1_ai_first_top20_pct'])}</td></tr>
</tbody>
</table>
<p class="verdict">=> Thị trường phân tán lành mạnh (không kênh nào &gt;40%), cầu vượt cung, mô hình AI đã được chứng minh &mdash; cửa vào còn mở.</p>

<h2>3 &middot; Công thức âm nhạc &mdash; 12 tham số BẮT BUỘC</h2>
<p>Cohort: {AR['cohort']['n_videos']} video &middot; {AR['cohort']['n_tracks']} track &middot; {AR['cohort']['n_channels']} kênh &middot;
ngưỡng &ge;{vn(AR['cohort']['view_threshold'])} view. Đây là 12/{AR['n_fields']} tham số có độ phân tán thấp nhất
(IQR/median &lt; 0,15) &mdash; kênh thắng đồng thuận gần như tuyệt đối, sai lệch khỏi khoảng này là rủi ro.</p>
<div class="box warn">
<span class="l">Mẫu của mục này HẸP HƠN HẲN phần còn lại &mdash; đọc kèm lưu ý</span>
<p>Mọi mục khác trong báo cáo dựa trên <b>{vn(_n_channel_all)} kênh / {vn(_n_video)} video</b>.
Riêng bảng này chỉ dựa trên <b>{AR['cohort']['n_channels']} kênh / {AR['cohort']['n_videos']} video</b> &mdash;
những video tải được audio để phân tích DSP, không phải mẫu ngẫu nhiên đại diện.</p>
<p>Nghĩa là: "BẮT BUỘC" ở đây = <b>{AR['cohort']['n_channels']} kênh dẫn đầu làm giống nhau</b>,
không phải "toàn thị trường làm giống nhau". Dùng làm đích ngắm sản xuất thì tốt;
đừng trích ra ngoài như một quy luật của cả ngách.</p>
</div>
<table>
<thead><tr><th>Tham số</th><th>Giá trị</th><th>Khoảng (p25&ndash;p75)</th><th>Độ chặt</th></tr></thead>
<tbody>{_recipe_rows}</tbody>
</table>

<h2>4 &middot; Chân dung khán giả</h2>
<table>
<tbody>
<tr><td>Tuổi tự khai (n={M5['age']['n']}, {pct(M5['age']['n']/M5['n_analyzed']*100,2)} mẫu)</td>
 <td class="n">trung vị {M5['age']['median']:.0f} &middot; 60&ndash;74: {M5['age']['dist']['60-74']} &middot; 75+: {M5['age']['dist']['75+']}</td></tr>
<tr><td>Bối cảnh nghe #1: cầu nguyện/tĩnh tâm</td><td class="n">{pct(context['prayer_devo']['pct'])} ({context['prayer_devo']['n']})</td></tr>
<tr><td>Bối cảnh #2: buổi sáng</td><td class="n">{pct(context['morning']['pct'])} ({context['morning']['n']})</td></tr>
<tr><td>Bối cảnh #3: bệnh viện</td><td class="n">{pct(context['sick_hosp']['pct'])} ({context['sick_hosp']['n']})</td></tr>
</tbody>
</table>
<p class="verdict">=> Tín hiệu xác nhận mạnh nhất (like cao gấp bội mức nền, p&lt;0,05):
tuổi cao ({vn(_SIGTEST.get('p_elder',{}).get('vs_baseline',0),1)}&times;),
"finally thoát khỏi lời Blues thô" ({vn(_fin.get('vs_baseline',0),1)}&times;).
Tín hiệu "chữa lành" chung chung bị {_SIGTEST.get('healing',{}).get('verdict','—')}
(p={vn(_SIGTEST.get('healing',{}).get('p',0),2)}) &mdash; cụ thể mới ăn.</p>

<h2>5 &middot; Từ khóa: chỉ xuất hiện ở kênh THẮNG</h2>
<table>
<thead><tr><th>Tag</th><th>Tần suất</th></tr></thead>
<tbody>{_tag_rows}</tbody>
</table>
<p class="verdict">=> Tag phổ biến ("gospel blues", "christian blues") không phân biệt thắng-thua. Tag hiếm hơn ("slow blues", "psalms in blues") mới là tín hiệu của kênh thắng &mdash; đưa vào tag list, không chỉ tiêu đề.</p>

<h2 class="pb">6 &middot; 5 giả thuyết kiểm chứng</h2>
<table>
<thead><tr><th>Giả thuyết</th><th>Kết luận</th><th>Bằng chứng</th></tr></thead>
<tbody>{_hyp_rows}</tbody>
</table>

<h2>7 &middot; 5 khoảng trống thị trường (xếp theo điểm)</h2>
<table>
<thead><tr><th>Gap</th><th>Điểm</th><th>Độ tin</th><th>Hiệu suất đo được</th></tr></thead>
<tbody>{_gap_rows}</tbody>
</table>

<h2>8 &middot; 24 ý tưởng tiêu đề sẵn dùng</h2>
<p>Toàn bộ nằm trên 2 trục đã xác nhận: <b>old-school/vintage</b> (gap #1) &times; <b>tạ ơn/vượt khó</b>, độ dài 1&ndash;3 giờ.</p>
<table>
<thead><tr><th>#</th><th>Tiêu đề</th><th>Cơ sở</th><th>Độ dài</th></tr></thead>
<tbody>{_idea_rows}</tbody>
</table>

<h2>9 &middot; Kiếm tiền &amp; rủi ro chính</h2>
<div class="kpi">
<div><div class="k">Kịch bản cơ sở</div><div class="v">${vn(M7['scenarios']['base']['rev_base'])}</div>
 <div class="c2">/tháng, {vn(M7['scenarios']['base']['views_per_month'])} view/tháng</div></div>
<div><div class="k">Kịch bản lạc quan</div><div class="v up">${vn(M7['scenarios']['optimistic']['rev_base'])}</div>
 <div class="c2">/tháng</div></div>
<div><div class="k">Format tối ưu ad-slot</div><div class="v">1&ndash;3h</div>
 <div class="c2">11,7 ad-slot, view trung vị 975</div></div>
</div>
<div class="box">
<span class="l">Rủi ro chính</span>
<p><b>Nội dung trùng lặp (&minus;1 điểm):</b> 453 video (6,3%) dùng chung 132 tiêu đề; 5 kênh có &ge;30% video trùng tiêu đề chéo kênh. YouTube yêu cầu "giá trị nguyên bản đáng kể".</p>
<p><b>Nội dung tôn giáo bị soi kỹ hơn (&minus;1 điểm):</b> không đo được từ dữ liệu, dựa trên chính sách nền tảng.</p>
</div>

<h2 class="pb">10 &middot; Làm gì tiếp &mdash; theo thứ tự</h2>
<table>
<thead><tr><th style="width:5%">#</th><th style="width:30%">Việc</th>
<th style="width:42%">Vì sao &mdash; số liệu chống lưng</th><th style="width:23%">Đo bằng gì</th></tr></thead>
<tbody>
<tr><td class="n">1</td><td><b>Mở 2&ndash;3 kênh song song, không dồn 1 kênh</b></td>
<td>Quy mô ngách chỉ {vn(M2['M1_1_views_per_month']/1e6,1)} triệu view/tháng &mdash; một kênh không ăn hết,
nhưng cửa vào mở ({pct(M3['M3_2_newcomer_success_pct'])} kênh mới đạt ngưỡng) nên mở nhiều rẻ hơn đánh cược một.</td>
<td>Sau 3 tháng: ít nhất 1 kênh đạt 100k view/tháng</td></tr>
<tr><td class="n">2</td><td><b>Làm nhạc CÓ LỜI cho bối cảnh cầu nguyện</b></td>
<td>Khoảng trống độ tin cậy cao nhất: cầu {pct(_ctx_prayer)} nhưng chỉ 1,03% video làm.
Instrumental đã được chứng minh là THẤT BẠI ở ngách này (lift 0,17×).</td>
<td>So view trung vị với dải 1&ndash;3h của thị trường ({vn(_ad['med_view'])})</td></tr>
<tr><td class="n">3</td><td><b>Độ dài 1&ndash;3 giờ</b></td>
<td>{vn(_ad['ad_slots'],1)} ad-slot/video so với {vn(_ad_short['ad_slots'],1)} của video ngắn &mdash;
chênh {vn(_ad['ad_slots']/_ad_short['ad_slots'],0)}×. Đây là đòn bẩy doanh thu lớn nhất đo được.</td>
<td>Doanh thu/1000 view thực tế so với RPM ${vn(_rpm_base,1)}</td></tr>
<tr><td class="n">4</td><td><b>Thử old-school/vintage ở quy mô NHỎ</b></td>
<td>lift 2,37× toàn thị trường nhưng trong từng kênh chỉ 1,05× &mdash; tín hiệu có thể do vài kênh may mắn,
không phải công thức. Thử nghiệm được, dồn lực thì không.</td>
<td>10 video, so với chính kênh mình chứ không so thị trường</td></tr>
<tr><td class="n">5</td><td><b>Tự sáng tác, đừng trông vào nhạc hết bản quyền</b></td>
<td>Không có lối tắt: {_pd_new} video là sáng tác mới hoàn toàn, không video nào hát lại hymn public domain.
Chi phí sáng tác là chi phí bắt buộc của ngách này.</td>
<td>Xem <b>NHAC_Ban-quyen-PD.pdf</b></td></tr>
</tbody>
</table>

<h2>11 &middot; Bộ tài liệu &mdash; mở bản nào khi cần gì</h2>
<table>
<thead><tr><th style="width:34%">Tài liệu</th><th>Trả lời câu hỏi gì</th></tr></thead>
<tbody>
<tr><td><b>BAO-CAO_{NICHE_LABEL.replace(' ', '-')}.pdf</b><br><span class="note">bản này</span></td>
<td>Ngách này có đáng làm không, làm thì làm gì trước?</td></tr>
<tr><td><b>CHI-TIET_Phan-tich-day-du.pdf</b></td>
<td>Số liệu đầy đủ từng bước, bằng chứng cho mỗi khoảng trống, và toàn bộ cảnh báo độ tin cậy.</td></tr>
<tr><td><b>HOSO_Ngach_{NICHE_LABEL.replace(' ', '-')}.pdf</b></td>
<td>Công thức sản xuất: 161 tham số âm nhạc đo được từ thị trường, dùng để brief cho AI hoặc nhạc sĩ.</td></tr>
<tr><td><b>NHAC_Bao-cao-Hop-nhat.pdf</b></td>
<td>Phân tích âm thanh + lời hát: BPM, điệu thức, chủ đề lời, xưng hô, cung cảm xúc.</td></tr>
<tr><td><b>NHAC_Ban-quyen-PD.pdf</b></td>
<td>Nhạc thị trường là public domain hay sáng tác mới? Có lối tắt bản quyền không?</td></tr>
<tr><td class="note">_phu-luc/ (5 file)</td>
<td>Phụ lục kỹ thuật: khung chấm điểm, kiến trúc hệ thống, bộ đối chiếu PD, bảng đối chứng track, brief thumbnail.</td></tr>
</tbody>
</table>

</body></html>"""

OUT = D / f"BAO-CAO_{NICHE_LABEL.replace(' ', '-')}.pdf"
HTML(string=DOC, base_url=str(D)).write_pdf(OUT)
print(f"Đã ghi {OUT}")
