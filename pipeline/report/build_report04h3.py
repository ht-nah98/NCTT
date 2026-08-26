"""Sinh PDF cho STEP_04h3 — CÔNG THỨC TÁI TẠO NHẠC.

Theo chuẩn framework/00_system/06_REPORT_STANDARDS.md:
  .n = số so sánh được (căn phải) · .c = nhãn (căn giữa) · chữ căn trái.
Mọi con số ĐỌC TỪ AUDIO_RECIPE.json, không gõ tay (T27).

Trình bày theo KHÂU SẢN XUẤT (sáng tác → giai điệu → groove → phối khí →
giọng → mix) chứ không theo tên cột, vì người dùng báo cáo này là người
dựng nhạc, không phải người phân tích dữ liệu.
"""
import json, sys, warnings
from pathlib import Path
from weasyprint import HTML
warnings.filterwarnings("ignore")

N = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--")
         else "niches/christian-blues")
SRC = N/"04_outlier/audio/AUDIO_RECIPE.json"
if not SRC.exists():
    sys.exit(f"Thiếu {SRC} — chạy pipeline/analyze/step04h3_audio_recipe.py trước.")
R = json.load(open(SRC))
OUT = N/"99_report/STEP04h3_Cong-thuc-Tai-tao-Nhac.pdf"


def vn(x, nd=None):
    s = f"{x:.{nd}f}" if nd is not None else f"{x:g}"
    return s.replace(".", ",")


C = R["cohort"]
SPEC, CATS = R["spec"], R["categorical"]

STAGE_NAME = {
    "1_sang_tac": ("1 · Sáng tác", "Khung bài: nhịp độ, điệu thức, hợp âm, độ dài"),
    "2_giai_dieu": ("2 · Giai điệu", "Đường nét câu hát"),
    "3_groove": ("3 · Groove", "Cảm giác nhịp — thứ tạo ra chất blues"),
    "4_phoi_khi": ("4 · Phối khí", "Tỉ trọng từng nhạc cụ trong bản phối"),
    "5_giong_hat": ("5 · Giọng hát", "Cách xử lý giọng — KHÔNG dùng autotune cứng"),
    "6_mix_master": ("6 · Mix &amp; Master", "Độ to, dải động, âm hình"),
}

LABEL = {
    "bpm": ("Nhịp độ", "BPM"), "phut": ("Độ dài bản", "phút"),
    "so_hop_am_rieng": ("Số hợp âm riêng", "hợp âm"),
    "hop_am_moi_o_nhip": ("Tốc độ đổi hợp âm", "hợp âm/ô nhịp"),
    "buoc_lien": ("Giai điệu đi liền bậc", "tỉ lệ"),
    "not_moi_giay": ("Mật độ nốt", "nốt/giây"),
    "quang_semitone": ("Quãng giọng dùng", "nửa cung"),
    "swing_phase": ("Pha swing", ""), "dao_phach": ("Đảo phách", ""),
    "four_on_floor": ("Four-on-floor", "tỉ lệ"),
    "tempo_cv": ("Độ trôi nhịp", ""), "do_tre_ms": ("Độ trễ nhịp", "ms"),
    "stem_vocals": ("Giọng hát", "tỉ trọng"), "stem_bass": ("Bass", "tỉ trọng"),
    "stem_drums": ("Trống", "tỉ trọng"), "stem_guitar": ("Ghi-ta", "tỉ trọng"),
    "stem_piano": ("Piano", "tỉ trọng"),
    "vibrato_hz": ("Tốc độ rung giọng", "Hz"), "hnr_db": ("Độ sạch giọng (HNR)", "dB"),
    "jitter": ("Rung tần số (jitter)", ""),
    "lech_cent": ("Lệch cao độ", "cent"),
    "bam_luoi_semitone": ("Bám lưới cao độ", "tỉ lệ"),
    "lufs": ("Độ to tổng", "LUFS"), "plr_db": ("Dải động đỉnh", "dB"),
    "lra": ("Dải động toàn bài", "LU"), "stereo_width": ("Độ rộng stereo", ""),
    "truong_thu": ("Điệu thức", ""), "nhip": ("Số phách/ô nhịp", ""),
    "quang_giong": ("Loại giọng", ""), "ho_the_loai": ("Họ thể loại", ""),
    "the_loai_chinh": ("Thể loại chính", ""), "tong": ("Tông", ""),
    "nhip_nhap_nhang": ("Nhịp nhấp nhô", ""),
}

TIGHT = {"CHẶT": '<b class="ok">BẮT BUỘC</b>',
         "vừa": '<b style="color:#B5731F">NÊN THEO</b>',
         "rộng": '<span style="color:#7A6F68">TỰ DO</span>'}


def stage_table(keys):
    out = []
    for k in keys:
        nm, unit = LABEL.get(k, (k, ""))
        if k in SPEC:
            s = SPEC[k]
            rng = (f'{vn(s["p25"], 3)} &ndash; {vn(s["p75"], 3)}'
                   if abs(s["median"]) < 10 else
                   f'{vn(s["p25"], 1)} &ndash; {vn(s["p75"], 1)}')
            med = vn(s["median"], 3) if abs(s["median"]) < 10 else vn(s["median"], 1)
            cls = ' class="hi"' if s["tightness"] == "CHẶT" else ""
            out.append(f'<tr{cls}><td>{nm}'
                       + (f' <span style="color:#7A6F68;font-size:7.5pt">{unit}</span>' if unit else "")
                       + f'<br><span style="font-size:6.5pt;color:#8A7F76"><code>{k}</code></span></td>'
                       f'<td class="n"><b>{med}</b></td><td class="n">{rng}</td>'
                       f'<td class="c">{TIGHT[s["tightness"]]}</td></tr>')
        elif k in CATS:
            c = CATS[k]
            dist = " · ".join(f"{kk} {vn(vv, 0)}%" for kk, vv in
                              list(c["distribution"].items())[:3])
            cls = ' class="hi"' if c["is_convention"] else ""
            out.append(f'<tr{cls}><td>{nm}<br>'
                       f'<span style="font-size:6.5pt;color:#8A7F76"><code>{k}</code></span></td>'
                       f'<td class="n"><b>{c["dominant"]}</b></td>'
                       f'<td class="n" style="font-size:7.5pt">{dist}</td>'
                       f'<td class="c">'
                       + ('<b class="ok">QUY ƯỚC</b>' if c["is_convention"]
                          else '<span style="color:#7A6F68">TỰ DO</span>')
                       + '</td></tr>')
    return "\n".join(out)


stages_html = ""
for key, ks in R["by_stage"].items():
    if not ks:
        continue
    title, desc = STAGE_NAME.get(key, (key, ""))
    stages_html += f"""
<h3>{title}</h3>
<p class="f">{desc}</p>
<table>
<thead><tr><th>Thông số</th><th class="n">Đặt ở</th><th class="n">Khoảng chấp nhận</th>
<th class="c">Mức ràng buộc</th></tr></thead>
<tbody>
{stage_table(ks)}
</tbody></table>"""

must_html = ", ".join(
    f'<b>{LABEL.get(k, (k, ""))[0]}</b> = {vn(SPEC[k]["median"], 3 if abs(SPEC[k]["median"]) < 10 else 1)}'
    for k in R["must_follow"])
free_html = ", ".join(LABEL.get(k, (k, ""))[0] for k in R["free_choice"])
limit_rows = "\n".join(f"<li>{l}</li>" for l in R["_meta"]["limits"])

_v = CATS.get("quang_giong", {})
_g = CATS.get("ho_the_loai", {})
_m = CATS.get("truong_thu", {})

DOC = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size:A4; margin:17mm 15mm 20mm;
 @bottom-center {{ content counter(page) " / " counter(pages);
  font-family:"DejaVu Sans";font-size:8pt;color:#9A8E85; }} }}
body {{ font-family:"DejaVu Sans",sans-serif;font-size:9.5pt;line-height:1.55;color:#1A1614; }}
h1 {{ font-size:23pt;margin:0 0 6pt;letter-spacing:-.4pt; }}
h2 {{ font-size:13pt;margin:20pt 0 7pt;padding-bottom:4pt;
 border-bottom:1.5pt solid #1A1614;page-break-after:avoid; }}
h3 {{ font-size:10.5pt;margin:14pt 0 3pt;color:#8C3A2B;page-break-after:avoid; }}
p {{ margin:6pt 0; }}
.sub {{ color:#6B615A;font-size:10pt;margin:0 0 10pt; }}
.meta {{ font-size:8pt;color:#7A6F68;border-top:.6pt solid #E2DAD1;
 border-bottom:.6pt solid #E2DAD1;padding:6pt 0;margin-bottom:14pt; }}
table {{ border-collapse:collapse;width:100%;font-size:8.5pt;margin:6pt 0 10pt;page-break-inside:avoid; }}
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
.formula {{ background:#F7F4F0;border:.6pt solid #E2DAD1;padding:8pt 11pt;
 font-size:8.5pt;margin:7pt 0;line-height:1.8; }}
.pb {{ page-break-before:always; }}
.f {{ font-size:7.5pt;color:#7A6F68;margin:-1pt 0 5pt; }}
ul {{ margin:6pt 0;padding-left:15pt; }} li {{ margin:3pt 0; }}
</style></head><body>

<h1>Công thức tái tạo nhạc</h1>
<p class="sub">Nhóm video thắng dựng nhạc theo thông số nào &mdash; và chép lại thế nào</p>
<div class="meta">
STEP_04h3 &nbsp;•&nbsp; Mục tiêu: <b>TÁI TẠO</b>, không so sánh thắng/thua
&nbsp;•&nbsp; {C['n_tracks']} track / {C['n_videos']} video / {C['n_channels']} kênh
&nbsp;•&nbsp; ngưỡng &ge; {C['view_threshold']:,.0f} view ({C['view_min']:,} &ndash; {C['view_max']:,})
</div>

<div class="box ok">
<span class="l">Cách đọc báo cáo này</span>
<p>Đây <b>không</b> phải báo cáo so sánh. Nhóm thắng đã biết là ai &mdash; việc còn lại
chỉ là <b>đo xem họ làm gì rồi chép lại</b>. Nên ở đây không có p-value, chỉ có
<b>khoảng thông số</b> và mức ràng buộc.</p>
<p><b class="ok">BẮT BUỘC</b> = cả nhóm thắng làm giống nhau &rarr; lệch là lạc chất ngách.
&nbsp;<b style="color:#B5731F">NÊN THEO</b> = có xu hướng chung.
&nbsp;<span style="color:#7A6F68">TỰ DO</span> = nhóm thắng <b>không</b> thống nhất &rarr;
ép theo một con số là bịa ra ràng buộc không có thật.</p>
</div>

<div class="kpi">
<div><div class="k">Bắt buộc theo</div><div class="v ok">{len(R['must_follow'])}</div>
 <div class="c">thông số cả nhóm làm giống nhau</div></div>
<div><div class="k">Tự do chọn</div><div class="v" style="color:#7A6F68">{len(R['free_choice'])}</div>
 <div class="c">nhóm thắng không thống nhất</div></div>
<div><div class="k">Thể loại</div><div class="v ac">{vn(_g.get('share_pct', 0), 0)}%</div>
 <div class="c">{_g.get('dominant', '—')}</div></div>
<div><div class="k">Điệu thức</div><div class="v">{vn(_m.get('share_pct', 0), 0)}%</div>
 <div class="c">{_m.get('dominant', '—')}</div></div>
</div>

<h2>1. Bản rút gọn &mdash; nếu chỉ nhớ được một dòng</h2>
<div class="formula">
{must_html}
</div>
<p>Năm thông số trên là phần <b>cứng</b> của công thức: mọi bản thắng đều nằm sát
các con số này. Còn lại &mdash; {free_html} &mdash; nhóm thắng
<b>mỗi bản một kiểu</b>, nên cứ chọn theo ý đồ bài hát.</p>

<div class="box crit">
<span class="l">Điểm quan trọng nhất: KHÔNG dùng autotune cứng</span>
<p>Độ lệch cao độ giữ ở <b>{vn(SPEC['lech_cent']['median'], 1)} cent</b>
(khoảng {vn(SPEC['lech_cent']['p25'], 1)}&ndash;{vn(SPEC['lech_cent']['p75'], 1)}) &mdash;
đây là thông số <b>CHẶT</b>, cả nhóm thắng giống nhau.</p>
<p>Bám lưới cao độ chỉ <b>{vn(SPEC['bam_luoi_semitone']['median'] * 100, 0)}%</b>.
Giọng hát <b>cố tình để lệch tự nhiên</b>. Nắn thẳng về 0 cent sẽ ra chất nhạc máy &mdash;
lạc hẳn khỏi ngách này.</p>
</div>

<h2 class="pb">2. Công thức đầy đủ theo khâu sản xuất</h2>
{stages_html}

<h2 class="pb">3. Ba điều dễ làm sai</h2>

<div class="box crit">
<span class="l">1. Đừng ép BPM về một con số</span>
<p>Nhịp độ nhóm thắng trải <b>{vn(SPEC['bpm']['p25'], 0)}&ndash;{vn(SPEC['bpm']['p75'], 0)} BPM</b>
(toàn dải {vn(SPEC['bpm']['min'], 0)}&ndash;{vn(SPEC['bpm']['max'], 0)}) &mdash; xếp loại
<b>TỰ DO</b>. Không có &laquo;BPM chuẩn của ngách&raquo;.</p>
<p>Brief cũ (STEP_04h, dựng từ 5 bản) ghi khoảng <b>51,7&ndash;80,8</b> &mdash;
lệch hẳn về phía chậm và <b>không đại diện</b>. Bỏ con số đó.</p>
</div>

<div class="box">
<span class="l">2. Tỉ trọng nhạc cụ là TỈ LỆ, không phải mức âm lượng</span>
<p>Năm giá trị stem cộng lại &asymp; 1. Tăng trống thì thứ khác <b>buộc phải giảm</b>.
Đọc bảng phối khí như &laquo;chia phần chiếc bánh&raquo;, đừng chỉnh từng fader theo
con số tuyệt đối.</p>
<p>Trật tự nhóm thắng: <b>giọng {vn(SPEC['stem_vocals']['median'], 2)}</b> &gt;
bass {vn(SPEC['stem_bass']['median'], 2)} &gt; trống {vn(SPEC['stem_drums']['median'], 2)}
&gt; ghi-ta {vn(SPEC['stem_guitar']['median'], 2)} &gt; piano {vn(SPEC['stem_piano']['median'], 2)}.
<b>Giọng hát luôn đứng đầu</b> &mdash; khớp với kết luận &laquo;nhạc CÓ LỜI&raquo; ở STEP_04h.</p>
</div>

<div class="box">
<span class="l">3. Công thức mô tả, không bảo đảm</span>
<p>Đây là <b>ảnh chụp cách nhóm thắng đang làm</b>. Làm đúng mọi thông số
<b>không</b> đảm bảo thắng &mdash; nhạc chỉ là một phần; tiêu đề, thumbnail, thời điểm
đăng đều tác động. Công thức này giúp bạn <b>không lạc chất ngách</b>, không thay thế
các yếu tố kia.</p>
</div>

<h2>4. Giới hạn</h2>
<ul>
{limit_rows}
</ul>
<p class="f">Phương pháp: {R['_meta']['method']} ·
Quy tắc phân loại ràng buộc: {R['_meta']['tightness_rule']} ·
Vì sao không có p-value: {R['_meta']['why_no_pvalue']}</p>

</body></html>"""

HTML(string=DOC).write_pdf(OUT)
print(f"✅ {OUT}")
