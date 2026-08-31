#!/usr/bin/env python3
"""Xuất bản ĐỊNH VỊ KÊNH ra PDF (A4).

Mỗi định vị = MỘT HƯỚNG KÊNH hoàn chỉnh, có đủ phần thi công:
thumbnail, âm nhạc, cấu trúc bài, công thức tiêu đề, thời lượng.

Khác với các build_report*.py: file này không tính toán lại gì cả. Mọi con số
đã được kiểm chứng khi soạn bản định vị; ở đây chỉ dựng trang in.

Dùng DejaVu Sans như các báo cáo khác trong pipeline — font này có đủ dấu
tiếng Việt, tránh ô vuông trống khi WeasyPrint không tìm được glyph.

    python3 pipeline/report/build_positioning_pdf.py
"""
import pathlib
from weasyprint import HTML

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "niches" / "christian-blues" / "99_report" / "DINH-VI_Christian-Blues.pdf"


def spec_table(rows):
    """Bảng thông số hai cột trong phần thi công."""
    return "\n".join(
        f'<tr><td class="sk">{k}</td><td>{v}</td></tr>' for k, v in rows)


def build(rank, title, sub, chip, chip_cls, ev, src, why,
          thumb, music, struct, titles, avoid):
    """Một định vị = luận điểm + bản thi công đầy đủ."""
    return f"""
<div class="pos">
  <div class="rank">Hướng kênh {rank}</div>
  <h3>{title}</h3>
  <div class="possub">{sub}</div>
  <div class="ev"><span class="chip {chip_cls}">{chip}</span>{ev}
    <span class="src">{src}</span></div>
  <div class="why">{why}</div>

  <div class="blk"><div class="bh">Thumbnail</div>
    <table class="sp">{spec_table(thumb)}</table></div>

  <div class="blk"><div class="bh">Âm nhạc</div>
    <table class="sp">{spec_table(music)}</table></div>

  <div class="blk"><div class="bh">Cấu trúc bài &amp; thời lượng</div>
    <table class="sp">{spec_table(struct)}</table></div>

  <div class="blk"><div class="bh">Công thức tiêu đề</div>
    <div class="tf">{titles}</div></div>

  <div class="blk warn"><div class="bh">Tránh trong hướng này</div>
    <div class="av">{avoid}</div></div>
</div>"""


# ── HƯỚNG 01 ────────────────────────────────────────────────────────────────
H1 = build(
    "01", "Nhạc của lời cảm tạ",
    "Bài hát ở thì <i>sau</i> cơn bão, không phải trong cơn bão.",
    "XÁC NHẬN", "ok",
    "lift 1,62× &nbsp;·&nbsp; trong-kênh 2,28× &nbsp;·&nbsp; p = 0,013",
    "02_theme_scores.csv",
    """<b>Khách hàng:</b> người vừa đi qua chuyện khó và muốn nói lời cảm ơn.
    <b>Vì sao chắc:</b> chỉ số trong-kênh 2,28× cao hơn chỉ số thô 1,62× — cùng một
    kênh làm chủ đề này thì thắng chính mình. Đây là chủ đề duy nhất trong 16 chủ đề
    vượt qua kiểm định Simpson. Cung hiện tại chỉ 55 video trên 5.609 (0,98%).""",
    [("Nhân vật", "Nhánh A “ông già blues” — nam da đen 60–80, râu trắng, mũ fedora. "
                  "Nhưng đổi biểu cảm: <b>mắt mở, ngẩng nhìn lên, mỉm cười nhẹ</b> — "
                  "không phải mắt nhắm đau đớn như phần còn lại của thị trường."),
     ("Đạo cụ", "Micro cổ điển Shure 55, hoặc hai bàn tay mở ngửa. Bỏ guitar nếu đã có micro."),
     ("Ánh sáng", "Chiaroscuro nhưng <b>nâng sáng hơn chuẩn ngách</b>: vùng tối ~50% "
                  "thay vì 61%. Nguồn hổ phách xiên từ trên cao xuống, gợi ánh sáng cửa sổ nhà thờ."),
     ("Màu", "Nền đen #000000 · sáng hổ phách #E8B84B · <b>tuyệt đối tránh xanh lạnh</b> "
             "(nhóm thua dùng 10,3%, nhóm top chỉ 0,7%)"),
     ("Bố cục", "Một người, chiếm 21–35% khung, lệch 1/3 trái hoặc phải. Mặt rõ, nằm nửa trên."),
     ("Chữ", "3 dòng, tổng 12–25% khung. Dòng 1 là <b>câu cảm tạ</b>, không phải tên thể loại.")],
    [("Giọng &amp; điệu thức", "<b>Trưởng (major)</b> — đây là điểm khác biệt cốt lõi. "
                              "Thị trường đã 201/307 bài là trưởng; hướng này đẩy hẳn về trưởng, bỏ thứ."),
     ("Tempo", "88 BPM (trung vị ngách). Có thể nhích 92–100 cho cảm giác nhẹ nhõm."),
     ("Swing", "Tỷ lệ swing 1,32 — giữ chất blues shuffle, đừng làm thẳng nhịp."),
     ("Nhạc cụ", "Guitar (105% bài có) + bass + trống + <b>piano</b>. Tổ hợp "
                 "<i>bass·drums·guitar·piano·vocals</i> là dày nhất trong nhóm dẫn đầu."),
     ("Điểm nhấn", "Thêm organ Hammond hoặc bè hợp xướng nhỏ ở đoạn cuối — "
                   "choir chỉ xuất hiện 5% bài, là chỗ trống dễ tạo dấu ấn."),
     ("Độ ồn", "−13,8 LUFS, dải động LRA 6,6 — chuẩn ngách, đừng nén chặt hơn.")],
    [("Độ dài bài", "3:54 (trung vị ngách), khoảng 3:22–4:40"),
     ("Mở đầu", "Khối đầu ~21 giây. Guitar đơn hoặc piano đơn vào trước."),
     ("Giọng vào", "<b>Giây thứ 4</b> — trung vị ngách. Đừng để intro dài quá 20 giây, "
                   "p75 của thị trường là 21 giây và đó đã là chậm."),
     ("Số khối", "13 khối, mỗi khối ~19,5 giây (khoảng 8 nhịp)"),
     ("Cao trào", "Ở <b>71% bài</b> — tức khoảng phút 2:45 của bài 3:54"),
     ("Thời lượng video", "Bài lẻ &lt;10 phút (view trung vị cao nhất: 149.186) "
                          "hoặc mix 40–80 phút cho bối cảnh cầu nguyện")],
    """<b>Dòng 1 — câu cảm tạ, viết như lời người nghe nói:</b><br>
    “THANK YOU LORD FOR BRINGING ME THROUGH” · “HE DID IT AGAIN” ·
    “I MADE IT OVER”<br><br>
    <b>Dòng 2:</b> “Gospel Blues” · “Songs of Thanksgiving”<br>
    <b>Dòng 3:</b> tên kênh, chữ nghiêng, góc dưới<br><br>
    <span class="hint">Tiêu đề video ~72 ký tự. Đặt từ cảm tạ ở <b>đầu</b> câu,
    tên thể loại đẩy về sau.</span>""",
    "Đừng làm mặt đau khổ, mắt nhắm nghiền — đó là hình ngôn của hướng “than thở” "
    "mà thị trường đã bão hòa. Đừng dùng điệu thứ. Đừng đặt tiêu đề bắt đầu bằng "
    "“Sad” hay “Broken”.")

# ── HƯỚNG 02 ────────────────────────────────────────────────────────────────
H2 = build(
    "02", "Thể loại mà họ đã tìm cả đời",
    "Định vị bằng <b>khoảnh khắc tìm thấy</b>, không phải bằng nỗi buồn.",
    "XÁC NHẬN", "ok",
    "n = 58 &nbsp;·&nbsp; 26,5 vs 4 like &nbsp;·&nbsp; 6,6× nền &nbsp;·&nbsp; p &lt; 0,0000001",
    "04_signal_tests.csv",
    """<b>Khách hàng:</b> người yêu Blues thật nhưng thấy lời Blues đời không hợp
    đức tin — và người mộ đạo lâu năm chưa từng nghe Kinh Thánh trình bày kiểu này.
    <b>Vì sao chắc:</b> hai tín hiệu độc lập cùng XÁC NHẬN với p &lt; 10⁻⁷ —
    <i>finally</i> (26,5 like) và <i>never_heard</i> (25 like), trong khi nền ngách
    là 4 like. Chưa kênh nào định vị trực diện.""",
    [("Nhân vật", "<b>Nhạc công thật</b>, không phải ca sĩ thờ phượng. Nam da đen 50–70, "
                  "ôm guitar bán rỗng (hollow-body), ngón tay đang bấm phím rõ nét."),
     ("Đạo cụ", "Guitar là <b>nhân vật chính</b> — để nó chiếm chỗ ngang người. "
                "Thêm harmonica, ampli đèn cũ. Thánh giá nhỏ ở nền, không phô."),
     ("Ánh sáng", "Chuẩn ngách 61% tối, nhưng thêm <b>khói và đèn sân khấu</b> — "
                  "không gian quán blues, không phải nhà thờ."),
     ("Màu", "Nền đen · hổ phách #E8B84B đậm · 1/6 số ảnh làm <b>đen trắng hoàn toàn</b> "
             "(16,6% ngách đã làm vậy — hợp hướng này nhất)"),
     ("Bố cục", "Cận trung, thấy được tay và mặt. Nền mờ bokeh mạnh (nét giữa gấp ~2× nét biên)."),
     ("Chữ", "Sans-serif đậm viền đen, IN HOA. Hoặc chữ khối kim loại vàng kiểu retro.")],
    [("Giọng &amp; điệu thức", "<b>Thứ (minor)</b> — đây là hướng duy nhất nên dùng thứ, "
                              "vì chất Blues thật đòi hỏi. Thang blues có nốt xanh (blue note) rõ."),
     ("Tempo", "76–88 BPM, chậm. Slow blues 12 ô nhịp."),
     ("Swing", "Đẩy swing lên <b>trên 1,32</b> — shuffle nặng, đây là dấu hiệu Blues thật "
               "phân biệt với worship nhẹ đội lốt Blues."),
     ("Nhạc cụ", "<b>Guitar điện</b> (chỉ 5% ngách dùng — chỗ trống rõ) + bass + trống thật "
                 "+ harmonica + organ. Tránh synth pad."),
     ("Điểm nhấn", "Slide guitar (4% ngách). Solo guitar thật ở giữa bài — "
                   "thị trường gần như không ai làm solo."),
     ("Độ ồn", "−13,8 LUFS nhưng để LRA rộng hơn 6,6 — nhạc thật cần dải động.")],
    [("Độ dài bài", "4:30–6:00, dài hơn chuẩn ngách vì cần chỗ cho solo"),
     ("Mở đầu", "<b>Guitar đơn 15–20 giây</b> — tổ hợp mở đầu phổ biến nhất ngách "
                "(41/307 bài mở bằng guitar đơn). Đây là chỗ khoe chất."),
     ("Giọng vào", "Chậm hơn chuẩn: giây 15–20, sau khi guitar đã nói xong câu đầu"),
     ("Số khối", "13–16 khối. Chèn 1 khối instrumental làm solo ở khoảng 60% bài."),
     ("Cao trào", "71% bài — sau solo, giọng quay lại mạnh nhất"),
     ("Thời lượng video", "Bài lẻ 4–6 phút, hoặc album 40–80 phút. "
                          "<b>Không</b> làm mix &gt;80 phút — hướng này cần nghe chủ động.")],
    """<b>Dòng 1 — khoảnh khắc tìm thấy:</b><br>
    “THE BLUES I'VE BEEN LOOKING FOR” · “REAL BLUES, CLEAN HEART” ·
    “BLUES THAT HONORS HIM”<br><br>
    <b>Dòng 2:</b> “Slow Blues” · “Delta Gospel” — dùng từ chuyên môn để báo hiệu chất thật<br>
    <b>Dòng 3:</b> tên kênh<br><br>
    <span class="hint">Thẻ tag nên có <i>slow blues</i>, <i>delta blues</i>,
    <i>blues guitar</i> — ba thẻ này chỉ xuất hiện ở nhóm thắng.</span>""",
    "Đừng làm nhạc nền ambient hay “relaxing”. Đừng dùng trống máy — nhóm này nghe ra ngay. "
    "Đừng đặt tiêu đề kiểu playlist (“3 Hours of…”).")

# ── HƯỚNG 03 ────────────────────────────────────────────────────────────────
H3 = build(
    "03", "Chứng nhân của một đời dài",
    "Góc nhìn hồi tưởng: một đời đã sống, đã giữ được đức tin.",
    "XÁC NHẬN", "ok",
    "n = 70 &nbsp;·&nbsp; 23,5 vs 4 like &nbsp;·&nbsp; 5,9× nền &nbsp;·&nbsp; p &lt; 0,0000001",
    "04_signal_tests.csv",
    """<b>Khách hàng:</b> người 60–90 tuổi có đức tin lâu năm. <b>Vì sao chắc:</b>
    tín hiệu <i>p_elder</i> XÁC NHẬN, gấp 5,9× nền. Trong 82 người tự khai tuổi,
    trung vị 70 và 64 người từ 60 trở lên. Thị trường đã vẽ đúng chân dung này trên
    thumbnail nhưng chưa viết nội dung cho họ — hình ảnh có, tiếng nói chưa có.""",
    [("Nhân vật", "Nhánh A, nhưng <b>già hơn và tĩnh hơn</b>: 70–85, ngồi, tay đặt trên "
                  "Kinh Thánh cũ hoặc thành ghế. Không hát, đang <b>nhớ lại</b>."),
     ("Đạo cụ", "Kinh Thánh sờn gáy · ảnh gia đình cũ · ghế bập bênh gỗ · "
                "kính lão. <b>Bỏ micro và guitar</b> — đây không phải cảnh biểu diễn."),
     ("Ánh sáng", "Ánh chiều muộn qua cửa sổ, hổ phách rất ấm. Giữ 61% tối "
                  "nhưng bóng mềm hơn, ít tương phản gắt."),
     ("Màu", "Nâu hổ phách #402000 làm chủ đạo thay vì đen tuyền — tông ảnh cũ, ngả sepia"),
     ("Bố cục", "Toàn thân hoặc bán thân, nhân vật nhỏ hơn chuẩn một chút (21–27%), "
                "chừa không gian trống gợi sự tĩnh lặng"),
     ("Chữ", "<b>Serif cổ điển</b>, không phải sans đậm. Chữ nhỏ hơn chuẩn, khiêm nhường.")],
    [("Giọng &amp; điệu thức", "Trưởng, nhưng chậm và trầm. Hòa âm đơn giản, ít biến đổi."),
     ("Tempo", "<b>70–80 BPM</b>, chậm hơn chuẩn ngách. Nhịp đi bộ của người già."),
     ("Swing", "Nhẹ, khoảng 1,2 — đừng shuffle nặng, không hợp giọng kể chuyện."),
     ("Nhạc cụ", "<b>Guitar thùng</b> (12% ngách) + piano + bass đứng (double bass, 12%). "
                 "Bỏ trống hoặc chỉ dùng brush rất nhẹ."),
     ("Giọng hát", "Giọng khàn, có tuổi. Đây là hướng mà chất giọng già là <b>ưu điểm</b>."),
     ("Độ ồn", "−14 LUFS, để dải động rộng cho những đoạn thì thầm")],
    [("Độ dài bài", "4:00–5:00, thong thả"),
     ("Mở đầu", "<b>Guitar thùng đơn hoặc piano đơn</b>, 20–25 giây. Chậm rãi."),
     ("Giọng vào", "Giây 15–22 — chậm, để người nghe kịp lắng xuống"),
     ("Số khối", "10–12 khối, ít hơn chuẩn. Cấu trúc đơn giản, lặp lại nhiều."),
     ("Cao trào", "Nhẹ, ở 71% bài — đây là hướng <b>không</b> cần cao trào mạnh"),
     ("Thời lượng video", "<b>Mix dài 40–80 phút</b> hợp nhất — khán giả nhóm này nghe "
                          "lúc cầu nguyện, buổi sáng, trước khi ngủ")],
    """<b>Dòng 1 — lời chứng ở ngôi thứ nhất:</b><br>
    “I'VE COME THIS FAR BY FAITH” · “EIGHTY YEARS OF MERCY” ·
    “HE NEVER LEFT ME”<br><br>
    <b>Dòng 2:</b> “A Life of Faith” · “Songs of Testimony”<br>
    <b>Dòng 3:</b> tên kênh<br><br>
    <span class="hint">Dùng con số tuổi trong tiêu đề — 29% tiêu đề nhóm top có chứa số,
    và với hướng này con số là bằng chứng của một đời.</span>""",
    "Đừng làm nhạc sôi động. Đừng dùng nhân vật trẻ. Đừng đặt tiêu đề kiểu khích lệ "
    "(“Rise Up”, “Victory”) — nhóm này đang nhìn lại, không đang chiến đấu.")

# ── HƯỚNG 04 ────────────────────────────────────────────────────────────────
H4 = build(
    "04", "Kênh nói bằng tiếng của khán giả",
    "Không phải hướng nội dung — là <b>lớp phủ</b> áp lên ba hướng trên.",
    "GIẢ THUYẾT", "hyp",
    "2.233 vs 5 lần &nbsp;·&nbsp; tỷ lệ 446× &nbsp;·&nbsp; chưa kênh nào test",
    "03_voice_gap.csv",
    """<b>Ý tưởng:</b> giữ nguyên nhạc và hình của hướng 01–03, chỉ đổi <b>cách đặt tên</b>.
    <b>Vì sao đáng thử:</b> <i>amen</i> xuất hiện 2.233 lần trong bình luận nhưng chỉ
    <b>5 lần</b> trong tiêu đề — khoảng cách lớn nhất toàn nghiên cứu, và chỉ là phép đếm.
    <b>Vì sao chỉ là giả thuyết:</b> chưa kênh nào làm, nên không có dữ liệu chứng minh
    nó hiệu quả. Khoảng trống có thể vì chưa ai thử, cũng có thể vì thử rồi không ăn.""",
    [("Thumbnail", "<b>Không đổi gì</b> — dùng nguyên bộ của hướng bạn đã chọn"),
     ("Chỉ đổi dòng chữ", "Thay tên thể loại bằng từ khán giả dùng: "
                          "“AMEN” · “THANK YOU LORD” · “BLESS HIS NAME”"),
     ("Vì sao hợp lý", "Chữ trên ảnh hiện nay lặp lại BLUES (91 lần) · GOSPEL (69) · "
                       "WORSHIP (56) — đúng những từ khán giả <b>ít</b> dùng nhất")],
    [("Âm nhạc", "<b>Không đổi gì</b> — đây là lớp phủ về ngôn ngữ, không phải về nhạc")],
    [("Cấu trúc", "<b>Không đổi gì</b>"),
     ("Cách test", "Chạy A/B trên 10–20 video: một nửa đặt tiêu đề kiểu cũ, "
                   "một nửa kiểu mới. So view/giờ đầu và tỷ lệ click."),
     ("Chi phí", "<b>Rẻ nhất trong bốn hướng</b> — không đụng đến sản xuất")],
    """<b>Bảng đổi từ — trái sang phải:</b><br>
    <span class="sw">blues / gospel / worship</span> →
    <b>amen · thank you Lord · bless · glory · beautiful</b><br><br>
    <b>Ví dụ áp lên hướng 01:</b><br>
    Cũ: “Soulful Christian Blues Worship Playlist”<br>
    Mới: “Thank You Lord — Gospel Blues for a Grateful Heart”<br><br>
    <span class="hint">Giữ 1 từ thể loại để YouTube vẫn hiểu chủ đề, nhưng đẩy về cuối.</span>""",
    "Đừng bỏ hết từ thể loại — thuật toán vẫn cần tín hiệu phân loại. "
    "Đừng áp lớp phủ này khi chưa chọn xong hướng nội dung ở trên.")


DOC = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size:A4; margin:18mm 16mm 20mm;
  @bottom-center {{ content counter(page) " / " counter(pages);
    font-family:"DejaVu Sans"; font-size:8pt; color:#9A8E85; }} }}
@page :first {{ @bottom-center {{ content:""; }} }}

body {{ font-family:"DejaVu Sans",sans-serif; font-size:9.5pt;
  line-height:1.55; color:#1C1917; }}
h1 {{ font-size:26pt; line-height:1.1; margin:0 0 8pt; letter-spacing:-.5pt; }}
h2 {{ font-size:11pt; margin:20pt 0 9pt; padding-bottom:4pt; color:#8C2F39;
  border-bottom:1.5pt solid #1C1917; page-break-after:avoid;
  text-transform:uppercase; letter-spacing:.6pt; }}
h3 {{ font-size:14pt; margin:0 0 2pt; page-break-after:avoid; }}
p {{ margin:6pt 0; }}
i {{ font-style:italic; }}

/* ── trang bìa ── */
.cover {{ padding-top:62mm; page-break-after:always; }}
.eyebrow {{ font-size:8pt; letter-spacing:1.4pt; text-transform:uppercase;
  color:#78716C; margin-bottom:12pt; }}
.stand {{ font-size:12pt; color:#57534E; line-height:1.5;
  margin:10pt 0 0; max-width:118mm; font-style:italic; }}
.rule {{ border:0; border-top:1.5pt solid #1C1917; margin:16pt 0; width:70mm; }}
.covmeta {{ font-size:8.5pt; color:#78716C; line-height:1.8; }}
.covmeta b {{ color:#1C1917; }}

/* ── thẻ hướng kênh ── */
/* KHÔNG dùng page-break-inside:avoid: thẻ dài hơn một trang, ép nguyên khối
   sẽ để lại cả trang trắng. Cho thẻ tự ngắt, chỉ giữ phần đầu dính nhau. */
.pos {{ border:.7pt solid #E3DDD5; border-radius:2.5pt; padding:12pt 13pt 10pt;
  margin:12pt 0; background:#FEFDFB; }}
.pos .rank, .pos h3, .pos .possub, .pos .ev {{ page-break-after:avoid; }}
.rank {{ font-size:7.5pt; letter-spacing:1.1pt; text-transform:uppercase;
  color:#8C2F39; font-weight:bold; margin-bottom:3pt; }}
.possub {{ font-size:9.5pt; color:#57534E; font-style:italic; margin-bottom:7pt; }}
.ev {{ background:#F7EFEF; border:.6pt solid #EBDCDC; border-radius:2pt;
  padding:4.5pt 8pt; font-size:8pt; color:#8C2F39; margin-bottom:8pt; }}
.ev .src {{ float:right; color:#9A8E85; font-size:7.5pt; }}
.chip {{ display:inline-block; font-size:7pt; font-weight:bold; letter-spacing:.5pt;
  padding:1.5pt 5pt; border-radius:2pt; margin-right:7pt; }}
.chip.ok {{ background:#E4EFE8; color:#2D6A4F; }}
.chip.hyp {{ background:#F2E6E6; color:#8C2F39; }}
.why {{ font-size:9pt; color:#44403C; background:#F7F5F2; border-radius:2pt;
  padding:7pt 9pt; margin-bottom:10pt; }}

/* ── khối thi công ── */
/* Cũng KHÔNG avoid ở đây: khối "Âm nhạc"/"Cấu trúc" cao 6-7 dòng, ép nguyên
   khối đẩy cả khối sang trang sau và chừa khoảng trắng cuối trang. Chỉ giữ
   tiêu đề khối dính với dòng đầu (bh có page-break-after:avoid) và không cho
   một dòng thông số bị cắt đôi (tr có page-break-inside:avoid). */
.blk {{ margin-top:9pt; }}
.bh {{ font-size:7.5pt; font-weight:bold; letter-spacing:.9pt; text-transform:uppercase;
  color:#8C2F39; padding-bottom:3pt; margin-bottom:4pt;
  border-bottom:.8pt solid #E3DDD5; page-break-after:avoid; }}
.blk.warn .bh {{ color:#9A6700; }}
table.sp {{ border-collapse:collapse; width:100%; }}
table.sp tr {{ page-break-inside:avoid; }}
table.sp td {{ padding:3.5pt 0; vertical-align:top; font-size:8.5pt;
  border-bottom:.5pt solid #F0EBE4; }}
table.sp tr:last-child td {{ border-bottom:none; }}
td.sk {{ width:31mm; padding-right:7pt; color:#78716C; font-size:7.5pt;
  letter-spacing:.4pt; text-transform:uppercase; }}
.tf {{ font-size:8.5pt; line-height:1.7; }}
/* hai khối này ngắn -> giữ nguyên vẹn được, không gây trang trắng */
.av {{ font-size:8.5pt; color:#6B5A2E; background:#FAF6EC; border-radius:2pt;
  padding:6pt 8pt; page-break-inside:avoid; }}
.hint {{ color:#78716C; font-size:8pt; }}
.sw {{ color:#9A8E85; text-decoration:line-through; }}

/* ── bảng chung ── */
table.d {{ border-collapse:collapse; width:100%; font-size:8.5pt; margin:8pt 0;
  page-break-inside:avoid; }}
table.d th {{ background:#F5F2ED; text-align:left; padding:5pt 7pt; font-size:7.5pt;
  text-transform:uppercase; letter-spacing:.4pt; color:#57534E;
  border-bottom:1pt solid #D6CEC4; }}
table.d td {{ padding:5pt 7pt; border-bottom:.6pt solid #EDE7E0; vertical-align:top; }}
td.n {{ text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }}
td.w {{ font-weight:bold; }}
.wa {{ color:#9A6700; font-weight:bold; }}
.no {{ color:#78716C; font-weight:bold; }}

.box {{ border-left:2.5pt solid #8C2F39; background:#FAF6F5; padding:8pt 11pt;
  margin:10pt 0; page-break-inside:avoid; }}
.box.plain {{ border-left-color:#A8A29E; background:#F7F5F2; }}
.box h4 {{ font-size:9.5pt; margin:0 0 4pt; }}
.box p {{ margin:4pt 0 0; }}
.small {{ font-size:8pt; color:#78716C; }}
.foot {{ margin-top:16pt; padding-top:8pt; border-top:1.5pt solid #1C1917;
  font-size:7.5pt; color:#78716C; line-height:1.65; }}
.foot code {{ font-family:"DejaVu Sans Mono",monospace; font-size:7pt; color:#44403C; }}
</style></head><body>

<div class="cover">
  <div class="eyebrow">Định vị kênh · Ngách Christian Blues</div>
  <h1>Bốn cửa vào<br>Christian Blues</h1>
  <p class="stand">Bốn hướng kênh, mỗi hướng kèm bản thi công: thumbnail, âm nhạc,
    cấu trúc bài, công thức tiêu đề.</p>
  <hr class="rule">
  <div class="covmeta">
    <b>Phạm vi</b> &nbsp; 53 kênh · 6.413 bình luận · 307 bản ghi · 259 thumbnail top 5%<br>
    <b>Phương pháp</b> &nbsp; Kiểm định so sánh trong từng kênh, chống nghịch lý Simpson<br>
    <b>Ngày</b> &nbsp; Hà Nội, 27/08/2026
  </div>
</div>

<h2>Đọc trước</h2>
<p>Mỗi hướng dưới đây là <b>một kênh riêng</b> — chọn một, không trộn. Phần “vì sao”
là bằng chứng đã qua kiểm định; phần thi công là <b>công thức của nhóm dẫn đầu</b>
đã được điều chỉnh cho hướng đó.</p>
<div class="box">
  <h4>Thi công là vé vào cửa, không phải lợi thế</h4>
  <p>Kiểm định riêng trên 259 thumbnail cho thấy <b>không đặc trưng hình ảnh nào</b>
  phân biệt được video thắng/thua trong ngách. Nghĩa là làm đúng công thức giúp bạn
  <b>không lạc lõng</b> và sản xuất nhanh — nhưng thắng hay không phụ thuộc
  <b>âm nhạc</b> và <b>nhịp đăng</b>. Đừng kỳ vọng thumbnail cứu được nội dung yếu.</p>
</div>

<h2>Bốn hướng kênh</h2>
{H1}{H2}{H3}{H4}

<h2>Nền chung cho cả bốn hướng</h2>
<p class="small">Những thông số này giống nhau ở mọi hướng — đo trên nhóm dẫn đầu.</p>
<table class="d">
  <thead><tr><th>Hạng mục</th><th>Chuẩn ngách</th><th>Ghi chú</th></tr></thead>
  <tbody>
    <tr><td class="w">Khung thumbnail</td><td>1280 × 720</td><td>97% dùng chuẩn này</td></tr>
    <tr><td class="w">Người chiếm khung</td><td>27,6%</td><td>khoảng 21–35%</td></tr>
    <tr><td class="w">Chữ chiếm khung</td><td>17,4%</td><td>3 dòng, khoảng 12–25%</td></tr>
    <tr><td class="w">Vùng tối</td><td>61%</td><td>ảnh tối là chuẩn</td></tr>
    <tr><td class="w">Độ ồn</td><td>−13,8 LUFS</td><td>dải động LRA 6,6</td></tr>
    <tr><td class="w">Tiêu đề</td><td>72 ký tự</td><td>khoảng 58–88 · 29% có số</td></tr>
    <tr><td class="w">Nhịp đăng</td><td>4,7 video/tuần</td><td>nhóm dẫn đầu</td></tr>
    <tr><td class="w">Mô tả</td><td>1.337 ký tự</td><td>89% có emoji</td></tr>
  </tbody>
</table>

<h2>Chọn mô hình sản xuất</h2>
<p>Hai mô hình đối lập cùng thành công. Phải chọn <b>một</b> — chúng đòi hỏi khối
lượng công việc khác hẳn nhau.</p>
<table class="d">
  <thead><tr><th></th><th class="n">Nhiều &amp; ngắn</th><th class="n">Ít &amp; dài</th></tr></thead>
  <tbody>
    <tr><td>Thời lượng trung vị</td><td class="n">5,7 phút</td><td class="n">62 phút</td></tr>
    <tr><td>Video mỗi tháng</td><td class="n">8,6</td><td class="n">7,1</td></tr>
    <tr><td>View mỗi video</td><td class="n">42.645</td><td class="n">39.845</td></tr>
    <tr><td>Tỷ lệ hit</td><td class="n">8,8%</td><td class="n">11,0%</td></tr>
    <tr><td>Số kênh trong top 12</td><td class="n">7</td><td class="n">5</td></tr>
  </tbody>
</table>
<p class="small">Không mô hình nào thắng rõ. Chọn theo năng lực sản xuất thật của bạn.</p>

<h2>Những hướng nên tránh</h2>
<p>Các chủ đề sau đang có nhiều kênh làm nhưng kiểm định cho kết quả ngược.</p>
<table class="d">
  <thead><tr><th>Chủ đề</th><th class="n">Quy mô</th><th class="n">Hiệu quả</th><th>Kết luận</th></tr></thead>
  <tbody>
    <tr><td class="w">scripture</td><td class="n">652 video · 11,6%</td><td class="n">0,61×</td><td class="wa">TRÁNH</td></tr>
    <tr><td class="w">instrumental</td><td class="n">58 video · 1,0%</td><td class="n">0,17×</td><td class="wa">TRÁNH</td></tr>
    <tr><td class="w">night_sleep</td><td class="n">283 video · 5,0%</td><td class="n">0,24×</td><td class="no">BÁC BỎ</td></tr>
    <tr><td class="w">healing</td><td class="n">733 video · 13,1%</td><td class="n">0,74×</td><td class="no">BÁC BỎ</td></tr>
    <tr><td class="w">prayer</td><td class="n">1.101 video · 19,6%</td><td class="n">0,98×</td><td class="no">BÁC BỎ</td></tr>
  </tbody>
</table>
<div class="box">
  <h4>Bẫy lớn nhất: Kinh Thánh / Thánh Vịnh</h4>
  <p>652 video, 11,6% thị trường, hiệu quả chỉ <b>0,61×</b>. Kiểm định trên thumbnail
  có tên sách Kinh Thánh cho “XÁC NHẬN”, nhưng soát trong từng kênh thì <b>7 trên 13
  kênh lại tệ đi</b> — đúng dạng nghịch lý Simpson.</p>
</div>

<h2>Việc cần làm tiếp</h2>
<div class="box plain">
  <h4>1 · Chọn một hướng, làm 10 video</h4>
  <p>Đừng trộn hai hướng. Mỗi hướng có bộ thumbnail, âm nhạc, tiêu đề riêng —
  trộn lại thì thuật toán không hiểu kênh nói về gì.</p>
</div>
<div class="box plain">
  <h4>2 · Test lớp phủ ngôn ngữ (hướng 04) song song</h4>
  <p>Không đụng đến sản xuất, chỉ đổi tiêu đề trên một nửa số video.
  Cách rẻ nhất biến giả thuyết mạnh nhất thành bằng chứng.</p>
</div>
<div class="box plain">
  <h4>3 · Gán nhãn giọng hát thủ công trước khi xét hướng giọng nữ</h4>
  <p>Đo tự động cho 79% nam / 13% nữ, nhưng điểm tin cậy quá thấp
  (chênh lệch trung vị 0,06 trên thang 0–1) để dựng định vị lên đó.</p>
</div>

<div class="foot">
  <b>Nguồn.</b> <code>06_keyword/02_theme_scores.csv</code>,
  <code>06_keyword/03_voice_gap.csv</code>, <code>05_audience/04_signal_tests.csv</code>,
  <code>04_outlier/THUMBNAIL_BRIEF.md</code>, <code>04_outlier/07_bible_within_channel.csv</code>,
  <code>03_competitor/PRODUCTION_NORMS.json</code>, <code>09_playbook/_playbook_data.json</code>,
  <code>00_input/raw/audio_dna_full.jsonl</code>.<br><br>
  <b>Phạm vi.</b> 53 kênh · 6.413 bình luận sạch trên 6.794 thu thập · 307 bản ghi âm
  thanh đã tách nhạc cụ · 259 thumbnail và video thuộc top 5% lượt xem. Kiểm định so
  sánh trong từng kênh để chống nghịch lý Simpson.<br><br>
  <b>Giới hạn.</b> Phần thi công mô tả <b>nhóm dẫn đầu đang làm thế nào</b>, không phải
  bằng chứng “làm thế này sẽ thắng” — không đặc trưng hình ảnh nào phân biệt được
  thắng/thua ở mức có ý nghĩa thống kê. Mô tả nhân vật là nhân vật hư cấu trong ảnh AI,
  không suy diễn về khán giả thật. Trích dẫn đã bỏ định danh.
</div>

</body></html>"""

if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=DOC, base_url=".").write_pdf(OUT)
    print(f"   -> {OUT.relative_to(ROOT)}  ({OUT.stat().st_size/1024:.0f} KB)")
