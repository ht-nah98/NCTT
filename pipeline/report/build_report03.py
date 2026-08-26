"""Sinh báo cáo PDF cho STEP_03 — Bản đồ đối thủ."""
import json, pandas as pd, warnings, base64
from pathlib import Path
from weasyprint import HTML
warnings.filterwarnings("ignore")

N=Path("niches/christian-blues"); D=N/"03_competitor"
R=json.load(open(D/"_metrics_raw.json"))
c=pd.read_csv(D/"02_channel_table.csv")

# Đọc điểm THẬT từ scores.json — không hardcode.
# (Bản trước ghi cứng T3=4,4; sau khi sửa bẫy L5 điểm còn 4,25 → PDF lệch với
#  scoring_engine suốt một thời gian. Bài học T27.)
_sc = json.load(open(N/"_state/scores.json"))
T3_REAL = _sc["axes"]["T3"]["score"]
T1_REAL = _sc["axes"]["T1"]["score"]; T2_REAL = _sc["axes"]["T2"]["score"]
T4_REAL = _sc["axes"]["T4"]["score"]
def _vn(x): return f"{x:g}".replace(".", ",")

def img(n): return "data:image/png;base64,"+base64.b64encode((D/n).read_bytes()).decode()
def fm(x,d=0): return f"{x:,.{d}f}"

top=c.nlargest(12,"tot_view")
top_rows="\n".join(
 f'<tr><td><b>{r.handle}</b></td><td class="n">{r.channel_age_months:.1f}</td>'
 f'<td class="n">{int(r.tot_view):,}</td><td class="n">{int(r.n_vid)}</td>'
 f'<td class="n">{r.per_month:.1f}</td><td class="n">{int(r.view_per_vid):,}</td>'
 f'<td>{r.model}</td></tr>' for _,r in top.iterrows())

eff=pd.DataFrame(R["top_efficiency"])
eff_rows="\n".join(
 f'<tr class="{"hi" if i<2 else ""}"><td><b>{r.handle}</b></td><td class="n">{int(r.view_per_vid):,}</td>'
 f'<td class="n">{int(r.n_vid)}</td><td class="n">{r.age_m:.1f}</td>'
 f'<td class="n">{r.per_month:.1f}</td><td>{r.model}</td></tr>'
 for i,r in eff.iterrows())

fast="\n".join(
 f'<tr><td><b>{e["handle"]}</b></td><td class="n">{e["age_m"]:.1f} tháng</td>'
 f'<td class="n">{e["vpm"]:,.0f}</td></tr>' for e in R["M3_3_alt_fastest_success"])

tier_rows="\n".join(f'<tr><td>{k}</td><td class="n">{x}</td>'
 f'<td class="n">{x/53*100:.0f}%</td></tr>' for k,x in R["tier_dist"].items())

a=c[c.n_vid>=20].copy()
q=pd.qcut(a.per_month,4,labels=["Q1 thưa","Q2","Q3","Q4 dày"])
gq=a.groupby(q).agg(n=("handle","size"),pm=("per_month","median"),
                    vpv=("view_per_vid","median"),vpm=("views_per_month","median"))
cad_rows="\n".join(
 f'<tr><td><b>{i}</b></td><td class="n">{int(r.n)}</td><td class="n">{r.pm:.1f}</td>'
 f'<td class="n">{int(r.vpv):,}</td><td class="n">{int(r.vpm):,}</td></tr>'
 for i,r in gq.iterrows())

gm=c.groupby("model").agg(n=("handle","size"),vpv=("view_per_vid","median"),
                          vpm=("views_per_month","median"),age=("channel_age_months","median"))
model_rows="\n".join(
 f'<tr class="{"hi" if i=="ai-first" else ""}"><td><b>{i}</b></td><td class="n">{int(r.n)}</td>'
 f'<td class="n">{r.age:.1f}</td><td class="n">{int(r.vpv):,}</td>'
 f'<td class="n">{int(r.vpm):,}</td></tr>' for i,r in gm.iterrows())

DOC=f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size:A4; margin:17mm 15mm 20mm;
 @bottom-center {{ content counter(page) " / " counter(pages);
  font-family:"DejaVu Sans";font-size:8pt;color:#9A8E85; }} }}
body {{ font-family:"DejaVu Sans",sans-serif;font-size:9.5pt;line-height:1.55;color:#1A1614; }}
h1 {{ font-size:23pt;margin:0 0 6pt;letter-spacing:-.4pt; }}
h2 {{ font-size:13pt;margin:20pt 0 7pt;padding-bottom:4pt;
 border-bottom:1.5pt solid #1A1614;page-break-after:avoid; }}
h3 {{ font-size:10.5pt;margin:14pt 0 5pt;color:#8C3A2B;page-break-after:avoid; }}
p {{ margin:6pt 0; }}
.sub {{ color:#6B615A;font-size:10pt;margin:0 0 10pt; }}
.meta {{ font-size:8pt;color:#7A6F68;border-top:.6pt solid #E2DAD1;
 border-bottom:.6pt solid #E2DAD1;padding:6pt 0;margin-bottom:14pt; }}
table {{ border-collapse:collapse;width:100%;font-size:8.5pt;margin:8pt 0;page-break-inside:avoid; }}
th {{ background:#F2EEE8;text-align:left;padding:5pt 7pt;font-size:7.5pt;
 text-transform:uppercase;letter-spacing:.4pt;color:#5A514B;border-bottom:1pt solid #CFC4B8; }}
td {{ padding:5pt 7pt;border-bottom:.6pt solid #EDE7E0;vertical-align:top; }}
td.n {{ text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap; }}
tr.hi {{ background:#F4E6E2; }}
.ok {{ color:#2F6B4F;font-weight:bold; }} .no {{ color:#9B2C2C;font-weight:bold; }}
.box {{ border-left:2.5pt solid #8C3A2B;background:#F9F4F2;padding:8pt 11pt;
 margin:11pt 0;page-break-inside:avoid; }}
.box.crit {{ border-left-color:#9B2C2C;background:#FBEEEE; }}
.box.ok {{ border-left-color:#2F6B4F;background:#EFF5F1; }}
.box .l {{ font-size:7.5pt;text-transform:uppercase;letter-spacing:.7pt;
 font-weight:bold;color:#8C3A2B;display:block;margin-bottom:4pt; }}
.box.crit .l {{ color:#9B2C2C; }} .box.ok .l {{ color:#2F6B4F; }}
.box p {{ margin:0 0 5pt;font-size:9pt; }} .box p:last-child {{ margin-bottom:0; }}
.kpi {{ display:flex;gap:7pt;margin:11pt 0; }}
.kpi div {{ flex:1;border:.6pt solid #E2DAD1;padding:8pt 9pt; }}
.kpi .k {{ font-size:6.8pt;text-transform:uppercase;letter-spacing:.5pt;color:#7A6F68;margin-bottom:4pt; }}
.kpi .v {{ font-size:17pt;font-weight:bold;letter-spacing:-.3pt; }}
.kpi .c {{ font-size:7pt;color:#7A6F68;margin-top:3pt;line-height:1.3; }}
.up {{ color:#2F6B4F; }} .dn {{ color:#9B2C2C; }} .ac {{ color:#8C3A2B; }}
img {{ width:100%;margin:8pt 0; }}
.half {{ width:49%; }}
.f {{ font-size:7.5pt;color:#7A6F68;text-align:center;margin:-4pt 0 12pt; }}
code {{ background:#F2EEE8;padding:.5pt 3pt;font-size:8.5pt; }}
.formula {{ background:#F7F4F0;border:.6pt solid #E2DAD1;padding:7pt 10pt;
 font-size:8.5pt;margin:7pt 0;line-height:1.7; }}
.pb {{ page-break-before:always; }}
ul {{ margin:6pt 0;padding-left:15pt; }} li {{ margin:3pt 0; }}
</style></head><body>

<h1>Bản đồ đối thủ &mdash; Christian Blues</h1>
<p class="sub">Báo cáo giai đoạn 2 &mdash; 53 kênh đối thủ: ai đang thắng, người mới còn cửa không</p>
<div class="meta">
STEP_03 &nbsp;•&nbsp; Agent A2 &nbsp;•&nbsp; Trục T3 (Cửa gia nhập) + T4 (Phù hợp AI)
&nbsp;•&nbsp; Rubric v1.0 &nbsp;•&nbsp; Dữ liệu crawl 13/08/2026 &nbsp;•&nbsp; Lập ngày 15/08/2026
</div>

<h2>1. Tóm tắt điều hành</h2>

<div class="box ok">
<span class="l">Kết luận: cửa gia nhập ĐANG MỞ &mdash; và mở bất thường</span>
<p><b>61,5% kênh dưới 12 tháng tuổi đã đạt trên 100.000 view mỗi tháng</b> (24 trên 39 kênh).
Đây là tỷ lệ rất cao. Theo rubric, mức trên 40% đã là <b>5 điểm tối đa</b>.</p>
<p>Nghi ngờ &ldquo;winner-takes-most&rdquo; nêu ở báo cáo trước <b>đã được bác bỏ</b>:
kênh lớn nhất chỉ chiếm <b>18,5%</b> tổng view &mdash; không có ai thống trị.</p>
</div>

<div class="kpi">
<div><div class="k">Kênh mới thành công</div><div class="v up">61,5<span style="font-size:10pt">%</span></div>
 <div class="c">24/39 kênh &lt;12 tháng đạt ≥100k view/tháng</div></div>
<div><div class="k">Hệ số Gini</div><div class="v">0,626</div>
 <div class="c">Mức tập trung trung bình</div></div>
<div><div class="k">Kênh lớn nhất chiếm</div><div class="v up">18,5<span style="font-size:10pt">%</span></div>
 <div class="c">Không có kênh thống trị</div></div>
<div><div class="k">AI-first trong top 20</div><div class="v ac">65<span style="font-size:10pt">%</span></div>
 <div class="c">Mô hình AI đã được chứng minh</div></div>
</div>

<h3>Điểm số hai trục</h3>
<table>
<thead><tr><th>Trục</th><th>Trọng số</th><th>Điểm</th><th>Căn cứ</th></tr></thead>
<tbody>
<tr class="hi"><td><b>T3</b> Cửa gia nhập</td><td class="n">25%</td>
 <td class="n up"><b>{_vn(T3_REAL)} / 5</b></td>
 <td>M3.2 = 61,5% (≥40% → 5đ) &times; 0,5 + Gini 0,626 (3đ) &times; 0,3<br>
 <span style="font-size:7.5pt;color:#9B2C2C">M3.3 <b>KHÔNG đo được</b> với 1 snapshot &rarr;
 chia lại trọng số 0,3:0,5 thay vì gán 5đ mặc định</span></td></tr>
<tr class="hi"><td><b>T4</b> Phù hợp AI</td><td class="n">15%</td><td class="n up"><b>5 / 5</b></td>
 <td>M4.1 = 65% (≥60%) và khán giả Gospel thuộc nhóm chấp nhận AI cao nhất</td></tr>
</tbody></table>

<h2>2. Cách đọc các chỉ số</h2>

<h3>2.1. Hệ số Gini &mdash; đo mức độ tập trung</h3>
<div class="formula">
<b>Gini = 0</b> &rarr; mọi kênh chia đều lượt xem<br>
<b>Gini = 1</b> &rarr; một kênh chiếm toàn bộ lượt xem
</div>
<p><b>Christian Blues = 0,626.</b> Để dễ hình dung, đây là mức tương đương phân bố thu nhập
của một nước đang phát triển: có chênh lệch rõ, nhưng không phải độc quyền.</p>
<p><b>So sánh với các ngách khác</b> (từ bảng chấm cũ của bạn):</p>
<table>
<thead><tr><th>Ngách</th><th>Tỷ trọng view của top 20% kênh</th><th>Đánh giá</th></tr></thead>
<tbody>
<tr><td>Trap Soul</td><td class="n">92,4%</td><td class="no">Bị khóa chặt</td></tr>
<tr><td>Phonk</td><td class="n">87,3%</td><td class="no">Bị khóa chặt</td></tr>
<tr><td>Christian/Gospel (ngách cha)</td><td class="n">82,0%</td><td class="no">Bị khóa chặt</td></tr>
<tr class="hi"><td><b>Christian Blues</b></td><td class="n up"><b>63,1%</b></td><td class="ok">Còn mở</td></tr>
<tr><td>R&amp;B</td><td class="n">60,4%</td><td class="ok">Còn mở</td></tr>
</tbody></table>
<p>Đáng chú ý: <b>ngách cha Christian/Gospel bị khóa ở mức 82%</b>, nhưng nhánh Christian Blues
chỉ 63,1%. Đây đúng là <b>cửa sau</b> để vào một thị trường lớn đã bị chiếm chỗ.</p>

<img src="{img('c1_lorenz.png')}" class="half">
<p class="f">Đường cong Lorenz. Càng xa đường chéo thì càng tập trung.</p>

<h3>2.2. M3.2 &mdash; Tỷ lệ kênh mới thành công</h3>
<div class="formula">
<b>M3.2 = % kênh dưới 12 tháng tuổi đạt ≥ 100.000 view/tháng</b>
</div>
<p>Đây là chỉ số <b>quan trọng nhất</b> của trục T3 (trọng số 0,5 trong công thức), vì nó là
bằng chứng <i>trực tiếp</i>: người mới vào ngách này có thắng được không. Gini chỉ là bằng
chứng gián tiếp.</p>
<p><b>Kết quả: 24 trên 39 kênh &mdash; tức 61,5%.</b> Theo thang rubric, trên 40% đã đạt điểm
tối đa 5/5. Ngách này vượt xa ngưỡng đó.</p>

<h2 class="pb">3. Cửa gia nhập (Trục T3)</h2>

<h3>3.1. Kênh trẻ vẫn đạt traction</h3>
<img src="{img('c2_age_vs_reach.png')}">
<p class="f">Mỗi chấm là một kênh. Trục ngang: tuổi kênh. Trục dọc: view mỗi tháng.
Đường xanh: ngưỡng 100k.</p>

<p>Biểu đồ cho thấy điều quan trọng: <b>các chấm nằm trên ngưỡng tập trung ở phía TRÁI</b>
(kênh trẻ), còn các kênh cũ nhất (bên phải, trên 100 tháng tuổi) lại nằm <i>dưới</i> ngưỡng.</p>
<p>Nói cách khác: trong ngách này, <b>thâm niên không phải lợi thế</b>. Kênh mới lập thậm chí
còn làm tốt hơn kênh lâu năm.</p>

<h3>3.2. Những kênh đạt traction nhanh nhất</h3>
<table>
<thead><tr><th>Kênh</th><th>Tuổi khi đạt</th><th>View/tháng hiện tại</th></tr></thead>
<tbody>{fast}</tbody></table>
<p><b>Tuổi trung vị của nhóm thành công: {R['M3_3_alt_median_age_of_successful']:.1f} tháng.</b>
Kênh <code>hopegospelblues</code> đạt hơn 230.000 view mỗi tháng khi <b>mới 0,6 tháng tuổi</b>
&mdash; tức chưa đầy 3 tuần.</p>

<div class="box crit">
<span class="l">Một chỉ số tôi đã phải loại bỏ &mdash; và vì sao</span>
<p>Rubric có yêu cầu đo <b>M3.3 &mdash; thời gian để kênh mới đạt 100.000 view tích lũy</b>.
Tôi đã tính thử và ra kết quả <b>0,4 tháng</b>, nghe rất vô lý.</p>
<p>Kiểm tra lại thì phát hiện chỉ số này <b>không thể đo được với dữ liệu hiện tại</b>.
Lý do: cột <code>view_count</code> ghi lượt xem <b>tích lũy đến ngày crawl</b>, không phải
lượt xem tại thời điểm video vừa đăng. Nên khi cộng dồn, chỉ vài video đầu là đã vượt 100.000
&mdash; con số ra vô nghĩa.</p>
<p><b>Đã thay bằng:</b> tuổi trung vị của nhóm kênh đã đạt traction (6,9 tháng) &mdash; đo được
và mang ý nghĩa tương đương. Muốn đo M3.3 thật thì cần ít nhất 2 lần snapshot.</p>
</div>

<h3>3.3. Mức độ tập trung</h3>
<table>
<thead><tr><th>Chỉ số</th><th>Giá trị</th><th>Ý nghĩa</th></tr></thead>
<tbody>
<tr><td>Kênh lớn nhất chiếm</td><td class="n up">{R['top1_share']:.1f}%</td>
 <td>Không có kênh thống trị. Để so sánh: Afro House có kênh dẫn đầu chiếm ~60%</td></tr>
<tr><td>Top 5 kênh chiếm</td><td class="n">{R['top5_share']:.1f}%</td>
 <td>Chưa tới một nửa &mdash; còn chỗ cho nhóm sau</td></tr>
<tr><td>Top 20% kênh chiếm</td><td class="n">{R['top20pct_share']:.1f}%</td>
 <td>Mở hơn ngách cha 19 điểm phần trăm</td></tr>
</tbody></table>

<div class="box ok">
<span class="l">Bác bỏ nghi ngờ &ldquo;winner-takes-most&rdquo;</span>
<p>Báo cáo trước nêu lo ngại: nhóm Top 20 tăng hiệu suất gấp đôi, có thể là dấu hiệu thị
trường dồn về người thắng, gây khó cho người mới.</p>
<p><b>Dữ liệu bác bỏ điều này.</b> Kênh lớn nhất chỉ chiếm 18,5% tổng view, và 61,5% kênh mới
đã đạt traction. Nhóm Top 20 tăng trưởng <i>cùng lúc</i> với nhóm còn lại (báo cáo trước:
VPD nhóm còn lại cũng tăng ×1,83) &mdash; đây là <b>cả thị trường cùng lên</b>, không phải
kẻ thắng nuốt phần của kẻ thua.</p>
</div>

<h2 class="pb">4. Phân tầng 53 kênh</h2>
<img src="{img('c4_tiers.png')}" class="half">
<table>
<thead><tr><th>Tầng</th><th>Số kênh</th><th>Tỷ lệ</th></tr></thead>
<tbody>{tier_rows}</tbody></table>
<p><b>19 kênh dẫn đầu và thách thức</b> (view/tháng ≥ 200k) so với <b>15 kênh hụt hơi hoặc đã
ngừng</b>. Tỷ lệ đào thải khoảng 28% &mdash; có cạnh tranh nhưng không khắc nghiệt.</p>

<h3>4.1. Top 12 kênh theo tổng lượt xem</h3>
<table>
<thead><tr><th>Kênh</th><th>Tuổi<br>(tháng)</th><th>Tổng view</th><th>Số<br>video</th>
<th>Video/<br>tháng</th><th>View/<br>video</th><th>Mô hình</th></tr></thead>
<tbody>{top_rows}</tbody></table>

<h2>5. Mô hình sản xuất (Trục T4)</h2>

<h3>5.1. Cách phân loại</h3>
<p>Không thể biết chắc kênh nào dùng AI &mdash; YouTube không công bố. Hệ thống <b>suy luận từ
dấu hiệu quan sát được</b>:</p>
<table>
<thead><tr><th>Dấu hiệu</th><th>Ngưỡng</th><th>Vì sao là dấu hiệu của AI-first</th></tr></thead>
<tbody>
<tr><td>Nhịp đăng dày</td><td class="n">≥12 video/tháng</td>
 <td>Sản xuất thủ công khó đạt nhịp này liên tục</td></tr>
<tr><td>Thumbnail đồng nhất</td><td class="n">độ đa dạng &lt;0,15</td>
 <td>Dùng chung một mẫu, sinh hàng loạt</td></tr>
<tr><td>Kênh trẻ</td><td class="n">&lt;18 tháng</td>
 <td>Làn sóng AI music mới xuất hiện gần đây</td></tr>
<tr><td>Thiên mix dài</td><td class="n">độ dài trung vị ≥1 giờ</td>
 <td>Định dạng dễ nhân bản bằng AI nhất</td></tr>
</tbody></table>
<p><i>Độ tin cậy: Vừa.</i> Đây là suy luận gián tiếp, có thể sai với từng kênh cụ thể,
nhưng đủ tin cậy ở mức tổng thể.</p>

<h3>5.2. Kết quả</h3>
<table>
<thead><tr><th>Mô hình</th><th>Số kênh</th><th>Tuổi TV<br>(tháng)</th>
<th>View/video<br>trung vị</th><th>View/tháng<br>trung vị</th></tr></thead>
<tbody>{model_rows}</tbody></table>

<div class="box ok">
<span class="l">M4.1 = 65% top 20 là AI-first &mdash; mô hình đã được chứng minh</span>
<p>Đây <b>không phải phỏng đoán</b> rằng &ldquo;AI có thể làm được dòng nhạc này&rdquo;.
Đây là bằng chứng thực nghiệm: <b>13 trên 20 kênh dẫn đầu đã và đang dùng mô hình AI-first,
và họ đang thắng</b>.</p>
<p>Cộng với dữ liệu khảo sát Wavelength (14.000 người Mỹ): khán giả Gospel thuộc <b>nhóm cởi
mở với nhạc AI cao nhất</b>, vì họ ít đặt nặng yếu tố &ldquo;nghệ sĩ&rdquo; mà tập trung vào
trải nghiệm nghe. Hai bằng chứng độc lập cùng chỉ một hướng &rarr; <b>T4 = 5/5</b>.</p>
</div>

<p><b>Lưu ý về nhóm artist/rebroadcast:</b> chỉ có 4 kênh, nhưng view/video cao nhất
(43.365). Đây là các kênh cũ (trung vị 196 tháng tuổi) phát lại nhạc gospel kinh điển.
Họ có tệp khán giả trung thành nhưng <b>view/tháng thấp</b> (42.298) vì đăng rất thưa
&mdash; không phải đối thủ cạnh tranh trực tiếp.</p>

<h2 class="pb">6. Phát hiện chiến lược: đánh đổi giữa nhịp đăng và chất lượng</h2>

<img src="{img('c3_cadence_tradeoff.png')}">

<table>
<thead><tr><th>Nhóm nhịp đăng</th><th>Số kênh</th><th>Video/tháng<br>(trung vị)</th>
<th>View mỗi video<br>(trung vị)</th><th>Tổng view/tháng<br>(trung vị)</th></tr></thead>
<tbody>{cad_rows}</tbody></table>

<div class="box">
<span class="l">Hai chỉ số đi ngược chiều nhau</span>
<p><b>Tương quan nhịp đăng với view mỗi video: &minus;0,311</b> (âm) &mdash; đăng càng dày thì
mỗi video càng ít view.</p>
<p><b>Tương quan nhịp đăng với tổng view mỗi tháng: +0,420</b> (dương) &mdash; nhưng đăng càng
dày thì tổng tiếp cận càng lớn.</p>
<p>Cụ thể: nhóm đăng thưa nhất có <b>10.987 view/video</b> nhưng chỉ <b>43.961 view/tháng</b>.
Nhóm đăng dày nhất chỉ có <b>7.605 view/video</b> nhưng đạt <b>232.752 view/tháng</b>
&mdash; gấp <b>5,3 lần</b>.</p>
</div>

<p><b>Hàm ý chiến lược:</b> trong ngách này, <b>số lượng thắng chất lượng</b> nếu mục tiêu là
tổng lượt xem. Mất khoảng 30% chất lượng mỗi video nhưng đổi lại gấp 5 lần tổng tiếp cận.
Điều này phù hợp với mô hình sản xuất AI-first.</p>
<p><i>Cảnh báo:</i> đây là <b>tương quan, chưa phải nhân quả</b>. Có thể các kênh đăng dày vốn
đã có nguồn lực tốt hơn. Sẽ kiểm chứng thêm ở STEP_04 bằng nhóm đối chứng.</p>

<h3>6.1. Ngoại lệ đáng học: hiệu suất mỗi video cao nhất</h3>
<table>
<thead><tr><th>Kênh</th><th>View/video</th><th>Số video</th><th>Tuổi<br>(tháng)</th>
<th>Video/tháng</th><th>Mô hình</th></tr></thead>
<tbody>{eff_rows}</tbody></table>

<div class="box">
<span class="l">Ba hình mẫu khác nhau cùng thành công</span>
<p><b>1. vintage_gospel_vgx</b> &mdash; 70.244 view mỗi video với chỉ <b>43 video</b> và nhịp
đăng thưa (5,5/tháng). Đây là mô hình <b>ít mà tinh</b>. Kênh đáng nghiên cứu kỹ nhất
ở STEP_04.</p>
<p><b>2. goldensoulworship</b> &mdash; 50.128 view/video, nhưng đăng <b>21,6 video/tháng</b>
và kênh mới <b>2,8 tháng tuổi</b>. Đây là mô hình <b>vừa nhiều vừa tốt</b> &mdash; hiếm và
đáng học nhất.</p>
<p><b>3. stillworshipmusic</b> &mdash; 511 video, 32,3 video/tháng, đạt 1,18 triệu view/tháng.
Mô hình <b>công nghiệp hóa</b> &mdash; chất lượng mỗi video thấp hơn nhưng tổng tiếp cận
lớn nhất ngách.</p>
</div>

<h2>7. Độ tin cậy và điều chưa biết</h2>
<table>
<thead><tr><th>Kết luận</th><th>Độ tin cậy</th><th>Lý do</th></tr></thead>
<tbody>
<tr><td>Cửa gia nhập còn mở (M3.2 = 61,5%)</td><td class="ok">Cao</td>
 <td>Đếm trực tiếp, không suy luận</td></tr>
<tr><td>Không có winner-takes-most</td><td class="ok">Cao</td>
 <td>Tính từ tổng view thực tế</td></tr>
<tr><td>65% top 20 là AI-first</td><td>Vừa</td>
 <td>Suy luận từ dấu hiệu gián tiếp, không có xác nhận</td></tr>
<tr><td>Đăng dày → tổng view cao hơn</td><td>Vừa</td>
 <td>Tương quan, chưa chứng minh nhân quả</td></tr>
<tr><td>Thời gian đạt traction</td><td class="no">Thấp</td>
 <td><b>Không đo được</b> &mdash; cần ≥2 snapshot</td></tr>
</tbody></table>

<h3>Bằng chứng phản bác</h3>
<ul>
<li><b>Dữ liệu chỉ có 53 kênh còn tồn tại.</b> Những kênh đã thất bại và bị xóa không có
trong dữ liệu &mdash; đây là <b>thiên lệch sống sót</b>. Tỷ lệ thành công thật của người mới
có thể thấp hơn 61,5%.</li>
<li><b>Ngưỡng 100k view/tháng có thể quá dễ.</b> Nếu nâng lên 500k thì chỉ còn 3 kênh
đạt &mdash; kết luận sẽ khác hẳn.</li>
<li><b>Phân loại AI-first dựa vào nhịp đăng</b> có thể nhầm với kênh có đội ngũ sản xuất lớn.</li>
<li><b>Gini 0,626 tính trên tổng view tích lũy</b>, mà kênh cũ có lợi thế thời gian. Nếu tính
trên view/tháng thì mức tập trung có thể khác.</li>
</ul>

<h2>8. Việc tiếp theo</h2>
<table>
<thead><tr><th>Ưu tiên</th><th>Việc</th><th>Vì sao</th></tr></thead>
<tbody>
<tr><td class="ac"><b>Cao</b></td><td>STEP_04 &mdash; Sàng lọc đối chứng</td>
 <td>Giải mã 435 video outlier so với 161 video đối chứng. Kiểm chứng giả thuyết định dạng ngắn
 và đánh đổi nhịp đăng.</td></tr>
<tr><td class="ac"><b>Cao</b></td><td>Giải mã <code>vintage_gospel_vgx</code> và <code>goldensoulworship</code></td>
 <td>Hai hình mẫu trái ngược nhưng cùng hiệu quả cao</td></tr>
<tr><td>Vừa</td><td>Chạy thêm snapshot</td>
 <td>Mở khóa chỉ số M3.3 và nâng tin cậy trục T2</td></tr>
</tbody></table>

<div class="box ok">
<span class="l">Tổng điểm tạm tính sau 4 trục</span>
<p>T1 = {_vn(T1_REAL)}/5 (20%) &nbsp;•&nbsp; T2 = {_vn(T2_REAL)}/5 (25%) &nbsp;•&nbsp;
T3 = {_vn(T3_REAL)}/5 (25%) &nbsp;•&nbsp; T4 = {_vn(T4_REAL)}/5 (15%)</p>
<p>Phần đã chấm chiếm 85% trọng số, quy đổi được
<b>{(T1_REAL*0.20+T2_REAL*0.25+T3_REAL*0.25+T4_REAL*0.15)*20/5:.1f} trên 17 điểm</b>
tương ứng. Còn thiếu T5 (kiếm tiền) và T6 (rủi ro) ở STEP_07.</p>
</div>

</body></html>"""

out=N/"99_report/STEP03_Ban-do-Doi-thu.pdf"
HTML(string=DOC,base_url=".").write_pdf(out)
print(f"PDF: {out} ({out.stat().st_size/1024:.0f} KB)")
