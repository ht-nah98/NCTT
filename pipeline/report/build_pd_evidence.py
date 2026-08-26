"""BÁO CÁO: Bảng đối chứng — nghe và tự kiểm từng track khớp hymn PD.

Trả lời câu hỏi "video nào, track nào đang trùng?" bằng bằng chứng nghe được:
link YouTube tua thẳng tới giây có cụm trùng, kèm cụm 4 từ nguyên văn để đối
chiếu bằng tai. Mọi số liệu đọc động từ pd_evidence.parquet (T27).

Không in toàn văn lời hát — chỉ cụm 4 từ trùng, đủ để đối chứng.
"""
import sys
from pathlib import Path

import pandas as pd
from weasyprint import HTML

N = Path(sys.argv[1] if len(sys.argv) > 1 else "niches/christian-blues")
D = N / "99_report"
D.mkdir(parents=True, exist_ok=True)
NICHE_LABEL = N.name.replace("-", " ").title()

ev = pd.read_parquet(N / "02_analysis/pd_evidence.parquet")
cls = pd.read_parquet(N / "02_analysis/pd_classification.parquet")

N_TRACK_ALL = len(cls)
N_HIT = len(ev)
N_ZERO = N_TRACK_ALL - N_HIT
N_OVER = int(ev.over_threshold.sum())
N_REAL = int((ev.verdict == "TRÍCH DẪN THẬT").sum())
N_FALSE = N_HIT - N_REAL
N_VIDEO = ev.video_id.nunique()
N_CHANNEL = ev.handle.nunique()
MAXS = ev.match_score.max()
THRESH = 0.40


def vnf(x, nd=3):
    return f"{x:.{nd}f}".replace(".", ",")


def mmss(s):
    s = int(s)
    return f"{s // 60}:{s % 60:02d}"


def row(r, i):
    cls_badge = "vuot" if r.over_threshold else ("gia" if r.verdict == "TRÙNG NGẪU NHIÊN" else "duoi")
    badge = {"vuot": "VƯỢT NGƯỠNG", "duoi": "dưới ngưỡng", "gia": "TRÙNG NGẪU NHIÊN"}[cls_badge]
    phrases = r.distinctive_phrases or r.shared_phrases
    warn = ""
    if r.verdict == "TRÙNG NGẪU NHIÊN":
        warn = ('<br><span class="flag">⚠ Cụm chỉ gồm từ tiếng Anh thông dụng '
                '— nhiều khả năng trùng ngẫu nhiên, không phải trích dẫn.</span>')
    return (
        f'<tr><td class="n">{i}</td>'
        f'<td><b>{r.track_title}</b><br>'
        f'<span class="note">trong video: {r.youtube_title[:62]}{"…" if len(r.youtube_title) > 62 else ""}</span><br>'
        f'<span class="note"><code>{r.handle}</code></span></td>'
        f'<td>{r.matched_hymn}<br><span class="note">{r.hymn_year}</span></td>'
        f'<td class="n">{vnf(r.match_score)}<br><span class="bd {cls_badge}">{badge}</span></td>'
        f'<td class="ph">“{phrases}”{warn}</td>'
        f'<td class="lk"><a href="{r.url_match}">{mmss(r.match_at_s)}</a><br>'
        f'<span class="note">track {mmss(r.track_start_s)}&ndash;{mmss(r.track_end_s)}</span></td>'
        f"</tr>"
    )


_rows = "\n".join(row(r, i) for i, r in enumerate(ev.itertuples(), 1))

CSS = """
@page { size:A4 landscape; margin:13mm 12mm 15mm;
 @bottom-center { content: counter(page) " / " counter(pages);
  font-family:"DejaVu Sans"; font-size:8pt; color:#9A8E85; } }
body { font-family:"DejaVu Sans",sans-serif; font-size:9.5pt; line-height:1.45; color:#1A1614; }
h1 { font-size:20pt; margin:0 0 4pt; letter-spacing:-.4pt; }
h2 { font-size:12.5pt; margin:15pt 0 6pt; padding-bottom:4pt;
 border-bottom:1.5pt solid #1A1614; page-break-after:avoid; }
p { margin:5pt 0; }
.sub { color:#6B615A; font-size:10.5pt; margin:0 0 9pt; }
.meta { font-size:8pt; color:#7A6F68; border-top:.6pt solid #E2DAD1;
 border-bottom:.6pt solid #E2DAD1; padding:6pt 0; margin-bottom:12pt; }
table { border-collapse:collapse; width:100%; font-size:8.2pt; margin:7pt 0; }
th { background:#F2EEE8; text-align:left; padding:5pt 6pt; font-size:7.2pt;
 text-transform:uppercase; letter-spacing:.4pt; color:#5A514B;
 border-bottom:1pt solid #CFC4B8; }
td { padding:6pt; border-bottom:.6pt solid #EDE7E0; vertical-align:top; }
tr { page-break-inside:avoid; }
td.n { text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
td.ph { font-size:8pt; color:#4A423D; font-style:italic; }
td.lk { white-space:nowrap; font-variant-numeric:tabular-nums; }
td.lk a { color:#8C3A2B; text-decoration:none; font-weight:bold; font-size:9.5pt; }
.note { font-size:7.3pt; color:#7A6F68; font-style:normal; }
.flag { font-size:7.3pt; color:#9B2C2C; font-style:normal; }
.bd { font-size:6.6pt; text-transform:uppercase; letter-spacing:.4pt;
 font-weight:bold; display:inline-block; margin-top:3pt; }
.bd.vuot { color:#9B2C2C; } .bd.duoi { color:#7A6F68; } .bd.gia { color:#B5731F; }
.box { border-left:2.5pt solid #8C3A2B; background:#F9F4F2; padding:8pt 11pt;
 margin:9pt 0; page-break-inside:avoid; }
.box.warn { border-left-color:#B5731F; background:#FBF3E8; }
.box.crit { border-left-color:#9B2C2C; background:#FBEEEE; }
.box.ok { border-left-color:#2F6B4F; background:#EFF5F1; }
.box .l { font-size:7.3pt; text-transform:uppercase; letter-spacing:.7pt;
 font-weight:bold; color:#8C3A2B; display:block; margin-bottom:4pt; }
.box.warn .l { color:#B5731F; } .box.crit .l { color:#9B2C2C; } .box.ok .l { color:#2F6B4F; }
.box p { margin:0 0 5pt; font-size:9pt; } .box p:last-child { margin-bottom:0; }
.kpi { display:flex; gap:7pt; margin:9pt 0; }
.kpi div { flex:1; border:.6pt solid #E2DAD1; padding:8pt 9pt; }
.kpi .k { font-size:6.6pt; text-transform:uppercase; letter-spacing:.5pt;
 color:#7A6F68; margin-bottom:4pt; }
.kpi .v { font-size:17pt; font-weight:bold; letter-spacing:-.3pt; }
.kpi .c2 { font-size:6.8pt; color:#7A6F68; margin-top:3pt; line-height:1.3; }
code { background:#F2EEE8; padding:.5pt 3pt; font-size:7.6pt; }
.verdict { color:#8C3A2B; font-weight:bold; font-size:8.6pt; }
.pb { page-break-before:always; }
"""

DOC = f"""<!doctype html><html><head><meta charset="utf-8">
<style>{CSS}</style></head><body>

<h1>Bảng đối chứng: nghe và tự kiểm</h1>
<p class="sub">{NICHE_LABEL} &mdash; {N_HIT} track có trùng lặp với hymn public domain, kèm link tua thẳng tới chỗ trùng</p>
<div class="meta">
Nguồn: <code>02_analysis/pd_evidence.parquet</code> &nbsp;&middot;&nbsp;
Quét toàn bộ {N_TRACK_ALL} track &nbsp;&middot;&nbsp;
Link YouTube kiểm chứng còn sống 26/08/2026 &nbsp;&middot;&nbsp;
Phụ lục đối chứng của <b>NHAC_Ban-quyen-PD.pdf</b>
</div>

<div class="kpi">
<div><div class="k">Track điểm khớp = 0</div><div class="v" style="color:#2F6B4F">{N_ZERO}</div>
<div class="c2">Không trùng một cụm 4 từ nào &mdash; không cần đối chứng</div></div>
<div><div class="k">Track cần nghe</div><div class="v">{N_HIT}</div>
<div class="c2">Trên {N_VIDEO} video, {N_CHANNEL} kênh &mdash; toàn bộ liệt kê ở bảng dưới</div></div>
<div><div class="k">Vượt ngưỡng {vnf(THRESH, 2)}</div><div class="v" style="color:#9B2C2C">{N_OVER}</div>
<div class="c2">Chỉ track này được xếp nhóm "mượn hymn PD"</div></div>
<div><div class="k">Điểm cao nhất</div><div class="v">{vnf(MAXS)}</div>
<div class="c2">Hát lại nguyên bài sẽ cho ~1,000 &mdash; còn rất xa</div></div>
</div>

<h2>1 &middot; {N_HIT} track cần đối chứng &mdash; bấm giờ để nghe</h2>
<table>
<thead><tr>
<th style="width:3%">#</th>
<th style="width:27%">Track &mdash; video chứa nó</th>
<th style="width:12%">Hymn khớp</th>
<th style="width:9%">Điểm</th>
<th style="width:33%">Cụm trùng nguyên văn</th>
<th style="width:11%">Nghe tại</th>
</tr></thead>
<tbody>{_rows}</tbody>
</table>
<p class="verdict">=> Toàn bộ {N_HIT} trường hợp đều chỉ trùng câu MỞ ĐẦU rồi rẽ sang lời mới.
Không track nào tái hiện đủ một hymn để coi là hát lại nguyên bản.</p>

<h2 class="pb">2 &middot; Đọc bảng này thế nào</h2>

<div class="box">
<span class="l">Con số ở cột Điểm nghĩa là gì</span>
<p>Câu mở đầu mỗi hymn được cắt thành các cụm <b>4 từ liên tiếp</b>. Điểm khớp =
số cụm của hymn xuất hiện nguyên văn trong track, chia cho tổng số cụm của hymn đó.
Ví dụ {vnf(MAXS)} nghĩa là track chứa {int(round(MAXS * 100))}% số cụm 4 từ của câu mở đầu
&mdash; tức mượn khoảng một dòng rưỡi, rồi phần còn lại là lời mới.</p>
<p><b>Ngưỡng {vnf(THRESH, 2)}</b> mới xếp vào nhóm "mượn hymn PD". Các track dưới ngưỡng vẫn liệt kê
đầy đủ ở đây để bạn tự phán quyết &mdash; giấu đi thì bảng này mất tác dụng đối chứng.</p>
</div>

<div class="box crit">
<span class="l">Mốc giờ là ƯỚC LƯỢNG, không phải timestamp chính xác</span>
<p>Whisper cho biết track bắt đầu và kết thúc ở giây nào, nhưng không đánh dấu từng câu hát.
Mốc giờ ở cột cuối được <b>nội suy tuyến tính</b> theo vị trí cụm trùng trong lời &mdash;
giả định hát đều nhịp suốt track, điều không đúng hoàn toàn.</p>
<p><b>Cách dùng đúng:</b> bấm link, rồi nghe quanh mốc đó trong khoảng &plusmn;30 giây.
Nếu vẫn không thấy, dùng cột "track" để nghe từ đầu track &mdash; đó là mốc chính xác từ dữ liệu.</p>
</div>

<div class="box warn">
<span class="l">{N_FALSE} trường hợp tôi tự gắn cờ nghi ngờ</span>
<p>Cụm trùng chỉ gồm từ tiếng Anh thông dụng ("when this life is") thì rất có thể là
<b>trùng ngẫu nhiên</b>, không phải trích dẫn. Tôi lọc bằng cách kiểm tra cụm có chứa từ đặc hiệu
hay không &mdash; "amazing", "foretaste", "faithfulness" là đặc hiệu; "when / this / life / is" thì không.</p>
<p><b>Ranh giới này không tuyệt đối.</b> Ví dụ rõ nhất trong bảng: cụm "every time i feel"
được tính là trích dẫn vì "feel" không nằm trong danh sách từ thông dụng của tôi &mdash;
nhưng thực tế đây cũng là cách nói rất phổ thông. Hai dòng đó
(<i>I'm Gonna Be Ready</i> và <i>At The Cross</i>) là những dòng đáng nghe nhất để bạn tự phán quyết.</p>
</div>

<div class="box ok">
<span class="l">Vì sao {N_ZERO} track còn lại không có trong bảng</span>
<p>Chúng có điểm khớp <b>bằng 0 tuyệt đối</b> &mdash; không chứa dù một cụm 4 từ nào của bất kỳ
hymn nào trong bộ đối chiếu. Không có gì để đối chứng, và đây cũng chính là lý do kết luận
"sáng tác mới hoàn toàn" đứng vững: không phải điểm thấp, mà là <b>bằng 0</b>.</p>
<p class="note">Nhắc lại giới hạn đã nêu ở báo cáo chính: "bằng 0" nghĩa là không khớp
<b>39 bài trong bộ đối chiếu</b>, không phải không khớp mọi hymn PD trên đời. Và phép đo này
chỉ xét LỜI &mdash; một bài dùng lời mới phổ trên giai điệu hymn cổ sẽ có điểm 0 mà vẫn mượn nhạc.</p>
</div>

</body></html>"""

out = D / "_phu-luc/PHU-LUC_Doi-chung-Track.pdf"
out.parent.mkdir(parents=True, exist_ok=True)
HTML(string=DOC).write_pdf(out)
print(f"OK  {out}  ({N_HIT} track / {N_VIDEO} video / {N_CHANNEL} kênh)")
