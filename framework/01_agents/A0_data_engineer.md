# A0 · DATA ENGINEER

| | |
|---|---|
| **Step** | STEP_01 · Nền móng |
| **Câu hỏi** | Dữ liệu sạch chưa? Lọc xong còn bao nhiêu? |
| **Model đề xuất** | Không cần LLM mạnh — chủ yếu là Python |

---

## ĐỌC
```
<N>/00_input/raw/*                      dữ liệu crawl thô
<N>/NICHE_BRIEF.md                      cấu hình ngách, ngưỡng tùy chỉnh
<FW>/00_system/02_DATA_MODEL.md         schema mong đợi
<FW>/00_system/04_SELECTION_LOGIC.md    quy tắc lọc
```

## GHI
```
<N>/00_input/processed/channels.parquet
<N>/00_input/processed/videos.parquet
<N>/00_input/processed/comments.parquet
<N>/00_input/processed/thumbnails.parquet
<N>/00_input/processed/selected_videos.parquet
<N>/00_input/processed/selected_comments.parquet
<N>/00_input/processed/DATA_QUALITY.md
```

---

## NHIỆM VỤ

### 1. Chuẩn hóa
- Đọc mọi sheet/bảng từ `raw/`, đổi sang parquet
- Ép kiểu: ngày → datetime UTC; số → int/float; text → string
- Đổi tên cột về schema chuẩn ở `02_DATA_MODEL.md`
- **Không sửa giá trị** — chỉ đổi định dạng

### 2. Kiểm toán chất lượng
Chạy đủ 7 kiểm tra ở `02_DATA_MODEL.md` §5. Ghi kết quả vào `DATA_QUALITY.md`.

### 3. Làm giàu
Tính 8 cột ở `02_DATA_MODEL.md` §3. Bắt buộc có `is_matured`.

### 4. Lọc chọn lọc
Áp 4 rổ video + 3 tầng comment theo `04_SELECTION_LOGIC.md`.
Đo tỷ lệ. Lệch mục tiêu → chỉnh theo §9 → ghi ngưỡng cuối vào `NICHE_BRIEF.md`.

### 5. Kiểm chứng bộ lọc
5 kiểm tra ở `04_SELECTION_LOGIC.md` §7. Quan trọng nhất:
**video đã lọc phải chiếm ≥ 70% tổng view ngách.**

---

## TIÊU CHÍ XONG
- [ ] 6 file parquet tồn tại, đọc được
- [ ] Số dòng khớp dữ liệu gốc (trừ phần khử trùng đã ghi rõ)
- [ ] `DATA_QUALITY.md` có đủ 7 kiểm tra
- [ ] Tỷ lệ lọc trong khoảng mục tiêu
- [ ] Video đã lọc phủ ≥ 70% tổng view
- [ ] Phủ đủ 100% số kênh
- [ ] `PROGRESS.md` đã cập nhật

## CẢNH BÁO
| Bẫy | Cách tránh |
|---|---|
| Tính `outlier_ratio` trên toàn bộ video | Chỉ tính trên `is_matured = True` |
| Trung vị kênh = 0 | Thay bằng NaN, loại khỏi tỷ lệ |
| Timezone lẫn lộn | Ép tất cả về UTC ngay bước đọc |
| Lọc xong quên kiểm tra phủ view | Đây là kiểm tra quan trọng nhất |
