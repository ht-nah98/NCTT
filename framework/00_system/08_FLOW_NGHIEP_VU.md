# FLOW NGHIỆP VỤ — Bản đồ cho người ngoài kỹ thuật

> Tài liệu này **dịch** hệ thống sang ngôn ngữ nghiệp vụ. Không thay thế
> `01_ARCHITECTURE.md` (bản kỹ thuật) — nó là bản đối chiếu để R&D và IT
> chắc chắn đang nói về cùng một quy trình.
>
> Trả lời đúng 4 câu hỏi đã thống nhất:
> **Ai đưa gì vào · Xử lý thế nào · Data nào ra thông tin gì · Kết quả cuối là gì**

---

## 1. ẨN DỤ CHUNG

| Vai | Việc | Sản phẩm |
|---|---|---|
| **Team R&D** | Lập **hồ sơ bệnh án** | CDKH — phân khúc khách hàng |
| **Phòng IT** | **Xét nghiệm & bắt bệnh** trên hồ sơ đó | Công thức thắng cho từng phân khúc |

Điểm cốt lõi: *cùng là "Nam đau đầu" nhưng nguyên nhân khác nhau → chẩn đoán
và toa thuốc khác nhau.* Một ngách không có **một** công thức thắng — nó có
**mỗi phân khúc một công thức**.

Và như mọi xét nghiệm: kết quả có thể **phản bác** chẩn đoán ban đầu.
Đó là giá trị của bước này, không phải sự cố.

---

## 2. TRẠNG THÁI HIỆN TẠI vs SẮP TỚI

```
LUỒNG CŨ (đang chạy hôm nay)
  danh sách kênh ──▶ [10 bước] ──▶ CDKH (suy ra) + 1 công thức thắng

LUỒNG MỚI (khi R&D bàn giao CDKH)
  danh sách kênh ─┐
                  ├─▶ [10 bước + cổng kiểm CDKH] ──▶ N công thức, mỗi phân khúc một cái
  CDKH ───────────┘                                  + kết luận XÁC NHẬN/BÁC BỎ từng phân khúc
```

**Không bỏ luồng cũ.** Việc hệ thống tự suy CDKH từ comment vẫn giữ — nó trở
thành **đối chứng độc lập** với hồ sơ R&D. Hai chiều gặp nhau ở bảng kiểm định:

- R&D nói: *"phân khúc này là phụ nữ 45–65 đang chịu tang"*
- Hệ thống đo và trả lời: *"XÁC NHẬN — n=?, like trung vị gấp ? lần nền, p<0.001"*
- hoặc: *"BÁC BỎ — tín hiệu thật sự có phản hồi là nhóm cao tuổi, không phải tang chế"*

---

## 3. CÂU 1 — INPUT: AI ĐƯA GÌ VÀO

| Nguồn | Ai cung cấp | Định dạng | Trạng thái |
|---|---|---|---|
| Danh sách kênh + video + comment | R&D (crawl YouTube) | xlsx → `00_input/raw/` | ✅ đang dùng |
| Đặc trưng âm thanh (DSP) | IT trích | yaml → `raw/audio/` | ✅ đang dùng |
| Ảnh thumbnail | IT tải | jpg → `raw/thumbs/` | ✅ đang dùng |
| **CDKH — hồ sơ phân khúc** | **R&D** | **yaml → `raw/cdkh.yaml`** | 🔜 chờ, xem `07_CDKH_CONTRACT.md` |
| Báo cáo ngoài (Luminate, Spotify Research, Scholar) | — | — | ❌ **chưa làm** |
| Diễn đàn (Reddit, X, Quora) | — | — | ❌ **chưa làm** |
| YouTube Studio (analytics nội bộ) | — | — | ❌ **chưa làm** |

> **Khoảng trống đã biết — nói thẳng:** toàn bộ chân dung khách hàng hiện nay
> suy ra **chỉ từ comment YouTube**. Comment chỉ chứa *người chịu bình luận* —
> đây là mẫu thiên lệch, không phải toàn bộ khán giả. Ba nguồn ❌ ở trên
> chính là cột "Nguồn khác" trong file flow của R&D, và hệ thống chưa chạm tới.

**Bất biến:** `00_input/raw/` **không bao giờ được sửa** sau khi nhận (quy tắc R1).
Mọi thứ phái sinh đều tái tạo được bằng cách chạy lại.

---

## 4. CÂU 2 — XỬ LÝ: DỮ LIỆU ĐI QUA NHỮNG GÌ

Bốn tầng, **không được trộn**. Đây là điều bảng Excel thủ công không làm được,
và là lý do bảng thủ công hay mâu thuẫn với chính nó.

| Tầng | Là gì | Ví dụ | Ai được sửa |
|---|---|---|---|
| 1 · FACT | số liệu thô, không diễn giải | `views = 1.204.331` | không ai |
| 2 · METRIC | chỉ số có công thức | `M2.4 = 1,305` | đổi công thức |
| 3 · SCORE | điểm 0–5 theo ngưỡng cố định | `12,05 / 20` | đổi ngưỡng |
| 4 · INSIGHT | diễn giải bằng lời | *"cầu vượt cung"* | người / AI |

**Tầng 4 không được sửa tầng 3.** Muốn đổi điểm → đổi *ngưỡng* ở tầng 3 →
chạy lại toàn bộ. Không có đường tắt viết đè kết luận.

Chuỗi xử lý thực tế: `crawl → chuẩn hóa → kiểm toán chất lượng → làm giàu →
lọc chọn lọc (4 rổ) → phân tích 10 bước → gom chỉ số → áp ngưỡng → chấm điểm → báo cáo`

Có **CỔNG QUYẾT ĐỊNH** sau bước 02: nếu cầu không tăng nhanh hơn cung
(`M2.4 < 0,5`) thì **dừng**, không phân tích tiếp. Phân tích một ngách đang
chìm là tối ưu hóa con tàu đang chìm.

---

## 5. CÂU 3 — DATA NÀO RA THÔNG TIN GÌ

Bảng này là phần R&D cần nhất: **mỗi loại dữ liệu trả lời được câu hỏi nào,
và tin được đến đâu.**

| Dữ liệu thô | Bước | Ra thông tin gì | Độ tin cậy |
|---|---|---|---|
| views, ngày đăng, số kênh | 02 | Ngách lên hay xuống? Cầu vs cung | **Cao** — mẫu lớn |
| kênh + video | 03 | Ai đang thắng? Còn cửa vào không? | **Cao** |
| video thắng vs thua | 04 | Đặc trưng nào **thật sự** phân biệt thắng/thua | **Cao** — có nhóm đối chứng |
| **comment** | 05 | **Painpoint · bối cảnh nghe · cách tìm thấy** | **Trung bình** — chỉ người chịu bình luận |
| comment (tuổi tự khai) | 05 | Nhân khẩu học | 🔻 **Thấp** — n=82 / 6.413 (1,3%) |
| tiêu đề, tag, mô tả | 06 | SEO · cách đóng gói · khoảng trống từ khóa | **Cao** |
| ảnh thumbnail | 04b/04g | Bố cục, màu, tỉ lệ người/chữ | **Trung bình** — nhánh tùy chọn |
| âm thanh (DSP) | 04h | Tempo, khóa, độ động, cấu trúc bài | **Trung bình** — mẫu còn nhỏ |
| RPM, rủi ro bản quyền | 07 | Ra tiền không? Rủi ro gì? | **Trung bình** — RPM là ước lượng ngoài |

> **Nguyên tắc đọc bảng này:** dòng nào ghi *Thấp* thì **không được dùng làm
> căn cứ quyết định một mình**. Ví dụ "tuổi trung vị 70" là của 82 người tự
> khai — không phải của khán giả ngách. Trích dẫn con số đó mà bỏ chữ số mẫu
> là sai lệch nghiêm trọng.

**Bốn mảng Phòng IT trong file flow R&D — đối chiếu:**

| File flow R&D | Hệ thống ta | Trạng thái |
|---|---|---|
| Thumbnail | STEP_04b → 04g | ✅ có, nhánh tùy chọn |
| SEO | STEP_06 | ✅ có |
| Comment | STEP_05 | ✅ có, mạnh nhất |
| Âm nhạc | STEP_04h | ✅ có, nhánh tùy chọn |

Ta còn có thứ file flow **không có**: STEP_04 (sàng lọc đối chứng — tìm đặc
trưng *không* phân biệt thắng/thua, tránh kết luận giả), CỔNG QUYẾT ĐỊNH,
và rubric chấm điểm 20 điểm để so sánh ngách này với ngách khác.

---

## 6. CÂU 4 — KẾT QUẢ CUỐI

| Sản phẩm | File | Dùng để làm gì |
|---|---|---|
| **Công thức thắng** | `09_playbook/CHANNEL_PLAYBOOK.json` | Đầu vào cho workflow sản xuất tự động |
| Hồ sơ 5 kênh hình mẫu | `09_playbook/CHANNEL_PROFILES.json` | Xem người thắng làm thế nào |
| Điểm ngách | `_state/scores.json` — hiện **12,05 / 20** | So sánh ngách này với ngách khác |
| Báo cáo PDF | `99_report/*.pdf` | Trình bày cho người quyết định |
| Brief tái tạo ảnh / nhạc | `04_outlier/` | Đầu vào cho khâu sản xuất nội dung |

**Hạn chế lớn nhất của kết quả hôm nay — cần nói rõ:**
`CHANNEL_PLAYBOOK.json` hiện là **MỘT công thức cho cả ngách**. Một mục tiêu độ
dài tiêu đề, một tỉ lệ người trên thumbnail, một nhịp đăng.

Theo ẩn dụ đã thống nhất: đó là **một toa thuốc phát cho cả phòng khám**.

Hệ thống *đã* nhận diện được 4 nhóm người nghe khác nhau
(`step05_audience.py` — nhóm cao tuổi · nhạc công · đang chịu đựng · mới tin đạo),
nhưng bốn nhóm đó **dừng lại ở dạng thống kê** và không đi tiếp vào công thức.
Bốn hồ sơ bệnh án được lập ra rồi cùng phát một toa.

Đây chính là chỗ luồng mới sửa — xem `07_CDKH_CONTRACT.md` §7 việc 4.

---

## 7. RANH GIỚI — VIỆC HỆ THỐNG KHÔNG LÀM

Ghi rõ để không ai kỳ vọng nhầm:

| Không làm | Vì sao |
|---|---|
| "Thời điểm mua hàng", "Khách hàng hiện tại" (thành phần 5–6 của CDKH) | Thuộc về HG Media với tư cách doanh nghiệp, không phải thứ nghiên cứu ngách nhạc trả lời được |
| Suy đoán tuổi / sắc tộc / tôn giáo từ tên người | Quy tắc R6 — chỉ ghi nhận khi tự khai công khai |
| Nhận diện cá nhân cụ thể | `author_hash` là SHA-256 có muối, **không đảo ngược** |
| Dự báo doanh thu chính xác | RPM là ước lượng từ nguồn ngoài, không phải số thật của kênh |
| Kết luận từ mẫu quá nhỏ | `n < 30` → báo **KHÔNG ĐỦ MẪU**, không phải kết luận |

**Ràng buộc thời hạn:** dữ liệu YouTube API phải **làm mới hoặc xóa trong 30 ngày**
(hạn hiện tại ≈ **2026-09-12**). Đây là điều khoản của YouTube, không thương lượng.

---

## 8. LIÊN KẾT

| Cần gì | Đọc file |
|---|---|
| Bản kỹ thuật đầy đủ + sơ đồ | `01_ARCHITECTURE.md` (có bản PDF) |
| Giao kèo CDKH với R&D | `07_CDKH_CONTRACT.md` |
| Ai đọc file gì, ghi file gì | `05_FILE_CONTRACTS.md` |
| Cách chấm điểm 20 điểm | `03_SCORING_RUBRIC.md` |
| Bài học đã rút | `../04_reference/lessons_learned.md` |
