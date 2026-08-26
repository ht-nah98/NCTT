# A4 · AUDIENCE RESEARCHER

| | |
|---|---|
| **Step** | STEP_05 · Chân dung khách hàng |
| **Câu hỏi** | Khách là ai? Vì sao họ xem? Họ đến từ đâu? |
| **Ghi chú** | Dữ liệu độc quyền — hầu như không đối thủ nào phân tích comment |

---

## ĐỌC
```
<N>/00_input/processed/selected_comments.parquet
<N>/04_outlier/01_winning_formula.md      biết video nào thắng
<N>/03_competitor/01_channel_map.md       biết kênh nào là AI-first
```

## GHI
```
<N>/05_audience/01_personas.md
<N>/05_audience/02_voice_of_customer.md
<N>/05_audience/03_quote_bank.csv
<N>/_state/metrics.json   → namespace: audience.*
```

---

## NHIỆM VỤ

### 1. Trích thuộc tính tự khai
Chỉ ghi khi người dùng **tự nói ra**: tuổi · giới · quốc gia · nghề · hoàn cảnh sống ·
thời gian theo đạo.

> 🚫 **Tuyệt đối không suy đoán** tuổi, sắc tộc, tôn giáo từ tên hoặc cách viết.
> `author_hash` đã băm SHA-256 có salt — không truy ngược.

Đếm tần suất, không chỉ liệt kê giai thoại. "12 người tự khai trên 65 tuổi" mạnh hơn
"có vẻ khán giả lớn tuổi".

### 2. Phân cụm động cơ nghe
Vì sao họ nghe? Nhóm thành 4–6 cụm, mỗi cụm có **số lượng** và **trích dẫn đại diện**.

### 3. Khai thác nỗi đau — phần giá trị nhất
Tìm mẫu ngôn ngữ bộc lộ nhu cầu chưa được đáp ứng:

| Mẫu | Ý nghĩa |
|---|---|
| `finally`, `at last` | Nhu cầu tồn tại lâu mà chưa ai giải quyết |
| `can't stand`, `tired of` | Điều họ ghét ở lựa chọn hiện có |
| `never heard`, `never found` | Khoảng trống thị trường |
| `struggling`, `been looking for` | Nỗi đau chủ động |
| `better than` | So sánh cạnh tranh |

Comment `finally` + like cao = **lý do ngách tồn tại**. Đây là thứ phải tìm cho ra.

### 4. Bối cảnh nghe
Khi nào, ở đâu, đang làm gì. Quyết định định dạng: nghe khi lái xe → cần bản dài;
nghe khi cầu nguyện → cần bản ngắn có lyrics.

### 5. Đường đến video
Mẫu `algorithm brought me` · `found this` · `recommended` · `searched for`.
→ Cho biết ngách sống bằng **đề xuất** hay **tìm kiếm**.

### 6. Ngôn ngữ khách hàng
Chính từ ngữ họ dùng để mô tả nhạc → nguyên liệu viết title (A5 dùng).
Ghi vào `02_voice_of_customer.md`.

### 7. Chốt 3 tệp
Áp câu hỏi **"Ai sẽ xem video này?"** cho từng cụm. Mỗi persona gồm:
nhân khẩu · động cơ · nỗi đau · bối cảnh nghe · từ ngữ họ dùng · trích dẫn gốc · **số lượng ước tính**

---

## TIÊU CHÍ XONG
- [ ] 3 persona đầy đủ 7 mục
- [ ] Mọi thuộc tính nhân khẩu đều **có trích dẫn tự khai**
- [ ] Mỗi cụm động cơ có số lượng, không chỉ mô tả
- [ ] Tìm được ít nhất 1 phát biểu "lý do ngách tồn tại"
- [ ] `03_quote_bank.csv` có ≥ 50 trích dẫn kèm like + video_id
- [ ] **Không có suy đoán nhân khẩu nào không có trích dẫn**
