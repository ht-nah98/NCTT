# M2 · TOOL LAYER

> ~20 tool tất định. Agent gọi, không tự tính. Đây là module tốn công nhất
> nhưng cũng là thứ giữ cho hệ thống đáng tin.
>
> **Xong khi:** 20 tool có test, gọi được bằng JSON, cùng input luôn ra cùng output.

---

## 1. NGUYÊN TẮC THIẾT KẾ TOOL

| # | Nguyên tắc | Vì sao |
|---|---|---|
| T1 | **Tất định** — cùng input luôn ra cùng output | agent chạy lại phải ra cùng số |
| T2 | **Tự khai giới hạn** trong output | agent cần biết khi nào không tin được |
| T3 | **Không bao giờ trả về `None` im lặng** | trả `{"error": "...", "reason": "..."}` |
| T4 | **Kèm cỡ mẫu** trong mọi kết quả | agent phải biết n để quyết định |
| T5 | **Ngưỡng phán quyết nằm trong tool**, không trong prompt | agent không được đổi luật chơi |

### T2 quan trọng nhất — ví dụ

```python
# ❌ Tool trả về số trần trụi
{"lift": 8.1, "p": 0.0003}
# -> agent sẽ kết luận "rất mạnh!" và nó SAI

# ✅ Tool tự khai giới hạn
{
  "lift": 8.1, "p": 0.0003, "n": 44,
  "within_channel": {"n_channels": 13, "n_better": 6, "median_lift": 0.94},
  "verdict": "BÁC BỎ (Simpson)",
  "warning": "hiệu ứng KHÔNG nhất quán trong từng kênh — 6/13 kênh ngược chiều",
  "market_lift": 0.48
}
```

Tool thứ hai khiến agent **không thể** kết luận sai, vì cảnh báo nằm ngay
trong dữ liệu nó đọc.

---

## 2. DANH MỤC 20 TOOL

### Nhóm A · Khảo sát (agent A1 dùng)

| Tool | Trả về |
|---|---|
| `describe_niche()` | tổng quan: n kênh, n video, khoảng thời gian, caveats |
| `market_size()` | view/tháng, trung vị, phân bố |
| `demand_supply_gap()` | M2.4 + cảnh báo maturation |
| `channel_concentration()` | Gini, top1/top5/top20% share |
| `newcomer_success()` | tỷ lệ kênh trẻ đạt ngưỡng + cảnh báo survivorship |

### Nhóm B · Lọc mẫu (agent A2 dùng)

| Tool | Trả về |
|---|---|
| `select_videos(strategy)` | 4 rổ B1–B4, kèm 5 kiểm chứng phủ mẫu |
| `select_comments(tiers)` | 3 tầng C1–C3 |
| `sample_check()` | mẫu có lệch không |

### Nhóm C · Kiểm định (agent A2 + A3 dùng) — **quan trọng nhất**

| Tool | Trả về |
|---|---|
| `test_title_theme(pattern)` | lift + p + **kiểm Simpson** + verdict |
| `test_comment_signal(pattern)` | like lift so nền + p + verdict |
| `test_binary_feature(col)` | so B1 vs B4 + 3 lớp |
| `test_correlation(x, y)` | Spearman + **kiểm theo kênh** |
| `compare_groups(a, b, metric)` | Mann-Whitney + Cliff's delta |

### Nhóm D · Đo lường (agent A2 dùng)

| Tool | Trả về |
|---|---|
| `vocab_gap()` | từ trong comment vs trong tiêu đề |
| `listening_context()` | phân bố bối cảnh nghe |
| `production_norms()` | nhịp đăng, độ dài, format |
| `audio_spec()` | BPM, LUFS, điệu thức (nếu có dữ liệu) |

### Nhóm E · Xuất (agent A5 dùng)

| Tool | Trả về |
|---|---|
| `make_chart(spec)` | đường dẫn file PNG |
| `render_document(doc_id, blocks)` | đường dẫn file PDF |
| `cite(metric_key)` | mã nguồn + cỡ mẫu cho một chỉ số |

---

## 3. TOOL LÕI — CODE ĐẦY ĐỦ

Đây là tool quan trọng nhất toàn hệ thống. Viết đúng cái này là xong 60% M2.

```python
# tools/test_title_theme.py
from scipy import stats
import numpy as np, pandas as pd

SCHEMA = {
    "name": "test_title_theme",
    "description": (
        "Kiểm định xem một chủ đề trong TIÊU ĐỀ có liên quan tới hiệu quả "
        "video không. Tự động kiểm nghịch lý Simpson trong từng kênh. "
        "Dùng khi muốn biết 'làm chủ đề X có ăn không'."),
    "input_schema": {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Regex tìm trong tiêu đề, ví dụ: "
                               r"'\\bthank(?:ful|s)?\\b|\\bgrateful\\b'"},
            "label": {"type": "string", "description": "Tên chủ đề để hiển thị"}
        },
        "required": ["pattern", "label"]
    }
}


def test_title_theme(data, pattern: str, label: str) -> dict:
    # CHỈ dùng video đã chín — bẫy L1
    m = data.matured.copy()
    m["hit"] = m.title.astype(str).str.lower().str.contains(pattern, regex=True)

    a, b = m[m.hit], m[~m.hit]

    # T3: không trả None im lặng
    if len(a) < 20:
        return {"error": "KHÔNG ĐỦ MẪU", "n": int(len(a)),
                "reason": f"chỉ {len(a)} video khớp, cần ≥20 để kiểm định",
                "suggestion": "nới regex hoặc bỏ chủ đề này"}

    # ── LỚP 1: trong toàn mẫu ────────────────────────────────────────
    p    = float(stats.mannwhitneyu(a.vpd.dropna(), b.vpd.dropna()).pvalue)
    lift = float(a.vpd.median() / b.vpd.median())

    # ── LỚP 3: trong TỪNG KÊNH — chống Simpson ───────────────────────
    wc = []
    for _, g in m.groupby("channel_id"):
        if g.hit.sum() >= 5 and (~g.hit).sum() >= 5:
            vb = g[~g.hit].vpd.median()
            if vb > 0:
                wc.append(g[g.hit].vpd.median() / vb)

    within = float(np.median(wc)) if wc else None
    n_better = int(sum(1 for x in wc if x > 1))

    # ── PHÁN QUYẾT — thứ tự QUAN TRỌNG, Simpson trước lift ───────────
    if p >= 0.05:
        verdict, why = "BÁC BỎ", "p ≥ 0,05 — không có ý nghĩa thống kê"
    elif len(wc) >= 5 and within < 1:
        verdict, why = ("BÁC BỎ (Simpson)",
                        f"p nhỏ nhưng chỉ {n_better}/{len(wc)} kênh cùng chiều "
                        f"— hiệu ứng là ảo giác do gộp kênh")
    elif lift >= 1.3 and (len(wc) < 5 or within >= 1.1):
        verdict, why = "XÁC NHẬN", "qua cả 3 lớp kiểm"
    elif lift >= 1.15:
        verdict, why = "YẾU", "có tín hiệu nhưng lift thấp"
    elif lift <= 0.8:
        verdict, why = "TRÁNH", "hiệu quả thấp hơn mặt bằng rõ rệt"
    else:
        verdict, why = "BÁC BỎ", "lift không đủ lớn"

    out = {
        "label": label, "verdict": verdict, "why": why,
        "n": int(len(a)), "share_pct": round(len(a)/len(m)*100, 2),
        "lift": round(lift, 3), "p": p,
        "within_channel": {
            "n_channels_tested": len(wc),
            "n_channels_better": n_better,
            "median_lift": round(within, 3) if within else None},
        "source_class": "Y",
    }

    # T2: tự khai giới hạn
    if len(wc) < 5:
        out["warning"] = (f"chỉ {len(wc)} kênh đủ mẫu để kiểm Simpson — "
                          "chưa loại trừ được hiệu ứng gộp kênh")
    if within and lift/within > 1.5:
        out["warning"] = (f"lift thô ({lift:.2f}) cao hơn nhiều lift trong-kênh "
                          f"({within:.2f}) — phần lớn hiệu ứng đến từ KÊNH nào làm, "
                          "không phải từ chủ đề")
    return out
```

### Ba chi tiết quyết định chất lượng

**① `data.matured`, không phải `data.videos`** — quên chỗ này là mắc bẫy L1,
kết luận đảo ngược.

**② Simpson kiểm TRƯỚC lift** — một chủ đề lift 2,4× vẫn phải bị bác nếu không
thắng trong từng kênh.

**③ Trường `warning` viết bằng câu người đọc được** — agent đọc câu này và
đưa nguyên vào báo cáo được.

---

## 4. TOOL KIỂM TÍN HIỆU BÌNH LUẬN

```python
def test_comment_signal(data, pattern: str, label: str) -> dict:
    """Tín hiệu này có được NGƯỜI KHÁC ĐỒNG TÌNH không?

    Khác test_title_theme: đo bằng LIKE, không đo bằng view.
    Lý do: like đo 'người khác đọc và gật đầu', tần suất chỉ đo 'có người nói'.
    """
    c = data.comments
    c = c[c.text.str.len() >= 15]                     # bỏ "Amen", emoji
    hit = c[c.text.str.lower().str.contains(pattern, regex=True)]

    if len(hit) < 30:
        return {"error": "KHÔNG ĐỦ MẪU", "n": len(hit),
                "reason": "n < 30, không kết luận được"}

    baseline = c.like_count.median()
    med      = hit.like_count.median()
    p = float(stats.mannwhitneyu(hit.like_count,
                                 c[~c.index.isin(hit.index)].like_count).pvalue)

    return {
        "label": label,
        "n": int(len(hit)),
        "freq_pct": round(len(hit)/len(c)*100, 2),
        "like_median": float(med),
        "baseline_like": float(baseline),
        "vs_baseline": round(med/baseline, 2),
        "p": p,
        "verdict": ("XÁC NHẬN" if p < 0.01 and med/baseline >= 3
                    else "YẾU" if p < 0.05 and med/baseline >= 1.5
                    else "BÁC BỎ"),
        "note": ("Tần suất đo 'người ta nói gì'; like đo 'người khác có thấy "
                 "đúng không'. Hai thứ khác nhau."),
        "source_class": "Y",
    }
```

### Ví dụ vì sao tool này cần thiết

| Tín hiệu | n | freq | like trung vị | vs nền | Verdict |
|---|---|---|---|---|---|
| `healing` | 757 | 11,8% | 3,0 | **0,8×** | BÁC BỎ |
| `finally` | 58 | 0,9% | 26,5 | **6,6×** | XÁC NHẬN |

`healing` xuất hiện **nhiều gấp 13 lần** nhưng không ai đồng tình đặc biệt.
Đếm từ khoá đơn thuần sẽ kết luận ngược.

---

## 5. TOOL CHỐNG ARTEFACT MẪU SỐ (bẫy L3)

```python
def test_correlation(data, x: str, y: str) -> dict:
    """Spearman + tự động cảnh báo artefact mẫu số.

    Bẫy L3: engagement_rate = (like+comment)/view cho hiệu ứng MẠNH NHẤT
    trong 26 đặc trưng — nhưng đó chỉ là toán học, vì nhóm thắng có view
    gấp 82 lần nhóm thua.
    """
    m = data.matured
    rho, p = stats.spearmanr(m[x], m[y], nan_policy="omit")

    out = {"x": x, "y": y, "rho": round(float(rho), 3), "p": float(p),
           "n": int(len(m)), "source_class": "Y"}

    # tự phát hiện tỷ lệ có view ở mẫu số
    RATIO_COLS = {"engagement_rate", "like_rate", "comment_rate"}
    if x in RATIO_COLS or y in RATIO_COLS:
        ratio_col = x if x in RATIO_COLS else y
        chk, _ = stats.spearmanr(m.view_count, m[ratio_col], nan_policy="omit")
        out["denominator_warning"] = (
            f"'{ratio_col}' có view ở mẫu số. Spearman(view, {ratio_col}) "
            f"= {chk:.3f}. Nếu âm mạnh thì tương quan này phần lớn là "
            f"ARTEFACT TOÁN HỌC, không phải phát hiện.")
        out["verdict_override"] = "CẦN KIỂM TAY"

    # kiểm trong từng kênh
    wc = [stats.spearmanr(g[x], g[y], nan_policy="omit")[0]
          for _, g in m.groupby("channel_id") if len(g) >= 15]
    wc = [r for r in wc if not np.isnan(r)]
    if wc:
        out["within_channel"] = {
            "n_channels": len(wc),
            "median_rho": round(float(np.median(wc)), 3),
            "n_same_sign": int(sum(1 for r in wc if np.sign(r) == np.sign(rho)))}
        if out["within_channel"]["n_same_sign"] < len(wc) * 0.6:
            out["warning"] = ("dấu tương quan KHÔNG nhất quán giữa các kênh "
                              "— nghi ngờ Simpson")
    return out
```

---

## 6. TOOL KHẢO SÁT — TỰ KHAI CAVEAT

```python
def describe_niche(data) -> dict:
    """Tổng quan + MỌI giới hạn đã biết. Agent A1 đọc đầu tiên."""
    v, m = data.videos, data.matured
    caveats = list(data.meta.get("caveats", []))

    if data.meta.get("snapshots", 1) < 2:
        caveats.append(
            "Chỉ 1 snapshot: mọi chỉ số dạng 'thời gian đạt X view' đều VÔ NGHĨA "
            "(bẫy L5). Không được báo cáo chúng.")

    if v.channel_id.nunique() < 20:
        caveats.append(
            f"Chỉ {v.channel_id.nunique()} kênh — kiểm Simpson sẽ yếu.")

    caveats.append(
        "Dữ liệu chỉ chứa kênh CÒN TỒN TẠI. Kênh đã thất bại và bị xoá không "
        "xuất hiện -> mọi tỷ lệ thành công đều CAO HƠN thực tế (bẫy L4).")

    return {
        "niche": data.meta["niche"],
        "n_channels": int(v.channel_id.nunique()),
        "n_videos": int(len(v)),
        "n_matured": int(len(m)),
        "matured_pct": round(len(m)/len(v)*100, 1),
        "n_comments": int(len(data.comments)),
        "date_range": [str(v.published_at.min().date()),
                       str(v.published_at.max().date())],
        "crawl_date": data.meta["crawl_date"],
        "source_class": data.meta.get("source_class", "Y"),
        "caveats": caveats,
    }
```

> **Đây là tool đầu tiên agent gọi**, và `caveats` đi thẳng vào context. Agent
> biết dữ liệu yếu chỗ nào **trước khi** bắt đầu phân tích.

---

## 7. ĐĂNG KÝ TOOL CHO AGENT

```python
# tools/registry.py
TOOLS = {}

def register(schema):
    def deco(fn):
        TOOLS[schema["name"]] = {"schema": schema, "fn": fn}
        return fn
    return deco

def get_schemas(group: str = None) -> list:
    """Trả schema cho agent. Lọc theo nhóm để không nạp thừa vào context."""
    return [t["schema"] for name, t in TOOLS.items()
            if group is None or t["schema"].get("group") == group]

def call(name: str, data, **kwargs) -> dict:
    """Gọi tool + ghi trace. MỌI lời gọi đều được ghi lại."""
    if name not in TOOLS:
        return {"error": f"tool '{name}' không tồn tại",
                "available": list(TOOLS)}
    try:
        result = TOOLS[name]["fn"](data, **kwargs)
    except Exception as e:
        result = {"error": type(e).__name__, "detail": str(e)[:300]}

    trace.append({"tool": name, "args": kwargs, "result": result})
    return result
```

**Vì sao lọc theo nhóm:** nạp cả 20 schema vào context của mọi agent là lãng
phí token và làm agent phân tâm. A1 chỉ cần nhóm A, A5 chỉ cần nhóm E.

---

## 8. TEST BẮT BUỘC CHO MỖI TOOL

```python
def test_tất_định():
    """T1: cùng input -> cùng output."""
    r1 = test_title_theme(data, r"\bthank", "cảm tạ")
    r2 = test_title_theme(data, r"\bthank", "cảm tạ")
    assert r1 == r2

def test_bắt_được_simpson():
    """Dữ liệu giả: lift thô cao nhưng trong kênh thấp -> phải BÁC BỎ."""
    fake = make_simpson_trap()
    assert test_title_theme(fake, r"\btrap", "bẫy")["verdict"] == "BÁC BỎ (Simpson)"

def test_mẫu_nhỏ_không_kết_luận():
    r = test_title_theme(data, r"\bxyzabc_không_tồn_tại", "hiếm")
    assert "error" in r and r["error"] == "KHÔNG ĐỦ MẪU"

def test_chỉ_dùng_video_đã_chín():
    """Bẫy L1: kết quả không được đổi khi thêm video mới toanh."""
    r1 = test_title_theme(data, r"\bthank", "x")
    r2 = test_title_theme(add_fresh_videos(data), r"\bthank", "x")
    assert r1["lift"] == r2["lift"]
```

Test thứ hai và thứ tư là **quan trọng nhất** — chúng kiểm rằng tool tránh
được hai bẫy đã từng đảo ngược kết luận trong thực tế.

---

## 9. NGHIỆM THU M2

```
□ 20 tool đã viết, mỗi tool có schema JSON hợp lệ
□ Mỗi tool có ≥3 test, trong đó bắt buộc: tất định · mẫu nhỏ · bẫy Simpson
□ Không tool nào trả None im lặng
□ Mọi output có "n" và "source_class"
□ Tool kiểm định có "within_channel" và "warning" khi cần
□ registry.call() ghi trace đầy đủ
□ Gọi thử toàn bộ 20 tool bằng JSON thuần, không lỗi
```

> **Phép thử quyết định:** dựng một bộ dữ liệu giả có **bẫy Simpson cài sẵn**
> (chủ đề X thắng đậm ở 2 kênh lớn, thua ở 11 kênh nhỏ). Nếu `test_title_theme`
> trả về `BÁC BỎ (Simpson)` thì tool layer đã đủ tin cậy để thả agent vào.
