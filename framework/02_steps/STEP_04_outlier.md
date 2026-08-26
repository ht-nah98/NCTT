# STEP_04 · SÀNG LỌC ĐỐI CHỨNG

| | |
|---|---|
| **Agent** | A3 · Outlier Miner |
| **Câu hỏi** | Đặc trưng nào **KHÔNG** phân biệt video thắng với video thua? |
| **Đầu ra** | `04_outlier/` |
| **Trục** | — |

---

## ⚠️ BƯỚC NÀY LOẠI TRỪ, KHÔNG TỔNG HỢP

Tên cũ *"Công thức thắng"* đã bỏ vì gây hiểu nhầm: bước này **bác bỏ** giả thuyết
(kết quả điển hình 0/20 đứng vững), nó không rút ra công thức nào cả.

```
STEP_04   loại bỏ cái KHÔNG hiệu quả   → chạy sớm được, chỉ cần tiêu đề + metadata
STEP_10   công thức sản xuất thật      → tổng hợp SAU 04b + 05 + 06
```

| | STEP_04 | STEP_10 |
|---|---|---|
| Nói gì | **đừng làm gì** | **nên làm gì** |
| Tầng | kiểm định | mô tả |
| Cần bước trước? | không | có — 04b, 05, 06 |

Vì sao 04 chạy được trước 04b/05/06: để chứng minh *"độ dài tiêu đề không phân biệt
thắng/thua"* chỉ cần cột `title`, không cần biết chân dung khách hàng hay từ khóa.
Phép loại trừ độc lập với phép tổng hợp.

Xem `00_system/01_ARCHITECTURE.md` §2.4.

---

## QUY TRÌNH

Runbook chi tiết nằm trong đặc tả agent:
👉 **`framework/01_agents/A3_outlier_miner.md`**

Agent đó chứa đầy đủ: nhiệm vụ từng bước · tiêu chí xong · bẫy thường gặp.

## TRƯỚC KHI CHẠY
1. Đọc `framework/00_system/05_FILE_CONTRACTS.md` — xác nhận file đầu vào đã tồn tại
2. Đọc `<N>/PROGRESS.md` — xem bước trước để lại cảnh báo gì
3. Đọc đặc tả agent tương ứng

## 🖼️ BỔ SUNG: PHÂN TÍCH ẢNH THUMBNAIL THẬT

STEP_04 mặc định chỉ dùng **22 đặc trưng số** đã trích sẵn (độ sáng, bão hòa, điểm chữ...).
Nếu có **file ảnh thật**, chạy thêm:

```bash
python3 pipeline/analyze/step04b_thumbnail.py [niche_path]
```

**Điều kiện:** ảnh `.jpg` đặt tại `<niche>/00_input/raw/thumbs/`, tên file = `video_id`.
Cần **≥30 ảnh mỗi nhóm** (B1 và B4) — script tự dừng nếu thiếu.

**Đo thêm được gì:** khuôn mặt (có/không, bao nhiêu, to nhỏ, vị trí) · bố cục (trọng tâm) ·
chữ (diện tích, vị trí, số khối) · màu chủ đạo · **trùng lặp hình ảnh giữa các kênh** (pHash).

### 🔴 8 ĐẶC TRƯNG THUMBNAIL CỦA STEP_04 ĐO BẰNG PROXY

`mean_lum` · `saturation` · `text_score` · `contrast` · `colorfulness` · `dark_ratio` ·
`center_focus` · `edge_density` — tất cả **trích sẵn trong Excel nguồn**, không đọc từ ảnh thật.

Chúng được gắn cờ `measure="proxy"` trong `04_feature_tests.csv` và hiện cột
**THƯỚC ĐO** trong PDF, để kết luận yếu **trông** yếu.

**Một trong số đó đã được chứng minh là hỏng:** `text_score` chỉ tương quan **0,233**
với lượng chữ thật đo bằng EasyOCR — gần như không liên quan (bài học T19).

⚠️ Vì vậy kết luận "thumbnail không phân biệt thắng/thua" của STEP_04 chỉ có hiệu lực
**với thước đo proxy**. Kết luận thật nằm ở STEP_04b/04g.

Vẫn áp dụng đủ **3 lớp kiểm chống nghịch lý Simpson** như STEP_04 gốc.

## SAU KHI CHẠY
1. Ghi output đúng đường dẫn trong hợp đồng file
2. Thêm metric vào `_state/metrics.json` (kèm `_meta`)
3. Cập nhật `PROGRESS.md`: trạng thái · phát hiện chính · độ tin cậy · cảnh báo cho bước sau
