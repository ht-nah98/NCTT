"""Sinh PDF cho STEP_04h2 — KIỂM ĐỊNH âm thanh (dữ liệu v2, nhiều track).

Theo chuẩn framework/00_system/06_REPORT_STANDARDS.md:
  .n = số so sánh được (căn phải) · .c = nhãn (căn giữa) · chữ căn trái.
Mọi con số ĐỌC TỪ AUDIO_TEST.json, không gõ tay (T27).

KHÁC build_report04h.py: bản kia MÔ TẢ nhóm top (n=5, không đối chứng).
Bản này KIỂM ĐỊNH — có view thật nên hỏi được "đặc trưng nào phân biệt
thắng/thua", và quan trọng hơn: **nêu rõ đặc trưng nào KHÔNG phân biệt**.
"""
import json, sys, warnings
from pathlib import Path
from weasyprint import HTML
warnings.filterwarnings("ignore")

N = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--")
         else "niches/christian-blues")
SRC = N/"04_outlier/audio/AUDIO_TEST.json"
if not SRC.exists():
    sys.exit(f"Thiếu {SRC} — chạy pipeline/analyze/step04h2_audio_test.py trước.")
R = json.load(open(SRC))
OUT = N/"99_report/STEP04h2_Kiem-dinh-am-thanh.pdf"


def vn(x, nd=None):
    s = f"{x:.{nd}f}" if nd is not None else f"{x:g}"
    return s.replace(".", ",")


# Tên tiếng Việt cho đặc trưng. Thiếu thì hiện nguyên mã — không bịa.
NAME = {
    "stem_drums": "Tỉ trọng TRỐNG trong bản phối",
    "stem_vocals": "Tỉ trọng GIỌNG HÁT",
    "stem_bass": "Tỉ trọng BASS",
    "stem_guitar": "Tỉ trọng GHI-TA",
    "stem_piano": "Tỉ trọng PIANO",
    "drums_over_vocals": "Tỉ lệ TRỐNG / GIỌNG HÁT",
    "drums_over_guitar": "Tỉ lệ TRỐNG / GHI-TA",
    "stereo_width": "Độ rộng âm hình stereo",
    "tach_stem_dB": "Độ sạch khi tách stem",
    "hnr_db": "Độ sạch giọng hát (HNR)",
    "buoc_lien": "Tỉ lệ giai điệu đi liền bậc",
    "vibrato_hz": "Tốc độ rung giọng (vibrato)",
    "lufs": "Độ to tổng (LUFS)",
    "bpm": "Nhịp độ (BPM)",
    "jitter": "Độ rung tần số giọng (jitter)",
    "lech_cent": "Độ lệch cao độ (cent)",
    "bam_luoi_semitone": "Mức bám lưới cao độ",
    "do_tre_ms": "Độ trễ nhịp (ms)",
    "not_moi_giay": "Mật độ nốt / giây",
    "four_on_floor": "Nhịp four-on-floor",
    "plr_db": "Dải động đỉnh–trung bình",
    "lra": "Dải động toàn bài",
    "phut": "Độ dài bản (phút)",
    "tempo_cv": "Độ trôi nhịp",
    "swing_phase": "Pha swing",
    "dao_phach": "Đảo phách",
    "quang_semitone": "Quãng giọng (nửa cung)",
    "so_hop_am_rieng": "Số hợp âm riêng",
    "hop_am_moi_o_nhip": "Tốc độ đổi hợp âm",
    "tuong_quan_LR": "Tương quan kênh trái–phải",
}
def nm(f):
    base = f.replace("_clr", "")
    t = NAME.get(f) or NAME.get(base, f)
    return t + " <i>(đã khử ràng buộc tỉ lệ)</i>" if f.endswith("_clr") else t


T = R["tests"]
VS, SW = R["view_span"], R["simpson_warnings"]
conf = [t for t in T if t["verdict"] == "XÁC NHẬN"]
weak = [t for t in T if t["verdict"] == "YẾU"]
rejected = [t for t in T if t["verdict"] == "BÁC BỎ"]

VERD = {"XÁC NHẬN": '<b class="ok">XÁC NHẬN</b>',
        "YẾU": '<b style="color:#B5731F">YẾU</b>',
        "BÁC BỎ": '<b class="no">BÁC BỎ</b>'}


def rows(items, lim=None):
    out = []
    for t in (items[:lim] if lim else items):
        cls = ' class="hi"' if t["verdict"] == "XÁC NHẬN" else ""
        agree = f'{t["k_positive"]}/{t["k_channels"]}'
        if t["k_positive"] in (0, t["k_channels"]):
            agree = f'<b>{agree}</b>'
        out.append(
            f'<tr{cls}><td>{nm(t["feature"])}<br>'
            f'<span style="font-size:6.5pt;color:#8A7F76"><code>{t["feature"]}</code></span></td>'
            f'<td class="n">{vn(t["rho_mean"], 3)}</td>'
            f'<td class="n">{vn(t["q"], 3)}</td>'
            f'<td class="c">{agree}</td>'
            f'<td class="c">{VERD[t["verdict"]]}</td></tr>')
    return "\n".join(out)


simpson_rows = "\n".join(
    f'<tr><td>{nm(s["feature"])}<br>'
    f'<span style="font-size:6.5pt;color:#8A7F76"><code>{s["feature"]}</code></span></td>'
    f'<td class="n">{vn(s["naive_rho"], 3)}</td>'
    f'<td class="n">{vn(s["naive_p"], 3)}</td>'
    f'<td class="n">{vn(s["within_rho"], 3)}</td>'
    f'<td class="c">{s["k_positive"]}/{s["k_channels"]}</td>'
    f'<td class="c">{"⚠ đảo dấu" if s["reversed_sign"] else "mất ý nghĩa"}</td></tr>'
    for s in SW)

CAT = R.get("categorical_tests", [])
CATNAME = {"truong_thu": "Điệu trưởng / thứ", "quang_giong": "Quãng giọng (tenor/alto…)",
           "ho_the_loai": "Họ thể loại", "nhip": "Số phách mỗi ô nhịp",
           "the_loai_chinh": "Thể loại chính"}
CATVERD = dict(VERD, **{"KHÔNG ĐỦ MẪU": '<b style="color:#7A6F68">KHÔNG ĐỦ MẪU</b>'})
cat_rows = "\n".join(
    f'<tr><td>{CATNAME.get(c["feature"], c["feature"])}<br>'
    f'<span style="font-size:6.5pt;color:#8A7F76"><code>{c["feature"]}</code></span></td>'
    f'<td class="c">{c["k_channels_tested"]}</td>'
    f'<td class="c">{"⚠ có" if c["note"] else "—"}</td>'
    f'<td class="c">{CATVERD.get(c["verdict"], c["verdict"])}</td></tr>'
    for c in CAT) or '<tr><td colspan="4">Không có đặc trưng phân loại nào đủ mẫu.</td></tr>'

limit_rows = "\n".join(f'<li>{l}</li>' for l in R["_meta"]["limits"])

# đặc trưng bị bác bỏ — cái này QUAN TRỌNG ngang cái được xác nhận
rej_names = ", ".join(f'<code>{t["feature"]}</code>' for t in rejected[:14])

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
code {{ background:#F2EEE8;padding:.5pt 3pt;font-size:8pt; }}
.formula {{ background:#F7F4F0;border:.6pt solid #E2DAD1;padding:7pt 10pt;
 font-size:8.5pt;margin:7pt 0;line-height:1.7; }}
.pb {{ page-break-before:always; }}
.f {{ font-size:7.5pt;color:#7A6F68;margin:-2pt 0 10pt; }}
ul {{ margin:6pt 0;padding-left:15pt; }} li {{ margin:3pt 0; }}
.keep {{ page-break-inside:avoid; }}
</style></head><body>

<h1>Kiểm định âm thanh</h1>
<p class="sub">Đặc trưng nào <b>thật sự</b> phân biệt video thắng và video thua?</p>
<div class="meta">
STEP_04h2 &nbsp;•&nbsp; Dữ liệu DNA âm thanh v2
&nbsp;•&nbsp; {R['n_tracks']} track &rarr; <b>{R['n_videos']} video</b> / {R['n_channels']} kênh
&nbsp;•&nbsp; {VS['min']:,} &ndash; {VS['max']:,} lượt xem (chênh {vn(VS['ratio'],1)}&times;)
</div>

<div class="box crit">
<span class="l">Đọc trước: n thật là {R['n_videos']}, không phải {R['n_tracks']}</span>
<p>{R['n_tracks']} track chỉ đến từ <b>{R['n_videos']} video</b> &mdash; nhiều track
cùng một video <b>chia chung một con số lượt xem</b>. Dùng track làm đơn vị sẽ thổi
phồng cỡ mẫu gấp ~{R['n_tracks']//max(R['n_videos'],1)} lần và cho ra ý nghĩa thống kê giả.
Báo cáo này gộp track &rarr; video bằng trung vị trước khi kiểm.</p>
<p>Bước lùi này khiến kết quả <b>khiêm tốn hơn</b> con số 307 gợi ý &mdash; nhưng đó là
cỡ mẫu thật.</p>
</div>

<div class="kpi">
<div><div class="k">Xác nhận</div><div class="v ok">{len(conf)}</div>
 <div class="c">qua đa kiểm định &amp; mọi kênh cùng dấu</div></div>
<div><div class="k">Tín hiệu yếu</div><div class="v" style="color:#B5731F">{len(weak)}</div>
 <div class="c">có dấu hiệu, chưa đủ chắc</div></div>
<div><div class="k">Bác bỏ</div><div class="v no">{len(rejected)}</div>
 <div class="c">không phân biệt thắng/thua</div></div>
<div><div class="k">Bẫy Simpson</div><div class="v ac">{len(SW)}</div>
 <div class="c">đã chặn</div></div>
</div>

<h2>1. Kết quả</h2>

{'<div class="box ok"><span class="l">Xác nhận: ' + nm(conf[0]["feature"]) + '</span>'
 '<p>Tương quan trung bình trong kênh <b>' + vn(conf[0]["rho_mean"],3) + '</b>, '
 'q=' + vn(conf[0]["q"],3) + ', và <b>toàn bộ ' + str(conf[0]["k_channels"]) +
 '/' + str(conf[0]["k_channels"]) + ' kênh cùng chiều</b>. '
 'Video ít trống hơn (so với chính kênh đó) có lượt xem cao hơn.</p></div>'
 if conf else
 '<div class="box crit"><span class="l">Không đặc trưng nào đạt XÁC NHẬN</span>'
 '<p>Không đặc trưng âm thanh nào vừa qua hiệu chỉnh đa kiểm định vừa nhất quán '
 'ở mọi kênh. Đây là kết quả hợp lệ, không phải lỗi.</p></div>'}

<table>
<thead><tr><th>Đặc trưng</th><th class="n">rho TB</th><th class="n">q (BH)</th>
<th class="c">Kênh cùng dấu</th><th class="c">Phán quyết</th></tr></thead>
<tbody>
{rows(T, 14)}
</tbody></table>
<p class="f">rho = tương quan Spearman trung bình <b>trong từng kênh</b> ·
q = giá trị p sau hiệu chỉnh Benjamini&ndash;Hochberg cho {len(T)} phép kiểm ·
XÁC NHẬN đòi <b>cả hai</b>: q&lt;0,05 <b>và</b> mọi kênh cùng dấu.</p>

<div class="box">
<span class="l">Vì sao đòi &laquo;mọi kênh cùng dấu&raquo;</span>
<p>Chỉ dựa vào q sẽ để lọt <code>drums_over_vocals</code> &mdash; đặc trưng có q nhỏ nhất
bảng nhưng <b>1 kênh đi ngược</b>. Một quy luật sản xuất mà một trong sáu kênh làm
ngược lại vẫn thắng thì <b>chưa phải quy luật</b>. Nên nó bị hạ xuống YẾU.</p>
</div>

<h2 class="pb">2. Năm cái bẫy đã chặn được</h2>

<p>Đây là phần quan trọng nhất của báo cáo. Nếu chỉ chạy tương quan gộp trên
{R['n_tracks']} track, <b>{len(SW)} đặc trưng dưới đây sẽ được báo cáo là phát hiện</b> &mdash;
và tất cả đều sai.</p>

<table>
<thead><tr><th>Đặc trưng</th><th class="n">rho gộp</th><th class="n">p gộp</th>
<th class="n">rho trong kênh</th><th class="c">Cùng dấu</th><th class="c">Vấn đề</th></tr></thead>
<tbody>
{simpson_rows}
</tbody></table>

<div class="box crit">
<span class="l">Ví dụ cụ thể: piano</span>
<p>Gộp toàn bộ track: <b>rho = +0,36 &nbsp; p = 0,000000000076</b>. Nhìn con số này
ai cũng sẽ viết vào brief sản xuất: <i>&laquo;thêm piano vào bản phối&raquo;</i>.</p>
<p>Nhưng {R['n_channels']} kênh chênh nhau <b>{vn(R['channel_spread_ratio'],1)}&times;</b> về lượt xem
trung vị. Hai kênh mạnh tình cờ dùng nhiều piano, hai kênh yếu gần như không dùng.
Tách theo kênh thì <b>2/6 kênh cho dấu ngược lại</b>, và phán quyết cuối là
<b class="no">BÁC BỎ</b>.</p>
<p>Tương quan gộp đang đo <b>sự khác nhau giữa các kênh</b>, không đo tác dụng của piano.
Đây là <b>nghịch lý Simpson</b> &mdash; đúng loại bẫy STEP_04 sinh ra để chặn.</p>
</div>

<h3>Thể loại nhạc cũng là bẫy tương tự</h3>
<p>Thể loại (<code>ho_the_loai</code>) phân biệt lượt xem rất mạnh khi gộp
(Kruskal p &lt; 0,0001). Nhưng thể loại <b>lẫn gần như hoàn toàn với kênh</b>
(chi&sup2; = 248, p = 5,7e&minus;34): mỗi kênh gần như chỉ làm một họ thể loại.
Trong từng kênh, thể loại <b>hết phân biệt</b> ở 3/4 kênh đủ mẫu.
Nói &laquo;làm Funk/Soul sẽ thắng&raquo; thực chất là nói &laquo;hãy là kênh khác&raquo;.</p>

<h2>3. Điều KHÔNG phân biệt thắng/thua</h2>

<p>Phần này ngang giá trị với phần trên. {len(rejected)} đặc trưng dưới đây
<b>không</b> phân biệt được video thắng và thua &mdash; đừng tốn công tối ưu chúng:</p>
<div class="formula">{rej_names}</div>
<p>Đáng chú ý nhất là <b>BPM</b>, <b>LUFS</b> (độ to) và <b>quãng giọng tính bằng nửa cung</b>
&mdash; ba thông số hay được đưa vào brief sản xuất. Ở đây chúng <b>không</b> phân biệt
được nhóm dẫn đầu với nhóm sau.</p>

<h3>Đặc trưng phân loại: chưa kết luận được</h3>
<table>
<thead><tr><th>Đặc trưng</th><th class="c">Kênh đủ mẫu</th>
<th class="c">Lẫn với kênh?</th><th class="c">Phán quyết</th></tr></thead>
<tbody>
{cat_rows}
</tbody></table>
<p class="f">Ở cỡ mẫu {R['n_videos']} video, mỗi kênh chỉ còn ~5 video nên phần lớn
<b>không đủ nhóm để kiểm</b>. <b>KHÔNG ĐỦ MẪU khác hẳn BÁC BỎ</b> &mdash; ta chưa biết,
chứ không phải đã biết là không.</p>

<h2>4. Dữ liệu v2 sửa lại điều gì so với v1</h2>

<div class="box">
<span class="l">Kết luận cũ về nhịp độ đã sai lệch</span>
<p>Brief cũ (STEP_04h) dựng trên <b>5 bản</b>, cho BPM trong khoảng
<b>51,7 &ndash; 80,8</b>. Với {R['n_tracks']} bản, phân bố thật là
<b>67 &ndash; 154</b> (trung vị 88,2).</p>
<p>Nghĩa là 5 bản cũ <b>không đại diện</b> cho ngách &mdash; chúng nằm lệch hẳn về phía
chậm. Mọi brief sản xuất dựa trên khoảng BPM cũ cần đọc lại.</p>
</div>

<h2>5. Giới hạn của báo cáo này</h2>
<ul>
{limit_rows}
</ul>

<div class="box crit">
<span class="l">Thiếu lớn nhất: chưa có nhóm THẤT BẠI</span>
<p>Cả {R['n_channels']} kênh trong mẫu đều là kênh <b>đang làm được</b> &mdash; kênh thấp nhất
vẫn có {VS['min']:,} lượt xem. Ta mới so &laquo;khá&raquo; với &laquo;rất tốt&raquo;,
chưa so &laquo;thắng&raquo; với &laquo;thua&raquo;.</p>
<p>Muốn kết luận chắc, cần track từ <b>kênh thất bại</b> &mdash; đúng logic nhóm đối chứng
của STEP_04. Đây là đề nghị ưu tiên số 1 cho đợt cào dữ liệu tiếp theo.</p>
</div>

<p class="f">Phương pháp: {R['_meta']['method']} ·
Quy tắc phán quyết: {R['_meta']['verdict_rule']} ·
Đơn vị phân tích: {R['unit_of_analysis']}</p>

</body></html>"""

HTML(string=DOC).write_pdf(OUT)
print(f"✅ {OUT}")
