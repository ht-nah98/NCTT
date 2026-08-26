# STEP_04b — PHÂN TÍCH THUMBNAIL (ẢNH THẬT)

> **Bước tùy chọn.** Chỉ chạy khi có file ảnh trong `<niche>/00_input/raw/thumbs/`.
> Nếu chỉ có đặc trưng số đã trích sẵn → dừng ở STEP_04.

---

## 1. BƯỚC NÀY TRẢ LỜI CÂU HỎI GÌ

> **Đặc điểm hình ảnh của thumbnail có quyết định kết quả video không?**

Và nếu không, thì: **ngách này trông như thế nào** (chuẩn hình ảnh để không lạc lõng).

**Khác gì STEP_04:** STEP_04 dùng 22 đặc trưng SỐ đã trích sẵn (độ sáng, bão hòa, `text_score`…).
Bước này mở **ảnh thật** → đo được bố cục, khuôn mặt, chữ, trùng lặp hình ảnh.

---

## 2. ĐIỀU KIỆN VÀO

| Cần có | Kiểm bằng |
|---|---|
| STEP_04 đã xong | `04_outlier/_metrics_raw.json` tồn tại |
| Ảnh `.jpg`, tên file = `video_id` | `ls raw/thumbs/*.jpg \| wc -l` |
| Model YuNet | `pipeline/_models/face_detection_yunet.onnx` |
| ≥30 ảnh mỗi nhóm B1/B4 | script tự kiểm và dừng nếu thiếu |

**Kiểm khớp trước khi chạy:**
```python
ids = set(pd.read_parquet("...videos_enriched.parquet").video_id)
files = {f.stem for f in Path("raw/thumbs").glob("*.jpg")}
print(len(ids & files), "khớp |", len(ids - files), "thiếu ảnh")
```
Phủ **<30%** → kết quả không đại diện, ghi rõ hạn chế hoặc bỏ bước.

---

## 3. CHẠY

```bash
# 1. Trích đặc trưng cho TOÀN BỘ ảnh (~15s/1000 ảnh với 8 tiến trình)
python3 pipeline/analyze/step04c_thumbnail_full.py <niche> --workers=8

# 2. So B1 (thắng) vs B4 (đối chứng)
python3 pipeline/analyze/step04b_thumbnail.py <niche>

# 3. Phân tích nhóm dẫn đầu (view và like tách riêng)
python3 pipeline/analyze/step04d_thumbnail_top.py <niche>

# 4. Biểu đồ + PDF
python3 pipeline/report/charts04b.py
python3 pipeline/report/build_report04b.py
```

---

## 4. ⚠️ KIỂM CÔNG CỤ TRƯỚC KHI TIN SỐ

**Bắt buộc, không được bỏ.** Bài học T12–T16: lần chạy đầu ở `christian-blues` cho
kết quả sai hoàn toàn vì bộ dò hỏng, mà nhìn vẫn rất hợp lý.

### 4.1 Đối chiếu với biến độc lập
```python
# n_faces phải tương quan với skin_ratio (đo độc lập từ crawl)
stats.mannwhitneyu(m[m.n_faces>0].skin_ratio, m[m.n_faces==0].skin_ratio)
```
p **lớn** (>0.05) → **bộ dò hỏng**, không phải "ngách không có mặt người".

### 4.2 Mở ảnh ra xem tận mắt
Dựng contact sheet 6 ảnh script nói "có mặt" + 6 ảnh nói "không mặt", rồi **nhìn**.
Mất 2 phút, và là thứ duy nhất chứng minh dứt khoát công cụ sai.

### 4.3 Kiểm tính hợp lý
| Chỉ số | Ngưỡng vô lý |
|---|---|
| Diện tích chữ trung vị | >40% ảnh → bộ dò gộp nhầm vùng ảnh |
| Tỷ lệ có mặt | <40% với ngách chân dung → bộ dò bỏ sót |
| Số mặt trung bình | >3 với ảnh chân dung đơn → dương tính giả |

---

## 5. LOGIC PHÂN TÍCH

### 5.1 Hai nghĩa của "dẫn đầu" — phải tách riêng
| Thước đo | Đo cái gì |
|---|---|
| **Lượt xem** | YouTube **đẩy** video đi bao xa |
| **Tỷ lệ like** | Khán giả **ủng hộ** mạnh đến đâu |

Chúng cho kết quả khác nhau (bài học B28). Không gộp.

### 5.2 Ba lớp kiểm — bắt buộc đủ
```
Lớp 1  top 10% vs nửa dưới        → |Cliff's δ| ≥ 0.30 và p < 0.01
Lớp 2  toàn thị trường            → lift > 1.15
Lớp 3  TRONG TỪNG KÊNH            → trung vị > 1 và ≥60% kênh cùng chiều
```
**Rớt bất kỳ lớp nào → BÁC BỎ.** Lớp 3 là lớp giết chết nhiều phát hiện nhất.

### 5.3 Ngưỡng đáng kể thực tế (B27)
Qua cả 3 lớp nhưng chênh **trong cùng kênh < 10%** → ghi
**"QUA KIỂM ĐỊNH NHƯNG KHÔNG ĐÁNG KỂ"**, không ghi "XÁC NHẬN".

### 5.4 Giải thích cơ chế khi bác bỏ
Tính **kênh giải thích bao nhiêu % biến thiên**:
```python
1 - ((m[metric] - m.groupby("handle")[metric].transform("median")).var() / m[metric].var())
```
Con số cao (>30%) + tương quan cấp kênh mạnh → **xác nhận là hiệu ứng kênh, không phải hiệu ứng ảnh**.

---

## 6. ĐẦU RA

| File | Nội dung |
|---|---|
| `processed/thumb_features_full.parquet` | 19 đặc trưng × toàn bộ ảnh (tầng FACT) |
| `04_outlier/10_thumb_top_tests.csv` | Kiểm định nhóm dẫn đầu, 2 thước đo |
| `04_outlier/11_cross_channel_dups.csv` | Cặp ảnh trùng giữa các kênh |
| `04_outlier/_thumb_top_metrics.json` | Metric + cơ chế giải thích |
| `99_report/STEP04b_Phan-tich-Thumbnail.pdf` | Báo cáo |

---

## 7. TIÊU CHÍ XONG

- [ ] Đã kiểm công cụ đo (§4) — **cả ba mục**
- [ ] Mỗi đặc trưng vượt lớp 1 đều đã kiểm lớp 2+3
- [ ] Đặc trưng qua 3 lớp đã kiểm ngưỡng đáng kể thực tế
- [ ] Nếu bác bỏ hết → **đã giải thích cơ chế** (kênh giải thích bao nhiêu %)
- [ ] Đã đo trùng lặp giữa kênh → đối chiếu trục T6
- [ ] PDF xuất được, số liệu khớp `_thumb_top_metrics.json`
- [ ] `PROGRESS.md` cập nhật

---

## 8. LIÊN KẾT

| Tài liệu | Quan hệ |
|---|---|
| `STEP_04_outlier.md` | Bước cha — bước này bổ sung |
| `01_agents/A3_outlier_miner.md` | Agent phụ trách |
| `04_reference/lessons_learned.md` | **T12–T16** (lỗi công cụ), **B27–B28** |
| `00_system/04_SELECTION_LOGIC.md` | Định nghĩa rổ B1/B4 |

---

## 9. KẾT QUẢ ĐÃ CÓ

| Ngách | Ảnh | Đặc trưng xác nhận | Kết luận |
|---|---|---|---|
| `christian-blues` | 7.193 (100%) | **0 / 12** | Hình ảnh thumbnail không quyết định kết quả. Kênh giải thích 39.1% biến thiên tỷ lệ like |

> **Kỳ vọng hợp lý:** kết quả âm tính là **bình thường** ở bước này. Thumbnail ảnh hưởng CTR,
> nhưng trong một ngách mà mọi kênh đều dùng cùng một phong cách AI-generated, phong cách đó
> trở thành **vé vào cửa**, không phải lợi thế cạnh tranh.
