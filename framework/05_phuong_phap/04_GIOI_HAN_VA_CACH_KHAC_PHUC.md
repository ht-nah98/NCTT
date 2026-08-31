# GIỚI HẠN VÀ CÁCH KHẮC PHỤC

> Chỗ nào hệ thống yếu, yếu tới mức nào, và sửa thế nào. Viết thẳng để bạn
> biết mình đang cầm công cụ gì trong tay.
>
> Phiên bản: v1.0 · Lập 2026-08-28

---

## 1. GIỚI HẠN LỚN NHẤT: CHỈ CÓ 1/6 NHÓM NGUỒN

| Mã | Nhóm nguồn | Trạng thái |
|---|---|---|
| **Y** | YouTube | ✅ đầy đủ |
| **P** | Spotify, podcast, TikTok | ❌ chưa có |
| **S** | Google Trends, autocomplete | ❌ chưa có |
| **V** | Reddit, forum, review app | ❌ chưa có |
| **K** | Báo cáo ngành | ⚠️ dùng rời rạc, không có quy trình |
| **N** | Analytics kênh nhà | ❌ chưa có |

**Hệ quả đo được:**

| Câu hỏi | Trả lời được không |
|---|---|
| Cái gì đang tồn tại, ai thắng, thắng bằng gì? | ✅ **đầy đủ** |
| Cầu nào có mà chưa ai phục vụ? | ⚠️ **suy gián tiếp** qua vocab gap |
| Cầu dịch chuyển về đâu 6–12 tháng? | ❌ **gần như mù** |

**Cách khắc phục, xếp theo giá trị trên công sức:**

| Ưu tiên | Mã | Việc | Vì sao trước |
|---|---|---|---|
| 1 | **S** | Google Trends + autocomplete cho 20–30 cụm | Rẻ nhất, không cần khoá API, trả lời trực tiếp hai câu YouTube mù |
| 2 | **N** | Nối Analytics khi kênh chạy | Nguồn **duy nhất** cho retention/CTR/RPM thật |
| 3 | **V** | Crawl Reddit theo subreddit | Bổ khuyết đúng chỗ comment YouTube thiên lệch |
| 4 | **P** | Playlist Spotify + podcast | Cầu đã được phục vụ ở đâu ngoài YouTube |
| 5 | **K** | Chuẩn hoá quy trình trích báo cáo | Đang dùng rời rạc, cần lưu vết |

---

## 2. REGEX KHÔNG HIỂU NGỮ NGHĨA

Đây là giới hạn của phương pháp, không phải lỗi triển khai.

### Bắt được

```
"finally found this"          ✓ khớp \bfinally\b
"I'm 76 years old"            ✓ khớp \b(\d{2})\s*years?\s*old\b
```

### Không bắt được

```
"at long last, after decades of searching"   ✗ không có chữ "finally"
"been on this earth three quarters century"  ✗ không có số tuổi
"my husband went home to be with the Lord"   ✗ không khớp mẫu tang chế
```

### Hệ quả

Mọi con số đếm được là **cận dưới**, không phải con số thật. `finally` n=58
nghĩa là *"ít nhất 58 người dùng đúng cụm từ đó"*, không phải *"58 người có
trải nghiệm đó"*.

**Điều này KHÔNG làm hỏng kết luận so sánh**, vì cùng một regex áp cho cả hai
nhóm. Nếu regex bỏ sót 30% ở nhóm A thì cũng bỏ sót ~30% ở nhóm B — tỷ lệ
lift vẫn đúng.

### Cách khắc phục

| Cách | Ưu | Nhược |
|---|---|---|
| **Mở rộng mẫu regex** | rẻ, giữ tái lập | không bao giờ đủ |
| **Embedding + phân cụm** | bắt được diễn đạt khác nhau | cần nhãn để kiểm |
| **LLM gắn nhãn hàng loạt** | hiểu ngữ nghĩa thật | **mất tái lập** — xem §6 |

Khuyến nghị: nếu dùng LLM, dùng ở **khâu gắn nhãn** rồi lưu nhãn xuống file,
và thống kê vẫn chạy trên nhãn đã lưu. Như vậy giữ được tái lập.

---

## 3. COMMENT LÀ MẪU THIÊN LỆCH

Comment chỉ chứa **người chịu bình luận**. Đây không phải mẫu đại diện.

| Số liệu | Giá trị | Đọc đúng là |
|---|---|---|
| Tuổi trung vị | 70 | của **82 người tự khai**, không phải của ngách |
| Tự khai tuổi | 82/6.413 | **1,3%** — không đại diện |

> Trích *"tuổi trung vị 70"* mà bỏ *"n=82"* là **sai lệch nghiêm trọng**.
> Tài liệu T1.1 luôn in cỡ mẫu ngay cạnh con số vì lý do này.

**Cách khắc phục:** nguồn `N` (Analytics kênh nhà) cho nhân khẩu học thật của
**toàn bộ** người xem, không chỉ người bình luận.

---

## 4. MỘT SNAPSHOT, KHÔNG PHẢI CHUỖI THỜI GIAN

`video_stats` chỉ có **1 lần chụp** (2026-08-13). Hệ quả:

- Không đo được **tốc độ tăng trưởng thật** của một video
- M2.4 phải suy từ `published_at`, không phải từ hai lần đo
- Chỉ số M3.3 (thời gian đạt ngưỡng) báo **KHÔNG ĐO ĐƯỢC**

Độ tin cậy trục động lượng bị hạ xuống mức **"vừa"** vì lý do này.

**Cách khắc phục:** chụp snapshot định kỳ 30–90 ngày. Hai snapshot là đủ để
mở khoá M3.3 và nâng độ tin cậy M2.

---

## 5. KHÔNG CÓ DỮ LIỆU HÀNH VI

YouTube API **không trả về** cho kênh người khác:

| Thiếu | Hệ quả |
|---|---|
| Retention (giữ chân) | không biết người xem bỏ ở giây thứ mấy |
| CTR (tỷ lệ click) | không biết thumbnail nào thật sự được click |
| Traffic source | không biết bao nhiêu % từ đề xuất |
| Doanh thu thật | RPM chỉ là ước lượng, sai số 4 lần |

Đây là lý do 5 cơ chế trong T1.2 đều ở dạng **giả thuyết có dự đoán**, chưa
phải kết luận. Chỉ nguồn `N` mới kiểm chứng được.

---

## 6. VÌ SAO KHÔNG DÙNG LLM ĐỂ PHÂN TÍCH — VÀ KHI NÀO NÊN DÙNG

### Ba thứ mất đi nếu để LLM phân tích

| Mất | Vì sao nghiêm trọng |
|---|---|
| **Tái lập** | chạy lại ra số khác, không biết số nào đúng |
| **Truy vết** | hỏi "vì sao kết luận thế" → không lần ngược được |
| **Kiểm định** | không có p-value, không biết có thật không |

### Khi nào LLM đáng dùng

| Việc | Nên dùng LLM? | Cách giữ tái lập |
|---|---|---|
| Đếm, trung vị, kiểm định | ❌ **không bao giờ** | — |
| Gắn nhãn ngữ nghĩa cho 6.413 comment | ✅ có | lưu nhãn xuống file, thống kê chạy trên file |
| Tóm tắt 300 comment tinh hoa | ✅ có | ghi rõ mẫu nào được đưa vào |
| Viết diễn giải từ bảng số | ✅ có | số phải đọc từ file, không để LLM tự nhớ |
| Quyết định ngưỡng phán quyết | ❌ không | ngưỡng phải cố định trong code |

**Nguyên tắc:** LLM được phép **hiểu ngôn ngữ**, không được phép **quyết định
con số**.

---

## 7. CÁC GIỚI HẠN ĐÃ BIẾT KHÁC

| Giới hạn | Mức độ | Ghi ở |
|---|---|---|
| Phân loại giọng nam/nữ tin cậy thấp (chênh 0,06/1,0) | không dùng được | T1.3 |
| Chưa đo mùa vụ (Giáng sinh, Phục sinh) | thiếu | T1.3 §Lớp 2 |
| Chưa đo ranh giới với dòng nhạc lân cận | thiếu | T1.1 §1 |
| Nhóm hoàn cảnh cá nhân n quá nhỏ (widow=5, disabled=1) | không kết luận được | T1.1 §3 |
| 0/26 đặc trưng thumbnail phân biệt thắng/thua | là kết quả, không phải lỗi | T1.2 §4 |

---

## 8. ĐIỀU HỆ THỐNG NÀY KHÔNG BAO GIỜ LÀM

Ghi rõ để không ai kỳ vọng nhầm:

| Không làm | Vì sao |
|---|---|
| Tự crawl dữ liệu | Crawl là khâu riêng |
| Dự đoán view tương lai | Chỉ đo trạng thái hiện tại |
| Suy đoán tuổi/sắc tộc/tôn giáo từ tên người | **Quy tắc R6** — chỉ ghi khi tự khai |
| Nhận diện cá nhân cụ thể | `author_hash` là SHA-256 có muối |
| Thay quyết định kinh doanh | Đưa bằng chứng có cấu trúc, người quyết |
| Kết luận từ mẫu n < 30 | Báo KHÔNG ĐỦ MẪU |
