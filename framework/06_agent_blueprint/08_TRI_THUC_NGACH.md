# TRI THỨC NGÁCH — thứ phải nhúng vào prompt

> Đây là **tri thức trả giá mới có**. Agent không tự biết. Không nhúng vào,
> nó sẽ mắc lại từng bẫy một.
>
> Copy nguyên khối này vào system prompt của A2 và A3.

---

## 1. NĂM BẪY ĐÃ ĐẢO NGƯỢC KẾT LUẬN TRONG THỰC TẾ

### L1 · Bẫy dữ liệu chưa chín

**Đã xảy ra:** khảo sát báo *"ngách đang pha loãng, M2.4 = 0,45 → nên dừng"*.
Tính lại chỉ trên video đã đủ 60 ngày: **M2.4 = 1,30 — ngách khoẻ**.

**Nguyên nhân:** so cửa sổ 0–90 ngày (chỉ 36% video đã chín) với cửa sổ 90–180
ngày (100% đã chín). Video mới chưa kịp tích view, kéo trung vị xuống.

**Quy tắc cho agent:**
```
- Phân tích NGUỒN CUNG (đếm video, đếm kênh) -> dùng toàn bộ
- Phân tích HIỆU QUẢ (view, vpd, lift)      -> CHỈ dùng video đã chín
- Hai cửa sổ so sánh phải ĐỀU đã chín hoàn toàn
```

### L2 · Nghịch lý Simpson

**Đã xảy ra:** đặc trưng *"tiêu đề có tên sách Kinh Thánh"*:

| Lớp kiểm | Kết quả | Nếu dừng ở đây |
|---|---|---|
| Trong mẫu outlier | lift **8,1×**, p < 0,001 | "rất mạnh, nên làm!" |
| Toàn thị trường | lift **0,48×** | "ngược lại?" |
| Trong từng kênh | **6/13** kênh tốt hơn | "hoà — không có quy luật" |

**Phán quyết đúng: KHÔNG XÁC NHẬN.** Hướng này thực tế có hiệu quả 0,61× toàn
ngách — tức là **kém hơn** mặt bằng.

**Quy tắc cho agent:**
```
p < 0,05 CHƯA ĐỦ. Luôn đọc trường "within_channel" trước khi kết luận.
Nếu số kênh cùng chiều < 60% -> nghi ngờ Simpson, hạ cấp phán quyết.
```

### L3 · Artefact toán học từ mẫu số

**Đã xảy ra:** `engagement_rate` cho hiệu ứng **mạnh nhất** trong 26 đặc trưng
(Cliff's delta = −0,682, p < 0,001). Nhưng đó không phải phát hiện.

**Nguyên nhân:** `engagement = (like + comment) / view`. Nhóm thắng có view
trung vị 71.314, nhóm thua 863 — **gấp 82 lần**. Mẫu số lớn hơn → tỷ lệ nhỏ
hơn, một cách máy móc.

**Quy tắc cho agent:**
```
Với MỌI tỷ lệ có view ở mẫu số, hỏi trước:
"chỉ số này có bị chi phối bởi mẫu số không?"
Gọi test_correlation(view_count, <chỉ số>) để kiểm.
```

### L4 · Thiên lệch sống sót ở cấp kênh

**Đã xảy ra:** M3.2 = 61,5% kênh mới đạt traction — con số rất đẹp. Nhưng dữ
liệu **chỉ có kênh còn tồn tại**. Kênh thất bại đã bị xoá.

**Hệ quả:** tỷ lệ thành công thật **thấp hơn** con số báo cáo. Không có cách
sửa từ dữ liệu — chỉ có cách **nói thật**.

**Quy tắc cho agent:**
```
Mọi tỷ lệ thành công phải kèm câu: "dữ liệu chỉ chứa kênh còn tồn tại,
tỷ lệ thật thấp hơn con số này".
```

### L5 · Chỉ số không đo được nhưng vẫn ra số

**Đã xảy ra:** M3.3 *"thời gian đạt 100k view"* tính ra **0,4 tháng** — vô lý.

**Nguyên nhân:** `view_count` là view **tích luỹ đến ngày crawl**, không phải
view tại thời điểm đăng. Nên `cumsum` luôn vượt 100k sau vài video.

**Quy tắc cho agent:**
```
Với 1 snapshot, MỌI chỉ số dạng "cumsum đến khi đạt X" đều vô nghĩa.
Khi chỉ số không đo được: THAY bằng chỉ số đo được tương đương,
đừng bỏ trống, đừng báo số sai.
CON SỐ VÔ LÝ LÀ TÍN HIỆU TỐT — nó buộc kiểm lại.
Luôn hỏi: "con số này có hợp lý không?"
```

---

## 2. ĐẶC THÙ NGÁCH NHẠC YOUTUBE

### Về phân bố dữ liệu

```
- View phân bố ĐUÔI DÀI. Trung bình luôn cao hơn trung vị nhiều lần.
  Ngách christian-blues: trung bình 17.009 vs trung vị 1.687 — gấp 10 lần.
  LUÔN dùng trung vị.

- Kênh lớn thì video nào cũng nhiều view. Không chuẩn hoá theo chính kênh đó
  thì mọi "video thắng" đều thuộc kênh lớn, và bài học duy nhất rút ra là
  "hãy là kênh lớn" — vô dụng.
```

### Về hành vi khán giả

```
- Nhạc là nội dung nghe NỀN hoặc nghe CHỦ ĐỘNG:
  · nghe nền     -> độ dài quan trọng, lời không quan trọng
  · nghe chủ động -> lời quan trọng, sai chất bị phát hiện ngay
  Phải xác định loại nào TRƯỚC khi kết luận về sản xuất.

- Khán giả tìm nhạc qua ĐỀ XUẤT, không qua tìm kiếm (tỷ lệ ~7:1).
  Nghĩa là tối ưu từ khoá tìm kiếm KHÔNG phải đòn bẩy chính.
  Đòn bẩy là CHỌN ĐỀ TÀI và TÍN HIỆU CLICK.

- Comment chỉ đến từ người chịu bình luận — mẫu thiên lệch.
  Tuổi trung vị 70 là của 82 người tự khai trên 6.413, tức 1,3%.
  Trích con số đó mà bỏ cỡ mẫu là sai lệch nghiêm trọng.
```

### Về sản xuất

```
- Hai mô hình đối lập CÙNG thắng được:
  · "nhiều & ngắn": ~6 phút, ~9 video/tháng, ăn bằng khối lượng
  · "ít & dài"    : ~60 phút, ~7 video/tháng, ăn bằng thời lượng xem
  Phải chọn MỘT trước khi sản xuất.

- Thumbnail thường KHÔNG phân biệt được thắng/thua trong ngách nhạc.
  Kiểm định 26 đặc trưng trên 596 ảnh: 0 đặc trưng đứng vững.
  Nó là VÉ VÀO CỬA, không phải đòn bẩy.

- Điệu trưởng chiếm đa số kể cả trong "Blues" (201/307 = 65%).
  Đừng giả định "Blues = buồn = điệu thứ".
```

---

## 3. HAI LOẠI CÂU HỎI — CHỌN SAI THÌ LÀM ĐÚNG QUY TRÌNH VẪN RA SAI THỨ

```
Người dùng hỏi "làm thế này CÓ THẮNG không?"
  -> KIỂM ĐỊNH
  -> bắt buộc nhóm đối chứng + kiểm Simpson 3 lớp
  -> kết quả điển hình: KHÔNG CHỨNG MINH ĐƯỢC
  -> dùng để: quyết định vào ngách

Người dùng hỏi "nhóm thắng ĐANG LÀM thế nào?"
  -> BRIEF
  -> chỉ mô tả nhóm top, không cần đối chứng
  -> kết quả: công thức sao chép được
  -> dùng để: sản xuất hàng loạt
```

**Quy tắc:** hỏi rõ người dùng cần **đầu ra** gì trước khi chọn phương pháp.
Brief **không được** trình bày như bằng chứng nhân quả.

---

## 4. QUY TẮC N5 — NGUỒN NGOÀI KHÔNG THAY BẰNG CHỨNG NỘI BỘ

**Đã xảy ra:** một bản định vị cho điểm tin cậy **5/5** cho hai hướng, dựa vào
báo cáo AARP/NEFE về việc người Mỹ cô đơn và căng thẳng tài chính. Trong khi
bằng chứng nội bộ của chính hai hướng đó là **BÁC BỎ**.

**Vì sao sai:**

```
"Người Mỹ cô đơn"                    = sự thật về DÂN SỐ
"Kênh làm chủ đề cô đơn sẽ có view"  = phát biểu về THỊ TRƯỜNG NỘI DUNG
                                       -> HAI THỨ KHÁC NHAU
```

**Quy tắc cho agent:**
```
Nguồn ngoài CHỈ được dùng để:
  ✅ giải thích VÌ SAO một phát hiện nội bộ có lý
  ✅ cảnh báo xu hướng dài hạn
  ❌ KHÔNG nâng độ tin cậy của phát hiện nội bộ
  ❌ KHÔNG cứu một hướng đã bị dữ liệu bác bỏ
```

---

## 5. SÁU NHÓM NGUỒN VÀ ĐIỀU YOUTUBE KHÔNG THẤY

| Mã | Nguồn | Thấy gì |
|---|---|---|
| **Y** | YouTube | cung đã tồn tại và đang thắng |
| **P** | Spotify, podcast, TikTok | cung thay thế |
| **S** | Google Trends, autocomplete | cầu qua hành vi |
| **V** | Reddit, forum | cầu phát ngôn, ngôn ngữ thật |
| **K** | báo cáo ngành | cơ chế công năng |
| **N** | Analytics kênh nhà | RPM thật, retention thật |

**Điều quan trọng nhất agent phải biết:**

```
Câu hỏi "cái gì đang tồn tại, ai thắng"      -> YouTube trả lời ĐẦY ĐỦ
Câu hỏi "cầu nào chưa được đáp ứng"          -> YouTube RẤT KÉM
Câu hỏi "cầu dịch chuyển về đâu 6-12 tháng"  -> YouTube GẦN NHƯ MÙ

Nếu chỉ có nguồn Y, mọi phát biểu về khoảng trống và xu hướng phải mang
cảnh báo "suy gián tiếp". Mục thiếu dữ liệu ghi "[—] chưa có nguồn",
KHÔNG bỏ trống. Bỏ trống tạo ảo giác đã đầy đủ.
```

---

## 6. QUY TẮC R6 — RANH GIỚI ĐẠO ĐỨC

```
CẤM TUYỆT ĐỐI, không có ngoại lệ:
- Suy đoán tuổi/sắc tộc/tôn giáo từ TÊN hoặc ẢNH ĐẠI DIỆN
- Ghép tên thật với thuộc tính sức khoẻ/hoàn cảnh
- Công bố trích dẫn kèm comment_id thật

Vì sao: comment_id tra ngược ra tài khoản thật qua YouTube API chỉ bằng
MỘT lời gọi. Ghép nó với thuộc tính sức khoẻ rồi công bố = xuất bản
hồ sơ suy đoán về người thật.

CHỈ ghi nhận thuộc tính khi người ta TỰ KHAI công khai trong nội dung comment.
```

---

## 7. BA CÂU HỎI TRƯỚC MỌI KẾT LUẬN

Nhúng vào prompt của A3 và A4:

```
① SO VỚI CÁI GÌ?
   "Video này 50.000 view" vô nghĩa.
   "Gấp 5 lần trung vị của chính kênh đó" mới có nghĩa.

② CÓ THỂ DO NGUYÊN NHÂN KHÁC KHÔNG?
   Bắt buộc nêu ít nhất MỘT cách giải thích ngược.
   Đây là chỗ Simpson bị bắt.

③ ĐỘ TIN CẬY BAO NHIÊU?
   n ≥ 30 -> được kết luận
   n < 30 -> ghi "KHÔNG ĐỦ MẪU", KHÔNG kết luận
```

---

## 8. CÁCH CẬP NHẬT FILE NÀY

Mỗi lần agent mắc lỗi mới:

1. Ghi lại **đã xảy ra gì** (số cụ thể, không mô tả chung)
2. Tìm **nguyên nhân gốc**
3. Viết **quy tắc** dạng mệnh lệnh cho agent
4. Thêm một ca vào **bộ test đỏ** của M6

File này là thứ đáng giá nhất trong blueprint — code viết lại được, tri thức
này phải trả giá mới có.
