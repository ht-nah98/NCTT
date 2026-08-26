# A2 · COMPETITOR ANALYST

| | |
|---|---|
| **Step** | STEP_03 · Đối thủ |
| **Câu hỏi** | Ai đang thắng? Người mới còn cửa không? |
| **Trục phụ trách** | T3 Cửa gia nhập · T4 Phù hợp AI |

---

## ĐỌC
```
<N>/00_input/processed/channels.parquet
<N>/00_input/processed/selected_videos.parquet
<N>/02_market/01_market_sizing.md
```

## GHI
```
<N>/03_competitor/01_channel_map.md
<N>/03_competitor/02_channel_table.csv
<N>/_state/metrics.json   → namespace: entry.*, ai_fit.*
```

---

## NHIỆM VỤ

### 1. Phân loại mô hình kênh (T4)
Gắn nhãn mỗi kênh — dựa vào **bằng chứng quan sát được**, không đoán:

| Nhãn | Dấu hiệu |
|---|---|
| `ai-first` | Nhịp đăng rất dày, thumbnail đồng nhất theo mẫu, mô tả lặp khuôn, không có mặt người |
| `artist` | Có tên nghệ sĩ thật, đăng thưa, nội dung biểu diễn |
| `rebroadcast` | Đăng lại nội dung cũ, chất lượng ảnh không đồng nhất |
| `hybrid` | Trộn nhiều kiểu |

`M4.1 = % kênh trong top 20 (theo view) là ai-first`

> ⚠️ Đây là **suy luận từ dấu hiệu**, không phải sự thật tuyệt đối. Ghi độ tin cậy và
> liệt kê dấu hiệu đã dùng.

### 2. Cửa gia nhập (T3)
```
M3.1 Gini             hệ số bất bình đẳng view giữa các kênh
M3.2 newcomer_success % kênh < 12 tháng đạt ≥ 100k view/tháng   ← trọng số cao nhất
M3.3 time_to_traction số tháng trung vị để kênh mới đạt 100k view tích lũy
```

### 3. Phân tầng kênh
Dẫn đầu / thách thức / mới nổi / hụt hơi. Kèm view, tuổi, nhịp đăng, view mỗi video.

### 4. Giải mã kênh hiệu suất cao nhất
Tìm kênh có **view/video cao nhất** (không phải tổng view cao nhất). Phân tích riêng:
họ làm gì khác? Đây thường là hình mẫu đáng học nhất cho người mới.

---

## TIÊU CHÍ XONG
- [ ] 100% kênh có nhãn mô hình + dấu hiệu kèm theo
- [ ] Đủ M3.1, M3.2, M3.3, M4.1 có `_meta`
- [ ] Bảng phân tầng đầy đủ
- [ ] Có phần giải mã kênh hiệu suất cao nhất
- [ ] `02_channel_table.csv` xuất được, mở bằng Excel
