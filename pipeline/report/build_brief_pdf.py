"""Sinh PDF cho THUMBNAIL_BRIEF — kèm ảnh minh họa thật từ nhóm top."""
import json, pandas as pd, numpy as np, base64, io, warnings
from pathlib import Path
from PIL import Image
from weasyprint import HTML
warnings.filterwarnings("ignore")

N = Path("niches/christian-blues"); D = N/"04_outlier"; P = N/"00_input/processed"
T = N/"00_input/raw/thumbs"
B = json.load(open(D/"_brief_data.json"))
F = pd.read_parquet(D/"_brief_features.parquet")
v = pd.read_parquet(P/"videos_enriched.parquet")

def vn(x): return f"{x:,.0f}".replace(",", ".")

def sheet(vids, cols=3, w=420):
    """Ghép ảnh thành lưới → data URI."""
    h = int(w*9/16); rows = (len(vids)+cols-1)//cols
    C = Image.new("RGB", (w*cols, h*rows), "white")
    for i, vid in enumerate(vids):
        f = T/f"{vid}.jpg"
        if f.exists():
            C.paste(Image.open(f).resize((w, h)), (w*(i % cols), h*(i//cols)))
    buf = io.BytesIO(); C.save(buf, "JPEG", quality=82)
    return "data:image/jpeg;base64,"+base64.b64encode(buf.getvalue()).decode()

m = v[(v.duration_sec > 60) & v.is_matured]
top = m[m.view_count >= m.view_count.quantile(.95)]

def ch_sheet(handle, n=3):
    return sheet(list(m[m.handle == handle].nlargest(n, "view_count").video_id), cols=3)

hero = sheet(list(top.nlargest(6, "view_count").video_id), cols=3)
tpl1 = ch_sheet("stillworshipmusic"); tpl2 = ch_sheet("oldiesgospelradio")
tpl3 = ch_sheet("holygrooveofficial")
lo = m[m.handle.isin(set(top.handle)) & (m.view_count < m.view_count.quantile(.30))]
bad = sheet(list(lo.nsmallest(3, "view_count").video_id), cols=3)

pal = "".join(
    f'<div class="sw"><div class="ch" style="background:{p["hex"]}"></div>'
    f'<code>{p["hex"]}</code><span>{p["share"]*100:.1f}%</span></div>'
    for p in B["palette_top"][:7])

words = B["words_top"][:14]
wrows = "".join(
    f'<tr><td>{words[i]["w"]}</td><td class="n">{words[i]["n"]}</td>'
    f'<td>{words[i+7]["w"] if i+7 < len(words) else ""}</td>'
    f'<td class="n">{words[i+7]["n"] if i+7 < len(words) else ""}</td></tr>'
    for i in range(min(7, len(words))))

p_, t_, c_, l_, d_, f_ = (B["person"], B["text"], B["color"], B["layout"],
                          B["depth"], B["face"])

DOC = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size:A4;margin:16mm 14mm 18mm;
 @bottom-center {{ content counter(page) " / " counter(pages);
  font-family:"DejaVu Sans";font-size:8pt;color:#9A8E85; }} }}
body {{ font-family:"DejaVu Sans",sans-serif;font-size:9.5pt;line-height:1.55;color:#1A1614; }}
h1 {{ font-size:24pt;margin:0 0 5pt;letter-spacing:-.5pt; }}
h2 {{ font-size:13pt;margin:19pt 0 7pt;padding-bottom:4pt;
 border-bottom:1.5pt solid #1A1614;page-break-after:avoid; }}
h3 {{ font-size:10.5pt;margin:13pt 0 5pt;color:#8C3A2B;page-break-after:avoid; }}
p {{ margin:6pt 0; }}
.sub {{ color:#6B615A;font-size:10pt;margin:0 0 9pt; }}
.meta {{ font-size:8pt;color:#7A6F68;border-top:.6pt solid #E2DAD1;
 border-bottom:.6pt solid #E2DAD1;padding:6pt 0;margin-bottom:13pt; }}
table {{ border-collapse:collapse;width:100%;font-size:8.5pt;margin:8pt 0;page-break-inside:avoid; }}
th {{ background:#F2EEE8;text-align:left;padding:5pt 7pt;font-size:7.5pt;
 text-transform:uppercase;letter-spacing:.4pt;color:#5A514B;border-bottom:1pt solid #CFC4B8; }}
td {{ padding:5pt 7pt;border-bottom:.6pt solid #EDE7E0;vertical-align:top; }}
td.n {{ text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap; }}
tr.hi {{ background:#F4E6E2; }}
.ok {{ color:#2F6B4F;font-weight:bold; }} .no {{ color:#9B2C2C;font-weight:bold; }}
.box {{ border-left:2.5pt solid #8C3A2B;background:#F9F4F2;padding:8pt 11pt;
 margin:10pt 0;page-break-inside:avoid; }}
.box.crit {{ border-left-color:#9B2C2C;background:#FBEEEE; }}
.box.ok {{ border-left-color:#2F6B4F;background:#EFF5F1; }}
.box .l {{ font-size:7.5pt;text-transform:uppercase;letter-spacing:.7pt;
 font-weight:bold;color:#8C3A2B;display:block;margin-bottom:4pt; }}
.box.crit .l {{ color:#9B2C2C; }} .box.ok .l {{ color:#2F6B4F; }}
.box p {{ margin:0 0 5pt;font-size:9pt; }} .box p:last-child {{ margin-bottom:0; }}
.kpi {{ display:flex;gap:7pt;margin:10pt 0; }}
.kpi div {{ flex:1;border:.6pt solid #E2DAD1;padding:8pt 9pt; }}
.kpi .k {{ font-size:6.8pt;text-transform:uppercase;letter-spacing:.5pt;color:#7A6F68;margin-bottom:3pt; }}
.kpi .v {{ font-size:17pt;font-weight:bold;letter-spacing:-.3pt; }}
.kpi .c {{ font-size:7pt;color:#7A6F68;margin-top:3pt;line-height:1.3; }}
.ac {{ color:#8C3A2B; }} .dn {{ color:#9B2C2C; }}
img {{ width:100%;margin:6pt 0; }}
.f {{ font-size:7.5pt;color:#7A6F68;text-align:center;margin:-3pt 0 11pt; }}
code {{ background:#F2EEE8;padding:.5pt 3pt;font-size:8.5pt; }}
pre {{ background:#1A1614;color:#E8DFD5;padding:9pt 11pt;font-size:7.6pt;
 line-height:1.5;white-space:pre-wrap;margin:7pt 0;page-break-inside:avoid; }}
.diag {{ background:#F7F4F0;border:.6pt solid #E2DAD1;padding:8pt 11pt;
 font-size:8pt;margin:7pt 0;line-height:1.5;white-space:pre; }}
.pb {{ page-break-before:always; }}
h3.pb {{ margin-top:0; }}
.pal {{ display:flex;gap:5pt;margin:8pt 0;flex-wrap:wrap; }}
.sw {{ text-align:center;font-size:6.5pt;width:13%; }}
.sw .ch {{ height:30pt;border:.6pt solid #CFC4B8;margin-bottom:2pt; }}
.sw code {{ display:block;font-size:6.5pt;background:none;padding:0; }}
.sw span {{ color:#7A6F68; }}
ul {{ margin:5pt 0;padding-left:15pt; }} li {{ margin:2.5pt 0; }}
.ck {{ font-size:8.5pt;line-height:1.9; }}
</style></head><body>

<h1>Brief Tái tạo Thumbnail</h1>
<p class="sub">Christian Blues &middot; công thức dựng ảnh cho sản xuất hàng loạt</p>
<div class="meta">
Nguồn: <b>{B['n']} thumbnail</b> của video top 5% lượt xem (&ge;{vn(B['view_threshold'])} view,
trung vị <b>{vn(B['view_median'])}</b>) &middot; {B['n_channels']} kênh &middot;
chỉ video dài &gt;60s, đủ 60 ngày tuổi &middot; 17/08/2026
</div>

<img src="{hero}">
<p class="f">6 thumbnail thành công nhất ngách (770 nghìn &ndash; 3,65 triệu view)</p>

<div class="box crit">
<span class="l">Brief này là gì &mdash; và không phải gì</span>
<p><b>LÀ:</b> mô tả chính xác nhóm dẫn đầu <b>đang làm thế nào</b> &mdash; công thức sao chép được.</p>
<p><b>KHÔNG phải:</b> bằng chứng "làm thế này sẽ thắng". Kiểm định riêng cho thấy không đặc trưng
hình ảnh nào phân biệt được thắng/thua trong ngách này.</p>
<p>Coi đây là <b>vé vào cửa</b> giúp sản xuất nhanh và không lạc lõng. Thắng hay không
phụ thuộc <b>âm nhạc</b> và <b>nhịp đăng</b>.</p>
</div>

<h2>1. Tỷ lệ chiếm chỗ</h2>
<div class="kpi">
<div><div class="k">Người chiếm</div><div class="v ac">{p_['area_med']*100:.0f}%</div>
 <div class="c">&asymp;1/4 khung &middot; khoảng {p_['area_p25']*100:.0f}&ndash;{p_['area_p75']*100:.0f}%</div></div>
<div><div class="k">Chữ chiếm</div><div class="v ac">{t_['area_med']*100:.0f}%</div>
 <div class="c">&asymp;1/6 khung &middot; khoảng {t_['area_p25']*100:.0f}&ndash;{t_['area_p75']*100:.0f}%</div></div>
<div><div class="k">Một nhân vật</div><div class="v">{p_['one_person']*100:.0f}%</div>
 <div class="c">không dùng nhóm đông</div></div>
<div><div class="k">Vùng tối</div><div class="v">{c_['dark_med']*100:.0f}%</div>
 <div class="c">ảnh tối là chuẩn, không phải ngoại lệ</div></div>
</div>
<table>
<thead><tr><th>Thành phần</th><th>Chiếm khung</th><th>Khoảng</th><th>Ghi chú</th></tr></thead>
<tbody>
<tr class="hi"><td><b>NGƯỜI</b> (cả thân, tóc, mũ)</td><td class="n"><b>{p_['area_med']*100:.1f}%</b></td>
 <td class="n">{p_['area_p25']*100:.1f}&ndash;{p_['area_p75']*100:.1f}%</td>
 <td>{p_['pct_has']*100:.1f}% ảnh có người</td></tr>
<tr><td>Khuôn mặt riêng</td><td class="n">{f_['area_med']*100:.1f}%</td><td class="n">&mdash;</td>
 <td>{f_['pct_has']*100:.1f}% có mặt &middot; {f_['one_face']*100:.0f}% đúng một mặt</td></tr>
<tr class="hi"><td><b>CHỮ</b> (tổng các dòng)</td><td class="n"><b>{t_['area_med']*100:.1f}%</b></td>
 <td class="n">{t_['area_p25']*100:.1f}&ndash;{t_['area_p75']*100:.1f}%</td>
 <td>{t_['pct_has']*100:.1f}% ảnh có chữ</td></tr>
<tr><td>Dòng chữ lớn nhất</td><td class="n">cao {t_['big_line_med']*100:.1f}%</td><td class="n">&mdash;</td>
 <td>&asymp;{t_['big_line_med']*720:.0f}px trên ảnh 720p</td></tr>
</tbody></table>

<h2>2. Bố cục</h2>
<div class="diag">┌─────────────────────────────────────┐
│                                     │
│   ┌──────────┐      ┌───────────┐   │   chữ giữa khung {l_['text_middle']*100:.0f}%
│   │  NGƯỜI   │      │   CHỮ     │   │   hoặc hơi cao {l_['text_top']*100:.0f}%
│   │   ~1/4   │      │  3 dòng   │   │
│   └──────────┘      └───────────┘   │   mặt ở {f_['cy_med']*100:.0f}% chiều cao
│                                     │   (nửa trên khung)
└─────────────────────────────────────┘</div>
<table>
<thead><tr><th>Kiểu bố cục</th><th>Tỷ lệ</th><th>Vị trí chữ (dọc)</th><th>Tỷ lệ</th></tr></thead>
<tbody>
<tr><td>Người <b>trái</b> &ndash; chữ <b>phải</b></td><td class="n">{l_['person_left_text_right']*100:.1f}%</td>
 <td>Giữa khung</td><td class="n">{l_['text_middle']*100:.1f}%</td></tr>
<tr><td>Người <b>phải</b> &ndash; chữ <b>trái</b></td><td class="n">{l_['person_right_text_left']*100:.1f}%</td>
 <td>Phần trên</td><td class="n">{l_['text_top']*100:.1f}%</td></tr>
<tr><td>Khác (chồng lấn, giữa)</td>
 <td class="n">{(1-l_['person_left_text_right']-l_['person_right_text_left'])*100:.1f}%</td>
 <td>Phần dưới</td><td class="n">{l_['text_bottom']*100:.1f}%</td></tr>
</tbody></table>
<p><b>Ba phần tư số ảnh tách đôi trái/phải.</b> Số dòng chữ: <b>{t_['lines_med']:.0f}</b> &mdash;
thường là tiêu đề lớn, phụ đề nhỏ, tên kênh.</p>

<h2 class="pb">3. Bảng màu</h2>
<div class="pal">{pal}</div>
<table>
<thead><tr><th>Chỉ số</th><th>Giá trị</th><th>Nghĩa</th></tr></thead>
<tbody>
<tr class="hi"><td>Vùng tối (V&lt;70)</td><td class="n"><b>{c_['dark_med']*100:.1f}%</b></td>
 <td>Ảnh tối là <b>chuẩn</b></td></tr>
<tr><td>Vùng sáng (&gt;190)</td><td class="n">{c_['bright_share']*100:.1f}%</td>
 <td>Điểm sáng nhỏ &mdash; đèn, viền tóc</td></tr>
<tr class="hi"><td>Sắc hổ phách/vàng</td><td class="n"><b>{c_['amber_med']*100:.1f}%</b></td>
 <td>Nguồn sáng ấm</td></tr>
<tr class="hi"><td>Sắc xanh lạnh</td><td class="n"><b>{c_['blue_med']*100:.1f}%</b></td>
 <td><span class="no">Gần như không dùng &mdash; tránh</span></td></tr>
<tr><td>Đen trắng hoàn toàn</td><td class="n">{c_['mono_pct']*100:.1f}%</td>
 <td>Một nhánh phong cách riêng</td></tr>
<tr><td>Độ ấm (R&minus;B)</td><td class="n">+{c_['warm_med']:.1f}</td><td>Ngả ấm rõ rệt</td></tr>
<tr><td>Nền mờ mạnh (bokeh)</td><td class="n">{d_['bokeh_pct_strong']*100:.1f}%</td>
 <td>Nét giữa gấp {d_['bokeh_med']:.1f}&times; nét biên</td></tr>
</tbody></table>
<div class="box">
<span class="l">Quy tắc màu</span>
<p>Nền đen &middot; nguồn sáng ấm hổ phách chiếu xiên một bên &middot;
<b>tránh xanh lam/xanh lá</b> &middot; cứ 6 ảnh làm 1 ảnh đen trắng để đỡ nhàm.</p>
</div>

<h2>4. Nhân vật</h2>
<p style="font-size:8.5pt;color:#6B615A">Mô tả <b>nhân vật hư cấu trong ảnh AI</b>,
dùng làm đầu vào prompt &mdash; không suy diễn về khán giả thật.</p>
<h3>Nhánh A &mdash; "Ông già blues" (&asymp;55%)</h3>
<pre>Nam, da đen, tuổi biểu kiến 60–80
Râu trắng/muối tiêu rậm · mũ phớt (fedora)
Trang phục: vest cũ, áo khoác da, sơ mi, dây đeo quần
Tư thế: hát vào micro cổ, mắt nhắm, biểu cảm mãnh liệt
        hoặc ôm guitar thùng, cúi đầu
Bối cảnh: quán blues tối, nhà thờ gỗ, hiên nhà miền Nam</pre>
<h3>Nhánh B &mdash; "Người trẻ đeo tai nghe" (&asymp;30%)</h3>
<pre>Nam hoặc nữ, da đen, tuổi biểu kiến 25–40
Tai nghe chụp tai lớn (rất đặc trưng) · râu quai nón gọn
Trang phục: áo khoác hiện đại, áo len cổ lọ
Tư thế: mắt nhắm, đầu hơi ngửa, thư giãn
Bối cảnh: phông studio xám trơn, ánh sáng viền</pre>
<h3>Nhánh C &mdash; "Nhạc công da trắng ngoài trời" (&asymp;15%)</h3>
<pre>Nam, da trắng, 40–70 · râu bạc · mũ cao bồi
Guitar thùng · đồng cỏ, nhà gỗ, hồ nước, trời u ám</pre>
<p><b>Đạo cụ lặp lại:</b> micro cổ điển kiểu Shure 55 (phổ biến nhất) &middot;
guitar thùng &middot; tai nghe chụp tai &middot; mũ fedora &middot; thánh giá trong nền.</p>

<h2 class="pb">5. Chữ trên ảnh</h2>
<table>
<thead><tr><th>Từ</th><th>Lần</th><th>Từ</th><th>Lần</th></tr></thead>
<tbody>{wrows}</tbody></table>
<div class="diag">DÒNG 1  (lớn nhất, cao ~{t_['big_line_med']*100:.0f}% khung)
        ├─ Kiểu A: tên thể loại    → "SOULFUL CHRISTIAN BLUES"
        ├─ Kiểu B: câu cảm xúc     → "SOMEBODY BEEN PRAYING FOR ME"
        └─ Kiểu C: sách Kinh Thánh → "PSALM 91" · "ECCLESIASTES IN BLUES"

DÒNG 2  (nhỏ hơn) → "PLAYLIST" · "Music Gospel" · "100 Minutes of..."

DÒNG 3  (nhỏ nhất) → tên kênh, chữ nghiêng, góc dưới</div>
<p><b>IN HOA TOÀN PHẦN: {t_['all_caps']*100:.1f}%</b> &mdash; gần một nửa. Nửa còn lại trộn
hoa/thường hoặc dùng chữ viết tay cho dòng phụ.</p>
<table>
<thead><tr><th>Kiểu chữ</th><th>Dùng cho</th></tr></thead>
<tbody>
<tr><td>Sans-serif đậm, viền đen</td><td>tiêu đề chính trên nền phức tạp</td></tr>
<tr><td>Serif cổ điển</td><td>tiêu đề trang trọng ("BE STILL")</td></tr>
<tr><td>Script/viết tay</td><td>tên kênh, dòng phụ ("Music", "Gospel")</td></tr>
<tr><td>Chữ khối kim loại vàng/bạc</td><td>kênh phong cách retro</td></tr>
</tbody></table>
<p><b>Màu chữ:</b> trắng (chủ đạo) &middot; vàng hổ phách <code>#E8B84B</code> &middot;
vàng gradient &middot; đỏ (nhấn).</p>

<h2>6. Prompt mẫu</h2>
<h3>Nhánh A &mdash; Ông già blues</h3>
<pre>elderly Black gospel blues singer, 70 years old, thick white beard,
wearing worn fedora hat and vintage leather jacket,
singing passionately into a chrome 1950s vintage microphone,
eyes closed, deeply emotional expression, head tilted slightly up,
dim smoky blues club interior, warm amber rim lighting from one side,
deep black background, shallow depth of field, bokeh,
cinematic chiaroscuro lighting, photorealistic, 8k, 16:9</pre>
<h3>Nhánh B &mdash; Người trẻ tai nghe</h3>
<pre>young Black man, 30s, short beard, wearing large over-ear headphones,
eyes closed, head tilted back, serene peaceful expression,
plain dark grey studio backdrop, soft rim light on face edge,
minimal composition, subject on right third of frame,
photorealistic portrait, 8k, 16:9</pre>
<h3>Tham số hậu kỳ (cả 3 nhánh)</h3>
<pre>- Đặt nhân vật vào 1/3 trái HOẶC 1/3 phải (không giữa)
- Nhân vật chiếm {p_['area_p25']*100:.0f}–{p_['area_p75']*100:.0f}% diện tích khung
- Chừa 1/3 đối diện cho chữ
- Làm tối nền: đưa ~{c_['dark_med']*100:.0f}% khung xuống dưới V=70
- Ngả ấm: tăng kênh đỏ so với xanh khoảng +{c_['warm_med']:.0f}
- Chèn {t_['lines_med']:.0f} dòng chữ, tổng {t_['area_p25']*100:.0f}–{t_['area_p75']*100:.0f}% khung
- Dòng lớn nhất cao ~{t_['big_line_med']*100:.0f}% khung</pre>

<h2 class="pb">7. Ba mẫu có sẵn từ kênh dẫn đầu</h2>
<h3>Mẫu 1 &mdash; stillworshipmusic (đỉnh 3,65 triệu view)</h3>
<img src="{tpl1}">
<pre>Nhân vật cố định : nam da đen 40–50, râu muối tiêu gọn
Nền              : xám studio trơn, tối
Đạo cụ           : tai nghe chụp tai HOẶC tay đặt lên ngực
Ánh sáng         : viền sáng bên, nền chìm
Chữ              : sans đậm + vàng nhấn, đặt đối diện nhân vật
Nhận diện        : dòng "Still Worship" nhỏ ở dưới + dải sóng âm</pre>

<h3 class="pb">Mẫu 2 &mdash; oldiesgospelradio (đỉnh 1,10 triệu view)</h3>
<img src="{tpl2}">
<pre>Phong cách : ĐEN TRẮNG hoàn toàn, thẩm mỹ thập niên 1960
Nhân vật   : nam da đen mặc vest, cà vạt hẹp, tóc chải gọn
Đạo cụ     : micro cổ điển bắt buộc
Bối cảnh   : nhà thờ có cửa kính màu, sân khấu cũ
Chữ        : khối 3D kim loại (bạc/vàng), góc trên
Biến thể   : nhóm tam ca/tứ ca (nam giữa, nữ hai bên)</pre>

<h3 class="pb">Mẫu 3 &mdash; holygrooveofficial (đỉnh 1,70 triệu view)</h3>
<img src="{tpl3}">
<pre>Công thức tiêu đề : "[TÊN SÁCH KINH THÁNH] IN BLUES"
                    PSALM · ISAIAH · ECCLESIASTES · IF DAVID SANG THE BLUES
Nhân vật          : nhạc công ôm guitar, đa dạng sắc tộc/tuổi
Bối cảnh          : NGOÀI TRỜI — nhà thờ gỗ, đồng cỏ, vườn ô-liu, mưa
Chữ               : trắng viền đen, IN HOA, chiếm nguyên dải trên
Nhận diện         : GẠCH CHÂN ĐỎ dưới một phần tiêu đề</pre>

<h2 class="pb">8. Tránh làm gì</h2>
<img src="{bad}">
<p class="f">Ba ảnh thất bại nhất &mdash; cùng kênh với nhóm top, chỉ 23&ndash;30 lượt xem</p>
<table>
<thead><tr><th>Tránh</th><th>Vì sao</th></tr></thead>
<tbody>
<tr><td><b>Toàn cảnh sân khấu từ xa</b></td>
 <td>Nhóm thua có 3,5 người/ảnh, mặt chiếm 0,1% &mdash; không nhìn rõ ai</td></tr>
<tr><td><b>Ánh sáng xanh lạnh</b></td>
 <td>Nhóm thua 10,3% xanh lạnh &middot; nhóm top chỉ 0,7%</td></tr>
<tr><td><b>Nhiều nhân vật nhỏ</b></td><td>Nhóm top {p_['one_person']*100:.0f}% chỉ một người</td></tr>
<tr><td><b>Không thấy khuôn mặt</b></td><td>Nhóm top {f_['pct_has']*100:.0f}% có mặt rõ</td></tr>
<tr><td><b>Nền sáng đều, không tương phản</b></td>
 <td>Chuẩn ngách là {c_['dark_med']*100:.0f}% khung tối</td></tr>
</tbody></table>
<div class="box crit">
<span class="l">Giới hạn của mục này</span>
<p>Quan sát trên mẫu nhỏ (n=60 mỗi nhóm). Ở n=150 khác biệt <b>không còn ý nghĩa thống kê</b>.
Dùng làm hướng dẫn thiết kế, <b>không</b> làm lời hứa kết quả.</p>
</div>

<h2>9. Checklist sản xuất</h2>
<div class="box ok"><div class="ck">
☐ 1280&times;720<br>
☐ Một nhân vật, chiếm {p_['area_p25']*100:.0f}&ndash;{p_['area_p75']*100:.0f}% khung<br>
☐ Đặt lệch 1/3 trái hoặc phải<br>
☐ Khuôn mặt nhìn rõ, nằm nửa trên (&asymp;{f_['cy_med']*100:.0f}% chiều cao)<br>
☐ Nền tối: &asymp;{c_['dark_med']*100:.0f}% khung dưới ngưỡng V=70<br>
☐ Nguồn sáng ấm hổ phách, chiếu xiên một bên<br>
☐ Nền mờ &mdash; nét giữa gấp &asymp;{d_['bokeh_med']:.1f}&times; nét biên<br>
☐ <b>TUYỆT ĐỐI tránh tông xanh lạnh</b><br>
☐ {t_['lines_med']:.0f} dòng chữ, tổng {t_['area_p25']*100:.0f}&ndash;{t_['area_p75']*100:.0f}% khung<br>
☐ Dòng lớn nhất cao &asymp;{t_['big_line_med']*100:.0f}% khung ({t_['big_line_med']*720:.0f}px)<br>
☐ Chữ đặt đối diện nhân vật, giữa hoặc hơi cao<br>
☐ Màu chữ: trắng / vàng hổ phách / vàng gradient<br>
☐ Có dòng tên kênh nhỏ (nhận diện thương hiệu)<br>
☐ Cứ &asymp;6 ảnh làm 1 ảnh đen trắng
</div></div>

<h2>10. Cách đo từng con số</h2>
<table>
<thead><tr><th>Con số</th><th>Cách tính</th></tr></thead>
<tbody>
<tr><td>Diện tích người</td><td>YOLO11-seg phân vùng lớp <code>person</code>, tính % pixel</td></tr>
<tr><td>Diện tích chữ</td><td>EasyOCR khoanh vùng chữ, cộng diện tích, độ tin cậy &gt;0,3</td></tr>
<tr><td>Bảng màu</td><td>k-means k=5 mỗi ảnh, gộp về lưới 32, cộng tỷ lệ</td></tr>
<tr><td>Vùng tối</td><td>% pixel có V&lt;70 trong không gian màu HSV</td></tr>
<tr><td>Bokeh</td><td>phương sai Laplacian vùng giữa &divide; vùng biên</td></tr>
<tr><td>Bố cục</td><td>so trọng tâm người và trọng tâm chữ theo trục ngang</td></tr>
</tbody></table>
<div class="box">
<span class="l">Kiểm chứng phép đo</span>
<p>9 ảnh đối chiếu bằng mắt, lệch trung bình <b>5,0 điểm %</b>.</p>
<p>Bản đo trước đó (báo cáo STEP_04b) báo người <b>3,2%</b> (sai ~10 lần) và chữ <b>11,4%</b>
(sai ~2,5 lần) &mdash; do đo khuôn mặt thay vì cả người, và dùng MSER đoán chữ thay vì OCR đọc chữ.
Bạn phát hiện ra khi đối chiếu báo cáo với ảnh thật.</p>
</div>

</body></html>"""

out = N/"99_report/_phu-luc/STEP04g_Brief-Thumbnail.pdf"
out.parent.mkdir(parents=True, exist_ok=True)
HTML(string=DOC, base_url=".").write_pdf(out)
print(f"PDF: {out} ({out.stat().st_size/1024:.0f} KB)")
