# ĐƯỜNG ĐI CỦA DỮ LIỆU — từ file thô đến kết luận

> Mọi con số ở đây đo trên ngách `christian-blues` ngày 2026-08-28. Chạy lại
> `bash pipeline/run_all.sh` là ra đúng những số này.
>
> Phiên bản: v1.0 · Lập 2026-08-28

---

## 1. TOÀN CẢNH — 6 CHẶNG

```
①  THU THẬP        xlsx từ YouTube API           7.193 video · 145.150 comment
        ↓
②  CHUẨN HOÁ       xlsx → parquet                cùng số dòng, kiểu dữ liệu chuẩn
        ↓
③  LÀM GIÀU        + 8 cột suy ra                7.193 × 13 → 7.193 × 28 cột
        ↓
④  LỌC CHỌN LỌC    4 rổ video + 3 tầng comment   7.193 → 965 · 145.150 → 6.794
        ↓
⑤  PHÂN TÍCH       6 bước độc lập                → _metrics_raw.json mỗi bước
        ↓
⑥  GOM + CHẤM      hợp nhất → áp ngưỡng → điểm   → metrics.json → scores.json
        ↓
    BÁO CÁO        4 tài liệu T1.1–T1.4
```

Tổng thời gian chạy lại: **66 giây** (nhánh lõi, không tính ảnh và âm thanh).

---

## 2. CHẶNG ① — THU THẬP (ngoài phạm vi hệ thống)

Hệ thống **không tự crawl**. Nó bắt đầu từ file đã có.

| File vào | Nội dung | Ai làm |
|---|---|---|
| `00_input/raw/*.xlsx` | kênh · video · comment | R&D crawl bằng YouTube Data API v3 |
| `00_input/raw/audio/*.yaml` | đặc trưng DSP | IT trích bằng librosa |
| `00_input/raw/thumbs/*.jpg` | ảnh thumbnail | IT tải |
| `niches/<ngách>/00_input/raw/audio_dna_full.jsonl` | 594 trường/track | IT trích |

**Bất biến R1:** `00_input/raw/` **không bao giờ được sửa** sau khi nhận. Mọi
thứ phái sinh đều tái tạo được bằng cách chạy lại. Nếu sửa raw, không ai biết
kết quả cũ dựa trên dữ liệu nào.

---

## 3. CHẶNG ② — CHUẨN HOÁ

`pipeline/extract/normalize.py` · xlsx → parquet

Việc duy nhất: đổi định dạng và chuẩn hoá kiểu dữ liệu. **Không tính toán gì.**

| Ra | Dòng × cột |
|---|---|
| `channels.parquet` | 53 × 15 |
| `videos.parquet` | 7.193 × 13 |
| `comments.parquet` | 145.150 × 11 |
| `video_stats.parquet` | 7.193 × 5 |
| `thumbnails.parquet` | 7.193 × 22 |

Vì sao dùng parquet: đọc nhanh hơn xlsx ~50 lần, giữ kiểu dữ liệu (ngày tháng
không bị biến thành chuỗi), và nén tốt.

---

## 4. CHẶNG ③ — LÀM GIÀU

`pipeline/transform/enrich.py` · 7.193 × 13 → **7.193 × 28 cột**

Đây là chặng **quan trọng nhất mà người ngoài hay bỏ qua**. Ba cột sinh ra ở
đây quyết định mọi kết luận về sau:

### `age_days` — tuổi video

```python
v["age_days"] = (CRAWL - v.published_at).dt.days.clip(lower=1)
```

`clip(lower=1)` tránh chia cho 0 với video đăng cùng ngày crawl.

### `vpd` — view mỗi ngày

```python
v["vpd"] = v.view_count / v.age_days
```

**Vì sao cần:** video đăng 2 năm trước có nhiều view hơn video đăng tuần trước
— không phải vì nó hay hơn, mà vì nó có nhiều thời gian tích view hơn. So
`view_count` trực tiếp là so người 30 tuổi với đứa trẻ 5 tuổi.

### `is_matured` — đã chín chưa

```python
v["is_matured"] = v.age_days >= 60
```

**Ngưỡng 60 ngày** không tuỳ tiện. Đây là bài học **L1**, bẫy suýt làm dừng cả
một ngách tốt:

> Khảo sát sơ bộ báo *"ngách đang pha loãng, M2.4 = 0,45 → nên dừng"*.
> Tính lại chỉ trên video đã chín: **M2.4 = 1,30 — ngách khoẻ.**
> Kết luận đảo ngược hoàn toàn.
>
> Nguyên nhân: so cửa sổ 0–90 ngày (chỉ 36% video đã chín) với cửa sổ 90–180
> ngày (100% đã chín).

**Quy tắc rút ra:** phân tích *nguồn cung* thì dùng toàn bộ; phân tích *hiệu
quả* thì **chỉ dùng video đã chín**.

### `outlier_ratio` — vượt trội so với chính kênh mình

```python
base = v[v.is_matured].groupby("channel_id").view_count.median()
v["outlier_ratio"] = v.view_count / v.channel_median_view
```

**Vì sao chia cho trung vị của chính kênh đó:** kênh 143.000 sub thì video nào
cũng nhiều view. Không chuẩn hoá thì mọi "video thắng" đều thuộc về kênh lớn,
và ta chỉ học được *"hãy là kênh lớn"* — vô dụng.

Chuẩn hoá xong, câu hỏi đổi thành: *"video nào vượt trội so với mặt bằng của
chính kênh nó?"* — câu này mới học được.

---

## 5. CHẶNG ④ — LỌC CHỌN LỌC

`pipeline/transform/apply_filters.py`

**Vì sao phải lọc:** 145.150 comment mà phân tích hết thì vừa chậm vừa nhiễu.
Phần lớn là `"Amen"`, emoji, spam. Lọc không phải để tiết kiệm — mà để **tăng
tỷ lệ tín hiệu trên nhiễu**.

### Bốn rổ video: 7.193 → 965

| Rổ | Điều kiện | Trả lời câu hỏi |
|---|---|---|
| **B1 · outlier** | `outlier_ratio ≥ 5` và `view ≥ 20.000` | Video thắng đậm trông thế nào? |
| **B2 · đang lên** | `age ≤ 90 ngày` và `vpd ≥ phân vị 90` | Cái gì đang lên ngay bây giờ? |
| **B3 · đại diện** | top 5 video mỗi kênh | Mỗi kênh làm gì là chính? |
| **B4 · ĐỐI CHỨNG** | `outlier_ratio ≤ 0,2` và `view ≥ 500` | **Video thua trông thế nào?** |

> **Rổ B4 là rổ quan trọng nhất, và là thứ hầu hết phân tích thị trường không có.**
>
> Không có nhóm đối chứng thì mọi "công thức thắng" đều là mê tín. Ví dụ:
> 90% video thắng có thumbnail nền tối → nghe như quy luật. Nhưng 90% video
> **thua** cũng nền tối → đặc trưng đó vô nghĩa.
>
> Đây chính là cách hệ thống phát hiện **0/26 đặc trưng thumbnail** thật sự
> phân biệt thắng/thua.

### Ba tầng comment: 145.150 → 6.794

| Tầng | Điều kiện | Ý nghĩa |
|---|---|---|
| **C1 · được bình chọn** | `like ≥ 25` | Nhiều người khác đồng tình |
| **C2 · chiều sâu** | `dài ≥ 200 ký tự` và `like ≥ 2` | Người chịu viết dài = kể chuyện thật |
| **C3 · ngẫu nhiên** | 1.500 mẫu, `random_state=42` | **Chống thiên lệch** của C1 và C2 |

Lọc sơ bộ trước cả ba tầng: bỏ comment dưới 15 ký tự (loại `"Amen"`, emoji),
bỏ trùng lặp theo `(video_id, text)` (loại spam).

`random_state=42` cố định để **chạy lại ra đúng mẫu cũ** — nếu không, mỗi lần
chạy sẽ ra kết quả hơi khác và không ai biết số nào đúng.

### Năm kiểm chứng sau khi lọc

Lọc xong phải chứng minh mẫu **không bị lệch**:

| Kiểm | Ngưỡng đạt |
|---|---|
| Phủ kênh | 100% kênh còn đại diện |
| Phủ thời gian | ≥ 90% số tháng |
| Phủ định dạng | đủ 6 dải độ dài |
| Rổ đối chứng B4 | ≥ 100 video |
| Phủ lượt xem | ghi lại % view được giữ |

Không đạt → dừng, sửa ngưỡng, chạy lại. Không đi tiếp với mẫu lệch.

---

## 6. CHẶNG ⑤ — SÁU BƯỚC PHÂN TÍCH

Mỗi bước độc lập, đọc parquet, ghi `_metrics_raw.json` của riêng nó.

| Bước | Đọc | Trả lời | Ghi |
|---|---|---|---|
| `step02_market` | videos, channels | Ngách lên hay xuống? | `02_market/` |
| `step03_competitor` | channels, selected_videos | Ai thắng? Còn cửa? | `03_competitor/` |
| `step04_outlier` | selected_videos + **B4** | Đặc trưng nào **không** phân biệt? | `04_outlier/` |
| `step05_audience` | selected_comments | Khách là ai? | `05_audience/` |
| `step06_keyword` | selected_videos | Chủ đề nào ăn? | `06_keyword/` |
| `step07_monetization` | channels | Ra tiền không? | `07_monetization/` |

### Thứ tự không tuỳ tiện

`step05` và `step06` chạy **sau** `step04` vì:

- `step04` chọn ra video thắng → `step05` chỉ đọc comment **của những video đó**
- `step04` loại bỏ giả thuyết sai → `step06` không phí công đi hướng đã bị bác

Đảo thứ tự sẽ phải quét toàn bộ 145.150 comment — vi phạm nguyên tắc chọn lọc.

### Cổng quyết định sau step02

```
M2.4 ≥ 1,0    → đi tiếp bình thường
0,5 ≤ M2.4 < 1,0 → đi tiếp nhưng đổi câu hỏi: không hỏi "vào hay không"
                    mà hỏi "vào bằng khác biệt gì"
M2.4 < 0,5    → DỪNG
```

Phân tích một ngách đang chìm là **tối ưu hoá con tàu đang chìm**.

---

## 7. CHẶNG ⑥ — GOM VÀ CHẤM

```
collect_metrics.py   6 file _metrics_raw.json → _state/metrics.json
                     + gắn source_class cho 111 chỉ số
        ↓
apply_thresholds.py  áp ngưỡng rubric → điểm từng trục
        ↓
scoring_engine.py    → _state/scores.json          ← file DUY NHẤT ghi được
        ↓
verify_rubric.py     tự kiểm: code tính lại có khớp scores.json không
```

**Bất biến:** chỉ `scoring_engine.py` được ghi `scores.json`. Đây là cách thực
thi quy tắc *"tầng 4 không sửa tầng 3"* ở cấp code, không chỉ ở cấp lời hứa.

---

## 8. HAI NHÁNH TUỲ CHỌN

Chạy song song, **không tác động điểm số**, vì chúng trả lời câu hỏi khác:

### Nhánh ảnh — cần `raw/thumbs/*.jpg`

```
step04c_thumbnail_full   trích đặc trưng hình học toàn ngách (7.193 ảnh)
step04b_thumbnail        so B1 vs B4  → KIỂM ĐỊNH
step04d_thumbnail_top    nhóm top + kiểm Simpson
step04g_brief_extract    YOLO-seg + OCR trên top 5%  → BRIEF
```

### Nhánh nhạc — cần `raw/audio*`

```
step04h_audio       AUDIO_BRIEF.json     mô tả nhóm top
step04h2_audio_test AUDIO_TEST.json      KIỂM ĐỊNH thắng/thua
step04h3_audio_recipe AUDIO_RECIPE.json  công thức tái tạo (161 thông số)
step04i_lyrics      LYRICS_ANALYSIS.json ghép lời × nhạc (307 track)
```

### Phân biệt KIỂM ĐỊNH và BRIEF — bài học đắt nhất dự án

| | KIỂM ĐỊNH | BRIEF |
|---|---|---|
| Câu hỏi | Đặc điểm X có **gây ra** thành công? | Nhóm thắng **đang làm** thế nào? |
| Cần đối chứng? | **Bắt buộc** (rổ B4) | Không |
| Cần kiểm Simpson? | **Bắt buộc** 3 lớp | Không |
| Kết quả điển hình | **KHÔNG CHỨNG MINH ĐƯỢC** | công thức sao chép được |
| Dùng để | quyết định vào ngách | sản xuất hàng loạt |

**Quy tắc:** hỏi người dùng cần **đầu ra** gì *trước khi* chọn phương pháp.
Brief **không được** trình bày như bằng chứng nhân quả.

---

## 9. BẢNG TRA NHANH — MUỐN ĐỔI GÌ THÌ SỬA Ở ĐÂU

| Muốn đổi | Sửa file | Nhớ chạy lại |
|---|---|---|
| Ngưỡng "đã chín" (60 ngày) | `pipeline/transform/enrich.py` | toàn bộ |
| Ngưỡng 4 rổ B1–B4 | `pipeline/transform/apply_filters.py` | từ chặng ④ |
| Mẫu regex chủ đề | `pipeline/analyze/step06_keyword.py` `THEME` | step06 trở đi |
| Mẫu regex bình luận | `pipeline/analyze/step05_audience.py` `PAT/PAIN/CTX` | step05 trở đi |
| Ngưỡng phán quyết | `pipeline/analyze/step06_keyword.py` `verdict()` | step06 trở đi |
| Ngưỡng chấm điểm | `00_system/03_SCORING_RUBRIC.md` + `scoring/` | từ chặng ⑥ |
| Nhóm nguồn dữ liệu | `pipeline/transform/collect_metrics.py` `SOURCE_CLASS_BY_GROUP` | từ chặng ⑥ |
