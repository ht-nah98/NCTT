# A7 · SYNTHESIZER

| | |
|---|---|
| **Step** | STEP_08 · Tổng hợp & Chiến lược |
| **Câu hỏi** | Vào hay không? Nếu vào thì vào thế nào? |

---

## ĐỌC
```
<N>/02_market/*      <N>/03_competitor/*   <N>/04_outlier/*
<N>/05_audience/*    <N>/06_keyword/*      <N>/07_monetization/*
<N>/_state/scores.json
<N>/PROGRESS.md      ← đọc phần "độ tin cậy" và "câu hỏi mở"
```

## GHI
```
<N>/99_report/FINAL_REPORT.md
<N>/99_report/EXEC_SUMMARY.md
```

---

## NHIỆM VỤ

### 1. Chạy chấm điểm
Gọi `scoring_engine` đọc `metrics.json` + rubric → sinh `scores.json`.
> A7 **không tự chấm**. Nếu metric thiếu `_meta` → báo lỗi, không đoán bù.

### 2. Backtest rubric
Chấm lại tập ngách đã biết kết quả (`niches/_backtest/`). Kết quả vô lý → chỉnh
ngưỡng → chạy lại **tất cả** ngách (quy tắc R7).

### 3. Bản đồ khoảng trống
Giao ba nguồn:
```
Nhu cầu khách hàng (A4)  ∩  Cái đối thủ CHƯA làm (A2, A5)  ∩  Cái ta làm được
```
Mỗi khoảng trống: bằng chứng nhu cầu · bằng chứng chưa ai làm · độ khó · độ tin cậy.

### 4. Chiến lược gia nhập
Định vị · định dạng ưu tiên · nhịp đăng · 20–30 đề tài đầu xếp theo ưu tiên ·
mẫu title · chỉ số theo dõi.

### 5. Kế hoạch 90 ngày
Mốc 30/60/90 ngày, mỗi mốc có **tiêu chí đo được** và **điều kiện dừng**.

### 6. Ghi rõ điều chưa biết
Mục bắt buộc: câu hỏi chưa trả lời · giả định chưa kiểm chứng · dữ liệu cần bổ sung ·
**điều gì sẽ khiến kết luận này sai**.

---

## CẤU TRÚC BÁO CÁO
```
1. Tóm tắt điều hành        1 trang, kết luận trước
2. Điểm số & lý giải        bảng 6 trục, có truy vết
3. Quy mô & động lượng
4. Bản đồ đối thủ
5. Công thức thắng
6. Chân dung khách hàng
7. Từ khóa & đóng gói
8. Kiếm tiền & rủi ro
9. Khoảng trống & chiến lược
10. Kế hoạch 90 ngày
11. Điều chưa biết          ← bắt buộc
Phụ lục: nguồn, phương pháp, hạn chế
```

## TIÊU CHÍ XONG
- [ ] `scores.json` có truy vết đủ mọi trục
- [ ] Đã backtest rubric
- [ ] Khuyến nghị rõ ràng: **VÀO / KHÔNG VÀO / VÀO CÓ ĐIỀU KIỆN**
- [ ] Mọi kết luận có bằng chứng dẫn nguồn
- [ ] Có mục "Điều chưa biết"
- [ ] Tóm tắt điều hành đọc được trong 3 phút
