"""Nền chung cho bốn tài liệu T1.1–T1.4.

VÌ SAO CÓ FILE NÀY: bốn builder T1.x đều cần đúng ba thứ giống nhau —
gắn mã nguồn Y·P·S·V·K·N, gắn cỡ mẫu, và chặn kết luận khi mẫu quá nhỏ.
Viết lại ở bốn chỗ thì bốn chỗ sẽ lệch nhau sau vài vòng sửa.

Xem framework/00_system/10_SOURCE_CLASSES.md và 11_OUTPUT_CONTRACT.md.

CÁCH DÙNG:
    from _t1_common import S, n_of, page_css, doc, section
    S.Y("Cầu tăng 1,62× trong khi cung tăng 1,24×", n=2338)
"""
import json
import pathlib
import datetime

# ── sáu nhóm nguồn ──────────────────────────────────────────────────────────
SOURCE_CLASSES = {
    "Y": ("YouTube", "Cung đã tồn tại và đang thắng"),
    "P": ("Nền tảng khác", "Cung thay thế — cầu được phục vụ ở nơi khác"),
    "S": ("Tín hiệu tìm kiếm", "Cầu hiển thị qua hành vi, độc lập với ai phục vụ"),
    "V": ("Tiếng nói người dùng", "Cầu phát ngôn, ngôn ngữ thật, cấm kỵ"),
    "K": ("Khoa học & báo cáo ngành", "Cơ chế công năng, ràng buộc sinh lý"),
    "N": ("Nội bộ HG Media / FMG", "RPM thật, Analytics kênh nhà"),
}

# Nhóm nguồn đã thực sự có dữ liệu tính đến hôm nay. Mọi nhóm ngoài danh sách
# này khi được dùng sẽ tự động mang cảnh báo — làm lỗ hổng hữu hình (quy tắc N6).
AVAILABLE = {"Y"}

MIN_N = 30   # dưới ngưỡng này => KHÔNG ĐỦ MẪU (quy tắc O3)


class _Src:
    """Gắn mã nguồn vào một phát biểu.

    Trả về HTML đã kèm chip mã nguồn, cỡ mẫu, và cảnh báo nếu cần.
    Dùng S.Y(...), S.K(...), S.none(...) thay vì tự nối chuỗi.
    """

    def _tag(self, code, text, n=None, note=None, weak=False):
        chip = f'<span class="src src-{code.lower()}">{code}</span>'
        out = f'{text} {chip}'
        if n is not None:
            flag = ' class="nsmall"' if n < MIN_N else ""
            out += f'<span{flag}>n={n:,}</span>'.replace(",", ".")
            if n < MIN_N:
                out += ' <span class="warn">KHÔNG ĐỦ MẪU</span>'
        if note:
            out += f' <span class="note">{note}</span>'
        if weak or (code not in AVAILABLE and code != "—"):
            out += ' <span class="warn">⚠ suy gián tiếp</span>'
        return out

    def Y(self, text, n=None, note=None, weak=False):
        return self._tag("Y", text, n, note, weak)

    def K(self, text, n=None, note=None):
        return self._tag("K", text, n, note)

    def S(self, text, n=None, note=None):
        return self._tag("S", text, n, note)

    def V(self, text, n=None, note=None):
        return self._tag("V", text, n, note)

    def P(self, text, n=None, note=None):
        return self._tag("P", text, n, note)

    def N(self, text, n=None, note=None):
        return self._tag("N", text, n, note)

    def none(self, what):
        """Mục chưa có nguồn — hiện rõ thay vì bỏ trống (quy tắc N6)."""
        return (f'<span class="missing">[—] chưa có nguồn</span> '
                f'<span class="note">{what}</span>')


S = _Src()


def source_of(metrics, key, default="Y"):
    """Đọc mã nguồn của một chỉ số từ `_meta` trong metrics.json.

    Trả về mã đã khai ở tầng dữ liệu (do collect_metrics.py gắn), thay vì để
    builder tự đoán. Nhờ vậy khi thêm nguồn S/V/P, chỉ cần sửa
    SOURCE_CLASS_BY_GROUP ở collect_metrics — mọi báo cáo tự đổi theo.
    """
    entry = (metrics.get("_meta") or {}).get(key)
    if isinstance(entry, dict) and entry.get("source_class"):
        return entry["source_class"]
    return default


def cite(metrics, key, text, n=None, note=None):
    """Gắn phát biểu với mã nguồn ĐỌC TỪ dữ liệu, không gõ tay.

        cite(M, "M2_4_demand_supply_gap", "Cầu vượt cung 1,30×")
    """
    code = source_of(metrics, key)
    primary = code.split("+")[0]
    out = getattr(S, primary, S.Y)(text, n=n, note=note)
    if "+" in code:                       # ví dụ "Y+K" -> hiện thêm chip K
        for extra in code.split("+")[1:]:
            out += f'<span class="src src-{extra.lower()}">{extra}</span>'
    return out


def n_of(value, total=None):
    """Định dạng cỡ mẫu kiểu Việt Nam: 6.413 thay vì 6,413."""
    s = f"{int(value):,}".replace(",", ".")
    if total:
        s += f"/{int(total):,}".replace(",", ".")
    return s


def vn(x, digits=1):
    """Số thập phân kiểu Việt Nam: 1,62 thay vì 1.62."""
    if x is None:
        return "—"
    return f"{x:,.{digits}f}".replace(",", "␟").replace(".", ",").replace("␟", ".")


def load(path, default=None):
    """Đọc JSON, trả default nếu thiếu — ngách mới chưa chạy hết các bước."""
    p = pathlib.Path(path)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return default


def today():
    return datetime.date.today().strftime("%d/%m/%Y")


# ── khung trang in dùng chung ───────────────────────────────────────────────
# Một bảng màu, một cỡ chữ, một kiểu bảng cho cả bốn tài liệu. Trước đây mỗi
# builder tự khai CSS riêng -> 22 file, mỗi file một tông màu hơi khác.
PAGE_CSS = """
@page {{ size:A4; margin:18mm 16mm 20mm;
  @bottom-left {{ content:"{doc_code} · {niche}"; font-family:"DejaVu Sans";
    font-size:7pt; color:#9A8E85; }}
  @bottom-right {{ content counter(page) " / " counter(pages);
    font-family:"DejaVu Sans"; font-size:7.5pt; color:#9A8E85; }} }}
@page :first {{ @bottom-left {{ content:""; }} @bottom-right {{ content:""; }} }}

body {{ font-family:"DejaVu Sans",sans-serif; font-size:9.5pt;
  line-height:1.55; color:#1C1917; }}
h1 {{ font-size:25pt; line-height:1.12; margin:0 0 8pt; letter-spacing:-.5pt; }}
h2 {{ font-size:11pt; margin:20pt 0 9pt; padding-bottom:4pt; color:#8C2F39;
  border-bottom:1.5pt solid #1C1917; page-break-after:avoid;
  text-transform:uppercase; letter-spacing:.6pt; }}
h3 {{ font-size:10.5pt; margin:13pt 0 5pt; page-break-after:avoid; }}
p {{ margin:6pt 0; }}
ul {{ margin:6pt 0; padding-left:14pt; }}
li {{ margin:3pt 0; }}
i {{ font-style:italic; }}

.cover {{ padding-top:58mm; page-break-after:always; }}
.eyebrow {{ font-size:8pt; letter-spacing:1.4pt; text-transform:uppercase;
  color:#78716C; margin-bottom:12pt; }}
.stand {{ font-size:11.5pt; color:#57534E; line-height:1.5; margin:10pt 0 0;
  max-width:118mm; font-style:italic; }}
.rule {{ border:0; border-top:1.5pt solid #1C1917; margin:16pt 0; width:70mm; }}
.covmeta {{ font-size:8.5pt; color:#78716C; line-height:1.8; }}
.covmeta b {{ color:#1C1917; }}

/* chip mã nguồn — nhìn là biết phát biểu dựa trên loại nguồn nào */
.src {{ display:inline-block; font-size:6.5pt; font-weight:bold; color:#fff;
  background:#78716C; border-radius:2pt; padding:.5pt 3.5pt; margin:0 3pt;
  vertical-align:.8pt; }}
.src-y {{ background:#8C2F39; }}
.src-k {{ background:#2D6A4F; }}
.src-s {{ background:#1D5B79; }}
.src-v {{ background:#7A4E8C; }}
.src-p {{ background:#9A6700; }}
.src-n {{ background:#44403C; }}
.note {{ color:#78716C; font-size:8pt; }}
.nsmall {{ color:#9A6700; font-weight:bold; }}
.warn {{ color:#9A6700; font-weight:bold; font-size:8pt; }}
.missing {{ color:#A8A29E; font-style:italic; }}

table {{ border-collapse:collapse; width:100%; font-size:8.5pt; margin:8pt 0; }}
table tr {{ page-break-inside:avoid; }}
th {{ background:#F5F2ED; text-align:left; padding:5pt 7pt; font-size:7.5pt;
  text-transform:uppercase; letter-spacing:.4pt; color:#57534E;
  border-bottom:1pt solid #D6CEC4; }}
td {{ padding:5pt 7pt; border-bottom:.6pt solid #EDE7E0; vertical-align:top; }}
td.n {{ text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }}
td.w {{ font-weight:bold; }}
.ok {{ color:#2D6A4F; font-weight:bold; }}
.no {{ color:#78716C; font-weight:bold; }}
.wa {{ color:#9A6700; font-weight:bold; }}

.box {{ border-left:2.5pt solid #8C2F39; background:#FAF6F5; padding:8pt 11pt;
  margin:10pt 0; page-break-inside:avoid; }}
.box.plain {{ border-left-color:#A8A29E; background:#F7F5F2; }}
.box.gap {{ border-left-color:#9A6700; background:#FAF6EC; }}
.box h4 {{ font-size:9.5pt; margin:0 0 4pt; }}
.box p {{ margin:4pt 0 0; }}
.small {{ font-size:8pt; color:#78716C; }}

.foot {{ margin-top:16pt; padding-top:8pt; border-top:1.5pt solid #1C1917;
  font-size:7.5pt; color:#78716C; line-height:1.65; }}
.foot code {{ font-family:"DejaVu Sans Mono",monospace; font-size:7pt; color:#44403C; }}
"""


def doc(doc_code, niche, title, standfirst, meta_rows, body, foot):
    """Dựng một tài liệu T1.x hoàn chỉnh."""
    css = PAGE_CSS.format(doc_code=doc_code, niche=niche)
    meta = "<br>".join(f"<b>{k}</b> &nbsp; {v}" for k, v in meta_rows)
    return f"""<!doctype html><html><head><meta charset="utf-8">
<style>{css}</style></head><body>
<div class="cover">
  <div class="eyebrow">{doc_code} · {niche}</div>
  <h1>{title}</h1>
  <p class="stand">{standfirst}</p>
  <hr class="rule">
  <div class="covmeta">{meta}</div>
</div>
{body}
<div class="foot">{foot}</div>
</body></html>"""


def source_legend():
    """Bảng chú giải mã nguồn — in ở cuối mỗi tài liệu."""
    rows = "".join(
        f'<tr><td class="w"><span class="src src-{c.lower()}">{c}</span></td>'
        f'<td>{name}</td><td>{what}</td>'
        f'<td class="{"ok" if c in AVAILABLE else "no"}">'
        f'{"đã có" if c in AVAILABLE else "chưa có"}</td></tr>'
        for c, (name, what) in SOURCE_CLASSES.items())
    return f"""<h2>Chú giải mã nguồn</h2>
<p class="small">Mọi phát biểu trong tài liệu này mang một mã nguồn.
Xem <code>framework/00_system/10_SOURCE_CLASSES.md</code>.</p>
<table><thead><tr><th>Mã</th><th>Nhóm nguồn</th><th>Quan sát được cái gì</th>
<th>Trạng thái</th></tr></thead><tbody>{rows}</tbody></table>
<div class="box gap"><h4>Giới hạn phải đọc kèm</h4>
<p>Hệ thống hiện chỉ có nguồn <b>Y</b>. YouTube trả lời <b>đầy đủ</b> câu hỏi
“cái gì đang tồn tại, ai đang thắng”, nhưng <b>rất kém</b> ở câu “cầu nào chưa
được đáp ứng” và <b>gần như mù</b> ở câu “cầu dịch chuyển về đâu trong 6–12
tháng”. Mọi phát biểu về khoảng trống và xu hướng trong tài liệu này đều mang
cảnh báo <i>suy gián tiếp</i>.</p></div>"""
