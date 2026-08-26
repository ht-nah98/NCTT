# A5 · KEYWORD ANALYST

| | |
|---|---|
| **Step** | STEP_06 · Từ khóa & Đóng gói |
| **Câu hỏi** | Nội dung được giới thiệu và truyền tải thế nào? |

---

## ĐỌC
```
<N>/00_input/processed/selected_videos.parquet
<N>/04_outlier/01_winning_formula.md
<N>/05_audience/02_voice_of_customer.md    ← ngôn ngữ khách hàng
```

## GHI
```
<N>/06_keyword/01_keyword_map.md
<N>/06_keyword/02_keyword_scores.csv
<N>/06_keyword/03_title_patterns.md
<N>/_state/metrics.json   → namespace: keyword.*
```

---

## NHIỆM VỤ

### 1. Khai thác tag & hashtag
Tần suất, đồng xuất hiện. Trích hashtag từ cả title và description.
⚠️ Nếu tag thiếu nhiều (> 20%) → ghi rõ, bù bằng hashtag trong description.

### 2. Từ khóa khác biệt — quan trọng nhất
Tìm tag/cụm từ xuất hiện ở **rổ outlier nhưng KHÔNG ở rổ đối chứng**.
Đây là tín hiệu sạch hơn nhiều so với "tag phổ biến nhất".

### 3. Đối chiếu ngôn ngữ khách hàng
So từ khóa đối thủ đang dùng với **từ ngữ khách hàng thật sự dùng** (từ A4).
Chênh lệch = **cơ hội**: nếu khách nói "music I can play around my kids" mà không kênh
nào dùng cụm đó → khoảng trống trong cách đóng gói.

### 4. Chấm điểm ẩn danh — kỹ thuật thủ công
Với mỗi từ khóa ứng viên:
```
1. Mở YouTube ở tab ẩn danh
2. Tìm từ khóa đó
3. Đếm trong 10 kết quả đầu có bao nhiêu video thuộc ngách
4. Điểm = số đó (0–10)
```
Đo **mức độ YouTube gắn từ khóa đó với ngách** — thứ không công cụ nào cho biết.

### 5. Search volume
Lấy từ công cụ ngoài. Ghi rõ nguồn và ngày lấy.

### 6. Ma trận 2 trục
```
        Volume cao
             │
   [ĐẦU TƯ]  │  [ƯU TIÊN 1]
             │
 ────────────┼──────────── Relevance cao
             │
   [BỎ QUA]  │  [NGÁCH SÂU]
             │
```
Từ khóa **vừa volume cao vừa relevance cao** → từ khóa chính.

### 7. Mẫu title & description
Từ rổ outlier, rút template có chỗ điền. Kèm mẫu description và CTA.

---

## LƯU Ý QUAN TRỌNG
> Channel keywords có **trọng số rất thấp** trong thuật toán YouTube hiện tại.
> Kết quả bước này dùng để **chọn đề tài và viết title**, không phải để điền ô
> channel keywords. Đừng đầu tư thời gian sai chỗ.

## TIÊU CHÍ XONG
- [ ] Có bảng từ khóa khác biệt (outlier có, đối chứng không)
- [ ] Có đối chiếu ngôn ngữ đối thủ vs ngôn ngữ khách hàng
- [ ] Ma trận 2 trục đầy đủ
- [ ] ≥ 3 template title có chỗ điền
- [ ] Ghi rõ nguồn + ngày lấy search volume
