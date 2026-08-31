# M1 · DATA CONTRACT

> Module đầu tiên, và là nền của mọi thứ. Không có agent ở đây — code thuần.
>
> **Xong khi:** nạp được 2 ngách khác nhau vào cùng schema, validator không báo lỗi.

---

## 1. MỤC TIÊU

Biến dữ liệu thô (xlsx/csv/API tuỳ nguồn) thành **schema cố định** mà mọi tool
và agent phía sau dựa vào.

**Vì sao phải làm trước:** nếu schema chưa chuẩn, mọi tool phải viết lại, mọi
prompt phải sửa. Đây là chỗ rẻ nhất để sửa sai và đắt nhất nếu bỏ qua.

---

## 2. SCHEMA BẮT BUỘC — 3 BẢNG LÕI

### 2.1 `channels`

| Cột | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| `channel_id` | str | ✅ | khoá chính |
| `handle` | str | ✅ | `@tenkenh` |
| `title` | str | ✅ | |
| `description` | str | | dùng cho T1.4 |
| `country` | str | | có thể trống |
| `published_at` | datetime UTC | ✅ | ngày lập kênh |
| `subscriber_count` | int | ✅ | 0 nếu ẩn |
| `view_count` | int | ✅ | tổng view kênh |
| `video_count` | int | ✅ | |
| `keywords` | str | | từ khoá kênh |
| `fetched_at` | datetime UTC | ✅ | **bắt buộc** — xem §5 |

### 2.2 `videos`

| Cột | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| `video_id` | str | ✅ | khoá chính |
| `channel_id` | str | ✅ | khoá ngoại |
| `title` | str | ✅ | |
| `description` | str | | |
| `tags` | str | | phân tách bằng `\|` |
| `duration_sec` | float | ✅ | |
| `published_at` | datetime UTC | ✅ | |
| `default_audio_language` | str | | |
| `thumbnail_url` | str | | |
| `fetched_at` | datetime UTC | ✅ | |

### 2.3 `video_stats`

Tách riêng khỏi `videos` vì **có thể có nhiều snapshot**.

| Cột | Kiểu | Bắt buộc |
|---|---|---|
| `video_id` | str | ✅ |
| `view_count` | int | ✅ |
| `like_count` | int | |
| `comment_count` | int | |
| `snapshot_at` | datetime UTC | ✅ |

> **Thiết kế cho tương lai:** hệ thống hiện tại chỉ có 1 snapshot, và điều đó
> khoá mất nhiều chỉ số. Tách bảng ngay từ đầu để khi có snapshot thứ hai
> không phải sửa schema.

### 2.4 `comments`

| Cột | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| `comment_id` | str | ✅ | |
| `video_id` | str | ✅ | |
| `parent_id` | str | | rỗng nếu là comment gốc |
| `author_hash` | str | ✅ | **SHA-256 có muối, không đảo ngược** |
| `text` | str | ✅ | |
| `like_count` | int | ✅ | |
| `published_at` | datetime UTC | ✅ | |

> **`author_name` KHÔNG thuộc schema.** Xem §6 về quy tắc R6.

---

## 3. CỘT SUY RA — SINH TỰ ĐỘNG, KHÔNG NHẬN TỪ NGUỒN

Bốn cột này là **xương sống của mọi phân tích**. Sinh ở M1, không để tool tự tính.

```python
def enrich(videos: pd.DataFrame, stats: pd.DataFrame,
           crawl_date: pd.Timestamp) -> pd.DataFrame:
    """Sinh cột suy ra. Đây là nơi DUY NHẤT định nghĩa 4 cột này."""
    v = videos.merge(
        stats.sort_values("snapshot_at").groupby("video_id").last(),
        on="video_id", how="left")

    # ① tuổi video — clip(1) tránh chia 0 với video đăng cùng ngày crawl
    v["age_days"] = (crawl_date - v.published_at).dt.days.clip(lower=1)

    # ② view mỗi ngày — chuẩn hoá theo thời gian tích view
    v["vpd"] = v.view_count / v.age_days

    # ③ đã chín chưa — NGƯỠNG 60 NGÀY, xem §4
    v["is_matured"] = v.age_days >= 60

    # ④ vượt trội so với CHÍNH KÊNH MÌNH
    #    baseline chỉ tính trên video đã chín của kênh đó
    base = (v[v.is_matured].groupby("channel_id").view_count.median()
            .rename("channel_median_view"))
    v = v.merge(base, on="channel_id", how="left")
    v["outlier_ratio"] = v.view_count / v.channel_median_view.replace(0, np.nan)

    return v
```

### Vì sao từng cột tồn tại

| Cột | Không có nó thì | Hệ quả thật |
|---|---|---|
| `age_days` | so video 2 năm với video 1 tuần | video cũ luôn "thắng" |
| `vpd` | không chuẩn hoá được theo thời gian | mọi so sánh hiệu quả đều sai |
| `is_matured` | so nhóm chưa chín với nhóm đã chín | **M2.4 = 0,45 thay vì 1,30 — kết luận đảo ngược** |
| `outlier_ratio` | mọi video thắng đều của kênh lớn | bài học duy nhất: "hãy là kênh lớn" |

---

## 4. NGƯỠNG 60 NGÀY — CÓ THỂ ĐỔI, NHƯNG PHẢI ĐO

Ngưỡng này không thiêng liêng. Cách xác định cho ngách mới:

```python
def find_maturity_threshold(v: pd.DataFrame, snapshots: pd.DataFrame) -> int:
    """Tìm ngưỡng ngày mà sau đó view tăng chậm lại (<5%/tuần).

    Cần ≥2 snapshot. Nếu chỉ có 1 snapshot -> dùng mặc định 60 và GHI RÕ
    đây là giả định chưa kiểm chứng.
    """
    if snapshots.snapshot_at.nunique() < 2:
        return 60          # mặc định, phải ghi caveat
    ...
```

**Quy tắc:** ngưỡng nào cũng phải trả lời được *"vì sao là con số này"*. Nếu
câu trả lời là "mặc định" thì phải ghi caveat vào metadata.

---

## 5. VALIDATOR — CHẶN DỮ LIỆU BẨN TRƯỚC KHI VÀO HỆ THỐNG

```python
CHECKS = [
    ("khoá chính không trùng",
     lambda d: d.video_id.is_unique),

    ("mọi video có kênh tồn tại",
     lambda d, ch: d.channel_id.isin(ch.channel_id).all()),

    ("không có ngày tương lai",
     lambda d: (d.published_at <= d.fetched_at).all()),

    ("view không âm",
     lambda s: (s.view_count >= 0).all()),

    ("đủ video đã chín để phân tích",
     lambda d: d.is_matured.sum() >= 200),

    ("đủ kênh để kiểm Simpson",
     lambda d: d.channel_id.nunique() >= 10),

    ("comment có video tương ứng",
     lambda c, d: c.video_id.isin(d.video_id).mean() >= 0.5),
]
```

Hai kiểm cuối là **cổng chặn**, không phải cảnh báo:

- **`is_matured >= 200`** — dưới ngưỡng này mọi kiểm định đều thiếu lực
- **`channel_id >= 10`** — dưới 10 kênh thì không kiểm Simpson được, mà không
  kiểm Simpson thì mọi phát hiện đều đáng ngờ

Không đạt → **dừng, không chạy agent**. Chạy agent trên dữ liệu không đủ chỉ
tốn token để nhận kết luận sai.

---

## 6. QUY TẮC R6 — THỰC THI Ở TẦNG SCHEMA

Đây là ranh giới đạo đức, và nó phải nằm trong **code**, không phải trong lời hứa.

```python
FORBIDDEN_COLUMNS = {
    "author_name",       # tên thật -> tra ngược ra tài khoản
    "author_channel_id", # như trên
    "author_avatar",
}

def strip_pii(df: pd.DataFrame) -> pd.DataFrame:
    """Xoá cột định danh NGAY khi nạp, không đợi tới lúc xuất báo cáo."""
    drop = [c for c in df.columns if c in FORBIDDEN_COLUMNS]
    if drop:
        log.warning(f"Đã xoá {len(drop)} cột định danh: {drop}")
    return df.drop(columns=drop)


def hash_author(name: str, salt: str) -> str:
    """SHA-256 có muối. Muối lưu ngoài repo, không commit."""
    return hashlib.sha256((salt + name).encode()).hexdigest()[:16]
```

### Vì sao nghiêm ngặt

`comment_id` **tra ngược ra tài khoản thật qua YouTube API chỉ bằng một lời
gọi**. Ghép `comment_id` với thuộc tính sức khoẻ/hoàn cảnh rồi công bố = xuất
bản hồ sơ suy đoán về người thật.

Ba việc bị cấm tuyệt đối:

| Cấm | Vì sao |
|---|---|
| Suy đoán tuổi/sắc tộc/tôn giáo từ tên hoặc ảnh | Sai và xâm phạm |
| Ghép tên thật với thuộc tính sức khoẻ | Thành hồ sơ suy đoán |
| Công bố quote kèm `comment_id` thật | Tra ngược được |

Chỉ ghi nhận thuộc tính khi người ta **tự khai công khai trong nội dung comment**.

---

## 7. CẤU TRÚC THƯ MỤC

```
data/
└── <ngách>/
    ├── raw/                    ← BẤT BIẾN, không bao giờ sửa
    │   ├── channels.xlsx
    │   ├── videos.xlsx
    │   └── comments.xlsx
    ├── processed/              ← sinh từ raw, xoá được, tái tạo được
    │   ├── channels.parquet
    │   ├── videos.parquet
    │   ├── video_stats.parquet
    │   ├── comments.parquet
    │   └── videos_enriched.parquet
    └── meta.json               ← ngày crawl, nguồn, phiên bản schema
```

`meta.json`:

```json
{
  "niche": "christian-blues",
  "crawl_date": "2026-08-13",
  "schema_version": "1.0",
  "source": "YouTube Data API v3",
  "source_class": "Y",
  "n_channels": 53,
  "n_videos": 7193,
  "n_comments": 145150,
  "snapshots": 1,
  "caveats": ["chỉ 1 snapshot -> mọi chỉ số dạng cumsum đều vô nghĩa"]
}
```

Trường `caveats` được **agent đọc vào context** — nó cần biết dữ liệu yếu chỗ nào.

---

## 8. CODE KHUNG

```python
# m1_data_contract.py
from dataclasses import dataclass
import pandas as pd, numpy as np, hashlib, json, logging

log = logging.getLogger(__name__)

@dataclass
class NicheData:
    """Đối tượng duy nhất mà mọi tool phía sau nhận vào."""
    channels: pd.DataFrame
    videos: pd.DataFrame          # đã enrich
    stats: pd.DataFrame
    comments: pd.DataFrame
    meta: dict

    @property
    def matured(self) -> pd.DataFrame:
        """Chỉ video đã chín — dùng cho MỌI so sánh hiệu quả."""
        return self.videos[self.videos.is_matured]


def load(niche_dir: str) -> NicheData:
    p = pathlib.Path(niche_dir)
    meta = json.loads((p/"meta.json").read_text())
    crawl = pd.Timestamp(meta["crawl_date"], tz="UTC")

    ch = pd.read_parquet(p/"processed/channels.parquet")
    vd = pd.read_parquet(p/"processed/videos.parquet")
    st = pd.read_parquet(p/"processed/video_stats.parquet")
    cm = strip_pii(pd.read_parquet(p/"processed/comments.parquet"))

    vd = enrich(vd, st, crawl)

    errs = validate(ch, vd, st, cm)
    if errs:
        raise ValueError(f"Dữ liệu không đạt {len(errs)} kiểm: {errs}")

    return NicheData(ch, vd, st, cm, meta)
```

---

## 9. NGHIỆM THU M1

```
□ Nạp được ngách christian-blues, validator không báo lỗi
□ Nạp được MỘT ngách khác (dù nhỏ) vào cùng schema
□ 4 cột suy ra sinh đúng, đối chiếu tay 10 dòng
□ strip_pii() xoá thật, kiểm bằng cách cố tình đưa author_name vào
□ Validator CHẶN được dữ liệu thiếu (thử xoá bớt kênh còn 5)
□ meta.json có đủ caveats
```

> **Phép thử quyết định:** tạo một thư mục ngách **trống hoàn toàn**, đặt dữ
> liệu mới vào, chạy `load()`. Nếu chạy được thì M1 xong. Nếu phải sửa code
> mới chạy được thì chưa xong — và bạn vừa tránh được lỗi sẽ tốn hàng tuần
> phát hiện về sau.
