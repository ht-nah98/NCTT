#!/usr/bin/env python3
"""T1.2 — MÔ HÌNH KHÁN GIẢ & CƠ CHẾ.

Trả lời: "Người xem là ai? Họ thuê nội dung này làm việc gì, và cơ chế nào
khiến họ chọn video A thay vì B?"

RÀNG BUỘC ĐẶC THÙ: mỗi cơ chế BẮT BUỘC kèm một dự đoán kiểm chứng được
("nếu đúng, làm X sẽ thấy Y"). Cơ chế không có dự đoán thì không phải cơ chế —
nó là lời kể. Script tự đếm và cảnh báo nếu thiếu.

Số liệu gốc KHÔNG lặp ở đây — dẫn chiếu T1.1. Xem 11_OUTPUT_CONTRACT.md §3.

    python3 pipeline/report/build_T12_audience_model.py [niche_path]
"""
import sys
import pathlib
from weasyprint import HTML

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from _t1_common import S, vn, n_of, load, today, doc, source_legend   # noqa: E402
from _common import niche_root                                        # noqa: E402

N = niche_root()
NICHE = N.name
OUT = N / "99_report" / "T1-2_Mo-hinh-khan-gia.pdf"

M = load(N / "_state/metrics.json", {})
AUD = load(N / "05_audience/_metrics_raw.json", {})
KW = load(N / "06_keyword/_metrics_raw.json", {})
au = M.get("audience", {})
kw = M.get("keyword", {})

sig = {s["signal"]: s for s in (AUD.get("signal_tests") or [])}
themes = {t["theme"]: t for t in (KW.get("themes") or [])}
ctx = AUD.get("context") or {}
disc = AUD.get("discovery") or {}
base = AUD.get("baseline_likes", 4.0)


def mech(num, title, claim, evidence, prediction, strength, falsify):
    """Một cơ chế. `prediction` là bắt buộc — không có thì không dựng được."""
    assert prediction, f"Cơ chế {num} thiếu dự đoán kiểm chứng được"
    cls = {"mạnh": "ok", "vừa": "wa", "yếu": "no"}[strength]
    return f"""<div class="mech">
  <div class="mnum">Cơ chế {num}</div>
  <h3>{title}</h3>
  <p class="claim">{claim}</p>
  <table class="mt"><tbody>
    <tr><td class="mk">Bằng chứng</td><td>{evidence}</td></tr>
    <tr><td class="mk">Độ mạnh</td><td class="{cls}">{strength.upper()}</td></tr>
    <tr><td class="mk">Dự đoán</td><td class="pred">{prediction}</td></tr>
    <tr><td class="mk">Bị bác nếu</td><td>{falsify}</td></tr>
  </tbody></table>
</div>"""


# ── JOB-TO-BE-DONE ──────────────────────────────────────────────────────────
top_ctx = sorted(ctx.items(), key=lambda x: -x[1]["n"])[:5]
ctx_rows = "".join(
    f'<tr><td>{k}</td><td class="n">{v["n"]}</td><td class="n">{vn(v["pct"],2)}%</td></tr>'
    for k, v in top_ctx)

jtbd = f"""<h2>1 · Công việc khán giả thuê nội dung này làm</h2>
<div class="box"><h4>Phát biểu job-to-be-done</h4>
<p>“Khi tôi <b>ở một mình và tâm trí đang nặng</b>, tôi muốn <b>một thứ vừa là
âm nhạc vừa là lời cầu nguyện</b>, để tôi <b>không phải chọn giữa gu nhạc của
mình và đức tin của mình</b>.”</p></div>
<p class="small">Đây là <b>giả thuyết</b> rút từ bối cảnh nghe và ngôn ngữ comment,
không phải sự thật đo được. Số liệu nền: xem T1.1 §3.</p>

<h3>Bốn lực</h3>
<table><thead><tr><th>Lực</th><th>Nội dung</th><th>Bằng chứng</th></tr></thead><tbody>
<tr><td class="w">Kéo</td><td>Muốn nhạc hợp gu Blues/Soul mà lời không nghịch đức tin</td>
    <td>{S.Y(f"tín hiệu <i>finally</i> gấp {vn(au.get('finally_like_lift'))}× nền",
             n=sig.get('finally',{}).get('n'))}</td></tr>
<tr><td class="w">Đẩy</td><td>Nhạc Christian trên radio không chạm được họ</td>
    <td>{S.Y("comment <i>cant_stand</i> nhắc trực tiếp lời Blues đời",
             n=sig.get('cant_stand',{}).get('n'))}</td></tr>
<tr><td class="w">Quán tính</td><td>Đã quen playlist/kênh cũ, ngại đổi</td>
    <td>{S.Y(f"<i>repeat</i> {disc.get('repeat',{}).get('n','—')} comment nói nghe lại nhiều lần")}</td></tr>
<tr><td class="w">Lo ngại</td><td>Sợ nhạc “đội lốt” — worship nhẹ gắn mác Blues</td>
    <td>{S.Y("comment đòi 'Blues thật' xuất hiện trong nhóm nói <i>finally</i>", weak=True)}</td></tr>
</tbody></table>

<h3>Bối cảnh nghe</h3>
<table><thead><tr><th>Bối cảnh</th><th class="n">n</th><th class="n">% mẫu</th></tr></thead>
<tbody>{ctx_rows}</tbody></table>
<p>{S.Y("Bối cảnh áp đảo là <b>cầu nguyện / tĩnh nguyện</b> — nghe <b>chủ động</b>, "
        "không phải nhạc nền", n=ctx.get('prayer_devo',{}).get('n'))}</p>
<div class="box gap"><h4>Hệ quả sản xuất</h4>
<p>Nghe chủ động ràng buộc khác hẳn nghe nền: người nghe <b>chú ý tới lời</b>,
nên lời sai chất sẽ bị phát hiện; và họ <b>ở lại lâu</b>, nên mix dài có chỗ.
Ngược lại, nhạc ngủ/ambient là nghe nền — và đó đúng là nhóm chủ đề dữ liệu
bảo tránh (xem T1.1 §3).</p></div>"""

# ── HÀNH TRÌNH KHÁM PHÁ ─────────────────────────────────────────────────────
d_algo = disc.get("algorithm", {}).get("n", 0)
d_search = disc.get("searched", {}).get("n", 0)
disc_rows = "".join(
    f'<tr><td>{k}</td><td class="n">{v["n"]}</td><td class="n">{vn(v["pct"],2)}%</td></tr>'
    for k, v in sorted(disc.items(), key=lambda x: -x[1]["n"]))

journey = f"""<h2>2 · Trigger &amp; hành trình khám phá</h2>
<table><thead><tr><th>Cách tìm thấy</th><th class="n">n</th><th class="n">% mẫu</th></tr></thead>
<tbody>{disc_rows}</tbody></table>
<p>{S.Y(f"Đề xuất thắng tìm kiếm <b>{vn(d_algo/max(d_search,1),1)}:1</b> — "
        "khán giả <b>được đưa tới</b>, không đi tìm", n=d_algo+d_search)}</p>
<div class="box"><h4>Điều này đảo ngược ưu tiên SEO</h4>
<p>Nếu người ta không gõ tìm, thì tối ưu từ khoá tìm kiếm không phải đòn bẩy
chính. Đòn bẩy là <b>chọn đề tài</b> và <b>tín hiệu click</b> để lọt vào luồng
đề xuất. Đây là lý do STEP_06 đã đổi trọng tâm từ SEO sang chọn đề tài.</p></div>
<h3>Họ có tìm ở đâu ngoài YouTube không?</h3>
<p>{S.none("Chưa đo. Cần nguồn P (Spotify/podcast/TikTok) và S (Google Trends) "
           "mới biết cầu này có đang được phục vụ ở nền tảng khác không")}</p>"""

# ── CƠ CHẾ ──────────────────────────────────────────────────────────────────
th = themes.get("thanks", {})
vg = {r["word"]: r for r in (KW.get("voice_gap") or [])}
amen = vg.get("amen", {})

MECHS = [
    mech(1, "Khoảnh khắc tìm thấy mạnh hơn khoảnh khắc đồng cảm",
         "Khán giả phản ứng mạnh nhất không khi được an ủi, mà khi phát hiện ra "
         "một thứ họ đã tìm từ lâu mà không biết là có.",
         S.Y(f"<i>finally</i> {vn(au.get('finally_like_lift'))}× nền và "
             f"<i>never_heard</i> {vn(au.get('never_heard_like_lift'))}× nền, "
             f"cả hai XÁC NHẬN với p &lt; 10⁻⁷. Trong khi <i>healing</i> "
             f"(n={sig.get('healing',{}).get('n','—')}) bị BÁC BỎ",
             n=(sig.get('finally',{}).get('n',0)+sig.get('never_heard',{}).get('n',0))),
         "Nếu đúng, video định vị bằng <b>phát hiện</b> (“thể loại bạn đã tìm cả đời”) "
         "sẽ có tỷ lệ bình luận/view cao hơn video định vị bằng <b>an ủi</b> "
         "(“nhạc cho lúc buồn”) — đo trên ít nhất 20 video mỗi nhóm.",
         "mạnh",
         "Nếu nhóm 'an ủi' đạt tỷ lệ bình luận ngang hoặc cao hơn."),

    mech(2, "Lời cảm tạ là chủ đề duy nhất chịu được kiểm định",
         "Trong 16 chủ đề, chỉ chủ đề <i>cảm tạ</i> thắng cả khi so trong nội bộ "
         "từng kênh — nghĩa là hiệu ứng đến từ chủ đề, không từ kênh mạnh.",
         S.Y(f"lift thô {vn(th.get('lift'),2)}×, lift trong-kênh "
             f"<b>{vn(th.get('within_median_lift'),2)}×</b> (cao hơn thô), "
             f"p = {vn(th.get('p'),3)}", n=th.get("n")),
         "Nếu đúng, khi một kênh đang chạy thêm bài chủ đề cảm tạ vào lịch, "
         "các bài đó sẽ có VPD cao hơn trung vị của chính kênh đó — đo sau 60 ngày.",
         "mạnh",
         "Nếu VPD nhóm cảm tạ không vượt trung vị kênh sau khi kiểm ≥3 kênh."),

    mech(3, "Khán giả và kênh đang nói hai thứ tiếng khác nhau",
         "Kênh đặt tên bằng <b>tên thể loại</b>; khán giả đáp lại bằng "
         "<b>lời cảm tạ</b>. Hai vốn từ gần như không giao nhau.",
         S.Y(f"<i>amen</i> xuất hiện {n_of(amen.get('in_comments',0))} lần trong comment "
             f"nhưng chỉ {amen.get('in_titles','—')} lần trong tiêu đề "
             f"(tỷ lệ {vn(amen.get('ratio'),0)}×). Ngược lại <i>blues</i> "
             f"{n_of(vg.get('blues',{}).get('in_titles',0))} lần trong tiêu đề, "
             f"chỉ {n_of(vg.get('blues',{}).get('in_comments',0))} trong comment",
             n=au.get("n_analyzed"), weak=True),
         "Nếu đúng, A/B đổi tiêu đề sang vốn từ khán giả sẽ nâng CTR trên "
         "impression đề xuất — đo bằng Analytics kênh nhà, 10–20 video mỗi nhánh.",
         "vừa",
         "Nếu CTR hai nhánh không khác nhau có ý nghĩa sau ≥20 video mỗi nhánh."),

    mech(4, "Người cao tuổi phản hồi mạnh nhưng không được nói tới",
         "Nhóm tự nhận cao tuổi có mức tương tác cao vượt trội, trong khi nội dung "
         "hiện tại không viết cho họ — chỉ vẽ họ trên thumbnail.",
         S.Y(f"<i>p_elder</i> trung vị {sig.get('p_elder',{}).get('like_median','—')} like "
             f"so với nền {base} — gấp {vn(sig.get('p_elder',{}).get('vs_baseline'))}×, "
             f"XÁC NHẬN p &lt; 10⁻⁷", n=sig.get('p_elder',{}).get('n')),
         "Nếu đúng, video có lời ở ngôi thứ nhất hồi tưởng (“tôi đã đi qua ngần ấy năm”) "
         "sẽ hút tỷ lệ comment dài (&gt;200 ký tự) cao hơn video mô tả chung chung.",
         "mạnh",
         "Nếu tỷ lệ comment dài không tăng, hoặc nhóm cao tuổi không xuất hiện thêm."),

    mech(5, "Thumbnail là vé vào cửa, không phải đòn bẩy",
         "Không đặc trưng hình ảnh nào phân biệt được video thắng và thua trong ngách. "
         "Làm đúng chuẩn giúp không lạc lõng; làm đẹp hơn chuẩn không giúp thắng.",
         S.Y(f"{M.get('formula',{}).get('features_tested','—')} đặc trưng được kiểm định, "
             f"<b>{M.get('formula',{}).get('features_confirmed','—')}</b> đặc trưng đứng vững "
             f"sau kiểm 3 lớp chống Simpson",
             n=(M.get('formula',{}).get('n_B1',0)+M.get('formula',{}).get('n_B4',0))),
         "Nếu đúng, đầu tư gấp đôi công vào thumbnail mà giữ nguyên nhạc sẽ "
         "<b>không</b> nâng được VPD — trong khi đổi chủ đề nhạc thì có.",
         "mạnh",
         "Nếu một đặc trưng hình ảnh nào đó vượt kiểm định 3 lớp ở ngách khác."),
]

mech_block = ("<h2>3 · Cơ chế — vì sao họ chọn video này</h2>"
              '<p class="small">Mỗi cơ chế kèm một <b>dự đoán kiểm chứng được</b>. '
              'Cơ chế không có dự đoán thì không phải cơ chế.</p>'
              + "".join(MECHS))

# ── BẢN ĐỒ NHÂN QUẢ ─────────────────────────────────────────────────────────
causal = """<h2>4 · Bản đồ nhân–quả</h2>
<table><thead><tr><th>Biến nguyên nhân</th><th>Biến kết quả</th>
<th class="n">Chiều</th><th class="n">Độ mạnh</th><th>Cơ sở</th></tr></thead><tbody>
<tr><td>Chủ đề cảm tạ</td><td>VPD</td><td class="n ok">+</td><td class="n">mạnh</td>
    <td class="small">lift trong-kênh 2,28×</td></tr>
<tr><td>Định vị “phát hiện”</td><td>Tỷ lệ bình luận</td><td class="n ok">+</td>
    <td class="n">mạnh</td><td class="small">finally/never_heard 6×</td></tr>
<tr><td>Chủ đề Kinh Thánh</td><td>VPD</td><td class="n wa">−</td><td class="n">mạnh</td>
    <td class="small">lift 0,61× · 7/13 kênh tệ đi</td></tr>
<tr><td>Chủ đề ngủ/ambient</td><td>VPD</td><td class="n wa">−</td><td class="n">mạnh</td>
    <td class="small">lift 0,24×</td></tr>
<tr><td>Đặc trưng thumbnail</td><td>VPD</td><td class="n no">0</td><td class="n">không</td>
    <td class="small">0/26 đặc trưng đứng vững</td></tr>
<tr><td>Độ dài video</td><td>VPD</td><td class="n no">0</td><td class="n">không</td>
    <td class="small">chênh biến mất khi kiểm trong kênh</td></tr>
<tr><td>Tracklist trong mô tả</td><td>VPD</td><td class="n no">0</td><td class="n">không</td>
    <td class="small">trong-kênh 0,94×</td></tr>
</tbody></table>
<div class="box gap"><h4>Ba biến bằng 0 là phát hiện, không phải thất bại</h4>
<p>Thumbnail, độ dài, tracklist — cả ba đều là thứ thị trường tin là đòn bẩy.
Dữ liệu nói chúng là <b>vé vào cửa</b>. Biết một biến không có tác dụng giúp
dồn công sức vào chỗ có tác dụng.</p></div>"""

# ── MA TRẬN KHOẢNG TRỐNG ────────────────────────────────────────────────────
gap = """<h2>5 · Ma trận khoảng trống</h2>
<p class="small">Cầu có dấu vết, cung chưa đáp ứng. Toàn bộ mục này dựa nguồn
<b>Y</b> nên mang cảnh báo <i>suy gián tiếp</i> — YouTube chỉ thấy cung đã tồn tại.</p>
<table><thead><tr><th>Khoảng trống</th><th>Dấu vết cầu</th><th>Cung hiện tại</th>
<th class="n">Độ chắc</th></tr></thead><tbody>
<tr><td class="w">Vốn từ cảm tạ trong tiêu đề</td>
    <td>amen 2.233 lần trong comment</td><td>5 lần trong tiêu đề</td>
    <td class="n wa">vừa</td></tr>
<tr><td class="w">Chủ đề cảm tạ</td><td>lift trong-kênh 2,28×</td>
    <td>55/5.609 video = 0,98%</td><td class="n ok">mạnh</td></tr>
<tr><td class="w">Nội dung cho người cao tuổi</td>
    <td>p_elder 5,9× nền</td><td>vẽ trên thumbnail, không viết trong lời</td>
    <td class="n ok">mạnh</td></tr>
<tr><td class="w">Blues thật (guitar điện, solo)</td>
    <td>comment đòi “Blues thật”</td><td>guitar điện chỉ 5% bài</td>
    <td class="n wa">vừa</td></tr>
</tbody></table>
<div class="box gap"><h4>Điều không kết luận được từ đây</h4>
<p>Khoảng trống có thể tồn tại vì <b>chưa ai thử</b>, cũng có thể vì
<b>đã thử và không ăn</b>. Dữ liệu YouTube không phân biệt được hai trường hợp.
Chỉ nguồn <b>S</b> (có người tìm không?) và <b>P</b> (nền tảng khác phục vụ chưa?)
mới tách được.</p></div>"""

BODY = jtbd + journey + mech_block + causal + gap + source_legend()

FOOT = f"""<b>Bản chất tài liệu.</b> Đây là <b>giả thuyết có cấu trúc</b>, không phải
sự thật đo được. Số liệu gốc nằm ở <b>T1.1</b> — tài liệu này chỉ dẫn chiếu.
Thông số sản xuất xem <b>T1.3</b>.<br><br>
<b>Cách dùng.</b> Mỗi cơ chế kèm một dự đoán kiểm chứng được. Khi kênh thật chạy,
đối chiếu kết quả với cột “Dự đoán” và cập nhật lại tài liệu này. Cơ chế bị bác
thì <b>xoá</b>, không sửa cho vừa dữ liệu.<br><br>
<b>Giới hạn.</b> Toàn bộ suy luận dựa trên comment YouTube — mẫu chỉ gồm người
chịu bình luận, không đại diện toàn bộ khán giả. Chưa có nguồn <b>V</b> (Reddit,
forum) để đối chứng ngôn ngữ thật, và chưa có <b>N</b> (Analytics kênh nhà) để
đo cơ chế click và giữ chân bằng số thật thay vì suy đoán.<br><br>
<b>Nguồn.</b> <code>05_audience/_metrics_raw.json</code>,
<code>06_keyword/_metrics_raw.json</code>, <code>_state/metrics.json</code>."""

DOC = doc(
    "T1.2", NICHE,
    "Mô hình khán giả<br>&amp; cơ chế",
    "Giả thuyết có cấu trúc về vì sao khán giả tìm, click, ở lại, quay lại — "
    "và điều đó ràng buộc ta phải làm gì.",
    [("Số cơ chế", f"{len(MECHS)} · mỗi cơ chế có dự đoán kiểm chứng được"),
     ("Dựng lúc", today()),
     ("Trả lời", "Họ thuê nội dung này làm việc gì cho họ?"),
     ("Ai đọc", "Người làm nội dung — nhạc, thumbnail, tiêu đề"),
     ("Nhịp cập nhật", "khi có insight mới hoặc dữ liệu kênh thật về")],
    BODY, FOOT)

# CSS riêng cho khối cơ chế
DOC = DOC.replace("</style>", """
.mech { border:.7pt solid #E3DDD5; border-radius:2.5pt; padding:10pt 12pt;
  margin:10pt 0; background:#FEFDFB; page-break-inside:avoid; }
.mnum { font-size:7.5pt; letter-spacing:1.1pt; text-transform:uppercase;
  color:#8C2F39; font-weight:bold; margin-bottom:2pt; }
.mech h3 { margin:0 0 5pt; font-size:11.5pt; }
.claim { font-size:9.5pt; color:#44403C; background:#F7F5F2; border-radius:2pt;
  padding:6pt 8pt; margin:0 0 7pt; }
table.mt { margin:0; }
table.mt td { padding:4pt 0; border-bottom:.5pt solid #F0EBE4; font-size:8.5pt; }
table.mt tr:last-child td { border-bottom:none; }
td.mk { width:26mm; color:#78716C; font-size:7.5pt; letter-spacing:.4pt;
  text-transform:uppercase; padding-right:7pt; }
td.pred { background:#F2F6F3; border-radius:2pt; padding:5pt 7pt; }
</style>""")

if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=DOC, base_url=".").write_pdf(OUT)
    print(f"   -> {OUT.relative_to(N.parent.parent)}  ({OUT.stat().st_size/1024:.0f} KB) "
          f"· {len(MECHS)} cơ chế")
