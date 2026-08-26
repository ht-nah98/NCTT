"""Sinh báo cáo PDF cho STEP_01+02."""
import json, pandas as pd, warnings, base64
from pathlib import Path
from weasyprint import HTML
warnings.filterwarnings("ignore")

N = Path("niches/christian-blues")
P = N/"00_input/processed"
M = N/"02_market"
R = json.load(open(M/"_metrics_raw.json"))
q = pd.read_csv(P/"quality_audit.csv")
s = pd.read_csv(P/"selection_validation.csv")
v = pd.read_parquet(P/"videos_enriched.parquet")

def img(name):
    return "data:image/png;base64," + base64.b64encode((M/name).read_bytes()).decode()

def rows(df, cols, fmt=None):
    out = []
    for _, r in df.iterrows():
        tds = []
        for c in cols:
            val = r[c]
            if c == "pass":
                val = '<span class="ok">✓ đạt</span>' if val else '<span class="no">✗ không đạt</span>'
            tds.append(f"<td>{val}</td>")
        out.append("<tr>" + "".join(tds) + "</tr>")
    return "\n".join(out)

band = (v.groupby("duration_band")
          .agg(n=("vpd","size"), vpd=("vpd","median"), mv=("view_count","median"))
          .sort_values("vpd", ascending=False))
band_rows = "\n".join(
    f'<tr class="{"hi" if b in ("Shorts","1-6m") else ""}"><td><b>{b}</b></td>'
    f'<td class="n">{int(r.n):,}</td><td class="n">{r.vpd:.1f}</td>'
    f'<td class="n">{int(r.mv):,}</td></tr>'
    for b, r in band.iterrows())

geo_rows = "\n".join(f'<tr><td>{k}</td><td class="n">{x}</td>'
                     f'<td class="n">{x/53*100:.1f}%</td></tr>'
                     for k, x in list(R["geo"].items())[:6])

HTML_DOC = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size:A4; margin:17mm 15mm 20mm;
  @bottom-center {{ content counter(page) " / " counter(pages);
    font-family:"DejaVu Sans"; font-size:8pt; color:#9A8E85; }} }}
body {{ font-family:"DejaVu Sans",sans-serif; font-size:9.5pt; line-height:1.55;
  color:#1A1614; }}
h1 {{ font-size:23pt; margin:0 0 6pt; letter-spacing:-.4pt; }}
h2 {{ font-size:13pt; margin:20pt 0 7pt; padding-bottom:4pt;
  border-bottom:1.5pt solid #1A1614; page-break-after:avoid; }}
h3 {{ font-size:10.5pt; margin:14pt 0 5pt; color:#8C3A2B; page-break-after:avoid; }}
p {{ margin:6pt 0; }}
.sub {{ color:#6B615A; font-size:10pt; margin:0 0 10pt; }}
.meta {{ font-size:8pt; color:#7A6F68; border-top:.6pt solid #E2DAD1;
  border-bottom:.6pt solid #E2DAD1; padding:6pt 0; margin-bottom:14pt; }}
table {{ border-collapse:collapse; width:100%; font-size:8.5pt; margin:8pt 0;
  page-break-inside:avoid; }}
th {{ background:#F2EEE8; text-align:left; padding:5pt 7pt; font-size:7.5pt;
  text-transform:uppercase; letter-spacing:.4pt; color:#5A514B;
  border-bottom:1pt solid #CFC4B8; }}
td {{ padding:5pt 7pt; border-bottom:.6pt solid #EDE7E0; vertical-align:top; }}
td.n {{ text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }}
tr.hi {{ background:#F4E6E2; }}
.ok {{ color:#2F6B4F; font-weight:bold; }}
.no {{ color:#9B2C2C; font-weight:bold; }}
.box {{ border-left:2.5pt solid #8C3A2B; background:#F9F4F2; padding:8pt 11pt;
  margin:11pt 0; page-break-inside:avoid; }}
.box.crit {{ border-left-color:#9B2C2C; background:#FBEEEE; }}
.box.ok {{ border-left-color:#2F6B4F; background:#EFF5F1; }}
.box .l {{ font-size:7.5pt; text-transform:uppercase; letter-spacing:.7pt;
  font-weight:bold; color:#8C3A2B; display:block; margin-bottom:4pt; }}
.box.crit .l {{ color:#9B2C2C; }} .box.ok .l {{ color:#2F6B4F; }}
.box p {{ margin:0 0 5pt; font-size:9pt; }} .box p:last-child {{ margin-bottom:0; }}
.kpi {{ display:flex; gap:7pt; margin:11pt 0; }}
.kpi div {{ flex:1; border:.6pt solid #E2DAD1; padding:8pt 9pt; }}
.kpi .k {{ font-size:6.8pt; text-transform:uppercase; letter-spacing:.5pt;
  color:#7A6F68; margin-bottom:4pt; }}
.kpi .v {{ font-size:17pt; font-weight:bold; letter-spacing:-.3pt; }}
.kpi .c {{ font-size:7pt; color:#7A6F68; margin-top:3pt; line-height:1.3; }}
.up {{ color:#2F6B4F; }} .dn {{ color:#9B2C2C; }} .ac {{ color:#8C3A2B; }}
img {{ width:100%; margin:8pt 0; }}
.f {{ font-size:7.5pt; color:#7A6F68; text-align:center; margin:-4pt 0 12pt; }}
code {{ background:#F2EEE8; padding:.5pt 3pt; font-size:8.5pt; }}
.formula {{ background:#F7F4F0; border:.6pt solid #E2DAD1; padding:7pt 10pt;
  font-size:8.5pt; margin:7pt 0; line-height:1.7; }}
.pb {{ page-break-before:always; }}
ul {{ margin:6pt 0; padding-left:15pt; }} li {{ margin:3pt 0; }}
</style></head><body>

<h1>Nghiên cứu ngách Christian Blues</h1>
<p class="sub">Báo cáo giai đoạn 1 &mdash; Nền móng dữ liệu, Quy mô thị trường và Động lượng tăng trưởng</p>
<div class="meta">
STEP_01 + STEP_02 &nbsp;•&nbsp; Agent A0 + A1 &nbsp;•&nbsp; Rubric v1.0 &nbsp;•&nbsp;
Dữ liệu crawl 13/08/2026 &nbsp;•&nbsp; 53 kênh · 7.193 video · 145.150 bình luận &nbsp;•&nbsp;
Lập ngày 15/08/2026
</div>

<h2>1. Tóm tắt điều hành</h2>

<div class="box ok">
<span class="l">Kết luận: ĐI TIẾP — ngách vượt qua cổng quyết định</span>
<p>Chỉ số cầu/cung <b>M2.4 = 1.305</b>, nghĩa là <b>nhu cầu người xem đang tăng nhanh hơn
lượng nội dung được sản xuất 30,5%</b>. Ngưỡng đi tiếp là ≥ 1.0, nên ngách này vượt qua khá thoải mái.</p>
<p>Ngách còn rất trẻ: <b>74% số kênh dưới 12 tháng tuổi</b>, và cả nhóm dẫn đầu lẫn nhóm
kênh nhỏ đều đang cải thiện hiệu suất. Không có dấu hiệu bão hòa thật.</p>
</div>

<div class="kpi">
<div><div class="k">Cầu / Cung (M2.4)</div><div class="v up">1.305</div>
  <div class="c">Ngưỡng đi tiếp ≥ 1.0</div></div>
<div><div class="k">View mỗi tháng</div><div class="v">7,45<span style="font-size:10pt">tr</span></div>
  <div class="c">12 tháng gần nhất</div></div>
<div><div class="k">Kênh &lt; 12 tháng</div><div class="v up">73,6<span style="font-size:10pt">%</span></div>
  <div class="c">39 trên 53 kênh</div></div>
<div><div class="k">Kênh Tier-1</div><div class="v ac">62,3<span style="font-size:10pt">%</span></div>
  <div class="c">Mỹ, Anh, Canada, Úc</div></div>
</div>

<h3>Phát hiện quan trọng nhất: một cái bẫy suýt dẫn đến kết luận ngược</h3>

<div class="box crit">
<span class="l">Cảnh báo phương pháp — xin đọc kỹ phần này</span>
<p>Ở lần khảo sát sơ bộ trước, tôi báo cáo với bạn rằng ngách <b>đang bị pha loãng</b>
với M2.4 ≈ 0,35. <b>Kết luận đó SAI.</b> Con số đúng là <b>1,305</b> &mdash; ngược hoàn toàn.</p>
<p>Nguyên nhân: tôi so sánh video đăng trong 90 ngày gần nhất với video đăng trước đó.
Nhưng <b>video mới chưa kịp tích lũy view</b>. Trong nhóm 90 ngày gần, chỉ <b>36%</b> video
đã đủ 60 ngày tuổi để coi là &ldquo;chín&rdquo;. So sánh như vậy giống như so chiều cao một
đứa trẻ 5 tuổi với một người 30 tuổi rồi kết luận loài người đang lùn đi.</p>
<p>Báo cáo này đã sửa: chỉ so sánh các cửa sổ thời gian mà <b>mọi video đều đã chín</b>.</p>
</div>

<h2>2. Cách đọc các con số trong báo cáo này</h2>

<p>Trước khi vào chi tiết, xin giải thích ba khái niệm được dùng xuyên suốt. Hiểu ba khái niệm
này thì đọc phần sau sẽ rất nhanh.</p>

<h3>2.1. VPD &mdash; View mỗi ngày</h3>
<div class="formula"><b>VPD = tổng view của video ÷ số ngày kể từ khi đăng</b></div>
<p><b>Vì sao cần:</b> một video đăng 1 năm trước có 10.000 view <i>không</i> mạnh bằng video
đăng 1 tháng trước cũng có 10.000 view. VPD đưa hai video về cùng một mặt bằng để so sánh
công bằng. Đây là thước đo <b>hiệu suất thật</b>.</p>

<h3>2.2. Video &ldquo;đã chín&rdquo; (matured)</h3>
<div class="formula"><b>Đã chín = video đăng được ít nhất 60 ngày</b></div>
<p><b>Vì sao cần:</b> video mới đăng vẫn đang tích view. Nếu trộn video mới vào phép so sánh,
số liệu sẽ bị kéo xuống một cách giả tạo. Trong dữ liệu này có <b>5.609 video đã chín</b>
trên tổng 7.193 (78%).</p>

<h3>2.3. M2.4 &mdash; Chỉ số cầu/cung</h3>
<div class="formula">
<b>M2.1 (cầu)</b> = tổng view giai đoạn gần ÷ tổng view giai đoạn trước<br>
<b>M2.2 (cung)</b> = số video giai đoạn gần ÷ số video giai đoạn trước<br>
<b>M2.4 = M2.1 ÷ M2.2</b>
</div>
<p><b>Cách hiểu:</b></p>
<ul>
<li><b>M2.4 &gt; 1</b> &rarr; người xem tăng nhanh hơn số video &rarr; miếng bánh cho mỗi
người làm đang <i>to ra</i> &rarr; cơ hội tốt</li>
<li><b>M2.4 ≈ 1</b> &rarr; cân bằng</li>
<li><b>M2.4 &lt; 1</b> &rarr; số video tăng nhanh hơn người xem &rarr; miếng bánh mỗi người
đang <i>nhỏ lại</i> &rarr; thị trường đang bão hòa</li>
</ul>

<h2 class="pb">3. STEP_01 &mdash; Nền móng dữ liệu</h2>

<p>Mục tiêu bước này: biến dữ liệu crawl thô thành nền phân tích tin cậy, và <b>lọc bớt</b>
để chỉ phân tích phần dữ liệu thật sự có tín hiệu.</p>

<h3>3.1. Kiểm toán chất lượng dữ liệu</h3>
<table>
<thead><tr><th>Kiểm tra</th><th>Kết quả</th><th>Đánh giá</th><th>Ghi chú</th></tr></thead>
<tbody>
{rows(q, ["check","value","pass","note"])}
</tbody></table>

<div class="box">
<span class="l">Hai hạn chế cần bạn biết</span>
<p><b>1. Chỉ có 1 lần chụp số liệu (snapshot).</b> Dữ liệu ghi nhận view tại một thời điểm duy
nhất, không phải chuỗi theo dõi. Vì vậy mọi phân tích động lượng đều <b>suy ra từ ngày đăng</b>
chứ không đo trực tiếp. Độ tin cậy trục Động lượng vì thế chỉ ở mức <b>Vừa</b>, không phải Cao.
<i>Khắc phục:</i> chạy thêm snapshot cách nhau 7&ndash;14 ngày.</p>
<p><b>2. Bảng media_probe chỉ phủ 0,6%</b> (40 trên 7.193 video). Không đủ để kết luận bất cứ
điều gì về tempo, tông nhạc hay đặc trưng âm thanh. Báo cáo này <b>không dùng</b> bảng đó.</p>
</div>

<h3>3.2. Lọc chọn lọc &mdash; vì sao không phân tích toàn bộ</h3>

<p>Dữ liệu có 7.193 video và 145.150 bình luận. Phân tích hết vừa tốn kém vừa nhiễu: phần lớn
video có rất ít view (trung vị chỉ 1.687 view), và phần lớn bình luận chỉ là &ldquo;Amen 🙏&rdquo;.
Hệ thống lọc theo <b>4 rổ video</b> và <b>3 tầng bình luận</b>:</p>

<table>
<thead><tr><th>Rổ</th><th>Điều kiện</th><th>Số lượng</th><th>Vì sao cần rổ này</th></tr></thead>
<tbody>
<tr><td><b>B1 Outlier</b></td><td>Vượt trung vị kênh ≥ 5 lần, và ≥ 20.000 view</td>
  <td class="n">435</td><td>Đây là các video &ldquo;nổ&rdquo; &mdash; nhóm để đối chứng với B4</td></tr>
<tr><td><b>B2 Đang lên</b></td><td>Đăng ≤ 90 ngày, VPD thuộc top 10%</td>
  <td class="n">366</td><td>Bắt xu hướng <i>hiện tại</i>, không phải quá khứ</td></tr>
<tr><td><b>B3 Đại diện</b></td><td>Top 5 video của mỗi kênh</td>
  <td class="n">264</td><td>Đảm bảo cả 53 kênh đều có mặt, kể cả kênh nhỏ</td></tr>
<tr class="hi"><td><b>B4 Đối chứng</b></td><td>Dưới trung vị kênh ≤ 0,2 lần, nhưng ≥ 500 view</td>
  <td class="n">161</td><td><b>Video THẤT BẠI</b> &mdash; để so sánh có kiểm soát</td></tr>
</tbody></table>

<div class="box ok">
<span class="l">Vì sao rổ B4 (video thất bại) là quan trọng nhất</span>
<p>Nếu chỉ nhìn video thắng, ta sẽ kết luận sai. Ví dụ: thấy video thắng thường có tiêu đề dài
60 ký tự rồi kết luận &ldquo;tiêu đề dài thì thắng&rdquo;. Nhưng nếu video <i>thua</i> cũng có
tiêu đề dài 60 ký tự, thì độ dài tiêu đề <b>không liên quan gì</b> đến thắng thua.</p>
<p>Có nhóm đối chứng thì mới phân biệt được <b>yếu tố thật</b> và <b>trùng hợp</b>. Đây là điều
cả script gốc lẫn bảng chấm thủ công đều thiếu.</p>
</div>

<h3>3.3. Kiểm chứng bộ lọc</h3>
<table>
<thead><tr><th>Kiểm tra</th><th>Kết quả</th><th>Mục tiêu</th><th>Đánh giá</th></tr></thead>
<tbody>
{rows(s, ["check","value","target","pass"])}
</tbody></table>

<p><b>Con số đáng chú ý nhất: phủ view 80,6%.</b> Nghĩa là 965 video được chọn (13,4% tổng số)
lại chiếm <b>80,6% toàn bộ lượt xem</b> của ngách. Ta đã bỏ qua 86,6% số video nhưng chỉ mất
19,4% lượt xem &mdash; đúng là phần thị trường không ai xem.</p>

<h2 class="pb">4. STEP_02 &mdash; Quy mô thị trường (Trục T1)</h2>

<table>
<thead><tr><th>Chỉ số</th><th>Giá trị</th><th>Cách tính &amp; ý nghĩa</th></tr></thead>
<tbody>
<tr><td><b>M1.1</b> View mỗi tháng</td><td class="n">{R['M1_1_views_per_month']:,.0f}</td>
  <td>Tổng view của video đăng trong 12 tháng gần nhất, chia 12. Đây là quy mô nhu cầu thực.</td></tr>
<tr><td><b>M1.2</b> Kênh hoạt động</td><td class="n">{R['M1_2_active_channels']} / {R['M1_2_total_channels']}</td>
  <td>Kênh có đăng ít nhất 1 video trong 90 ngày qua. 5 kênh đã ngừng hoạt động.</td></tr>
<tr><td><b>M1.3</b> View trung vị</td><td class="n">{R['M1_3_median_view']:,.0f}</td>
  <td>Chỉ tính video đã chín. Dùng <b>trung vị</b> chứ không dùng trung bình.</td></tr>
<tr><td>(so sánh) View trung bình</td><td class="n">{R['M1_3_mean_view']:,.0f}</td>
  <td>Cao gấp <b>10 lần</b> trung vị &mdash; minh chứng vì sao không được dùng trung bình.</td></tr>
</tbody></table>

<div class="box">
<span class="l">Vì sao dùng trung vị chứ không dùng trung bình</span>
<p>View trung bình là <b>17.009</b>, nhưng view trung vị chỉ <b>1.687</b> &mdash; chênh 10 lần.
Lý do: một số ít video cực nổ (trên 1 triệu view) kéo trung bình lên rất cao, trong khi
phần lớn video thực tế chỉ vài trăm view.</p>
<p>Nếu lập kế hoạch dựa trên trung bình, bạn sẽ kỳ vọng mỗi video được 17.000 view &mdash; và
thất vọng. Trung vị 1.687 mới là con số <b>một video điển hình</b> thật sự đạt được.</p>
</div>

<p><b>Điểm T1 theo rubric:</b> M1.1 = 7,45 triệu view/tháng, nằm trong khoảng 3&ndash;8 triệu
&rarr; <b>2 điểm trên 5</b>. Đây là ngách <i>cỡ vừa</i>, không phải ngách lớn.</p>

<h2>5. STEP_02 &mdash; Động lượng tăng trưởng (Trục T2)</h2>

<h3>5.1. Cái bẫy: hai cách tính cho hai kết luận ngược nhau</h3>

<table>
<thead><tr><th>Cách tính</th><th>Cửa sổ so sánh</th><th>% video đã chín</th><th>M2.4</th><th>Kết luận</th></tr></thead>
<tbody>
<tr><td>Ngây thơ (SAI)</td><td>0&ndash;90 ngày vs 90&ndash;180 ngày</td>
  <td class="n">36%</td><td class="n dn">{R['_naive_M2_4']:.3f}</td><td class="no">Ngách đang sụp</td></tr>
<tr class="hi"><td><b>Đã sửa (ĐÚNG)</b></td><td>60&ndash;150 ngày vs 150&ndash;240 ngày</td>
  <td class="n">100%</td><td class="n up"><b>{R['M2_4_demand_supply_gap']:.3f}</b></td>
  <td class="ok">Ngách đang khỏe</td></tr>
</tbody></table>

<p>Cùng một bộ dữ liệu, chỉ khác cách chọn cửa sổ thời gian, cho ra hai kết luận trái ngược.
Cách đúng là <b>chọn hai cửa sổ mà mọi video đều đã chín</b>, để so sánh công bằng.</p>

<h3>5.2. Kết quả sau khi sửa</h3>
<table>
<thead><tr><th>Chỉ số</th><th>Giá trị</th><th>Dữ liệu thô</th><th>Ý nghĩa</th></tr></thead>
<tbody>
<tr><td><b>M2.1</b> Tăng trưởng cầu</td><td class="n up">{R['M2_1_view_growth']:.3f}</td>
  <td class="n">{R['_w_prev_views']:,} → {R['_w_now_views']:,}</td>
  <td>Lượt xem tăng <b>61,8%</b></td></tr>
<tr><td><b>M2.2</b> Tăng trưởng cung</td><td class="n">{R['M2_2_supply_growth']:.3f}</td>
  <td class="n">{R['_w_prev_videos']:,} → {R['_w_now_videos']:,} video</td>
  <td>Nội dung tăng <b>24,0%</b></td></tr>
<tr><td><b>M2.3</b> Tỷ lệ kênh mới</td><td class="n up">{R['M2_3_new_channel_rate']:.1f}%</td>
  <td class="n">39 / 53 kênh</td><td>Ngách hình thành trong 1 năm</td></tr>
<tr class="hi"><td><b>M2.4</b> Cầu ÷ Cung</td><td class="n up"><b>{R['M2_4_demand_supply_gap']:.3f}</b></td>
  <td class="n">1,618 ÷ 1,240</td>
  <td><b>Cầu tăng nhanh hơn cung 30,5%</b></td></tr>
</tbody></table>

<img src="{img('c3_supply_demand.png')}">
<p class="f">Cột xám: số video đăng mỗi tháng (cung). Đường đỏ: tổng lượt xem (cầu).
Cầu dốc hơn cung.</p>

<h3>5.3. Kiểm tra pha loãng &mdash; tách hai giả thuyết</h3>

<p>Quy trình bắt buộc phải phân biệt hai khả năng khi thấy view trung vị giảm:</p>
<ul>
<li><b>H1</b> &mdash; Kênh kém kéo trung vị xuống, nhưng kênh tốt vẫn khỏe</li>
<li><b>H2</b> &mdash; Cả ngách suy giảm, kể cả nhóm dẫn đầu</li>
</ul>

<table>
<thead><tr><th>Phân khúc</th><th>View thô<br>(2025-08 → 2026-05)</th><th>VPD chuẩn hóa tuổi<br>(2025-08 → 2026-05)</th><th>Diễn giải</th></tr></thead>
<tbody>
<tr><td>Toàn ngách</td><td class="n dn">×{R['H_all_median_ratio']:.2f}</td>
  <td class="n up">×{R['H_all_vpd_ratio']:.2f}</td><td>Thô giảm, thực tế tăng</td></tr>
<tr><td>Top 20 kênh</td><td class="n dn">×{R['H_top20_median_ratio']:.2f}</td>
  <td class="n up"><b>×{R['H_top20_vpd_ratio']:.2f}</b></td><td>Hiệu suất <b>gấp đôi</b></td></tr>
<tr><td>33 kênh còn lại</td><td class="n dn">×{R['H_rest_median_ratio']:.2f}</td>
  <td class="n up">×{R['H_rest_vpd_ratio']:.2f}</td><td>Cũng cải thiện mạnh</td></tr>
</tbody></table>

<img src="{img('c1_maturation_trap.png')}">
<p class="f">Cùng một dữ liệu, hai thước đo. Trái: view thô (bị nhiễu bởi tuổi video).
Phải: VPD đã chuẩn hóa &mdash; thước đo đúng.</p>

<img src="{img('c2_vpd_segments.png')}">
<p class="f">Cả ba phân khúc đều đi lên. Không nhóm nào suy giảm.</p>

<div class="box ok">
<span class="l">Kết luận: H0 &mdash; không có pha loãng thật</span>
<p>Cả hai giả thuyết H1 và H2 đều <b>bị bác bỏ</b>. Khi đo bằng VPD (thước đo đã chuẩn hóa
theo tuổi video), <b>không phân khúc nào suy giảm</b> &mdash; ngược lại, tất cả đều cải thiện.
Nhóm Top 20 tăng hiệu suất <b>gấp đôi</b>.</p>
<p>Việc &ldquo;view trung vị giảm 70%&rdquo; mà tôi báo cáo lần trước là <b>ảo giác thống kê</b>
do video mới chưa kịp tích view, không phải dấu hiệu thị trường xấu đi.</p>
</div>

<h2 class="pb">6. Cơ cấu thị trường</h2>

<h3>6.1. Tuổi kênh &mdash; ngách rất trẻ</h3>
<img src="{img('c4_channel_age.png')}">
<p>39 trên 53 kênh (73,6%) được lập trong vòng 12 tháng. Chỉ 4 kênh trên 5 năm tuổi.
Nghĩa là <b>không có đối thủ thâm niên nào chặn cửa</b> &mdash; hầu hết đối thủ cũng chỉ mới
bắt đầu như bạn.</p>

<h3>6.2. Địa lý</h3>
<table>
<thead><tr><th>Quốc gia</th><th>Số kênh</th><th>Tỷ lệ</th></tr></thead>
<tbody>{geo_rows}</tbody></table>
<p><b>62,3% kênh thuộc nhóm Tier-1</b> (Mỹ, Anh, Canada, Úc, New Zealand). Đây là nhóm thị
trường có RPM cao nhất &mdash; tín hiệu tốt cho khả năng kiếm tiền, sẽ phân tích kỹ ở STEP_07.</p>
<p>Đáng chú ý: có <b>8 kênh Mỹ Latin</b> (Brazil 5, Peru 2, Colombia 1) &mdash; một nhánh
ngôn ngữ khác đang hình thành, đáng cân nhắc mở rộng về sau.</p>

<h3>6.3. Định dạng video &mdash; phát hiện một khoảng trống</h3>
<table>
<thead><tr><th>Định dạng</th><th>Số video<br>thị trường đang làm</th><th>VPD trung vị<br>(hiệu quả)</th><th>View trung vị</th></tr></thead>
<tbody>{band_rows}</tbody></table>

<img src="{img('c5_format_gap.png')}">
<p class="f">Trái: thị trường đổ nguồn lực vào đâu. Phải: định dạng nào thật sự hiệu quả.
Hai biểu đồ gần như ngược nhau.</p>

<div class="box">
<span class="l">Khoảng trống: thị trường đang làm sai định dạng</span>
<p><b>3.068 video</b> (43% toàn ngách) là mix dài 1&ndash;3 giờ &mdash; nhưng đó chỉ là định
dạng hiệu quả <b>hạng ba</b>, với VPD 11,7 và view trung vị chỉ 738.</p>
<p>Trong khi đó định dạng <b>1&ndash;6 phút</b> có VPD <b>15,6</b> (cao hơn 34%) và view trung
vị <b>2.557</b> (cao hơn 3,5 lần), nhưng chỉ có 1.156 video &mdash; bằng một phần ba.</p>
<p><b>Vì sao có khoảng trống này:</b> mix dài rẻ và dễ sản xuất hàng loạt bằng AI, nên nhiều
kênh chọn. Nhưng khán giả lại xem bài hát ngắn có lời nhiều hơn. Đây là <b>giả thuyết cần
kiểm chứng ở STEP_04</b> bằng nhóm đối chứng.</p>
</div>

<h2>7. Chấm điểm sơ bộ</h2>
<table>
<thead><tr><th>Trục</th><th>Trọng số</th><th>Điểm</th><th>Căn cứ</th></tr></thead>
<tbody>
<tr><td><b>T1</b> Quy mô</td><td class="n">20%</td><td class="n">2 / 5</td>
  <td>7,45tr view/tháng, thuộc khoảng 3&ndash;8tr</td></tr>
<tr class="hi"><td><b>T2</b> Động lượng</td><td class="n">25%</td><td class="n up"><b>4 / 5</b></td>
  <td>M2.1 = 1,62 (≥1,5) và M2.4 = 1,31 (≥1,0)</td></tr>
<tr><td><b>T3</b> Cửa gia nhập</td><td class="n">25%</td><td class="n">chờ</td><td>STEP_03</td></tr>
<tr><td><b>T4</b> Phù hợp AI</td><td class="n">15%</td><td class="n">chờ</td><td>STEP_03</td></tr>
<tr><td><b>T5</b> Kiếm tiền</td><td class="n">10%</td><td class="n">chờ</td><td>STEP_07</td></tr>
<tr><td><b>T6</b> Rủi ro</td><td class="n">&minus;5đ</td><td class="n">chờ</td><td>STEP_07</td></tr>
</tbody></table>
<p>Hai trục đã chấm đóng góp <b>{(2*0.20+4*0.25)*20/5:.1f} điểm</b> trên phần trọng số 45%.
Điểm tổng chỉ có nghĩa khi đủ 6 trục &mdash; sẽ hoàn tất ở STEP_08.</p>

<h2>8. Độ tin cậy và những điều chưa biết</h2>

<table>
<thead><tr><th>Kết luận</th><th>Độ tin cậy</th><th>Lý do</th></tr></thead>
<tbody>
<tr><td>Ngách trẻ, 74% kênh &lt;12 tháng</td><td class="ok">Cao</td>
  <td>Đếm trực tiếp từ ngày lập kênh</td></tr>
<tr><td>Cầu tăng nhanh hơn cung (M2.4=1,31)</td><td>Vừa</td>
  <td>Chỉ 1 snapshot; suy từ ngày đăng chứ không đo trực tiếp</td></tr>
<tr><td>Không có pha loãng thật</td><td>Vừa&ndash;Cao</td>
  <td>Nhất quán trên cả 3 phân khúc, nhưng vẫn dựa 1 snapshot</td></tr>
<tr><td>Định dạng ngắn hiệu quả hơn</td><td>Vừa</td>
  <td>Mới là tương quan, <b>chưa có nhóm đối chứng</b> &mdash; chờ STEP_04</td></tr>
<tr><td>62,3% kênh Tier-1</td><td>Vừa</td>
  <td>8 kênh không khai quốc gia</td></tr>
</tbody></table>

<h3>Bằng chứng phản bác &mdash; những gì có thể làm kết luận này sai</h3>
<ul>
<li><b>Chỉ có 1 snapshot.</b> Nếu view thực tế tăng chậm hơn suy đoán từ ngày đăng, M2.4 sẽ
thấp hơn. Cách kiểm: chạy thêm snapshot sau 7&ndash;14 ngày.</li>
<li><b>Cửa sổ so sánh 90 ngày là ngắn.</b> Có thể bị ảnh hưởng bởi mùa vụ (ví dụ Lễ Phục sinh,
Giáng sinh). Cách kiểm: so sánh cùng kỳ năm trước &mdash; nhưng dữ liệu chỉ có từ 01/2025.</li>
<li><b>VPD tăng có thể do chọn lọc sống sót.</b> Kênh yếu ngừng đăng, chỉ kênh khỏe còn lại
&rarr; VPD trung vị tăng mà không phải do thị trường tốt lên. Cách kiểm: theo dõi số kênh
ngừng hoạt động &mdash; hiện có 5 kênh, khá thấp.</li>
<li><b>Nhóm dẫn đầu tăng gấp đôi</b> có thể là dấu hiệu &ldquo;winner-takes-most&rdquo;
&mdash; tốt cho ngách nhưng khó cho người mới. Cách kiểm: STEP_03 đo hệ số Gini và tỷ lệ
thành công của kênh mới.</li>
</ul>

<h2>9. Việc tiếp theo</h2>
<table>
<thead><tr><th>Ưu tiên</th><th>Việc</th><th>Vì sao</th></tr></thead>
<tbody>
<tr><td class="ac"><b>Cao</b></td><td>Chạy thêm snapshot (7&ndash;14 ngày)</td>
  <td>Nâng độ tin cậy trục T2 từ Vừa lên Cao. Làm càng sớm càng tốt vì cần khoảng cách thời gian.</td></tr>
<tr><td class="ac"><b>Cao</b></td><td>STEP_03 &mdash; Bản đồ đối thủ</td>
  <td>Trả lời câu hỏi &ldquo;người mới còn cửa không&rdquo; (T3) &mdash; quan trọng nhất còn lại</td></tr>
<tr><td>Vừa</td><td>STEP_04 &mdash; Sàng lọc đối chứng</td>
  <td>Kiểm chứng giả thuyết định dạng ngắn bằng nhóm đối chứng B4</td></tr>
<tr><td>Vừa</td><td>Giải mã kênh <code>vintage_gospel_vgx</code></td>
  <td>3,81tr view với chỉ 48 video &mdash; hiệu suất cao nhất ngách</td></tr>
</tbody></table>

<div class="box">
<span class="l">Ghi chú về thời hạn dữ liệu</span>
<p>Điều khoản YouTube API yêu cầu làm mới hoặc xóa dữ liệu API trong vòng <b>30 ngày</b>.
Dữ liệu crawl ngày 13/08/2026 &rarr; hạn khoảng <b>12/09/2026</b>. Nên hoàn tất các bước
phân tích cần dữ liệu thô trước mốc này.</p>
</div>

</body></html>"""

out = N/"99_report/STEP01-02_Bao-cao-Quy-mo-Dong-luong.pdf"
out.parent.mkdir(parents=True, exist_ok=True)
HTML(string=HTML_DOC, base_url=".").write_pdf(out)
print(f"PDF: {out}  ({out.stat().st_size/1024:.0f} KB)")
