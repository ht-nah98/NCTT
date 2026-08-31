# ĐỌC TRƯỚC TIÊN — Sự thật về "mô hình AI phân tích"

> Thư mục này giải thích **cách nghĩ**, không chỉ cách chạy. Mục tiêu: bạn đọc
> xong có thể tự nâng cấp, tự xây lại, hoặc bác bỏ cách làm hiện tại.
>
> Phiên bản: v1.0 · Lập 2026-08-28

---

## 1. ĐIỀU BẤT NGỜ NHẤT: HỆ THỐNG NÀY KHÔNG DÙNG AI ĐỂ PHÂN TÍCH

Bạn hỏi *"AI đọc data phân tích data như thế nào để ra kết luận"*. Câu trả lời
thẳng: **nó không làm vậy**.

Kiểm chứng được ngay:

```bash
grep -rn "import openai\|import anthropic\|api_key\|chat.completions" \
     pipeline/ --include="*.py" | grep -v _archive
# -> không kết quả nào
```

Toàn bộ **15.542 dòng code** trong `pipeline/` không có một lời gọi mô hình
ngôn ngữ nào. Mọi con số trong mọi báo cáo đến từ:

| Công cụ | Việc | Tỷ trọng |
|---|---|---|
| **Regex** (biểu thức chính quy) | tìm mẫu chữ trong tiêu đề và bình luận | ~40% |
| **pandas** | đếm, nhóm, trung vị, ghép bảng | ~40% |
| **scipy.stats** | kiểm định Mann–Whitney, Spearman | ~15% |
| **matplotlib** | vẽ biểu đồ | ~5% |

Mô hình học máy chỉ xuất hiện ở **khâu trích đặc trưng** — nơi cần đọc thứ mà
code thường không đọc được:

| Mô hình | Đọc gì | Ra gì | Nằm ở |
|---|---|---|---|
| `faster-whisper` | file âm thanh | lời hát dạng chữ | `pipeline/lyrics/L3` |
| `YOLO11-seg` | ảnh thumbnail | vị trí và diện tích người | `step04g` |
| `EasyOCR` | ảnh thumbnail | chữ trên ảnh | `step04g` |
| `librosa` + DSP | file âm thanh | BPM, điệu thức, độ ồn | `step04h` |

Chúng **không kết luận gì cả**. Chúng biến ảnh và âm thanh thành **con số**,
rồi thống kê mới làm việc kết luận.

### Vậy "AI" nằm ở đâu?

Ở **hai chỗ, và chỉ hai chỗ**:

1. **Lúc thiết kế** — một người (hoặc Claude) quyết định: đo cái gì, so với
   cái gì, ngưỡng nào là "đạt". Quyết định này nằm trong code, không đổi khi chạy.
2. **Lúc viết diễn giải** — biến bảng số thành câu tiếng Việt trong báo cáo.

Nghĩa là: **AI viết ra công cụ đo, chứ không phải AI đi đo.** Đây là lựa chọn
có chủ đích, không phải thiếu sót — lý do ở §3.

---

## 2. TẠI SAO ĐIỀU NÀY QUAN TRỌNG VỚI BẠN

Nếu hệ thống này dùng LLM để "đọc 6.413 bình luận rồi rút ra chân dung khách
hàng", bạn sẽ gặp ba vấn đề không sửa được:

| Vấn đề | Hệ quả |
|---|---|
| **Không tái lập** | Chạy lại cho kết quả khác. Không biết số nào đúng. |
| **Không truy vết** | Hỏi "vì sao kết luận thế?" → không có đường lần ngược. |
| **Không kiểm định được** | LLM nói "khán giả thích chủ đề chữa lành" — không có p-value, không biết có thật không. |

Cách hiện tại đổi lại được ba thứ:

- **Tái lập tuyệt đối**: cùng dữ liệu → cùng con số, mọi lúc.
- **Truy vết đến từng dòng**: mọi số đều có `source` trỏ về file gốc.
- **Bác bỏ được**: mỗi phát hiện có p-value và kiểm định trong từng kênh.

Cái giá phải trả: **regex không hiểu ngữ nghĩa**. Nó bắt được `"finally"`
nhưng không bắt được `"at long last, after decades of searching"`. Giới hạn này
được ghi rõ ở `04_GIOI_HAN_VA_CACH_KHAC_PHUC.md`.

---

## 3. NGUYÊN TẮC XUYÊN SUỐT: BỐN TẦNG KHÔNG ĐƯỢC TRỘN

Đây là cột sống của toàn hệ thống. Hiểu cái này là hiểu 80%.

```
TẦNG 1 · FACT      số thô, không diễn giải          views = 1.204.331
    ↓              (không ai được sửa)
TẦNG 2 · METRIC    chỉ số có công thức              M2.4 = 1,305
    ↓              (đổi được, bằng cách đổi công thức)
TẦNG 3 · SCORE     điểm 0–5 theo ngưỡng cố định     12,05 / 20
    ↓              (đổi được, bằng cách đổi ngưỡng)
TẦNG 4 · INSIGHT   diễn giải bằng lời               "cầu vượt cung"
                   (người hoặc AI viết)

           ❌ TẦNG 4 KHÔNG ĐƯỢC SỬA TẦNG 3
```

Muốn đổi điểm → đổi **ngưỡng ở tầng 3** → chạy lại toàn bộ. Không có đường tắt
viết đè kết luận.

**Vì sao khắt khe vậy:** bảng Excel thủ công hay mâu thuẫn với chính nó đúng vì
thiếu ranh giới này — ai đó thấy điểm thấp, sửa tay điểm lên, và không ai biết
số nào là số thật.

Thực thi bằng code: **chỉ `scoring_engine.py` được ghi `scores.json`**. Mọi
script phân tích khác chỉ được ghi `metrics.json`.

---

## 4. BẢN ĐỒ THƯ MỤC NÀY

Đọc theo thứ tự nếu bạn muốn hiểu toàn bộ:

| File | Trả lời câu hỏi |
|---|---|
| `00_DOC_TRUOC_TIEN.md` | ← bạn đang đọc. AI nằm ở đâu, bốn tầng là gì |
| `01_DUONG_DI_CUA_DU_LIEU.md` | Từ file thô đến báo cáo, đi qua những gì |
| `02_CACH_PHAN_TICH_TUNG_BUOC.md` | Mỗi bước: đọc gì, làm gì, ra gì — kèm code thật |
| `03_CACH_RA_KET_LUAN.md` | Từ bảng số thành câu kết luận — quy tắc chống tự lừa |
| `04_GIOI_HAN_VA_CACH_KHAC_PHUC.md` | Chỗ nào yếu, sửa thế nào |
| `05_TU_XAY_LAI.md` | Muốn tự xây / nâng cấp thì bắt đầu từ đâu |
| `06_PROMPT_VA_VAI_TRO_AI.md` | Prompt thật đã dùng, và AI được phép làm gì |

---

## 5. BA CÂU HỎI PHẢI TRẢ LỜI TRƯỚC MỌI KẾT LUẬN

Ghi ở đây vì nó áp dụng cho **mọi** phần còn lại:

1. **So với cái gì?** — Không có mốc so sánh thì con số vô nghĩa.
   *"Video này 50.000 view"* không nói lên gì. *"Gấp 5 lần trung vị của chính
   kênh đó"* mới nói lên điều gì đó.

2. **Có thể do nguyên nhân khác không?** — Phải liệt kê ít nhất một cách giải
   thích ngược. Đây là chỗ nghịch lý Simpson bị bắt.

3. **Độ tin cậy bao nhiêu?** — cao / vừa / thấp, kèm lý do. Cỡ mẫu `n < 30` thì
   ghi **KHÔNG ĐỦ MẪU**, không được kết luận.

---

## 6. MỘT VÍ DỤ CHẠY XUYÊN SUỐT

Để bạn thấy cả bốn tầng trong một câu chuyện. Câu hỏi:
*"Chủ đề Kinh Thánh có giúp video thắng không?"*

| Tầng | Điều xảy ra |
|---|---|
| **FACT** | 652 video có chữ `psalm/scripture/bible` trong tiêu đề |
| **METRIC** | VPD nhóm đó = 6,17 · nhóm còn lại = 10,07 → lift **0,61×** |
| **KIỂM ĐỊNH** | p = 0,00028 (có ý nghĩa) — *nhưng* kiểm trong từng kênh: **7/13 kênh tệ đi**, trung vị 1,28 |
| **SCORE** | không vào điểm — đây là phát hiện nội dung, không phải trục chấm |
| **INSIGHT** | *"TRÁNH — hướng đông kênh nhất và kém nhất"* |

Điểm mấu chốt: nếu dừng ở p-value, kết luận sẽ là *"có ý nghĩa thống kê"*.
Kiểm thêm một lớp mới thấy hiệu ứng **không nhất quán trong từng kênh** — dấu
hiệu kinh điển của nghịch lý Simpson.

Đây chính là thứ mà một LLM đọc 652 tiêu đề rồi "cảm thấy" sẽ không bao giờ
phát hiện được.

---

## 7. LIÊN KẾT NGOÀI THƯ MỤC NÀY

| Cần gì | Đọc |
|---|---|
| Kiến trúc kỹ thuật + sơ đồ | `../00_system/01_ARCHITECTURE.md` |
| Schema dữ liệu | `../00_system/02_DATA_MODEL.md` |
| Cách chấm điểm | `../00_system/03_SCORING_RUBRIC.md` |
| Logic lọc 4 rổ | `../00_system/04_SELECTION_LOGIC.md` |
| Sáu nhóm nguồn Y·P·S·V·K·N | `../00_system/10_SOURCE_CLASSES.md` |
| Bốn tài liệu đầu ra | `../00_system/11_OUTPUT_CONTRACT.md` |
| **90 bài học đã rút** | `../04_reference/lessons_learned.md` |
