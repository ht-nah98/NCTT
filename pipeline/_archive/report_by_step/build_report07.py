"""Sinh báo cáo PDF cho STEP_07 — Kiếm tiền & Rủi ro + chấm điểm cuối."""
import json, pandas as pd, warnings, base64
from pathlib import Path
from weasyprint import HTML
warnings.filterwarnings("ignore")

N=Path("niches/christian-blues"); D=N/"07_monetization"
R=json.load(open(D/"_metrics_raw.json"))
SC=json.load(open(N/"_state/scores.json"))
# Điểm hiển thị kiểu Việt, KHÔNG làm tròn (12,05 chứ không phải 12,1).
# Làm tròn 1 chữ số từng khiến PDF lệch với scores.json. Bài học T27.
def _sc_vn(x): return f"{x:g}".replace(".", ",")
M=json.load(open(N/"_state/metrics.json"))
def img(n): return "data:image/png;base64,"+base64.b64encode((D/n).read_bytes()).decode()

b=pd.DataFrame(R["M5_3_band"]).set_index("duration_band").reindex(
  ["Shorts","1-6m","6-30m","30-60m","1-3h","3h+"])
band_rows="\n".join(
 f'<tr class="{"hi" if i in ("1-3h","3h+") else ""}"><td><b>{i}</b></td>'
 f'<td class="n">{int(r.n):,}</td><td class="n">{r.med_sec/60:.0f}</td>'
 f'<td class="n">{r.ad_slots:.1f}</td><td class="n">{int(r.med_view):,}</td></tr>'
 for i,r in b.iterrows())

sc=R["scenarios"]
lblS={"conservative":"Thận trọng (phân vị 25)","base":"Cơ sở (trung vị)","optimistic":"Lạc quan (phân vị 90)"}
sc_rows="\n".join(
 f'<tr class="{"hi" if k=="base" else ""}"><td>{lblS[k]}</td>'
 f'<td class="n">{s["views_per_month"]:,.0f}</td><td class="n">${s["rev_low"]:,.0f}</td>'
 f'<td class="n"><b>${s["rev_base"]:,.0f}</b></td><td class="n">${s["rev_high"]:,.0f}</td></tr>'
 for k,s in sc.items())

risk_rows="\n".join(
 f'<tr class="{"hi" if r["penalty"]<0 else ""}"><td><b>{r["risk"]}</b></td>'
 f'<td class="n">{r["penalty"]:+d}</td><td>{r["evidence"]}</td><td>{r["detail"]}</td></tr>'
 for r in R["risks"])

ax_rows="\n".join(
 f'<tr><td><b>{k}</b> {n}</td><td class="n">{SC["axes"][k]["score"]:.1f}</td>'
 f'<td class="n">{SC["axes"][k]["weight"]*100:.0f}%</td>'
 f'<td class="n">{SC["axes"][k]["score"]*SC["axes"][k]["weight"]*4:.2f}</td>'
 f'<td>{SC["axes"][k]["metric"]}</td>'
 f'<td>{"<span class=\'ok\'>Cao</span>" if SC["axes"][k]["confidence"]=="high" else "<span class=\'wa\'>Vừa</span>" if SC["axes"][k]["confidence"]=="medium" else "<span class=\'no\'>Thấp</span>"}</td></tr>'
 for k,n in [("T1","Quy mô"),("T2","Động lượng"),("T3","Cửa gia nhập"),
             ("T4","Phù hợp AI"),("T5","Kiếm tiền")])

cb=R["cross_by_channel"]
cb_rows="\n".join(f'<tr class="{"hi" if v>=30 else ""}"><td>{k}</td><td class="n">{v:.1f}%</td></tr>'
 for k,v in sorted(cb.items(),key=lambda x:-x[1])[:8])

DOC=f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size:A4;margin:17mm 15mm 20mm;
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
.wa {{ color:#8A6410;font-weight:bold; }}
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
img {{ width:100%;margin:8pt 0; }} .half {{ width:58%; }}
.f {{ font-size:7.5pt;color:#7A6F68;text-align:center;margin:-4pt 0 12pt; }}
code {{ background:#F2EEE8;padding:.5pt 3pt;font-size:8.5pt; }}
.formula {{ background:#F7F4F0;border:.6pt solid #E2DAD1;padding:7pt 10pt;
 font-size:8.5pt;margin:7pt 0;line-height:1.7; }}
.big {{ text-align:center;border:1.2pt solid #8C3A2B;padding:12pt;margin:12pt 0;background:#F9F4F2; }}
.big .n1 {{ font-size:34pt;font-weight:bold;color:#8C3A2B;line-height:1; }}
.big .n2 {{ font-size:11pt;color:#6B615A;margin-top:5pt; }}
.pb {{ page-break-before:always; }}
ul {{ margin:6pt 0;padding-left:15pt; }} li {{ margin:3pt 0; }}
</style></head><body>

<h1>Kiếm tiền &amp; Rủi ro &mdash; Christian Blues</h1>
<p class="sub">Báo cáo giai đoạn 5 &mdash; Ngách này ra tiền được không, và rủi ro nằm ở đâu</p>
<div class="meta">
STEP_07 &nbsp;•&nbsp; Agent A6 &nbsp;•&nbsp; Trục T5 (Kiếm tiền) + T6 (Rủi ro)
&nbsp;•&nbsp; Kèm chấm điểm cuối 6 trục &nbsp;•&nbsp; Lập ngày 15/08/2026
</div>

<h2>1. Tóm tắt điều hành</h2>

<div class="box crit">
<span class="l">Cảnh báo quan trọng về bản chất báo cáo này</span>
<p>Khác với các bước trước, <b>RPM không có trong dữ liệu</b>. YouTube API không trả về doanh
thu của kênh người khác. Mọi con số tiền trong báo cáo này là <b>ƯỚC TÍNH CÓ GIẢ ĐỊNH</b>,
độ tin cậy <b>Thấp</b>.</p>
<p>Phần rủi ro thì ngược lại &mdash; đo được trực tiếp từ dữ liệu, độ tin cậy Vừa đến Cao.</p>
</div>

<div class="kpi">
<div><div class="k">RPM ước tính</div><div class="v ac">$3,0</div>
 <div class="c">khoảng $1,5&ndash;6,0</div></div>
<div><div class="k">Doanh thu cơ sở</div><div class="v">$319</div>
 <div class="c">mỗi tháng, kênh trung vị</div></div>
<div><div class="k">Điểm rủi ro</div><div class="v dn">&minus;2</div>
 <div class="c">trùng lặp + chủ đề nhạy cảm</div></div>
<div><div class="k">Tổng điểm cuối</div><div class="v">{_sc_vn(SC['total_score'])}<span style="font-size:10pt">/20</span></div>
 <div class="c">{SC['verdict']}</div></div>
</div>

<h2>2. Trục T5 &mdash; Khả năng kiếm tiền</h2>

<h3>2.1. Ba yếu tố quyết định RPM</h3>
<div class="formula">
<b>RPM</b> (doanh thu trên 1.000 lượt xem) <b>≈ f(</b> địa lý khán giả , độ tuổi , số điểm chèn quảng cáo <b>)</b>
</div>

<table>
<thead><tr><th>Yếu tố</th><th>Kết quả đo được</th><th>Tác động tới RPM</th></tr></thead>
<tbody>
<tr><td><b>Ngôn ngữ nội dung</b></td>
 <td class="n">{R['M5_1_lang']['en_pct_of_known']:.1f}% tiếng Anh</td>
 <td class="ok">Tăng &mdash; thị trường nói tiếng Anh có giá quảng cáo cao nhất</td></tr>
<tr><td><b>Quốc gia kênh</b></td>
 <td class="n">{R['M5_1_tier1_of_declared']:.1f}% Tier-1</td>
 <td class="ok">Tăng &mdash; Mỹ, Anh, Canada, Úc</td></tr>
<tr><td><b>Độ tuổi khán giả</b></td>
 <td class="n">trung vị 70 tuổi (tự khai)</td>
 <td class="ok">Tăng &mdash; sức mua cao, ít dùng chặn quảng cáo</td></tr>
<tr><td><b>Loại nội dung</b></td>
 <td>Nhạc nghe nền</td>
 <td class="no">Giảm &mdash; độ chú ý thấp, nhà quảng cáo trả ít hơn</td></tr>
<tr><td><b>Độ dài video</b></td>
 <td class="n">trung vị {R['M5_3_median_duration_sec']/60:.0f} phút</td>
 <td class="ok">Tăng mạnh &mdash; nhiều điểm chèn quảng cáo</td></tr>
</tbody></table>

<div class="box">
<span class="l">Giả định dùng để ước tính RPM &mdash; xin đọc kỹ</span>
<p><b>Điểm xuất phát:</b> nhạc thị trường Tier-1 thường có RPM $1,5&ndash;4. Nhạc luôn thấp
hơn nội dung nói (talking-head) vì người nghe không chú ý màn hình.</p>
<p><b>Điều chỉnh TĂNG:</b> khán giả 60+ ở Mỹ (nhóm có RPM cao nhất theo tuổi) và định dạng
dài nhiều ad slot.</p>
<p><b>Điều chỉnh GIẢM:</b> nhạc nghe nền, người dùng thường tắt màn hình.</p>
<p><b>Kết quả: $1,5 &ndash; $6,0, cơ sở $3,0.</b> Đây là <i>khoảng</i>, không phải con số.
Chỉ có thể xác minh khi bạn tự vận hành kênh và xem báo cáo YouTube Analytics thật.</p>
</div>

<h3>2.2. Số điểm chèn quảng cáo theo định dạng</h3>
<img src="{img('c2_adslots.png')}">
<table>
<thead><tr><th>Định dạng</th><th>Số video</th><th>Độ dài trung vị<br>(phút)</th>
<th>Ad slot ước tính</th><th>View trung vị</th></tr></thead>
<tbody>{band_rows}</tbody></table>

<div class="box ok">
<span class="l">Đảo ngược kinh tế học của định dạng</span>
<p>STEP_04 cho thấy video ngắn có VPD cao hơn (15,6 so với 11,7). Nhưng về <b>doanh thu</b>
thì hoàn toàn ngược lại:</p>
<p>Video <b>1&ndash;6 phút</b>: chỉ <b>1 điểm quảng cáo</b> (YouTube cần video ≥8 phút mới cho
chèn giữa video).<br>
Video <b>1&ndash;3 giờ</b>: khoảng <b>11,7 điểm quảng cáo</b> &mdash; gấp gần 12 lần.</p>
<p>Cộng với phát hiện STEP_05 (khán giả nghe khi cầu nguyện, bệnh tật &rarr; cần âm thanh
liền mạch kéo dài), <b>mix dài là lựa chọn đúng cả về nhu cầu lẫn doanh thu</b>.</p>
<p>Điều này khép lại tranh luận định dạng kéo dài từ STEP_01. Kết luận cuối:
<b>mix dài 1&ndash;3 giờ là định dạng chủ lực đúng đắn</b>; video ngắn chỉ nên dùng để
thu hút người xem mới.</p>
</div>

<h3>2.3. Ba kịch bản doanh thu</h3>
<img src="{img('c1_revenue.png')}" class="half">
<table>
<thead><tr><th>Kịch bản</th><th>View/tháng</th><th>RPM $1,5</th><th>RPM $3,0</th><th>RPM $6,0</th></tr></thead>
<tbody>{sc_rows}</tbody></table>
<p>Các mức view lấy từ <b>phân bố thật của 53 kênh trong ngách</b>, không phải giả định.
Kịch bản cơ sở dùng kênh trung vị: <b>106.406 view/tháng &rarr; khoảng $319/tháng</b>.</p>

<div class="box">
<span class="l">Cách đọc bảng này cho đúng</span>
<p>Kịch bản &ldquo;lạc quan&rdquo; ($1.391/tháng) là mức <b>phân vị 90</b> &mdash; tức chỉ
khoảng 5 trên 53 kênh đạt được. Đừng lấy đó làm kỳ vọng mặc định.</p>
<p>Kịch bản &ldquo;thận trọng&rdquo; ($124/tháng) là mức phân vị 25 &mdash; một phần tư số kênh
trong ngách kiếm được ít hơn con số này.</p>
<p><b>Đây là doanh thu quảng cáo YouTube thuần túy</b>, chưa tính các nguồn khác
(tài trợ, bán nhạc số, phân phối streaming).</p>
</div>

<p><b>Điểm T5 = {SC['axes']['T5']['score']}/5.</b> {R['T5_note']}</p>

<h2 class="pb">3. Trục T6 &mdash; Sổ rủi ro</h2>

<table>
<thead><tr><th>Rủi ro</th><th>Điểm trừ</th><th>Bằng chứng</th><th>Nhận định</th></tr></thead>
<tbody>{risk_rows}</tbody></table>

<h3>3.1. Rủi ro chính: nội dung trùng lặp</h3>
<img src="{img('c3_dup_risk.png')}" class="half">
<table>
<thead><tr><th>Kênh</th><th>% video có tiêu đề trùng kênh khác</th></tr></thead>
<tbody>{cb_rows}</tbody></table>

<div class="box crit">
<span class="l">Đây là rủi ro đáng lo nhất của ngách</span>
<p><b>132 tiêu đề</b> được nhiều kênh khác nhau dùng chung. Một số tiêu đề xuất hiện ở
<b>5 kênh</b> khác nhau, gần như giống hệt từng chữ.</p>
<p>Có <b>5 kênh</b> mà trên 30% video mang tiêu đề trùng với kênh khác. Kênh cao nhất:
<code>faithbluesworship</code> với <b>55,4%</b>.</p>
<p><b>Vì sao đáng lo:</b> YouTube yêu cầu nội dung có &ldquo;giá trị nguyên bản đáng kể&rdquo;
để được bật kiếm tiền. Khi nhiều kênh AI cùng sản xuất nội dung na ná nhau với tiêu đề giống
hệt, cả cụm có nguy cơ bị đánh giá là nội dung lặp lại hàng loạt.</p>
</div>

<div class="box">
<span class="l">Nhưng có một nghịch lý: trùng lặp lại đang HIỆU QUẢ hơn</span>
<p>VPD trung vị của video có tiêu đề trùng chéo: <b>{R['cross_title_perf']['cross_vpd']:.2f}</b><br>
VPD trung vị của video có tiêu đề riêng: <b>{R['cross_title_perf']['clean_vpd']:.2f}</b></p>
<p>Video trùng tiêu đề đang chạy <b>tốt hơn 68%</b>. Lý do khả dĩ: các kênh copy tiêu đề
<i>của video đã thành công</i> &mdash; đúng nguyên tắc &ldquo;không sáng tạo cái đã win&rdquo;
trong script gốc bạn đưa.</p>
<p><b>Đây là đánh đổi thật:</b> copy tiêu đề cho hiệu quả ngắn hạn cao hơn, nhưng tăng rủi ro
chính sách dài hạn. Khuyến nghị: <b>học cấu trúc tiêu đề, đừng sao chép nguyên văn.</b></p>
</div>

<h3>3.2. Các rủi ro KHÔNG thành vấn đề</h3>
<ul>
<li><b>Mô tả dùng lại:</b> 1.406 video dùng mô tả lặp, nhưng <b>0 mẫu dùng chéo giữa các kênh</b>
&mdash; toàn bộ là template trong nội bộ một kênh. Đây là bình thường, không phải rủi ro.</li>
<li><b>Bản quyền thánh ca:</b> chỉ 19 video (0,3%) đặt tên theo thánh ca kinh điển. Hầu hết là
sáng tác mới. Thánh ca xuất bản trước 1929 thuộc phạm vi công cộng.</li>
<li><b>Phụ thuộc kênh dẫn đầu:</b> kênh lớn nhất chỉ chiếm 17,9% &mdash; xa ngưỡng rủi ro 40%.</li>
<li><b>Cung vượt cầu:</b> M2.4 = 1,305, cầu vẫn tăng nhanh hơn cung.</li>
</ul>

<h3>3.3. Rủi ro không đo được từ dữ liệu</h3>
<p><b>Chủ đề tôn giáo kết hợp nội dung AI</b> thuộc nhóm bị nền tảng rà soát kỹ hơn. Đây là
đánh giá dựa trên chính sách nền tảng, không phải từ dữ liệu &mdash; nên tôi ghi rõ là
<b>không đo được</b>. Trừ 1 điểm mang tính thận trọng.</p>

<h2 class="pb">4. Chấm điểm cuối &mdash; 6 trục</h2>

<img src="{img('c4_radar.png')}" style="width:52%">

<table>
<thead><tr><th>Trục</th><th>Điểm<br>(0-5)</th><th>Trọng số</th><th>Đóng góp</th>
<th>Chỉ số quyết định</th><th>Tin cậy</th></tr></thead>
<tbody>
{ax_rows}
<tr><td><b>T6</b> Rủi ro</td><td class="n dn">{SC['T6']['penalty']}</td><td class="n">&mdash;</td>
 <td class="n dn">{SC['T6']['penalty']:.2f}</td><td>Trùng lặp &minus;1, tôn giáo+AI &minus;1</td>
 <td><span class="wa">Vừa</span></td></tr>
</tbody></table>

<div class="big">
<div class="n1">{_sc_vn(SC['total_score'])} / 20</div>
<div class="n2">Xếp loại: <b>{SC['verdict']}</b></div>
</div>

<table>
<thead><tr><th>Thang xếp loại</th><th>Ý nghĩa</th></tr></thead>
<tbody>
<tr><td class="n">16&ndash;20</td><td>Ưu tiên cao &mdash; vào ngay</td></tr>
<tr><td class="n">13&ndash;15,9</td><td>Tiềm năng &mdash; vào có điều kiện, cần khác biệt hóa</td></tr>
<tr class="hi"><td class="n">10&ndash;12,9</td><td><b>Theo dõi &mdash; chưa vào, quan sát thêm</b></td></tr>
<tr><td class="n">dưới 10</td><td>Bỏ qua</td></tr>
</tbody></table>

<div class="box">
<span class="l">So sánh với bảng chấm thủ công ban đầu của bạn</span>
<p>Bảng cũ chấm Christian Blues <b>12/20</b>. Hệ thống chấm <b>{_sc_vn(SC['total_score'])}/20</b>.
Con số gần như trùng nhau &mdash; nhưng <b>vì lý do hoàn toàn khác</b>.</p>
<p><b>Bảng cũ:</b> quy mô 3đ, phù hợp AI 4đ, tín hiệu gia nhập 2đ, hợp gu 3đ.<br>
<b>Hệ thống:</b> quy mô 2đ (thấp hơn), động lượng 4đ, <b>cửa gia nhập 4,4đ</b> (cao hơn nhiều),
phù hợp AI 5đ (cao hơn), kiếm tiền 3đ, rủi ro &minus;2đ.</p>
<p>Bảng cũ đánh giá <b>quá thấp</b> cửa gia nhập (2đ so với 4,4đ) và <b>bỏ sót hoàn toàn</b>
động lượng lẫn rủi ro. Việc hai con số trùng nhau là ngẫu nhiên.</p>
</div>

<h2>5. Vì sao chỉ đạt &ldquo;Theo dõi&rdquo; dù nhiều trục rất mạnh</h2>

<p>Ngách có <b>ba trục rất mạnh</b>: cửa gia nhập 4,4/5, phù hợp AI 5/5, động lượng 4/5.
Nhưng bị kéo xuống bởi:</p>
<table>
<thead><tr><th>Yếu tố kéo điểm</th><th>Mất</th><th>Giải thích</th></tr></thead>
<tbody>
<tr><td><b>T1 Quy mô chỉ 2/5</b></td><td class="n">&minus;2,4đ</td>
 <td>7,45tr view/tháng là ngách <i>cỡ vừa</i>. Trần doanh thu bị giới hạn.</td></tr>
<tr><td><b>T5 Kiếm tiền chỉ 3/5</b></td><td class="n">&minus;0,8đ</td>
 <td>Nhạc nghe nền vốn RPM thấp hơn nội dung nói.</td></tr>
<tr><td><b>T6 Rủi ro &minus;2đ</b></td><td class="n">&minus;2,0đ</td>
 <td>Trùng lặp nội dung + chủ đề bị soi kỹ.</td></tr>
</tbody></table>

<div class="box ok">
<span class="l">Diễn giải thực tế của điểm 12,2</span>
<p>&ldquo;Theo dõi&rdquo; <b>không có nghĩa là ngách xấu</b>. Nó có nghĩa: ngách này
<b>dễ vào nhưng trần thấp</b>.</p>
<p>Bạn <i>có thể</i> vào và thành công (61,5% kênh mới đạt traction &mdash; tỷ lệ rất cao).
Nhưng kỳ vọng doanh thu nên đặt ở mức <b>vài trăm đô mỗi tháng cho một kênh</b>,
không phải vài nghìn.</p>
<p><b>Mô hình phù hợp:</b> nhiều kênh chạy song song, chi phí sản xuất thấp bằng AI &mdash;
chứ không phải dồn toàn lực vào một kênh lớn.</p>
</div>

<h2>6. Độ tin cậy &mdash; nhìn thẳng vào điểm yếu</h2>
<table>
<thead><tr><th>Trục</th><th>Tin cậy</th><th>Điểm yếu cụ thể</th></tr></thead>
<tbody>
<tr><td>T1 Quy mô</td><td class="ok">Cao</td><td>Đếm trực tiếp từ dữ liệu</td></tr>
<tr><td>T2 Động lượng</td><td class="wa">Vừa</td>
 <td>Chỉ 1 snapshot. Nếu dùng cửa sổ chưa chín thì M2.4 = 0,447 và T2 = 0đ</td></tr>
<tr><td>T3 Cửa gia nhập</td><td class="ok">Cao</td>
 <td>Nhưng có thiên lệch sống sót &mdash; kênh đã xóa không có trong dữ liệu</td></tr>
<tr><td>T4 Phù hợp AI</td><td class="wa">Vừa</td>
 <td>Phân loại AI-first là suy luận gián tiếp từ nhịp đăng và thumbnail</td></tr>
<tr><td>T5 Kiếm tiền</td><td class="no">Thấp</td>
 <td><b>RPM hoàn toàn là ước tính.</b> Không có trong dữ liệu API.</td></tr>
<tr><td>T6 Rủi ro</td><td class="wa">Vừa</td>
 <td>Trùng lặp đo được; rủi ro chính sách chỉ là đánh giá định tính</td></tr>
</tbody></table>

<h3>Điều gì sẽ làm điểm số này thay đổi</h3>
<ul>
<li><b>Nếu RPM thật là $6 thay vì $3</b> &rarr; T5 lên 4đ &rarr; tổng thành 12,6. Vẫn
&ldquo;Theo dõi&rdquo;.</li>
<li><b>Nếu chạy thêm snapshot và M2.4 thật thấp hơn</b> &rarr; T2 có thể giảm mạnh &rarr;
tổng xuống dưới 10 &rarr; chuyển thành &ldquo;Bỏ qua&rdquo;. <b>Đây là rủi ro lớn nhất
với kết luận hiện tại.</b></li>
<li><b>Nếu YouTube siết chính sách nội dung AI hàng loạt</b> &rarr; T6 có thể xuống &minus;4
&rarr; tổng còn 10,2.</li>
</ul>

<h2>7. Khuyến nghị</h2>
<table>
<thead><tr><th>Ưu tiên</th><th>Việc</th><th>Lý do</th></tr></thead>
<tbody>
<tr><td class="ac"><b>Cao</b></td><td>Chạy thêm snapshot ngay</td>
 <td>Đây là biến số duy nhất có thể lật ngược kết luận. Cần cách nhau 7&ndash;14 ngày.</td></tr>
<tr><td class="ac"><b>Cao</b></td><td>Nếu vào: dùng <b>mix dài 1&ndash;3 giờ</b> làm chủ lực</td>
 <td>Gấp ~12 lần ad slot, và đúng bối cảnh nghe của khán giả</td></tr>
<tr><td class="ac"><b>Cao</b></td><td>Không sao chép nguyên văn tiêu đề đối thủ</td>
 <td>Học cấu trúc thì được, copy từng chữ thì rủi ro chính sách</td></tr>
<tr><td>Vừa</td><td>Lập kế hoạch nhiều kênh song song</td>
 <td>Trần doanh thu mỗi kênh thấp, nhưng cửa vào rất rộng</td></tr>
<tr><td>Vừa</td><td>STEP_06 &mdash; Từ khóa &amp; đóng gói</td>
 <td>Bước duy nhất còn thiếu. Trọng tâm: chọn đề tài, không phải SEO.</td></tr>
<tr><td>Vừa</td><td>Xác minh RPM bằng kênh thử nghiệm</td>
 <td>T5 là trục yếu nhất về độ tin cậy</td></tr>
</tbody></table>

<div class="box">
<span class="l">Ghi chú về thời hạn dữ liệu</span>
<p>Điều khoản YouTube API yêu cầu làm mới hoặc xóa dữ liệu trong <b>30 ngày</b>.
Crawl ngày 13/08/2026 &rarr; hạn khoảng <b>12/09/2026</b>.</p>
</div>

</body></html>"""

out=N/"99_report/STEP07_Kiem-tien-Rui-ro.pdf"
HTML(string=DOC,base_url=".").write_pdf(out)
print(f"PDF: {out} ({out.stat().st_size/1024:.0f} KB)")
