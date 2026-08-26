"""Sinh báo cáo PDF cho STEP_05 — Chân dung khách hàng."""
import json, pandas as pd, warnings, base64, html
from pathlib import Path
from weasyprint import HTML
warnings.filterwarnings("ignore")

N=Path("niches/christian-blues"); D=N/"05_audience"
R=json.load(open(D/"_metrics_raw.json"))
d=pd.read_parquet(D/"_comments_tagged.parquet")
SIG=pd.read_csv(D/"04_signal_tests.csv")
def img(n): return "data:image/png;base64,"+base64.b64encode((D/n).read_bytes()).decode()
def esc(t,n=330):
    t=" ".join(str(t).split())
    return html.escape(t[:n]+("…" if len(t)>n else ""))

def quotes(mask,k=3,minl=0):
    sub=d[mask & (d.tlen>=minl)].nlargest(k,"like_count")
    return "\n".join(
      f'<div class="q"><p>&ldquo;{esc(r.t)}&rdquo;</p><span>{int(r.like_count):,} lượt thích</span></div>'
      for _,r in sub.iterrows())

lblS={"finally":"&ldquo;finally / at last&rdquo;","never_heard":"&ldquo;never heard&rdquo;",
 "p_elder":"Người 60+ hoặc nghỉ hưu","p_music":"Nhạc công","struggling":"Đang khó khăn",
 "better_than":"&ldquo;better than&rdquo;","cant_stand":"&ldquo;can't stand&rdquo;",
 "healing":"Nhắc chữa lành","p_healing":"Tìm chữa lành","p_convert":"Mới cải đạo"}
def vb(v): return {"XÁC NHẬN":'<span class="ok">XÁC NHẬN</span>',
                   "YẾU":'<span class="wa">YẾU</span>'}.get(v,'<span class="no">BÁC BỎ</span>')
sig_rows="\n".join(
 f'<tr class="{"hi" if r.verdict=="XÁC NHẬN" else ""}"><td>{lblS.get(r.signal,r.signal)}</td>'
 f'<td class="n">{int(r.n)}</td><td class="n">{r.like_median:.0f}</td>'
 f'<td class="n">{r.vs_baseline:.1f}×</td><td class="n">{r.p:.4f}</td><td>{vb(r.verdict)}</td></tr>'
 for _,r in SIG.sort_values("vs_baseline",ascending=False).iterrows())

lblC={"prayer_devo":"Cầu nguyện / tĩnh tâm","morning":"Buổi sáng","sick_hosp":"Bệnh tật / bệnh viện",
 "grief":"Tang chế / mất người thân","driving":"Lái xe","housework":"Việc nhà",
 "work":"Nơi làm việc","sleep_night":"Đêm khuya / khó ngủ"}
ctx_rows="\n".join(
 f'<tr><td>{lblC.get(k,k)}</td><td class="n">{v["n"]}</td><td class="n">{v["pct"]:.2f}%</td></tr>'
 for k,v in sorted(R["context"].items(),key=lambda x:-x[1]["n"]))

lblD={"repeat":"Nghe lặp lại / hằng ngày","algorithm":"YouTube tự đề xuất",
 "subscribed":"Vừa đăng ký kênh","shared":"Người quen chia sẻ","searched":"Chủ động tìm kiếm"}
disc_rows="\n".join(
 f'<tr class="{"hi" if k=="algorithm" else ""}"><td>{lblD.get(k,k)}</td>'
 f'<td class="n">{v["n"]}</td><td class="n">{v["pct"]:.2f}%</td></tr>'
 for k,v in sorted(R["discovery"].items(),key=lambda x:-x[1]["n"]))

lblA={"recovery":"Đang cai nghiện / phục hồi","new_convert":"Mới cải đạo","widow":"Góa bụa",
 "musician":"Nhạc công","trucker":"Tài xế đường dài","nurse_care":"Điều dưỡng / chăm sóc",
 "longtime_faith":"Theo đạo lâu năm","retired":"Đã nghỉ hưu","veteran":"Cựu quân nhân",
 "disabled":"Khuyết tật"}
attr_rows="\n".join(
 f'<tr><td>{lblA.get(k,k)}</td><td class="n">{v["n"]}</td><td class="n">{v["pct"]:.2f}%</td></tr>'
 for k,v in sorted(R["attributes"].items(),key=lambda x:-x[1]["n"]) if v["n"]>0)

vocab=list(R["vocab_top"].items())[:24]
vocab_rows="".join(f'<span class="chip">{k} <b>{v}</b></span>' for k,v in vocab)

ad=R["age"]
age_rows="\n".join(f'<tr class="{"hi" if k in ("60-74","75+") else ""}"><td>{k} tuổi</td>'
 f'<td class="n">{v}</td><td class="n">{v/ad["n"]*100:.0f}%</td></tr>' for k,v in ad["dist"].items())

DOC=f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size:A4;margin:17mm 15mm 20mm;
 @bottom-center {{ content counter(page) " / " counter(pages);
  font-family:"DejaVu Sans";font-size:8pt;color:#9A8E85; }} }}
body {{ font-family:"DejaVu Sans",sans-serif;font-size:9.5pt;line-height:1.55;color:#1A1614; }}
h1 {{ font-size:23pt;margin:0 0 6pt;letter-spacing:-.4pt; }}
h2 {{ font-size:13pt;margin:20pt 0 7pt;padding-bottom:4pt;
 border-bottom:1.5pt solid #1A1614;page-break-after:avoid; }}
h3 {{ font-size:10.5pt;margin:14pt 0 5pt;color:#8C3A2B;page-break-after:avoid; }}
h4 {{ font-size:9.5pt;margin:10pt 0 4pt; }}
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
.q {{ border-left:2pt solid #CFC4B8;padding:5pt 0 5pt 10pt;margin:7pt 0;page-break-inside:avoid; }}
.q p {{ margin:0 0 3pt;font-style:italic;font-size:9pt;line-height:1.5; }}
.q span {{ font-size:7.5pt;color:#8C3A2B;font-weight:bold; }}
.persona {{ border:.8pt solid #CFC4B8;padding:10pt 12pt;margin:11pt 0;page-break-inside:avoid; }}
.persona h4 {{ margin:0 0 3pt;font-size:11pt;color:#8C3A2B; }}
.persona .tag {{ font-size:7.5pt;color:#7A6F68;margin-bottom:7pt; }}
.chip {{ display:inline-block;background:#F2EEE8;border:.5pt solid #E2DAD1;
 padding:2pt 6pt;margin:2pt;font-size:8pt;border-radius:2pt; }}
.pb {{ page-break-before:always; }}
ul {{ margin:6pt 0;padding-left:15pt; }} li {{ margin:3pt 0; }}
</style></head><body>

<h1>Chân dung khách hàng &mdash; Christian Blues</h1>
<p class="sub">Báo cáo giai đoạn 4 &mdash; Khán giả là ai, vì sao họ nghe, họ đến từ đâu</p>
<div class="meta">
STEP_05 &nbsp;•&nbsp; Agent A4 &nbsp;•&nbsp; Nguồn: {R['n_analyzed']:,} bình luận đã lọc
(từ 145.150 gốc) &nbsp;•&nbsp; Dữ liệu crawl 13/08/2026 &nbsp;•&nbsp; Lập ngày 15/08/2026
</div>

<h2>1. Tóm tắt điều hành</h2>

<div class="box ok">
<span class="l">Đây là nguồn dữ liệu giá trị nhất trong toàn bộ nghiên cứu</span>
<p>STEP_04 cho thấy metadata (tiêu đề, thumbnail) <b>đã cạn tín hiệu</b>. Nhưng bình luận thì
ngược lại &mdash; khán giả <b>tự nói ra</b> họ là ai, vì sao nghe, và nghe lúc nào.</p>
<p>Quan trọng hơn: <b>lượt thích trên bình luận là phiếu bầu của cộng đồng</b>. Một bình luận
1.444 lượt thích không phải ý kiến một người &mdash; đó là 1.444 người cùng đồng tình.</p>
</div>

<div class="kpi">
<div><div class="k">Bình luận phân tích</div><div class="v">{R['n_analyzed']:,}</div>
 <div class="c">đã loại {R['n_noise']} nhiễu</div></div>
<div><div class="k">Tuổi tự khai (trung vị)</div><div class="v ac">{ad['median']:.0f}</div>
 <div class="c">n={ad['n']} người tự nói</div></div>
<div><div class="k">Nghe khi cầu nguyện</div><div class="v">13,5<span style="font-size:10pt">%</span></div>
 <div class="c">bối cảnh phổ biến nhất</div></div>
<div><div class="k">&ldquo;Finally&rdquo; được thích</div><div class="v up">6,6<span style="font-size:10pt">×</span></div>
 <div class="c">so với bình luận trung bình</div></div>
</div>

<h3>Ba phát hiện chính</h3>
<ul>
<li><b>Khán giả lớn tuổi rõ rệt.</b> Trong 82 người tự khai tuổi, trung vị là <b>70 tuổi</b>;
78% thuộc nhóm 60 tuổi trở lên.</li>
<li><b>Nỗi đau trung tâm đã được xác nhận thống kê.</b> Bình luận chứa &ldquo;finally&rdquo;
hoặc &ldquo;never heard&rdquo; nhận lượt thích cao gấp <b>6,2&ndash;6,6 lần</b> mức trung bình
(p &lt; 0,0001).</li>
<li><b>Đây là nhạc chức năng, không phải nhạc giải trí.</b> Bối cảnh nghe hàng đầu là
<b>cầu nguyện và tĩnh tâm</b> (13,5%), không phải nghe thư giãn.</li>
</ul>

<h2>2. Phương pháp và giới hạn</h2>

<h3>2.1. Cách lọc dữ liệu</h3>
<div class="formula" style="background:#F7F4F0;border:.6pt solid #E2DAD1;padding:7pt 10pt;font-size:8.5pt;">
145.150 bình luận gốc &rarr; lọc 3 tầng &rarr; 6.794 &rarr; loại {R['n_noise']} nhiễu
&rarr; <b>{R['n_analyzed']:,} bình luận phân tích</b>
</div>
<p>Nhiễu bị loại gồm: lời cầu nguyện dài chép nguyên văn, bản chép lời bài hát, và spam kinh
&mdash; những nội dung không nói gì về người viết.</p>

<div class="box crit">
<span class="l">Ranh giới đạo đức &mdash; áp dụng nghiêm ngặt</span>
<p><b>Chỉ ghi nhận thuộc tính khi người dùng TỰ KHAI công khai.</b> Không suy đoán tuổi, giới
tính, sắc tộc hay tôn giáo từ tên hoặc cách viết.</p>
<p>Mã <code>author_hash</code> đã được băm SHA-256 có muối &mdash; không truy ngược được
danh tính. Trích dẫn dùng để hiểu nhu cầu thị trường, không nhắm vào cá nhân nào.</p>
</div>

<div class="box crit">
<span class="l">Giới hạn quan trọng: mẫu tuổi rất nhỏ</span>
<p>Chỉ <b>{ad['n']} trên {R['n_analyzed']:,} bình luận</b> ({ad['n']/R['n_analyzed']*100:.2f}%)
có người tự khai tuổi. Đây là mẫu rất nhỏ, và <b>có thiên lệch</b>: người khai tuổi thường
viết bình luận dài, xúc động &mdash; nhóm này nhận lượt thích trung vị 12 so với 4 của toàn bộ.</p>
<p>Vì vậy con số &ldquo;trung vị 70 tuổi&rdquo; <b>không nên hiểu là tuổi trung bình của toàn
bộ khán giả</b>. Nó chỉ cho biết: trong nhóm khán giả gắn bó đủ để kể chuyện đời mình,
người lớn tuổi chiếm đa số áp đảo.</p>
</div>

<h2 class="pb">3. Nhân khẩu học tự khai</h2>

<img src="{img('c1_age.png')}" class="half">
<table>
<thead><tr><th>Nhóm tuổi</th><th>Số người</th><th>Tỷ lệ</th></tr></thead>
<tbody>{age_rows}</tbody></table>
<p><b>64 trên 82 người (78%) từ 60 tuổi trở lên.</b> Người trẻ nhất 20 tuổi, lớn nhất
{ad['max']} tuổi.</p>

<h3>3.1. Hoàn cảnh sống tự khai</h3>
<table>
<thead><tr><th>Hoàn cảnh</th><th>Số người</th><th>Tỷ lệ</th></tr></thead>
<tbody>{attr_rows}</tbody></table>
<p>Các con số này <b>thấp một cách hệ thống</b> &mdash; hầu hết người xem không kể về bản thân.
Nhưng chúng cho biết <i>loại</i> người nào gắn bó đủ để chia sẻ: đang phục hồi sau nghiện
(31 người), mới cải đạo (17), góa bụa (5).</p>

<h3>3.2. Trích dẫn minh chứng</h3>
{quotes(d.age.notna(),4)}

<h2>4. Nỗi đau và động cơ nghe</h2>

<img src="{img('c2_signals.png')}">
<p class="f">So sánh lượt thích trung vị của từng nhóm với mức trung bình
({R['baseline_likes']:.0f} lượt thích).</p>

<table>
<thead><tr><th>Tín hiệu</th><th>Số bình luận</th><th>Lượt thích<br>trung vị</th>
<th>So với<br>trung bình</th><th>p-value</th><th>Kết luận</th></tr></thead>
<tbody>{sig_rows}</tbody></table>

<div class="box ok">
<span class="l">Xác nhận nỗi đau trung tâm của ngách</span>
<p>Bình luận chứa &ldquo;finally / at last / been looking for&rdquo; nhận lượt thích trung vị
<b>26,5</b> &mdash; gấp <b>6,6 lần</b> mức trung bình, p &lt; 0,0001.</p>
<p>Bình luận chứa &ldquo;never heard&rdquo; đạt <b>25</b> lượt thích &mdash; gấp <b>6,2 lần</b>,
cũng p &lt; 0,0001.</p>
<p>Đây là bằng chứng thống kê rằng <b>tồn tại một nhu cầu chưa được đáp ứng trong thời gian
dài</b>, và khi được đáp ứng thì cộng đồng phản ứng rất mạnh.</p>
</div>

<h4>Lý do ngách này tồn tại &mdash; do chính khán giả viết ra</h4>
{quotes(d["finally"] | d.cant_stand, 4)}

<div class="box">
<span class="l">Điều đáng chú ý: &ldquo;healing&rdquo; KHÔNG phải tín hiệu phân biệt</span>
<p>Từ ngữ về chữa lành xuất hiện ở <b>757 bình luận (11,8%)</b> &mdash; nhiều nhất trong mọi
nhóm. Nhưng lượt thích trung vị chỉ <b>3</b>, tức <i>thấp hơn</i> mức trung bình 4.</p>
<p>Nghĩa là: nói về chữa lành là <b>ngôn ngữ chung của ngách</b>, ai cũng nói. Nó là điều kiện
cần, không phải điều tạo khác biệt. Giống phát hiện ở STEP_04 với từ khóa
&ldquo;prayer&rdquo;, &ldquo;god&rdquo;.</p>
</div>

<h2 class="pb">5. Bối cảnh nghe</h2>

<img src="{img('c3_context.png')}" class="half">
<table>
<thead><tr><th>Bối cảnh</th><th>Số bình luận</th><th>Tỷ lệ</th></tr></thead>
<tbody>{ctx_rows}</tbody></table>

<div class="box ok">
<span class="l">Đây là nhạc CHỨC NĂNG, không phải nhạc giải trí</span>
<p>Bối cảnh phổ biến nhất là <b>cầu nguyện và tĩnh tâm (868 bình luận, 13,5%)</b> &mdash;
gấp hơn 3 lần bối cảnh đứng thứ hai.</p>
<p>Đáng chú ý: <b>bệnh tật/bệnh viện (105)</b> và <b>tang chế (70)</b> đều cao hơn
<b>lái xe (35)</b> và <b>việc nhà (30)</b>.</p>
<p><b>Hàm ý sản xuất:</b> khán giả dùng nhạc này trong những <i>khoảnh khắc nặng nề của đời
sống</i>, không phải làm nền cho việc khác. Điều này ủng hộ định dạng dài, liền mạch,
không quảng cáo chen ngang &mdash; và giải thích vì sao mix 1&ndash;3 giờ vẫn hoạt động tốt
dù VPD thấp (câu hỏi treo từ STEP_04).</p>
</div>

{quotes(d.sick_hosp | d.grief, 3, 60)}

<h2>6. Đường đến video</h2>
<img src="{img('c4_discovery.png')}" class="half">
<table>
<thead><tr><th>Cách tiếp cận</th><th>Số bình luận</th><th>Tỷ lệ</th></tr></thead>
<tbody>{disc_rows}</tbody></table>

<div class="box">
<span class="l">Ngách sống bằng ĐỀ XUẤT, không phải tìm kiếm</span>
<p><b>83 bình luận</b> nhắc đến việc YouTube tự đề xuất, so với chỉ <b>12 bình luận</b> nói
họ chủ động tìm kiếm &mdash; tỷ lệ <b>gần 7 trên 1</b>.</p>
<p><b>Hàm ý chiến lược quan trọng:</b> tối ưu từ khóa tìm kiếm có giá trị thấp trong ngách này.
Thứ quyết định là <b>thuật toán đề xuất</b>, vốn phụ thuộc vào thời lượng xem và hành vi
người xem tương tự &mdash; không phụ thuộc từ khóa.</p>
<p>Điều này <b>củng cố kết luận STEP_04</b>: tối ưu metadata ít tác dụng. Và nó định hướng
lại STEP_06: nghiên cứu từ khóa nên nhằm vào <i>chọn đề tài</i>, không phải SEO.</p>
</div>

<p><b>114 bình luận (1,78%)</b> nói họ nghe lặp lại hằng ngày &mdash; nhóm lớn nhất trong mục
này. Đây là dấu hiệu tốt về khả năng giữ chân khán giả.</p>

<h2 class="pb">7. Ba chân dung khách hàng</h2>

<div class="persona">
<h4>Persona 1 &mdash; Tín đồ cao tuổi</h4>
<p class="tag">Ước tính n = {R['personas']['p_elder']['n']} bình luận
&nbsp;•&nbsp; lượt thích trung vị {R['personas']['p_elder']['med_likes']:.0f}
(gấp {R['personas']['p_elder']['med_likes']/R['baseline_likes']:.1f}× mức trung bình)</p>
<table>
<tbody>
<tr><td width="26%"><b>Nhân khẩu</b></td><td>60&ndash;85 tuổi, chủ yếu ở Mỹ, theo đạo lâu năm
(có người &ldquo;walking with the Lord over 50 years&rdquo;)</td></tr>
<tr><td><b>Động cơ nghe</b></td><td>Thờ phượng và tĩnh tâm; tìm hình thức mới cho đức tin cũ</td></tr>
<tr><td><b>Nỗi đau</b></td><td>Nhạc Christian trên radio &ldquo;không chạm được&rdquo;;
chưa từng nghe Lời Chúa trình bày theo cách này</td></tr>
<tr><td><b>Bối cảnh</b></td><td>Cầu nguyện buổi sáng, lúc bệnh tật, khi tưởng nhớ người đã mất</td></tr>
<tr><td><b>Giá trị thương mại</b></td><td><b>Cao</b> &mdash; nhóm tuổi này ở Mỹ có RPM tốt
(sức mua cao, ít dùng chặn quảng cáo)</td></tr>
</tbody></table>
{quotes(d.p_elder,2)}
</div>

<div class="persona">
<h4>Persona 2 &mdash; Người yêu blues có đức tin</h4>
<p class="tag">Ước tính n = {R['personas']['p_convert']['n']+R['personas']['p_music']['n']} bình luận
&nbsp;•&nbsp; nhóm nhạc công có lượt thích trung vị {R['personas']['p_music']['med_likes']:.0f}
&mdash; cao nhất trong mọi nhóm</p>
<table>
<tbody>
<tr><td width="26%"><b>Nhân khẩu</b></td><td>Nhạc công, người viết lời, hoặc người nghe blues
lâu năm; nhiều người mới cải đạo</td></tr>
<tr><td><b>Động cơ nghe</b></td><td>Yêu chất nhạc blues nhưng cần lời phù hợp đức tin</td></tr>
<tr><td><b>Nỗi đau</b></td><td><b>Đây là nỗi đau lõi của ngách:</b> yêu âm nhạc nhưng
&ldquo;can't stand the lyrics of the blues&rdquo; (rượu, tình dục, ngoại tình)</td></tr>
<tr><td><b>Bối cảnh</b></td><td>Nghe chủ động, đánh giá chất lượng chuyên môn</td></tr>
<tr><td><b>Giá trị chiến lược</b></td><td><b>Rất cao</b> &mdash; nhóm nhỏ nhưng bình luận của
họ được thích nhiều nhất, tạo hiệu ứng lan tỏa</td></tr>
</tbody></table>
{quotes(d.p_music | d.cant_stand,2)}
</div>

<div class="persona">
<h4>Persona 3 &mdash; Người tìm chữa lành</h4>
<p class="tag">Ước tính n = {R['personas']['p_healing']['n']} bình luận
({R['personas']['p_healing']['pct']:.1f}% &mdash; nhóm lớn nhất về số lượng)</p>
<table>
<tbody>
<tr><td width="26%"><b>Nhân khẩu</b></td><td>Đa dạng tuổi; đang trải qua bệnh tật, mất mát,
cai nghiện, hoặc giai đoạn khó khăn</td></tr>
<tr><td><b>Động cơ nghe</b></td><td>Dùng nhạc như công cụ vượt qua khó khăn &mdash;
&ldquo;Blues were never about bad times, they are about getting through tough times&rdquo;</td></tr>
<tr><td><b>Nỗi đau</b></td><td>Cần điều gì đó vừa thừa nhận nỗi đau vừa mang hy vọng</td></tr>
<tr><td><b>Bối cảnh</b></td><td>Bệnh viện, đêm khuya, sau tang lễ, trong quá trình phục hồi</td></tr>
<tr><td><b>Lưu ý</b></td><td>Đông nhất nhưng lượt thích thấp nhất
({R['personas']['p_healing']['med_likes']:.0f}) &mdash; họ ít tương tác với nhau,
đây là trải nghiệm riêng tư</td></tr>
</tbody></table>
{quotes(d.p_healing & (d.like_count>=100),2)}
</div>

<h2 class="pb">8. Ngôn ngữ khách hàng</h2>
<p>Đây là chính từ ngữ khán giả dùng &mdash; nguyên liệu để viết tiêu đề và mô tả ở STEP_06.
Con số là số lần xuất hiện trong {R['n_analyzed']:,} bình luận.</p>
<div style="margin:10pt 0;">{vocab_rows}</div>

<div class="box">
<span class="l">Cách dùng bảng từ vựng này</span>
<p>Dùng chính từ ngữ khán giả nói, không phải từ ngữ marketing. Nhưng nhớ bài học STEP_04:
những từ phổ biến nhất (&ldquo;god&rdquo;, &ldquo;lord&rdquo;, &ldquo;music&rdquo;) xuất hiện
ở <b>cả video thắng lẫn video thua</b> &mdash; chúng là điều kiện cần, không tạo khác biệt.</p>
</div>

<h2>9. Độ tin cậy và điều chưa biết</h2>
<table>
<thead><tr><th>Kết luận</th><th>Độ tin cậy</th><th>Lý do</th></tr></thead>
<tbody>
<tr><td>&ldquo;Finally&rdquo; và &ldquo;never heard&rdquo; được đồng tình mạnh</td>
 <td class="ok">Cao</td><td>n=58 và n=55, p&lt;0,0001, hiệu ứng 6×</td></tr>
<tr><td>Ngách sống bằng đề xuất, không phải tìm kiếm</td><td class="ok">Cao</td>
 <td>Tỷ lệ 7:1, nhất quán với kết luận STEP_04</td></tr>
<tr><td>Bối cảnh nghe là cầu nguyện/tĩnh tâm</td><td>Vừa&ndash;Cao</td>
 <td>n=868, nhưng dựa vào mẫu từ khóa nên có thể sót</td></tr>
<tr><td>Khán giả chủ yếu 60+</td><td class="wa">Vừa</td>
 <td>Chỉ {ad['n']} người tự khai ({ad['n']/R['n_analyzed']*100:.2f}%), có thiên lệch</td></tr>
<tr><td>Quy mô từng persona</td><td class="no">Thấp</td>
 <td>Dựa vào mẫu từ khóa, chỉ là ước tính tương đối</td></tr>
</tbody></table>

<h3>Bằng chứng phản bác</h3>
<ul>
<li><b>Người bình luận không đại diện cho người xem.</b> Chỉ một phần rất nhỏ khán giả để lại
bình luận, và họ thường là nhóm gắn bó nhất. Người xem thụ động có thể có chân dung khác hẳn.</li>
<li><b>Thiên lệch tuổi rõ rệt.</b> Người lớn tuổi có xu hướng viết bình luận dài và tự giới
thiệu; người trẻ ít làm vậy. Con số 70 tuổi gần như chắc chắn <b>cao hơn</b> tuổi trung bình thật.</li>
<li><b>Phát hiện dựa trên mẫu từ khóa</b> (regex), nên sót các cách diễn đạt khác. Ví dụ
&ldquo;lái xe&rdquo; chỉ bắt được 35 trường hợp &mdash; con số thật chắc chắn cao hơn.</li>
<li><b>Bình luận thiên về cảm xúc tích cực.</b> Người không thích thường bỏ đi, không bình luận
&mdash; nên dữ liệu này không cho biết vì sao người ta <i>không</i> xem.</li>
</ul>

<h2>10. Hàm ý cho các bước sau</h2>
<table>
<thead><tr><th>Phát hiện</th><th>Hàm ý</th><th>Dùng ở bước</th></tr></thead>
<tbody>
<tr><td>Khán giả 60+ ở Mỹ</td><td>RPM có thể cao hơn mức trung bình ngành nhạc</td>
 <td class="n">STEP_07</td></tr>
<tr><td>Nghe khi cầu nguyện, bệnh tật</td><td>Ủng hộ định dạng dài liền mạch &mdash;
giải thích vì sao mix 1&ndash;3h vẫn hiệu quả</td><td class="n">STEP_08</td></tr>
<tr><td>Đề xuất thắng tìm kiếm 7:1</td><td>Nghiên cứu từ khóa nhằm chọn đề tài,
không phải SEO</td><td class="n">STEP_06</td></tr>
<tr><td>Nỗi đau &ldquo;yêu nhạc, ghét lời&rdquo;</td><td>Đây là định vị cốt lõi cần
truyền tải trong mô tả kênh</td><td class="n">STEP_08</td></tr>
<tr><td>Nhóm nhạc công được thích nhiều nhất</td><td>Chất lượng chuyên môn của bản nhạc
là đòn bẩy lan tỏa</td><td class="n">STEP_08</td></tr>
</tbody></table>

<div class="box ok">
<span class="l">Ghi chú: bước này giải được câu hỏi treo từ STEP_04</span>
<p>STEP_04 không kết luận được về định dạng vì VPD (thiên vị video ngắn) mâu thuẫn với tỷ lệ
thắng. Dữ liệu bối cảnh nghe ở đây <b>giải thích được</b>: khán giả dùng nhạc này trong
cầu nguyện, bệnh tật, tang chế &mdash; những tình huống cần âm thanh <b>liền mạch, kéo dài,
không gián đoạn</b>.</p>
<p>Điều đó ủng hộ mix dài, và giải thích vì sao 43% thị trường chọn định dạng 1&ndash;3 giờ
dù VPD thấp hơn &mdash; <b>họ không làm sai, họ đang phục vụ đúng bối cảnh sử dụng.</b></p>
</div>

</body></html>"""

out=N/"99_report/STEP05_Chan-dung-Khach-hang.pdf"
HTML(string=DOC,base_url=".").write_pdf(out)
print(f"PDF: {out} ({out.stat().st_size/1024:.0f} KB)")
