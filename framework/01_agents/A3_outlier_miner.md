# A3 · OUTLIER MINER

| | |
|---|---|
| **Step** | STEP_04 · Sàng lọc đối chứng |
| **Câu hỏi** | Video nổ có gì chung mà video thường không có? |
| **Ghi chú** | ROI cao nhất trong toàn bộ quy trình |

---

## ĐỌC
```
<N>/00_input/processed/selected_videos.parquet
<N>/00_input/processed/thumbnails.parquet
<N>/03_competitor/01_channel_map.md
```

## GHI
```
<N>/04_outlier/01_winning_formula.md
<N>/04_outlier/02_outlier_table.csv
<N>/04_outlier/03_control_group.csv
<N>/_state/metrics.json   → namespace: formula.*
```

---

## NGUYÊN TẮC CỐT LÕI — SO SÁNH CÓ ĐỐI CHỨNG

**Không bao giờ mô tả video thắng mà không so với video thua.**

```
Rổ B1 (outlier, ~500)  ←→  Rổ B4 (đối chứng, ~130)
```

Mọi phát biểu phải ở dạng so sánh:
- ❌ Sai: "Video thắng thường có title dài 60 ký tự"
- ✅ Đúng: "Video thắng: title trung vị 62 ký tự. Video thua: 58. **Chênh lệch không đáng kể → title dài KHÔNG phải yếu tố quyết định**"

> Phần lớn giả thuyết sẽ **bị bác bỏ** khi so với đối chứng. Đó là kết quả tốt — nó loại
> bỏ mê tín và giữ lại yếu tố thật.

---

## NHIỆM VỤ

### 1. So sánh theo định dạng
VPD trung vị theo `duration_band`, cả hai rổ. Định dạng nào thắng thật?
Đối chiếu **số lượng video mỗi định dạng** — nếu thị trường đổ dồn vào định dạng
hiệu quả thấp → đó là **khoảng trống**.

### 2. Giải phẫu tiêu đề
So sánh B1 vs B4 trên: độ dài · số từ · emoji · dấu phân cách · từ khóa lặp ·
có tên riêng cụ thể không (tên bài, tên chương, tên nhân vật) · cấu trúc.

### 3. Chủ đề lặp lại
Trích cụm từ xuất hiện ở **nhiều kênh khác nhau** trong rổ B1.
Xuất hiện ở ≥ 3 kênh khác nhau → **công thức tái lập được**, không phải may mắn.

### 4. Thumbnail
So sánh 22 đặc trưng có sẵn giữa B1 và B4. Kiểm định ý nghĩa thống kê,
không chỉ nhìn chênh lệch trung bình.

### 5. Thời điểm đăng
Ngày trong tuần, giờ. ⚠️ Thường **không có tương quan** — nếu vậy phải nói rõ,
đừng cố tìm mẫu không tồn tại.

---

## ĐẦU RA BẮT BUỘC

`01_winning_formula.md` phải có 3 phần:

| Phần | Nội dung |
|---|---|
| **Yếu tố ĐÃ XÁC NHẬN** | Khác biệt rõ giữa B1 và B4 |
| **Yếu tố ĐÃ BÁC BỎ** | Tưởng quan trọng nhưng B1 và B4 giống nhau |
| **Yếu tố CHƯA KẾT LUẬN** | Cần thêm dữ liệu |

### 6 · Ảnh thumbnail thật (nếu có)
Chạy `pipeline/analyze/step04b_thumbnail.py`. Chỉ chạy khi có ≥30 ảnh mỗi nhóm.
Đo: khuôn mặt · bố cục · chữ · màu · trùng lặp hình ảnh giữa kênh.
> Nếu chưa có ảnh: ghi rõ trong output là "chưa phân tích được ảnh thật", **đừng bỏ qua im lặng**.

## TIÊU CHÍ XONG
- [ ] Mọi phát biểu đều là **so sánh B1 vs B4**
- [ ] Có phần "đã bác bỏ" — nếu trống là dấu hiệu làm chưa kỹ
- [ ] Chủ đề lặp có ghi rõ **số kênh khác nhau**
- [ ] Danh sách video outlier xuất ra CSV
