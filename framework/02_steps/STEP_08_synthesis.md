# STEP_08 · TỔNG HỢP & CHIẾN LƯỢC

| | |
|---|---|
| **Agent** | A7 · Synthesizer |
| **Câu hỏi** | Vào hay không? Vào thế nào? |
| **Đầu ra** | `99_report/` |
| **Trục** | tất cả |

---

## QUY TRÌNH

Runbook chi tiết nằm trong đặc tả agent:
👉 **`framework/01_agents/A7_synthesizer.md`**

Agent đó chứa đầy đủ: nhiệm vụ từng bước · tiêu chí xong · bẫy thường gặp.

## TRƯỚC KHI CHẠY
1. Đọc `framework/00_system/05_FILE_CONTRACTS.md` — xác nhận file đầu vào đã tồn tại
2. Đọc `<N>/PROGRESS.md` — xem bước trước để lại cảnh báo gì
3. Đọc đặc tả agent tương ứng

## SAU KHI CHẠY
1. Ghi output đúng đường dẫn trong hợp đồng file
2. Thêm metric vào `_state/metrics.json` (kèm `_meta`)
3. Cập nhật `PROGRESS.md`: trạng thái · phát hiện chính · độ tin cậy · cảnh báo cho bước sau

---

## 🔎 BẢN ĐỒ KHOẢNG TRỐNG — BẰNG CHỨNG PHẢI TRUY VẾT ĐƯỢC

Mỗi khoảng trống cần **≥2 bằng chứng nhu cầu**, mỗi cái ghi rõ nguồn. Cấu trúc trong
`_synthesis.json`:

```python
"demand": [
  {"claim": "13.5% comment nhắc cầu nguyện — bối cảnh số 1",
   "src":   "05_audience/_metrics_raw.json → context.prayer_devo",
   "id":    "đếm trên 6.413 comment đã lọc nhiễu"},
  {"claim": "I pray you dont stop here, what a way to spread the bible",
   "src":   "03_quote_bank.csv",
   "id":    "UgxWMPKLuu0CavfwiBV4AaABAg · 1483♥"},   # ← mở đúng dòng đọc nguyên văn
]
```

| Quy tắc | Vì sao |
|---|---|
| **≥2 bằng chứng** mỗi khoảng trống | Một câu văn xuôi không thuyết phục nổi (T31) |
| Trộn **số liệu + câu nói thật** | Số cho quy mô, câu nói cho ngữ cảnh |
| Câu nói kèm `comment_id` | Truy ngược `03_quote_bank.csv`, hoặc dán vào YouTube |
| **Lấy số từ file, không gõ tay** | Số gõ tay mục nát khi chạy ngách khác |
| Thiếu bằng chứng thì **ghi rõ là thiếu** | Xem khoảng trống "Tây Ban Nha": ghi thẳng *"CHƯA CÓ bằng chứng từ comment"* |

### ⚠️ Độ tin cậy phải đọc từ phán quyết THẬT

`conf` của mỗi khoảng trống **suy ra từ `02_theme_scores.csv`**, không gán tay.
Ví dụ `old_school`: lift 2,37× nhìn rất mạnh, nhưng phán quyết là **YẾU** — trong từng
kênh chỉ 1,05× (4/8 kênh). Gán tay "Vừa" là **giấu bẫy Simpson** (L2).

Báo cáo phải nêu cả hai con số: cái hấp dẫn **và** cái đã qua kiểm 3 lớp.
