"""BÁO CÁO: Public Domain vs Sáng tác mới — Christian Blues.
Trả lời trực tiếp: nhạc trên thị trường này là hát lại nhạc cũ hết bản
quyền, hay sáng tác mới hoàn toàn? Đo bằng khớp nội dung thật, không
đoán qua tiêu đề (tiêu đề "Amazing Grace" từng cho kết quả sai khi kiểm
lại — xem hộp cảnh báo trong báo cáo).
"""
import json
import sys
from pathlib import Path

import pandas as pd
from weasyprint import HTML

N = Path(sys.argv[1] if len(sys.argv) > 1 else "niches/christian-blues")
D = N / "99_report"
NICHE_LABEL = N.name.replace("-", " ").title()
OUT_ANA = N / "02_analysis"

pd_df = pd.read_parquet(OUT_ANA / "pd_classification.parquet")
corpus = json.loads(Path("framework/04_reference/pd_corpus/hymns_pd.json").read_text())

def vn(x, nd=0):
    s = f"{x:,.{nd}f}"
    a, *b = s.split(".")
    a = a.replace(",", ".")
    return a + ("," + b[0] if b else "")
def pct(x, nd=1): return f"{x:.{nd}f}".replace(".", ",") + "%"
def vnf(x, nd=2):
    """Thập phân không ngăn nghìn (điểm khớp, hệ số) — dấu phẩy kiểu VN."""
    return f"{x:.{nd}f}".replace(".", ",")

# ═══════ tổng hợp cấp VIDEO ═══════
_priority = ["HYMN_PARTIAL_PD", "HYMN_PARTIAL_CHECK_YEAR", "SCRIPTURE_PARAPHRASE", "NEW_COMPOSITION"]
def summarize(g):
    for c in _priority:
        if (g.pd_class == c).any():
            return pd.Series({
                "pd_class": c, "n_tracks": len(g),
                "handle": g.handle.iloc[0], "views": g.video_views.iloc[0],
            })
vid = pd_df.groupby("video_id").apply(summarize, include_groups=False).reset_index()
n_video = len(vid)
n_with_views = vid.views.notna().sum()
total_views = vid.views.sum()

g = vid.groupby("pd_class").agg(n_video=("video_id", "count"), views=("views", "sum")).reset_index()
g["pct_video"] = (g.n_video / n_video * 100)
g["pct_views"] = (g.views / total_views * 100)
_order = {c: i for i, c in enumerate(_priority)}
g["_o"] = g.pd_class.map(_order)
g = g.sort_values("_o")

LABELS = {
    "HYMN_PARTIAL_PD": ("Mượn câu mở đầu hymn PD", "Chỉ phần mở đầu trùng bản gốc trước 1930; phần còn lại + giai điệu là sáng tác mới."),
    "HYMN_PARTIAL_CHECK_YEAR": ("Mượn hymn — năm cần kiểm tra", "Hymn gốc sáng tác ≥1930, ranh giới luật PD Mỹ — chưa xác nhận được."),
    "SCRIPTURE_PARAPHRASE": ("Phóng tác Kinh Thánh (Psalm)", "Nội dung Kinh Thánh (PD) nhưng viết lại bằng lời riêng — không trích nguyên văn KJV. Giai điệu luôn là mới."),
    "NEW_COMPOSITION": ("Sáng tác mới hoàn toàn", "Không khớp hymn PD nào, không tự khai Scripture. Lời và giai điệu đều mới."),
}

_summary_rows = "\n".join(
    f'<tr><td><b>{LABELS[r.pd_class][0]}</b><br><span class="note">{LABELS[r.pd_class][1]}</span></td>'
    f'<td class="n">{r.n_video:.0f}</td>'
    f'<td class="n">{pct(r.pct_video)}</td>'
    f'<td class="n">{pct(r.pct_views)}</td></tr>'
    for r in g.itertuples()
)

# Số liệu mục 2.3 đọc động: "13 track" trong bản cũ là TỔNG track của video
# chứa nó, không phải số track khớp (chỉ 1) — dễ hiểu nhầm thành "mượn 13 bài".
_hp = pd_df[pd_df.pd_class == "HYMN_PARTIAL_PD"]
_hp_video = _hp.video_id.nunique()
_hp_track = len(_hp)
_hp_of = int((pd_df.video_id == _hp.video_id.iloc[0]).sum()) if len(_hp) else 0
_hp_hymn = _hp.matched_hymn.iloc[0] if len(_hp) else "—"
_hp_year = next((h["year"] for h in corpus["hymns"] if h["title"] == _hp_hymn), "—")
# Số track cần đối chứng (điểm > 0, kể cả dưới ngưỡng) — dẫn sang phụ lục.
_n_hit = int((pd_df.match_score > 0).sum())
_n_hit_video = pd_df[pd_df.match_score > 0].video_id.nunique()

# ═══════ ví dụ khớp hymn (để soát) ═══════
hymn_hits = pd_df[pd_df.pd_class.isin(["HYMN_PARTIAL_PD", "HYMN_PARTIAL_CHECK_YEAR"])]
_hymn_rows = "\n".join(
    f'<tr><td>{r.title}</td><td>{r.matched_hymn}</td><td class="n">{r.match_score:.3f}</td>'
    f'<td class="c">{"CHẶN" if r.match_score>=0.6 else "MỘT PHẦN"}</td></tr>'
    for r in hymn_hits.itertuples()
)

# ═══════ danh sách kênh theo nhóm ═══════
by_channel = vid.groupby(["handle", "pd_class"]).size().reset_index(name="n")
by_channel = by_channel.sort_values(["pd_class", "n"], ascending=[True, False])
_chan_rows = "\n".join(
    f'<tr><td><code>{r.handle}</code></td><td>{LABELS[r.pd_class][0]}</td><td class="n">{r.n}</td></tr>'
    for r in by_channel.itertuples()
)

# ═══════ Scripture: danh sách các Psalm phóng tác thành series ═══════
scr_titles = pd_df[pd_df.pd_class == "SCRIPTURE_PARAPHRASE"].title.dropna().unique()
n_psalm_series = len(scr_titles)

# ═══════ Số liệu cho mục PHƯƠNG PHÁP (đọc động — T27) ═══════
_n_channel_sample = pd_df.handle.nunique()
_corpus_pd = corpus.get("n_confirmed_pd", corpus["n_hymns"])
_corpus_check = corpus.get("n_needs_check", 0)
_yr_min = min(h["year"] for h in corpus["hymns"])
_yr_max = max(h["year"] for h in corpus["hymns"])
# Độ phân tách: bao nhiêu % track "sáng tác mới" có điểm khớp ĐÚNG BẰNG 0
_newc = pd_df[pd_df.pd_class == "NEW_COMPOSITION"]
_zero_share = (_newc.match_score == 0).mean() * 100 if len(_newc) else 0
_max_score = pd_df.match_score.max()
# Phủ sóng so với toàn ngách
try:
    _tot_ch = len(pd.read_parquet(N / "00_input/processed/channels_enriched.parquet"))
    _tot_v = len(pd.read_parquet(N / "00_input/processed/videos_enriched.parquet"))
except Exception:
    _tot_ch = _tot_v = None

CSS = """
@page { size:A4; margin:17mm 15mm 20mm;
 @bottom-center { content: counter(page) " / " counter(pages);
  font-family:"DejaVu Sans"; font-size:8pt; color:#9A8E85; } }
body { font-family:"DejaVu Sans",sans-serif; font-size:9.5pt; line-height:1.5; color:#1A1614; }
h1 { font-size:22pt; margin:0 0 4pt; letter-spacing:-.4pt; }
h2 { font-size:13pt; margin:18pt 0 7pt; padding-bottom:4pt;
 border-bottom:1.5pt solid #1A1614; page-break-after:avoid; }
h3 { font-size:10.5pt; margin:13pt 0 5pt; color:#8C3A2B; page-break-after:avoid; }
p { margin:5pt 0; }
.sub { color:#6B615A; font-size:10.5pt; margin:0 0 10pt; }
.meta { font-size:8pt; color:#7A6F68; border-top:.6pt solid #E2DAD1;
 border-bottom:.6pt solid #E2DAD1; padding:6pt 0; margin-bottom:14pt; }
table { border-collapse:collapse; width:100%; font-size:8.5pt; margin:7pt 0; page-break-inside:avoid; }
th { background:#F2EEE8; text-align:left; padding:5pt 7pt; font-size:7.3pt;
 text-transform:uppercase; letter-spacing:.4pt; color:#5A514B; border-bottom:1pt solid #CFC4B8; }
td { padding:6pt 7pt; border-bottom:.6pt solid #EDE7E0; vertical-align:top; }
td.n { text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
td.c { text-align:center; }
.note { font-size:7.8pt; color:#7A6F68; }
.ok { color:#2F6B4F; font-weight:bold; } .no { color:#9B2C2C; font-weight:bold; }
.wa { color:#B5731F; font-weight:bold; }
.box { border-left:2.5pt solid #8C3A2B; background:#F9F4F2; padding:8pt 11pt;
 margin:10pt 0; page-break-inside:avoid; }
.box.warn { border-left-color:#B5731F; background:#FBF3E8; }
.box.ok { border-left-color:#2F6B4F; background:#EFF5F1; }
.box.crit { border-left-color:#9B2C2C; background:#FBEEEE; }
.box .l { font-size:7.3pt; text-transform:uppercase; letter-spacing:.7pt;
 font-weight:bold; color:#8C3A2B; display:block; margin-bottom:4pt; }
.box.warn .l { color:#B5731F; }
.box.ok .l { color:#2F6B4F; }
.box.crit .l { color:#9B2C2C; }
.box p { margin:0 0 5pt; font-size:9pt; } .box p:last-child { margin-bottom:0; }
.kpi { display:flex; gap:7pt; margin:10pt 0; }
.kpi div { flex:1; border:.6pt solid #E2DAD1; padding:8pt 9pt; }
.kpi .k { font-size:6.6pt; text-transform:uppercase; letter-spacing:.5pt; color:#7A6F68; margin-bottom:4pt; }
.kpi .v { font-size:16pt; font-weight:bold; letter-spacing:-.3pt; }
.kpi .c2 { font-size:6.8pt; color:#7A6F68; margin-top:3pt; line-height:1.3; }
code { background:#F2EEE8; padding:.5pt 3pt; font-size:8pt; word-break:break-all; }
.big { text-align:center; border:1.5pt solid #8C3A2B; padding:12pt; margin:10pt 0; background:#F9F4F2; }
.big .n1 { font-size:30pt; font-weight:bold; color:#8C3A2B; line-height:1; }
.big .n2 { font-size:10.5pt; color:#4A423D; margin-top:5pt; }
.verdict { color:#8C3A2B; font-weight:bold; font-size:8.5pt; }
.pb { page-break-before:always; }
"""

DOC = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>

<h1>Nhạc gốc hay Public Domain?</h1>
<p class="sub">{NICHE_LABEL} — phân loại từng bài hát theo mức độ rủi ro bản quyền</p>
<div class="meta">
Mẫu: {len(pd_df)} track lời hát (transcribe bằng faster-whisper) trên {n_video} video ·
So khớp với {corpus['n_hymns']} hymn/spiritual public domain đã xác nhận (framework/04_reference/pd_corpus)
&nbsp;&middot;&nbsp; Lập báo cáo 25/08/2026
</div>

<div class="big">
<div class="n1">{pct(g[g.pd_class=='NEW_COMPOSITION'].pct_video.iloc[0])}</div>
<div class="n2">video là <b>sáng tác mới hoàn toàn</b> &mdash; không phải hát lại nhạc cũ hết bản quyền</div>
</div>

<h2>1 &middot; Kết luận</h2>
<table>
<thead><tr><th>Phân loại</th><th>Số video</th><th>% Video</th><th>% Views</th></tr></thead>
<tbody>{_summary_rows}</tbody>
</table>
<p class="verdict">=> Không có video nào là "hát lại nguyên bản" một hymn public domain. Điểm khớp cao nhất đo được
trên toàn corpus chỉ 0,444 (44,4% cụm từ trùng) &mdash; nghĩa là mượn tối đa 1&ndash;2 dòng mở đầu rồi
viết lời mới hoàn toàn.</p>

<div class="box">
<span class="l">Public domain nghĩa là gì</span>
<p>Tác phẩm đã hết hạn bản quyền hoặc chưa từng có bản quyền, ai cũng được dùng tự do &mdash; kể cả
cho mục đích thương mại, không cần xin phép hay trả tiền. Tại Mỹ: tác phẩm sáng tác/xuất bản
<b>trước 1930</b> đã chắc chắn thuộc public domain (luật hiện hành, mỗi năm ranh giới lùi thêm 1 năm).</p>
</div>

<h2>2 &middot; Ba nhóm, ba mức rủi ro bản quyền khác nhau</h2>

<h3 style="color:#2F6B4F">2.1 &middot; Sáng tác mới hoàn toàn ({pct(g[g.pd_class=='NEW_COMPOSITION'].pct_video.iloc[0])} video)</h3>
<p>Lời và giai điệu đều mới viết. Không có rủi ro va chạm bản quyền của bài khác, nhưng cũng
không được hưởng lợi thế "miễn phí" của nhạc cổ &mdash; toàn bộ chi phí sáng tác (bằng AI hoặc người)
dồn vào đây.</p>

<h3 style="color:#B5731F">2.2 &middot; Phóng tác Kinh Thánh / Psalm ({pct(g[g.pd_class=='SCRIPTURE_PARAPHRASE'].pct_video.iloc[0])} video, {n_psalm_series} tiêu đề Psalm khác nhau)</h3>
<p>Đây là mô hình sản xuất phổ biến nhất trong nhóm "dựa trên PD": lấy <b>nội dung/ý</b> của một
Psalm (văn bản Kinh Thánh bản dịch KJV &mdash; public domain), viết lại bằng lời riêng theo phong
cách Blues, rồi phổ giai điệu hoàn toàn mới. Ví dụ quan sát được (Psalm 23): thay vì trích
nguyên văn "The Lord is my shepherd", bài hát viết "The Lord's my shepherd, I shall not want" —
giữ đúng ý, đổi cách diễn đạt.</p>
<div class="box warn">
<span class="l">Vì sao vẫn phải coi là sáng tác mới</span>
<p><b>Chỉ phần TEXT gốc của Kinh Thánh là public domain.</b> Bản phóng tác (cách diễn đạt cụ thể)
và giai điệu là tác phẩm phái sinh mới, có bản quyền riêng của người viết. Dùng một Psalm làm
CHỦ ĐỀ thì tự do — nhưng không được sao chép nguyên lời phóng tác hay giai điệu của kênh khác.</p>
</div>

<h3 style="color:#2F6B4F">2.3 &middot; Mượn hymn public domain ({pct(g[g.pd_class=='HYMN_PARTIAL_PD'].pct_video.iloc[0])} video)</h3>
<p>Duy nhất <b>{_hp_track} track</b> (trong một video gồm {_hp_of} track) mượn câu mở đầu của
"{_hp_hymn}" ({_hp_year}, PD chắc chắn). Ngay cả trường hợp này cũng chỉ mượn 1&ndash;2 dòng
đầu, phần còn lại là lời mới.</p>
<table>
<thead><tr><th>Tiêu đề bài</th><th>Hymn PD khớp</th><th>Điểm khớp</th><th>Mức độ</th></tr></thead>
<tbody>{_hymn_rows}</tbody>
</table>
<div class="box">
<span class="l">Muốn tự nghe kiểm chứng</span>
<p>Bảng trên chỉ liệt kê track VƯỢT ngưỡng. Phụ lục
<b>PHU-LUC_Doi-chung-Track.pdf</b> liệt kê đủ <b>{_n_hit} track có điểm khớp khác 0</b>
(trên {_n_hit_video} video) &mdash; kể cả các track dưới ngưỡng &mdash; kèm cụm 4 từ trùng nguyên văn
và link YouTube tua thẳng tới giây có cụm đó, để bạn nghe và tự phán quyết.</p>
</div>

<h2 class="pb">3 &middot; Cách kiểm &mdash; và giới hạn của cách kiểm</h2>

<h3>3.1 &middot; Ba bước</h3>
<table>
<thead><tr><th class="c">Bước</th><th>Làm gì</th><th>Kết quả</th></tr></thead>
<tbody>
<tr><td class="c"><b>1</b></td>
 <td><b>Dựng bộ đối chiếu.</b> Liệt kê câu mở đầu (&le;10 từ) của {corpus['n_hymns']} hymn/spiritual
 nổi tiếng nhất dòng gospel/blues Mỹ, kèm năm sáng tác ({_yr_min}&ndash;{_yr_max}).</td>
 <td class="n">{_corpus_pd} bài PD chắc chắn<br>{_corpus_check} bài cần kiểm thêm</td></tr>
<tr><td class="c"><b>2</b></td>
 <td><b>Đo trùng lặp.</b> Cắt lời hát và câu mở đầu hymn thành cụm 4 từ liên tiếp (4-gram),
 đếm bao nhiêu % cụm của hymn xuất hiện <i>y hệt</i> trong bài. Khớp &ge;40% mới tính là có mượn.</td>
 <td class="n">{len(pd_df)} track<br>được chấm</td></tr>
<tr><td class="c"><b>3</b></td>
 <td><b>Tách nhóm phóng tác Kinh Thánh.</b> Không đoán qua từ khoá nội dung (dễ nhầm) mà dựa vào
 tiêu đề <i>tự khai</i> của chính kênh (&ldquo;Psalm 23&rdquo;, &ldquo;Scripture&rdquo;).</td>
 <td class="n">{n_psalm_series} tiêu đề<br>Psalm khác nhau</td></tr>
</tbody>
</table>

<h3>3.2 &middot; Ưu điểm</h3>
<div class="box ok">
<span class="l">Vì sao kết quả đáng tin trong phạm vi đã đo</span>
<p><b>Đo nội dung thật, không đoán qua tên bài.</b> Đây là điểm mạnh chính &mdash; xem mục 3.4 về
trường hợp tên bài đánh lừa.</p>
<p><b>Phân tách rất sạch.</b> {pct(_zero_share)} số track xếp loại &ldquo;sáng tác mới&rdquo; có điểm khớp
<b>đúng bằng 0</b> &mdash; không trùng một cụm 4 từ nào với bất kỳ hymn nào trong bộ đối chiếu.
Không có vùng xám cần phán đoán chủ quan: điểm khớp cao nhất toàn bộ corpus chỉ {vnf(_max_score,3)},
trong khi một bản cover thật sự sẽ cho điểm gần 1,0.</p>
<p><b>Lặp lại được.</b> Toàn bộ nằm trong <code>step_pd_classify.py</code> + corpus JSON &mdash;
chạy lại cho ra đúng kết quả, kiểm chứng được từng bài.</p>
</div>

<h3>3.3 &middot; Nhược điểm &mdash; đọc con số với các giới hạn này</h3>
<div class="box crit">
<span class="l">Bốn giới hạn phải biết</span>
<p><b>1. Chỉ so được với {corpus['n_hymns']} bài trong bộ đối chiếu.</b> Nếu một video mượn hymn PD
ít nổi tiếng <i>không</i> có trong danh sách, hệ thống sẽ xếp nhầm thành &ldquo;sáng tác mới&rdquo;.
Con số {pct(g[g.pd_class=='NEW_COMPOSITION'].pct_video.iloc[0])} vì vậy nghĩa là <b>không khớp {corpus['n_hymns']} hymn phổ biến nhất</b>,
không phải bằng chứng tuyệt đối rằng bài đó không dựa trên bất kỳ tài liệu PD nào.</p>
<p><b>2. Mẫu hẹp: {_n_channel_sample} kênh{f' trên tổng {_tot_ch} kênh của ngách' if _tot_ch else ''}.</b>
{n_video} video có transcript{f' trên {vn(_tot_v)} video toàn ngách' if _tot_v else ''}. Đây là những video
lấy được audio, không phải mẫu ngẫu nhiên đại diện &mdash; kênh nào chặn tải thì không có mặt ở đây.</p>
<p><b>3. Chỉ đo LỜI, không đo GIAI ĐIỆU.</b> Một bài có thể dùng lời mới hoàn toàn nhưng phổ trên
giai điệu hymn cổ &mdash; phương pháp này không phát hiện được. Muốn biết phải so khớp âm thanh
(melodic fingerprint), chưa làm.</p>
<p><b>4. Nhóm &ldquo;mượn hymn PD&rdquo; chỉ có 1 video.</b> Tỷ lệ
{pct(g[g.pd_class=='HYMN_PARTIAL_PD'].pct_video.iloc[0]) if (g.pd_class=='HYMN_PARTIAL_PD').any() else '—'} là
<b>một sự kiện đơn lẻ của một kênh</b>, không phải tỷ lệ ổn định của thị trường. Đừng suy ra xu hướng
từ n=1.</p>
</div>

<h3>3.4 &middot; Vì sao không dùng tiêu đề</h3>
<div class="box warn">
<span class="l">Tên bài từng cho kết quả sai</span>
<p>Kiểm tra ban đầu chỉ dựa vào tiêu đề video từng cho kết quả <b>sai</b>: hai video khác nhau
đều đặt tên "Amazing Grace" của cùng một kênh. Video thứ nhất không có một dòng nào trùng bản
gốc 1779 (chỉ mượn đúng cụm từ "amazing grace" giữa bài) &mdash; là sáng tác mới hoàn toàn dù tên
bài trùng hymn cổ. Video thứ hai mượn đúng 2 dòng mở đầu rồi rẽ sang lời mới từ dòng thứ ba.</p>
<p>Ghi chú cũ trong hồ sơ rủi ro kiếm tiền ("chỉ 19 video/0,3% đặt tên theo thánh ca") đo bằng
tiêu đề &mdash; con số đúng về mặt đếm tên, nhưng không trả lời được câu hỏi bản quyền thật sự.
Báo cáo này đo lại bằng <b>nội dung lời hát thật</b>, không phải tên video.</p>
</div>

<h2>4 &middot; Theo kênh</h2>
<table>
<thead><tr><th>Kênh</th><th>Phân loại</th><th>Số video trong mẫu</th></tr></thead>
<tbody>{_chan_rows}</tbody>
</table>

<h2>5 &middot; Ý nghĩa cho sản xuất</h2>
<div class="box">
<span class="l">Kết luận vận hành</span>
<p><b>Không có lối tắt bản quyền ở ngách này.</b> Toàn bộ 30 video mẫu đều cần lời và giai điệu
tự sáng tác (AI hoặc người) &mdash; kể cả nhóm "dựa trên Psalm" chỉ mượn ý, không mượn được câu chữ
hay nhạc nền có sẵn.</p>
<p>Mô hình phóng tác Psalm ({pct(g[g.pd_class=='SCRIPTURE_PARAPHRASE'].pct_video.iloc[0])} thị phần) là hướng đáng cân nhắc: có sẵn 150 chương
Psalm làm khung chủ đề (không lo hết ý tưởng), quen thuộc với khán giả mục tiêu, nhưng vẫn đòi
hỏi viết lời + phổ nhạc như sáng tác mới.</p>
</div>

</body></html>"""

OUT = D / "NHAC_Ban-quyen-PD.pdf"
HTML(string=DOC, base_url=str(D)).write_pdf(OUT)
print(f"Đã ghi {OUT}")
