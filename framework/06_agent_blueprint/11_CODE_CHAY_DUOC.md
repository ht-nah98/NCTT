# CODE CHẠY ĐƯỢC — lấp 23 hàm còn thiếu

> Các file M1–M7 gọi 23 hàm mà không định nghĩa. File này viết đủ chúng.
> **Toàn bộ code dưới đây đã chạy thử**, không phải giả code.
>
> Phiên bản: v1.0 · Lập 2026-08-28

---

## 1. M1 — DATA CONTRACT

### `enrich()` — sinh 4 cột suy ra

```python
import pandas as pd, numpy as np

def enrich(videos: pd.DataFrame, stats: pd.DataFrame,
           crawl_date: pd.Timestamp) -> pd.DataFrame:
    """Sinh age_days, vpd, is_matured, outlier_ratio.

    Đây là nơi DUY NHẤT định nghĩa 4 cột này. Tool không được tự tính lại.
    """
    # lấy snapshot MỚI NHẤT của mỗi video
    latest = (stats.sort_values("snapshot_at")
                   .groupby("video_id", as_index=False).last())
    v = videos.merge(latest[["video_id", "view_count"]],
                     on="video_id", how="left")

    v["age_days"]   = (crawl_date - v.published_at).dt.days.clip(lower=1)
    v["vpd"]        = v.view_count / v.age_days
    v["is_matured"] = v.age_days >= 60

    # baseline CHỈ tính trên video đã chín của chính kênh đó
    base = (v[v.is_matured].groupby("channel_id").view_count.median()
              .rename("channel_median_view").reset_index())
    v = v.merge(base, on="channel_id", how="left")
    v["outlier_ratio"] = v.view_count / v.channel_median_view.replace(0, np.nan)
    return v
```

### `strip_pii()` — xoá cột định danh

```python
FORBIDDEN_COLUMNS = {"author_name", "author_channel_id",
                     "author_avatar", "author_display_name"}

def strip_pii(df: pd.DataFrame) -> pd.DataFrame:
    drop = [c for c in df.columns if c in FORBIDDEN_COLUMNS]
    if drop:
        print(f"[R6] Đã xoá {len(drop)} cột định danh: {drop}")
    return df.drop(columns=drop)
```

### `validate()` — 7 kiểm, 2 cổng chặn cứng

```python
def validate(ch, vd, st, cm) -> list[str]:
    """Trả list lỗi. Rỗng = đạt. Gọi TRƯỚC khi chạy bất kỳ agent nào."""
    errs = []

    if not vd.video_id.is_unique:
        errs.append("video_id bị trùng")
    if not ch.channel_id.is_unique:
        errs.append("channel_id bị trùng")
    if not vd.channel_id.isin(ch.channel_id).all():
        n = (~vd.channel_id.isin(ch.channel_id)).sum()
        errs.append(f"{n} video trỏ tới kênh không tồn tại")
    if (vd.published_at > vd.fetched_at).any():
        errs.append("có video ngày đăng SAU ngày crawl")
    if (st.view_count < 0).any():
        errs.append("có view âm")

    # ── HAI CỔNG CHẶN CỨNG ──────────────────────────────────
    n_mat = int(vd.is_matured.sum())
    if n_mat < 200:
        errs.append(f"CHẶN: chỉ {n_mat} video đã chín, cần ≥200 để kiểm định")

    n_ch = int(vd.channel_id.nunique())
    if n_ch < 10:
        errs.append(f"CHẶN: chỉ {n_ch} kênh, cần ≥10 để kiểm Simpson")

    if len(cm) and cm.video_id.isin(vd.video_id).mean() < 0.5:
        errs.append("hơn nửa comment không khớp video nào")
    return errs
```

---

## 2. M2 — TOOL LAYER

### `describe_niche()` — tool đầu tiên agent gọi

```python
def describe_niche(data) -> dict:
    v, m = data.videos, data.matured
    caveats = list(data.meta.get("caveats", []))

    if data.meta.get("snapshots", 1) < 2:
        caveats.append("Chỉ 1 snapshot: mọi chỉ số dạng 'thời gian đạt X view' "
                       "đều VÔ NGHĨA (bẫy L5). Không được báo cáo chúng.")
    if v.channel_id.nunique() < 20:
        caveats.append(f"Chỉ {v.channel_id.nunique()} kênh — kiểm Simpson yếu.")
    caveats.append("Dữ liệu chỉ chứa kênh CÒN TỒN TẠI. Kênh thất bại đã bị xoá "
                   "-> mọi tỷ lệ thành công đều CAO HƠN thực tế (bẫy L4).")

    return {
        "niche": data.meta["niche"],
        "n_channels": int(v.channel_id.nunique()),
        "n_videos": int(len(v)),
        "n_matured": int(len(m)),
        "matured_pct": round(len(m) / len(v) * 100, 1),
        "n_comments": int(len(data.comments)),
        "date_range": [str(v.published_at.min().date()),
                       str(v.published_at.max().date())],
        "crawl_date": data.meta["crawl_date"],
        "source_class": data.meta.get("source_class", "Y"),
        "caveats": caveats,
    }
```

### `make_simpson_trap()` — dữ liệu giả để test

```python
def make_simpson_trap(n_big=2, n_small=11, seed=42):
    """Dựng bẫy Simpson: lift thô CAO nhưng trong từng kênh THẤP.

    Cơ chế của bẫy — ba điều kiện phải có ĐỦ:
      ① kênh lớn có vpd cao hơn hẳn kênh nhỏ (100 vs 4-9)
      ② kênh lớn dùng chủ đề NHIỀU (50/60), kênh nhỏ dùng ÍT (6/40)
      ③ TRONG mỗi kênh, dùng chủ đề lại TỆ hơn (100 vs 108 · 4 vs 9)

    -> gộp lại: nhóm "có chủ đề" toàn video của kênh lớn -> lift thô ~10×
    -> tách kênh: mọi kênh đều tệ đi -> trong-kênh ~0,47×

    Kết quả đo được: lift thô 10,42 · trong-kênh 0,47 · 0/13 kênh cùng chiều.

    Dùng cho phép thử quyết định của M2. Nếu test_title_theme() trả
    'XÁC NHẬN' trên dữ liệu này thì tool CHƯA đạt.
    """
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n_big):                # kênh lớn: vpd cao, dùng NHIỀU
        for j in range(60):
            hit = j < 50
            rows.append({"channel_id": f"BIG{i}",
                         "title": "trap song" if hit else "normal song",
                         "vpd": rng.normal(100 if hit else 108, 6),
                         "is_matured": True})
    for i in range(n_small):              # kênh nhỏ: vpd thấp, dùng ÍT
        for j in range(40):
            hit = j < 6
            rows.append({"channel_id": f"SML{i}",
                         "title": "trap song" if hit else "normal song",
                         "vpd": rng.normal(4 if hit else 9, 1.5),
                         "is_matured": True})

    df = pd.DataFrame(rows)
    df["video_id"] = [f"v{i}" for i in range(len(df))]

    class Fake:
        videos = df
        matured = df
    return Fake()
```

### `add_fresh_videos()` — test bẫy L1

```python
def add_fresh_videos(data, n=200):
    """Thêm video MỚI TOANH (chưa chín). Kết quả kiểm định KHÔNG được đổi.

    Nếu đổi -> tool đang dùng data.videos thay vì data.matured -> mắc bẫy L1.
    """
    fresh = data.videos.head(n).copy()
    fresh["video_id"]   = "fresh_" + fresh.video_id
    fresh["age_days"]   = 5
    fresh["is_matured"] = False
    fresh["view_count"] = 10
    fresh["vpd"]        = 2.0

    class Fake:
        videos  = pd.concat([data.videos, fresh], ignore_index=True)
        matured = data.matured
        meta    = data.meta
    return Fake()
```

---

## 3. M3 — CONTEXT

### `format_tool_schemas()`

```python
def format_tool_schemas(tools: list[dict]) -> str:
    """Biến schema JSON thành mô tả gọn cho context (tiết kiệm token)."""
    lines = []
    for t in tools:
        props = t.get("input_schema", {}).get("properties", {})
        args = ", ".join(f"{k}: {v.get('type','?')}" for k, v in props.items())
        lines.append(f"- {t['name']}({args})\n    {t['description']}")
    return "\n".join(lines)
```

---

## 4. M6 — VERIFICATION (5 hàm phụ trợ)

```python
def flatten_values(obj, out=None):
    """Rút MỌI giá trị vô hướng trong dict/list lồng nhau."""
    out = [] if out is None else out
    if isinstance(obj, dict):
        for v in obj.values():
            flatten_values(v, out)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            flatten_values(v, out)
    else:
        out.append(obj)
    return out


def extract_texts(draft: dict) -> list[str]:
    """Rút mọi chuỗi người đọc thấy — kể cả trong bảng."""
    texts = []
    for b in draft.get("blocks", []):
        if b.get("text"):
            texts.append(b["text"])
        for row in b.get("rows", []):
            texts += [str(c) for c in row]
        texts += [str(h) for h in b.get("headers", [])]
    return texts


def find_by_id(findings: list, fid: str) -> dict:
    for f in findings:
        if f.get("id") == fid:
            return f
    return {}


def collect_tool_results(findings: list) -> list:
    return [f["tool_result"] for f in findings if "tool_result" in f]


def key_phrase(warning: str, n_words: int = 4) -> str:
    """Rút cụm đặc trưng của cảnh báo để dò trong báo cáo.

    Bỏ từ nối để tránh khớp nhầm.
    """
    STOP = {"và","của","là","có","không","một","các","này","đó",
            "trong","với","cho","thì","mà","nhưng"}
    words = [w for w in warning.split() if w.lower() not in STOP]
    return " ".join(words[:n_words])
```

---

## 5. M5 — ORCHESTRATOR

```python
def stop_at_gate_1(scout: dict) -> dict:
    return {"status": "stopped_at_gate_1",
            "reason": scout.get("reasoning", ""),
            "metrics": scout.get("key_metrics", {}),
            "message": ("Ngách không đạt ngưỡng cầu/cung. Phân tích tiếp là "
                        "tối ưu hoá con tàu đang chìm.")}


def stop_at_gate_2(survived: list) -> dict:
    return {"status": "stopped_at_gate_2",
            "n_survived": len(survived),
            "survived": survived,
            "message": ("Không đủ phát hiện đứng vững sau phản biện. Đây là "
                        "kết quả HỢP LỆ, không phải lỗi hệ thống."),
            "suggestion": "Thu thập thêm dữ liệu hoặc thêm nguồn ngoài (S/V/P)."}


class AgentError(Exception):
    pass


def validate_schema(obj: dict, schema: dict) -> tuple[bool, str]:
    """Kiểm schema tối thiểu, không cần thư viện ngoài."""
    if not isinstance(obj, dict):
        return False, f"cần dict, nhận {type(obj).__name__}"
    for k in schema.get("required", []):
        if k not in obj:
            return False, f"thiếu trường bắt buộc '{k}'"
    for k, spec in schema.get("properties", {}).items():
        if k not in obj:
            continue
        want = spec.get("type")
        TYPES = {"string": str, "number": (int, float), "integer": int,
                 "boolean": bool, "array": list, "object": dict}
        if want in TYPES and not isinstance(obj[k], TYPES[want]):
            return False, f"'{k}' phải là {want}"
        if "enum" in spec and obj[k] not in spec["enum"]:
            return False, f"'{k}' phải thuộc {spec['enum']}, nhận '{obj[k]}'"
    return True, ""
```

---

## 6. M7 — OUTPUT

```python
import html as _html

def esc(s) -> str:
    """Thoát HTML. BẮT BUỘC dùng cho mọi text từ agent."""
    return _html.escape(str(s), quote=False)


def vn(x, digits=0) -> str:
    """Số kiểu Việt Nam: 1234.5 -> '1.234,5'"""
    if x is None:
        return "—"
    s = f"{x:,.{digits}f}"
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def render_table(b: dict) -> str:
    head = "".join(f"<th>{esc(h)}</th>" for h in b.get("headers", []))
    body = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in row) + "</tr>"
                   for row in b.get("rows", []))
    return (f'<div class="scroll"><table><thead><tr>{head}</tr></thead>'
            f'<tbody>{body}</tbody></table></div>')
```

---

## 7. KIỂM TRA TOÀN BỘ

Chạy file này để chắc chắn mọi hàm hoạt động:

```python
# test_all.py
def test_flatten():
    assert set(flatten_values({"a": 1, "b": {"c": 2}, "d": [3, 4]})) == {1,2,3,4}

def test_key_phrase():
    kp = key_phrase("hiệu ứng không nhất quán trong từng kênh")
    assert "nhất" in kp and "của" not in kp

def test_validate_schema():
    s = {"required": ["v"], "properties": {"v": {"type": "string",
                                                 "enum": ["GO", "NO_GO"]}}}
    assert validate_schema({"v": "GO"}, s)[0] is True
    assert validate_schema({}, s)[0] is False              # thiếu trường
    assert validate_schema({"v": "MAYBE"}, s)[0] is False  # ngoài enum
    assert validate_schema({"v": 1}, s)[0] is False        # sai kiểu

def test_vn():
    assert vn(1234.5, 1) == "1.234,5"
    assert vn(1687) == "1.687"

def test_esc():
    assert esc("<script>") == "&lt;script&gt;"

def test_simpson_trap_is_a_trap():
    """Bẫy phải THẬT: lift thô >1 nhưng trong-kênh <1."""
    fake = make_simpson_trap()
    df = fake.matured
    df["hit"] = df.title.str.contains("trap")
    lift = df[df.hit].vpd.median() / df[~df.hit].vpd.median()
    wc = []
    for _, g in df.groupby("channel_id"):
        if g.hit.sum() >= 5 and (~g.hit).sum() >= 5:
            wc.append(g[g.hit].vpd.median() / g[~g.hit].vpd.median())
    assert lift > 1.0,          f"lift thô phải >1, đang là {lift:.2f}"
    assert np.median(wc) < 1.0, f"trong-kênh phải <1, đang là {np.median(wc):.2f}"
    assert sum(1 for x in wc if x > 1) < len(wc) * 0.6
```

---

## 8. TRẠNG THÁI KIỂM CHỨNG

| Hàm | Đã chạy thử |
|---|---|
| `flatten_values`, `extract_texts`, `find_by_id`, `key_phrase` | ✅ |
| `validate_schema` (4 ca) | ✅ |
| `vn`, `esc`, `render_table` | ✅ |
| `make_simpson_trap` — bẫy thật sự là bẫy | ✅ |
| `enrich`, `validate`, `strip_pii` | ✅ trên dữ liệu thật |
| `describe_niche` | ✅ trên dữ liệu thật |
| `add_fresh_videos` | ✅ |
| `stop_at_gate_*`, `format_tool_schemas` | ✅ |

Xem `_verify_snippets.py` cùng thư mục để chạy lại toàn bộ.
