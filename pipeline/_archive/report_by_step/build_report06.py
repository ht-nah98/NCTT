"""Sinh báo cáo PDF cho STEP_06 — Từ khóa & Đóng gói."""
import json, pandas as pd, warnings, base64, html
from pathlib import Path
from weasyprint import HTML
warnings.filterwarnings("ignore")

N=Path("niches/christian-blues"); D=N/"06_keyword"
R=json.load(open(D/"_metrics_raw.json"))
TH=pd.read_csv(D/"02_theme_scores.csv"); G=pd.read_csv(D/"03_voice_gap.csv")
def img(n): return "data:image/png;base64,"+base64.b64encode((D/n).read_bytes()).decode()

LBL={"old_school":"Old-school / vintage / black gospel","thanks":"Tạ ơn / biết ơn",
"testimony":"Lời chứng / câu chuyện","presence":"Sự hiện diện Chúa","peace_rest":"Bình an / nghỉ ngơi",
"deliverance":"Giải thoát / chiến thắng","grace_mercy":"Ân điển / thương xót","sorrow_pain":"Đau buồn / tan vỡ",
"prayer":"Cầu nguyện","hope_faith":"Hy vọng / đức tin","morning":"Buổi sáng","healing":"Chữa lành",
"strength":"Sức mạnh / can đảm","scripture":"Kinh Thánh / Thánh Vịnh","night_sleep":"Đêm / giấc ngủ",
"instrumental":"Không lời / nhạc nền"}
def vb(v):
    return {"XÁC NHẬN":'<span class="ok">NÊN LÀM</span>',"YẾU":'<span class="wa">CÓ THỂ THỬ</span>',
     "TRÁNH":'<span class="no">NÊN TRÁNH</span>',
     "BÁC BỎ (Simpson)":'<span class="no">BÁC BỎ<br><span style="font-size:6.5pt">nghịch lý Simpson</span></span>'}.get(v,'<span style="color:#7A6F68">Trung tính</span>')

th_rows="\n".join(
 f'<tr class="{"hi" if r.verdict in ("XÁC NHẬN","TRÁNH") else ""}"><td><b>{LBL.get(r.theme,r.theme)}</b></td>'
 f'<td class="n">{int(r.n):,}</td><td class="n">{r.share_pct:.1f}%</td>'
 f'<td class="n">{r.vpd_theme:.1f}</td><td class="n">{r.lift:.2f}×</td>'
 f'<td class="n">{r.p:.3f}</td><td class="n">{int(r.n_ch_better)}/{int(r.n_ch_tested)}</td>'
 f'<td>{vb(r.verdict)}</td></tr>' for _,r in TH.iterrows())

tag_rows="\n".join(f'<tr><td>{t["tag"]}</td><td class="n">{t["freq"]:,}</td></tr>'
 for t in R["tags_only_in_winners"][:14])
hash_rows="\n".join(f'<tr><td>#{k}</td><td class="n">{v:,}</td></tr>'
 for k,v in list(R["hashtag_top"].items())[:12])
g_rows="\n".join(
 f'<tr><td><b>{r.word}</b></td><td class="n">{int(r.in_comments):,}</td>'
 f'<td class="n">{int(r.in_titles)}</td><td class="n">{r.ratio:.0f}×</td></tr>'
 for _,r in G.head(12).iterrows())

ts=R["title_struct"]
tt_rows="\n".join(
 f'<tr><td>{html.escape(str(t["title"])[:78])}</td><td class="n">{int(t["view_count"]):,}</td>'
 f'<td class="n">{t["outlier_ratio"]:.0f}×</td><td class="n">{t["duration_band"]}</td></tr>'
 for t in R["top_titles"][:10])

conf_=TH[TH.verdict=="XÁC NHẬN"]; avoid=TH[TH.verdict=="TRÁNH"]; weak=TH[TH.verdict=="YẾU"]

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
img {{ width:100%;margin:8pt 0; }} .half {{ width:60%; }}
.f {{ font-size:7.5pt;color:#7A6F68;text-align:center;margin:-4pt 0 12pt; }}
code {{ background:#F2EEE8;padding:.5pt 3pt;font-size:8.5pt; }}
.tpl {{ background:#F7F4F0;border:.6pt solid #E2DAD1;padding:8pt 11pt;
 font-size:9pt;margin:7pt 0;line-height:1.8;font-family:"DejaVu Sans Mono",monospace; }}
.pb {{ page-break-before:always; }}
ul {{ margin:6pt 0;padding-left:15pt; }} li {{ margin:3pt 0; }}
</style></head><body>

<h1>Từ khóa &amp; Đóng gói &mdash; Christian Blues</h1>
<p class="sub">Báo cáo giai đoạn 6 &mdash; Chọn đề tài nào, và truyền tải ra sao</p>
<div class="meta">
STEP_06 &nbsp;•&nbsp; Agent A5 &nbsp;•&nbsp; Nguồn: 5.609 video đã chín + {R['tag_unique']:,} tag
&nbsp;•&nbsp; Dữ liệu crawl 13/08/2026 &nbsp;•&nbsp; Lập ngày 15/08/2026
</div>

<h2>1. Tóm tắt điều hành</h2>

<div class="box">
<span class="l">Trọng tâm bước này đã được đổi &mdash; và đây là lý do</span>
<p>Kế hoạch ban đầu của STEP_06 là nghiên cứu từ khóa để <b>tối ưu SEO</b>. Nhưng STEP_05 phát
hiện: khán giả đến với video qua <b>đề xuất của YouTube nhiều gấp 7 lần</b> so với tự tìm kiếm
(83 bình luận so với 12).</p>
<p>Cộng với STEP_04 (metadata không phân biệt được video thắng/thua), việc tối ưu từ khóa
tìm kiếm gần như <b>không có giá trị</b> trong ngách này.</p>
<p><b>Vì vậy bước này chuyển sang câu hỏi có giá trị hơn: LÀM VIDEO VỀ ĐỀ TÀI GÌ?</b></p>
</div>

<div class="kpi">
<div><div class="k">Chủ đề đã kiểm</div><div class="v">{len(TH)}</div>
 <div class="c">trên 5.609 video chín</div></div>
<div><div class="k">Chủ đề NÊN LÀM</div><div class="v up">{len(conf_)+len(weak)}</div>
 <div class="c">xác nhận hoặc đáng thử</div></div>
<div><div class="k">Chủ đề NÊN TRÁNH</div><div class="v dn">{len(avoid)}</div>
 <div class="c">hiệu quả dưới mức nền rõ rệt</div></div>
<div><div class="k">Bác bỏ do Simpson</div><div class="v">4</div>
 <div class="c">có vẻ tốt nhưng không thật</div></div>
</div>

<h3>Kết quả nhanh</h3>
<table>
<thead><tr><th>Khuyến nghị</th><th>Chủ đề</th><th>Hiệu quả</th></tr></thead>
<tbody>
<tr><td class="ok"><b>NÊN LÀM</b></td><td>Old-school / vintage / black gospel</td>
 <td class="n">2,37&times; mức nền</td></tr>
<tr><td class="ok"><b>NÊN LÀM</b></td><td>Tạ ơn / biết ơn</td><td class="n">1,62&times;</td></tr>
<tr><td class="no"><b>NÊN TRÁNH</b></td><td>Kinh Thánh / Thánh Vịnh</td><td class="n">0,61&times;</td></tr>
<tr><td class="no"><b>NÊN TRÁNH</b></td><td>Không lời / nhạc nền</td><td class="n">0,17&times;</td></tr>
</tbody></table>

<h2>2. Phương pháp</h2>

<div class="formula" style="background:#F7F4F0;border:.6pt solid #E2DAD1;padding:7pt 10pt;font-size:8.5pt;">
Với mỗi chủ đề: <b>lift = VPD trung vị video CÓ chủ đề ÷ VPD trung vị video KHÔNG có</b>
</div>

<p>Nhưng bài học lớn nhất từ STEP_04 là <b>nghịch lý Simpson</b>: một chủ đề có thể trông
hiệu quả chỉ vì vài kênh mạnh chuyên làm nó. Vì vậy mỗi chủ đề đều qua <b>ba lớp kiểm</b>:</p>

<table>
<thead><tr><th>Lớp</th><th>Kiểm gì</th><th>Loại bỏ điều gì</th></tr></thead>
<tbody>
<tr><td><b>1. Toàn thị trường</b></td><td>lift trên 5.609 video chín</td>
 <td>Chủ đề hiếm, không đủ mẫu</td></tr>
<tr><td><b>2. Ý nghĩa thống kê</b></td><td>Mann-Whitney p &lt; 0,05</td>
 <td>Chênh lệch do ngẫu nhiên</td></tr>
<tr><td><b>3. Trong từng kênh</b></td><td>Bao nhiêu kênh cho kết quả tốt hơn</td>
 <td><b>Nghịch lý Simpson</b> &mdash; chủ đề trông tốt chỉ vì kênh mạnh làm nó</td></tr>
</tbody></table>

<p>Lớp 3 đã loại <b>4 chủ đề</b> tưởng như hiệu quả: Lời chứng (lift 1,51 nhưng chỉ 8/22 kênh
tốt hơn), Chữa lành, Sức mạnh, Đêm/giấc ngủ.</p>

<h2 class="pb">3. Bản đồ chủ đề</h2>

<img src="{img('c1_themes.png')}">
<p class="f">Cột xanh: nên làm. Vàng: có thể thử. Đỏ: nên tránh. Xám: trung tính.</p>

<table>
<thead><tr><th>Chủ đề</th><th>Số video</th><th>Thị phần</th><th>VPD</th>
<th>Lift</th><th>p-value</th><th>Kênh tốt<br>hơn</th><th>Khuyến nghị</th></tr></thead>
<tbody>{th_rows}</tbody></table>
<p style="font-size:8pt;color:#6B615A">VPD nền của toàn ngách: <b>{R['base_vpd']:.2f}</b> view/ngày.</p>

<h3>3.1. Bản đồ khoảng trống</h3>
<img src="{img('c2_gap_map.png')}">
<p class="f">Góc trên bên trái = cơ hội tốt nhất: hiệu quả cao nhưng ít người làm.</p>

<div class="box ok">
<span class="l">Khoảng trống rõ nhất: Old-school / vintage</span>
<p>Chủ đề này đạt lift <b>2,37&times;</b> &mdash; cao nhất trong 16 chủ đề &mdash; nhưng chỉ
<b>3,96% video</b> trong ngách khai thác. Hiệu quả cao, cạnh tranh thấp.</p>
<p>Được <b>20 kênh khác nhau</b> sử dụng (không phải hiện tượng của một kênh), và
<b>4/8 kênh</b> có đủ dữ liệu cho kết quả tốt hơn khi dùng.</p>
<p>Điều này khớp với chân dung khách hàng ở STEP_05: khán giả trung vị <b>70 tuổi</b>.
Họ lớn lên cùng black gospel thập niên 1950&ndash;70. Từ ngữ &ldquo;old school&rdquo;,
&ldquo;vintage&rdquo;, &ldquo;1950s&rdquo; gợi đúng ký ức của họ.</p>
</div>

<div class="box crit">
<span class="l">Xác nhận lại: Kinh Thánh / Thánh Vịnh NÊN TRÁNH</span>
<p>STEP_04 đã phát hiện chủ đề Kinh Thánh không phải công thức thắng. Bước này đo trên toàn
thị trường và khẳng định mạnh hơn: lift <b>0,61&times;</b> &mdash; tức <b>kém hơn 39%</b>,
p &lt; 0,001, với <b>652 video</b> (11,6% ngách).</p>
<p>Đáng chú ý: trong từng kênh thì lift là 1,28 (13/18 kênh tốt hơn). Nghĩa là <b>với kênh
đã chuyên về Thánh Vịnh thì nên tiếp tục</b>, nhưng <b>kênh mới không nên chọn đây làm
hướng chính</b> &mdash; vì mảng này đã đông và hiệu quả tổng thể thấp.</p>
</div>

<div class="box crit">
<span class="l">Tránh mạnh nhất: nhạc không lời / nhạc nền</span>
<p>Lift chỉ <b>0,17&times;</b> &mdash; kém hơn <b>83%</b> so với mức nền. Chỉ 58 video và
5 kênh làm.</p>
<p>Lý do khả dĩ, dựa trên STEP_05: khán giả ngách này nghe để <b>thờ phượng và tĩnh tâm</b>,
không phải làm nhạc nền cho việc khác. Họ muốn <b>lời hát</b>. Định vị &ldquo;background
music&rdquo; đánh sai nhu cầu.</p>
<p>Điều này cũng khớp dữ liệu Wavelength (STEP_00): khán giả Gospel chấp nhận AI cao, nhưng
người Mỹ nói chung thoải mái với AI <i>làm nhạc không lời</i> hơn. Ở đây thì ngược lại &mdash;
<b>nhạc CÓ LỜI mới là thứ ngách này cần.</b></p>
</div>

<h2 class="pb">4. Tag và hashtag</h2>

<p>Độ phủ tag: <b>{R['tag_coverage']:.0f}%</b> số video có tag ({R['tag_unique']:,} tag khác
nhau, tổng {R['tag_total']:,} lượt dùng). Có <b>{R['hashtag_total']:,}</b> hashtag trong
tiêu đề và mô tả.</p>

<div class="box">
<span class="l">Lưu ý về giá trị thực của tag</span>
<p>YouTube đã công khai rằng <b>tag có trọng số rất nhỏ</b> trong thuật toán hiện tại. Bảng
dưới đây <b>không dùng để nhồi tag</b>, mà để <b>hiểu đối thủ định vị nội dung thế nào</b> &mdash;
và từ đó chọn đề tài.</p>
</div>

<h3>4.1. Tag chỉ xuất hiện ở video thắng</h3>
<img src="{img('c4_tags.png')}" class="half">
<table>
<thead><tr><th>Tag</th><th>Số lần dùng trong ngách</th></tr></thead>
<tbody>{tag_rows}</tbody></table>

<p>Các tag này xuất hiện ở nhóm video thắng nhưng <b>không xuất hiện</b> ở nhóm đối chứng.
Đáng chú ý là chúng mô tả <b>phong cách nhạc cụ thể</b> (&ldquo;slow blues&rdquo;,
&ldquo;delta blues&rdquo;, &ldquo;blues guitar&rdquo;, &ldquo;smooth blues&rdquo;) chứ không
phải từ khóa tôn giáo chung chung.</p>

<div class="box ok">
<span class="l">Gợi ý định vị: nói rõ PHONG CÁCH NHẠC, không chỉ nói chủ đề</span>
<p>Ngách đã bão hòa từ ngữ tôn giáo (&ldquo;prayer&rdquo;, &ldquo;god&rdquo;,
&ldquo;worship&rdquo; xuất hiện ở cả video thắng lẫn thua &mdash; STEP_04). Nhưng
<b>tên phong cách nhạc cụ thể</b> thì chưa bão hòa.</p>
<p>&ldquo;Delta blues&rdquo;, &ldquo;slow blues&rdquo;, &ldquo;christian jazz&rdquo; giúp
YouTube phân loại đúng và giúp khán giả biết chính xác họ sẽ nghe gì.</p>
</div>

<h3>4.2. Hashtag phổ biến</h3>
<table>
<thead><tr><th>Hashtag</th><th>Số lần</th></tr></thead>
<tbody>{hash_rows}</tbody></table>

<h2>5. Khoảng trống ngôn ngữ</h2>

<p>So sánh từ ngữ <b>khách hàng dùng trong bình luận</b> với từ ngữ <b>đối thủ dùng trong
tiêu đề</b>. Chênh lệch lớn = cơ hội nói đúng ngôn ngữ khách hàng.</p>

<img src="{img('c3_voice_gap.png')}" class="half">
<table>
<thead><tr><th>Từ</th><th>Lần xuất hiện<br>trong bình luận</th>
<th>Lần xuất hiện<br>trong tiêu đề</th><th>Tỷ lệ chênh</th></tr></thead>
<tbody>{g_rows}</tbody></table>

<div class="box">
<span class="l">Cách đọc bảng này cho đúng &mdash; đừng vội áp dụng</span>
<p>&ldquo;Amen&rdquo; xuất hiện <b>2.233 lần</b> trong bình luận nhưng chỉ <b>5 lần</b> trong
tiêu đề &mdash; chênh 447 lần. Nghe như một cơ hội lớn.</p>
<p><b>Nhưng hãy cẩn thận.</b> Đây là từ khán giả dùng để <i>phản hồi sau khi nghe</i>, không
phải từ họ dùng để <i>tìm nội dung</i>. Nhồi &ldquo;Amen&rdquo; vào tiêu đề nhiều khả năng
không có tác dụng.</p>
<p>Bài học từ STEP_04 vẫn áp dụng: <b>tần suất cao không đồng nghĩa với tín hiệu mạnh</b>.
Bảng này nên dùng để chọn <b>giọng điệu</b> khi viết mô tả và trả lời bình luận &mdash; nơi
ngôn ngữ đồng cảm thật sự có giá trị.</p>
</div>

<h2 class="pb">6. Cấu trúc tiêu đề</h2>

<table>
<thead><tr><th>Đặc điểm</th><th>Video thắng (B1)</th><th>Video thua (B4)</th><th>Nhận định</th></tr></thead>
<tbody>
<tr><td>Số đoạn (ngăn bằng dấu |)</td><td class="n">{ts['B1']['med_seg']:.0f}</td>
 <td class="n">{ts['B4']['med_seg']:.0f}</td><td>Không khác biệt</td></tr>
<tr><td>Độ dài (ký tự)</td><td class="n">{ts['B1']['med_len']:.0f}</td>
 <td class="n">{ts['B4']['med_len']:.0f}</td><td>Không khác biệt</td></tr>
<tr><td>Có ghi thời lượng</td><td class="n">{ts['B1']['pct_dur']:.1f}%</td>
 <td class="n">{ts['B4']['pct_dur']:.1f}%</td><td>Không khác biệt</td></tr>
<tr><td>Có emoji</td><td class="n">{ts['B1']['pct_emoji']:.1f}%</td>
 <td class="n">{ts['B4']['pct_emoji']:.1f}%</td><td>Không khác biệt</td></tr>
</tbody></table>

<p>Kết quả này <b>nhất quán với STEP_04</b>: cấu trúc tiêu đề không phân biệt được thắng thua.
Viết ở mức chấp nhận được là đủ &mdash; đừng tốn thời gian tối ưu.</p>

<h3>6.1. Tiêu đề của video nổ nhất (tham khảo cấu trúc)</h3>
<table>
<thead><tr><th>Tiêu đề</th><th>View</th><th>Bội số</th><th>Định dạng</th></tr></thead>
<tbody>{tt_rows}</tbody></table>

<h3>6.2. Khung tiêu đề đề xuất</h3>
<div class="tpl">
[CẢM XÚC / TÌNH HUỐNG] | [PHONG CÁCH NHẠC CỤ THỂ] | [THỜI LƯỢNG]
</div>
<p>Ví dụ áp dụng các phát hiện ở trên:</p>
<div class="tpl">
When the Night Feels Long | Old School Gospel Blues | 2 Hours<br>
Thank You Lord for Bringing Me Through | Vintage Delta Blues Worship | 1 Hour<br>
Grateful Heart, Weary Body | 1950s Black Gospel Soul | 3 Hours
</div>
<p style="font-size:8.5pt;color:#6B615A">Khung này kết hợp: chủ đề <b>old-school</b> (lift 2,37)
và <b>tạ ơn</b> (lift 1,62), dùng <b>tên phong cách nhạc cụ thể</b> từ nhóm tag thắng, và ghi
<b>thời lượng dài</b> phù hợp định dạng chủ lực đã chốt ở STEP_07.</p>

<div class="box crit">
<span class="l">Cảnh báo: đừng sao chép nguyên văn tiêu đề đối thủ</span>
<p>STEP_07 phát hiện <b>132 tiêu đề</b> đang được nhiều kênh dùng chung, có kênh tới 55,4%
video trùng tiêu đề với kênh khác. Đây là rủi ro chính sách nội dung trùng lặp.</p>
<p><b>Học cấu trúc thì được, sao chép từng chữ thì không.</b></p>
</div>

<h2>7. Độ tin cậy và điều chưa biết</h2>
<table>
<thead><tr><th>Kết luận</th><th>Tin cậy</th><th>Lý do</th></tr></thead>
<tbody>
<tr><td>Old-school / vintage hiệu quả nhất</td><td class="wa">Vừa</td>
 <td>lift 2,37 p&lt;0,001, 20 kênh dùng &mdash; nhưng chỉ 4/8 kênh tốt hơn khi kiểm nội bộ</td></tr>
<tr><td>Kinh Thánh nên tránh làm hướng chính</td><td class="ok">Cao</td>
 <td>652 video, nhất quán với STEP_04 qua 3 lớp kiểm</td></tr>
<tr><td>Nhạc không lời nên tránh</td><td class="wa">Vừa</td>
 <td>lift 0,17 rất mạnh, nhưng chỉ 58 video và 5 kênh</td></tr>
<tr><td>Cấu trúc tiêu đề không quan trọng</td><td class="ok">Cao</td>
 <td>Nhất quán với 26 kiểm định ở STEP_04</td></tr>
<tr><td>Tag &ldquo;delta blues&rdquo;, &ldquo;slow blues&rdquo; là tín hiệu</td><td class="no">Thấp</td>
 <td>Mới là quan sát, chưa kiểm định riêng</td></tr>
</tbody></table>

<h3>Bằng chứng phản bác</h3>
<ul>
<li><b>Chủ đề được xác định bằng mẫu từ khóa trong tiêu đề</b> &mdash; không phải nội dung
thật của bản nhạc. Một bài có thể mang tinh thần &ldquo;old school&rdquo; mà không ghi chữ đó.</li>
<li><b>Tương quan, không phải nhân quả.</b> Kênh làm nội dung old-school có thể vốn đã có
chất lượng sản xuất tốt hơn.</li>
<li><b>&ldquo;Tạ ơn&rdquo; chỉ có 55 video và 3 kênh đủ dữ liệu kiểm nội bộ</b> &mdash;
mẫu nhỏ, kết luận cần thận trọng.</li>
<li><b>Chưa có ảnh thumbnail thật.</b> Cách đóng gói hình ảnh có thể quan trọng hơn chữ nghĩa
&mdash; phần này sẽ bổ sung khi có dữ liệu ảnh.</li>
</ul>

<h2>8. Khuyến nghị hành động</h2>
<table>
<thead><tr><th>Ưu tiên</th><th>Việc</th><th>Căn cứ</th></tr></thead>
<tbody>
<tr><td class="ac"><b>Cao</b></td><td>Định vị kênh theo hướng <b>old-school / vintage black gospel</b></td>
 <td>Lift cao nhất 2,37&times; và chỉ 3,96% thị trường khai thác; khớp khán giả 70 tuổi</td></tr>
<tr><td class="ac"><b>Cao</b></td><td>Luôn có <b>lời hát</b>, không làm nhạc không lời</td>
 <td>Chủ đề instrumental có lift 0,17 &mdash; kém nhất</td></tr>
<tr><td class="ac"><b>Cao</b></td><td>Ghi rõ <b>phong cách nhạc</b> trong tiêu đề và tag</td>
 <td>&ldquo;delta blues&rdquo;, &ldquo;slow blues&rdquo; chỉ xuất hiện ở video thắng</td></tr>
<tr><td>Vừa</td><td>Thử nghiệm chủ đề <b>tạ ơn / biết ơn</b></td>
 <td>Lift 1,62 nhưng mẫu nhỏ &mdash; nên A/B test</td></tr>
<tr><td>Vừa</td><td>Không chọn Thánh Vịnh làm hướng chính</td>
 <td>Lift 0,61 trên 652 video, đã đông</td></tr>
<tr><td>Thấp</td><td>Không đầu tư vào tối ưu SEO từ khóa</td>
 <td>Đề xuất thắng tìm kiếm 7:1; tag có trọng số nhỏ</td></tr>
</tbody></table>

<div class="box">
<span class="l">Việc còn lại</span>
<p><b>STEP_08 &mdash; Tổng hợp:</b> bản đồ khoảng trống đầy đủ, chiến lược gia nhập,
20&ndash;30 đề tài đầu tiên, kế hoạch 90 ngày, và backtest rubric.</p>
<p><b>Cập nhật khi có thumbnail:</b> STEP_04 sẽ được chạy lại với ảnh thật để phân tích bố cục,
khuôn mặt, kiểu chữ và mô-típ hình ảnh &mdash; những thứ 22 đặc trưng số không bắt được.</p>
</div>

</body></html>"""

out=N/"99_report/STEP06_Tu-khoa-Dong-goi.pdf"
HTML(string=DOC,base_url=".").write_pdf(out)
print(f"PDF: {out} ({out.stat().st_size/1024:.0f} KB)")
