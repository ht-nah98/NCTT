# M7 · OUTPUT — sinh tài liệu và biểu đồ

> Biến JSON của A5 thành PDF người đọc được. Không có agent ở đây — code thuần.
>
> **Xong khi:** 4 tài liệu dựng ra, render ảnh nhìn không có lỗi bố cục.

---

## 1. VÌ SAO A5 TRẢ JSON CHỨ KHÔNG TRẢ HTML

| Nếu agent trả HTML | Nếu agent trả JSON |
|---|---|
| không validate được | schema kiểm được |
| agent tự do đổi bố cục → mỗi lần khác | bố cục do code quyết, nhất quán |
| lẫn nội dung với trình bày | tách bạch |

```json
{
  "document": "T1.1",
  "blocks": [
    {"type": "heading", "level": 2, "text": "Trạng thái cung"},
    {"type": "paragraph", "text": "Cầu tăng nhanh hơn cung 1,30 lần.",
     "cites": ["F01"], "n": 2338, "source_class": "Y"},
    {"type": "table", "headers": ["Chỉ số", "Giá trị"],
     "rows": [["M2.4", "1,30×"]]},
    {"type": "warning", "text": "Chỉ 1 snapshot — độ tin cậy ở mức vừa"},
    {"type": "chart", "spec": {"kind": "bar", "data_key": "age_dist"}}
  ]
}
```

---

## 2. RENDERER

```python
BLOCK_RENDERERS = {
    "heading":   lambda b: f'<h{b.get("level",2)}>{esc(b["text"])}</h{b.get("level",2)}>',
    "paragraph": render_paragraph,
    "table":     render_table,
    "warning":   lambda b: f'<div class="box gap"><p>{esc(b["text"])}</p></div>',
    "chart":     lambda b: f'<img src="{make_chart(b["spec"])}">',
}

def render_paragraph(b: dict) -> str:
    """Tự động gắn chip mã nguồn và cỡ mẫu — agent không phải nhớ."""
    html = esc(b["text"])
    if b.get("source_class"):
        html += f' <span class="src src-{b["source_class"].lower()}">' \
                f'{b["source_class"]}</span>'
    if b.get("n"):
        cls = ' class="nsmall"' if b["n"] < 30 else ""
        html += f'<span{cls}>n={vn(b["n"])}</span>'
        if b["n"] < 30:
            html += ' <span class="warn">KHÔNG ĐỦ MẪU</span>'
    return f"<p>{html}</p>"
```

> **Chi tiết quan trọng:** chip nguồn và cỡ mẫu do **code gắn**, không phải
> agent viết tay. Agent chỉ khai `source_class` và `n` trong JSON. Như vậy
> không bao giờ quên, và định dạng luôn nhất quán.

---

## 3. BIỂU ĐỒ — SINH TỪ SPEC, KHÔNG PHẢI TỪ MÔ TẢ

Agent **không** vẽ biểu đồ. Nó khai một `spec`, code vẽ.

```python
def make_chart(spec: dict, data: dict) -> str:
    """spec: {"kind": "bar"|"barh"|"line", "data_key": ..., "title": ...}"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 9, "figure.dpi": 150,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.grid": True, "grid.alpha": .25})

    ACC, OK, WARN, MUTE = "#8C2F39", "#2D6A4F", "#9A6700", "#A8A29E"
    d = data[spec["data_key"]]                  # ĐỌC TỪ DỮ LIỆU, không từ agent

    fig, ax = plt.subplots(figsize=spec.get("size", (5.5, 3)))

    if spec["kind"] == "barh":
        # màu MANG NGHĨA: xanh=xác nhận, vàng=yếu, xám=bác bỏ
        colors = [OK if v == "XÁC NHẬN" else WARN if v == "YẾU" else MUTE
                  for v in d["verdicts"]]
        ax.barh(d["labels"], d["values"], color=colors)
    elif spec["kind"] == "bar":
        ax.bar(d["labels"], d["values"], color=ACC)

    # cỡ mẫu LUÔN trong tiêu đề, không giấu ở chú thích
    ax.set_title(f"{spec['title']} (n={vn(d['n'])})", fontweight="bold")

    path = OUT / f"chart_{spec['data_key']}.png"
    plt.tight_layout(); plt.savefig(path, bbox_inches="tight"); plt.close()
    return str(path)
```

### Ba quy tắc biểu đồ

| Quy tắc | Vì sao |
|---|---|
| Màu mang nghĩa, không trang trí | người đọc nhìn màu biết độ tin cậy |
| Cỡ mẫu trong tiêu đề | không giấu n ở chú thích nhỏ |
| Số đọc từ dữ liệu, không từ agent | agent bịa số thì biểu đồ cũng sai |

---

## 4. DỰNG PDF — BA BẪY ĐÃ MẮC

Dùng WeasyPrint (HTML+CSS → PDF).

```python
from weasyprint import HTML
HTML(string=doc_html, base_url=".").write_pdf(out_path)
```

| Bẫy | Triệu chứng | Cách tránh |
|---|---|---|
| **T87** | `display:flex` → **cả khối biến mất**, không báo lỗi | nhiều cột phải dùng `<table>` thật |
| **T88** | `page-break-inside:avoid` trên khối cao → **trang trắng** | chỉ dùng cho khối < 1/3 trang |
| **T89** | `table-layout:fixed` thiếu width → chữ dán nhau | đặt width cho **tất cả** cột, cộng đủ 100% |

> **T87 nguy hiểm nhất:** `extract_text()` vẫn thấy chữ dù khối không hiển thị.
> Chỉ render ra ảnh và **nhìn bằng mắt** mới phát hiện.

```python
def verify_pdf(path: str) -> list[str]:
    """Kiểm cơ học sau khi dựng."""
    import pypdf
    r = pypdf.PdfReader(path)
    errs = []
    for i, page in enumerate(r.pages, 1):
        t = page.extract_text()
        if len(t) < 200 and i > 1:
            errs.append(f"trang {i} gần trống ({len(t)} ký tự) — nghi T88")
        if "�" in t:
            errs.append(f"trang {i} có ô vuông thiếu glyph — sai font")
    return errs
```

```bash
# và luôn nhìn bằng mắt
pdftoppm -png -r 68 bao-cao.pdf /tmp/trang
```

---

## 5. FONT CHO TIẾNG VIỆT

```css
body { font-family: "DejaVu Sans", sans-serif; }
```

DejaVu Sans có đủ dấu tiếng Việt. Font thiếu glyph sẽ in ra ô vuông — và điều
tệ nhất là **PDF vẫn dựng thành công**, chỉ khi nhìn mới thấy.

---

## 6. ĐỊNH DẠNG SỐ KIỂU VIỆT NAM

```python
def vn(x, digits=0) -> str:
    """1234.5 -> '1.234,5' — nghìn dùng chấm, thập phân dùng phẩy."""
    if x is None:
        return "—"
    s = f"{x:,.{digits}f}"
    return s.replace(",", "␟").replace(".", ",").replace("␟", ".")
```

Đây là lỗi hay gặp: agent sinh số kiểu Mỹ (`1,234.5`), người Việt đọc nhầm.
Chuẩn hoá ở tầng render, không bắt agent nhớ.

---

## 7. NGHIỆM THU M7

```
□ 4 tài liệu dựng ra được từ JSON của A5
□ Chip mã nguồn và cỡ mẫu do CODE gắn, không do agent viết
□ Biểu đồ có màu mang nghĩa + cỡ mẫu trong tiêu đề
□ verify_pdf() chạy sau mỗi lần dựng
□ Đã render ra ảnh và NHÌN từng trang
□ Không có ô vuông thiếu glyph
□ Số định dạng kiểu Việt Nam
```
