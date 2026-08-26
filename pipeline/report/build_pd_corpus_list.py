"""BÁO CÁO: Danh sách bộ đối chiếu public domain — nguồn từng bài.

Phụ lục tra cứu cho NHAC_Ban-quyen-PD.pdf: liệt kê đầy đủ các hymn/spiritual
trong corpus, kèm năm xuất bản đầu tiên, ghi công tác giả và link nguồn.
Mọi số liệu đọc động từ hymns_pd.json (T27) — không hard-code.

Link nguồn đã kiểm chứng HTTP 200 ngày ghi trong corpus['source_checked'].
Kiểm lại bất cứ lúc nào:  python3 pipeline/report/build_pd_corpus_list.py --check
"""
import json
import sys
from pathlib import Path

from weasyprint import HTML

CORPUS_PATH = Path("framework/04_reference/pd_corpus/hymns_pd.json")
corpus = json.loads(CORPUS_PATH.read_text())
HYMNS = corpus["hymns"]

# ═══════ chế độ kiểm link (không dựng PDF) ═══════
if "--check" in sys.argv:
    import concurrent.futures as cf
    import urllib.request
    UA = "Mozilla/5.0 (X11; Linux x86_64) Chrome/126.0 Safari/537.36"

    def _chk(h):
        req = urllib.request.Request(h["source_url"], headers={"User-Agent": UA})
        try:
            return h["title"], urllib.request.urlopen(req, timeout=20).status
        except Exception as e:
            return h["title"], getattr(e, "code", "ERR")

    with cf.ThreadPoolExecutor(8) as ex:
        res = list(ex.map(_chk, HYMNS))
    bad = [r for r in res if r[1] != 200]
    print(f"OK: {len(res) - len(bad)}/{len(res)}")
    for t, c in bad:
        print(f"  FAIL {c}  {t}")
    sys.exit(1 if bad else 0)

N = Path(sys.argv[1] if len(sys.argv) > 1 else "niches/christian-blues")
D = N / "99_report"
D.mkdir(parents=True, exist_ok=True)

# ═══════ số liệu đọc động (T27) ═══════
PD = sorted([h for h in HYMNS if h.get("status") == "pd"], key=lambda x: x["year"])
CHECK = sorted([h for h in HYMNS if h.get("status") == "check"], key=lambda x: x["year"])
N_PD, N_CHECK = len(PD), len(CHECK)
YR_MIN, YR_MAX = min(h["year"] for h in HYMNS), max(h["year"] for h in HYMNS)
PD_YR_MAX = max(h["year"] for h in PD)
# Mốc PD Mỹ trượt 1 năm mỗi năm: tác phẩm xuất bản trước (năm hiện tại - 96).
CUTOFF = 1930
N_SPIRITUAL = sum(1 for h in PD if h.get("kind") == "spiritual")
N_HYMN = N_PD - N_SPIRITUAL
CHECKED = corpus.get("source_checked", "—")

KIND_LABEL = {"spiritual": "Spiritual (khuyết danh)", "hymn": "Thánh ca (có tác giả)"}
KIND_CLS = {"spiritual": "kd-s", "hymn": "kd-h"}


def rows(items, start=1):
    out = []
    for i, h in enumerate(items, start):
        kind = h.get("kind", "hymn")
        out.append(
            f'<tr><td class="n">{i}</td>'
            f'<td class="n">{h["year"]}</td>'
            f'<td><b>{h["title"]}</b><br>'
            f'<span class="note">{h.get("author", "")}</span></td>'
            f'<td class="c"><span class="{KIND_CLS[kind]}">{KIND_LABEL[kind]}</span></td>'
            f'<td class="src"><a href="{h["source_url"]}">{h["source_url"].split("/wiki/")[-1]}</a></td>'
            f"</tr>"
        )
    return "\n".join(out)


_pd_rows = rows(PD)
_check_rows = rows(CHECK)

CSS = """
@page { size:A4; margin:16mm 13mm 18mm;
 @bottom-center { content: counter(page) " / " counter(pages);
  font-family:"DejaVu Sans"; font-size:8pt; color:#9A8E85; } }
body { font-family:"DejaVu Sans",sans-serif; font-size:9.5pt; line-height:1.5; color:#1A1614; }
h1 { font-size:21pt; margin:0 0 4pt; letter-spacing:-.4pt; }
h2 { font-size:13pt; margin:16pt 0 7pt; padding-bottom:4pt;
 border-bottom:1.5pt solid #1A1614; page-break-after:avoid; }
p { margin:5pt 0; }
.sub { color:#6B615A; font-size:10.5pt; margin:0 0 10pt; }
.meta { font-size:8pt; color:#7A6F68; border-top:.6pt solid #E2DAD1;
 border-bottom:.6pt solid #E2DAD1; padding:6pt 0; margin-bottom:12pt; }
table { border-collapse:collapse; width:100%; font-size:8.3pt; margin:7pt 0; }
th { background:#F2EEE8; text-align:left; padding:5pt 6pt; font-size:7.2pt;
 text-transform:uppercase; letter-spacing:.4pt; color:#5A514B;
 border-bottom:1pt solid #CFC4B8; }
td { padding:5pt 6pt; border-bottom:.6pt solid #EDE7E0; vertical-align:top; }
tr { page-break-inside:avoid; }
td.n { text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
td.c { text-align:center; white-space:nowrap; }
td.src { font-size:7pt; word-break:break-all; }
td.src a { color:#8C3A2B; text-decoration:none; }
.note { font-size:7.5pt; color:#7A6F68; }
.kd-s { font-size:7pt; color:#2F6B4F; }
.kd-h { font-size:7pt; color:#7A6F68; }
.box { border-left:2.5pt solid #8C3A2B; background:#F9F4F2; padding:8pt 11pt;
 margin:10pt 0; page-break-inside:avoid; }
.box.warn { border-left-color:#B5731F; background:#FBF3E8; }
.box.crit { border-left-color:#9B2C2C; background:#FBEEEE; }
.box.ok { border-left-color:#2F6B4F; background:#EFF5F1; }
.box .l { font-size:7.3pt; text-transform:uppercase; letter-spacing:.7pt;
 font-weight:bold; color:#8C3A2B; display:block; margin-bottom:4pt; }
.box.warn .l { color:#B5731F; }
.box.crit .l { color:#9B2C2C; }
.box.ok .l { color:#2F6B4F; }
.box p { margin:0 0 5pt; font-size:9pt; } .box p:last-child { margin-bottom:0; }
.kpi { display:flex; gap:7pt; margin:10pt 0; }
.kpi div { flex:1; border:.6pt solid #E2DAD1; padding:8pt 9pt; }
.kpi .k { font-size:6.6pt; text-transform:uppercase; letter-spacing:.5pt;
 color:#7A6F68; margin-bottom:4pt; }
.kpi .v { font-size:17pt; font-weight:bold; letter-spacing:-.3pt; }
.kpi .c2 { font-size:6.8pt; color:#7A6F68; margin-top:3pt; line-height:1.3; }
code { background:#F2EEE8; padding:.5pt 3pt; font-size:8pt; }
.pb { page-break-before:always; }
"""

DOC = f"""<!doctype html><html><head><meta charset="utf-8">
<style>{CSS}</style></head><body>

<h1>Bộ đối chiếu public domain</h1>
<p class="sub">{len(HYMNS)} hymn &amp; spiritual dùng làm chuẩn so khớp &mdash; nguồn từng bài</p>
<div class="meta">
Nguồn dữ liệu: <code>{CORPUS_PATH}</code> &nbsp;&middot;&nbsp;
Link kiểm chứng HTTP 200 ngày {CHECKED} &nbsp;&middot;&nbsp;
Phụ lục của báo cáo <b>NHAC_Ban-quyen-PD.pdf</b>
</div>

<div class="kpi">
<div><div class="k">Chắc chắn PD</div><div class="v" style="color:#2F6B4F">{N_PD}</div>
<div class="c2">Xuất bản {YR_MIN}&ndash;{PD_YR_MAX}, đều trước mốc {CUTOFF}</div></div>
<div><div class="k">Cần xác minh</div><div class="v" style="color:#B5731F">{N_CHECK}</div>
<div class="c2">Sau mốc {CUTOFF} &mdash; KHÔNG dùng được cho đến khi tra cứu riêng</div></div>
<div><div class="k">Spiritual khuyết danh</div><div class="v">{N_SPIRITUAL}</div>
<div class="c2">Nhóm an toàn nhất: không có người thừa kế đòi quyền</div></div>
<div><div class="k">Thánh ca có tác giả</div><div class="v">{N_HYMN}</div>
<div class="c2">PD do hết hạn bản quyền, không do khuyết danh</div></div>
</div>

<h2>1 &middot; {N_PD} bài chắc chắn public domain</h2>
<table>
<thead><tr><th style="width:4%">#</th><th style="width:7%">Năm</th>
<th style="width:44%">Bài &mdash; ghi công</th><th style="width:17%">Loại</th>
<th style="width:28%">Nguồn tra cứu</th></tr></thead>
<tbody>{_pd_rows}</tbody>
</table>

<h2 class="pb">2 &middot; {N_CHECK} bài KHÔNG tính là PD &mdash; cần xác minh riêng</h2>
<p>Ba bài này nằm trong bộ đối chiếu để <b>phát hiện</b> trường hợp mượn lời, nhưng
gắn cờ <code>status: "check"</code> &mdash; hệ thống không xếp chúng vào nhóm public domain.
Lý do: năm xuất bản đầu tiên rơi sau mốc {CUTOFF}.</p>
<table>
<thead><tr><th style="width:4%">#</th><th style="width:7%">Năm</th>
<th style="width:44%">Bài &mdash; ghi công</th><th style="width:17%">Loại</th>
<th style="width:28%">Nguồn tra cứu</th></tr></thead>
<tbody>{_check_rows}</tbody>
</table>
<div class="box warn">
<span class="l">Muốn dùng ba bài này thì phải làm gì</span>
<p>Tra cứu trực tiếp US Copyright Office (<code>copyright.gov/public-records</code>) xem bản
quyền có được gia hạn hay không. Tác phẩm Mỹ giai đoạn 1930&ndash;1963 chỉ còn bản quyền
<b>nếu chủ sở hữu đã nộp đơn gia hạn</b> &mdash; rất nhiều tác phẩm không gia hạn và đã rơi vào
public domain, nhưng phải tra mới biết, không suy đoán được.</p>
</div>

<h2>3 &middot; Đọc bảng này thế nào cho đúng</h2>

<div class="box crit">
<span class="l">Ba giới hạn phải nắm trước khi dùng</span>
<p><b>1. "PD" ở đây là PD của LỜI và GIAI ĐIỆU GỐC, không phải của mọi bản thu.</b>
<i>Amazing Grace</i> là public domain, nhưng một bản phối cụ thể năm 1995 vẫn có bản quyền
riêng của bản phối đó. Bạn tự hát/phối lại thì an toàn; lấy bản thu có sẵn thì không.</p>
<p><b>2. Mốc {CUTOFF} tự trượt mỗi năm.</b> Sang 2027 mốc thành {CUTOFF + 1}, sang 2028 thành
{CUTOFF + 2}. File corpus cần rà lại hằng năm &mdash; đây không phải danh sách vĩnh viễn.</p>
<p><b>3. Wikipedia là nguồn TRA CỨU, không phải văn bản pháp lý.</b> Dùng để biết tác giả và
năm xuất bản. Trước khi ra quyết định thương mại có giá trị lớn, đối chiếu thêm PD Info
Project (<code>pdinfo.com</code>) hoặc tra cứu US Copyright Office.</p>
</div>

<div class="box ok">
<span class="l">Nhóm an toàn nhất: {N_SPIRITUAL} spiritual khuyết danh</span>
<p>Các bài như <i>Wade in the Water</i>, <i>Deep River</i>, <i>Steal Away</i>, <i>Balm in Gilead</i>
không có tác giả xác định &mdash; chúng là dân ca truyền miệng thời kỳ nô lệ, được ghi chép lại
từ thập niên 1860. Không tồn tại người thừa kế nào có thể đứng ra đòi quyền, nên rủi ro
thấp hơn cả nhóm thánh ca có tác giả đã hết hạn.</p>
<p>Lưu ý một ngoại lệ trong bảng: <i>Deep River</i> ghi "phối Harry T. Burleigh (1917)" &mdash;
bản dân ca gốc là PD, nhưng <b>bản phối cụ thể của Burleigh</b> là tác phẩm riêng. Đây đúng là
tình huống ở giới hạn số 1 phía trên.</p>
</div>

<div class="box warn">
<span class="l">Một cái bẫy đã có sẵn trong bảng</span>
<p><i>How Great Thou Art</i> (1885) nằm trong nhóm PD vì <b>bài thơ Thụy Điển gốc</b> của Carl
Boberg đã hết bản quyền. Nhưng <b>bản dịch tiếng Anh quen thuộc của Stuart K. Hine (1949)
vẫn còn bản quyền</b>. Hát lời tiếng Anh phổ biến hiện nay là dùng bản dịch có bản quyền,
không phải bản PD. Trường hợp tương tự có thể xảy ra với bất kỳ hymn gốc ngoại ngữ nào.</p>
</div>

<h2>4 &middot; Bộ đối chiếu này dùng vào việc gì</h2>
<p>Đây là chuẩn so khớp của <code>pipeline/analyze/step_pd_classify.py</code>: mỗi track lời hát
được cắt thành các cụm 4 từ liên tiếp, rồi đo xem bao nhiêu phần trăm cụm của câu mở đầu
trong {len(HYMNS)} bài trên xuất hiện nguyên văn trong track. Từ 40% trở lên tính là có mượn lời.</p>
<p class="note">Hệ quả trực tiếp của việc corpus chỉ có {len(HYMNS)} bài: khi báo cáo chính nói
"sáng tác mới hoàn toàn", con số đó có nghĩa chính xác là <b>không khớp {len(HYMNS)} bài trong bảng
này</b> &mdash; một hymn PD ít phổ biến nằm ngoài danh sách sẽ bị xếp nhầm thành sáng tác mới.
Muốn thu hẹp giới hạn đó thì mở rộng corpus, và mọi bài thêm vào đều phải có cột nguồn như trên.</p>

</body></html>"""

out = D / "_phu-luc/PHU-LUC_Bo-doi-chieu-PD.pdf"
out.parent.mkdir(parents=True, exist_ok=True)
HTML(string=DOC).write_pdf(out)
print(f"OK  {out}  ({N_PD} PD + {N_CHECK} cần kiểm)")
