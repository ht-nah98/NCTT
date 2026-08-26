# STEP_00 · SETUP

| | |
|---|---|
| **Agent** | — (người làm) |
| **Đầu vào** | Dữ liệu crawl thô |
| **Đầu ra** | `NICHE_BRIEF.md` · `PROGRESS.md` · cây thư mục |

---

## 1. TẠO THƯ MỤC NGÁCH
```bash
NICHE=<tên-ngách-kebab-case>
mkdir -p niches/$NICHE/{00_input/{raw,processed},02_market,03_competitor,\
04_outlier,05_audience,06_keyword,07_monetization,99_report,_state}
cp framework/03_templates/NICHE_BRIEF.md niches/$NICHE/
cp framework/03_templates/PROGRESS.md    niches/$NICHE/
```

## 2. ĐẶT DỮ LIỆU THÔ
Chép dữ liệu crawl vào `00_input/raw/`. **Không sửa file gốc** (quy tắc R1).

## 3. KIỂM KÊ DỮ LIỆU
Liệt kê bảng có gì, bao nhiêu dòng, cột nào. Đối chiếu `02_DATA_MODEL.md`:

| Câu hỏi | Không đạt thì sao |
|---|---|
| Có đủ 3 bảng bắt buộc? | **Dừng** — không chạy được |
| Có `comments` không? | Mất STEP_05 — cân nhắc crawl thêm |
| `video_stats` có mấy snapshot? | 1 snapshot → hạ tin cậy trục T2 |
| Bảng tùy chọn phủ ≥ 30%? | Dưới ngưỡng → ghi rõ, không dùng kết luận |

## 4. ĐIỀN `NICHE_BRIEF.md`
Đặc biệt phần **giả thuyết ban đầu** — ghi TRƯỚC khi phân tích (quy tắc D5).
Sau này đối chiếu xem giả thuyết đúng hay sai; đây là cách chống thiên lệch xác nhận.

## 5. KIỂM TRA CỠ NGÁCH → CHỌN NGƯỠNG LỌC
Theo bảng ở `04_SELECTION_LOGIC.md` §9. Ghi ngưỡng chọn vào `NICHE_BRIEF.md`.

---

## TIÊU CHÍ XONG
- [ ] Cây thư mục đầy đủ
- [ ] Dữ liệu thô đã đặt vào `raw/`
- [ ] `NICHE_BRIEF.md` điền đủ, **có giả thuyết ban đầu**
- [ ] Đã chọn ngưỡng lọc theo cỡ ngách
- [ ] `PROGRESS.md` khởi tạo
