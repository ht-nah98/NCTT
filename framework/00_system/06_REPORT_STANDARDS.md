# CHUẨN TRÌNH BÀY BÁO CÁO

> Vì sao có file này: báo cáo dựng bởi 12 script khác nhau, mỗi script tự quyết định
> cách căn lề và dựng bảng → **lúc trái lúc phải, người đọc mất mạch** (bài học T33).
> File này là nguồn duy nhất cho quy ước trình bày.

---

## 1. NGUYÊN TẮC CĂN LỀ

Chỉ có **ba** trường hợp. Không có trường hợp thứ tư.

| Loại nội dung | Căn | Class | Ví dụ |
|---|---|---|---|
| **Số so sánh được theo cột** | PHẢI | `.n` | `12,05` · `61,8%` · `$3` · `1.687 view` |
| **Nhãn / mã ngắn** | GIỮA | `.c` | mức điểm `5` · `Cao/Vừa/Thấp` · `−2` · `16–20` |
| **Chữ** | TRÁI | *(mặc định)* | tên trục, mô tả, kết luận |

### Phép thử một câu

> **Người đọc có cần so sánh con số này với con số ngay trên/dưới nó không?**
>
> Có → `.n` (căn phải, `tabular-nums` để chữ số thẳng cột).
> Không → nó là nhãn → `.c`.

**Lỗi hay mắc:** mức điểm `0–5` trông như số nên bị gán `.n`. Nhưng không ai cộng
hay so sánh `5` với `4` — nó là **nhãn của một bậc**. Gán `.n` làm nó dính sát cột chữ
bên phải, mắt phải nhảy qua lại từng dòng.

```css
td.n      { text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
td.c, th.c{ text-align:center; white-space:nowrap; }
/* mặc định: căn trái */
```

> **Tiêu đề cột phải căn cùng chiều với dữ liệu bên dưới.** Cột `.n` thì `<th class="n">`.

---

## 2. BẢNG NGƯỠNG — ĐỂ ĐIỂM LÀM CỘT

Ngưỡng chấm điểm luôn có 6 bậc (5→0). **Đừng cho mỗi bậc một dòng.**

❌ **Dọc** — 6 dòng, không so sánh được các bậc với nhau:

| Điểm | Điều kiện |
|---|---|
| 5 | M2.1 ≥ 2,0 và M2.4 ≥ 1,2 |
| 4 | M2.1 ≥ 1,5 và M2.4 ≥ 1,0 |
| … | … |

✅ **Ngang** — 3 dòng, ngưỡng thẳng hàng dưới từng bậc:

| Điểm | 5 | 4 | 3 | 2 | 1 | 0 |
|---|---|---|---|---|---|---|
| **M2.1** (tăng trưởng view) | ≥2,0 | ≥1,5 | ≥1,2 | ≥0,9 | ≥0,7 | <0,7 |
| **M2.4** (cầu/cung) | ≥1,2 | ≥1,0 | *không xét* | | | |
| Diễn giải | đang lên | | tăng nhẹ | đi ngang | giảm nhẹ | sụp |

**Quy tắc:** trục nào cần **so sánh** thì trục đó nằm **ngang**.

Dạng ngang còn cho thêm hàng *"diễn giải"* — thứ không nhét được vào dạng dọc.

---

## 3. SỐ KIỂU VIỆT NAM

| Thứ | Quy ước | Ví dụ |
|---|---|---|
| Thập phân | dấu **phẩy** | `12,05` không phải `12.05` |
| Hàng nghìn | dấu **chấm** | `6.413` |
| Phần trăm | 1–2 chữ số thập phân | `13,5%` · `1,73%` |
| Điểm số | **in đủ chữ số**, đừng làm tròn | `12,05` không phải `12,1` (T28) |

```python
def vn(x, nd=None):
    s = f"{x:.{nd}f}" if nd is not None else f"{x:g}"
    return s.replace(".", ",")
```

---

## 4. MÀU CÓ NGHĨA, KHÔNG TRANG TRÍ

| Màu | Class | Dùng khi |
|---|---|---|
| Xanh lá | `.ok` | kết quả tốt, đã xác nhận |
| Đỏ | `.no` `.dn` | cảnh báo, điểm trừ, kết quả xấu |
| Nâu đỏ | `.ac` | nhấn mạnh trung tính |
| Xám | *(inline)* | thông tin phụ, nguồn truy vết |

Hộp: `.box` (thường) · `.box.crit` (cảnh báo) · `.box.ok` (tin tốt).

**Đừng dùng màu chỉ cho đẹp** — mỗi màu phải mang một tầng thông tin.

---

## 5. BẰNG CHỨNG PHẢI TRUY VẾT ĐƯỢC

Mọi con số trong báo cáo phải trả lời được *"lấy ở đâu ra?"* (T31).

```
<số liệu>
05_audience/_metrics_raw.json → context.prayer_devo     ← chữ nhỏ, xám, ngay dưới
```

Câu trích dẫn thật: in nghiêng, gạch bên trái, kèm `comment_id` + số tim.

**Số liệu từ nguồn ngoài** phải ghi rõ tên nguồn và cỡ mẫu:
`nguồn ngoài: FMG _ Nghiên cứu thị trường Mỹ.xlsx → sheet «Chân dung» · n=1.017`

---

## 6. ĐỌC SỐ TỪ FILE, ĐỪNG GÕ TAY

Builder **không được gõ cứng** điểm số hay chỉ số (T27).

```python
_sc = json.load(open(N/"_state/scores.json"))
T3  = _sc["axes"]["T3"]["score"]        # ✅
# T3 = 4.4                               # ❌ mục nát khi metric đổi
```

`pipeline/report/verify_reports.py` dò lại toàn bộ PDF sau mỗi lần dựng để bắt lỗi này.

---

## 7. TIÊU CHÍ XONG CHO MỘT BÁO CÁO

- [ ] Mọi cột số dùng `.n`; nhãn dùng `.c`; chữ căn trái
- [ ] Tiêu đề cột căn cùng chiều với dữ liệu
- [ ] Bảng ngưỡng để điểm làm cột
- [ ] Số theo quy ước Việt, điểm không làm tròn
- [ ] Mọi số liệu có nguồn truy vết
- [ ] Không gõ cứng điểm — đọc `scores.json`
- [ ] `verify_reports.py` chạy sạch
