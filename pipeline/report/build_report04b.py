"""Sinh báo cáo PDF STEP_04b — Phân tích thumbnail (ảnh thật)."""
import json, pandas as pd, numpy as np, warnings, base64
from pathlib import Path
from weasyprint import HTML
warnings.filterwarnings("ignore")

N = Path("niches/christian-blues"); D = N/"04_outlier"; P = N/"00_input/processed"
R = json.load(open(D/"_thumb_top_metrics.json"))
T = pd.read_csv(D/"10_thumb_top_tests.csv")
DUP = pd.read_csv(D/"11_cross_channel_dups.csv")
f = pd.read_parquet(P/"thumb_features_full.parquet")
v = pd.read_parquet(P/"videos_enriched.parquet")
m = v.merge(f, on="video_id"); m = m[m.is_matured & (m.view_count >= 500)].copy()
m["like_rate"] = m.like_count/m.view_count.clip(lower=1)

def vn(x): return f"{x:,}".replace(",", ".")

def dec(x, sign=False):
    """Số thập phân kiểu Việt: dấu phẩy ngăn phần lẻ, dấu chấm ngăn hàng nghìn."""
    s = f"{x:+,.3f}" if sign else f"{x:,.3f}"
    return s.replace(",", "\u0000").replace(".", ",").replace("\u0000", ".")

def img(n): return "data:image/png;base64,"+base64.b64encode((D/n).read_bytes()).decode()

def vb(x):
    if x == "XÁC NHẬN": return '<span class="ok">XÁC NHẬN</span>'
    if x == "YẾU": return '<span class="wa">YẾU</span>'
    if "KHÔNG ĐÁNG KỂ" in str(x): return '<span class="wa">KHÔNG ĐÁNG KỂ</span>'
    if "Simpson" in str(x): return '<span class="no">BÁC BỎ (Simpson)</span>'
    return '<span class="no">BÁC BỎ</span>'

def rows(metric):
    s = T[T.thước_đo == metric].sort_values("cliffs_delta", key=abs, ascending=False)
    return "\n".join(
        f'<tr class="{"hi" if r.lớp1 in ("XÁC NHẬN","YẾU") else ""}"><td>{r.đặc_trưng}</td>'
        f'<td class="n">{dec(r.top_median)}</td><td class="n">{dec(r.dưới_median)}</td>'
        f'<td class="n">{dec(r.cliffs_delta, sign=True)}</td>'
        f'<td class="n">{"&lt;0,001" if r.p < 0.001 else f"{r.p:.3f}".replace(".", ",")}</td>'
        f'<td>{vb(r.lớp1)}</td><td>{vb(r.kết_luận)}</td></tr>'
        for _, r in s.iterrows())

dup_rows = "\n".join(
    f'<tr><td><code>{r.ch1}</code></td><td><code>{r.ch2}</code></td>'
    f'<td class="n">{r.hamming}</td></tr>'
    for _, r in DUP.nsmallest(10, "hamming").iterrows())

n_face = (f.n_faces > 0).mean()*100
n_one = (f.n_faces == 1).mean()*100
n_txt = (f.n_text_blocks > 0).mean()*100
cl = R["channel_level"]
vc_like = R["var_by_channel_like_rate"]*100
vc_view = R["var_by_channel_view_count"]*100
n_dup_ch = len(set(DUP.ch1) | set(DUP.ch2))
# Số ĐO LẠI (YOLO-seg + OCR) — thay cho phép đo hình học sai của bản đầu
B2 = json.load(open(D/"_brief_data.json"))
bp, bt, bc = B2["person"], B2["text"], B2["color"]
n_dup_vid = len(set(DUP.v1) | set(DUP.v2))

DOC = f"""<!doctype html><html><head><meta charset="utf-8"><style>
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

<h1>Phân tích Thumbnail</h1>
<p class="sub">STEP_04b &middot; Ngách <b>Christian Blues</b> &middot; 7.193 ảnh thật</p>
<div class="meta">
Dữ liệu: toàn bộ 7.193 thumbnail (100% ngách) &middot; Phân tích: 4.139 video đủ tuổi &ge;500 view
&middot; Công cụ: YuNet CNN + MSER &middot; Ngày 17/08/2026
</div>

<div class="box crit">
<span class="l">Đọc phần này trước</span>
<p>Báo cáo này <b>không đưa ra công thức thumbnail</b> để làm theo. Nó chứng minh rằng
với ngách này, <b>đặc điểm hình ảnh của thumbnail không quyết định kết quả video</b> &mdash;
và giải thích vì sao những phân tích ban đầu tưởng như tìm ra công thức lại sai.</p>
<p>Trong quá trình làm, tôi đã <b>phát hiện và sửa một lỗi công cụ nghiêm trọng</b> của chính mình.
Mục 2 kể lại đầy đủ, vì nó là bài học quan trọng hơn cả kết quả.</p>
</div>

<div class="kpi">
<div><div class="k">Ảnh phân tích</div><div class="v">7.193</div>
 <div class="c">100% video trong ngách &mdash; không lấy mẫu</div></div>
<div><div class="k">Đặc trưng xác nhận</div><div class="v dn">0 / 12</div>
 <div class="c">sau khi kiểm đủ 3 lớp chống Simpson</div></div>
<div><div class="k">Kênh giải thích</div><div class="v ac">{vc_like:.0f}%</div>
 <div class="c">biến thiên tỷ lệ like &mdash; ảnh thì không</div></div>
<div><div class="k">Trùng lặp giữa kênh</div><div class="v dn">{len(DUP)}</div>
 <div class="c">cặp ảnh gần/giống hệt, {n_dup_ch} kênh</div></div>
</div>

<h2>1. Câu hỏi và cách trả lời</h2>
<p>Bạn nêu đúng vấn đề: thumbnail ảnh hưởng CTR, và trong dự án này ảnh còn là
<b>đại diện hình ảnh chính</b> của video bên cạnh âm nhạc. Nên câu hỏi là:</p>
<div class="formula">
<b>Video thành công có thumbnail khác video thất bại ở điểm nào?</b>
</div>
<p>Theo yêu cầu của bạn, tôi tập trung vào <b>nhóm dẫn đầu</b> thay vì quét đều. Nhưng
"dẫn đầu" có hai nghĩa khác nhau, và tôi tách riêng vì chúng đo hai thứ khác nhau:</p>
<table>
<thead><tr><th>Thước đo</th><th>Nghĩa là gì</th><th>Nhóm top 10%</th><th>Đối chứng</th></tr></thead>
<tbody>
<tr><td><b>Lượt xem</b></td><td>YouTube <b>đẩy</b> video đi bao xa</td>
 <td class="n">{R['n_top_view_count']} video</td><td class="n">nửa dưới ({vn(len(m[m.view_count<=m.view_count.median()]))})</td></tr>
<tr><td><b>Tỷ lệ like</b></td><td>Khán giả <b>ủng hộ</b> mạnh đến đâu</td>
 <td class="n">{R['n_top_like_rate']} video</td><td class="n">nửa dưới ({vn(len(m[m.like_rate<=m.like_rate.median()]))})</td></tr>
</tbody></table>
<p>Chỉ lấy video <b>đã đủ 60 ngày tuổi</b> (tránh bẫy độ chín &mdash; video mới chưa kịp
tích view) và <b>&ge;500 lượt xem</b> (dưới ngưỡng đó tỷ lệ like là nhiễu).
Còn lại <b>{vn(R['n_pool'])} video</b>.</p>

<h2>2. Lỗi công cụ tôi đã mắc và cách phát hiện</h2>
<div class="box crit">
<span class="l">Lần chạy đầu tiên cho kết quả sai hoàn toàn</span>
<p>Bản đầu dùng <b>Haar cascade</b> để dò khuôn mặt. Kết quả: chỉ <b>35,8%</b> ảnh có mặt người,
và không đặc trưng nào phân biệt được thắng/thua. Nghe hợp lý &mdash; nhưng sai.</p>
</div>
<p><b>Cách tôi phát hiện:</b> đối chiếu chéo với <code>skin_ratio</code> (tỷ lệ da, đo độc lập
từ lần crawl trước). Nếu bộ dò đúng, ảnh "có mặt" phải nhiều da hơn rõ rệt. Kết quả:
p = 0,34 &mdash; <b>không khác biệt</b>. Dấu hiệu công cụ hỏng.</p>
<p>Tôi <b>mở 12 ảnh ra xem tận mắt</b>. Cả 12 đều có mặt người rõ ràng, chiếm phần lớn khung hình.
Haar chỉ bắt được 6.</p>
<p><b>Nguyên nhân:</b> Haar cascade <code>frontalface</code> chỉ nhận mặt <b>nhìn thẳng, đủ sáng</b>.
Thumbnail ngách này chủ yếu là mặt <b>nghiêng, ngẩng lên, nhắm mắt, tương phản mạnh</b> &mdash;
đúng phong cách gospel. Bộ dò bỏ sót hơn một nửa.</p>
<p><b>Cách sửa:</b> thay bằng <b>YuNet</b> (mạng nơ-ron). Kiểm lại trên đúng 12 ảnh đã soi mắt:
YuNet đúng 11/12, Haar đúng 6/12.</p>
<img src="{img('c1_detector.png')}">
<p class="f">Hình 1 &mdash; Cùng 7.193 ảnh, hai bộ dò cho kết quả lệch 2,5 lần.</p>
<p>Lỗi thứ hai cùng lúc: bộ dò chữ (Canny + dilate) báo chữ chiếm <b>90,7% diện tích ảnh</b> &mdash;
vô lý. Nó gộp cả tóc, nhạc cụ, nếp áo thành "khối chữ". Thay bằng <b>MSER</b> &rarr;
kết quả <b>11,4%</b>, khớp với quan sát bằng mắt.</p>
<div class="box">
<span class="l">Vì sao kể lại chuyện này</span>
<p>Nếu tôi không đối chiếu chéo, báo cáo này đã kết luận "thumbnail không quan trọng"
dựa trên <b>dữ liệu sai</b> &mdash; và tình cờ vẫn ra đúng kết luận cuối cùng.
Đúng vì may, không phải vì đúng phương pháp.</p>
<p>Đã đưa vào <code>lessons_learned.md</code> (T12&ndash;T14) và thêm chốt chặn trong code:
mọi lỗi đọc ảnh giờ bị đếm và báo ra, không nuốt im lặng.</p>
</div>

<h2 class="pb">3. Kết quả: top theo LƯỢT XEM</h2>
<p>So 12 đặc trưng hình ảnh giữa top 10% và nửa dưới.</p>
<table>
<thead><tr><th>Đặc trưng</th><th>Top 10%</th><th>Nửa dưới</th><th>Cliff's &delta;</th><th>p</th>
<th>Lớp 1</th><th>Kết luận</th></tr></thead>
<tbody>{rows('LƯỢT XEM')}</tbody></table>
<div class="box ok">
<span class="l">Kết quả</span>
<p><b>Không đặc trưng nào</b> phân biệt được video nhiều view với video ít view.
Đặc trưng mạnh nhất (vị trí mặt theo chiều dọc) chỉ đạt &delta; = 0,198 &mdash;
dưới ngưỡng 0,30, và bị loại tiếp ở lớp 2&ndash;3.</p>
</div>

<h2>4. Kết quả: top theo TỶ LỆ LIKE</h2>
<p>Đây là nơi ban đầu tưởng như có phát hiện lớn.</p>
<table>
<thead><tr><th>Đặc trưng</th><th>Top 10%</th><th>Nửa dưới</th><th>Cliff's &delta;</th><th>p</th>
<th>Lớp 1</th><th>Kết luận</th></tr></thead>
<tbody>{rows('TỶ LỆ LIKE')}</tbody></table>
<p><b>Ở lớp 1, ba đặc trưng vượt ngưỡng XÁC NHẬN</b>, tất cả cùng một chiều: video được
ủng hộ cao có ảnh <b>đơn giản hơn</b> &mdash; ít chi tiết, ít chữ, ít khối chữ.
Nếu dừng ở đây, kết luận sẽ là <i>"làm thumbnail tối giản để được nhiều like"</i>.</p>
<div class="box crit">
<span class="l">Nhưng kết luận đó sai</span>
<p>Kiểm lớp 3 (so <b>trong cùng một kênh</b>): chênh lệch rơi từ 24% xuống còn
<b>2&ndash;5%</b>, và chỉ 24&ndash;30 trên 41&ndash;44 kênh cùng chiều.</p>
</div>
<img src="{img('c2_layers.png')}">
<p class="f">Hình 2 &mdash; Cột đỏ (lớp 1) vượt ngưỡng. Cột xám (lớp 3, cùng kênh) gần như bằng 0.</p>

<h2>5. Vậy cái gì thực sự quyết định?</h2>
<p>Nếu không phải thumbnail, thì là gì? Câu trả lời nằm ở <b>cấp kênh</b>.</p>
<div class="kpi">
<div><div class="k">Kênh giải thích</div><div class="v ac">{vc_like:.1f}%</div>
 <div class="c">biến thiên TỶ LỆ LIKE</div></div>
<div><div class="k">Kênh giải thích</div><div class="v">{vc_view:.1f}%</div>
 <div class="c">biến thiên LƯỢT XEM</div></div>
<div><div class="k">Tương quan cấp kênh</div><div class="v dn">&minus;0,55</div>
 <div class="c">chi tiết ảnh &harr; tỷ lệ like</div></div>
<div><div class="k">Chênh giữa các kênh</div><div class="v">3,5&times;</div>
 <div class="c">{cl['like_rate_max']*100:.2f}% so với {cl['like_rate_min']*100:.2f}%</div></div>
</div>
<img src="{img('c3_channel.png')}">
<p class="f">Hình 3 &mdash; Trái: mỗi chấm là một kênh (&ge;10 video), quan hệ rõ. Phải: ở cấp video, hai phân bố chồng lấn nhiều.</p>
<div class="formula">
<b>Cơ chế:</b> không phải &laquo;ảnh đơn giản &rarr; nhiều like&raquo;,<br>
mà là &laquo;<b>kênh làm tốt</b> &rarr; nhiều like&raquo; <b>và</b> &laquo;kênh làm tốt <b>tình cờ</b> cũng dùng ảnh đơn giản&raquo;.
</div>
<p>Đây là <b>nghịch lý Simpson</b>: xu hướng đúng khi gộp chung, biến mất khi tách theo nhóm.
Người mới đổi sang ảnh tối giản sẽ <b>không</b> nhận được kết quả của kênh mạnh &mdash;
vì cái tạo ra kết quả là những thứ khác (chất lượng nhạc, tệp khán giả sẵn có, tần suất đăng).</p>
<div class="box">
<span class="l">Một chi tiết đáng chú ý</span>
<p>Kênh giải thích <b>{vc_like:.1f}%</b> biến thiên tỷ lệ like nhưng chỉ <b>{vc_view:.1f}%</b> biến thiên lượt xem.</p>
<p>Nghĩa là: <b>ủng hộ</b> gắn chặt với thương hiệu kênh, còn <b>lượt xem</b> do thuật toán YouTube
phân phối gần như độc lập với kênh. Video nào cũng có cơ hội nổ &mdash; tin tốt cho người mới.</p>
</div>

<h2 class="pb">6. Chuẩn hình ảnh của ngách</h2>
<div class="box crit">
<span class="l">Sửa lỗi &mdash; bản trước của mục này SAI</span>
<p>Bản đầu ghi &laquo;diện tích mặt <b>3,2%</b>&raquo; và &laquo;diện tích chữ <b>11,4%</b>&raquo;.
Người dùng đối chiếu với ảnh thật và chỉ ra: người chiếm <b>1/3&ndash;1/4</b> khung, chữ <b>1/5&ndash;1/6</b>.</p>
<p><b>Nguyên nhân:</b> tôi đo <b>khuôn mặt</b> (trán&rarr;cằm) rồi diễn giải như thể đó là
<b>nhân vật</b>. Người xem nhìn thấy cả đầu, tóc, mũ, thân. Chữ thì đo bằng MSER &mdash;
<i>đoán</i> theo hình dạng thay vì <i>đọc</i>, tương quan với thực tế chỉ <b>0,233</b>.</p>
<p><b>Đã sửa:</b> dùng YOLO11-seg phân vùng người + EasyOCR đọc chữ.
Bảng dưới là số <b>đã đo lại</b>. Xem <code>lessons_learned</code> T17, T20.</p>
</div>
<table>
<thead><tr><th>Đặc điểm</th><th>Số cũ (SAI)</th><th>Đo lại</th><th>Ý nghĩa</th></tr></thead>
<tbody>
<tr class="hi"><td><b>NGƯỜI chiếm khung</b></td><td class="n"><span class="no">3,2%</span></td>
 <td class="n"><b>{bp['area_med']*100:.1f}%</b></td>
 <td>&asymp;1/4 khung &mdash; khoảng {bp['area_p25']*100:.0f}&ndash;{bp['area_p75']*100:.0f}%</td></tr>
<tr class="hi"><td><b>CHỮ chiếm khung</b></td><td class="n"><span class="no">11,4%</span></td>
 <td class="n"><b>{bt['area_med']*100:.1f}%</b></td>
 <td>&asymp;1/6 khung &mdash; khoảng {bt['area_p25']*100:.0f}&ndash;{bt['area_p75']*100:.0f}%</td></tr>
<tr><td>Có người trong ảnh</td><td class="n">&mdash;</td><td class="n">{bp['pct_has']*100:.1f}%</td>
 <td>Gần như bắt buộc</td></tr>
<tr><td>Đúng một nhân vật</td><td class="n">&mdash;</td><td class="n">{bp['one_person']*100:.1f}%</td>
 <td>Chân dung đơn, không dùng nhóm đông</td></tr>
<tr><td>Có chữ trên ảnh</td><td class="n">&mdash;</td><td class="n">{bt['pct_has']*100:.1f}%</td>
 <td>Gần như bắt buộc</td></tr>
<tr><td>Số dòng chữ</td><td class="n">&mdash;</td><td class="n">{bt['lines_med']:.0f}</td>
 <td>Tiêu đề + phụ đề + tên kênh</td></tr>
<tr><td>Vùng tối trong khung</td><td class="n">&mdash;</td><td class="n">{bc['dark_med']*100:.1f}%</td>
 <td>Ảnh tối là <b>chuẩn</b>, không phải ngoại lệ</td></tr>
<tr><td>Sắc xanh lạnh</td><td class="n">&mdash;</td><td class="n">{bc['blue_med']*100:.1f}%</td>
 <td><span class="no">Gần như không dùng &mdash; nên tránh</span></td></tr>
<tr><td>Kích thước ảnh</td><td class="n">&mdash;</td><td class="n">1280&times;720</td>
 <td>{(f.px_w==1280).mean()*100:.0f}% dùng chuẩn HD</td></tr>
</tbody></table>
<p style="font-size:8.5pt;color:#6B615A">Số đo lại lấy từ <b>{B2['n']} ảnh top 5%</b> (video dài,
đã đủ tuổi). Số cũ lấy từ 7.193 ảnh nhưng bằng phép đo sai &mdash; sai ở <b>công cụ</b>,
không phải ở cỡ mẫu.</p>
<div class="box ok">
<span class="l">Muốn công thức dựng ảnh đầy đủ?</span>
<p>Mục này chỉ nêu con số chuẩn. Công thức tái tạo &mdash; bố cục, bảng màu, ba nhánh nhân vật,
prompt mẫu, ba template từ kênh dẫn đầu, checklist sản xuất &mdash; nằm ở tài liệu riêng:</p>
<p><b>&rarr; <code>99_report/STEP04g_Brief-Thumbnail.pdf</code></b></p>
</div>
<div class="box">
<span class="l">Dùng bảng này thế nào</span>
<p>Đây là <b>vé vào cửa, không phải lợi thế cạnh tranh</b>. Làm giống chuẩn ngách giúp
bạn không trông lạc lõng; nhưng dữ liệu cho thấy làm giống <b>không</b> giúp bạn thắng &mdash;
vì tất cả đối thủ cũng đang làm giống.</p>
</div>

<h2>7. Phát hiện phụ: trùng lặp hình ảnh giữa các kênh</h2>
<p>So sánh pHash toàn bộ 7.193 ảnh (mỗi ảnh thành mã 64 bit, đo khoảng cách Hamming):</p>
<div class="kpi">
<div><div class="k">Cùng kênh</div><div class="v">1.690</div>
 <div class="c">cặp gần trùng &mdash; tái dùng mẫu, bình thường</div></div>
<div><div class="k">Giữa các kênh</div><div class="v dn">{len(DUP)}</div>
 <div class="c">cặp gần trùng &mdash; đáng chú ý</div></div>
<div><div class="k">Giống hệt</div><div class="v dn">{(DUP.hamming==0).sum()}</div>
 <div class="c">Hamming = 0, trùng từng pixel</div></div>
<div><div class="k">Kênh dính líu</div><div class="v">{n_dup_ch}</div>
 <div class="c">{n_dup_vid} video ({n_dup_vid/len(v)*100:.1f}% ngách)</div></div>
</div>
<table>
<thead><tr><th>Kênh A</th><th>Kênh B</th><th>Hamming</th></tr></thead>
<tbody>{dup_rows}</tbody></table>
<p><b>Đã kiểm tra bằng mắt:</b> các cặp Hamming = 0 giống hệt nhau <b>kể cả chữ trên ảnh</b> &mdash;
cùng một file, đăng ở nhiều kênh khác nhau.</p>
<div class="box crit">
<span class="l">Ý nghĩa cho trục T6 (rủi ro)</span>
<p><b>{n_dup_ch} trên khoảng 50 kênh</b> có ảnh trùng với kênh khác. Hai khả năng:
(a) cùng một người vận hành nhiều kênh, (b) sao chép lẫn nhau.</p>
<p>Cả hai đều là dấu hiệu ngách có <b>hàng loạt nội dung công nghiệp hóa</b> &mdash;
rào cản gia nhập thấp, nhưng cũng nghĩa là cạnh tranh bằng khối lượng, dễ dính
chính sách nội dung lặp lại của YouTube.</p>
<p>Mức độ hiện <b>chưa đủ để đổi điểm T6</b> ({n_dup_vid/len(v)*100:.1f}% video), nhưng cần theo dõi.
Danh sách đầy đủ: <code>04_outlier/11_cross_channel_dups.csv</code></p>
</div>

<h2 class="pb">8. Cách đọc từng con số</h2>
<table>
<thead><tr><th>Con số</th><th>Tính thế nào</th><th>Nguồn</th></tr></thead>
<tbody>
<tr><td><b>Cliff's &delta;</b></td>
 <td>Xác suất một video top vượt một video nhóm dưới, trừ chiều ngược lại.
 &delta; = 0 &rarr; hai nhóm như nhau; &delta; = 1 &rarr; tách hoàn toàn.</td>
 <td>tự tính, không phụ thuộc phân phối</td></tr>
<tr><td><b>p</b></td><td>Mann-Whitney U hai phía &mdash; xác suất thấy chênh lệch này nếu thực tế không có khác biệt.</td>
 <td><code>scipy.stats</code></td></tr>
<tr><td><b>Ngưỡng XÁC NHẬN</b></td><td>p &lt; 0,01 <b>và</b> |&delta;| &ge; 0,30. Cần cả hai:
 mẫu lớn khiến p nhỏ ngay cả khi chênh lệch vô nghĩa.</td><td>rubric hệ thống</td></tr>
<tr><td><b>Lớp 2</b></td><td>Lặp lại phép so trên <b>toàn thị trường</b> thay vì chỉ nhóm top.</td>
 <td>4.139 video</td></tr>
<tr><td><b>Lớp 3</b></td><td>Lặp lại <b>bên trong từng kênh</b> (kênh có &ge;5 video mỗi nửa),
 lấy trung vị các tỷ số.</td><td>41&ndash;44 kênh</td></tr>
<tr><td><b>KHÔNG ĐÁNG KỂ</b></td><td>Qua cả 3 lớp nhưng chênh trong cùng kênh &lt; 10% &rarr;
 quá nhỏ để hành động.</td><td>ngưỡng thêm mới</td></tr>
<tr><td><b>Kênh giải thích {vc_like:.1f}%</b></td>
 <td>1 &minus; (phương sai phần dư sau khi trừ trung vị kênh) / (phương sai tổng).</td>
 <td>4.139 video</td></tr>
<tr><td><b>Hamming</b></td><td>Số bit khác nhau giữa hai mã pHash 64 bit. 0 = giống hệt,
 &le;6 = gần trùng.</td><td>pHash DCT 8&times;8</td></tr>
</tbody></table>

<h2>9. Việc tiếp theo</h2>
<table>
<thead><tr><th>Ưu tiên</th><th>Việc</th><th>Vì sao</th></tr></thead>
<tbody>
<tr><td class="ac"><b>Cao</b></td><td>Nghiên cứu <b>âm nhạc</b> (khoảng trống lớn nhất)</td>
 <td>Ảnh đã loại trừ. Kênh giải thích {vc_like:.1f}% ủng hộ &mdash; phần lớn khác biệt
 nằm ở <b>nội dung nghe</b>, hiện chưa có dữ liệu (<code>media_probe</code> mới 0,6%).</td></tr>
<tr><td class="ac"><b>Cao</b></td><td>Snapshot lần 2</td>
 <td>Không liên quan thumbnail nhưng vẫn là rủi ro lớn nhất của toàn bộ kết luận (trục T2).</td></tr>
<tr><td>Vừa</td><td>Theo dõi trùng lặp hình ảnh</td>
 <td>{n_dup_ch} kênh đang dùng chung ảnh. Nếu tỷ lệ tăng &rarr; xem lại T6.</td></tr>
<tr><td>Thấp</td><td>Thử OCR đọc chữ trên ảnh</td>
 <td>Hiện chỉ đo <b>diện tích</b> chữ, chưa đọc <b>nội dung</b> chữ. Nội dung có thể có tín hiệu
 mà hình dạng không có.</td></tr>
</tbody></table>

<div class="box">
<span class="l">Ghi chú phương pháp</span>
<p>Bước này <b>loại trừ 12 giả thuyết</b> về thumbnail. Không tìm ra công thức &mdash;
nhưng biết chắc <b>không nên tốn công vào đâu</b> cũng là kết quả có giá trị.</p>
<p>Quan trọng hơn: bước này bắt được <b>một lỗi công cụ của chính tôi</b> nhờ đối chiếu chéo
và mở ảnh ra xem. Không có bước kiểm chứng đó, báo cáo vẫn sẽ trông thuyết phục &mdash; và vẫn sai.</p>
</div>

</body></html>"""

out = N/"99_report/_phu-luc/STEP04b_Phan-tich-Thumbnail.pdf"
out.parent.mkdir(parents=True, exist_ok=True)
HTML(string=DOC, base_url=".").write_pdf(out)
print(f"PDF: {out} ({out.stat().st_size/1024:.0f} KB)")
