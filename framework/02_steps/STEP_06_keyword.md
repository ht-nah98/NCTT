# STEP_06 · TỪ KHÓA & ĐÓNG GÓI

| | |
|---|---|
| **Agent** | A5 · Keyword Analyst |
| **Câu hỏi** | Nội dung truyền tải thế nào? |
| **Đầu ra** | `06_keyword/` |
| **Trục** | — |

---

## QUY TRÌNH

Runbook chi tiết nằm trong đặc tả agent:
👉 **`framework/01_agents/A5_keyword_analyst.md`**

Agent đó chứa đầy đủ: nhiệm vụ từng bước · tiêu chí xong · bẫy thường gặp.

## TRƯỚC KHI CHẠY
1. Đọc `framework/00_system/05_FILE_CONTRACTS.md` — xác nhận file đầu vào đã tồn tại
2. Đọc `<N>/PROGRESS.md` — xem bước trước để lại cảnh báo gì
3. Đọc đặc tả agent tương ứng

## SAU KHI CHẠY
1. Ghi output đúng đường dẫn trong hợp đồng file
2. Thêm metric vào `_state/metrics.json` (kèm `_meta`)
3. Cập nhật `PROGRESS.md`: trạng thái · phát hiện chính · độ tin cậy · cảnh báo cho bước sau
