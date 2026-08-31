# CÁCH PHÂN TÍCH TỪNG BƯỚC — kèm code thật

> Mỗi mục theo cùng một khuôn: **Câu hỏi → Đọc gì → Làm gì → Ra gì → Bẫy**.
> Code trích nguyên văn từ `pipeline/`, không viết lại cho đẹp.
>
> Phiên bản: v1.0 · Lập 2026-08-28

---

## STEP_02 · QUY MÔ & ĐỘNG LƯỢNG

**Câu hỏi:** Ngách đang lên hay đang xuống? Cầu có tăng nhanh hơn cung không?

**Đọc:** `videos_enriched.parquet` · `channels.parquet`

### Làm gì

So hai cửa sổ thời gian **đều đã chín**:

```
cửa sổ NAY  : 150–60 ngày trước   (mọi video đều ≥60 ngày tuổi)
cửa sổ TRƯỚC: 240–150 ngày trước  (mọi video đều ≥60 ngày tuổi)
```

```python
M2_1_view_growth   = view_cửa_sổ_nay / view_cửa_sổ_trước      # cầu
M2_2_supply_growth = số_video_nay    / số_video_trước          # cung
M2_4_gap           = M2_1 / M2_2                               # cầu so cung
```

### Ra gì

| Chỉ số | Giá trị | Nghĩa |
|---|---|---|
| M2.1 | 1,62× | cầu tăng 62% |
| M2.2 | 1,24× | cung tăng 24% |
| **M2.4** | **1,30×** | **cầu tăng nhanh hơn cung → còn chỗ** |

### Bẫy — L1, bẫy đắt nhất dự án

Nếu **không** lọc theo `is_matured`, hai cửa sổ mặc định là 0–90 và 90–180 ngày:

```
M2.4 thô = 0,45  →  "ngách đang pha loãng, nên DỪNG"
M2.4 đúng = 1,30 →  "ngách khoẻ, ĐI TIẾP"
```

Nguyên nhân: cửa sổ 0–90 ngày chỉ có **36%** video đã đủ 60 ngày. Video mới
chưa kịp tích view, kéo trung vị xuống.

> Giống như so chiều cao đứa trẻ 5 tuổi với người 30 tuổi rồi kết luận
> loài người đang lùn đi.

---

## STEP_03 · ĐỐI THỦ

**Câu hỏi:** Ai đang thắng? Người mới còn cửa vào không?

**Đọc:** `channels.parquet` · `selected_videos.parquet`

### Làm gì

**Gini** — đo mức độ tập trung thị phần:

```
Gini = 0   → mọi kênh chia đều
Gini = 1   → một kênh ăn hết
```

Ngách này: **0,63** — tập trung vừa phải.

**Tỷ lệ kênh mới thành công** — chỉ số quyết định "còn cửa không":

```python
young = channels[channels.age_months < 24]
success = young[young.views_per_month >= threshold]
M3_2 = len(success) / len(young)        # 24/39 = 61,5%
```

### Ra gì

| Chỉ số | Giá trị |
|---|---|
| Gini | 0,63 |
| Top 1 kênh | 18,5% thị phần |
| Top 20% kênh | 63,1% |
| **Kênh trẻ thành công** | **61,5%** (24/39) |
| Nhanh nhất đạt ngưỡng | **0,6 tháng** |

### Bẫy

Ngách cha (Christian/Gospel) có top 20% chiếm **81,98%** — bị khoá chặt.
Ngách con này 63,1% — thoáng hơn rõ rệt. **Luôn so với ngách cha**, không so
với con số tuyệt đối.

---

## STEP_04 · SÀNG LỌC ĐỐI CHỨNG

> ⚠️ Bước này **không** tìm công thức thắng. Nó **loại trừ**. Tên cũ là
> *"Công thức thắng"* và đã đổi vì gây hiểu nhầm nghiêm trọng (bài học T29).

**Câu hỏi:** Đặc trưng nào **thật sự** phân biệt video thắng và thua?

**Đọc:** `selected_videos.parquet` — cả rổ **B1** (thắng) và **B4** (thua)

### Làm gì — kiểm định 3 lớp

```
LỚP 1 · trong mẫu     so B1 với B4          → Mann-Whitney U, p-value
LỚP 2 · toàn thị trường  đặc trưng đó trên TẤT CẢ video
LỚP 3 · trong từng kênh  đếm bao nhiêu kênh cùng chiều
```

Chỉ khi **cả ba lớp cùng chiều** mới gọi là XÁC NHẬN.

### Ra gì

| Chỉ số | Kết quả |
|---|---|
| Đặc trưng kiểm định | 26 |
| **Đặc trưng đứng vững** | **0** |

### Vì sao "0/26" là kết quả TỐT

Đây là chỗ dễ hiểu lầm nhất. Kết quả rỗng nghĩa là:

> *"Không có mẹo thumbnail nào cứu được nội dung yếu."*

Nếu không có rổ đối chứng B4, ta sẽ kết luận: *"90% video thắng có nền tối →
làm nền tối sẽ thắng."* Nhưng 90% video **thua** cũng nền tối.

Biết một biến **không** có tác dụng giúp dồn công sức vào chỗ có tác dụng.

### Bẫy — nghịch lý Simpson, ví dụ thật

Đặc trưng *"tiêu đề có tên sách Kinh Thánh"*:

| Lớp | Kết quả | Đọc là |
|---|---|---|
| Lớp 1 · trong mẫu outlier | lift **8,1×** · p < 0,001 | "rất mạnh!" |
| Lớp 2 · toàn thị trường | lift **0,48×** | "ngược lại?" |
| Lớp 3 · trong từng kênh | **6/13 kênh** tốt hơn | "hoà — không có quy luật" |

**Phán quyết: KHÔNG XÁC NHẬN.**

Nếu chỉ chạy lớp 1, kết luận sẽ là *"hãy đặt tên sách Kinh Thánh vào tiêu đề"*
— và nó **sai**, vì hướng này có hiệu quả 0,61× toàn ngách.

---

## STEP_05 · KHÁN GIẢ

**Câu hỏi:** Khách hàng là ai? Họ nghe lúc nào? Họ đau chỗ nào?

**Đọc:** `selected_comments.parquet` (6.794 dòng)

### Làm gì — regex, không phải LLM

Đây là bước bạn hỏi nhiều nhất, nên viết kỹ.

**Bước 1 — loại nhiễu:**

```python
noise = (c.low.str.count(r'\n') >= 6) | c.low.str.contains(
         r'purgatory|st\. gertrude|prayer for (venezuela|the dead)')
lyric = c.low.str.contains(r'verse\s*:|chorus\s*:|\d+:\d{2}\s*-')
c["is_noise"] = noise | lyric
```

Loại 381 dòng: lời cầu nguyện dài chép lại, lyrics chép nguyên bài. 6.794 → **6.413**.

**Bước 2 — bắt thuộc tính TỰ KHAI:**

```python
AGE = re.compile(r"\bi(?:'m| am)\s+(\d{2})\b|\b(\d{2})\s*(?:years?\s*old|yrs?\s*old|yo)\b", re.I)

def age_of(t):
    m = AGE.search(t)
    if not m: return np.nan
    a = int(m.group(1) or m.group(2))
    return a if 13 <= a <= 99 else np.nan     # chặn số vô lý
```

> **Quy tắc R6 — ranh giới đạo đức:** chỉ ghi nhận thuộc tính khi người ta
> **tự khai công khai**. Tuyệt đối không suy đoán tuổi/sắc tộc/tôn giáo từ tên
> người hay ảnh đại diện.

**Bước 3 — bắt nỗi đau và bối cảnh:**

```python
PAIN = {
 "finally":     r"\bfinally\b|\bat last\b|\bbeen (?:looking|searching) for\b",
 "never_heard": r"\bnever heard\b|\bnever found\b|\bfirst time i(?:'ve)? heard\b",
 "cant_stand":  r"\bcan'?t stand\b|\btired of\b|\bhate the lyrics\b",
 ...
}
CTX = {
 "prayer_devo": r"\b(?:pray(?:er|ing)?|devotion|quiet time|bible study|meditat)\b",
 "sick_hosp":   r"\b(?:hospital|chemo|cancer|surgery|in pain|hospice)\b",
 "grief":       r"\b(?:passed away|funeral|lost my|grie(?:f|ving))\b",
 ...
}
```

**Bước 4 — kiểm định tín hiệu nào THẬT SỰ được đồng tình:**

Đây là chỗ tách hệ thống này khỏi một bảng đếm từ khoá thông thường.

```python
baseline = d.like_count.median()                    # nền của ngách = 4 like
for signal in PAIN:
    nhóm = d[d[signal]]
    p = mannwhitneyu(nhóm.like_count, d[~d[signal]].like_count).pvalue
    lift = nhóm.like_count.median() / baseline
```

### Ra gì

| Tín hiệu | n | Like trung vị | So nền | Phán quyết |
|---|---|---|---|---|
| `finally` | 58 | 26,5 | **6,6×** | XÁC NHẬN |
| `never_heard` | 55 | 25,0 | **6,2×** | XÁC NHẬN |
| `p_elder` | 70 | 23,5 | **5,9×** | XÁC NHẬN |
| `struggling` | 110 | 5,0 | 1,2× | YẾU |
| `healing` | 757 | 3,0 | 0,8× | **BÁC BỎ** |

### Bẫy — số lượng không phải sức mạnh

`healing` xuất hiện **757 lần** — nhiều gấp 13 lần `finally` (58 lần). Đếm từ
khoá đơn thuần sẽ kết luận *"khán giả cần chữa lành"*.

Nhưng like trung vị của nhóm `healing` là **3**, thấp hơn nền (4). Nghĩa là
người ta **nói nhiều** về chữa lành nhưng **không ai đồng tình đặc biệt**.

Còn `finally` chỉ 58 lần nhưng mỗi lần được **26,5 like** — người khác đọc và
gật đầu.

> **Bài học:** tần suất đo *"người ta nói gì"*; like đo *"người khác có thấy
> đúng không"*. Hai thứ khác nhau, và thứ hai mới đáng tin.

---

## STEP_06 · TỪ KHOÁ & CHỦ ĐỀ

**Câu hỏi:** Chủ đề nào thật sự ăn? Khán giả và kênh có nói cùng thứ tiếng không?

**Đọc:** `selected_videos.parquet` · output của step05

### Làm gì — code kiểm định đầy đủ

Đây là đoạn code quan trọng nhất trong toàn hệ thống, trích nguyên văn:

```python
for k, p_ in THEME.items():
    m[k] = m.title.str.lower().str.contains(p_, regex=True)
    a = m[m[k]]; b = m[~m[k]]
    if len(a) < 20: continue                          # mẫu quá nhỏ -> bỏ

    pv   = mannwhitneyu(a.vpd, b.vpd).pvalue          # LỚP 1
    lift = a.vpd.median() / b.vpd.median()

    wc = []                                            # LỚP 3 — chống Simpson
    for h, g in m.groupby("handle"):
        if g[k].sum() >= 5 and (~g[k]).sum() >= 5:    # kênh đủ mẫu cả hai phía
            wc.append(g[g[k]].vpd.median() / g[~g[k]].vpd.median())

    within_median_lift = np.median(wc)
```

Rồi phán quyết theo thứ tự — **thứ tự này quan trọng**:

```python
def verdict(r):
    if r.p >= 0.05:                              return "BÁC BỎ"
    if r.n_ch_tested >= 5 and r.within_median_lift < 1:
                                                 return "BÁC BỎ (Simpson)"
    if r.lift >= 1.3 and (r.n_ch_tested < 5 or r.within_median_lift >= 1.1):
                                                 return "XÁC NHẬN"
    if r.lift >= 1.15:                           return "YẾU"
    if r.lift <= 0.8:                            return "TRÁNH"
    return "BÁC BỎ"
```

Đọc kỹ dòng thứ hai: **kiểm Simpson đặt TRƯỚC kiểm XÁC NHẬN**. Một chủ đề có
p rất nhỏ và lift rất cao vẫn bị bác nếu nó không thắng trong từng kênh.

### Ra gì

16 chủ đề kiểm định → **1 XÁC NHẬN**:

| Chủ đề | n | lift thô | lift trong-kênh | Phán quyết |
|---|---|---|---|---|
| `thanks` | 55 | 1,62× | **2,28×** | **XÁC NHẬN** |
| `old_school` | 222 | 2,37× | 1,05× | YẾU |
| `testimony` | 452 | 1,51× | 0,85× | BÁC BỎ (Simpson) |
| `healing` | 733 | 0,74× | 0,88× | BÁC BỎ (Simpson) |
| `scripture` | 652 | 0,61× | 1,28× | **TRÁNH** |

**Đọc bảng này thế nào:**

- `thanks` có lift trong-kênh (2,28×) **cao hơn** lift thô (1,62×) → hiệu ứng
  thật, không phải do rơi vào kênh mạnh. Đây là tín hiệu mạnh nhất có thể có.
- `old_school` lift thô cao nhất (2,37×) nhưng trong-kênh chỉ 1,05× → hiệu ứng
  đến từ *kênh nào làm*, không phải *chủ đề*.

### Khoảng trống ngôn ngữ

Phép đếm đơn giản nhưng cho phát hiện chắc chắn nhất, vì không phụ thuộc mô hình:

```python
for word in vocab_top:
    ratio = số_lần_trong_comment / số_lần_trong_tiêu_đề
```

| Từ | Trong comment | Trong tiêu đề | Tỷ lệ |
|---|---|---|---|
| `amen` | 2.233 | **5** | **446×** |
| `thank` | 3.062 | 24 | 128× |
| `blues` | 715 | **6.623** | 0,1× |

Khán giả nói *"amen, thank you"*; kênh đặt tên *"blues, gospel"*. Hai vốn từ
gần như không giao nhau.

---

## STEP_07 · KIẾM TIỀN & RỦI RO

**Câu hỏi:** Ngách này ra tiền không? Rủi ro gì?

**Làm gì:** ước lượng RPM theo thị trường Tier-1 và độ dài video, nhân với
dung lượng view.

### Ra gì

| Kịch bản | RPM | Doanh thu/tháng |
|---|---|---|
| Thấp | $1,5 | $159 |
| Cơ sở | $3,0 | **$319** |
| Cao | $6,0 | $638 |

### Bẫy — đây là chỉ số YẾU NHẤT trong toàn hệ thống

Khoảng dao động $1,5–$6,0 là **sai số 4 lần** giữa hai đầu. RPM lấy từ
benchmark ngoài, **không phải số thật của kênh nào**.

Đây là chỉ số duy nhất mang mã nguồn `Y+K` (trộn YouTube với báo cáo ngành).
Chỉ nguồn `N` — Analytics kênh nhà — mới cho RPM thật.

---

## PHỤ · CÁCH VẼ BIỂU ĐỒ

Bạn hỏi *"bạn tạo ảnh như thế nào"*. Không có AI sinh ảnh nào cả — chỉ
matplotlib, và mọi số đọc từ file.

```python
import matplotlib
matplotlib.use("Agg")                    # không mở cửa sổ, chạy được trên server
import matplotlib.pyplot as plt

plt.rcParams.update({
  "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
  "figure.dpi": 150, "axes.grid": True, "grid.alpha": .25})

ACC="#8C3A2B"; OK="#2F6B4F"; WARN="#B8860B"; MUTE="#9A8E85"

R = json.load(open(OUT/"_metrics_raw.json"))     # ĐỌC TỪ FILE, không gõ tay
ad = R["age"]["dist"]

fig, ax = plt.subplots(figsize=(5, 2.9))
ax.bar(list(ad.keys()), list(ad.values()), color=[MUTE,MUTE,MUTE,ACC,ACC])
ax.set_title(f"Tuổi tự khai (n={R['age']['n']}) — trung vị {R['age']['median']:.0f}")
plt.savefig(OUT/"c1_age.png", bbox_inches="tight")
```

Ba quy tắc:

1. **Màu mang nghĩa**, không trang trí: xanh lá = XÁC NHẬN, vàng = YẾU,
   xám = BÁC BỎ. Người đọc nhìn màu là biết độ tin cậy.
2. **Cỡ mẫu luôn trong tiêu đề** — `n=82` ngay trên biểu đồ, không giấu ở chú thích.
3. **Số đọc từ JSON**, không gõ tay (bài học T27) — nếu không, sửa dữ liệu mà
   biểu đồ vẫn hiện số cũ.

---

## PHỤ · CÁCH DỰNG PDF

`WeasyPrint` — HTML + CSS → PDF. Không dùng LaTeX, không dùng Word.

```python
from weasyprint import HTML
HTML(string=DOC, base_url=".").write_pdf(OUT)
```

Ba bẫy đã mắc, ghi lại để bạn khỏi mắc lại:

| Bẫy | Triệu chứng | Cách tránh |
|---|---|---|
| **T87** | `display:flex` → cả khối **biến mất**, không báo lỗi | Nhiều cột phải dùng `<table>` thật |
| **T88** | `page-break-inside:avoid` trên khối cao → **trang trắng** | Chỉ dùng cho khối < 1/3 trang |
| **T89** | `table-layout:fixed` thiếu width → chữ dán nhau | Đặt width cho **tất cả** cột, cộng đủ 100% |

> **Quy tắc nghiệm thu:** luôn render PDF ra ảnh và **nhìn bằng mắt**.
> `extract_text()` không phát hiện được T87 — chữ vẫn nằm trong luồng văn bản
> dù khối không hiển thị.

```bash
pdftoppm -png -r 68 bao-cao.pdf /tmp/trang
```
