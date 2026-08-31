# BLUEPRINT — XÂY HỆ THỐNG AI AGENT PHÂN TÍCH NGÁCH NHẠC

> **Đây không phải tài liệu mô tả hệ thống hiện có.** Đây là bản thiết kế để
> bạn xây sản phẩm mới, trong đó AI agent làm việc mà Claude đang làm thủ công.
>
> Phiên bản: v1.0 · Lập 2026-08-28

---

## Vấn đề đang giải

```
HIỆN TẠI
  Dữ liệu → [Claude đọc, nghĩ, viết script, chạy, kết luận] → Báo cáo
             ▲ tư duy nằm TRONG ĐẦU, không đóng gói được

MỤC TIÊU
  Dữ liệu → [Agent: đọc → quyết định → gọi tool → kết luận] → Báo cáo
             ▲ tư duy nằm trong        ▲ phép tính nằm trong
               SYSTEM PROMPT             TOOL (code tất định)
```

**Nguyên tắc vàng:** agent **không bao giờ tự tính số**. Mọi con số đến từ tool.

---

## Người mới bắt đầu ở đâu

> **Đừng đọc từ file 00.** Nếu bạn chưa từng xây AI agent, mở
> **`12_BAT_DAU_TU_DAU.md`** trước — nó nói ngày đầu tiên làm gì.
>
> Nguyên tắc quan trọng nhất: **làm thủ công một ngách trước khi xây agent.**
> Không có "đáp án" tự tính tay thì không có cách nào biết agent đúng hay bịa.

---

## Đọc theo thứ tự

| File | Nội dung |
|---|---|
| `00_TONG_QUAN.md` | Kiến trúc 7 module · lộ trình 6 giai đoạn |
| `01_M1_DATA_CONTRACT.md` | Schema · 4 cột suy ra · validator · R6 |
| `02_M2_TOOL_LAYER.md` | 20 tool · **code đầy đủ** tool lõi · test |
| `03_M3_CONTEXT.md` | Nạp gì vào agent · nén lịch sử · trace |
| `04_M4_AGENTS.md` | **5 system prompt đầy đủ, copy dùng được** |
| `05_M5_ORCHESTRATOR.md` | Luồng · 2 cổng dừng · checkpoint · ngân sách |
| `06_M6_VERIFICATION.md` | 6 lớp bắt agent bịa · bộ test đỏ |
| `07_M7_OUTPUT.md` | JSON → PDF · biểu đồ · 3 bẫy WeasyPrint |
| `08_TRI_THUC_NGACH.md` | **Tri thức phải nhúng vào prompt** |
| `09_CHECKLIST_TRIEN_KHAI.md` | Danh sách kiểm từng giai đoạn |
| **`10_GOI_MODEL.md`** | **Vòng lặp tool-use · schema 5 agent · retry · chi phí** |
| **`11_CODE_CHAY_DUOC.md`** | **23 hàm còn thiếu, đã chạy thử trên dữ liệu thật** |
| **`12_BAT_DAU_TU_DAU.md`** | **Tuần 0 làm tay · 30 regex mồi · lộ trình 4 tuần** |

---

## Kiến trúc 5 agent

| Agent | Vai | Thay việc gì của Claude |
|---|---|---|
| **A1 Scout** | Gác cổng — có đáng làm không | đọc dữ liệu, xem có đáng làm |
| **A2 Analyst** | Sinh giả thuyết, gọi tool kiểm | nghĩ "đo cái gì bây giờ" |
| **A3 Skeptic** | **Phá** phát hiện của A2 | tự hỏi "hay là do nguyên nhân khác" |
| **A4 Synthesizer** | Gom thành hướng đi | đúc kết |
| **A5 Writer** | Viết báo cáo | viết tiếng Việt |

**Vì sao tách A3 riêng:** một agent làm tất sẽ tự xác nhận chính mình — nó
sinh giả thuyết rồi tự đánh giá, và luôn thấy mình đúng. A3 có nhiệm vụ duy
nhất là phá A2. Đây là cách đưa nguyên tắc *"luôn có bằng chứng phản bác"* vào
**kiến trúc**, không chỉ vào lời hứa.

---

## Ba phép thử quyết định

Không qua thì đừng đi tiếp:

**① Sau M1** — tạo ngách trống hoàn toàn, chạy `load()`. Phải chạy được mà
không sửa code.

**② Sau M2** — dựng dữ liệu giả có bẫy Simpson cài sẵn. `test_title_theme()`
phải trả `BÁC BỎ (Simpson)`.

**③ Sau M6** — chạy `test_red_team()`. Phải bắt được cả 5 ca bịa số.

---

## Bản tối thiểu nếu thiếu thời gian

```
M1 (data contract) + M2 nhóm C (kiểm định) + M6 (verification)
+ A2 (Analyst) + A3 (Skeptic)
```

Đây đã là hệ thống **sinh giả thuyết và tự phản biện** — phần khó nhất và giá
trị nhất. Bốn module còn lại làm dần được.

---

## Ước tính công sức và chi phí

| Giai đoạn | Thời gian |
|---|---|
| M1 Data Contract | 3–5 ngày |
| M2 Tool Layer | 2–3 tuần |
| M6 Verification | 3–5 ngày |
| M3 + M4 (A1, A2) | 1–2 tuần |
| M4 (A3, A4, A5) + M7 | 1–2 tuần |
| M5 Orchestrator | 1 tuần |

**Token mỗi lần chạy:** dừng cổng 1 ~15k · dừng cổng 2 ~150k · chạy đủ 300–500k.

> **Mẹo tiết kiệm:** chạy A1 cho mọi ngách ứng viên trước (15k/ngách), rồi mới
> chạy đủ cho ngách qua cổng. Sàng 20 ngách tốn bằng chạy đủ một ngách.

---

## Liên kết

| Cần gì | Đọc |
|---|---|
| Hệ thống hiện tại hoạt động thế nào | `../05_phuong_phap/` |
| 90 bài học đã rút | `../04_reference/lessons_learned.md` |
| Bốn tài liệu đầu ra T1.1–T1.4 | `../00_system/11_OUTPUT_CONTRACT.md` |
| Sáu nhóm nguồn Y·P·S·V·K·N | `../00_system/10_SOURCE_CLASSES.md` |
