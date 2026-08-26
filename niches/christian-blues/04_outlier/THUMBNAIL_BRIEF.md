# BRIEF TÁI TẠO THUMBNAIL — CHRISTIAN BLUES

> **Mục đích:** tài liệu để dựng hệ thống sinh ảnh hàng loạt.
> **Nguồn:** 259 thumbnail của video **top 5% lượt xem** (≥53.374 view, trung vị **122.711**),
> từ 41 kênh, chỉ video dài >60s, đã đủ 60 ngày tuổi.
> **Ngày:** 17/08/2026 · Đo bằng YOLO11-seg (người) + EasyOCR (chữ) + k-means (màu)

---

## ⚠️ ĐỌC TRƯỚC: brief này là gì và KHÔNG phải gì

| | |
|---|---|
| ✅ **LÀ** | Mô tả chính xác **nhóm dẫn đầu đang làm thế nào** — công thức sao chép được |
| ❌ **KHÔNG phải** | Bằng chứng "làm thế này sẽ thắng" |

Kiểm định riêng (STEP_04b) cho thấy **không đặc trưng hình ảnh nào phân biệt được**
video thắng/thua trong ngách. Nghĩa là: brief này giúp bạn **không lạc lõng** và
**sản xuất nhanh**, nhưng thắng hay không phụ thuộc **âm nhạc** và **nhịp đăng**.

Hãy coi đây là **vé vào cửa**, không phải lợi thế cạnh tranh.

---

## 1. KHUNG HÌNH & TỶ LỆ CHIẾM CHỖ

```
Kích thước      1280 × 720 px (16:9)  — 97% dùng chuẩn này
```

| Thành phần | Chiếm khung | Khoảng chấp nhận | Ghi chú |
|---|---|---|---|
| **NGƯỜI** (cả thân, tóc, mũ) | **27,6%** ≈ 1/4 | 21,7% – 34,8% | 94,2% ảnh có người |
| **KHUÔN MẶT** riêng | 3,4% | — | 91,5% có mặt · 76,1% đúng **một** mặt |
| **CHỮ** (tổng các dòng) | **17,4%** ≈ 1/6 | 11,7% – 24,5% | 96,5% ảnh có chữ |
| Dòng chữ lớn nhất | cao 20,1% khung | — | tức ~145px trên ảnh 720p |

> **Quy tắc ngón tay cái:** người 1/4 khung · chữ 1/6 khung · còn lại là nền.
> 68,7% ảnh chỉ có **một** nhân vật — không dùng nhóm đông.

---

## 2. BỐ CỤC

```
┌─────────────────────────────────────┐
│                                     │
│   ┌──────────┐      ┌───────────┐   │  chữ đặt ở giữa theo chiều dọc
│   │          │      │   CHỮ     │   │  (44% ảnh) hoặc hơi cao (38,6%)
│   │  NGƯỜI   │      │  3 dòng   │   │
│   │          │      └───────────┘   │  mặt nằm ở 34,6% chiều cao
│   └──────────┘                      │  (nửa trên khung)
│                                     │
└─────────────────────────────────────┘
        người ~1/4          chữ ~1/6
```

| Kiểu bố cục | Tỷ lệ |
|---|---|
| Người **trái** – chữ **phải** | 40,9% |
| Người **phải** – chữ **trái** | 34,4% |
| Khác (chồng lấn, giữa) | 24,7% |

**→ Ba phần tư số ảnh tách đôi trái/phải.** Chọn ngẫu nhiên hướng, tỷ lệ ~55/45.

| Vị trí chữ theo chiều dọc | Tỷ lệ |
|---|---|
| Giữa khung | 44,0% |
| Phần trên | 38,6% |
| Phần dưới | 13,9% |

**Số dòng chữ: 3** (trung vị) — thường là: tiêu đề lớn · phụ đề nhỏ · tên kênh.

---

## 3. BẢNG MÀU

```
#000000  đen              40,3%  ← nền chủ đạo
#202020  xám rất tối       6,4%
#200000  nâu đen           6,3%
#402000  nâu hổ phách      4,1%
#402020  nâu đỏ            2,5%
#404040  xám trung tính    2,2%
#202000  ô-liu tối         2,2%
```

| Chỉ số | Giá trị | Nghĩa |
|---|---|---|
| Vùng tối (V<70) | **61,0%** khung | Ảnh **tối là chuẩn**, không phải ngoại lệ |
| Vùng rất tối (<60 xám) | 65,4% | |
| Vùng sáng (>190 xám) | 6,6% | Điểm sáng nhỏ — đèn sân khấu, viền tóc |
| Sắc hổ phách/vàng | **15,8%** | Nguồn sáng ấm |
| Sắc xanh lạnh | **0,8%** | ⚠️ **Gần như không dùng** |
| Ảnh đen trắng hoàn toàn | 16,6% | Một nhánh phong cách riêng |
| Độ ấm (R−B) | +20,1 | Ngả ấm rõ rệt |

> **Quy tắc màu:** nền đen · nguồn sáng ấm hổ phách · **tránh xanh lam/xanh lá**.
> Cứ 6 ảnh thì 1 ảnh làm đen trắng hoàn toàn (biến thể để đỡ nhàm).

---

## 4. ÁNH SÁNG & ỐNG KÍNH

| Đặc điểm | Giá trị |
|---|---|
| Nền mờ (bokeh) | 45,9% ảnh có nền mờ mạnh (tỷ số nét giữa/biên > 2) |
| Tỷ số nét trung vị | 1,88× |

**Kiểu ánh sáng chuẩn:** một nguồn sáng ấm chiếu xiên từ một bên, nền chìm trong bóng tối,
viền sáng nhẹ trên tóc/vai. Đây là kiểu **chiaroscuro** — tương phản sáng tối mạnh.

---

## 5. NHÂN VẬT (mô tả chủ thể do AI tạo)

> Đây là mô tả **nhân vật hư cấu trong ảnh AI**, không phải người thật —
> dùng làm đầu vào prompt, không suy diễn về khán giả.

### Nhánh A — "Ông già blues" (chủ đạo)
```
Nam, da đen, tuổi biểu kiến 60–80
Râu trắng/muối tiêu rậm · thường đội mũ phớt (fedora)
Trang phục: vest cũ, áo khoác da, sơ mi, dây đeo quần
Tư thế: hát vào micro cổ, mắt nhắm, biểu cảm mãnh liệt
        hoặc ôm guitar thùng, cúi đầu
Bối cảnh: quán blues tối, nhà thờ gỗ, hiên nhà miền Nam
```

### Nhánh B — "Người trẻ đeo tai nghe" (playlist/R&B)
```
Nam hoặc nữ, da đen, tuổi biểu kiến 25–40
Tai nghe chụp tai lớn (rất đặc trưng) · râu quai nón gọn (nam)
Trang phục: áo khoác hiện đại, áo len cổ lọ
Tư thế: mắt nhắm, đầu hơi ngửa, thư giãn
Bối cảnh: phông studio xám trơn, ánh sáng viền
```

### Nhánh C — "Nhạc công da trắng ngoài trời" (thiểu số)
```
Nam, da trắng, 40–70 · râu bạc · mũ cao bồi
Guitar thùng · đồng cỏ, nhà gỗ, hồ nước, trời u ám
```

**Tỷ lệ ước tính từ mẫu quan sát:** A ≈ 55% · B ≈ 30% · C ≈ 15%

### Đạo cụ lặp lại
| Đạo cụ | Ghi chú |
|---|---|
| **Micro cổ điển** (Shure 55 kiểu 1950) | phổ biến nhất |
| **Guitar thùng / bán rỗng** | nhánh A và C |
| **Tai nghe chụp tai** | dấu hiệu nhận biết nhánh B |
| **Mũ fedora** | nhánh A |
| **Thánh giá** | trong nền, cửa sổ kính màu |

---

## 6. CHỮ TRÊN ẢNH

### Từ ngữ dùng nhiều nhất (OCR đọc từ 259 ảnh)

| Từ | Số lần | Từ | Số lần |
|---|---|---|---|
| BLUES | 91 | PSALM | 18 |
| GOSPEL | 69 | YOU | 17 |
| WORSHIP | 56 | PLAYLIST | 13 |
| SOUL | 30 | YOUR | 12 |
| CHRISTIAN | 27 | JESUS | 12 |
| SOULFUL | 25 | LORD | 12 |
| STILL | 23 | GOD | 20 |

### Công thức chữ

```
DÒNG 1  (lớn nhất, cao ~20% khung)
        ├─ Kiểu A: tên thể loại       → "SOULFUL CHRISTIAN BLUES"
        ├─ Kiểu B: câu cảm xúc        → "SOMEBODY BEEN PRAYING FOR ME"
        └─ Kiểu C: sách Kinh Thánh    → "PSALM 91" · "ECCLESIASTES IN BLUES"

DÒNG 2  (nhỏ hơn) → "PLAYLIST" · "Music Gospel" · "100 Minutes of..."

DÒNG 3  (nhỏ nhất) → tên kênh, chữ nghiêng, thường góc dưới
```

**IN HOA TOÀN PHẦN: 46,3%** — gần một nửa. Nửa còn lại trộn hoa/thường
hoặc dùng chữ viết tay (script) cho dòng phụ.

### Kiểu chữ quan sát được
| Kiểu | Dùng cho |
|---|---|
| **Sans-serif đậm, viền đen** | tiêu đề chính, nền ảnh phức tạp |
| **Serif cổ điển** | tiêu đề trang trọng ("BE STILL") |
| **Script/viết tay** | tên kênh, dòng phụ ("Music", "Gospel") |
| **Chữ khối kim loại vàng/bạc** | kênh phong cách retro |

**Màu chữ:** trắng (chủ đạo) · vàng hổ phách (#E8B84B) · vàng gradient · đỏ (nhấn)

---

## 7. PROMPT MẪU ĐỂ SINH ẢNH

### Nhánh A — Ông già blues
```
elderly Black gospel blues singer, 70 years old, thick white beard,
wearing worn fedora hat and vintage leather jacket,
singing passionately into a chrome 1950s vintage microphone,
eyes closed, deeply emotional expression, head tilted slightly up,
dim smoky blues club interior, warm amber rim lighting from one side,
deep black background, shallow depth of field, bokeh,
cinematic chiaroscuro lighting, photorealistic, 8k, 16:9
```

### Nhánh B — Người trẻ tai nghe
```
young Black man, 30s, short beard, wearing large over-ear headphones,
eyes closed, head tilted back, serene peaceful expression,
plain dark grey studio backdrop, soft rim light on face edge,
minimal composition, subject on right third of frame,
photorealistic portrait, 8k, 16:9
```

### Nhánh C — Nhạc công ngoài trời
```
weathered white man, 60s, grey beard, cowboy hat, flannel shirt,
sitting on wooden porch of old rural church, playing acoustic guitar,
overcast moody sky, muted green field, cinematic wide shot,
desaturated color grade, 8k, 16:9
```

### Tham số hậu kỳ (áp cho cả 3 nhánh)
```
- Đặt nhân vật vào 1/3 trái HOẶC 1/3 phải (không giữa)
- Nhân vật chiếm 21–35% diện tích khung
- Chừa 1/3 đối diện cho chữ
- Làm tối vùng nền: đưa ~61% khung xuống dưới V=70
- Ngả ấm: tăng kênh đỏ so với xanh khoảng +20
- Chèn 3 dòng chữ, tổng chiếm 12–25% khung, dòng lớn nhất cao ~20%
```

---

## 8. BA MẪU CÓ SẴN TỪ KÊNH DẪN ĐẦU

### Mẫu 1 — `stillworshipmusic` (đỉnh: 3,65 triệu view)
```
Nhân vật cố định   : nam da đen 40–50, râu muối tiêu gọn
Nền                : xám studio trơn, tối
Đạo cụ             : tai nghe chụp tai HOẶC tay đặt lên ngực
Ánh sáng           : viền sáng bên, nền chìm
Chữ                : sans đậm + vàng nhấn, đặt đối diện nhân vật
Nhận diện          : dòng "Still Worship" nhỏ ở dưới + dải sóng âm
```

### Mẫu 2 — `oldiesgospelradio` (đỉnh: 1,10 triệu view)
```
Phong cách         : ĐEN TRẮNG hoàn toàn, thẩm mỹ thập niên 1960
Nhân vật           : nam da đen mặc vest, cà vạt hẹp, tóc chải gọn
Đạo cụ             : micro cổ điển bắt buộc
Bối cảnh           : nhà thờ có cửa kính màu, sân khấu cũ
Chữ                : khối 3D kim loại (bạc/vàng), đặt góc trên
Biến thể           : nhóm tam ca/tứ ca (nam giữa, nữ hai bên)
```

### Mẫu 3 — `holygrooveofficial` (đỉnh: 1,70 triệu view)
```
Công thức tiêu đề  : "[TÊN SÁCH KINH THÁNH] IN BLUES"
                     (PSALM · ISAIAH · ECCLESIASTES · IF DAVID SANG THE BLUES)
Nhân vật           : nhạc công ôm guitar, đa dạng sắc tộc/tuổi
Bối cảnh           : NGOÀI TRỜI — nhà thờ gỗ, đồng cỏ, vườn ô-liu, mưa
Chữ                : trắng viền đen, IN HOA, chiếm nguyên dải trên
Nhận diện          : GẠCH CHÂN ĐỎ dưới một phần tiêu đề
```

---

## 9. TÍN HIỆU CẢNH BÁO — TRÁNH LÀM

Rút từ nhóm **thất bại** (cùng kênh với nhóm top, chỉ 23–60 view):

| ❌ Tránh | Vì sao |
|---|---|
| **Toàn cảnh sân khấu từ xa** | Nhóm thua có 3,5 người/ảnh, mặt chiếm 0,1% — không nhìn rõ ai |
| **Ánh sáng xanh lạnh** | Nhóm thua: 10,3% xanh lạnh · nhóm top: 0,7% |
| **Nhiều nhân vật nhỏ** | Nhóm top 68,7% chỉ một người |
| **Không thấy khuôn mặt** | Nhóm top 91,5% có mặt rõ |
| **Nền sáng đều, không tương phản** | Chuẩn ngách là 61% khung tối |

> ⚠️ Đây là quan sát trên mẫu nhỏ (n=60/nhóm). Ở n=150 khác biệt không còn ý nghĩa
> thống kê — nghĩa là những dấu hiệu này **tương quan chứ chưa chứng minh nhân quả**.
> Dùng làm hướng dẫn thiết kế, không dùng làm lời hứa kết quả.

---

## 10. GẮN VỚI TIÊU ĐỀ & THỜI LƯỢNG VIDEO

### Từ khóa tiêu đề (top 5%, n=259)
| Từ | Tỷ lệ | Từ | Tỷ lệ |
|---|---|---|---|
| gospel | 80,7% | soulful | 19,7% |
| blues | 79,9% | prayer | 17,8% |
| worship | 43,6% | psalm | 11,2% |
| soul | 25,5% | healing | 10,0% |
| christian | 23,6% | praise | 10,0% |

**Độ dài tiêu đề: 72 ký tự** (trung vị) · **29%** có chứa số

### Thời lượng — cả bốn nhóm đều thành công
| Nhóm | Tỷ lệ | View trung vị |
|---|---|---|
| <10 phút | 28,6% | 149.186 |
| 10–40 phút | 15,4% | 107.861 |
| 40–80 phút | 22,0% | 132.840 |
| >80 phút | 34,0% | 105.450 |

**→ Không có thời lượng "đúng".** Chọn theo bối cảnh nghe (STEP_05: khán giả nghe
lúc cầu nguyện, bệnh tật → mix dài phục vụ tốt), không theo thumbnail.

---

## 11. CHECKLIST SẢN XUẤT

```
□ 1280×720
□ Một nhân vật, chiếm 21–35% khung
□ Đặt lệch 1/3 trái hoặc phải
□ Khuôn mặt nhìn rõ, nằm nửa trên (≈35% chiều cao)
□ Nền tối: ~61% khung dưới ngưỡng V=70
□ Nguồn sáng ấm hổ phách, chiếu xiên một bên
□ Nền mờ (bokeh) — nét giữa gấp ~2× nét biên
□ TUYỆT ĐỐI tránh tông xanh lạnh
□ 3 dòng chữ, tổng 12–25% khung
□ Dòng lớn nhất cao ~20% khung (~145px)
□ Chữ đặt đối diện nhân vật, giữa hoặc hơi cao
□ Màu chữ: trắng / vàng hổ phách / vàng gradient
□ Có dòng tên kênh nhỏ (nhận diện thương hiệu)
□ Cứ ~6 ảnh làm 1 ảnh đen trắng (biến thể)
```

---

## 12. NGUỒN SỐ LIỆU

| Con số | Cách tính | File |
|---|---|---|
| Diện tích người | YOLO11-seg phân vùng lớp `person`, tính % pixel | `_brief_features.parquet` |
| Diện tích chữ | EasyOCR khoanh vùng, cộng diện tích, độ tin cậy >0,3 | ↑ |
| Bảng màu | k-means k=5 mỗi ảnh, gộp về lưới 32, cộng tỷ lệ | ↑ |
| Vùng tối | % pixel có V<70 trong không gian HSV | ↑ |
| Bokeh | phương sai Laplacian vùng giữa ÷ vùng biên | ↑ |
| Bố cục | so trọng tâm người và trọng tâm chữ theo trục X | ↑ |

**Kiểm chứng:** 9 ảnh đối chiếu bằng mắt, lệch trung bình **5,0 điểm %**.
Trước khi sửa, phép đo cũ báo người 3,2% (sai ~10×) và chữ 11,4% (sai ~2,5×).

**Script:** `pipeline/analyze/step04g_brief_extract.py`
