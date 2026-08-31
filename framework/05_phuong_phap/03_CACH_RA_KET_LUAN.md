# CÁCH RA KẾT LUẬN — từ bảng số thành câu nói

> Đây là phần "đúc kết" — chỗ dễ tự lừa nhất trong toàn bộ quy trình.
> Tài liệu này ghi các quy tắc chặn việc đó.
>
> Phiên bản: v1.0 · Lập 2026-08-28

---

## 1. VẤN ĐỀ CỐT LÕI

Sau khi chạy xong, ta có hàng trăm con số. Nhưng người đọc cần **một câu**:
*"nên vào ngách này hay không, và vào bằng cách nào."*

Khoảng cách từ *bảng số* đến *câu nói* là chỗ mọi sai lệch chui vào. Ba kiểu
sai phổ biến nhất:

| Kiểu sai | Biểu hiện | Ví dụ thật đã mắc |
|---|---|---|
| **Chọn số hợp ý** | bỏ qua số ngược chiều | Bản định vị cũ cho 5/5 tin cậy cho hướng mà nội bộ **BÁC BỎ** |
| **Nhầm tương quan với nhân quả** | "X đi cùng thắng → X gây ra thắng" | Kinh Thánh lift 8,1× trong mẫu, 0,48× toàn thị trường |
| **Số lớn nghe như quan trọng** | tần suất cao = đáng làm | `healing` 757 lần nhưng like thấp hơn nền |

---

## 2. THANG PHÁN QUYẾT — NĂM MỨC

Mọi phát hiện phải rơi vào đúng một mức. Không có mức "có vẻ tốt".

| Mức | Điều kiện | Được phép nói gì |
|---|---|---|
| **XÁC NHẬN** | p < 0,05 · lift ≥ 1,3 · thắng trong từng kênh | "dữ liệu ủng hộ hướng này" |
| **YẾU** | p < 0,05 · lift 1,15–1,3 | "có tín hiệu, cần thêm mẫu" |
| **BÁC BỎ** | p ≥ 0,05 | "không có bằng chứng" |
| **BÁC BỎ (Simpson)** | p nhỏ nhưng **thua trong từng kênh** | "hiệu ứng là ảo giác do gộp kênh" |
| **TRÁNH** | lift ≤ 0,8 | "dữ liệu nói hướng này kém hơn mặt bằng" |

**Thứ tự kiểm bắt buộc:** p-value → Simpson → lift. Đặt Simpson sau lift là
sai, vì một chủ đề lift 2,4× vẫn có thể là ảo giác gộp kênh.

---

## 3. BỐN CÂU HỎI TRƯỚC KHI VIẾT MỘT CÂU KẾT LUẬN

### ① So với cái gì?

Con số trần trụi vô nghĩa.

| ❌ Sai | ✅ Đúng |
|---|---|
| "Video này 50.000 view" | "Gấp 5 lần trung vị của chính kênh đó" |
| "757 comment nhắc chữa lành" | "757/6.413 = 11,8%, nhưng like trung vị 3 so với nền 4" |
| "RPM $3" | "$3 với khoảng dao động $1,5–$6 — sai số 4 lần" |

### ② Có thể do nguyên nhân khác không?

Bắt buộc liệt kê **ít nhất một** cách giải thích ngược. Đây là chỗ Simpson bị bắt.

Ví dụ thật:
> *"Chủ đề `old_school` có lift 2,37× — cao nhất."*
> **Giải thích ngược:** hay là vì mấy kênh mạnh tình cờ hay làm chủ đề này?
> **Kiểm:** trong từng kênh lift chỉ 1,05× → **đúng là do kênh, không do chủ đề**.

### ③ Cỡ mẫu bao nhiêu?

```
n ≥ 30    → được kết luận
n < 30    → ghi "KHÔNG ĐỦ MẪU", KHÔNG kết luận
```

Ví dụ thật: nhóm `widow` có **5 người**, `nurse_care` **2 người**, `disabled`
**1 người** trên 6.413. Xây cả một hướng kênh cho nhóm n=1 không phải phân
tích — và còn chạm quy tắc R6 về suy đoán nhóm thuộc tính nhạy cảm.

### ④ Bằng chứng phản bác là gì?

Mỗi kết luận phải kèm **điều kiện bị bác**. Không có nghĩa là chưa nghĩ kỹ.

```
Kết luận : "chủ đề cảm tạ đáng thử"
Bị bác nếu: VPD nhóm cảm tạ không vượt trung vị kênh sau khi kiểm ≥3 kênh
```

---

## 4. QUY TẮC N5 — NGUỒN NGOÀI KHÔNG THAY BẰNG CHỨNG NỘI BỘ

Đây là quy tắc sinh ra từ một lỗi thật, đáng nhắc riêng.

**Lỗi đã mắc:** bản định vị 14 hướng cho điểm tin cậy **5/5** cho hai hướng,
dựa vào báo cáo AARP/NEFE về việc người Mỹ cô đơn và căng thẳng tài chính.
Trong khi bằng chứng nội bộ của chính hai hướng đó là **BÁC BỎ**.

**Vì sao sai:** báo cáo ngành nói *"người Mỹ cô đơn"* — đó là sự thật về **dân
số**. Nó không chứng minh *"kênh làm chủ đề cô đơn sẽ có view"* — đó là phát
biểu về **thị trường nội dung**. Hai thứ khác nhau.

**Quy tắc:**

```
Nguồn K (báo cáo ngành) chỉ được dùng để:
  ✅ giải thích VÌ SAO một phát hiện nội bộ có lý
  ✅ cảnh báo xu hướng dài hạn
  ❌ KHÔNG được dùng để nâng độ tin cậy của phát hiện nội bộ
  ❌ KHÔNG được dùng để cứu một hướng đã bị dữ liệu bác bỏ
```

---

## 5. CÁCH GẮN MÃ NGUỒN — LÀM LỖ HỔNG HỮU HÌNH

Mọi phát biểu mang mã `Y·P·S·V·K·N`. Chi tiết ở `../00_system/10_SOURCE_CLASSES.md`.

Điều quan trọng nhất: **YouTube mù ở hai câu hỏi**.

| Câu hỏi | YouTube thấy | Kết luận |
|---|---|---|
| Cái gì đang tồn tại, ai đang thắng? | **Đầy đủ** | Y là đủ |
| Cầu nào chưa được đáp ứng? | **Rất kém** | bắt buộc nguồn ngoài |
| Cầu dịch chuyển về đâu 6–12 tháng? | **Gần như mù** | bắt buộc nguồn ngoài |

Hệ thống hiện có **1/6 nhóm nguồn**. Nên mọi phát biểu về khoảng trống tự động
mang cảnh báo *"suy gián tiếp"*, và mục thiếu dữ liệu ghi `[—] chưa có nguồn`
thay vì bỏ trống.

> Một mục ghi *"chưa có nguồn"* là **thông tin**.
> Một mục bỏ trống là **ảo giác đã đầy đủ**.

---

## 6. VÍ DỤ ĐẦY ĐỦ — TỪ SỐ THÔ ĐẾN CÂU KẾT LUẬN

Theo dõi một phát hiện đi hết đường:

### Bước 1 — số thô (FACT)

```
55 video có chữ thank/grateful/blessing trong tiêu đề
VPD nhóm này  : 15,32
VPD nhóm khác : 9,43
```

### Bước 2 — chỉ số (METRIC)

```
lift = 15,32 / 9,43 = 1,62×
p = 0,0134
```

### Bước 3 — kiểm Simpson (LỚP 3)

```
3 kênh có đủ ≥5 video cả hai phía
lift trong từng kênh: [2,28 · 1,94 · 2,63]
trung vị = 2,28×
```

### Bước 4 — phán quyết

```
p < 0,05                      ✓ qua
within_median_lift = 2,28 > 1 ✓ không phải Simpson
lift = 1,62 ≥ 1,3             ✓
n_ch_tested = 3 < 5           → nhánh "n_ch_tested < 5" của điều kiện XÁC NHẬN

=> XÁC NHẬN
```

### Bước 5 — câu kết luận, kèm đủ ràng buộc

> **Chủ đề cảm tạ là chủ đề duy nhất trong 16 chủ đề vượt qua kiểm định
> Simpson.** Lift trong-kênh (2,28×) cao hơn lift thô (1,62×) — nghĩa là khi
> cùng một kênh làm chủ đề này, nó thắng chính mình. Đây là dấu hiệu hiệu ứng
> thật, không phải ảo giác do kênh mạnh. **Rủi ro:** mẫu nhỏ (n=55, chỉ 3 kênh
> được kiểm) — kết luận đúng về hướng, nhưng độ lớn hiệu ứng có thể lệch.
> `[Y]` `n=55`

Chú ý câu kết luận chứa: **phát hiện** + **vì sao tin được** + **rủi ro** +
**mã nguồn** + **cỡ mẫu**. Thiếu bất kỳ phần nào là chưa đạt chuẩn.

---

## 7. PHÂN BIỆT BỐN LOẠI PHÁT BIỂU

Sau 49 vòng, đây là cách phân loại đã chốt (`11_OUTPUT_CONTRACT.md`):

| Phát biểu có thể… | Thuộc | Ví dụ |
|---|---|---|
| **sai khi dữ liệu mới về** | T1.1 fact | "53 kênh, trung vị 1.687 view" |
| **bị bác bằng một thí nghiệm** | T1.2 cơ chế | "nếu đổi tiêu đề, CTR sẽ tăng" |
| **là tham số để làm ra thứ gì đó** | T1.3 đặc tả | "BPM 88, LUFS −13,8" |
| **nói về một kênh cụ thể** | T1.4 thẻ đối thủ | "kênh X đăng 27 video/tháng" |

Trộn bốn loại này trong một trang là lỗi tổ chức đã sửa ở vòng 49 — trước đó
một câu hỏi phải mở 6 file, và sự thật quan sát bị trộn với suy luận.

---

## 8. RÀNG BUỘC ĐẶC BIỆT CHO T1.2 — CƠ CHẾ

Mỗi cơ chế **bắt buộc** kèm dự đoán kiểm chứng được:

```python
def mech(num, title, claim, evidence, prediction, strength, falsify):
    assert prediction, f"Cơ chế {num} thiếu dự đoán kiểm chứng được"
```

Script **không dựng được PDF** nếu thiếu. Lý do:

> Cơ chế không có dự đoán kiểm chứng được thì **không phải cơ chế** — nó là
> lời kể. Lời kể nghe hợp lý và không bao giờ sai, vì không có cách nào sai.

Ví dụ đạt chuẩn:

```
Cơ chế  : "khoảnh khắc tìm thấy mạnh hơn khoảnh khắc đồng cảm"
Dự đoán : nếu đúng, video định vị bằng PHÁT HIỆN sẽ có tỷ lệ bình luận/view
          cao hơn video định vị bằng AN ỦI — đo trên ≥20 video mỗi nhóm
Bị bác  : nếu nhóm "an ủi" đạt tỷ lệ ngang hoặc cao hơn
```

---

## 9. DANH SÁCH KIỂM TRƯỚC KHI GIAO BÁO CÁO

```
□ Mọi con số có cỡ mẫu đi kèm
□ Mọi phát biểu có mã nguồn Y·P·S·V·K·N
□ n < 30 đã ghi KHÔNG ĐỦ MẪU, không kết luận
□ Mỗi kết luận có ít nhất một bằng chứng phản bác
□ Đã kiểm Simpson cho mọi phát hiện có p nhỏ
□ Không có kết luận nào trái với kiểm định thống kê
□ Nguồn ngoài không được dùng để nâng tin cậy nội bộ (N5)
□ Mục thiếu dữ liệu ghi "[—] chưa có nguồn", không bỏ trống
□ Số trong PDF đọc từ file, không gõ tay (T27)
□ Đã render PDF ra ảnh và nhìn bằng mắt (T87)
```
