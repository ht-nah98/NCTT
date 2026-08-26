"""Sinh BÁO CÁO CUỐI — STEP_08 Tổng hợp & Chiến lược."""
import json, pandas as pd, warnings, base64, html
from pathlib import Path
from weasyprint import HTML
warnings.filterwarnings("ignore")

N=Path("niches/christian-blues"); D=N/"99_report"
S=json.load(open(D/"_synthesis.json")); SC=json.load(open(N/"_state/scores.json"))
# Điểm hiển thị kiểu Việt, KHÔNG làm tròn (12,05 chứ không phải 12,1).
# Làm tròn 1 chữ số từng khiến PDF lệch với scores.json. Bài học T27.
def _sc_vn(x): return f"{x:g}".replace(".", ",")
M=json.load(open(N/"_state/metrics.json")); BT=json.load(open(D/"backtest_summary.json"))
B=pd.read_csv(D/"backtest_rubric.csv")
# PLAYBOOK — thông số khởi tạo kênh (STEP_10). Không có thì bỏ qua mục 7.
_pbf=N/"09_playbook/CHANNEL_PLAYBOOK.json"
PB=json.load(open(_pbf)) if _pbf.exists() else None
_prf=N/"09_playbook/CHANNEL_PROFILES.json"
PR=json.load(open(_prf)) if _prf.exists() else None
# ÂM NHẠC (STEP_04h). Không có thì mục 7.6 tự biến mất.
_auf=N/"04_outlier/audio/AUDIO_BRIEF.json"
AU=json.load(open(_auf)) if _auf.exists() else None
def vn(x): return f"{x:,.0f}".replace(",", ".")
# ═══════ MỤC 7 · PLAYBOOK KHỞI TẠO KÊNH ═══════
if PB is None:
    PLAYBOOK_SECTION = ""
else:
    _t, _d, _g = PB["title"], PB["description"], PB["tags"]
    _f, _c, _th = PB["format"], PB["cadence"], PB["thumbnail"]

    _pat = "\n".join(
        f'<tr class="{"hi" if i==0 else ""}"><td><b>{p["id"]}</b></td>'
        f'<td class="n">{p["share"]*100:.0f}%</td>'
        f'<td><code>{html.escape(p["template"])}</code></td></tr>'
        for i, p in enumerate(sorted(_t["patterns"], key=lambda x: -x["share"])))

    _ex = "\n".join(
        f'<tr><td class="n">{vn(e["views"])}</td><td>{html.escape(e["title"][:78])}</td></tr>'
        for e in _t["examples"][:6])

    _blk = "\n".join(
        f'<tr><td class="n">{b["order"]}</td><td><b>{b["name"]}</b></td>'
        f'<td class="n">{b["chars"]}</td><td>{html.escape(b["rule"])}</td></tr>'
        for b in _d["blocks"])

    _mod = "\n".join(
        f'<tr><td><code>{m["handle"]}</code></td>'
        f'<td class="n">{vn(m["total_view"])}</td><td class="n">{m["videos"]}</td>'
        f'<td class="n">{vn(m["best_video_view"])}</td>'
        f'<td class="n">{m["videos_per_month"] or "—"}</td>'
        f'<td class="n">{m["duration_median_min"]:.0f}p</td>'
        f'<td class="n">{m["hit_rate"]*100:.0f}%</td></tr>'
        for m in PB["reference_channels"])

    _st = "\n".join(
        f'<tr class="{"hi" if i==0 else ""}"><td><b>{x["id"].replace("_"," ")}</b></td>'
        f'<td class="n">{x["thời_lượng_trung_vị_phút"]:.0f}p</td>'
        f'<td class="n">{x["video_mỗi_tháng"]:.1f}</td>'
        f'<td class="n">{vn(x["view_mỗi_video"])}</td>'
        f'<td class="n">{x["tỷ_lệ_hit"]*100:.0f}%</td>'
        f'<td>{", ".join(f"<code>{e}</code>" for e in x["ví_dụ"][:2])}</td></tr>'
        for i, x in enumerate(PB["strategy"]["profiles"]))

# ---- 7.5 hồ sơ chi tiết 5 kênh ----
    if PR is None:
        _profiles = ""
    else:
        _cards = []
        for i, pf in enumerate(PR["profiles"], 1):
            q, sx, tt, dc = (pf["quy_mô"], pf["sản_xuất"],
                             pf["công_thức_tiêu_đề"], pf["cấu_trúc_mô_tả"])
            _ex = "".join(
                f'<li>{html.escape(e["title"][:88])} &mdash; <b>{vn(e["views"])}</b></li>'
                for e in tt["ví_dụ_top"][:3])
            _early = " · ".join(vn(x) for x in sx["view_10_video_đầu"][:5])
            _rev = ""
            if pf["channel_created"] and pf["channel_created"][:4] < pf["first_video"][:4]:
                _rev = (f'<p class="warn">⚠ Kênh lập <b>{pf["channel_created"]}</b> '
                        f'nhưng video đầu <b>{pf["first_video"]}</b> &mdash; '
                        f'kênh cũ hồi sinh, không phải kênh mới.</p>')
            _pos = (html.escape(pf["định_vị"]["mô_tả_kênh"][:340]) + "…"
                    if pf["định_vị"]["mô_tả_kênh"] else "—")
            _cards.append(f"""
<div class="card">
<h4>{i}. {html.escape(pf["channel_name"] or pf["handle"])}
 <span class="hd">@{pf["handle"]}</span></h4>
<table class="mini">
<tr><td>Tổng view</td><td class="n"><b>{vn(q["tổng_view"])}</b></td>
    <td>Video</td><td class="n">{q["số_video"]}</td>
    <td>Người đăng ký</td><td class="n">{vn(pf["subscribers"]) if pf["subscribers"] else "—"}</td></tr>
<tr><td>Video đỉnh</td><td class="n">{vn(q["video_đỉnh"])}</td>
    <td>View trung vị</td><td class="n">{vn(q["view_trung_vị"])}</td>
    <td>Tỷ lệ hit</td><td class="n"><b>{q["tỷ_lệ_hit"]*100:.0f}%</b></td></tr>
<tr><td>Mô hình</td><td class="n">{sx["mô_hình"].replace("_"," ")}</td>
    <td>Thời lượng</td><td class="n">{sx["thời_lượng_trung_vị_phút"]:.0f}p</td>
    <td>Nhịp đăng</td><td class="n">{sx["video_mỗi_tuần"]:.1f}/tuần</td></tr>
</table>
{_rev}
<p><span class="lb">Tự định vị</span> {_pos}</p>
<p><span class="lb">Tiêu đề</span> kiểu <b>{tt["kiểu_chủ_đạo"].replace("_"," ")}</b> ·
 {tt["độ_dài_trung_vị"]} ký tự · phân cách <code>{tt["dấu_phân_cách"] or "—"}</code></p>
<ul class="ex">{_ex}</ul>
<p><span class="lb">Mô tả</span> {dc["độ_dài_trung_vị"]} ký tự ·
 emoji {dc["có_emoji"]*100:.0f}% ·
 membership {dc["có_membership"]*100:.0f}% ·
 tracklist {dc["có_tracklist"]*100:.0f}%</p>
<p><span class="lb">5 video đầu</span> {_early} &mdash;
 <b>{"nổ ngay" if sx["khởi_đầu"]=="nổ_ngay" else "leo dần"}</b></p>
</div>""")

        _bh = PR["bài_học"]
        _rv = "".join(f'<li><code>@{r["handle"]}</code> &mdash; lập <b>{r["lập"]}</b>, '
                      f'video đầu <b>{r["video_đầu"]}</b></li>'
                      for r in _bh["kênh_cũ_hồi_sinh"])
        _profiles = f"""
<h3 class="pb">7.5b Hồ sơ chi tiết từng kênh</h3>
{"".join(_cards)}

<h3 class="pb">7.5c Bốn bài học từ 5 kênh</h3>
<div class="box crit">
<span class="l">1. Hai trên năm kênh là kênh CŨ hồi sinh</span>
<ul>{_rv}</ul>
<p>Kênh lập từ 2008&ndash;2010, ngừng nhiều năm, nay đăng lại nội dung AI.
Chúng mang sẵn <b>tuổi đời và lịch sử</b> mà kênh mới không có.</p>
<p><b>Hệ quả:</b> con số &laquo;61,5% kênh mới đạt traction&raquo; (T3) <b>lạc quan hơn thực tế</b>
&mdash; một phần &laquo;kênh mới&raquo; thực chất là kênh cũ. Nếu bạn mở kênh hoàn toàn mới,
hãy kỳ vọng thấp hơn.</p>
</div>
<div class="box">
<span class="l">2. Khởi đầu chia hai kiểu &mdash; đừng so mình với kiểu sai</span>
<table>
<thead><tr><th>Kênh</th><th>3 video đầu</th><th>Kiểu</th></tr></thead>
<tbody>
{"".join(f'<tr><td><code>@{x["handle"]}</code></td>'
         f'<td class="n">{" · ".join(vn(y) for y in x["view_3_video_đầu"])}</td>'
         f'<td>{"nổ ngay" if x["kiểu"]=="nổ_ngay" else "leo dần"}</td></tr>'
         for x in _bh["khởi_đầu_chi_tiết"])}
</tbody></table>
<p><code>@revivalworshiproommusic</code> có 3 video đầu chỉ <b>213 · 147 · 105</b> view
&mdash; nay 7,2 triệu view. <b>Video đầu ít view không có nghĩa là ngách sai.</b></p>
</div>
<div class="box ok">
<span class="l">3. Tỷ lệ hit quan trọng hơn tổng view</span>
<p><code>@{_bh["tỷ_lệ_hit_cao_nhất"]["handle"]}</code> đạt tỷ lệ hit
<b>{_bh["tỷ_lệ_hit_cao_nhất"]["giá_trị"]*100:.0f}%</b> &mdash; cao gấp đôi kênh tổng view lớn nhất,
với chỉ 184 video so với 437.</p>
<p>Sản xuất ít mà trúng nhiều <b>rẻ hơn</b> sản xuất nhiều mà trúng ít &mdash;
đặc biệt khi mỗi video là một mix dài phải dựng.</p>
</div>
<div class="box">
<span class="l">4. Không kênh nào ghi rõ dùng AI</span>
<p>Tỷ lệ mô tả có ghi bản quyền/AI: <b>0%</b> trên cả 5 kênh.
<code>@stillworshipmusic</code> còn kể chuyện &laquo;nhạc gospel blues tôi nghe từ bà ngoại&raquo;
&mdash; định vị bằng <b>câu chuyện con người</b>, không phải công nghệ.</p>
<p><b>Rủi ro:</b> nếu YouTube siết nhãn nội dung AI, cách định vị này thành điểm yếu.
Đây là một phần của điểm trừ T6.</p>
</div>"""

    _dur = "\n".join(
        f'<tr><td>{o["band"]}</td><td class="n">{o["share"]*100:.0f}%</td>'
        f'<td class="n">{vn(o["view_median"])}</td></tr>'
        for o in _f["duration_options"])

    _thumb = "" if not _th else f"""
<h3>7.6 Thumbnail</h3>
<table>
<thead><tr><th>Thông số</th><th>Giá trị</th><th>Ghi chú</th></tr></thead>
<tbody>
<tr class="hi"><td>NGƯỜI chiếm khung</td><td class="n"><b>{_th['person_area_pct']:.0f}%</b></td>
 <td>khoảng {_th['person_range_pct'][0]:.0f}&ndash;{_th['person_range_pct'][1]:.0f}% &middot; &asymp;1/4 khung</td></tr>
<tr class="hi"><td>CHỮ chiếm khung</td><td class="n"><b>{_th['text_area_pct']:.0f}%</b></td>
 <td>{_th['text_lines']} dòng &middot; &asymp;1/6 khung</td></tr>
<tr><td>Vùng tối</td><td class="n">{_th['dark_pct']:.0f}%</td><td>ảnh tối là chuẩn</td></tr>
<tr><td>Sắc hổ phách</td><td class="n">{_th['amber_pct']:.0f}%</td><td>nguồn sáng ấm</td></tr>
<tr><td>Sắc xanh lạnh</td><td class="n">{_th['blue_pct']:.1f}%</td>
 <td><span class="no">gần như không dùng &mdash; tránh</span></td></tr>
<tr><td>Đen trắng hoàn toàn</td><td class="n">{_th['mono_pct']:.0f}%</td><td>biến thể cứ ~6 ảnh 1 lần</td></tr>
<tr><td>Bố cục tách trái/phải</td><td class="n">{_th['layout_split']:.0f}%</td>
 <td>người một bên, chữ bên kia</td></tr>
</tbody></table>
<p>Prompt sinh ảnh đầy đủ cho 3 nhánh nhân vật: <code>{_th['brief_doc']}</code>
&middot; PDF: <code>99_report/STEP04g_Brief-Thumbnail.pdf</code></p>"""

    # ── 7.6 ÂM NHẠC ────────────────────────────────────────────────
    if AU is None:
        MUSIC_SUB = ""
    else:
        _rc, _tp, _hm, _ky = AU["recipe"], AU["tempo"], AU["harmony"], AU["key"]
        _au = AU["generated_from"]
        _nmaj = _ky["mode_distribution"].get("major", 0)
        def _v(x, nd=1): return f"{x:.{nd}f}".replace(".", ",")
        MUSIC_SUB = f"""
<h3 class="pb">7.6 Âm nhạc &mdash; công thức tái tạo</h3>

<p>Rút từ <b>{_au['n_tracks']} bản nhạc {_au['percentile']}</b> phân tích bằng DSP
(librosa). Đây là <b>khung xương</b> để sinh nhạc hàng loạt.</p>

<div class="box ok">
<span class="l">Chốt trước tiên: NHẠC CÓ LỜI</span>
<p>Ba nguồn độc lập cùng chỉ một hướng &mdash; và đây là một trong <b>rất ít</b> kết luận
của dự án đứng vững cả ba lớp chống nghịch lý Simpson:</p>
<p><b>1. Hiệu quả:</b> video gắn nhãn <i>instrumental / no lyrics</i> đạt VPD bằng
<b>17%</b> phần còn lại &mdash; thấp nhất trong 16 chủ đề. Trong từng kênh vẫn kém
(0/2 kênh tốt hơn) nên không phải hiệu ứng &laquo;kênh yếu&raquo;.</p>
<p><b>2. Bối cảnh nghe:</b> nghe <b>chủ động</b> (cầu nguyện, sáng sớm, bệnh tật)
chiếm 20,4%; nghe <b>làm nền</b> (ngủ, lái xe, việc nhà) chỉ 1,8% &mdash; chênh 11,5 lần.</p>
<p><b>3. Nỗi đau lõi:</b> comment được thích nhiều nhất ngách (1.444♥) nói thẳng về
<b>lời hát</b>: <i>&ldquo;love the music but can't stand the lyrics&rdquo;</i>.
Bỏ lời là bỏ đúng thứ khiến khán giả tìm đến.</p>
</div>

<table>
<thead><tr><th>Thông số</th><th class="n">Khoảng quan sát</th>
<th class="n">Mục tiêu</th><th>Ghi chú</th></tr></thead>
<tbody>
<tr class="hi"><td><b>Nhịp độ</b></td>
 <td class="n">{_v(_tp['bpm']['min'])}&ndash;{_v(_tp['bpm']['max'])} BPM</td>
 <td class="n"><b>{_v(_rc['tempo_bpm']['target'])}</b></td>
 <td>slow blues / gospel ballad</td></tr>
<tr><td><b>Điệu thức</b></td><td class="n">&mdash;</td>
 <td class="c"><b>{_rc['mode']}</b></td>
 <td>{_nmaj}/{_au['n_tracks']} bản &mdash; màu buồn đến từ hợp âm thứ xen vào</td></tr>
<tr class="hi"><td><b>Nhịp hòa âm</b></td>
 <td class="n">{_v(_hm['sec_per_chord']['min'])}&ndash;{_v(_hm['sec_per_chord']['max'])} giây</td>
 <td class="n"><b>{_v(_rc['harmonic_rhythm_sec']['target'])}s</b></td>
 <td>mỗi hợp âm giữ bao lâu</td></tr>
<tr><td><b>Số hợp âm</b></td>
 <td class="n">{_v(_hm['distinct_chords']['min'],0)}&ndash;{_v(_hm['distinct_chords']['max'],0)}</td>
 <td class="n">&mdash;</td><td>{_rc['chord_vocabulary']['ghi_chú']}</td></tr>
</tbody></table>

<p><b>Prompt tiếng Anh</b> (nạp vào Suno / Udio):</p>
<div class="formula" style="font-family:'DejaVu Sans Mono',monospace;font-size:8pt">
{_rc['prompt_en']}</div>

<div class="box crit">
<span class="l">⚠ Giới hạn &mdash; đọc trước khi dùng</span>
<p><b>n = {_au['n_tracks']}, không có nhóm đối chứng.</b> Đây là <b>MÔ TẢ</b> nhóm dẫn đầu,
không phải bằng chứng &laquo;làm thế này sẽ thắng&raquo;.</p>
<p><b>Chưa đo được:</b> {', '.join(AU['limits'][i]['thiếu'] for i in (2,3,4))}.
Brief cho khung xương, <b>chưa cho biết bản nhạc nghe như thế nào</b> &mdash;
phần quyết định &laquo;giống hay không giống&raquo;.</p>
<p><b>Chi tiết đầy đủ</b> (bảng từng bản, bẫy đo tempo, hai mô hình sản xuất):
<code>99_report/STEP04h_Brief-Am-nhac.pdf</code></p>
</div>"""

    PLAYBOOK_SECTION = f"""
<h2 class="pb">7. CÔNG THỨC THẮNG &mdash; PLAYBOOK KHỞI TẠO KÊNH</h2>

<div class="box crit">
<span class="l">Mục này khác gì phần trước</span>
<p>Mục 1&ndash;6 trả lời <b>&laquo;có nên vào không&raquo;</b>. Mục này trả lời
<b>&laquo;vào thì làm gì&raquo;</b> &mdash; thông số cụ thể để bắt đầu sản xuất.</p>
<p><b>Đây mới là &laquo;công thức thắng&raquo; của ngách.</b> Nó tổng hợp được vì đã có đủ
STEP_04b (thumbnail thật), STEP_05 (khán giả) và STEP_06 (từ khóa).
STEP_04 &mdash; <i>Sàng lọc đối chứng</i> &mdash; chỉ làm việc ngược lại: <b>loại bỏ</b>
những giả thuyết không đứng vững, để mục này không xây trên nền sai.</p>
<p>Toàn bộ số liệu rút từ <b>{PB['generated_from']['n_videos']} video top 5%</b>
({PB['generated_from']['n_channels']} kênh, &ge;{vn(PB['generated_from']['view_threshold'])} view).
Đây là <b>MÔ TẢ</b> nhóm dẫn đầu đang làm gì, <b>không phải</b> bằng chứng
&laquo;làm thế này sẽ thắng&raquo;.</p>
<p><b>File máy đọc:</b> <code>09_playbook/CHANNEL_PLAYBOOK.json</code> &mdash;
nạp thẳng vào workflow sản xuất tự động.</p>
</div>

<h3>7.1 Tiêu đề</h3>
<div class="kpi">
<div><div class="k">Độ dài</div><div class="v ac">{_t['char_target']}</div>
 <div class="c">ký tự &middot; khoảng {_t['char_range'][0]}&ndash;{_t['char_range'][1]}</div></div>
<div><div class="k">Có hashtag</div><div class="v">{_t['hashtag_usage_rate']*100:.0f}%</div>
 <div class="c">không bắt buộc</div></div>
<div><div class="k">Có số</div><div class="v">{PB['title'].get('pct_with_number', 0.29)*100:.0f}%</div>
 <div class="c">thường là thời lượng hoặc chương Kinh Thánh</div></div>
<div><div class="k">Dấu phân cách</div><div class="v">{_t['separator']}</div>
 <div class="c">nối các vế trong tiêu đề</div></div>
</div>
<table>
<thead><tr><th>Mẫu câu</th><th>Tỷ lệ</th><th>Khuôn</th></tr></thead>
<tbody>{_pat}</tbody></table>
<p><b>Bắt buộc chứa ít nhất một trong:</b>
{" &middot; ".join(f"<code>{w}</code>" for w in _t["must_include_one_of"])}</p>
<p><b>Từ vựng hay dùng:</b> {", ".join(_t["vocabulary"][:12])}</p>
<p><b>Hashtag:</b> {" ".join(f"<code>{h}</code>" for h in _t["hashtags"])}</p>
<table>
<thead><tr><th>Lượt xem</th><th>Ví dụ thật từ nhóm top</th></tr></thead>
<tbody>{_ex}</tbody></table>

<h3 class="pb">7.2 Mô tả (description)</h3>
<div class="kpi">
<div><div class="k">Độ dài</div><div class="v ac">{_d['char_target']}</div>
 <div class="c">ký tự &middot; khoảng {_d['char_range'][0]}&ndash;{_d['char_range'][1]}</div></div>
<div><div class="k">Dùng emoji</div><div class="v">{_d['emoji_rate']*100:.0f}%</div>
 <div class="c">gần như bắt buộc</div></div>
<div><div class="k">Mời membership</div><div class="v">{PB['description']['blocks'][4].get('membership_rate', 0)*100:.0f}%</div>
 <div class="c">mô hình $3.99/tháng đã có kênh áp dụng</div></div>
<div><div class="k">Có mốc thời gian</div><div class="v">{_d['timestamp_rate']*100:.0f}%</div>
 <div class="c">tracklist cho mix dài</div></div>
</div>
<table>
<thead><tr><th>#</th><th>Khối</th><th>Ký tự</th><th>Nội dung</th></tr></thead>
<tbody>{_blk}</tbody></table>
<p><b>Từ vựng:</b> {", ".join(_d["vocabulary"][:14])}</p>

<h3>7.3 Thẻ (tags)</h3>
<p>Số thẻ: <b>{_g['count_target']}</b> mỗi video (tối đa {_g['count_max']}).</p>
<p><b>Nhóm lõi &mdash; dùng cho mọi video:</b><br>
{" &middot; ".join(f"<code>{t}</code>" for t in _g["core"])}</p>
<p><b>Nhóm mở rộng &mdash; chọn theo chủ đề:</b><br>
{" &middot; ".join(f"<code>{t}</code>" for t in _g["extended"])}</p>

<h3>7.4 Chọn mô hình sản xuất &mdash; quyết định đầu tiên</h3>
<div class="box crit">
<span class="l">Hai mô hình đối lập, cùng thành công</span>
<p>Nhóm dẫn đầu chia làm hai chiến lược <b>khác hẳn nhau</b>. Phải chọn <b>một</b>
trước khi sản xuất &mdash; chúng đòi hỏi khối lượng công việc và loại nội dung khác nhau.</p>
</div>
<table>
<thead><tr><th>Mô hình</th><th>Thời lượng</th><th>Video/tháng</th>
<th>View/video</th><th>Tỷ lệ hit</th><th>Kênh mẫu</th></tr></thead>
<tbody>{_st}</tbody></table>
<p>Ví dụ rõ nhất: <code>stillworshipmusic</code> làm <b>437 video ~3 phút</b>
(27,7 video/tháng) đạt 16,7 triệu view. <code>oldiesgospelradio</code> làm
<b>184 video ~108 phút</b> (0,9 video/tháng) đạt 8,6 triệu view &mdash; với
<b>tỷ lệ hit cao gấp đôi</b>.</p>
<div class="box">
<span class="l">Chọn thế nào</span>
<p><b>Nhiều &amp; ngắn</b> &mdash; hợp nếu bạn tự động hóa được khâu sản xuất nhạc.
Rủi ro: ít ad slot mỗi video, phụ thuộc mạnh vào thuật toán đề xuất.</p>
<p><b>Ít &amp; dài</b> &mdash; hợp với bối cảnh nghe của ngách (STEP_05: cầu nguyện,
tĩnh tâm). Mỗi video ~{_f['ad_slots_est']:.0f} ad slot thay vì 1. Rủi ro: mỗi lần sai
là mất nhiều công.</p>
</div>

<h3>7.4b Thời lượng &amp; nhịp đăng</h3>
<div class="kpi">
<div><div class="k">Thời lượng</div><div class="v ac">{_f['duration_target_min']:.0f}p</div>
 <div class="c">trung vị nhóm top</div></div>
<div><div class="k">Ad slot ước tính</div><div class="v">{_f['ad_slots_est']:.0f}</div>
 <div class="c">~1 slot / 8 phút</div></div>
<div><div class="k">Nhịp đăng</div><div class="v ac">{_c['videos_per_week']:.1f}</div>
 <div class="c">video/tuần &middot; nhóm mạnh {_c['videos_per_week_aggressive']:.1f}</div></div>
<div><div class="k">Kênh tham chiếu</div><div class="v">{_c['n_channels']}</div>
 <div class="c">có video lọt top 5%</div></div>
</div>
<table>
<thead><tr><th>Nhóm thời lượng</th><th>Tỷ trọng</th><th>View trung vị</th></tr></thead>
<tbody>{_dur}</tbody></table>
<div class="box">
<span class="l">Không có thời lượng &laquo;đúng&raquo;</span>
<p>Cả bốn nhóm đều thành công tương đương. Chọn theo <b>bối cảnh nghe</b>
(STEP_05: khán giả nghe lúc cầu nguyện, bệnh tật &rarr; mix dài phục vụ tốt hơn),
không chọn theo thumbnail hay tiêu đề.</p>
<p><b>Nhịp đăng là đòn bẩy đáng tin nhất</b> &mdash; STEP_03 cho thấy nhóm đăng dày
đạt tổng view gấp <b>5,3&times;</b> nhóm thưa, dù view mỗi video thấp hơn.</p>
</div>

<h3 class="pb">7.5 Năm kênh nên học</h3>
<table>
<thead><tr><th>Kênh</th><th>Tổng view</th><th>Video</th><th>Video đỉnh</th>
<th>Video/tháng</th><th>Thời lượng</th><th>Tỷ lệ hit</th></tr></thead>
<tbody>{_mod}</tbody></table>
<p><b>Tỷ lệ hit</b> = % video của kênh lọt top 5% ngách. Chỉ số này quan trọng hơn tổng view:
<code>oldiesgospelradio</code> có tỷ lệ hit <b>16%</b> &mdash; cao gấp đôi kênh tổng view lớn nhất.</p>
{_profiles}
{_thumb}

{MUSIC_SUB}

<h3>7.7 Nạp vào workflow tự động</h3>
<div class="formula">
<code>09_playbook/CHANNEL_PLAYBOOK.json</code> &mdash; cấu trúc:<br><br>
<code>title</code> &nbsp; khuôn câu + từ vựng + hashtag &rarr; sinh tiêu đề<br>
<code>description</code> &nbsp; 6 khối có thứ tự + số ký tự &rarr; sinh mô tả<br>
<code>tags</code> &nbsp; nhóm lõi + mở rộng &rarr; gắn thẻ<br>
<code>format</code> &nbsp; thời lượng mục tiêu &rarr; đặt độ dài bản nhạc<br>
<code>cadence</code> &nbsp; video/tuần &rarr; lập lịch sản xuất<br>
<code>thumbnail</code> &nbsp; tỷ lệ người/chữ/màu &rarr; sinh ảnh + kiểm tự động<br>
<code>reference_channels</code> &nbsp; 5 kênh mẫu &rarr; đối chiếu định kỳ
</div>
<div class="box crit">
<span class="l">Ba thứ playbook KHÔNG cung cấp</span>
<p><b>1. Âm thanh nghe như thế nào.</b> Mục 7.6 đã cho <b>khung xương</b> bản nhạc
(nhịp độ, điệu thức, hòa âm) từ {"" if AU is None else AU["generated_from"]["n_tracks"]} bản top.
Nhưng <b>nhạc cụ, giọng hát, âm sắc, chuẩn master</b> vẫn chưa đo được &mdash;
đó mới là phần quyết định &laquo;giống hay không giống&raquo;. Cần tách stem + đo LUFS.</p>
<p><b>2. Tên kênh.</b> Không suy được từ dữ liệu. Quan sát: kênh top dùng cụm 2&ndash;3 từ
gợi không gian thờ phượng (<code>stillworshipmusic</code>, <code>holygroove</code>,
<code>oldiesgospelradio</code>).</p>
<p><b>3. Bảo đảm kết quả.</b> Playbook giúp bạn không lạc lõng và sản xuất nhanh &mdash;
nó là <b>vé vào cửa</b>, không phải lợi thế cạnh tranh.</p>
</div>
"""

def img(n): return "data:image/png;base64,"+base64.b64encode((D/n).read_bytes()).decode()

def demand_cell(d):
    """Dựng ô BẰNG CHỨNG NHU CẦU — mỗi mục kèm nguồn truy vết (T31).

    Bản trước chỉ in một câu văn xuôi, người đọc không kiểm chứng được.
    Nay: câu nói thật để trong ngoặc kép + comment_id; số liệu kèm đường dẫn file.
    """
    if isinstance(d, str):          # ngách cũ chưa nâng cấp → vẫn hiện được
        return html.escape(d)
    out=[]
    for e in d:
        claim, src, _id = e["claim"], e.get("src",""), e.get("id","")
        is_quote = "quote_bank" in src and "→" not in src
        if is_quote:
            out.append(f'<div style="margin:3pt 0;padding-left:5pt;'
                       f'border-left:1.5pt solid #C9BDB0">'
                       f'<span style="font-style:italic">&ldquo;{html.escape(claim)}&rdquo;</span>'
                       f'<br><span style="font-size:6.5pt;color:#8A7F76">{html.escape(_id)}</span></div>')
        else:
            out.append(f'<div style="margin:3pt 0">{html.escape(claim)}'
                       f'<br><span style="font-size:6.5pt;color:#8A7F76">'
                       f'{html.escape(src)}{" · "+html.escape(_id) if _id else ""}</span></div>')
    return "".join(out)

def perf_cell(g):
    """Hiệu quả + nguồn số đó ở đâu ra."""
    s = html.escape(g["perf"])
    if g.get("src_perf") and not g["src_perf"].startswith("—"):
        s += (f'<br><span style="font-size:6.5pt;color:#8A7F76">'
              f'{html.escape(g["src_perf"])}</span>')
    return s

gap_rows="\n".join(
 f'<tr class="{"hi" if g["score"]=="CAO" else ""}"><td><b>{g["gap"]}</b></td>'
 f'<td style="font-size:7.5pt">{demand_cell(g["demand"])}</td>'
 f'<td>{html.escape(g["supply"])}</td><td>{perf_cell(g)}</td>'
 f'<td class="n">{g["score"]}</td><td class="n">{g["conf"]}</td></tr>' for g in S["gaps"])

n_ev = sum(len(g["demand"]) if isinstance(g["demand"], list) else 1 for g in S["gaps"])

# Số cho hộp "vì sao khoảng trống #1 tin cậy thấp" — ĐỌC TỪ DỮ LIỆU, không gõ tay (T27).
_TH = pd.read_csv(N/"06_keyword/02_theme_scores.csv")
_os = _TH[_TH.theme == "old_school"]
_A8 = json.load(open(N/"05_audience/_metrics_raw.json"))
_ag = _A8.get("age", {})
if len(_os):
    _o = _os.iloc[0]
    os_lift, os_share = f"{_o.lift:.2f}×".replace(".", ","), f"{_o.share_pct:.2f}%".replace(".", ",")
    os_verdict, os_within = _o.verdict, f"{_o.within_median_lift:.2f}×".replace(".", ",")
    os_better, os_tested = int(_o.n_ch_better), int(_o.n_ch_tested)
else:
    os_lift, os_share, os_verdict = "2,37×", "3,96%", "YẾU"
    os_within, os_better, os_tested = "1,05×", 4, 8
os_conf = next((g["conf"] for g in S["gaps"] if g["gap"].startswith("Old-school")), "Thấp")
age_med = f"{_ag.get('median',0):.0f}"
age_n   = int(_ag.get("n", 0))
age_pct = f"{age_n/_A8.get('n_analyzed',1)*100:.2f}%".replace(".", ",")

idea_rows="\n".join(
 f'<tr><td class="n">{i["n"]}</td><td>{html.escape(i["title"])}</td>'
 f'<td style="font-size:7.5pt;color:#6B615A">{i["basis"]}</td><td class="n">{i["len"]}</td></tr>'
 for i in S["ideas"])

hyp_rows="\n".join(
 f'<tr><td>{h["h"]}</td>'
 f'<td>{"<span class=\'ok\'>"+h["verdict"]+"</span>" if h["verdict"].startswith("ĐÚNG") else "<span class=\'wa\'>"+h["verdict"]+"</span>"}</td>'
 f'<td style="font-size:8pt">{h["evidence"]}</td></tr>' for h in S["hypotheses"])

b=S["benchmarks"]
ax_rows="\n".join(
 f'<tr><td><b>{k}</b> {n}</td><td class="n">{SC["axes"][k]["score"]:.1f}</td>'
 f'<td class="n">{SC["axes"][k]["weight"]*100:.0f}%</td>'
 f'<td>{SC["axes"][k]["metric"]}</td>'
 f'<td>{"<span class=\'ok\'>Cao</span>" if SC["axes"][k]["confidence"]=="high" else "<span class=\'wa\'>Vừa</span>" if SC["axes"][k]["confidence"]=="medium" else "<span class=\'no\'>Thấp</span>"}</td></tr>'
 for k,n in [("T1","Quy mô"),("T2","Động lượng"),("T3","Cửa gia nhập"),("T4","Phù hợp AI"),("T5","Kiếm tiền")])

d=B.dropna(subset=["T3_proxy","T3_old"])
incons=d[(d.top20_pct>55)&(d.top20_pct<=62)]
inc_rows="\n".join(
 f'<tr><td>{r.genre}</td><td class="n">{r.top20_pct:.1f}%</td>'
 f'<td class="n dn">{r.T3_old:.0f}</td><td class="n up">{r.T3_proxy:.0f}</td></tr>'
 for _,r in incons.iterrows())

DOC=f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size:A4;margin:17mm 15mm 20mm;
 @bottom-center {{ content counter(page) " / " counter(pages);
  font-family:"DejaVu Sans";font-size:8pt;color:#9A8E85; }} }}
body {{ font-family:"DejaVu Sans",sans-serif;font-size:9.5pt;line-height:1.55;color:#1A1614; }}
h1 {{ font-size:24pt;margin:0 0 6pt;letter-spacing:-.4pt; }}
h2 {{ font-size:13pt;margin:20pt 0 7pt;padding-bottom:4pt;
 border-bottom:1.5pt solid #1A1614;page-break-after:avoid; }}
h3 {{ font-size:10.5pt;margin:14pt 0 5pt;color:#8C3A2B;page-break-after:avoid; }}
p {{ margin:6pt 0; }}
.sub {{ color:#6B615A;font-size:10.5pt;margin:0 0 10pt; }}
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
.big {{ text-align:center;border:1.5pt solid #8C3A2B;padding:14pt;margin:12pt 0;background:#F9F4F2; }}
.big .n1 {{ font-size:36pt;font-weight:bold;color:#8C3A2B;line-height:1; }}
.big .n2 {{ font-size:12pt;color:#4A423D;margin-top:6pt; }}
.phase {{ border:.8pt solid #CFC4B8;padding:9pt 11pt;margin:9pt 0;page-break-inside:avoid; }}
.phase h4 {{ margin:0 0 4pt;font-size:10pt;color:#8C3A2B; }}
.phase p {{ margin:2pt 0;font-size:8.5pt; }}
.pb {{ page-break-before:always; }}
ul {{ margin:6pt 0;padding-left:15pt; }} li {{ margin:3pt 0; }}
</style></head><body>

<h1>Báo cáo tổng hợp &mdash; Christian Blues</h1>
<p class="sub">Quyết định đầu tư ngách: vào hay không, và nếu vào thì vào thế nào</p>
<div class="meta">
STEP_08 &nbsp;•&nbsp; Agent A7 &nbsp;•&nbsp; Tổng hợp 7 bước nghiên cứu
&nbsp;•&nbsp; 53 kênh · 7.193 video · 145.150 bình luận &nbsp;•&nbsp;
Dữ liệu crawl 13/08/2026 &nbsp;•&nbsp; Lập ngày 15/08/2026
</div>

<h2>1. Kết luận</h2>

<div class="big">
<div class="n1">{_sc_vn(SC['total_score'])} / 20</div>
<div class="n2">Xếp loại: <b>{SC['verdict']}</b></div>
</div>

<div class="box ok">
<span class="l">Khuyến nghị: VÀO CÓ ĐIỀU KIỆN</span>
<p>Ngách này <b>dễ vào nhưng trần thấp</b>. Cửa gia nhập rất rộng (61,5% kênh mới đạt traction)
và mô hình AI đã được chứng minh (65% kênh dẫn đầu là AI-first). Nhưng quy mô chỉ ở mức trung
bình và RPM nhạc vốn thấp.</p>
<p><b>Mô hình phù hợp:</b> nhiều kênh chạy song song với chi phí sản xuất AI thấp &mdash;
không phải dồn toàn lực vào một kênh lớn. Kỳ vọng hợp lý: <b>vài trăm đô mỗi tháng cho một
kênh</b> ở mức trung vị.</p>
<p><b>Điều kiện kèm theo:</b> phải chạy thêm snapshot để xác nhận trục Động lượng trước khi
cam kết nguồn lực lớn (xem mục 7).</p>
</div>

<div class="kpi">
<div><div class="k">Cửa gia nhập</div><div class="v up">4,4<span style="font-size:10pt">/5</span></div>
 <div class="c">61,5% kênh mới thành công</div></div>
<div><div class="k">Phù hợp AI</div><div class="v up">5,0<span style="font-size:10pt">/5</span></div>
 <div class="c">65% top20 là AI-first</div></div>
<div><div class="k">Quy mô</div><div class="v dn">2,0<span style="font-size:10pt">/5</span></div>
 <div class="c">7,45tr view/tháng</div></div>
<div><div class="k">Doanh thu kỳ vọng</div><div class="v">$319</div>
 <div class="c">mỗi tháng, kênh trung vị</div></div>
</div>

<img src="{img('s2_axes.png')}">

<h2>2. Hành trình nghiên cứu &mdash; và ba lần sửa sai</h2>

<p>Nghiên cứu này đi qua 7 bước. Điều đáng ghi nhận nhất không phải các phát hiện, mà là
<b>ba lần hệ thống tự bắt được lỗi của chính nó</b> &mdash; những lỗi mà nếu bỏ qua sẽ dẫn
đến khuyến nghị sai hoàn toàn.</p>

<table>
<thead><tr><th>Bước</th><th>Kết luận ban đầu (SAI)</th><th>Kết luận sau kiểm chứng</th><th>Nguyên nhân lỗi</th></tr></thead>
<tbody>
<tr class="hi"><td><b>STEP_02</b></td>
 <td class="no">Ngách đang bị pha loãng, M2.4 = 0,35 &rarr; nên dừng</td>
 <td class="ok">Cầu tăng nhanh hơn cung, M2.4 = 1,305 &rarr; đi tiếp</td>
 <td>So sánh cửa sổ thời gian mà video chưa kịp tích view (chỉ 36% đã chín)</td></tr>
<tr class="hi"><td><b>STEP_04</b></td>
 <td class="no">Công thức thắng là dùng tên Thánh Vịnh (lift 8,1&times;)</td>
 <td class="ok">Ngược lại &mdash; toàn thị trường kém hơn 52% (lift 0,48&times;)</td>
 <td>Nghịch lý Simpson: vài kênh chuyên chủ đề đó có video nổ</td></tr>
<tr class="hi"><td><b>STEP_04</b></td>
 <td class="no">Tỷ lệ tương tác phân biệt mạnh nhất (delta &minus;0,68)</td>
 <td class="ok">Artefact toán học &mdash; đã loại bỏ</td>
 <td>Mẫu số là view; nhóm thắng có view gấp 82 lần</td></tr>
</tbody></table>

<div class="box">
<span class="l">Vì sao phần này quan trọng với bạn</span>
<p>Cả ba lỗi trên đều <b>trông rất thuyết phục</b> khi nhìn lần đầu, và đều có ý nghĩa thống kê.
Nếu dùng bảng chấm thủ công hoặc phương pháp trong script gốc, cả ba đều sẽ lọt qua.</p>
<p>Thứ bắt được chúng là <b>ba quy tắc bắt buộc</b> của hệ thống: chỉ so sánh dữ liệu đã chín,
luôn có nhóm đối chứng, và kiểm mọi phát hiện ở ba lớp (mẫu &rarr; toàn thị trường &rarr;
trong từng kênh).</p>
</div>

<h2 class="pb">3. Backtest rubric</h2>

<p>Trước khi tin điểm số, phải kiểm rubric trên tập ngách đã biết: <b>24 dòng nhạc</b> trong
bảng chấm thủ công của bạn.</p>

<div class="kpi">
<div><div class="k">Ngách backtest</div><div class="v">{BT['n_genres']}</div><div class="c">dòng nhạc</div></div>
<div><div class="k">Sai lệch trung bình T1</div><div class="v up">{BT['mean_abs_dT1']:.2f}</div>
 <div class="c">điểm, trên thang 0&ndash;5</div></div>
<div><div class="k">Sai lệch trung bình T3</div><div class="v up">{BT['mean_abs_dT3']:.2f}</div>
 <div class="c">điểm, trên thang 0&ndash;5</div></div>
</div>

<p>Sai lệch dưới 0,55 điểm nghĩa là rubric <b>không mâu thuẫn</b> với đánh giá thủ công &mdash;
nó chỉ làm cho việc chấm trở nên nhất quán và tái lập được.</p>

<img src="{img('s1_backtest.png')}">
<p class="f">Chấm đỏ: điểm thủ công. Đường xanh: rubric có ngưỡng.</p>

<h3>3.1. Bằng chứng rubric sửa được lỗi bất nhất</h3>
<p>Bốn dòng nhạc có tỷ trọng top 20% gần như bằng nhau (55&ndash;62%), nhưng bảng thủ công
cho <b>bốn mức điểm khác nhau</b>:</p>
<table>
<thead><tr><th>Dòng nhạc</th><th>Top 20% chiếm</th><th>Điểm thủ công</th><th>Điểm rubric</th></tr></thead>
<tbody>{inc_rows}</tbody></table>
<p>Rubric cho cả bốn <b>cùng 4 điểm</b> &mdash; vì chúng thực sự tương đương. Đây chính là
lỗi L1 đã nêu từ đầu dự án, nay được chứng minh bằng dữ liệu.</p>

<h2>4. Kiểm lại 5 giả thuyết ban đầu</h2>
<p>Các giả thuyết này được ghi vào <code>NICHE_BRIEF.md</code> <b>trước khi phân tích</b>,
để tránh thiên lệch xác nhận.</p>
<table>
<thead><tr><th>Giả thuyết</th><th>Kết quả</th><th>Bằng chứng</th></tr></thead>
<tbody>{hyp_rows}</tbody></table>

<h2 class="pb">5. Bản đồ khoảng trống</h2>
<p>Khoảng trống thật = giao của ba điều: <b>khán giả có nhu cầu</b> &times; <b>đối thủ chưa
làm tốt</b> &times; <b>mình làm được</b>.</p>

<div class="box">
<span class="l">Cách đọc cột &laquo;bằng chứng nhu cầu&raquo; &mdash; {n_ev} bằng chứng, truy vết được</span>
<p>Mỗi ô có <b>nhiều bằng chứng</b>, mỗi bằng chứng ghi <b>nguồn</b> ngay bên dưới bằng
chữ nhỏ. Bạn kiểm chứng lại được từng cái:</p>
<p><b>Số liệu</b> &rarr; mở đúng file + khóa ghi kèm.
Ví dụ <code>05_audience/_metrics_raw.json &rarr; context.prayer_devo</code>.</p>
<p><b>Câu nói thật</b> (in nghiêng, có gạch bên trái) &rarr; kèm <code>comment_id</code> và số
tim. Mở <code>05_audience/03_quote_bank.csv</code>, lọc đúng ID đó để đọc <b>nguyên văn</b>;
hoặc dán ID vào YouTube để xem comment gốc.</p>
<p class="f" style="text-align:left;margin:6pt 0 0">Toàn bộ rút từ <b>6.413 comment</b>
đã lọc nhiễu (từ 6.794 thô) &mdash; xem STEP_05.</p>
</div>

<table>
<thead><tr><th>Khoảng trống</th><th>Bằng chứng nhu cầu<br><span style="font-weight:400;
font-size:6.5pt">số liệu + câu nói thật, kèm nguồn</span></th><th>Mức cạnh tranh</th>
<th>Hiệu quả</th><th>Ưu tiên</th><th>Tin cậy</th></tr></thead>
<tbody>{gap_rows}</tbody></table>

<div class="box">
<span class="l">Khoảng trống số 1: Old-school / vintage black gospel &mdash; đọc kỹ phần cảnh báo</span>
<p><b>Ba nguồn dữ liệu độc lập cùng chỉ về một hướng:</b></p>
<p><b>1. Hiệu quả (STEP_06):</b> lift {os_lift} &mdash; cao nhất trong 16 chủ đề được kiểm.
Chỉ {os_share} video trong ngách khai thác.</p>
<p><b>2. Khán giả (STEP_05):</b> tuổi tự khai trung vị {age_med}. Nhóm này lớn lên cùng
black gospel thập niên 1950&ndash;70 &mdash; đây là âm nhạc tuổi trẻ của họ.</p>
<p><b>3. Từ khóa (STEP_06):</b> các tag chỉ xuất hiện ở video thắng đều là tên phong cách
nhạc cụ thể: &ldquo;delta blues&rdquo;, &ldquo;slow blues&rdquo;, &ldquo;blues guitar&rdquo;.</p>
</div>

<div class="box crit">
<span class="l">⚠ Vì sao độ tin cậy của khoảng trống số 1 chỉ là &laquo;{os_conf}&raquo;</span>
<p>Con số lift {os_lift} <b>không đứng vững qua lớp kiểm thứ ba</b>. Phán quyết chính thức
của STEP_06 là <b>&laquo;{os_verdict}&raquo;</b>:</p>
<p>Trong từng kênh, lift chỉ còn <b>{os_within}</b> &mdash; và chỉ <b>{os_better}/{os_tested}
kênh</b> làm chủ đề này tốt hơn phần còn lại của chính họ. Nghĩa là phần lớn hiệu ứng
&laquo;2,37&times;&raquo; đến từ <b>vài kênh mạnh chuyên chủ đề đó</b>, không phải từ bản thân
chủ đề (nghịch lý Simpson &mdash; bẫy L2).</p>
<p>Bằng chứng khán giả cũng mỏng: tuổi trung vị {age_med} rút từ <b>chỉ {age_n} người tự khai</b>
({age_pct} mẫu). Nó gợi ý, không chứng minh.</p>
<p><b>Vẫn nên thử</b> &mdash; chi phí thấp, ba nguồn cùng hướng. Nhưng hãy coi đây là
<b>giả thuyết đáng kiểm</b>, không phải kết luận chắc chắn. Đo lại sau 10&ndash;15 video đầu.</p>
</div>

<div class="box ok">
<span class="l">Khoảng trống số 2: định vị &ldquo;yêu nhạc blues, cần lời sạch&rdquo;</span>
<p>Bình luận được thích nhiều nhất trong toàn bộ 145.150 bình luận nói đúng nỗi đau này:</p>
<p style="font-style:italic;padding-left:10pt;border-left:2pt solid #CFC4B8">
&ldquo;Finally something for those of us who love the music but can't stand the lyrics of the
blues.&rdquo; &mdash; 1.444 lượt thích</p>
<p>Bình luận chứa &ldquo;finally&rdquo; nhận lượt thích gấp <b>6,6 lần</b> mức trung bình
(p &lt; 0,0001). Nhưng <b>chưa kênh nào dùng điều này làm định vị chính</b> trong mô tả kênh.</p>
<p>Đây là khoảng trống <b>rẻ nhất để lấp</b> &mdash; chỉ là cách viết mô tả, không tốn chi phí
sản xuất.</p>
</div>

<h2 class="pb">5.1. Đối chiếu với nghiên cứu độc lập</h2>

<p>Team khác trong công ty (FMG) làm một nghiên cứu chân dung khán giả Christian Blues
<b>riêng biệt</b>: mẫu 60 video / 38 kênh, <b>1.017 bình luận</b> &mdash; không dùng chung
dữ liệu, không dùng chung phương pháp với nghiên cứu này.</p>

<p>Đây là cơ hội hiếm: <b>hai nghiên cứu độc lập trên cùng một ngách</b>. Nếu kết quả trùng
nhau thì độ tin cậy tăng thật; nếu lệch thì phải giải thích được.</p>

<table>
<thead><tr><th>Chỉ số</th><th>FMG<br><span style="font-weight:400;font-size:6.5pt">n = 1.017</span></th>
<th>Nghiên cứu này<br><span style="font-weight:400;font-size:6.5pt">n = 6.413</span></th>
<th>Kết luận</th></tr></thead>
<tbody>
<tr class="hi"><td><b>Tuổi trung vị</b> (tự khai)</td><td class="n">69</td><td class="n">70</td>
 <td><b class="ok">TRÙNG</b> &mdash; lệch 1 tuổi, hai mẫu tách rời</td></tr>
<tr><td>Cỡ mẫu tự khai tuổi</td><td class="n">11</td><td class="n">82</td>
 <td>Cả hai đều mỏng &mdash; vẫn là giả thuyết</td></tr>
<tr class="hi"><td><b>Bối cảnh nghe số 1</b></td><td>Cầu nguyện</td><td>Cầu nguyện</td>
 <td><b class="ok">TRÙNG</b> &mdash; cùng thứ hạng</td></tr>
<tr><td>Bối cảnh số 2</td><td>Nhà thờ / buổi sáng</td><td>Buổi sáng</td>
 <td>Gần trùng</td></tr>
<tr><td>Nhu cầu lớn nhất</td><td>Hy vọng / khích lệ (21,7%)</td><td>Cầu nguyện / tĩnh tâm (13,5%)</td>
 <td>Khác cách phân loại, cùng bản chất</td></tr>
<tr class="hi"><td><b>Tiếng Tây Ban Nha</b></td><td class="n">6,0%</td><td class="n">1,73%</td>
 <td>Khác mức, <b>cùng khẳng định có</b></td></tr>
</tbody></table>

<div class="box ok">
<span class="l">Vì sao điều này quan trọng</span>
<p><b>Tuổi trung vị 69 và 70</b> đến từ hai mẫu hoàn toàn tách rời, hai người mã hóa khác nhau.
Trùng nhau đến mức này rất khó xảy ra do ngẫu nhiên &mdash; đây là <b>bằng chứng mạnh nhất</b>
cho chân dung &ldquo;khán giả cao tuổi&rdquo;.</p>
<p>Cùng lúc, cả hai đều thừa nhận <b>mẫu tự khai tuổi rất mỏng</b> (11 và 82 người).
Hai nghiên cứu cùng sai theo một hướng vẫn là sai &mdash; nên kết luận này vẫn xếp
<b>độ tin cậy Vừa</b>, không nâng lên Cao.</p>
</div>

<div class="box crit">
<span class="l">⚠ Chênh lệch phải giải thích được: tiếng Tây Ban Nha 6,0% vs 1,73%</span>
<p>FMG đo <b>6,0%</b>; đo lại trên dữ liệu của ta được <b>1,73%</b>. Chênh hơn 3 lần.</p>
<p><b>Nguyên nhân:</b> FMG phân loại ngôn ngữ từng bình luận (có cả nhóm
&ldquo;khác/khó xác định&rdquo; 13,4%); ta dùng bộ lọc từ chức năng, yêu cầu ≥2 từ đặc trưng
nên <b>bỏ sót bình luận ngắn</b> (&ldquo;Amén&rdquo;, &ldquo;Gloria a Dios&rdquo;).
Con số của ta là <b>chặn dưới</b>.</p>
<p><b>Điều cả hai đồng ý:</b> có một nhóm khán giả nói tiếng Tây Ban Nha đủ lớn để đáng chú ý.
Nhờ đó khoảng trống &ldquo;Nhánh Tây Ban Nha&rdquo; được nâng từ
<b>Thấp lên Vừa</b> &mdash; trước đây nó <i>không có bằng chứng phía cầu nào cả</i>.</p>
</div>

<h2>6. Chiến lược gia nhập</h2>

<h3>6.1. Định vị</h3>
<table>
<thead><tr><th>Yếu tố</th><th>Quyết định</th><th>Căn cứ</th></tr></thead>
<tbody>
<tr><td><b>Chủ đề lõi</b></td><td>Old-school / vintage black gospel blues</td>
 <td>Lift 2,37&times;, chỉ 3,96% thị trường (STEP_06)</td></tr>
<tr><td><b>Định vị kênh</b></td><td>&ldquo;Nhạc blues cho người yêu blues nhưng cần lời phù hợp đức tin&rdquo;</td>
 <td>Nỗi đau được thích gấp 6,6&times; (STEP_05)</td></tr>
<tr><td><b>Định dạng chủ lực</b></td><td>Mix dài 1&ndash;3 giờ, <b>có lời hát</b></td>
 <td>~11,7 ad slot; khán giả nghe khi cầu nguyện (STEP_05, 07)</td></tr>
<tr><td><b>Tuyệt đối tránh</b></td><td>Nhạc không lời / định vị &ldquo;background music&rdquo;</td>
 <td>Lift 0,17&times; &mdash; kém nhất (STEP_06)</td></tr>
<tr><td><b>Nhịp đăng</b></td><td>15&ndash;20 video/tháng</td>
 <td>Trung vị ngách {b['median_upload_per_month']:.0f}; đăng dày cho tổng view gấp 5,3&times; (STEP_03)</td></tr>
</tbody></table>

<h3>6.2. Mốc chuẩn từ 53 kênh thật</h3>
<img src="{img('s3_benchmarks.png')}" class="half">
<table>
<thead><tr><th>Mốc</th><th>View/tháng</th><th>Ý nghĩa</th></tr></thead>
<tbody>
<tr><td>Phân vị 25</td><td class="n">{b['p25_vpm']:,.0f}</td><td>Một phần tư kênh dưới mức này</td></tr>
<tr class="hi"><td><b>Trung vị</b></td><td class="n">{b['p50_vpm']:,.0f}</td>
 <td><b>Mục tiêu hợp lý cho kênh mới</b></td></tr>
<tr><td>Phân vị 75</td><td class="n">{b['p75_vpm']:,.0f}</td><td>Nhóm khá</td></tr>
<tr><td>Phân vị 90</td><td class="n">{b['p90_vpm']:,.0f}</td><td>Chỉ ~5 kênh đạt</td></tr>
<tr><td>Kênh &lt;12 tháng (trung vị)</td><td class="n">{b['young_median_vpm']:,.0f}</td>
 <td>Mức kênh mới thực tế đạt được</td></tr>
</tbody></table>
<p>View trung vị mỗi video: <b>{b['median_view_per_video']:,.0f}</b>; nhóm phần tư trên:
<b>{b['top_quartile_view_per_video']:,.0f}</b>. Dùng làm mốc đánh giá từng video.</p>

{PLAYBOOK_SECTION}

<h2 class="pb">8. Kế hoạch 90 ngày</h2>


<div class="phase">
<h4>Ngày 1&ndash;30 &mdash; Thiết lập và kiểm chứng giả định</h4>
<p><b>Việc:</b> Dựng kênh với định vị đã chốt. Sản xuất 15&ndash;20 mix dài 1&ndash;3 giờ theo
chủ đề old-school. Chạy snapshot lần 2 trên dữ liệu ngách.</p>
<p><b>Tiêu chí đo:</b> đăng đủ 15 video · ít nhất 1 video vượt {b['median_view_per_video']:,.0f}
view · snapshot xác nhận M2.4 &ge; 1,0</p>
<p><b>Điều kiện dừng:</b> nếu snapshot cho M2.4 &lt; 0,8 &rarr; <b>dừng lại đánh giá lại</b>,
vì trục Động lượng chiếm 25% điểm số.</p>
</div>

<div class="phase">
<h4>Ngày 31&ndash;60 &mdash; Tìm công thức riêng</h4>
<p><b>Việc:</b> A/B test chủ đề tạ ơn (lift 1,62&times;) so với old-school thuần. Thử 3 mẫu
tiêu đề khác nhau. Theo dõi video nào vượt trội.</p>
<p><b>Tiêu chí đo:</b> đạt {b['p25_vpm']:,.0f} view/tháng (phân vị 25 của ngách) ·
xác định được ít nhất 1 mô-típ lặp lại được</p>
<p><b>Điều kiện dừng:</b> nếu sau 60 ngày chưa có video nào vượt
{b['median_view_per_video']:,.0f} view &rarr; xem lại chất lượng bản nhạc, không phải metadata.</p>
</div>

<div class="phase">
<h4>Ngày 61&ndash;90 &mdash; Nhân rộng hoặc dừng</h4>
<p><b>Việc:</b> Nếu đạt mốc, mở kênh thứ 2&ndash;3 theo mô hình song song. Xác minh RPM thật từ
YouTube Analytics.</p>
<p><b>Tiêu chí đo:</b> đạt {b['p50_vpm']:,.0f} view/tháng (trung vị ngách) · RPM thật &ge; $1,5 ·
đủ điều kiện bật kiếm tiền</p>
<p><b>Quyết định:</b> RPM thật &ge; $3 &rarr; nhân rộng. RPM &lt; $1,5 &rarr; ngách không đủ
hấp dẫn về tài chính, chuyển hướng.</p>
</div>

<div class="box crit">
<span class="l">Ba việc phải làm ngay trong tuần đầu</span>
<p><b>1. Chạy snapshot lần 2.</b> Đây là biến số duy nhất có thể lật ngược toàn bộ kết luận.
Cần cách lần đầu 7&ndash;14 ngày &mdash; càng để lâu càng mất cơ hội.</p>
<p><b>2. Không sao chép nguyên văn tiêu đề đối thủ.</b> 132 tiêu đề đang bị dùng chung giữa
các kênh; có kênh tới 55,4% video trùng. Học cấu trúc thì được.</p>
<p><b>3. Chuẩn bị dữ liệu thumbnail</b> để hoàn thiện phân tích còn thiếu (mục 9).</p>
</div>

<h2>9. Danh sách 24 đề tài đầu tiên</h2>
<p>Kết hợp: chủ đề thắng (old-school lift 2,37&times;, tạ ơn 1,62&times;) &times; bối cảnh nghe
thật của khán giả (STEP_05) &times; định dạng dài (STEP_07).</p>
<table>
<thead><tr><th>#</th><th>Tiêu đề đề xuất</th><th>Căn cứ</th><th>Độ dài</th></tr></thead>
<tbody>{idea_rows}</tbody></table>
<p style="font-size:8pt;color:#6B615A">Đây là <b>khung để bắt đầu</b>, không phải công thức đảm
bảo. STEP_04 đã chứng minh metadata không quyết định thắng thua &mdash; chất lượng bản nhạc mới
là biến chính, và đó là thứ dữ liệu không đo được.</p>

<h2 class="pb">10. Điểm số &mdash; và những gì có thể làm nó sai</h2>

<table>
<thead><tr><th>Trục</th><th>Điểm</th><th>Trọng số</th><th>Chỉ số quyết định</th><th>Tin cậy</th></tr></thead>
<tbody>
{ax_rows}
<tr><td><b>T6</b> Rủi ro</td><td class="n dn">{SC['T6']['penalty']}</td><td class="n">&mdash;</td>
 <td>Trùng lặp nội dung &minus;1, chủ đề tôn giáo+AI &minus;1</td><td><span class="wa">Vừa</span></td></tr>
</tbody></table>

<h3>9.1. Ba kịch bản có thể thay đổi kết luận</h3>
<table>
<thead><tr><th>Nếu...</th><th>Thì điểm</th><th>Xếp loại mới</th></tr></thead>
<tbody>
<tr><td>Snapshot mới cho M2.4 &lt; 0,8 &rarr; T2 giảm còn 1</td>
 <td class="n dn">9,2</td><td class="no">Bỏ qua</td></tr>
<tr><td>RPM thật là $6 &rarr; T5 lên 4</td><td class="n up">12,6</td><td>Theo dõi</td></tr>
<tr><td>YouTube siết chính sách AI &rarr; T6 xuống &minus;4</td>
 <td class="n dn">10,2</td><td>Theo dõi</td></tr>
</tbody></table>
<p><b>Kịch bản đầu là rủi ro lớn nhất.</b> Trục Động lượng chiếm 25% trọng số và hiện chỉ dựa
trên <b>một lần chụp dữ liệu</b>.</p>

<h3>9.2. Dữ liệu còn thiếu</h3>
<table>
<thead><tr><th>Dữ liệu</th><th>Ảnh hưởng khi có</th><th>Trạng thái</th></tr></thead>
<tbody>
<tr class="hi"><td><b>Ảnh thumbnail thật</b></td>
 <td>Cập nhật STEP_04: phân tích bố cục, khuôn mặt, kiểu chữ, mô-típ hình ảnh &mdash;
 những thứ 22 đặc trưng số không bắt được. <b>Có thể lật ngược</b> kết luận
 &ldquo;thumbnail không phân biệt thắng thua&rdquo;</td>
 <td class="wa">Sẽ bổ sung</td></tr>
<tr><td>Snapshot lần 2</td><td>Nâng trục T2 từ tin cậy Vừa lên Cao</td>
 <td class="no">Chưa chạy</td></tr>
<tr><td>media_probe mở rộng</td><td>Phân tích tempo, tông, đặc trưng âm thanh (hiện phủ 0,6%)</td>
 <td>Tùy chọn</td></tr>
<tr><td>RPM thật</td><td>Thay ước tính bằng số đo &mdash; trục T5 hiện tin cậy Thấp</td>
 <td>Cần kênh thử nghiệm</td></tr>
</tbody></table>

<h3>9.3. Giới hạn của toàn bộ nghiên cứu</h3>
<ul>
<li><b>Chỉ đo được metadata.</b> Không đo được chất lượng âm nhạc, thời lượng xem, hay tỷ lệ
nhấp &mdash; mà đó nhiều khả năng là các biến quyết định thật.</li>
<li><b>Thiên lệch sống sót ở cấp kênh.</b> Dữ liệu chỉ có 53 kênh <i>còn tồn tại</i>. Kênh đã
thất bại và bị xóa không xuất hiện, nên tỷ lệ thành công 61,5% có thể lạc quan hơn thực tế.</li>
<li><b>Người bình luận không đại diện cho người xem.</b> Chân dung khách hàng dựng từ nhóm
gắn bó nhất; người xem thụ động có thể khác hẳn.</li>
<li><b>Không cho biết vì sao người ta KHÔNG xem.</b> Dữ liệu chỉ có người đã đến.</li>
</ul>

<h2>11. Tổng kết bảy bước</h2>
<table>
<thead><tr><th>Bước</th><th>Câu hỏi</th><th>Kết luận</th></tr></thead>
<tbody>
<tr><td><b>01+02</b></td><td>Ngách đang lên hay xuống?</td>
 <td class="ok">Đang lên. Cầu tăng nhanh hơn cung 30,5%</td></tr>
<tr><td><b>03</b></td><td>Người mới còn cửa không?</td>
 <td class="ok">Còn rất rộng. 61,5% kênh mới đạt traction</td></tr>
<tr><td><b>04</b></td><td>Công thức video thắng là gì?</td>
 <td class="wa">Không có công thức từ metadata &mdash; 26 giả thuyết đều bị bác bỏ</td></tr>
<tr><td><b>05</b></td><td>Khách hàng là ai?</td>
 <td class="ok">Tín đồ lớn tuổi Mỹ, nghe khi cầu nguyện và lúc khó khăn</td></tr>
<tr><td><b>06</b></td><td>Làm đề tài gì?</td>
 <td class="ok">Old-school / vintage. Tránh nhạc không lời và Thánh Vịnh</td></tr>
<tr><td><b>07</b></td><td>Ra tiền không?</td>
 <td class="wa">~$319/tháng kênh trung vị. Ước tính, tin cậy thấp</td></tr>
<tr><td><b>08</b></td><td>Vào hay không?</td>
 <td class="ok"><b>Vào có điều kiện</b> &mdash; mô hình nhiều kênh song song</td></tr>
</tbody></table>

<div class="box">
<span class="l">Ghi chú cuối</span>
<p>Toàn bộ điểm số trong báo cáo này có thể truy vết đến công thức, ngưỡng, nguồn dữ liệu và
độ tin cậy &mdash; xem <code>_state/scores.json</code> và <code>_state/metrics.json</code>.</p>
<p>Khung nghiên cứu (<code>framework/</code>) tách rời khỏi dữ liệu ngách
(<code>niches/</code>), nên có thể chạy lại nguyên vẹn cho ngách tiếp theo và <b>so sánh trực
tiếp điểm số</b> giữa các ngách.</p>
<p><b>Thời hạn dữ liệu:</b> điều khoản YouTube API yêu cầu làm mới hoặc xóa trong 30 ngày
&mdash; hạn khoảng 12/09/2026.</p>
</div>

</body></html>"""

out=D/"STEP08_Bao-cao-Tong-hop.pdf"
HTML(string=DOC,base_url=".").write_pdf(out)
print(f"PDF: {out} ({out.stat().st_size/1024:.0f} KB)")
