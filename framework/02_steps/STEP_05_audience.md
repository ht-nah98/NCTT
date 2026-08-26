# STEP_05 · CHÂN DUNG KHÁCH HÀNG

| | |
|---|---|
| **Agent** | A4 · Audience Researcher |
| **Câu hỏi** | Khách là ai? Vì sao xem? |
| **Đầu ra** | `05_audience/` |
| **Trục** | — |

---

## QUY TRÌNH

Runbook chi tiết nằm trong đặc tả agent:
👉 **`framework/01_agents/A4_audience_researcher.md`**

Agent đó chứa đầy đủ: nhiệm vụ từng bước · tiêu chí xong · bẫy thường gặp.

## TRƯỚC KHI CHẠY
1. Đọc `framework/00_system/05_FILE_CONTRACTS.md` — xác nhận file đầu vào đã tồn tại
2. Đọc `<N>/PROGRESS.md` — xem bước trước để lại cảnh báo gì
3. Đọc đặc tả agent tương ứng

## SAU KHI CHẠY
1. Ghi output đúng đường dẫn trong hợp đồng file
2. Thêm metric vào `_state/metrics.json` (kèm `_meta`)
3. Cập nhật `PROGRESS.md`: trạng thái · phát hiện chính · độ tin cậy · cảnh báo cho bước sau
