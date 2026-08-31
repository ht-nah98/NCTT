#!/usr/bin/env python3
"""T1.4 — THẺ ĐỐI THỦ (Competitor Card) — mỗi kênh một thẻ.

Trả lời: "Kênh này thắng bằng cái gì, và ta học/né được gì?"

CHỈ 5–10 kênh: nhóm dẫn đầu + kênh breakout + outlier phá luật. Không làm cho
tất cả. Mỗi thẻ tối đa 1–2 trang.

Điểm phân biệt của thẻ: tách rõ ĐIỂM MẠNH KHÔNG COPY ĐƯỢC (tuổi kênh, thư viện
cũ, thương hiệu) khỏi ĐIỂM YẾU KHAI THÁC ĐƯỢC (chỗ họ bỏ trống). Bảng số liệu
thuần tuý không làm được việc đó — nên phần này suy ra từ dữ liệu theo quy tắc
cố định, ghi rõ ở §quy_tac bên dưới.

Xem framework/00_system/11_OUTPUT_CONTRACT.md §5.

    python3 pipeline/report/build_T14_competitor_cards.py [niche_path]
"""
import sys
import csv
import pathlib
from weasyprint import HTML

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from _t1_common import S, vn, n_of, load, today, doc, source_legend   # noqa: E402
from _common import niche_root                                        # noqa: E402

N = niche_root()
NICHE = N.name
OUT = N / "99_report" / "T1-4_The-doi-thu.pdf"

PROF = load(N / "09_playbook/CHANNEL_PROFILES.json", {})
M = load(N / "_state/metrics.json", {})
profiles = PROF.get("profiles") or []
lesson = PROF.get("bài_học") or {}

# bảng kênh đầy đủ — để lấy tier và model cho từng handle
chan = {}
p_ch = N / "03_competitor/02_channel_table.csv"
if p_ch.exists():
    for r in csv.DictReader(p_ch.open(encoding="utf-8")):
        chan[r.get("handle", "")] = r


def months_between(a, b):
    """Số tháng giữa hai chuỗi ngày YYYY-MM-DD."""
    try:
        ya, ma = int(a[:4]), int(a[5:7])
        yb, mb = int(b[:4]), int(b[5:7])
        return (yb - ya) * 12 + (mb - ma)
    except (ValueError, TypeError, IndexError):
        return None


def strengths_weaknesses(p):
    """Tách điểm mạnh không copy được khỏi điểm yếu khai thác được.

    QUY TẮC (cố định, không tuỳ hứng):
      KHÔNG COPY ĐƯỢC = thứ cần THỜI GIAN hoặc TÀI SẢN có sẵn
        · kênh lập trước 2020 (thư viện + tín nhiệm tích luỹ)
        · subscriber > 100k (đòn bẩy đề xuất)
        · thư viện > 300 video (bề mặt tìm kiếm)
      KHAI THÁC ĐƯỢC = chỗ họ BỎ TRỐNG, ta vào được ngay
        · tỷ lệ hit thấp (< 10%) -> chất lượng không đều
        · hệ số biến thiên cao (> 4) -> phụ thuộc vài video may mắn
        · không dùng kiểu tiêu đề cảm tạ -> bỏ trống vốn từ khán giả
        · nhịp đăng > 8 video/tuần -> khó giữ chất, dễ loãng
    """
    q, s = p.get("quy_mô", {}), p.get("sản_xuất", {})
    created = p.get("channel_created", "") or ""
    strong, weak = [], []

    if created[:4] and created[:4] < "2020":
        strong.append(f"Kênh lập từ {created[:4]} — thư viện và tín nhiệm tích luỹ "
                      f"{months_between(created, p.get('latest_video','')) or '?'} tháng, "
                      "không mua được bằng tiền")
    if (p.get("subscribers") or 0) > 100000:
        strong.append(f"{n_of(p['subscribers'])} người đăng ký — mỗi video mới có "
                      "sẵn cú hích đề xuất ban đầu")
    if (q.get("số_video") or 0) > 300:
        strong.append(f"{n_of(q['số_video'])} video — bề mặt tìm kiếm rộng, "
                      "cần nhiều năm để bắt kịp")
    if s.get("khởi_đầu") == "nổ_ngay" and (s.get("tháng_đến_video_đầu_tiên_vượt_ngưỡng") or 9) < 1:
        strong.append("Video đầu tiên đã vượt ngưỡng — có thể do tài sản sẵn có "
                      "hoặc quảng bá ngoài, không tái lập được bằng quy trình")

    hit = q.get("tỷ_lệ_hit")
    if hit is not None and hit < 0.10:
        weak.append(f"Tỷ lệ hit chỉ {vn(100*hit,1)}% — {vn(100*(1-hit),0)}% video "
                    "không đạt ngưỡng, chất lượng không đều")
    cv = q.get("hệ_số_biến_thiên")
    if cv and cv > 4:
        weak.append(f"Hệ số biến thiên {vn(cv,1)} — tổng view phụ thuộc vài video "
                    "đột biến, không phải nền tảng ổn định")
    tit = (p.get("công_thức_tiêu_đề") or {}).get("phân_bố") or {}
    if tit.get("kinh_thánh", 0) > 0.10:
        weak.append(f"{vn(100*tit['kinh_thánh'],0)}% tiêu đề dùng Kinh Thánh — "
                    "hướng có hiệu quả 0,61× toàn ngách")
    wk = s.get("video_mỗi_tuần")
    if wk and wk > 8:
        weak.append(f"Đăng {vn(wk,1)} video/tuần — nhịp cao khó giữ chất, "
                    "trung vị view đang loãng dần")
    desc = (p.get("cấu_trúc_mô_tả") or {})
    if (desc.get("có_tracklist") or 0) < 0.2:
        weak.append("Ít dùng tracklist trong mô tả — bỏ trống một điểm chạm "
                    "(dù tracklist không phải yếu tố thắng)")
    if not weak:
        weak.append("Chưa thấy điểm yếu rõ trong dữ liệu hiện có")
    return strong, weak


def trajectory(p):
    """Đọc quỹ đạo: đang lên hay đang loãng."""
    tr = p.get("quỹ_đạo") or []
    if len(tr) < 4:
        return None, ""
    first3 = [x["med_view"] for x in tr[:3]]
    last3 = [x["med_view"] for x in tr[-3:]]
    a = sum(first3) / len(first3)
    b = sum(last3) / len(last3)
    ratio = b / a if a else None
    if ratio is None:
        return None, ""
    if ratio >= 1.2:
        return ratio, '<span class="ok">đang lên</span>'
    if ratio <= 0.8:
        return ratio, '<span class="wa">đang loãng</span>'
    return ratio, '<span class="no">đi ngang</span>'


def card(i, p):
    q, s = p.get("quy_mô", {}), p.get("sản_xuất", {})
    t = p.get("công_thức_tiêu_đề", {})
    d = p.get("cấu_trúc_mô_tả", {})
    strong, weak = strengths_weaknesses(p)
    ratio, traj_txt = trajectory(p)
    row = chan.get(p.get("handle", ""), {})

    age = months_between(p.get("channel_created", ""), p.get("latest_video", ""))
    ex = "".join(
        f'<tr><td class="small">{e["title"][:88]}</td>'
        f'<td class="n">{n_of(e["views"])}</td></tr>'
        for e in (t.get("ví_dụ_top") or [])[:3])
    shapes = "".join(
        f'<tr><td>{k.replace("_"," ")}</td><td class="n">{vn(100*v,1)}%</td></tr>'
        for k, v in sorted((t.get("phân_bố") or {}).items(), key=lambda x: -x[1])[:4])

    strong_li = "".join(f"<li>{x}</li>" for x in strong) or "<li>—</li>"
    weak_li = "".join(f"<li>{x}</li>" for x in weak)

    # bài học: rút từ chỗ kênh này khác biệt nhất so với chuẩn ngách
    if s.get("mô_hình") == "nhiều_và_ngắn":
        take = ("Mô hình <b>nhiều &amp; ngắn</b>: ăn bằng khối lượng và tần suất "
                "đề xuất. Đòi hỏi dây chuyền sản xuất chạy đều — không hợp nếu "
                "làm thủ công từng bài.")
    elif s.get("mô_hình") == "ít_và_dài":
        take = ("Mô hình <b>ít &amp; dài</b>: ăn bằng thời lượng xem và số điểm "
                "quảng cáo. Ít video hơn nhưng mỗi video phải giữ chân được lâu.")
    else:
        take = "Mô hình chưa phân loại rõ."

    return f"""<div class="card">
<div class="chead">
  <div class="cnum">Thẻ {i:02d}</div>
  <h3>{p.get('channel_name') or p.get('handle')}</h3>
  <div class="curl">@{p.get('handle','')} · {p.get('country','—')}</div>
</div>

<table class="kv"><tbody>
<tr><td class="kk">Người đăng ký</td><td class="n">{n_of(p.get('subscribers',0))}</td>
    <td class="kk kk2">Tổng view</td><td class="n">{n_of(q.get('tổng_view',0))}</td></tr>
<tr><td class="kk">Số video</td><td class="n">{n_of(q.get('số_video',0))}</td>
    <td class="kk kk2">View trung vị</td><td class="n">{n_of(q.get('view_trung_vị',0))}</td></tr>
<tr><td class="kk">Tuổi kênh</td><td class="n">{age or '—'} tháng</td>
    <td class="kk kk2">Video đỉnh</td><td class="n">{n_of(q.get('video_đỉnh',0))}</td></tr>
<tr><td class="kk">Tỷ lệ hit</td><td class="n">{vn(100*(q.get('tỷ_lệ_hit') or 0),1)}%</td>
    <td class="kk kk2">Tầng</td><td class="n">{row.get('tier','—')}</td></tr>
</tbody></table>

<h4>Lịch sử tăng trưởng</h4>
<p class="small">Lập {p.get('channel_created','—')} · video đầu {p.get('first_video','—')}
{f"· <b>ngủ {months_between(p.get('channel_created',''), p.get('first_video',''))} tháng rồi hồi sinh</b>"
  if (months_between(p.get('channel_created',''), p.get('first_video','')) or 0) > 24 else ""}
· khởi đầu <b>{(s.get('khởi_đầu') or '—').replace('_',' ')}</b>
{f"· quỹ đạo {traj_txt} ({vn(ratio,2)}× so với 3 tháng đầu)" if ratio else ""}</p>

<h4>Format &amp; lịch đăng</h4>
<table><tbody>
<tr><td class="w">Mô hình</td><td>{(s.get('mô_hình') or '—').replace('_',' ')}</td></tr>
<tr><td class="w">Thời lượng</td><td>trung vị {vn(s.get('thời_lượng_trung_vị_phút'))} phút</td></tr>
<tr><td class="w">Nhịp đăng</td><td>{vn(s.get('video_mỗi_tuần'))} video/tuần</td></tr>
</tbody></table>

<h4>Hệ thống tiêu đề</h4>
<table><tbody>{shapes}</tbody></table>
<p class="small">Dấu phân cách <b>{t.get('dấu_phân_cách','—')}</b> ·
độ dài trung vị {t.get('độ_dài_trung_vị','—')} ký tự</p>
<table><thead><tr><th>Tiêu đề mạnh nhất</th><th class="n">View</th></tr></thead>
<tbody>{ex}</tbody></table>

<h4>Mô tả &amp; kiếm tiền quan sát được</h4>
<p class="small">Mô tả {n_of(d.get('độ_dài_trung_vị',0))} ký tự ·
emoji {vn(100*(d.get('có_emoji') or 0),0)}% ·
membership {vn(100*(d.get('có_membership') or 0),0)}% ·
tracklist {vn(100*(d.get('có_tracklist') or 0),0)}%
{"· có link nền tảng nhạc (Spotify/Apple/Amazon)" if any(
    k in (d.get('từ_khóa') or []) for k in ('spotify','apple','amazon')) else ""}</p>

<table class="two"><tbody><tr>
  <td class="col nocopy"><div class="ch">Mạnh — không copy được</div>
    <ul>{strong_li}</ul></td>
  <td class="col exploit"><div class="ch">Yếu — khai thác được</div>
    <ul>{weak_li}</ul></td>
</tr></tbody></table>

<div class="take"><b>Bài học rút ra.</b> {take}</div>
</div>"""


cards = "".join(card(i, p) for i, p in enumerate(profiles, 1))

# ── bảng tổng &amp; bài học chung ────────────────────────────────────────────
sum_rows = "".join(
    f'<tr><td class="w">{p.get("handle")}</td>'
    f'<td class="n">{n_of(p.get("quy_mô",{}).get("tổng_view",0))}</td>'
    f'<td class="n">{n_of(p.get("quy_mô",{}).get("số_video",0))}</td>'
    f'<td class="n">{vn(100*(p.get("quy_mô",{}).get("tỷ_lệ_hit") or 0),1)}%</td>'
    f'<td>{(p.get("sản_xuất",{}).get("mô_hình") or "—").replace("_"," ")}</td>'
    f'<td>{(p.get("sản_xuất",{}).get("khởi_đầu") or "—").replace("_"," ")}</td></tr>'
    for p in profiles)

revive = lesson.get("kênh_cũ_hồi_sinh") or []
revive_txt = " · ".join(f"{r['handle']} (lập {r['lập'][:4]}, video đầu {r['video_đầu'][:7]})"
                        for r in revive)

overview = f"""<h2>Bảng tổng — {len(profiles)} kênh được chọn</h2>
<p class="small">Chọn theo tổng view trên video dài đã đủ tuổi. Ngưỡng hit:
{n_of(PROF.get('cohort',{}).get('ngưỡng_hit',0))} view.</p>
<table><thead><tr><th>Kênh</th><th class="n">Tổng view</th><th class="n">Video</th>
<th class="n">Hit</th><th>Mô hình</th><th>Khởi đầu</th></tr></thead>
<tbody>{sum_rows}</tbody></table>

<div class="box"><h4>Ba điều bảng này nói</h4>
<p>1 · {S.Y(f"Hai mô hình <b>đối lập</b> cùng thắng: "
            f"{lesson.get('phân_bố_mô_hình',{}).get('nhiều_và_ngắn','—')} kênh nhiều &amp; ngắn, "
            f"{lesson.get('phân_bố_mô_hình',{}).get('ít_và_dài','—')} kênh ít &amp; dài. "
            "Phải chọn một trước khi sản xuất")}</p>
<p>2 · {S.Y(f"Tỷ lệ hit cao nhất thuộc <b>{lesson.get('tỷ_lệ_hit_cao_nhất',{}).get('handle','—')}</b> "
            f"({vn(100*(lesson.get('tỷ_lệ_hit_cao_nhất',{}).get('giá_trị') or 0),1)}%) — "
            "không phải kênh tổng view lớn nhất. Chất khác lượng")}</p>
<p>3 · {S.Y(f"Kênh cũ hồi sinh: {revive_txt}. Tài khoản lập từ lâu rồi bỏ, "
            "nay đăng lại — tuổi kênh là tài sản không mua được"
            if revive else "Chưa ghi nhận kênh hồi sinh")}</p></div>

<div class="box gap"><h4>Điều thẻ đối thủ KHÔNG nói được</h4>
<p>Mọi số ở đây là <b>quan sát từ bên ngoài</b>. Không biết được retention thật,
CTR thật, nguồn traffic, hay doanh thu thật của họ — YouTube API không trả về
cho kênh người khác. Mô hình kiếm tiền chỉ suy từ dấu hiệu công khai
(membership, link nền tảng nhạc trong mô tả).</p>
<p class="small">{S.none("Retention · CTR · traffic source · doanh thu — cần nguồn N "
                         "(Analytics kênh nhà) và chỉ đo được cho kênh của mình")}</p></div>"""

BODY = overview + "<h2>Thẻ từng kênh</h2>" + cards + source_legend()

FOOT = f"""<b>Bản chất tài liệu.</b> Hồ sơ sâu {len(profiles)} kênh đáng học —
nhóm dẫn đầu, kênh breakout, outlier phá luật. <b>Không</b> làm cho tất cả
{M.get('market',{}).get('M1_2_total_channels','—')} kênh trong mẫu.<br><br>
<b>Cách phân loại mạnh/yếu.</b> Theo quy tắc cố định, không tuỳ hứng:
<i>không copy được</i> = cần thời gian hoặc tài sản có sẵn (tuổi kênh &lt;2020,
&gt;100k đăng ký, &gt;300 video). <i>Khai thác được</i> = chỗ bỏ trống ta vào ngay
(hit &lt;10%, hệ số biến thiên &gt;4, tiêu đề Kinh Thánh &gt;10%, nhịp &gt;8/tuần).<br><br>
<b>Nguồn.</b> <code>09_playbook/CHANNEL_PROFILES.json</code>,
<code>03_competitor/02_channel_table.csv</code>, <code>_state/metrics.json</code>.<br><br>
<b>Nhịp cập nhật.</b> Làm 1 lần, soát lại mỗi quý. Số liệu chụp tại thời điểm
crawl — kênh có thể đã đổi hướng."""

DOC = doc(
    "T1.4", NICHE,
    "Thẻ đối thủ",
    f"Hồ sơ sâu {len(profiles)} kênh đáng học — thắng bằng cái gì, "
    "và ta học hay né được gì.",
    [("Số thẻ", f"{len(profiles)} kênh"),
     ("Dựng lúc", today()),
     ("Trả lời", "Kênh này thắng bằng cái gì?"),
     ("Ai đọc", "Người học chiến thuật cụ thể"),
     ("Nhịp cập nhật", "làm 1 lần, soát lại mỗi quý")],
    BODY, FOOT)

DOC = DOC.replace("</style>", """
/* KHÔNG page-break-inside:avoid — thẻ cao gần trọn trang, ép nguyên khối sẽ
   đẩy cả thẻ sang trang sau và để lại một trang trắng. Chỉ giữ phần đầu thẻ
   dính với nội dung đầu tiên. */
.card { border:.7pt solid #E3DDD5; border-radius:2.5pt; padding:11pt 13pt 9pt;
  margin:11pt 0; background:#FEFDFB; }
.chead { border-bottom:1.2pt solid #1C1917; padding-bottom:5pt; margin-bottom:8pt;
  page-break-after:avoid; }
.cnum { font-size:7.5pt; letter-spacing:1.1pt; text-transform:uppercase;
  color:#8C2F39; font-weight:bold; }
.card h3 { margin:2pt 0 1pt; font-size:13pt; }
.curl { font-size:8pt; color:#78716C; }
.card h4 { font-size:8pt; letter-spacing:.8pt; text-transform:uppercase;
  color:#8C2F39; margin:9pt 0 3pt; page-break-after:avoid; }
/* Bảng 2x2 thông số. table-layout:fixed + width TỪNG cột: nếu chỉ đặt width
   cho cột nhãn, cột số co lại vừa khít chữ và nhãn cặp thứ hai dán liền vào
   số của cặp thứ nhất ("65.600TỔNG VIEW"). Bốn cột phải cộng đủ 100%. */
table.kv { margin:0 0 4pt; table-layout:fixed; width:100%; }
table.kv td { padding:3.5pt 0; border-bottom:.5pt solid #F0EBE4; font-size:8.5pt; }
table.kv td:nth-child(1) { width:27%; }
table.kv td:nth-child(2) { width:21%; padding-right:9pt; }
table.kv td:nth-child(3) { width:29%; padding-left:9pt; }
table.kv td:nth-child(4) { width:23%; }
td.kk { color:#78716C; font-size:7pt; letter-spacing:.3pt; text-transform:uppercase; }

/* WeasyPrint KHÔNG dựng được flexbox -> hai cột phải là bảng thật, nếu không
   cả khối biến mất khỏi bản in mà không báo lỗi. */
table.two { margin-top:9pt; table-layout:fixed; border-collapse:separate;
  border-spacing:6pt 0; }
td.col { border-radius:2pt; padding:7pt 9pt; width:50%; vertical-align:top;
  border-bottom:none; }
td.col ul { margin:3pt 0 0; padding-left:11pt; }
td.col li { font-size:8pt; margin:2.5pt 0; line-height:1.45; }
td.nocopy { background:#F7F5F2; border-left:2pt solid #A8A29E; }
td.exploit { background:#FAF6EC; border-left:2pt solid #9A6700; }
.ch { font-size:7.5pt; font-weight:bold; letter-spacing:.6pt;
  text-transform:uppercase; color:#57534E; }
.take { margin-top:8pt; background:#F7EFEF; border-left:2pt solid #8C2F39;
  border-radius:0 2pt 2pt 0; padding:6pt 9pt; font-size:8.5pt; }
</style>""")

if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=DOC, base_url=".").write_pdf(OUT)
    print(f"   -> {OUT.relative_to(N.parent.parent)}  ({OUT.stat().st_size/1024:.0f} KB) "
          f"· {len(profiles)} thẻ")
