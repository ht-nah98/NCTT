"""Sinh báo cáo PDF cho STEP_04 — Sàng lọc đối chứng.

Tên cũ "Công thức thắng" gây hiểu nhầm: bước này BÁC BỎ giả thuyết (0/20 đứng
vững), không rút ra công thức. Công thức sản xuất thật nằm ở STEP_10. Bài học T29.
"""
import json, pandas as pd, warnings, base64
from pathlib import Path
from weasyprint import HTML
warnings.filterwarnings("ignore")

N=Path("niches/christian-blues"); D=N/"04_outlier"
R=json.load(open(D/"_metrics_raw.json"))
T=pd.read_csv(D/"04_feature_tests.csv")
B=pd.read_csv(D/"06_binary_tests.csv")
PH=pd.read_csv(D/"05_repeated_phrases.csv")
W=pd.read_csv(D/"07_bible_within_channel.csv")
def img(n): return "data:image/png;base64,"+base64.b64encode((D/n).read_bytes()).decode()

def vb(v):
    return {"XÁC NHẬN":'<span class="ok">XÁC NHẬN</span>',
            "YẾU":'<span class="wa">YẾU</span>'}.get(v,'<span class="no">BÁC BỎ</span>')

def meas(m):
    """Cột THƯỚC ĐO — kết luận yếu phải TRÔNG yếu.
    8 đặc trưng thumbnail lấy từ Excel nguồn (proxy), không đọc ảnh thật;
    STEP_04b/04g đo lại và chứng minh `text_score` hỏng. Bài học T29."""
    return ('<span class="wa" title="đo gián tiếp — xem STEP_04b">proxy ⚠</span>'
            if m == "proxy" else '<span style="color:#7A6F68">trực tiếp</span>')

n_proxy = int((T["measure"] == "proxy").sum())

t_rows="\n".join(
 f'<tr><td>{r.feature}</td><td class="n">{r.B1:,.3f}</td><td class="n">{r.B4:,.3f}</td>'
 f'<td class="n">{r.p:.3f}</td><td class="n">{r.cliffs_delta:+.3f}</td>'
 f'<td>{meas(r.measure)}</td><td>{vb(r.verdict)}</td></tr>'
 for _,r in T.iterrows())

b_rows="\n".join(
 f'<tr class="{"hi" if r.verdict=="XÁC NHẬN" else ""}"><td>{r.feature}</td>'
 f'<td class="n">{r.B1_pct:.1f}%</td><td class="n">{r.B4_pct:.1f}%</td>'
 f'<td class="n">{r.B1_n}</td><td class="n">{r.B4_n}</td>'
 f'<td class="n">{"∞" if r.lift==float("inf") else f"{r.lift:.1f}×"}</td>'
 f'<td class="n">{r.p:.3f}</td><td>{vb(r.verdict)}</td></tr>'
 for _,r in B.iterrows())

fm=pd.DataFrame(R["format_b1b4"])
fm_rows="\n".join(
 f'<tr><td><b>{r.duration_band}</b></td><td class="n">{int(r["B1_thắng"])}</td>'
 f'<td class="n">{int(r["B4_thua"])}</td><td class="n">{r.pct_B1:.1f}%</td></tr>'
 for _,r in fm.iterrows())

fa=pd.DataFrame(R["format_all"]).set_index("duration_band").reindex(
    ["Shorts","1-6m","6-30m","30-60m","1-3h","3h+"])
fa_rows="\n".join(
 f'<tr class="{"hi" if i in ("Shorts","1-6m") else ""}"><td><b>{i}</b></td>'
 f'<td class="n">{int(r.n):,}</td><td class="n">{r.vpd:.1f}</td>'
 f'<td class="n">{int(r.mv):,}</td></tr>' for i,r in fa.iterrows())

ph=PH[PH.n_words==1].head(12)
ph_rows="\n".join(
 f'<tr><td><b>{r.phrase}</b></td><td class="n">{int(r.n_channels)}</td>'
 f'<td class="n">{int(r.in_B4_count)}</td>'
 f'<td>{"<span class=\'no\'>cả hai nhóm</span>" if r.in_B4_count>=r.n_channels*0.7 else "<span class=\'wa\'>thiên về nhóm thắng</span>"}</td></tr>'
 for _,r in ph.iterrows())

w_rows="\n".join(
 f'<tr><td>{r.handle}</td><td class="n">{int(r.n_bib)}</td><td class="n">{r.vpd_bib:.1f}</td>'
 f'<td class="n">{r.vpd_no:.1f}</td><td class="n">{r.lift:.2f}×</td>'
 f'<td>{"<span class=\'ok\'>tốt hơn</span>" if r.lift>1 else "<span class=\'no\'>kém hơn</span>"}</td></tr>'
 for _,r in W.iterrows())

bm=R["bible_market_wide"]; bw=R["bible_within_channel"]
n_conf=int((T.verdict=="XÁC NHẬN").sum()+(B.verdict=="XÁC NHẬN").sum())
n_all=len(T)+len(B)

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
img {{ width:100%;margin:8pt 0; }} .half {{ width:62%; }}
.f {{ font-size:7.5pt;color:#7A6F68;text-align:center;margin:-4pt 0 12pt; }}
code {{ background:#F2EEE8;padding:.5pt 3pt;font-size:8.5pt; }}
.formula {{ background:#F7F4F0;border:.6pt solid #E2DAD1;padding:7pt 10pt;
 font-size:8.5pt;margin:7pt 0;line-height:1.7; }}
.pb {{ page-break-before:always; }}
ul {{ margin:6pt 0;padding-left:15pt; }} li {{ margin:3pt 0; }}
</style></head><body>

<h1>Sàng lọc đối chứng &mdash; Christian Blues</h1>
<p class="sub">Báo cáo giai đoạn 3 &mdash; Loại bỏ giả thuyết sai: 435 video thắng đối chiếu 161 video thua</p>
<div class="meta">
STEP_04 &nbsp;•&nbsp; Agent A3 &nbsp;•&nbsp; Phương pháp: so sánh có kiểm soát + kiểm định thống kê
&nbsp;•&nbsp; Dữ liệu crawl 13/08/2026 &nbsp;•&nbsp; Lập ngày 15/08/2026
</div>

<h2>1. Tóm tắt điều hành</h2>

<div class="box">
<span class="l">Bước này LOẠI TRỪ, không tổng hợp</span>
<p>Câu hỏi ở đây là <b>&ldquo;đặc trưng nào KHÔNG phân biệt video thắng với video thua?&rdquo;</b>
&mdash; trả lời bằng nhóm đối chứng. Đây là phép <b>sàng lọc</b>, chạy được sớm vì chỉ cần
tiêu đề và metadata.</p>
<p><b>Công thức sản xuất</b> &mdash; tiêu đề viết thế nào, mô tả ra sao, thumbnail dựng kiểu gì
&mdash; là đầu ra của <b>STEP_10 · Playbook</b>, bước tổng hợp SAU khi đã có phân tích
thumbnail (STEP_04b), chân dung khách hàng (STEP_05) và từ khóa (STEP_06).</p>
<p class="f" style="text-align:left;margin:6pt 0 0">
STEP_04 nói <b>đừng làm gì</b> &nbsp;→&nbsp; STEP_10 nói <b>nên làm gì</b>.</p>
</div>

<div class="box crit">
<span class="l">Kết quả chính: gần như MỌI giả thuyết về "công thức thắng" đều bị bác bỏ</span>
<p>Tôi kiểm định <b>{n_all} đặc trưng</b> của video &mdash; độ dài tiêu đề, emoji, hashtag,
độ sáng thumbnail, độ dài video, tên sách Kinh Thánh, và nhiều yếu tố khác.</p>
<p><b>Không một đặc trưng nào đứng vững</b> sau khi kiểm chứng đầy đủ. Video thắng và video
thua <b>gần như giống hệt nhau</b> ở mọi thứ đo được từ tiêu đề và ảnh đại diện.</p>
</div>

<div class="kpi">
<div><div class="k">Đặc trưng đã kiểm</div><div class="v">{n_all}</div>
 <div class="c">tiêu đề · thumbnail · định dạng</div></div>
<div><div class="k">Đứng vững sau kiểm chứng</div><div class="v dn">0</div>
 <div class="c">sau khi loại artefact &amp; Simpson</div></div>
<div><div class="k">Nhóm so sánh</div><div class="v">435<span style="font-size:10pt"> vs </span>161</div>
 <div class="c">thắng vs thua</div></div>
<div><div class="k">Kênh có cả hai nhóm</div><div class="v ac">{R['paired_channels']}</div>
 <div class="c">cho phép so sánh ghép cặp</div></div>
</div>

<div class="box ok">
<span class="l">Vì sao đây là kết quả TỐT, không phải thất bại</span>
<p>Nếu tôi chỉ nhìn video thắng (như cách làm phổ biến), tôi đã báo cáo với bạn rằng
&ldquo;công thức thắng là dùng tên Thánh Vịnh trong tiêu đề&rdquo; &mdash; nghe rất thuyết phục,
vì <b>10,1% video thắng có tên sách Kinh Thánh so với chỉ 1,2% video thua, gấp 8,1 lần</b>.</p>
<p>Nhưng khi kiểm trên toàn bộ thị trường, video có tên Kinh Thánh lại đạt hiệu suất
<b>thấp hơn 52%</b>. Nếu bạn làm theo &ldquo;công thức&rdquo; đó, kết quả sẽ tệ đi.</p>
<p><b>Giá trị của bước này là ngăn bạn đầu tư vào những thứ không có tác dụng.</b></p>
</div>

<h2>2. Phương pháp: vì sao cần nhóm đối chứng</h2>

<div class="formula">
<b>Nhóm B1 (thắng)</b> = video vượt trung vị kênh ≥5 lần, và ≥20.000 view &rarr; 435 video<br>
<b>Nhóm B4 (thua)</b> = video dưới trung vị kênh ≤0,2 lần, nhưng ≥500 view &rarr; 161 video
</div>

<p>Điểm mấu chốt: cả hai nhóm đều <b>chuẩn hóa theo chính kênh đó</b>. Một video 50.000 view
trên kênh trung vị 40.000 là bình thường; cũng 50.000 view trên kênh trung vị 500 là bùng nổ.</p>

<p><b>{R['paired_channels']} kênh có cả video thắng lẫn video thua</b> &mdash; nghĩa là ta so sánh
được trong cùng một kênh, loại bỏ ảnh hưởng &ldquo;kênh mạnh thì video nào cũng mạnh&rdquo;.</p>

<h3>2.1. Hai thước đo dùng trong báo cáo</h3>
<table>
<thead><tr><th>Thước đo</th><th>Nghĩa là gì</th><th>Ngưỡng để tin</th></tr></thead>
<tbody>
<tr><td><b>p-value</b></td>
 <td>Xác suất thấy chênh lệch này do ngẫu nhiên. p = 0,03 nghĩa là 3% khả năng là may rủi.</td>
 <td class="n">p &lt; 0,01</td></tr>
<tr><td><b>Cliff's delta</b></td>
 <td>Độ mạnh của chênh lệch, từ &minus;1 đến +1. Gần 0 = hai nhóm gần như trùng nhau.</td>
 <td class="n">|delta| ≥ 0,30</td></tr>
</tbody></table>
<p><b>Phải đạt cả hai</b> mới coi là XÁC NHẬN. Chỉ có p nhỏ mà hiệu ứng yếu thì vẫn vô dụng
&mdash; với mẫu lớn, chênh lệch cực nhỏ cũng cho p nhỏ.</p>

<h2 class="pb">3. Kết quả kiểm định</h2>

<h3>3.1. Các đặc trưng liên tục</h3>
<img src="{img('c1_effects.png')}">
<p class="f">Cột càng ngắn thì hai nhóm càng giống nhau. Hầu hết nằm sát vạch 0.</p>

<table>
<thead><tr><th>Đặc trưng</th><th>Nhóm thắng<br>(trung vị)</th><th>Nhóm thua<br>(trung vị)</th>
<th>p-value</th><th>Cliff's<br>delta</th><th>Thước đo</th><th>Kết luận</th></tr></thead>
<tbody>{t_rows}</tbody></table>

<div class="box crit">
<span class="l">⚠ {n_proxy} dòng đánh dấu &ldquo;proxy&rdquo; có độ tin cậy THẤP HƠN phần còn lại</span>
<p>Các đặc trưng thumbnail ở đây (độ sáng, bão hòa, tương phản, điểm chữ, rực màu, vùng tối,
tập trung giữa ảnh, mật độ đường nét) <b>không đọc từ ảnh thật</b> &mdash; chúng được trích sẵn
trong file Excel nguồn.</p>
<p><b>Một thước đo trong số đó đã được chứng minh là hỏng.</b> STEP_04b/04g đo lại bằng
YuNet + YOLO-seg + EasyOCR cho thấy <code>text_score</code> (&ldquo;Điểm chữ trên ảnh&rdquo;)
chỉ tương quan <b>0,233</b> với lượng chữ thật &mdash; gần như không liên quan.</p>
<p>Vì vậy kết luận &ldquo;BÁC BỎ&rdquo; của {n_proxy} dòng này chỉ có hiệu lực
<b>với thước đo proxy</b>, không phải kết luận cuối cùng về thumbnail.
&rarr; Xem <b>STEP_04b · Phân tích Thumbnail</b> để có số đo từ ảnh thật.</p>
</div>

<div class="box">
<span class="l">Những "quy tắc" phổ biến đã bị bác bỏ</span>
<p><b>Độ dài tiêu đề:</b> thắng 74 ký tự, thua 73 ký tự. Chênh 1 ký tự (p = 0,851).
&rarr; Viết tiêu đề dài hay ngắn <b>không quan trọng</b>.</p>
<p><b>Emoji:</b> cả hai nhóm trung vị đều 0 (p = 0,939). &rarr; Emoji <b>không giúp gì</b>.</p>
<p><b>Thumbnail sáng/tối, rực màu, nhiều chữ:</b> tất cả đều bác bỏ (p &gt; 0,08)
&mdash; nhưng <b>chỉ theo thước đo proxy</b>, xem cảnh báo phía trên.
&rarr; Kết luận về thumbnail phải đọc ở <b>STEP_04b</b>, không phải ở đây.</p>
<p><b>Độ dài video:</b> thắng 2.650 giây, thua 1.825 giây, nhưng p = 0,597 và delta = 0,028.
&rarr; Chênh lệch <b>không đáng tin</b>.</p>
</div>

<h3>3.2. Các đặc trưng có/không (kiểm định tỷ lệ)</h3>
<p>Với biến chỉ có hai giá trị (có hoặc không), trung vị vô nghĩa vì hầu hết đều bằng 0.
Phải dùng <b>kiểm định Fisher trên tỷ lệ</b>:</p>
<table>
<thead><tr><th>Đặc trưng</th><th>% nhóm<br>thắng</th><th>% nhóm<br>thua</th>
<th>Số lượng<br>thắng</th><th>Số lượng<br>thua</th><th>Lift</th><th>p-value</th><th>Kết luận</th></tr></thead>
<tbody>{b_rows}</tbody></table>

<p>Hai đặc trưng có vẻ đạt: <b>tên sách Kinh Thánh (8,1×)</b> và <b>chữ Psalm (3,3×)</b>.
Phần tiếp theo kiểm chứng chúng &mdash; và cả hai đều <b>sụp đổ</b>.</p>

<h2 class="pb">4. Nghịch lý Simpson: bài học quan trọng nhất</h2>

<img src="{img('c2_simpson.png')}">

<p>Trong mẫu B1/B4, video có tên sách Kinh Thánh chiếm <b>10,1% nhóm thắng</b> nhưng chỉ
<b>1,2% nhóm thua</b> &mdash; lift 8,1 lần, p &lt; 0,001. Nhìn qua thì đây là công thức rõ ràng.</p>

<h3>4.1. Kiểm chứng trên toàn bộ thị trường</h3>
<table>
<thead><tr><th>Nhóm video</th><th>Số lượng</th><th>VPD trung vị</th><th>Chênh lệch</th></tr></thead>
<tbody>
<tr><td>Có tên sách Kinh Thánh</td><td class="n">{bm['n_bib']:,}</td>
 <td class="n dn">{bm['vpd_bib']:.2f}</td><td class="n dn">&minus;52%</td></tr>
<tr><td>Không có</td><td class="n">{bm['n_no']:,}</td>
 <td class="n">{bm['vpd_no']:.2f}</td><td class="n">&mdash;</td></tr>
</tbody></table>
<p>Trên toàn bộ <b>5.609 video đã chín</b>, video có tên Kinh Thánh đạt hiệu suất
<b>chỉ bằng 0,48 lần</b> video không có (p &lt; 0,00001). <b>Ngược hoàn toàn</b> với kết luận
từ mẫu B1/B4.</p>

<h3>4.2. Kiểm trong từng kênh</h3>
<img src="{img('c3_within.png')}" class="half">
<table>
<thead><tr><th>Kênh</th><th>Số video<br>có KT</th><th>VPD<br>có KT</th><th>VPD<br>không</th>
<th>Lift</th><th>Kết quả</th></tr></thead>
<tbody>{w_rows}</tbody></table>
<p>Trong <b>{bw['n_channels']} kênh</b> có đủ dữ liệu cả hai loại, chỉ <b>{bw['n_better']} kênh</b>
cho kết quả tốt hơn khi dùng tên Kinh Thánh. Trung vị lift = <b>{bw['median_lift']:.2f}×</b>
&mdash; tức <i>kém hơn</i> một chút.</p>

<div class="box crit">
<span class="l">Vì sao xảy ra nghịch lý này</span>
<p>Một vài kênh <b>chuyên</b> làm nội dung Thánh Vịnh (ví dụ <code>holygroove-1</code> có 76,6%
video loại này). Những kênh đó có một số video cực nổ, nên video Kinh Thánh xuất hiện nhiều
trong nhóm outlier.</p>
<p>Nhưng bản thân việc <b>đưa tên Kinh Thánh vào tiêu đề không làm video chạy tốt hơn</b>.
Cái thắng là <i>kênh đó</i>, không phải <i>đặc điểm đó</i>.</p>
<p>Đây gọi là <b>nghịch lý Simpson</b>: xu hướng đúng trong từng nhóm nhỏ có thể đảo ngược
khi gộp lại &mdash; hoặc ngược lại.</p>
</div>

<h3>4.3. Một phát hiện tôi đã phải loại bỏ</h3>
<div class="box crit">
<span class="l">Tỷ lệ tương tác &mdash; artefact toán học</span>
<p>Kiểm định ban đầu cho kết quả rất mạnh: nhóm thắng có tỷ lệ tương tác <b>2,3%</b> so với
nhóm thua <b>4,3%</b>, p &lt; 0,001, Cliff's delta = &minus;0,682 &mdash; hiệu ứng mạnh nhất
trong tất cả.</p>
<p><b>Nhưng đây không phải phát hiện.</b> Tỷ lệ tương tác = (like + bình luận) ÷ view.
Nhóm thắng có view trung vị <b>71.314</b>, nhóm thua chỉ <b>863</b> &mdash; gấp 82 lần.
Mẫu số lớn hơn nên tỷ lệ nhỏ hơn, một cách máy móc.</p>
<p>Xác nhận: tương quan Spearman giữa view và tỷ lệ tương tác trên toàn bộ dữ liệu là
<b>&minus;0,202</b> &mdash; video càng nhiều view thì tỷ lệ tương tác càng thấp, đúng như dự đoán.
Đã loại khỏi kết quả.</p>
</div>

<h2 class="pb">5. Định dạng video</h2>

<h3>5.1. Giả thuyết từ báo cáo trước</h3>
<p>Báo cáo STEP_01+02 nêu giả thuyết: <b>định dạng 1&ndash;6 phút hiệu quả hơn mix dài 1&ndash;3 giờ</b>,
và thị trường đang đầu tư sai chỗ. Nay kiểm chứng bằng nhóm đối chứng.</p>

<img src="{img('c4_format.png')}">
<table>
<thead><tr><th>Định dạng</th><th>Số video<br>toàn ngách</th><th>VPD trung vị</th><th>View trung vị</th></tr></thead>
<tbody>{fa_rows}</tbody></table>

<h3>5.2. Nhưng nhóm đối chứng cho kết quả khác</h3>
<table>
<thead><tr><th>Định dạng</th><th>Số video<br>thắng</th><th>Số video<br>thua</th><th>Tỷ lệ thắng</th></tr></thead>
<tbody>{fm_rows}</tbody></table>
<p>Chi-square p = <b>{R['format_chi2_p']:.4f}</b> &mdash; có khác biệt thống kê, nhưng
<b>không theo hướng giả thuyết</b>. Định dạng có tỷ lệ thắng cao nhất là <b>30&ndash;60 phút
(80,6%)</b>, không phải 1&ndash;6 phút (78,4%). Và 1&ndash;3 giờ đạt 73,6% &mdash; không hề tệ.</p>

<div class="box">
<span class="l">Kết luận về định dạng: CHƯA KẾT LUẬN ĐƯỢC</span>
<p>Hai thước đo cho hai câu trả lời khác nhau:</p>
<p><b>Theo VPD toàn ngách:</b> định dạng ngắn (Shorts 21,6 và 1&ndash;6m 15,6) hiệu quả hơn
mix dài (1&ndash;3h 11,7).</p>
<p><b>Theo tỷ lệ thắng trong nhóm đối chứng:</b> mọi định dạng đều có tỷ lệ thắng
58&ndash;81%, không có định dạng nào vượt trội rõ rệt.</p>
<p><b>Cách giải thích khả dĩ:</b> VPD thiên vị video ngắn vì chúng dễ đạt view nhanh, nhưng
mix dài giữ người xem lâu hơn &mdash; mà thời lượng xem mới là thứ YouTube thưởng.
Dữ liệu hiện có <b>không đo được thời lượng xem</b>, nên không kết luận được.</p>
</div>

<h2>6. Chủ đề lặp lại</h2>
<p>Quy tắc: cụm từ xuất hiện ở <b>≥3 kênh khác nhau</b> trong nhóm thắng thì mới coi là công
thức, không phải may mắn. Nhưng phải đối chiếu xem cụm đó có xuất hiện ở nhóm thua không.</p>
<table>
<thead><tr><th>Từ khóa</th><th>Số kênh thắng<br>dùng từ này</th><th>Số lần xuất hiện<br>ở nhóm thua</th><th>Đánh giá</th></tr></thead>
<tbody>{ph_rows}</tbody></table>

<div class="box">
<span class="l">Hầu hết từ khóa xuất hiện ở CẢ HAI nhóm</span>
<p>&ldquo;prayer&rdquo; xuất hiện ở 23 kênh thắng &mdash; nhưng cũng 26 lần ở nhóm thua.
&ldquo;god&rdquo;, &ldquo;praise&rdquo;, &ldquo;peace&rdquo; tương tự.</p>
<p>Đây là <b>từ vựng chung của ngách</b>, không phải yếu tố phân biệt. Dùng chúng là điều
kiện cần, không phải điều kiện đủ.</p>
<p><b>Hai ngoại lệ đáng chú ý:</b> <code>grace</code> (10 kênh thắng, chỉ 2 lần ở nhóm thua)
và <code>strength</code> (10 kênh thắng, 3 lần ở nhóm thua). Tỷ lệ lệch rõ hơn hẳn &mdash;
đáng thử nghiệm, nhưng mẫu còn nhỏ nên <b>chưa đủ để kết luận</b>.</p>
</div>

<h2 class="pb">7. Ý nghĩa thực tiễn</h2>

<div class="box ok">
<span class="l">Điều này nói gì về cách vào ngách</span>
<p><b>1. Đừng tốn thời gian tối ưu tiêu đề và thumbnail theo "bí quyết".</b> Dữ liệu cho thấy
những yếu tố này không phân biệt được thắng thua trong ngách này. Làm ở mức chấp nhận được
là đủ.</p>
<p><b>2. Yếu tố quyết định nằm ở chỗ dữ liệu này không đo được:</b> chất lượng bản nhạc,
độ giữ chân người nghe, thời điểm YouTube đẩy video. Đây là giới hạn thật của dữ liệu
metadata.</p>
<p><b>3. Kết hợp với phát hiện STEP_03:</b> nhịp đăng dày cho tổng view gấp 5,3 lần. Khi
không có công thức nội dung rõ ràng, <b>số lượng và tính đều đặn là đòn bẩy đáng tin nhất</b>.</p>
</div>

<h3>7.1. Những gì KHÔNG nên làm</h3>
<ul>
<li><b>Không</b> nhồi tên Thánh Vịnh vào tiêu đề &mdash; toàn thị trường cho thấy kém hơn 52%</li>
<li><b>Không</b> đầu tư vào emoji, độ dài tiêu đề, hay tinh chỉnh màu thumbnail</li>
<li><b>Không</b> bỏ mix dài để chạy theo video ngắn &mdash; dữ liệu chưa đủ để kết luận</li>
</ul>

<h3>7.2. Những gì nên làm</h3>
<p>Bước này <b>không trả lời được câu hỏi đó</b> &mdash; nó chỉ loại trừ. Vài hướng duy nhất
còn đứng vững sau sàng lọc:</p>
<ul>
<li>Duy trì <b>nhịp đăng đều và dày</b> (bằng chứng mạnh nhất từ STEP_03)</li>
<li>Thử nghiệm A/B với <code>grace</code> và <code>strength</code> trong tiêu đề &mdash;
tín hiệu yếu nhưng đáng thử</li>
<li>Tập trung nguồn lực vào <b>chất lượng bản nhạc</b>, vì đó là biến không đo được nhưng
nhiều khả năng là biến quyết định</li>
</ul>
<div class="box ok">
<span class="l">Công thức sản xuất đầy đủ nằm ở STEP_10</span>
<p>Tiêu đề viết theo khuôn nào, mô tả gồm những khối gì, thẻ ra sao, thời lượng và nhịp đăng
bao nhiêu, thumbnail dựng thế nào &mdash; xem <b>STEP_08 mục 7</b> và
<code>09_playbook/CHANNEL_PLAYBOOK.json</code>.</p>
<p>Bước đó tổng hợp <b>sau</b> khi đã có thumbnail thật (04b), chân dung khách hàng (05)
và từ khóa (06) &mdash; nên nó mới đủ dữ kiện để nói &ldquo;nên làm gì&rdquo;.</p>
</div>

<h2>8. Độ tin cậy và điều chưa biết</h2>
<table>
<thead><tr><th>Kết luận</th><th>Độ tin cậy</th><th>Lý do</th></tr></thead>
<tbody>
<tr><td><b>Tiêu đề</b> không phân biệt thắng thua</td><td class="ok">Cao</td>
 <td>Đo trực tiếp từ metadata, mẫu 596 video, kết quả nhất quán</td></tr>
<tr><td><b>Thumbnail</b> không phân biệt thắng thua</td><td class="wa">Thấp</td>
 <td>{n_proxy} đặc trưng đo bằng proxy, trong đó <code>text_score</code> đã được chứng minh
 hỏng (tương quan 0,233). Kết luận thật ở STEP_04b</td></tr>
<tr><td>Kinh Thánh KHÔNG phải công thức thắng</td><td class="ok">Cao</td>
 <td>Kiểm 3 lớp: mẫu B1/B4, toàn thị trường, và trong từng kênh</td></tr>
<tr><td>Tỷ lệ tương tác là artefact</td><td class="ok">Cao</td>
 <td>Xác nhận bằng tương quan âm giữa view và engagement</td></tr>
<tr><td>Định dạng nào tốt nhất</td><td class="no">Thấp</td>
 <td><b>Chưa kết luận được</b> &mdash; hai thước đo mâu thuẫn</td></tr>
<tr><td><code>grace</code>, <code>strength</code> có tác dụng</td><td class="no">Thấp</td>
 <td>Mẫu nhỏ, chưa kiểm định riêng</td></tr>
</tbody></table>

<h3>Bằng chứng phản bác</h3>
<ul>
<li><b>Chỉ đo được metadata.</b> Tiêu đề, thumbnail, độ dài &mdash; không đo được chất lượng
âm nhạc, retention, hay CTR. Rất có thể công thức thắng nằm hoàn toàn ở những biến này.</li>
<li><b>Nhóm B4 có thể không phải "thua" thật.</b> Nó gồm video dưới trung vị kênh &mdash;
trên kênh mạnh thì đó vẫn có thể là video tốt.</li>
<li><b>161 video đối chứng là ít</b> so với 435 video thắng. Với các đặc trưng hiếm,
kiểm định thiếu lực thống kê.</li>
<li><b>Việc không tìm thấy khác biệt không chứng minh là không có khác biệt.</b> Có thể
công thức tồn tại nhưng phức tạp hơn (tương tác nhiều yếu tố), mà phương pháp một biến
không bắt được.</li>
</ul>

<h2>9. Việc tiếp theo</h2>
<table>
<thead><tr><th>Ưu tiên</th><th>Việc</th><th>Vì sao</th></tr></thead>
<tbody>
<tr><td class="ac"><b>Cao</b></td><td>STEP_05 &mdash; Chân dung khách hàng</td>
 <td>Metadata đã cạn tín hiệu. 145.150 bình luận là nguồn còn lại &mdash; và là nguồn giàu nhất.</td></tr>
<tr><td>Vừa</td><td>Giải mã <code>vintage_gospel_vgx</code> thủ công</td>
 <td>70.244 view/video với 43 video. Thống kê không giải thích được &mdash; cần nghe nhạc và xem trực tiếp.</td></tr>
<tr><td>Thấp</td><td>Mở rộng <code>media_probe</code></td>
 <td>Nếu công thức nằm ở đặc trưng âm thanh thì cần dữ liệu này (hiện chỉ 0,6%)</td></tr>
</tbody></table>

<div class="box">
<span class="l">Ghi chú phương pháp</span>
<p>Bước này <b>không tạo ra công thức</b> để làm theo. Nhưng nó loại bỏ <b>{n_all} giả thuyết sai</b>
mà nếu tin theo, bạn sẽ tốn thời gian và tiền bạc vào những thứ không có tác dụng.</p>
<p>Trong nghiên cứu, kết quả âm tính có giá trị ngang kết quả dương tính &mdash; miễn là được
kiểm chứng đúng cách.</p>
</div>

</body></html>"""

out=N/"99_report/STEP04_Sang-loc-Doi-chung.pdf"
HTML(string=DOC,base_url=".").write_pdf(out)
print(f"PDF: {out} ({out.stat().st_size/1024:.0f} KB)")
