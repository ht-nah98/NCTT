# TỰ XÂY LẠI / NÂNG CẤP — bắt đầu từ đâu

> Dành cho người muốn tự làm: nâng cấp một phần, thêm nguồn mới, hoặc xây lại
> từ đầu bằng công cụ khác.
>
> Phiên bản: v1.0 · Lập 2026-08-28

---

## 1. NẾU CHỈ CÓ 1 NGÀY — XÂY BẢN TỐI GIẢN

Bốn thứ này là **xương sống**. Có đủ bốn thì đã hơn hầu hết phân tích thị
trường; thiếu một thì kết luận không đáng tin.

### ① Chuẩn hoá theo tuổi video

```python
df["age_days"]   = (crawl_date - df.published_at).dt.days.clip(lower=1)
df["vpd"]        = df.view_count / df.age_days
df["is_matured"] = df.age_days >= 60
```

Không có bước này, mọi so sánh đều lệch — video cũ luôn "thắng" chỉ vì có nhiều
thời gian tích view.

### ② Chuẩn hoá theo chính kênh

```python
base = df[df.is_matured].groupby("channel_id").view_count.median()
df["outlier_ratio"] = df.view_count / df.channel_id.map(base)
```

Không có bước này, mọi "video thắng" đều thuộc kênh lớn, và bài học duy nhất
rút ra là *"hãy là kênh lớn"*.

### ③ Nhóm đối chứng

```python
B1 = matured[(matured.outlier_ratio >= 5)   & (matured.view_count >= 20000)]  # thắng
B4 = matured[(matured.outlier_ratio <= 0.2) & (matured.view_count >= 500)]    # THUA
```

Không có `B4`, mọi "công thức thắng" đều là mê tín.

### ④ Kiểm trong từng kênh (chống Simpson)

```python
wc = []
for handle, g in df.groupby("handle"):
    if g[feature].sum() >= 5 and (~g[feature]).sum() >= 5:
        wc.append(g[g[feature]].vpd.median() / g[~g[feature]].vpd.median())

within_lift = np.median(wc)
if p < 0.05 and len(wc) >= 5 and within_lift < 1:
    verdict = "BÁC BỎ (Simpson)"        # p nhỏ vẫn bác
```

Không có bước này, bạn sẽ tin vào hiệu ứng 8,1× mà thực tế là 0,48×.

---

## 2. THÊM MỘT NGUỒN DỮ LIỆU MỚI (S / V / P / N)

Nhờ vòng nâng cấp 2026-08-28, việc này giờ chỉ đụng **3 chỗ**.

### Bước 1 — khai nhóm nguồn

`pipeline/transform/collect_metrics.py`:

```python
SOURCE_CLASS_BY_GROUP = {
    "market": "Y", "momentum": "Y", ...
    "trends": "S",        # ← thêm dòng này
}
```

### Bước 2 — thêm nguồn vào danh sách gom

Cùng file:

```python
SOURCES = [
    ("02_market", {"market": "M1_", "momentum": "M2_"}),
    ...
    ("10_trends", {"trends": None}),      # ← thư mục mới
]
```

### Bước 3 — mở khoá mã nguồn trong báo cáo

`pipeline/report/_t1_common.py`:

```python
AVAILABLE = {"Y", "S"}        # ← thêm "S"
```

Xong. Mọi báo cáo tự động: bỏ cảnh báo *"suy gián tiếp"* cho phát biểu dựa
nguồn S, và bảng chú giải tự đổi trạng thái từ "chưa có" thành "đã có".

**Không phải sửa** 4 builder T1.x — chúng đọc mã từ `_meta` qua hàm `cite()`.

---

## 3. CHẠY NGÁCH THỨ HAI

### Bước 1 — dựng khung thư mục

```bash
python3 pipeline/_common.py niches/ngach-moi
```

### Bước 2 — đặt dữ liệu thô

```
niches/ngach-moi/00_input/raw/*.xlsx
```

### Bước 3 — điền NICHE_BRIEF.md

Bắt buộc, vì T1.1 đọc file này cho mục "định nghĩa phạm vi".

### Bước 4 — chạy

```bash
bash pipeline/run_all.sh niches/ngach-moi
```

### ⚠️ Cảnh báo từ bài học T22–T25

> *"Chạy lại được"* chỉ chứng minh **file cũ còn đó**, không chứng minh
> pipeline tự động.

Lần đầu thử trên ngách trống đã lộ ra **4 lỗi ẩn trong một lần chạy** — các
script quên tạo thư mục, quên gom metrics, quên tính điểm trục. Chúng chạy
được suốt nhiều tháng vì file cũ vẫn còn.

**Nên làm:** tạo một ngách trống hoàn toàn và chạy thử **trước khi** tin rằng
hệ thống tự động.

---

## 4. ĐỔI NGƯỠNG PHÁN QUYẾT

Ngưỡng nằm ở **hai chỗ**, đừng nhầm:

| Loại ngưỡng | File | Ảnh hưởng |
|---|---|---|
| Phán quyết chủ đề (XÁC NHẬN/BÁC BỎ) | `pipeline/analyze/step06_keyword.py` hàm `verdict()` | nội dung báo cáo |
| Chấm điểm ngách (0–20) | `00_system/03_SCORING_RUBRIC.md` + `scoring/` | điểm so sánh ngách |

Sau khi đổi **bắt buộc** chạy:

```bash
python3 pipeline/scoring/verify_rubric.py niches/<ngách>
```

Script này kiểm tài liệu ↔ code ↔ điểm có khớp nhau không.

---

## 5. NẾU MUỐN XÂY LẠI BẰNG CÔNG CỤ KHÁC

Bốn nguyên tắc **không phụ thuộc ngôn ngữ**, giữ lại dù bạn dùng R, Julia hay SQL:

### ① Bốn tầng không được trộn

```
FACT → METRIC → SCORE → INSIGHT
       tầng sau KHÔNG được sửa tầng trước
```

Thực thi bằng code: chỉ **một** file được ghi file điểm.

### ② Mọi chỉ số mang metadata

```json
{
  "source": "processed/videos.parquet",
  "source_class": "Y",
  "computed_by": "A1",
  "confidence": "medium",
  "caveat": "chỉ 1 snapshot",
  "counter_evidence": "kênh mới vẫn đạt 3,05tr/2,8 tháng"
}
```

Trường `counter_evidence` **bắt buộc** khi `confidence ≠ high`. Đây là cách ép
người viết phải nghĩ về bằng chứng phản bác.

### ③ Quy tắc nào cũng phải có thứ thực thi và thứ kiểm

Bài học T90, đắt nhất về mặt tổ chức:

> `10_SOURCE_CLASSES.md` viết quy tắc *"mọi chỉ số phải mang `source_class`"*
> nhưng dữ liệu thật có **0/24** chỉ số mang nó. Quy tắc thành hư cấu.

Mỗi quy tắc mới phải trả lời ngay: *"cái gì thực thi nó, cái gì kiểm rằng nó
được thực thi?"* Không trả lời được thì đó là **nguyện vọng**, không phải quy tắc.

Hệ thống hiện có 3 lớp tự kiểm:

| Script | Kiểm gì |
|---|---|
| `verify_rubric.py` | code tính lại có khớp điểm không |
| `verify_reports.py` | số trong PDF có khớp điểm hiện tại không |
| `verify_system_docs.py` | tài liệu có còn khớp code không |

### ④ Ghi lại bài học ngay khi mắc lỗi

`framework/04_reference/lessons_learned.md` — **90 bài học**, xếp theo mức nguy
hiểm chứ không theo thời gian. File này đáng giá hơn code, vì code viết lại
được còn bài học thì phải trả giá mới có.

---

## 6. THỨ TỰ ƯU TIÊN NẾU MUỐN NÂNG CẤP

Xếp theo giá trị trên công sức, dựa trên trạng thái hiện tại:

| # | Việc | Vì sao | Khó |
|---|---|---|---|
| 1 | **Thêm nguồn S** (Trends) | Lấp đúng hai câu YouTube mù | thấp |
| 2 | **Snapshot thứ hai** | Mở khoá M3.3, nâng tin cậy M2 | thấp |
| 3 | **Chạy ngách thứ hai** | Kiểm pipeline có thật sự tự động | trung bình |
| 4 | **Nguồn N** (Analytics) | Kiểm chứng 5 cơ chế trong T1.2 | phụ thuộc kênh chạy |
| 5 | **LLM gắn nhãn comment** | Vượt giới hạn regex | trung bình |
| 6 | **Nguồn V** (Reddit) | Ngôn ngữ thật, bổ khuyết comment lệch | trung bình |

---

## 7. BẢN ĐỒ FILE — SỬA GÌ Ở ĐÂU

```
pipeline/
├── extract/normalize.py           xlsx → parquet
├── transform/
│   ├── enrich.py                  ← ngưỡng "đã chín", công thức vpd
│   ├── apply_filters.py           ← ngưỡng 4 rổ B1–B4
│   └── collect_metrics.py         ← nhóm nguồn, gom chỉ số
├── analyze/
│   ├── step02_market.py           quy mô, động lượng
│   ├── step03_competitor.py       đối thủ, Gini
│   ├── step04_outlier.py          sàng lọc đối chứng
│   ├── step05_audience.py         ← regex bình luận
│   ├── step06_keyword.py          ← regex chủ đề + hàm verdict()
│   └── step07_monetization.py     RPM, rủi ro
├── scoring/
│   ├── scoring_engine.py          ← FILE DUY NHẤT ghi scores.json
│   ├── verify_rubric.py           tự kiểm điểm
│   └── verify_system_docs.py      tự kiểm tài liệu
└── report/
    ├── _t1_common.py              ← bảng màu, hàm cite(), AVAILABLE
    ├── build_T11_niche_facts.py   T1.1
    ├── build_T12_audience_model.py T1.2
    ├── build_T13_music_spec.py    T1.3
    └── build_T14_competitor_cards.py T1.4
```
