# PROMPT VÀ VAI TRÒ CỦA AI

> Bạn hỏi *"bạn prompt ra làm sao"*. Câu trả lời khác điều bạn có thể đang hình
> dung, nên viết riêng một file.
>
> Phiên bản: v1.0 · Lập 2026-08-28

---

## 1. PIPELINE KHÔNG GỌI MÔ HÌNH NGÔN NGỮ NÀO

Kiểm chứng được:

```bash
grep -rn "import openai\|import anthropic\|api_key\|chat.completions" \
     pipeline/ --include="*.py" | grep -v _archive
# -> không kết quả nào
```

Pipeline chạy được **không cần internet, không cần khoá API**. 66 giây trên máy
cá nhân, không tốn một đồng token nào.

Chữ "prompt" có xuất hiện trong repo, nhưng ở **hai vai trò khác hẳn** — cả hai
đều là **đầu ra cho người dùng đem đi dùng nơi khác**, không phải thứ hệ thống
tự gọi:

### ① Prompt sinh nhạc — ghép bằng f-string từ số đo được

`pipeline/analyze/step04h_audio.py`:

```python
"prompt_en": (
    f"slow gospel blues, {int(bpm_r['min'])}-{int(bpm_r['max'])} BPM, "
    f"major key with frequent minor-chord colouring, "
    f"chord changes every {spc['min']:.0f}-{spc['max']:.0f} seconds, "
    f"low syncopation, warm analog production, ...")
```

Mọi con số trong prompt (`bpm_r`, `spc`) **đọc từ kết quả đo**, không ai gõ tay.
Đây là chuỗi ký tự do Python ghép, không phải văn bản do mô hình sinh.

Đáng chú ý là chính code tự khai giới hạn ngay bên cạnh:

```python
"prompt_ghi_chú": ("«có lời» là kết luận CÓ BẰNG CHỨNG (vocal_decision). "
                   "Nhưng LOẠI giọng và nhạc cụ cụ thể trong prompt là GỢI Ý "
                   "theo thể loại, KHÔNG đo được từ dữ liệu hiện có")
```

Phần đo được và phần suy đoán được tách bạch **ngay trong dữ liệu đầu ra**.

### ② Prompt sinh ảnh — trong THUMBNAIL_BRIEF.md

```
elderly Black gospel blues singer, 70 years old, thick white beard,
wearing worn fedora hat, singing into a chrome 1950s vintage microphone,
eyes closed, dim smoky blues club interior, warm amber rim lighting,
cinematic chiaroscuro lighting, photorealistic, 8k, 16:9
```

Prompt này **rút ra từ dữ liệu đo được**, không phải tưởng tượng:

| Câu trong prompt | Đo từ đâu |
|---|---|
| "elderly Black... 70 years old" | 91,5% ảnh top có mặt · nhánh A chiếm ~55% mẫu |
| "dim... interior" | vùng tối chiếm **61%** khung ảnh |
| "warm amber rim lighting" | sắc hổ phách 15,8% · **xanh lạnh chỉ 0,8%** |
| "16:9" | 97% ảnh dùng 1280×720 |
| "chiaroscuro" | tỷ số nét giữa/biên = 1,88× (nền mờ) |

---

## 2. VẬY AI ĐÃ LÀM GÌ

AI (Claude) tham gia ở **ba chỗ**, và cả ba đều nằm **ngoài lúc chạy**:

### ① Lúc thiết kế phương pháp — quan trọng nhất

Đây là chỗ AI đóng góp nhiều nhất, và nó là **suy nghĩ**, không phải prompt.

Ví dụ thật — cuộc đối thoại dẫn tới kiểm định 3 lớp:

```
Quan sát : "tiêu đề có tên sách Kinh Thánh" có lift 8,1× trong nhóm outlier
Câu hỏi  : có thể do nguyên nhân khác không?
Giả thuyết: hay là vì vài kênh mạnh tình cờ hay đặt tên Kinh Thánh?
Cách kiểm: đo lại trên TOÀN thị trường, rồi đo TRONG TỪNG kênh
Kết quả  : toàn thị trường 0,48× · trong kênh 6/13 → BÁC BỎ
Thành code: hàm verdict() đặt kiểm Simpson TRƯỚC kiểm XÁC NHẬN
```

Kết quả của bước này là **code**, không phải văn bản. Sau khi viết xong, code
chạy mãi mà không cần AI nữa.

### ② Lúc viết diễn giải

Biến bảng số thành câu tiếng Việt. Ràng buộc:

```
✅ Được  : chọn cách diễn đạt, sắp xếp thứ tự, nêu bối cảnh
❌ Không : bịa số, làm tròn có lợi, bỏ qua số ngược chiều,
           nâng độ tin cậy vượt mức phán quyết
```

Mọi số trong báo cáo **đọc từ file lúc dựng PDF**, không gõ tay (bài học T27).
Nếu AI viết sai số, `verify_reports.py` sẽ bắt được.

### ③ Lúc rút bài học

`lessons_learned.md` — 90 bài học. Mỗi lần mắc lỗi, ghi lại theo khuôn:
*đã xảy ra gì · nguyên nhân · quy tắc rút ra*.

---

## 3. NẾU BẠN MUỐN DÙNG AI ĐỂ PHÂN TÍCH — LÀM ĐÚNG CÁCH

Giả sử muốn vượt giới hạn regex (§2 của `04_GIOI_HAN`). Đây là cách giữ được
tái lập:

### ❌ Cách sai

```
Prompt: "Đây là 6.413 bình luận. Hãy phân tích và cho tôi biết
         chân dung khách hàng của ngách này."
```

Ba vấn đề: chạy lại ra kết quả khác · không truy vết được · không có p-value.

### ✅ Cách đúng — LLM gắn nhãn, thống kê kết luận

**Bước 1 — gắn nhãn từng comment, một việc rất hẹp:**

```
Đọc bình luận sau. Trả lời JSON, không giải thích.

{
  "tim_thay_lau_nay": true/false,   // người này nói đã tìm thứ này từ lâu?
  "khong_hop_nhac_cu": true/false,  // chê nhạc Christian/Blues khác?
  "boi_canh": "cau_nguyen|lai_xe|benh_vien|dem_khuya|khac|khong_ro",
  "tuoi_tu_khai": <số hoặc null>
}

Chỉ đánh dấu true khi người viết NÓI RÕ. Không suy đoán.

Bình luận: {text}
```

**Bước 2 — lưu nhãn xuống file:**

```python
labels.to_parquet("05_audience/_llm_labels.parquet")
```

**Bước 3 — thống kê chạy trên file nhãn, y hệt cách chạy trên regex:**

```python
d = pd.read_parquet("_llm_labels.parquet")
for signal in ["tim_thay_lau_nay", "khong_hop_nhac_cu"]:
    nhóm = d[d[signal]]
    p    = mannwhitneyu(nhóm.like_count, d[~d[signal]].like_count).pvalue
    lift = nhóm.like_count.median() / baseline
```

**Vì sao cách này giữ được tái lập:** nhãn sinh **một lần** rồi đóng băng
xuống file. Thống kê chạy lại bao nhiêu lần cũng ra cùng số. Muốn kiểm chất
lượng nhãn thì lấy 100 mẫu gắn tay rồi so.

### Bốn quy tắc bắt buộc nếu dùng LLM

| # | Quy tắc | Vì sao |
|---|---|---|
| 1 | LLM chỉ trả **JSON có schema cố định**, không trả văn xuôi | để thống kê đọc được |
| 2 | **Lưu nhãn xuống file**, không gọi lại mỗi lần phân tích | giữ tái lập |
| 3 | Ghi rõ **model + ngày + phiên bản prompt** vào `_meta` | truy vết được |
| 4 | Kiểm chất lượng trên **≥100 mẫu gắn tay** | biết nhãn sai bao nhiêu % |

---

## 4. VÍ DỤ PROMPT ĐẠT CHUẨN

Nếu bạn muốn tự viết, đây là khuôn đã kiểm nghiệm:

```
VAI TRÒ
Bạn gắn nhãn dữ liệu. Bạn KHÔNG phân tích, KHÔNG kết luận, KHÔNG suy đoán.

NHIỆM VỤ
Đọc một bình luận YouTube, trả về JSON đúng schema dưới đây.

SCHEMA
{
  "<tên_nhãn>": true | false,
  "boi_canh": "<một trong: A|B|C|khong_ro>",
  "tuoi_tu_khai": <số nguyên 13-99, hoặc null>
}

QUY TẮC
1. Chỉ đánh true khi người viết NÓI RÕ. Ám chỉ không tính.
2. Không suy đoán tuổi/giới tính/sắc tộc từ văn phong hay tên.
3. Không chắc → "khong_ro" hoặc null. Đoán bừa tệ hơn bỏ trống.
4. Chỉ trả JSON. Không lời dẫn, không giải thích.

BÌNH LUẬN
{text}
```

Ba điểm khiến prompt này đạt chuẩn:

- **Vai trò hẹp** — "gắn nhãn", không phải "phân tích"
- **Schema đóng** — mọi trường có kiểu và miền giá trị rõ
- **Quy tắc 2** thực thi **R6** (cấm suy đoán thuộc tính nhạy cảm) ở tầng prompt

---

## 5. RANH GIỚI ĐẠO ĐỨC — QUY TẮC R6

Áp dụng cho **cả người lẫn AI**, không có ngoại lệ:

| Cấm | Vì sao |
|---|---|
| Suy đoán tuổi/sắc tộc/tôn giáo từ tên hoặc ảnh đại diện | Sai và xâm phạm |
| Ghép tên thật với thuộc tính sức khoẻ/hoàn cảnh | Thành **hồ sơ suy đoán** về người thật |
| Công bố quote bank kèm `comment_id` | `comment_id` tra ngược ra tài khoản thật qua API **một lời gọi** |

Đây không phải quy tắc trên giấy. `.gitignore` của dự án chặn ở tầng file:

```
selected_comments.parquet      # có author_name thật
_comments_tagged.parquet       # tên thật + thuộc tính sức khoẻ
niches/*/05_audience/*quote_bank*.csv
```

Và khi deploy web, `pipeline/tools/anon_web.py` thay mọi `comment_id` thật bằng
mã tổng hợp `c0001…` trước khi đẩy lên.

---

## 6. TÓM TẮT — AI ĐƯỢC LÀM GÌ

| Việc | Được? | Điều kiện |
|---|---|---|
| Thiết kế phương pháp, viết code phân tích | ✅ | code phải tái lập được |
| Gắn nhãn ngữ nghĩa hàng loạt | ✅ | schema đóng · lưu file · kiểm ≥100 mẫu |
| Viết diễn giải từ bảng số | ✅ | số đọc từ file, không gõ tay |
| Rút bài học, viết tài liệu | ✅ | — |
| **Tính toán thống kê** | ❌ | dùng scipy, không dùng LLM |
| **Quyết định ngưỡng phán quyết** | ❌ | ngưỡng cố định trong code |
| **Suy đoán thuộc tính cá nhân** | ❌ | quy tắc R6 |
| **Sửa điểm số trực tiếp** | ❌ | chỉ `scoring_engine.py` được ghi |

> **Một câu tóm lại:** AI viết ra **công cụ đo**, chứ không phải AI đi **đo**.
> Công cụ đo phải chạy được mà không cần AI, và cho cùng kết quả mọi lần chạy.
