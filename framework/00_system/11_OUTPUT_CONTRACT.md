# HỢP ĐỒNG ĐẦU RA — BỐN TÀI LIỆU T1.1–T1.4

> Chuẩn đầu ra sau 49 vòng cải tiến. Thay thế cách tổ chức báo cáo cũ
> (7 báo cáo theo STEP + 6 PDF chồng chéo).
>
> Phiên bản: v1.0 · Lập 2026-08-28

---

## 1. VÌ SAO ĐỔI

Cách cũ tổ chức báo cáo **theo bước chạy** (STEP_02, STEP_03…). Hệ quả:

- Một người đọc phải mở 6 file mới trả lời được một câu hỏi
- Cùng một bộ số nền lặp lại ở 6–7 file, lệch nhau khi cập nhật
- Không phân biệt được **sự thật quan sát** với **suy luận** — hai thứ trộn trong cùng một trang

Cách mới tổ chức **theo người đọc và theo loại phát biểu**:

| | Loại phát biểu | Ai đọc |
|---|---|---|
| **T1.1** | Chỉ sự thật quan sát được | Người quyết định đầu tư ngách |
| **T1.2** | Giả thuyết có cấu trúc về cơ chế | Người làm nội dung |
| **T1.3** | Thông số kỹ thuật để sản xuất | Nhạc sĩ / vận hành Suno / designer |
| **T1.4** | Hồ sơ sâu từng đối thủ | Người học chiến thuật cụ thể |

Ranh giới giữa bốn tài liệu là **ranh giới nhận thức luận**, không phải ranh
giới tiện lợi. T1.1 nói *cái gì đang xảy ra*; T1.2 nói *vì sao*; T1.3 nói
*làm thế nào*; T1.4 nói *ai đã làm được*.

---

## 2. T1.1 — HỒ SƠ NGÁCH CHI TIẾT (fact base)

**Trả lời:** "Ngách này thực tế trông như thế nào trên YouTube?"

**Định nghĩa:** bản mô tả những gì quan sát được về một ngách tại một thời
điểm, mỗi phát biểu có nguồn và mức tin cậy.

### Chứa

| Mục | Nội dung | Nguồn dữ liệu |
|---|---|---|
| 1 · Định nghĩa phạm vi | Cái gì tính là ngách này, cái gì không, tiêu chí vào/ra, ngách con, ranh giới với dòng lân cận | `NICHE_BRIEF.md` |
| 2 · Trạng thái cung | Số kênh, view, phân tầng, thị phần, tuổi kênh, tần suất đăng, kênh breakout | `02_market/`, `03_competitor/` |
| 3 · Dấu vết cầu (thô) | Từ khoá tag/tiêu đề, vocab gap, phân bố comment, độ dài video, tỉ lệ có lời/không lời. **Số liệu, chưa diễn giải** | `06_keyword/`, `05_audience/` |
| 4 · Kinh tế ngách | Dung lượng × RPM, trần doanh thu, độ nhạy | `07_monetization/` |
| 5 · Rủi ro & rào cản | Bản quyền, chính sách nền tảng, bão hoà | `07_monetization/`, `02_analysis/` |

### KHÔNG chứa

- "Vì sao khán giả click" → T1.2
- Đề xuất concept → T2.1
- Thông số sản xuất chi tiết → T1.3
- Hồ sơ từng đối thủ → T1.4

### Quy ước phiên bản

Bắt buộc ghi ở đầu tài liệu: **"đo ngày X, n=Y kênh"**. Nhịp cập nhật theo
snapshot dữ liệu (30–90 ngày).

### Đóng góp bước sau

Ra quyết định Go/No-Go, và cung cấp nền dữ liệu cho T1.2.

---

## 3. T1.2 — MÔ HÌNH KHÁN GIẢ & CƠ CHẾ

**Trả lời:** "Người xem là ai? Họ đang thuê nội dung này làm việc gì cho họ,
và cơ chế nào khiến họ chọn video A thay vì B?"

**Định nghĩa:** giả thuyết **có cấu trúc** về vì sao khán giả tìm, click, ở
lại, quay lại — và điều đó ràng buộc ta phải làm gì.

### Chứa

- Job-to-be-done + 4 lực (kéo / đẩy / quán tính / lo ngại)
- Bối cảnh nghe (nghe nền hay nghe chủ động)
- Trigger & hành trình khám phá (Search vs Suggested vs Browse), và họ có tìm ở nguồn nào ngoài YouTube không
- Cơ chế click — giải mã thumbnail/title, pattern và outlier
- Cơ chế giữ chân — mở đầu, độ dài, chuyển bài, cấu trúc playlist
- Bản đồ nhân–quả — biến nào tác động biến nào, chiều và độ mạnh
- Ma trận khoảng trống — cầu có, cung chưa đáp ứng

### Ràng buộc đặc thù

> **Mỗi cơ chế bắt buộc kèm một dự đoán kiểm chứng được:**
> *"nếu đúng, thì khi ta làm X sẽ thấy Y"*

Cơ chế không có dự đoán kiểm chứng được thì **không phải cơ chế** — nó là
lời kể. Đây là điều tách T1.2 khỏi một bản "chân dung khách hàng" thông thường.

### KHÔNG chứa

- Số liệu gốc → dẫn chiếu T1.1
- Đề xuất concept kênh cụ thể → T2.1

### Nhịp

Đổi khi có insight mới, hoặc khi dữ liệu tầng C (kênh thật) về.

### Đóng góp bước sau

Đây là **nguồn của mọi giả thuyết về định vị kênh** được đem đi test.

---

## 4. T1.3 — ĐẶC TẢ DÒNG NHẠC (Music DNA Spec)

**Trả lời:** "Bản nhạc/video phải nghe và trông như thế nào thì được coi là
đúng ngách?"

**Định nghĩa:** bản thông số kỹ thuật để sản xuất đúng chất dòng nhạc này —
dùng như tài liệu tra cứu hằng ngày.

### Ba lớp

| Lớp | Nội dung |
|---|---|
| **1 · Âm thanh** | BPM, tone, nhạc cụ bắt buộc/cấm, cấu trúc, thời lượng, chất giọng, mix, prompt mẫu |
| **2 · Văn hoá & ngôn ngữ** | Vốn từ lời hát, chủ đề được/không được chạm, quy ước tôn giáo, vốn từ hình ảnh, nhịp sinh hoạt (lễ, mùa) |
| **3 · Ràng buộc pháp lý & nguồn gốc** | Public domain / cover / sáng tác mới (danh sách bài cụ thể nếu là PD hoặc cover), yêu cầu Content ID, nhãn nội dung tổng hợp |

Kèm **checklist QC** cho dòng nhạc.

### KHÔNG chứa

- Định nghĩa phạm vi thị trường → T1.1 §1
- Phân tích đối thủ → T1.4

### Nhịp

Đổi khi QC phát hiện lệch, hoặc khi test cho tín hiệu mới.

### Đóng góp bước sau

Là đầu vào trực tiếp của production brief, và là chuẩn để QC nghiệm thu asset.

---

## 5. T1.4 — THẺ ĐỐI THỦ (Competitor Card)

**Trả lời:** "Kênh này thắng bằng cái gì, và ta học/né được gì?"

**Định nghĩa:** hồ sơ sâu một kênh đối thủ đáng học, tối đa 1–2 trang mỗi thẻ.

### Chứa

Nhận dạng kênh · lịch sử tăng trưởng · format & lịch đăng · hệ thống
thumbnail/title · cấu trúc playlist · mô hình kiếm tiền quan sát được ·
điểm mạnh **không copy được** vs điểm yếu **khai thác được** · bài học rút ra.

### KHÔNG chứa

Làm cho tất cả các kênh. **Chỉ 5–10 kênh:** nhóm dẫn đầu + kênh breakout +
outlier phá luật.

### Nhịp

Làm 1 lần, soát lại mỗi quý.

### Đóng góp bước sau

Cấp bằng chứng cụ thể cho bước SXND, và mẫu tham chiếu cho production brief.

---

## 6. RANH GIỚI GIỮA BỐN TÀI LIỆU — BẢNG TRA NHANH

Khi phân vân một phát biểu thuộc tài liệu nào:

| Phát biểu dạng… | Thuộc | Ví dụ |
|---|---|---|
| "Có N kênh, trung vị X view" | **T1.1** | 53 kênh, trung vị 1.687 view |
| "Cầu tăng nhanh hơn cung 1,30×" | **T1.1** | chỉ số đo được |
| "Khán giả nghe lúc cầu nguyện vì cần bạn đồng hành" | **T1.2** | suy luận về động cơ |
| "Nếu đổi tiêu đề sang ngôn ngữ khán giả, CTR sẽ tăng" | **T1.2** | dự đoán kiểm chứng được |
| "BPM 88, LUFS −13,8, swing 1,32" | **T1.3** | thông số sản xuất |
| "Tránh tông xanh lạnh" | **T1.3** | quy tắc sản xuất |
| "Kênh X thắng nhờ đăng 27 video/tháng" | **T1.4** | hồ sơ một đối thủ |

**Nguyên tắc phân xử:** nếu phát biểu có thể **sai khi dữ liệu mới về** →
T1.1. Nếu nó có thể **bị bác bỏ bằng một thí nghiệm** → T1.2. Nếu nó là
**tham số để làm ra thứ gì đó** → T1.3. Nếu nó nói về **một kênh cụ thể** → T1.4.

---

## 7. QUY TẮC CHUNG CHO CẢ BỐN

| # | Quy tắc |
|---|---|
| **O1** | Mọi phát biểu mang mã nguồn theo `10_SOURCE_CLASSES.md` |
| **O2** | Mọi phát biểu định lượng kèm cỡ mẫu `n=` |
| **O3** | `n < 30` → ghi **KHÔNG ĐỦ MẪU**, không được kết luận |
| **O4** | Kết luận trái với kiểm định thống kê → **cấm**, kể cả khi nguồn ngoài ủng hộ |
| **O5** | Mục chưa có dữ liệu → ghi `[—] chưa có nguồn`, không bỏ trống |
| **O6** | Sinh tự động từ pipeline, **không** viết tay số liệu |

Quy tắc **O6** là lý do bốn tài liệu này được sinh bằng script: viết tay thì
lần cập nhật thứ hai sẽ lệch so với dữ liệu, và không ai biết lệch chỗ nào.

---

## 8. SINH RA THẾ NÀO

| Tài liệu | Script | Đầu vào chính |
|---|---|---|
| T1.1 | `pipeline/report/build_T11_niche_facts.py` | `metrics.json`, `02_market/`, `03_competitor/`, `06_keyword/` |
| T1.2 | `pipeline/report/build_T12_audience_model.py` | `05_audience/`, `06_keyword/`, `04_outlier/` |
| T1.3 | `pipeline/report/build_T13_music_spec.py` | `04_outlier/audio/`, `04_outlier/lyrics/`, `02_analysis/` |
| T1.4 | `pipeline/report/build_T14_competitor_cards.py` | `03_competitor/`, `09_playbook/CHANNEL_PROFILES.json` |

Cả bốn chạy trong `run_all.sh`, sau bước chấm điểm.

---

## 9. LIÊN KẾT

| Cần gì | Đọc file |
|---|---|
| Sáu nhóm nguồn Y·P·S·V·K·N | `10_SOURCE_CLASSES.md` |
| Chuẩn trình bày báo cáo | `06_REPORT_STANDARDS.md` |
| Ai đọc file gì, ghi file gì | `05_FILE_CONTRACTS.md` |
| Bài học đã rút | `../04_reference/lessons_learned.md` |
