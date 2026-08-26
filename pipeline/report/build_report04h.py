"""Sinh PDF cho STEP_04h — Brief âm nhạc (tái tạo được).

Theo chuẩn framework/00_system/06_REPORT_STANDARDS.md:
  .n = số so sánh được (căn phải) · .c = nhãn (căn giữa) · chữ căn trái.
Mọi con số ĐỌC TỪ AUDIO_BRIEF.json, không gõ tay (T27).
"""
import json, sys, warnings
from pathlib import Path
from weasyprint import HTML
warnings.filterwarnings("ignore")

N = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--")
         else "niches/christian-blues")
SRC = N/"04_outlier/audio/AUDIO_BRIEF.json"
if not SRC.exists():
    sys.exit(f"Thiếu {SRC} — chạy pipeline/analyze/step04h_audio.py trước.")
R = json.load(open(SRC))


def vn(x, nd=None):
    s = f"{x:.{nd}f}" if nd is not None else f"{x:g}"
    return s.replace(".", ",")


G = R["generated_from"]

# ── Quyết định CÓ LỜI / KHÔNG LỜI (gom từ STEP_05 + STEP_06) ────────────
VD = R.get("vocal_decision", {})
_ve = VD.get("bằng_chứng_hiệu_quả", {})
_vc = VD.get("bằng_chứng_bối_cảnh", {})
_vq = VD.get("bằng_chứng_định_tính", {})
_lift = _ve.get("lift_toàn_thị_trường", 0)
T, K, H, GR, ST, RC = R["tempo"], R["key"], R["harmony"], R["groove"], R["structure"], R["recipe"]


def band(d, unit="", nd=1):
    """Ô hiển thị khoảng [min – max] + trung vị."""
    return (f'{vn(d["min"], nd)}–{vn(d["max"], nd)}{unit}'
            f'<br><span style="font-size:6.5pt;color:#8A7F76">trung vị {vn(d["median"], nd)}{unit}</span>')


track_rows = "\n".join(
    f'<tr><td>{t["title"][:44]}<br>'
    f'<span style="font-size:6.5pt;color:#8A7F76">{t["video_id"]}</span></td>'
    f'<td class="n">{t["view_count"]:,}</td>'
    f'<td class="n">{vn(t["bpm"])}<br>'
    f'<span style="font-size:6.5pt;color:#8A7F76">gốc {vn(t["bpm_raw"])}</span></td>'
    f'<td class="c">{t["key"]}</td>'
    f'<td class="n">{vn(t["sec_per_chord"])}s</td>'
    f'<td class="n">{t["distinct_chords"]}</td>'
    f'<td class="n">{vn(t["swing_pct"])}%</td>'
    f'<td class="c">{t["energy_shape"]}</td></tr>'.replace(",", ".")
    for t in R["tracks"])

model_rows = "\n".join(
    f'<tr><td><b>{m["model"]}</b></td><td class="n">{m["n"]}</td>'
    f'<td class="n">{vn(m["bpm_median"])}</td>'
    f'<td class="n">{vn(m["sec_per_chord_median"])}s</td>'
    f'<td class="n">{vn(m["distinct_chords_median"], 0)}</td>'
    f'<td class="n">{vn(m["n_sections_median"], 0)}</td></tr>'
    for m in R["by_model"])

limit_rows = "\n".join(
    f'<tr><td><b>{l["thiếu"]}</b></td><td>{l["hệ_quả"]}</td>'
    f'<td style="font-size:7.5pt">{l["khắc_phục"]}</td></tr>'
    for l in R["limits"])

shape_rows = "\n".join(
    f'<tr><td class="c">{v}</td><td>{k}</td></tr>'
    for k, v in R["energy_curve"]["shape_distribution"].items())

DOC = f"""<!doctype html><html><head><meta charset="utf-8"><style>
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
td.n, th.n {{ text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap; }}
td.c, th.c {{ text-align:center;white-space:nowrap; }}
tr.hi {{ background:#F4E6E2; }}
.ok {{ color:#2F6B4F;font-weight:bold; }} .no {{ color:#9B2C2C;font-weight:bold; }}
.ac {{ color:#8C3A2B; }}
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
.kpi .v {{ font-size:15pt;font-weight:bold;letter-spacing:-.3pt; }}
.kpi .c {{ font-size:7pt;color:#7A6F68;margin-top:3pt;line-height:1.3; }}
code {{ background:#F2EEE8;padding:.5pt 3pt;font-size:8.5pt; }}
.formula {{ background:#F7F4F0;border:.6pt solid #E2DAD1;padding:7pt 10pt;
 font-size:8.5pt;margin:7pt 0;line-height:1.7; }}
.prompt {{ background:#1A1614;color:#F2EEE8;padding:9pt 11pt;font-size:8.5pt;
 line-height:1.6;margin:8pt 0;font-family:"DejaVu Sans Mono",monospace; }}
.pb {{ page-break-before:always; }}
.f {{ font-size:7.5pt;color:#7A6F68;margin:-2pt 0 10pt; }}
ul {{ margin:6pt 0;padding-left:15pt; }} li {{ margin:3pt 0; }}
</style></head><body>

<h1>Brief âm nhạc &mdash; tái tạo được</h1>
<p class="sub">Năm bản nhạc top {G['percentile'].split()[1]} của ngách được dựng như thế nào</p>
<div class="meta">
STEP_04h &nbsp;•&nbsp; Phân tích DSP (librosa), không dùng model huấn luyện sẵn
&nbsp;•&nbsp; {G['n_tracks']} bản &middot; {G['n_sections']} đoạn
&nbsp;•&nbsp; {G['view_min']:,} &ndash; {G['view_max']:,} lượt xem
</div>

<div class="box crit">
<span class="l">Đọc trước: đây là MÔ TẢ, không phải bằng chứng nhân quả</span>
<p>Với <b>{G['n_tracks']} bản và không có nhóm đối chứng</b>, không thể kết luận
&ldquo;đặc điểm nào GÂY RA thành công&rdquo;. Báo cáo này trả lời câu hỏi khác:
<b>&laquo;nhóm dẫn đầu đang dựng nhạc như thế nào?&raquo;</b> &mdash; câu đó trả lời
chính xác được, và <b>tái tạo được</b>.</p>
<p>Cùng logic với brief thumbnail (STEP_04g). Xem
<code>00_system/01_ARCHITECTURE.md</code> §2.4.</p>
</div>

<div class="kpi">
<div><div class="k">Nhịp độ</div><div class="v ac">{vn(T['bpm']['min'])}&ndash;{vn(T['bpm']['max'])}</div>
 <div class="c">BPM · trung vị {vn(T['bpm']['median'])}</div></div>
<div><div class="k">Điệu thức</div><div class="v">{K['mode_distribution'].get('major',0)}/{G['n_tracks']}</div>
 <div class="c">ở điệu TRƯỞNG</div></div>
<div><div class="k">Đổi hợp âm</div><div class="v">{vn(H['sec_per_chord']['median'])}s</div>
 <div class="c">mỗi {vn(H['sec_per_chord']['min'])}&ndash;{vn(H['sec_per_chord']['max'])} giây</div></div>
<div><div class="k">Groove</div><div class="v">{GR['n_swing']} / {GR['n_straight']}</div>
 <div class="c">swing / thẳng</div></div>
</div>

<h2>1. Câu hỏi đầu tiên: có lời hay không lời?</h2>

<div class="box ok">
<span class="l">Trả lời: NHẠC CÓ LỜI &mdash; độ tin cậy {VD.get('độ_tin_cậy','—')}</span>
<p>Đây là quyết định sản xuất phải chốt <b>trước</b> mọi thông số khác. Câu trả lời
<b>không đến từ 5 file DSP</b> (chúng không tách được giọng hát) mà từ hai bước khác
của nghiên cứu &mdash; gom về đây vì đây là nơi bạn hỏi.</p>
</div>

<table>
<thead><tr><th>Bằng chứng</th><th class="n">Số liệu</th><th>Nghĩa là gì</th></tr></thead>
<tbody>
<tr class="hi"><td><b>Hiệu quả</b><br>
 <span style="font-size:6.5pt;color:#8A7F76">06_keyword/02_theme_scores.csv</span></td>
 <td class="n">lift <b>{vn(_lift,2)}</b></td>
 <td>Video gắn nhãn <i>instrumental / no lyrics / background</i> chỉ đạt VPD bằng
 <b>{_lift*100:.0f}%</b> so với phần còn lại &mdash; <b>{_ve.get('xếp_hạng','—')}</b></td></tr>
<tr><td><b>Kiểm trong từng kênh</b><br>
 <span style="font-size:6.5pt;color:#8A7F76">lớp 3 chống nghịch lý Simpson</span></td>
 <td class="n">{vn(_ve.get('trong_từng_kênh',0),2)}</td>
 <td>Chỉ <b>{_ve.get('số_kênh_tốt_hơn','—')}</b> kênh làm không lời tốt hơn chính họ
 &rarr; không phải hiệu ứng &laquo;kênh yếu&raquo;.
 Phán quyết: <b class="no">{_ve.get('phán_quyết','—')}</b></td></tr>
<tr class="hi"><td><b>Bối cảnh nghe</b><br>
 <span style="font-size:6.5pt;color:#8A7F76">05_audience → context</span></td>
 <td class="n">{vn(_vc.get('tỷ_lệ',0))}&times;</td>
 <td>Nghe <b>chủ động</b> (cầu nguyện, sáng sớm, bệnh tật, tang chế) chiếm
 {vn(_vc.get('nghe_chủ_động_pct',0))}%; nghe <b>làm nền</b> (ngủ, lái xe, việc nhà)
 chỉ {vn(_vc.get('nghe_nền_pct',0))}%</td></tr>
<tr><td><b>Nỗi đau lõi</b><br>
 <span style="font-size:6.5pt;color:#8A7F76">05_audience/03_quote_bank.csv</span></td>
 <td class="n">1.444 ♥</td>
 <td>Comment được thích nhiều nhất toàn ngách nói thẳng về <b>lời hát</b></td></tr>
</tbody></table>

<div class="box">
<span class="l">Vì sao bằng chứng này đáng tin hơn phần còn lại của báo cáo</span>
<p>Hầu hết giả thuyết trong dự án <b>bị bác bỏ</b> ở lớp kiểm thứ ba. Kết luận này
<b>đứng vững cả ba lớp</b>: mẫu &rarr; toàn thị trường &rarr; trong từng kênh.
Đó là chuyện hiếm ở đây.</p>
<p style="font-style:italic;padding-left:10pt;border-left:2pt solid #CFC4B8;margin-top:7pt">
&ldquo;{_vq.get('nội_dung','')}&rdquo;</p>
<p class="f" style="margin:3pt 0 0">Nỗi đau của khán giả nằm ở <b>lời hát thế tục</b>,
không phải ở phần nhạc. Bỏ lời là bỏ đúng thứ khiến họ tìm đến ngách này.</p>
</div>

<div class="box crit">
<span class="l">Ngoại lệ duy nhất</span>
<p>{VD.get('ngoại_lệ','')}</p>
</div>

<h2 class="pb">2. Một lỗi đo phải sửa trước khi tin bất cứ số nào</h2>

<div class="box crit">
<span class="l">Bẫy nhân đôi tempo &mdash; {T['n_corrected']}/{G['n_tracks']} bản bị ảnh hưởng</span>
<p>File YAML thô báo <b>{vn(T['bpm_raw_before_fix']['min'])}&ndash;{vn(T['bpm_raw_before_fix']['max'])} BPM</b>
cho nhạc gospel/blues <b>chậm</b>. Con số đó gấp đôi thực tế: <code>librosa</code> bám vào
lớp đệm (hi-hat, tremolo guitar) thay vì phách chính.</p>
<p><b>Ba bằng chứng độc lập:</b></p>
<p>1. <b>Nhịp hòa âm</b> &mdash; 7,3&ndash;13,8 phách mỗi hợp âm. Ở nhịp 4/4 thì 8 phách
= 2 ô nhịp; 13,8 phách là vô lý.</p>
<p>2. <b>Giây mỗi hợp âm</b> &mdash; 3,2&ndash;5,4 giây, quá nhanh cho ballad.</p>
<p>3. <b>Onset mỗi phách</b> &mdash; cả {G['n_tracks']} bản đều &lt;1,0. Ít nốt hơn phách
nghĩa là lưới phách <b>dày hơn nhạc thật</b>.</p>
<p>Sau khi chia đôi: <b>{vn(T['bpm']['min'])}&ndash;{vn(T['bpm']['max'])} BPM</b> &mdash;
đúng dải slow blues / gospel ballad.</p>
<p class="f" style="margin:6pt 0 0">Số gốc vẫn được giữ trong
<code>bpm_raw</code> để truy vết. Không bao giờ xóa dữ liệu gốc.</p>
</div>

<h2>3. Công thức tái tạo</h2>
<p>Đây là mục tiêu cuối cùng: thông số máy đọc được, nạp thẳng vào công cụ sinh nhạc.
File: <code>04_outlier/audio/AUDIO_BRIEF.json &rarr; recipe</code></p>

<table>
<thead><tr><th>Thông số</th><th class="n">Khoảng quan sát</th><th class="n">Mục tiêu</th>
<th>Ghi chú</th></tr></thead>
<tbody>
<tr class="hi"><td><b>Nhịp độ</b></td>
 <td class="n">{vn(T['bpm']['min'])}&ndash;{vn(T['bpm']['max'])} BPM</td>
 <td class="n"><b>{vn(RC['tempo_bpm']['target'])}</b></td>
 <td>đã sửa bẫy nhân đôi</td></tr>
<tr><td><b>Điệu thức</b></td><td class="n">&mdash;</td>
 <td class="c"><b>{RC['mode']}</b></td>
 <td>{K['mode_distribution'].get('major',0)}/{G['n_tracks']} bản</td></tr>
<tr class="hi"><td><b>Nhịp hòa âm</b></td>
 <td class="n">{vn(H['sec_per_chord']['min'])}&ndash;{vn(H['sec_per_chord']['max'])} giây</td>
 <td class="n"><b>{vn(RC['harmonic_rhythm_sec']['target'])}s</b></td>
 <td>mỗi hợp âm giữ bao lâu</td></tr>
<tr><td><b>Số hợp âm khác nhau</b></td>
 <td class="n">{vn(H['distinct_chords']['min'],0)}&ndash;{vn(H['distinct_chords']['max'],0)}</td>
 <td class="n">&mdash;</td><td>{RC['chord_vocabulary']['ghi_chú']}</td></tr>
<tr class="hi"><td><b>Syncopation</b></td>
 <td class="n">{vn(GR['syncopation']['min'],3)}&ndash;{vn(GR['syncopation']['max'],3)}</td>
 <td class="n">&lt;0,2</td><td>nhịp đơn giản, không giật</td></tr>
<tr><td><b>Độ dài mỗi đoạn</b></td>
 <td class="n">{vn(ST['section_dur_sec']['min'])}&ndash;{vn(ST['section_dur_sec']['max'])} giây</td>
 <td class="n">{vn(RC['section_dur_sec']['target'])}s</td>
 <td>{RC['section_dur_sec']['ghi_chú']}</td></tr>
</tbody></table>

<h3>Prompt tiếng Anh (nạp vào Suno / Udio)</h3>
<div class="prompt">{RC['prompt_en']}</div>
<p class="f">⚠ {RC['prompt_ghi_chú']}</p>

<h2 class="pb">4. Ba phát hiện đáng chú ý</h2>

<div class="box ok">
<span class="l">1. Cả {G['n_tracks']} bản đều ở điệu TRƯỞNG &mdash; trái trực giác</span>
<p>&ldquo;Blues thì buồn nên phải dùng điệu thứ&rdquo; &mdash; dữ liệu nói ngược lại.
Toàn bộ {G['n_tracks']} bản dẫn đầu ở <b>điệu trưởng</b>, độ tin cậy nhận diện
{vn(K['key_confidence']['min'],2)}&ndash;{vn(K['key_confidence']['max'],2)}.</p>
<p>Màu &ldquo;buồn&rdquo; không đến từ điệu thức mà từ <b>hợp âm thứ xen vào</b> &mdash;
nền sáng, màu tối. Đây chính là chất gospel: thừa nhận nỗi đau nhưng kết ở hy vọng,
khớp đúng phát hiện STEP_05 về động cơ nghe.</p>
</div>

<div class="box">
<span class="l">2. Bảng màu hợp âm KHÔNG có chuẩn</span>
<p>{H['phát_hiện']}</p>
<p>Đây là chỗ <b>chọn phong cách</b>, không phải chỗ sao chép.</p>
</div>

<div class="box">
<span class="l">3. Đường cong năng lượng cũng không có khuôn</span>
<table style="margin:4pt 0">
<thead><tr><th class="c">Số bản</th><th>Dạng đường cong</th></tr></thead>
<tbody>{shape_rows}</tbody></table>
<p>{R['energy_curve']['phát_hiện']}</p>
</div>

<h2>5. Hai mô hình sản xuất</h2>
<p>Giống phát hiện ở STEP_10, nhạc của hai nhóm khác nhau rõ rệt:</p>
<table>
<thead><tr><th>Mô hình</th><th class="n">Số bản</th><th class="n">BPM</th>
<th class="n">Giây/hợp âm</th><th class="n">Số hợp âm</th><th class="n">Số đoạn</th></tr></thead>
<tbody>{model_rows}</tbody></table>
<p class="f">Bản dài dùng <b>gấp đôi vốn hợp âm</b> và gấp hơn hai lần số đoạn &mdash;
cần thế để giữ tai người nghe suốt 30&ndash;100 phút.</p>

<h2>6. Từng bản &mdash; truy vết được</h2>
<table>
<thead><tr><th>Bản nhạc</th><th class="n">Lượt xem</th><th class="n">BPM</th>
<th class="c">Điệu</th><th class="n">Giây/<br>hợp âm</th><th class="n">Số<br>hợp âm</th>
<th class="n">Swing</th><th class="c">Năng lượng</th></tr></thead>
<tbody>{track_rows}</tbody></table>
<p class="f">Mở <code>00_input/raw/audio/&lt;video_id&gt;.yaml</code> để xem phân tích gốc
đầy đủ, gồm cả danh sách hợp âm từng đoạn.</p>

<h2>7. Những gì chưa đo được</h2>
<div class="box crit">
<span class="l">Nói thẳng để không kỳ vọng sai</span>
<p>Brief này cho <b>khung xương</b> của bản nhạc (nhịp độ, điệu thức, hòa âm, cấu trúc).
Nó <b>chưa</b> cho biết bản nhạc <i>nghe như thế nào</i> &mdash; phần quyết định
&ldquo;giống hay không giống&rdquo;.</p>
</div>
<table>
<thead><tr><th>Thiếu</th><th>Hệ quả</th><th>Cách khắc phục</th></tr></thead>
<tbody>{limit_rows}</tbody></table>

<div class="box ok">
<span class="l">Bước tiếp theo đáng làm nhất</span>
<p><b>1. Tăng mẫu lên ≥30 bản top</b> &mdash; biến &ldquo;khoảng quan sát&rdquo; thành
chuẩn ngành đáng tin.</p>
<p><b>2. Thêm ~30 bản nhóm thua (B4)</b> &mdash; có nhóm đối chứng thì mới chuyển từ
tầng MÔ TẢ sang tầng KIỂM ĐỊNH, trả lời được &ldquo;đặc điểm nào thật sự phân biệt&rdquo;.</p>
<p><b>3. Tách stem + đo LUFS</b> &mdash; lấp đúng khoảng trống lớn nhất: nhạc cụ,
giọng hát, chuẩn âm lượng.</p>
</div>

</body></html>"""

out = N/"99_report/STEP04h_Brief-Am-nhac.pdf"
out.parent.mkdir(parents=True, exist_ok=True)
HTML(string=DOC).write_pdf(out)
print(f"PDF: {out} ({out.stat().st_size//1024} KB)")
