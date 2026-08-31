# BLUEPRINT — XÂY HỆ THỐNG AI AGENT PHÂN TÍCH NGÁCH NHẠC YOUTUBE

> Đây **không phải** tài liệu mô tả hệ thống hiện có. Đây là **bản thiết kế để
> bạn xây sản phẩm mới**, trong đó AI agent làm việc mà Claude đang làm thủ công.
>
> Phiên bản: v1.0 · Lập 2026-08-28 · Phạm vi: ngách nhạc trên YouTube

---

## 1. VẤN ĐỀ CẦN GIẢI

### Hiện trạng

```
Dữ liệu thô  →  [Claude đọc, nghĩ, viết script, chạy, đọc kết quả, kết luận]  →  Báo cáo
                 ▲
                 └── toàn bộ tư duy nằm TRONG ĐẦU, không nằm trong code
```

Hệ quả: **không đóng gói được thành sản phẩm.** Muốn chạy ngách mới lại phải
có Claude ngồi làm lại từ đầu.

### Mục tiêu

```
Dữ liệu thô  →  [AI Agent: đọc → quyết định → gọi tool → đọc kết quả → kết luận]  →  Báo cáo
                 ▲                              ▲
                 └── tư duy nằm trong           └── phép tính nằm trong
                     SYSTEM PROMPT                  TOOL (code tất định)
```

Agent thay Claude ở phần **quyết định**. Code giữ phần **tính toán**.

### Ranh giới không được vượt

| Agent ĐƯỢC làm | Agent KHÔNG được làm |
|---|---|
| Chọn phân tích nào chạy trước | Tự tính trung vị, p-value, lift |
| Sinh giả thuyết từ dữ liệu | Tự bịa con số không có trong tool output |
| Quyết định có cần kiểm thêm không | Đổi ngưỡng phán quyết |
| Diễn giải bảng số thành câu | Bỏ qua kết quả ngược chiều |
| Dừng và báo "không đủ dữ liệu" | Suy đoán thuộc tính cá nhân (R6) |

> **Nguyên tắc vàng:** agent **không bao giờ tự tính số**. Mọi con số phải đến
> từ tool. Nếu agent viết ra một con số không có trong tool output → đó là ảo giác,
> và lớp kiểm chứng phải bắt được.

---

## 2. KIẾN TRÚC — 7 MODULE

```
┌─ M1 · DATA CONTRACT ────────────────────────────────────────┐
│  Chuẩn hoá dữ liệu thô → schema cố định                     │
│  KHÔNG có agent. Code thuần.                                │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─ M2 · TOOL LAYER ───────────────────────────────────────────┐
│  ~20 tool tất định: đo, lọc, kiểm định, vẽ                  │
│  KHÔNG có agent. Code thuần. Agent gọi qua schema.          │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─ M3 · CONTEXT BUILDER ──────────────────────────────────────┐
│  Nạp gì vào context của agent, nạp bao nhiêu, nạp lúc nào   │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─ M4 · AGENT LAYER ──────────────────────────────────────────┐
│  5 agent chuyên trách, mỗi agent 1 system prompt            │
│  A1 Scout · A2 Analyst · A3 Skeptic · A4 Synthesizer · A5 Writer │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─ M5 · ORCHESTRATOR ─────────────────────────────────────────┐
│  Điều phối: agent nào chạy khi nào, cổng dừng, retry        │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─ M6 · VERIFICATION ─────────────────────────────────────────┐
│  Bắt ảo giác, bắt số bịa, bắt kết luận trái kiểm định       │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─ M7 · OUTPUT ───────────────────────────────────────────────┐
│  Sinh 4 tài liệu T1.1–T1.4 + biểu đồ + PDF                  │
└─────────────────────────────────────────────────────────────┘
```

### Vì sao 5 agent chứ không 1

Một agent làm tất sẽ **tự xác nhận chính mình**: nó sinh giả thuyết rồi tự
đánh giá giả thuyết đó, và luôn thấy mình đúng.

Tách ra thì **A3 Skeptic có nhiệm vụ duy nhất là phá A2**. Đây là cách đưa
nguyên tắc *"luôn có bằng chứng phản bác"* vào kiến trúc, không chỉ vào lời hứa.

| Agent | Vai | Đầu vào | Đầu ra |
|---|---|---|---|
| **A1 Scout** | Khảo sát, quyết định có đáng phân tích tiếp không | schema + thống kê mô tả | GO / NO-GO + lý do |
| **A2 Analyst** | Sinh giả thuyết, gọi tool kiểm định | dữ liệu đã lọc | danh sách phát hiện |
| **A3 Skeptic** | **Phá** từng phát hiện của A2 | phát hiện + dữ liệu gốc | phát hiện sống sót |
| **A4 Synthesizer** | Gom phát hiện thành kết luận | phát hiện đã qua A3 | kết luận + độ tin cậy |
| **A5 Writer** | Viết báo cáo | kết luận + số liệu | 4 tài liệu T1.x |

---

## 3. LỘ TRÌNH XÂY — 6 GIAI ĐOẠN

Xếp theo thứ tự bắt buộc. Không nhảy cóc — mỗi giai đoạn là nền của giai đoạn sau.

| GĐ | Việc | Thời gian ước | Xong khi |
|---|---|---|---|
| **1** | M1 Data Contract | 3–5 ngày | Nạp được 2 ngách khác nhau vào cùng schema |
| **2** | M2 Tool Layer | 2–3 tuần | 20 tool có test, gọi được bằng JSON |
| **3** | M6 Verification | 3–5 ngày | Bắt được số bịa trong output giả lập |
| **4** | M3 + M4 (A1, A2) | 1–2 tuần | Agent sinh được giả thuyết đúng định dạng |
| **5** | M4 (A3, A4, A5) | 1–2 tuần | Chạy hết luồng ra được T1.1 |
| **6** | M5 Orchestrator | 1 tuần | Chạy tự động end-to-end, có cổng dừng |

> **Vì sao M6 Verification làm TRƯỚC agent:** nếu không có lớp bắt ảo giác từ
> đầu, bạn sẽ không biết agent đang bịa. Và một khi đã quen nhìn output đẹp,
> rất khó phát hiện chỗ sai. Xây lưới trước khi thả agent.

---

## 4. CÁC FILE TRONG BLUEPRINT NÀY

| File | Nội dung |
|---|---|
| `00_TONG_QUAN.md` | ← bạn đang đọc |
| `01_M1_DATA_CONTRACT.md` | Schema, validator, code khung |
| `02_M2_TOOL_LAYER.md` | 20 tool: schema + code + test |
| `03_M3_CONTEXT.md` | Nạp gì vào context, chống tràn |
| `04_M4_AGENTS.md` | **5 system prompt đầy đủ** |
| `05_M5_ORCHESTRATOR.md` | Luồng điều phối, cổng dừng |
| `06_M6_VERIFICATION.md` | 6 lớp kiểm chứng |
| `07_M7_OUTPUT.md` | Sinh tài liệu và biểu đồ |
| `08_TRI_THUC_NGACH.md` | Tri thức domain phải nhúng vào prompt |
| `09_CHECKLIST_TRIEN_KHAI.md` | Danh sách kiểm từng giai đoạn |

---

## 5. NGUYÊN TẮC THIẾT KẾ — ÁP CHO MỌI MODULE

### ① Agent không tính số

Mọi con số đến từ tool. Agent chỉ **chọn tool nào gọi** và **diễn giải kết quả**.

```
❌ Agent: "Tôi tính được lift là 1,62×"
✅ Agent: gọi tool test_theme(theme="thanks") → nhận {"lift": 1.62} → diễn giải
```

### ② Mọi output có schema đóng

Agent trả JSON theo schema cố định, không trả văn xuôi tự do. Lý do: có schema
thì mới validate được, mới bắt được ảo giác.

### ③ Mỗi phát hiện phải qua Skeptic

Không có ngoại lệ. A2 sinh 10 phát hiện thì A3 phải phá cả 10.

### ④ Ngưỡng phán quyết nằm trong CODE, không nằm trong prompt

```python
# ✅ trong tool
def verdict(p, lift, within_lift, n_ch):
    if p >= 0.05: return "BÁC BỎ"
    if n_ch >= 5 and within_lift < 1: return "BÁC BỎ (Simpson)"
    ...
```

Nếu để agent tự quyết ngưỡng, mỗi lần chạy sẽ ra phán quyết khác.

### ⑤ Ghi lại mọi quyết định của agent

Mỗi lần agent chọn gì, vì sao → ghi vào `_trace.jsonl`. Đây là thứ giúp bạn
gỡ lỗi khi agent làm sai, và là dữ liệu để cải thiện prompt.

---

## 6. ĐIỀU KIỆN TIÊN QUYẾT

Trước khi bắt đầu, cần có:

| Thứ | Vì sao |
|---|---|
| Dữ liệu ≥2 ngách | Để biết cái gì là chung, cái gì riêng từng ngách |
| Khoá API mô hình | Claude/GPT — chọn model có tool-use tốt |
| Ngân sách token ước tính | Mỗi lần chạy 1 ngách ≈ 200k–500k token đầu vào |
| Người kiểm chứng | Ai đó đọc output và nói "cái này sai" |

> **Cảnh báo về chi phí:** agent gọi tool nhiều vòng. Một ngách chạy đủ 5 agent
> có thể tốn 500k–1M token. Nên thiết kế cổng dừng sớm (M5) từ đầu.

---

## 7. ĐỌC TIẾP

Bắt đầu từ `01_M1_DATA_CONTRACT.md`. Đừng đọc phần agent trước — nếu schema
dữ liệu chưa chuẩn thì mọi prompt viết ra đều phải sửa lại.
