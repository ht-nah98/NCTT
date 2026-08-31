# LỘ TRÌNH DỮ LIỆU ÂM THANH — phản hồi cho đợt cào tiếp theo

> Viết sau khi phân tích **v2 (307 track)**. Mục đích: nói rõ **cào thêm gì**
> thì kết luận mạnh lên, và **cào thêm gì thì vô ích** — để không tốn công.
>
> Nguyên tắc: dữ liệu nhiều hơn ≠ kết luận chắc hơn. Cái quyết định là
> **cấu trúc** của mẫu, không phải số dòng.
>
> Phiên bản: v1.0 · Cập nhật 2026-08-19 · lộ trình dữ liệu âm thanh

---

## 1. v2 ĐÃ GIẢI QUYẾT ĐƯỢC GÌ

| Trước (v1) | Sau (v2) |
|---|---|
| 5 bản, không nối được view | **307 track / 29 video**, nối 100% với `video_master` |
| Không tách được nhạc cụ | **6 stem** (Demucs) — mở ra cả nhóm câu hỏi mới |
| Không có độ to chuẩn | **LUFS · PLR · LRA · true peak** |
| Không phân tích giọng | vibrato · HNR · jitter · formant · quãng giọng |
| Chỉ MÔ TẢ được | **KIỂM ĐỊNH được** (có view thật để so) |

Hai hạng mục từng nằm trong danh sách *bị chặn* — **tách stem** và **LUFS** —
nay đã xong. Gạch khỏi mục còn thiếu.

---

## 2. NÚT THẮT HIỆN TẠI: KHÔNG PHẢI SỐ TRACK

Đây là điểm quan trọng nhất của tài liệu này.

```
307 track  →  29 video  →  6 kênh
   ↑              ↑           ↑
nhiều       n THẬT ở đây   nút thắt THẬT ở đây
```

Nhiều track cùng một video **chia chung một con số lượt xem**, nên track không
phải mẫu độc lập. Và vì phải kiểm **trong từng kênh** (chống nghịch lý Simpson),
sức mạnh thống kê cuối cùng phụ thuộc vào **số video mỗi kênh** — hiện chỉ ~5.

> **Hệ quả thực tế:** cào thêm 1.000 track từ **cùng 29 video** sẽ **không**
> làm kết luận chắc hơn chút nào. Đó là công bỏ đi.

---

## 3. ƯU TIÊN CÀO — XẾP THEO GIÁ TRỊ THẬT

### 🔴 Ưu tiên 1 — KÊNH THẤT BẠI (giá trị cao nhất)

Cả 6 kênh hiện có đều **đang làm được**; kênh thấp nhất vẫn 11.967 view.
Ta mới so *khá* với *rất tốt*, **chưa hề so *thắng* với *thua***.

Không có nhóm này thì mọi kết luận đều mắc **thiên lệch sống sót**: ta đang
mô tả đặc điểm của người thắng mà không biết người thua có đúng đặc điểm đó không.

| Cần | Số lượng |
|---|---|
| Kênh cùng ngách, **< 5.000 view/video**, còn đăng đều | **6–10 kênh** |
| Video mỗi kênh | ≥ 5 |
| Track mỗi video | 3–5 là đủ (không cần nhiều) |

Đây là **nhóm đối chứng** đúng nghĩa của STEP_04. Có nó, câu hỏi đổi từ
*"nhóm dẫn đầu nghe thế nào"* thành *"cái gì phân biệt thắng với thua"*.

### 🟠 Ưu tiên 2 — THÊM VIDEO trong kênh đã có

Mỗi kênh hiện ~5 video → Spearman trong kênh rất yếu.

| Cần | Số lượng |
|---|---|
| Video mỗi kênh hiện có | **15–20** (thay vì 5) |
| Trải đều theo hiệu suất | lấy cả video **kém nhất** của kênh, không chỉ top |

Điểm cuối quan trọng: nếu chỉ cào video top của mỗi kênh thì trong kênh
**không còn phương sai** để đo. Phải có cả video flop của chính kênh đó.

### 🟡 Ưu tiên 3 — THÊM KÊNH tầm trung

6 kênh là mức tối thiểu để gộp Stouffer. **12–15 kênh** sẽ cho phép
kiểm định vững hơn nhiều và giảm rủi ro một kênh dị biệt kéo lệch kết quả.

### ⚪ KHÔNG cần thêm

| Việc | Vì sao |
|---|---|
| Thêm track từ video đã có | Không tăng n độc lập (xem §2) |
| Thêm cột đặc trưng mới | 45 cột hiện đã **thừa** so với n=29. Thêm cột chỉ làm nặng gánh đa kiểm định |
| Cào lại `prompt Suno` | Người dùng xác nhận cột này **sai dữ liệu thô** — đã bỏ khỏi phân tích |

> **Quy tắc ngón tay cái:** khi số đặc trưng (45) lớn hơn số mẫu (29),
> mọi phát hiện đều mong manh. Ưu tiên **thêm hàng**, đừng thêm cột.

---

## 4. TRƯỜNG DỮ LIỆU NÊN BỔ SUNG (không phải đặc trưng nhạc)

Không phải cào thêm nhạc — cào thêm **ngữ cảnh** để kiểm soát biến gây nhiễu:

| Trường | Vì sao cần |
|---|---|
| `published_at` chính xác của từng track | Video dài là tuyển tập; track có thể phát hành khác thời điểm |
| Vị trí track trong video (thứ tự, mốc thời gian) | Track mở đầu và track thứ 20 **không** được nghe như nhau — đây là biến gây nhiễu chưa kiểm soát |
| Có phải bản đăng lại / phối lại không | Bản hit đăng lại sẽ làm nhiễu quan hệ nhạc↔view |
| Lượt xem theo track (nếu có chapter analytics) | Sẽ **gỡ hẳn** nút thắt ở §2 — biến 29 mẫu thành 307 mẫu thật |

Dòng cuối là **thay đổi lớn nhất có thể có**. Nếu YouTube Studio cho dữ liệu
giữ chân theo chapter, toàn bộ giới hạn của báo cáo hiện tại biến mất.

---

## 5. NGƯỠNG "ĐỦ DỮ LIỆU" — chốt trước để biết khi nào dừng

| Mức | Điều kiện | Kết luận đạt được |
|---|---|---|
| **Hiện tại (v2)** | 29 video / 6 kênh, không có nhóm thua | 1 XÁC NHẬN, phần lớn KHÔNG ĐỦ MẪU |
| **v3 mục tiêu** | 100+ video / 12+ kênh, **có nhóm thua** | Kiểm định vững, tách được theo phân khúc |
| **v4 lý tưởng** | + view theo track | Đơn vị phân tích thành track → n thật 1.000+ |

---

## 6. LIÊN QUAN

| Cần gì | Đọc |
|---|---|
| Kết quả kiểm định v2 | `niches/*/99_report/STEP04h2_Kiem-dinh-am-thanh.pdf` |
| Dữ liệu gốc kiểm định | `niches/*/04_outlier/audio/AUDIO_TEST.json` |
| Bẫy thống kê đã gặp | `../04_reference/lessons_learned.md` T46–T50 |
| Luồng nghiệp vụ tổng | `08_FLOW_NGHIEP_VU.md` |
