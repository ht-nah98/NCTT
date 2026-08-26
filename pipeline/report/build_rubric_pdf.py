"""Sinh PDF cho KHUNG CHẤM ĐIỂM — framework/00_system/03_SCORING_RUBRIC.md.

CHẠY: python3 pipeline/report/build_rubric_pdf.py [niche_path]

KHÁC VỚI CÁC BUILDER KHÁC: đây là tài liệu **khung chung**, không thuộc ngách nào.
Nhưng nó vẫn đọc `scores.json` của một ngách để làm **ví dụ minh họa** — nhờ vậy
con số trong PDF không bao giờ lệch với điểm thật (bài học T27).

Ngưỡng in ra lấy từ `apply_thresholds.py` (nguồn duy nhất), không gõ lại.
"""
import json, sys, warnings
from pathlib import Path
from weasyprint import HTML
warnings.filterwarnings("ignore")

N = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--")
         else "niches/christian-blues")
SC = json.load(open(N/"_state/scores.json"))
AX = SC["axes"]


def vn(x, nd=None):
    """Số kiểu Việt: dấu phẩy thập phân, bỏ số 0 thừa."""
    s = f"{x:.{nd}f}" if nd is not None else f"{x:g}"
    return s.replace(".", ",")


# ── Bảng ví dụ: đọc điểm THẬT, tự tính đóng góp ──────────────────────────
AXIS_NAME = {"T1": "Quy mô thị trường", "T2": "Động lượng tăng trưởng",
             "T3": "Cửa gia nhập", "T4": "Phù hợp sản xuất AI",
             "T5": "Giá trị kiếm tiền"}
CONF_VN = {"high": "Cao", "medium": "Vừa", "low": "Thấp"}

rows, raw = [], 0.0
for k in ["T1", "T2", "T3", "T4", "T5"]:
    a = AX[k]; s, w = a["score"], a["weight"]
    contrib = s * w * 4          # ×4 để đưa thang 0–5 về 0–20
    raw += contrib
    rows.append(
        f'<tr><td><b>{k}</b> · {AXIS_NAME[k]}</td>'
        f'<td class="c"><b>{vn(s)}</b></td><td class="n">{w*100:.0f}%</td>'
        f'<td class="n">{vn(contrib, 2)}</td>'
        f'<td class="c">{CONF_VN.get(a.get("confidence",""), "—")}</td></tr>')

T6 = SC["T6"]
t6_pen = T6 if isinstance(T6, (int, float)) else T6.get("penalty", 0)
rows.append(f'<tr><td><b>T6</b> · Rủi ro <i>(điểm trừ)</i></td>'
            f'<td class="c"><b>−{vn(abs(t6_pen))}</b></td><td class="c">—</td>'
            f'<td class="n dn">−{vn(abs(t6_pen), 2)}</td><td class="c">—</td></tr>')
rows.append(f'<tr class="hi"><td><b>TỔNG</b></td><td class="c">—</td><td class="n">100%</td>'
            f'<td class="n"><b>{vn(SC["total_score"], 2)} / 20</b></td>'
            f'<td class="c">—</td></tr>')
score_rows = "\n".join(rows)

TOTAL = vn(SC["total_score"], 2)
VERDICT = SC.get("verdict", "—")

# M3.3 có đo được không → quyết định có hiện hộp ghi chú T3 hay không.
# Trạng thái nằm ở metrics.json (entry.M3_3_status), KHÔNG ở scores.json.
try:
    _M = json.load(open(N/"_state/metrics.json"))
    M33_FIXED = "KHÔNG ĐO ĐƯỢC" in str(_M.get("entry", {}).get("M3_3_status", ""))
except FileNotFoundError:
    _M, M33_FIXED = {}, False


# ── BẢNG DẪN XUẤT: số thô → ngưỡng chạm → điểm ───────────────────────────
# Đây là thứ trả lời "vì sao ra con số đó". `_meta.derivation` đã có sẵn trong
# metrics.json từ apply_thresholds.py nhưng chưa báo cáo nào hiển thị (T36).
def fnum(x):
    """Số lớn → dạng dễ đọc (7.450.227 → 7,45tr)."""
    if not isinstance(x, (int, float)): return str(x)
    if abs(x) >= 1e6: return f"{x/1e6:.2f}tr".replace(".", ",")
    if abs(x) >= 1e3: return f"{x:,.0f}".replace(",", ".")
    return vn(round(x, 3))


_g = lambda grp, k: _M.get(grp, {}).get(k)
_rpm = _g("money", "M5_2_rpm_range")
_rpm_mid = _rpm[1] if isinstance(_rpm, list) and len(_rpm) >= 2 else _rpm

DERIV = [
    ("T1", "M1.1 · view/tháng", fnum(_g("market", "M1_1_views_per_month")),
     "khoảng 3–8tr", AX["T1"]["score"]),
    ("T2", "M2.1 · tăng trưởng view", vn(round(_g("momentum", "M2_1_view_growth") or 0, 3)),
     "≥1,5 kèm M2.4 ≥1,0", AX["T2"]["score"]),
    ("", "M2.4 · cầu/cung", vn(round(_g("momentum", "M2_4_demand_supply_gap") or 0, 3)),
     "đạt → không tụt bậc", ""),
    ("T3", "M3.2 · người mới thành công",
     f'{(_g("entry","M3_2_newcomer_success_pct") or 0):.1f}%'.replace(".", ","),
     "≥40% → 5đ", AX["T3"]["score"]),
    ("", "M3.1 · Gini", vn(round(_g("entry", "M3_1_gini") or 0, 3)),
     "0,55–0,65 → 3đ", ""),
    ("", "M3.3 · thời gian đạt traction", "KHÔNG ĐO ĐƯỢC",
     "chia lại trọng số 0,3:0,5", ""),
    ("T4", "M4.1 · kênh top là AI-first",
     f'{(_g("ai_fit","M4_1_ai_first_top20_pct") or 0):.0f}%',
     "≥60% → 5đ", AX["T4"]["score"]),
    ("T5", "M5.2 · RPM (lấy giá trị giữa)", f"${vn(_rpm_mid)}",
     "khoảng $3–5", AX["T5"]["score"]),
    ("T6", "rủi ro phát hiện được",
     f'trùng tiêu đề {vn(round(_g("risk","cross_title_pct") or 0, 1))}%',
     "≥5% → −2", f"−{vn(abs(t6_pen))}"),
]
deriv_rows = "\n".join(
    f'<tr{" class=hi" if ax else ""}><td class="c"><b>{ax}</b></td><td>{lab}</td>'
    f'<td class="n">{val}</td><td>{rule}</td>'
    f'<td class="c"><b>{vn(sc) if isinstance(sc, (int, float)) else sc}</b></td></tr>'
    for ax, lab, val, rule, sc in DERIV)

# Dựng sẵn ngoài f-string — nhúng HTML nhiều dấu {} vào f-string rất dễ hỏng ngầm.
T3_BOX = (f'''<div class="box">
<span class="l">Ghi chú về T3 trong ví dụ này</span>
<p>T3 = <b>{vn(AX["T3"]["score"])}</b> chứ không phải 4,4 vì <b>M3.3 không đo được</b>
với một snapshot &mdash; trọng số đã chia lại cho M3.1 và M3.2 thay vì gán điểm mặc định.
Có snapshot thứ hai thì con số này được tính lại đầy đủ.</p>
</div>''' if M33_FIXED else "")

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
/* ── NGUYÊN TẮC CĂN LỀ (nhất quán toàn báo cáo) ────────────────────
   .n   PHẢI so sánh được theo cột → căn PHẢI + chữ số đều bề ngang
        (điểm đóng góp, %, tiền, view…)
   .c   nhãn/mã ngắn không so sánh số học → căn GIỮA
        (mức điểm 0–5, độ tin cậy Cao/Vừa/Thấp)
   mặc định: chữ → căn TRÁI
   Sai lầm cũ: gán .n cho cả nhãn, làm "5 | M2.1 ≥ 2,0" thành cột số
   dính sát cột chữ, mắt phải nhảy qua lại. */
td.n {{ text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap; }}
td.c, th.c {{ text-align:center;white-space:nowrap; }}
tr.hi {{ background:#F4E6E2; }}
.ok {{ color:#2F6B4F;font-weight:bold; }} .no {{ color:#9B2C2C;font-weight:bold; }}
.dn {{ color:#9B2C2C; }} .ac {{ color:#8C3A2B; }}
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
code {{ background:#F2EEE8;padding:.5pt 3pt;font-size:8.5pt; }}
.formula {{ background:#F7F4F0;border:.6pt solid #E2DAD1;padding:7pt 10pt;
 font-size:8.5pt;margin:7pt 0;line-height:1.7; }}
.flow {{ background:#F7F4F0;border:.6pt solid #E2DAD1;padding:9pt 11pt;
 font-size:8.5pt;margin:9pt 0;line-height:1.8;text-align:center; }}
.pb {{ page-break-before:always; }}
ul {{ margin:6pt 0;padding-left:15pt; }} li {{ margin:3pt 0; }}
.f {{ font-size:7.5pt;color:#7A6F68;margin:-2pt 0 10pt; }}
</style></head><body>

<h1>Khung chấm điểm ngách</h1>
<p class="sub">Rubric v{SC.get('rubric_version','1.0')} &mdash; bảng tiêu chí có ngưỡng cố định,
để hai người chấm cùng dữ liệu ra cùng một điểm</p>
<div class="meta">
Tài liệu KHUNG CHUNG &nbsp;•&nbsp; áp dụng cho mọi ngách
&nbsp;•&nbsp; Nguồn: <code>framework/00_system/03_SCORING_RUBRIC.md</code>
&nbsp;•&nbsp; Ví dụ minh họa: ngách <b>{SC.get('niche','—')}</b> (chấm {SC.get('scored_at','—')})
</div>

<div class="box ok">
<span class="l">Đọc nhanh trong 30 giây</span>
<p><b>Việc của rubric:</b> biến dữ liệu YouTube thô thành <b>một con số 0&ndash;20</b>
để trả lời <i>&ldquo;ngách này có đáng làm không?&rdquo;</i> &mdash; theo cách mà
<b>ai chấm cũng ra kết quả giống nhau</b>.</p>
<p><b>Cách làm:</b> chấm 6 khía cạnh (quy mô · động lượng · cửa gia nhập · phù hợp AI ·
kiếm tiền · rủi ro), mỗi khía cạnh có <b>ngưỡng viết sẵn từ trước</b>, rồi cộng theo
trọng số.</p>
<p><b>Điều quan trọng nhất:</b> ngưỡng viết <b>trước khi nhìn dữ liệu</b>. Nhìn số rồi
mới đặt ngưỡng là tự chứng minh điều mình muốn tin.</p>
<p style="margin-top:6pt"><b>Muốn kiểm chứng?</b> Mục 4 có bảng
<i>&ldquo;từ số thô đến điểm&rdquo;</i> &mdash; bạn tự chấm lại được và phải ra
đúng <b>{TOTAL}/20</b>.</p>
</div>

<h2>1. Rubric là gì</h2>

<p><b>Rubric = bảng tiêu chí chấm điểm có ngưỡng cố định.</b> Giống barem chấm thi:
không phải &ldquo;bài này hay thì cho 8 điểm&rdquo;, mà là <i>&ldquo;đúng ý A được 2 điểm,
đúng ý B được 3 điểm&rdquo;</i>. Ai chấm cũng ra cùng kết quả.</p>

<p>Nó trả lời đúng một câu hỏi:
<b>Ngách YouTube này đáng đầu tư đến mức nào, trên thang 0&ndash;20?</b></p>

<div class="box crit">
<span class="l">Vì sao cần rubric &mdash; ví dụ CÓ THẬT từ bảng chấm tay</span>
<table style="margin:4pt 0">
<thead><tr><th>Dòng nhạc</th><th class="n">Top 20% kênh chiếm</th>
<th class="c">Điểm được chấm</th></tr></thead>
<tbody>
<tr><td>Reggaeton</td><td class="n">57,6%</td><td class="c"><b>5</b></td></tr>
<tr><td>R&amp;B</td><td class="n">60,4%</td><td class="c"><b>4</b></td></tr>
<tr><td>Soul Funk</td><td class="n">60,7%</td><td class="c"><b>3</b></td></tr>
<tr><td>Christian Blues</td><td class="n">61,8%</td><td class="c"><b>2</b></td></tr>
</tbody></table>
<p>Bốn con số gần như bằng nhau (57&ndash;62%) nhưng nhận <b>bốn mức điểm khác nhau</b>
&mdash; chênh tới 3 điểm. Đây không phải lỗi người chấm; đây là điều <b>tất yếu</b>
khi không có ngưỡng viết sẵn.</p>
<p>Với rubric, cả bốn rơi vào khoảng <code>55&ndash;62% &rarr; 4 điểm</code> nên
<b>cùng được 4 điểm</b>.</p>
</div>

<h3>Ba thành phần</h3>
<div class="formula">
<b>1. TRỤC</b> &mdash; chấm những khía cạnh nào? &nbsp;(6 trục: T1…T6)<br>
<b>2. NGƯỠNG</b> &mdash; số bao nhiêu thì được mấy điểm? &nbsp;(bảng tra cứu cố định)<br>
<b>3. TRỌNG SỐ</b> &mdash; trục nào quan trọng hơn? &nbsp;(%, cộng lại = 100%)
</div>

<h3>Kiến trúc 4 tầng</h3>
<div class="flow">
<b>TẦNG 1 · FACT</b> &nbsp;&rarr;&nbsp; <b>TẦNG 2 · METRIC</b> &nbsp;&rarr;&nbsp;
<b>TẦNG 3 · SCORE</b> &nbsp;&rarr;&nbsp; <b>TẦNG 4 · INSIGHT</b><br>
<span style="font-size:7.5pt;color:#7A6F68">
số liệu thô &nbsp;·&nbsp; chỉ số có công thức &nbsp;·&nbsp; điểm 0–5 theo ngưỡng &nbsp;·&nbsp; diễn giải</span>
</div>
<p class="f"><b>Quy tắc bất di bất dịch:</b> tầng 4 KHÔNG được sửa tầng 3.
Thấy điểm sai &rarr; sửa <b>ngưỡng</b> ở tầng 3 rồi chạy lại toàn bộ ngách.</p>

<h2 class="pb">2. Sáu trục chấm điểm</h2>

<table>
<thead><tr><th>Trục</th><th>Trọng số</th><th>Đo cái gì</th></tr></thead>
<tbody>
<tr><td><b>T1</b> · Quy mô thị trường</td><td class="n">20%</td>
 <td>Ngách đủ lớn để nuôi kênh không</td></tr>
<tr class="hi"><td><b>T2</b> · Động lượng tăng trưởng</td><td class="n">25%</td>
 <td>Đang lên hay đang xuống</td></tr>
<tr class="hi"><td><b>T3</b> · Cửa gia nhập</td><td class="n">25%</td>
 <td>Người mới còn cửa không</td></tr>
<tr><td><b>T4</b> · Phù hợp sản xuất AI</td><td class="n">15%</td>
 <td>Mô hình AI-first làm được không</td></tr>
<tr><td><b>T5</b> · Giá trị kiếm tiền</td><td class="n">10%</td>
 <td>1 triệu view ra bao nhiêu tiền</td></tr>
<tr><td><b>T6</b> · Rủi ro</td><td class="n">trừ điểm</td>
 <td>Policy, bão hòa, phụ thuộc</td></tr>
</tbody></table>

<div class="box">
<span class="l">Vì sao T2 và T3 nặng nhất</span>
<p><b>T2 (25%):</b> động lượng dự báo tương lai tốt hơn quy mô hiện tại. Christian Blues
chứng minh điều đó &mdash; quy mô chỉ trung bình nhưng tăng từ 3tr lên 10tr view/tháng.</p>
<p><b>T3 (25%):</b> ngách lớn mà bị khóa thì vô dụng với người mới.
Christian/Gospel gốc có top20% = 81,98% &mdash; gần như không còn cửa.</p>
</div>

<h2>3. Công thức &amp; ngưỡng từng trục</h2>

<h3>T1 · Quy mô thị trường (20%)</h3>
<div class="formula">
<code>M1.1</code> = tổng views/tháng của ngách<br>
<code>M1.2</code> = số kênh hoạt động (≥1 video/90 ngày)<br>
<code>M1.3</code> = <b>median</b> view/video &nbsp;&larr; median, KHÔNG dùng mean (đuôi dài)
</div>
<table>
<thead><tr><th class="c">Điểm</th><th>5</th><th>4</th><th>3</th><th>2</th><th>1</th><th>0</th></tr></thead>
<tbody><tr><td><b>Views/tháng</b></td><td>≥50tr</td><td>20–50tr</td><td>8–20tr</td>
<td>3–8tr</td><td>1–3tr</td><td>&lt;1tr</td></tr></tbody></table>
<p class="f">Ngưỡng theo bậc ~2,5× thay vì tuyến tính &mdash; vì view phân bố log-normal.</p>

<h3>T2 · Động lượng tăng trưởng (25%)</h3>
<div class="formula">
<code>M2.1</code> = view 3 tháng gần / 3 tháng trước đó<br>
<code>M2.2</code> = video mới 3 tháng gần / 3 tháng trước<br>
<code>M2.4</code> = M2.1 / M2.2 &nbsp;&larr; <b>chỉ số quan trọng nhất</b>
</div>
<p><b>Đọc M2.4:</b> <code>&gt;1,2</code> cầu tăng nhanh hơn cung = cơ hội &nbsp;·&nbsp;
<code>≈1,0</code> cân bằng &nbsp;·&nbsp; <code>&lt;0,8</code> đang bão hòa, view/video sẽ giảm.</p>
<table>
<thead><tr><th class="c">Điểm</th><th>5</th><th>4</th><th>3</th><th>2</th><th>1</th><th>0</th></tr></thead>
<tbody>
<tr><td><b>M2.1</b> (tăng trưởng view)</td><td>≥2,0</td><td>≥1,5</td><td>≥1,2</td>
<td>≥0,9</td><td>≥0,7</td><td>&lt;0,7</td></tr>
<tr><td><b>M2.4</b> (cầu/cung) &mdash; <i>kèm theo</i></td><td>≥1,2</td><td>≥1,0</td>
<td colspan="4" style="color:#7A6F68">không xét</td></tr>
<tr><td>Diễn giải</td><td colspan="2" style="color:#2F6B4F">đang lên</td>
<td>tăng nhẹ</td><td>đi ngang</td><td>giảm nhẹ</td>
<td style="color:#9B2C2C">sụp</td></tr>
</tbody></table>

<h3 class="pb">T3 · Cửa gia nhập (25%)</h3>
<div class="formula">
<code>M3.1</code> = Gini của phân bố view theo kênh &nbsp;(0 = đều, 1 = độc quyền)<br>
<code>M3.2</code> = % kênh &lt;12 tháng đạt ≥100k view/tháng<br>
<code>M3.3</code> = số tháng trung vị để kênh mới đạt 100k view tích lũy<br>
<b>T3 = 0,3×score(M3.1) + 0,5×score(M3.2) + 0,2×score(M3.3)</b>
</div>
<table>
<thead><tr><th class="c">Điểm</th><th>5</th><th>4</th><th>3</th><th>2</th><th>1</th><th>0</th></tr></thead>
<tbody>
<tr><td><b>M3.2</b> · người mới thành công <i>(trọng số 0,5)</i></td>
<td>≥40%</td><td>25–40%</td><td>15–25%</td><td>8–15%</td><td>3–8%</td><td>&lt;3%</td></tr>
<tr><td><b>M3.1</b> · Gini <i>(0,3)</i> &mdash; thấp là mở</td>
<td>≤0,45</td><td>0,45–<br>0,55</td><td>0,55–<br>0,65</td><td>0,65–<br>0,75</td>
<td>0,75–<br>0,85</td><td>&gt;0,85</td></tr>
</tbody></table>
<p class="f"><b>M3.2 có trọng số cao nhất (0,5)</b> vì đây là bằng chứng trực tiếp:
người mới có thắng được không. Gini chỉ gián tiếp.</p>

<div class="box crit">
<span class="l">⚠ Khi một metric KHÔNG ĐO ĐƯỢC thì chia lại trọng số, đừng gán mặc định</span>
<p><code>M3.3</code> cần <b>≥2 lần chụp dữ liệu</b> mới tính được. Với một snapshot,
mọi chỉ số dạng &ldquo;cumsum đến khi đạt X&rdquo; đều vô nghĩa &mdash; vì
<code>view_count</code> là view <i>tích lũy đến ngày crawl</i>, không phải view lúc đăng.</p>
<p><b>Lỗi đã mắc:</b> M3.3 ghi rõ <i>&ldquo;KHÔNG ĐO ĐƯỢC&rdquo;</i> nhưng công thức vẫn
hardcode <code>0.2×5</code> &mdash; tức <b>chấm 5/5 điểm tối đa cho thứ không đo được</b>.
Nó đẩy T3 từ 4,0 lên 4,4 và tổng từ 12,05 lên 12,20.</p>
<p><b>Cách đúng:</b> bỏ thành phần thiếu và <b>chia lại trọng số cho phần đo được</b>:
<code>T3 = (0,3×M3.1 + 0,5×M3.2) / 0,8</code>.</p>
</div>

<h3>T4 · Phù hợp sản xuất AI (15%)</h3>
<div class="formula">
<code>M4.1</code> = % kênh top 20 là AI-first &nbsp;·&nbsp;
<code>M4.2</code> = mức khán giả chấp nhận AI theo genre<br>
<code>M4.3</code> = độ phức tạp sản xuất &nbsp;·&nbsp;
<code>M4.4</code> = % video dạng long-mix/lyric (dễ nhân bản)
</div>
<table>
<thead><tr><th class="c">Điểm</th><th>5</th><th>4</th><th>3</th><th>2</th><th>1</th><th>0</th></tr></thead>
<tbody><tr><td><b>Điều kiện</b></td>
<td>M4.1≥60%<br>&amp; M4.2 Cao</td><td>M4.1≥40%<br>&amp; M4.2 ≥Khá</td>
<td>M4.1≥25%</td><td>M4.1≥10%</td><td>M4.1≥3%</td><td>nghệ sĩ thật<br>thống trị</td></tr>
</tbody></table>
<p class="f"><b>M4.1 là bằng chứng thực nghiệm</b> &mdash; thay cho việc đoán
&ldquo;AI làm được không&rdquo;. Nếu 60% kênh top đã là AI-first và đang thắng
thì chứng minh xong.</p>

<h3>T5 · Giá trị kiếm tiền (10%)</h3>
<table>
<thead><tr><th class="c">Điểm</th><th>5</th><th>4</th><th>3</th><th>2</th><th>1</th><th>0</th></tr></thead>
<tbody><tr><td><b>RPM ước tính</b></td><td>≥$8</td><td>$5–8</td><td>$3–5</td>
<td>$1,5–3</td><td>$0,7–1,5</td><td>&lt;$0,7</td></tr></tbody></table>
<p class="f">RPM phụ thuộc mạnh vào geo + độ tuổi khán giả + chủ đề.
Luôn verify ở STEP_07, không đoán.</p>
<div class="box">
<span class="l">RPM ghi dạng khoảng &mdash; chấm theo giá trị GIỮA</span>
<p>Vì RPM không đo trực tiếp được, <code>M5.2</code> lưu <code>[thấp, giữa, cao]</code>
và bộ chấm lấy <b>phần tử giữa</b> &mdash; thận trọng, không lấy cận trên.</p>
<p>Ví dụ ngách này: <code>[1,5 · 3,0 · 6,0]</code> &rarr; chấm theo <b>$3,0</b>
&rarr; rơi đúng ranh giới khoảng $3&ndash;5 &rarr; <b>3 điểm</b>.
Lấy cận trên 6,0 sẽ thành 4 điểm &mdash; nên quy ước phải <b>cố định</b>,
không chọn tùy lúc.</p>
</div>

<h3 style="page-break-before:avoid">T6 · Rủi ro (trừ tối đa 5 điểm)</h3>
<table>
<thead><tr><th>Rủi ro</th><th class="c">Trừ</th><th>Metric</th>
<th>Ngưỡng kích hoạt</th></tr></thead>
<tbody>
<tr><td>Reused content / AI bị soi</td><td class="c dn"><b>−2</b></td>
 <td><code>risk.cross_title_pct</code></td><td><b>≥5%</b> video trùng tiêu đề</td></tr>
<tr><td>Bản quyền (cover thánh ca)</td><td class="c dn"><b>−1</b></td>
 <td><code>risk.copyright_flag</code></td><td>cờ bật</td></tr>
<tr><td>Phụ thuộc 1 kênh dẫn đầu</td><td class="c dn"><b>−1</b></td>
 <td><code>entry.top1_share</code></td><td><b>&gt;40%</b> view thuộc 1 kênh</td></tr>
<tr><td>Cung tăng vượt cầu</td><td class="c dn"><b>−1</b></td>
 <td><code>momentum.M2.4</code></td><td><b>&lt;0,8</b></td></tr>
</tbody></table>
<p class="f">Điểm trừ <b>cộng dồn</b>, chặn ở tối đa −5.</p>

<h2>4. Tổng điểm &amp; diễn giải</h2>

<div class="formula" style="text-align:center;font-size:9.5pt">
<b>SCORE = (T1×20% + T2×25% + T3×25% + T4×15% + T5×10%) × 4 − T6</b>
</div>
<p class="f">Nhân 4 để đưa thang 0&ndash;5 về thang 0&ndash;20.
T6 là điểm <b>trừ</b>, không phải điểm cộng.</p>

<table>
<thead><tr><th class="c">Điểm</th><th>Kết luận</th></tr></thead>
<tbody>
<tr><td class="c"><b>16–20</b></td><td><b class="ok">Ưu tiên cao</b> &mdash; vào ngay</td></tr>
<tr><td class="c"><b>13–15,9</b></td><td><b>Tiềm năng</b> &mdash; vào có điều kiện, cần khác biệt hóa</td></tr>
<tr><td class="c"><b>10–12,9</b></td><td><b class="ac">Theo dõi</b> &mdash; chưa vào, quan sát thêm</td></tr>
<tr><td class="c"><b>&lt;10</b></td><td><b class="no">Bỏ qua</b></td></tr>
</tbody></table>

<h3>Ví dụ chấm thật &mdash; ngách {SC.get('niche','—')}</h3>
<table>
<thead><tr><th>Trục</th><th class="c">Điểm<br>(0–5)</th><th class="n">Trọng số</th>
<th class="n">Đóng góp</th><th class="c">Tin cậy</th></tr></thead>
<tbody>{score_rows}</tbody></table>

<div class="kpi">
<div><div class="k">Tổng điểm</div><div class="v ac">{TOTAL}</div>
 <div class="c">trên thang 0–20</div></div>
<div><div class="k">Xếp loại</div><div class="v" style="font-size:12pt">{VERDICT}</div>
 <div class="c">theo bảng diễn giải</div></div>
<div><div class="k">Phiên bản rubric</div><div class="v" style="font-size:12pt">v{SC.get('rubric_version','1.0')}</div>
 <div class="c">chấm {SC.get('scored_at','—')}</div></div>
</div>

{T3_BOX}

<h3>Từ số thô đến điểm &mdash; xem toàn bộ đường đi</h3>
<p>Bảng dưới là <b>bản ghi thật</b> của lần chấm này, trích từ
<code>_state/metrics.json &rarr; _meta.derivation</code>. Mỗi dòng cho thấy
số đo được, ngưỡng nó chạm, và điểm nhận được &mdash; không có bước nào ẩn.</p>

<table>
<thead><tr><th class="c">Trục</th><th>Metric</th><th class="n">Giá trị đo được</th>
<th>Ngưỡng chạm</th><th class="c">Điểm</th></tr></thead>
<tbody>{deriv_rows}</tbody></table>

<p class="f">Dòng không có tên trục = thành phần phụ của trục ngay phía trên.</p>

<div class="box ok">
<span class="l">Đây là ý nghĩa của &laquo;truy vết được&raquo;</span>
<p>Bạn đọc bảng này rồi <b>tự chấm lại</b> được: mở <code>metrics.json</code>,
đối chiếu giá trị, tra ngưỡng ở mục 3, cộng theo công thức. Ra đúng <b>{TOTAL}</b>.</p>
<p>Nếu không tái tạo được thì rubric đã hỏng &mdash; đó chính là điều bảng chấm tay
cũ không làm được.</p>
</div>

<h2>5. Ba nguyên tắc bất di bất dịch</h2>
<table>
<thead><tr><th>#</th><th>Nguyên tắc</th><th>Vì sao</th></tr></thead>
<tbody>
<tr><td class="c"><b>1</b></td><td><b>Ngưỡng viết TRƯỚC khi nhìn dữ liệu</b></td>
 <td>Nhìn dữ liệu rồi mới đặt ngưỡng = tự chứng minh điều mình muốn tin</td></tr>
<tr><td class="c"><b>2</b></td><td><b>Muốn đổi điểm thì đổi NGƯỠNG, rồi chạy lại TẤT CẢ ngách</b></td>
 <td>Sửa điểm lẻ cho một ngách thì các ngách không còn so sánh được với nhau</td></tr>
<tr><td class="c"><b>3</b></td><td><b>Mọi điểm phải truy vết được</b><br>
 công thức → ngưỡng → bằng chứng → nguồn → độ tin cậy</td>
 <td>Để 6 tháng sau vẫn biết vì sao ra con số đó</td></tr>
</tbody></table>

<h3>Bảng truy vết bắt buộc</h3>
<p>Mỗi lần chấm sinh ra <code>_state/scores.json</code>, mỗi trục ghi đủ:
<code>score</code> · <code>weight</code> · <code>metrics</code> ·
<code>threshold_hit</code> · <code>evidence</code> · <code>confidence</code> ·
<code>source</code>.</p>
<p class="f">Đây là thứ bảng Excel cũ không có &mdash; và là lý do nó không nhất quán được.</p>

<h2>6. Rubric KHÔNG làm được gì</h2>
<div class="box crit">
<span class="l">Nói rõ giới hạn để không kỳ vọng sai</span>
<p><b>Không thay quyết định kinh doanh.</b> Nó cho điểm có căn cứ; người quyết vẫn là bạn.</p>
<p><b>Không chính xác tuyệt đối.</b> T5 dựa trên RPM ước tính &mdash; độ tin cậy Thấp.</p>
<p><b>Không dự đoán tương lai.</b> Nó đo trạng thái hiện tại và xu hướng đã xảy ra.</p>
<p><b>Điểm cao không đảm bảo thành công</b>, điểm thấp không đảm bảo thất bại.
Nó chỉ nói <i>xác suất và mức độ thuận lợi</i>.</p>
</div>

<h3>Hiệu chuẩn &mdash; không backtest thì rubric chỉ là ý kiến có công thức</h3>
<p>Trước khi tin rubric, phải chấm lại các ngách <b>đã biết kết quả</b>. Nếu ngách
&ldquo;rõ ràng tốt&rdquo; được điểm cao và ngách &ldquo;rõ ràng xấu&rdquo; được điểm thấp
thì rubric đúng. Ra kết quả vô lý &rarr; chỉnh ngưỡng, chạy lại <b>tất cả</b> ngách.</p>
<p class="f">Tập backtest hiện có: 24 dòng nhạc trong
<code>niches/_backtest/FMG_phan-tich-dong-nhac.csv</code>.</p>

</body></html>"""

out = N/"99_report/_phu-luc/RUBRIC_Khung-cham-diem.pdf"
out.parent.mkdir(parents=True, exist_ok=True)
out.parent.mkdir(parents=True, exist_ok=True)
HTML(string=DOC).write_pdf(out)
print(f"PDF: {out} ({out.stat().st_size//1024} KB)")
