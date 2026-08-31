# BẮT ĐẦU TỪ ĐÂU — dành cho người mới làm AI agent

> Blueprint M1–M7 mô tả **hệ thống hoàn chỉnh**. File này nói **ngày đầu tiên
> làm gì**, và thứ tự để không bị choáng.
>
> Phiên bản: v1.0 · Lập 2026-08-28

---

## 1. ĐỪNG XÂY AGENT TRƯỚC

Sai lầm phổ biến nhất: đọc xong blueprint rồi mở editor viết `agent.py`.

**Vấn đề:** bạn chưa biết đầu ra ĐÚNG trông thế nào. Agent chạy ra một bảng số
— bạn không có gì để đối chiếu xem nó đúng hay bịa.

### Thứ tự đúng

```
TUẦN 0  ·  làm THỦ CÔNG một ngách, không dùng AI
              ↓ giờ bạn có "đáp án" để đối chiếu
TUẦN 1  ·  M1 + vài tool nhóm C
              ↓ tool trả ra đúng số bạn đã tính tay
TUẦN 2  ·  M6 Verification + "hello world" agent
              ↓ có lưới bắt bịa, biết vòng lặp chạy
TUẦN 3+ ·  A2 + A3, rồi mở rộng
```

---

## 2. TUẦN 0 — LÀM TAY, KHÔNG DÙNG AI

Mục tiêu: tự tay trả lời 5 câu hỏi trên **một** ngách. Dùng pandas thuần,
Jupyter cũng được.

### Câu 1 — Ngách lên hay xuống?

```python
import pandas as pd
v = pd.read_parquet("videos.parquet")
crawl = pd.Timestamp("2026-08-13", tz="UTC")
v["age_days"] = (crawl - v.published_at).dt.days.clip(lower=1)
v["is_matured"] = v.age_days >= 60

# CHỈ so hai cửa sổ ĐỀU đã chín — đây là bẫy L1
now  = v[(v.age_days >=  60) & (v.age_days <= 150)]
prev = v[(v.age_days >= 150) & (v.age_days <= 240)]

M2_1 = now.view_count.sum() / prev.view_count.sum()   # cầu
M2_2 = len(now) / len(prev)                            # cung
print(f"M2.4 = {M2_1/M2_2:.2f}")
```

**Tự kiểm:** tính lại **không** lọc `is_matured`. Nếu hai số khác nhau nhiều,
bạn vừa tự tay chứng kiến bẫy L1.

### Câu 2 — Video nào thắng, và so với cái gì?

```python
base = v[v.is_matured].groupby("channel_id").view_count.median()
v["outlier_ratio"] = v.view_count / v.channel_id.map(base)

B1 = v[(v.is_matured) & (v.outlier_ratio >= 5)  & (v.view_count >= 20000)]
B4 = v[(v.is_matured) & (v.outlier_ratio <= .2) & (v.view_count >= 500)]
print(f"thắng {len(B1)} · thua {len(B4)}")
```

**Tự kiểm:** nhìn 10 tiêu đề B1 và 10 tiêu đề B4. Bạn có đoán được cái nào
thắng không? Nếu không → đó chính là lý do cần thống kê.

### Câu 3 — Chủ đề nào ăn?

```python
from scipy import stats
m = v[v.is_matured].copy()
m["vpd"] = m.view_count / m.age_days

pattern = r"\bthank(?:ful|s|sgiving)?\b|\bgrateful\b|\bblessing"
m["hit"] = m.title.str.lower().str.contains(pattern)

lift = m[m.hit].vpd.median() / m[~m.hit].vpd.median()
p = stats.mannwhitneyu(m[m.hit].vpd, m[~m.hit].vpd).pvalue
print(f"lift {lift:.2f} · p {p:.4f}")

# LỚP 3 — đây là bước hầu hết người ta bỏ qua
wc = []
for _, g in m.groupby("channel_id"):
    if g.hit.sum() >= 5 and (~g.hit).sum() >= 5:
        wc.append(g[g.hit].vpd.median() / g[~g.hit].vpd.median())
import numpy as np
print(f"trong-kênh {np.median(wc):.2f} · {sum(x>1 for x in wc)}/{len(wc)} kênh")
```

**Tự kiểm:** chạy với `scripture` (`r"\bpsalm|\bscripture\b|\bbible\b"`). Bạn
sẽ thấy lift thô và lift trong-kênh nói **hai chuyện khác nhau**. Đó là Simpson.

### Câu 4 — Khán giả nói gì?

```python
c = pd.read_parquet("comments.parquet")
c = c[c.text.str.len() >= 15]
baseline = c.like_count.median()

for label, pat in [("finally", r"\bfinally\b|\bat last\b"),
                   ("healing", r"\bheal(?:ed|ing)?\b|\bcomfort")]:
    hit = c[c.text.str.lower().str.contains(pat)]
    print(f"{label:10} n={len(hit):5} like={hit.like_count.median():5.1f} "
          f"vs nền {baseline} -> {hit.like_count.median()/baseline:.1f}×")
```

**Tự kiểm:** `healing` xuất hiện nhiều gấp hàng chục lần `finally` nhưng like
không cao hơn nền. Đây là lúc bạn hiểu *"số lượng không phải sức mạnh"*.

> ⚠️ **Số bạn ra sẽ KHÁC số trong báo cáo chính thức — và đó là đúng.**
> Đoạn trên chạy trên **toàn bộ** comment (145.150 dòng, like trung vị 1).
> Hệ thống thật chạy trên **6.413 comment đã lọc 3 tầng** (like trung vị 4).
>
> | | toàn bộ | đã lọc |
> |---|---|---|
> | nền like | 1,0 | 4,0 |
> | `finally` | 2,0× nền | **6,6× nền** |
>
> Lọc không phải để tiết kiệm — nó **tăng tỷ lệ tín hiệu trên nhiễu**. Bỏ
> comment dưới 15 ký tự (loại "Amen", emoji) là bước quan trọng nhất. Đây
> chính là lý do M2 có tool `select_comments()`.

### Câu 5 — Khán giả và kênh có nói cùng thứ tiếng?

```python
from collections import Counter
import re
words_cmt = Counter(re.findall(r"\b[a-z']{3,}\b", " ".join(c.text.str.lower())))
words_ttl = Counter(re.findall(r"\b[a-z']{3,}\b", " ".join(v.title.str.lower())))

for w in ["amen","thank","blues","gospel"]:
    print(f"{w:10} comment {words_cmt[w]:6} · tiêu đề {words_ttl[w]:6} "
          f"· tỷ lệ {words_cmt[w]/max(words_ttl[w],1):.0f}×")
```

Kết quả trên toàn bộ comment:

```
amen     comment  39.486 · tiêu đề      5 · 7.897×
thank    comment  37.201 · tiêu đề     24 · 1.550×
blues    comment   5.582 · tiêu đề  6.623 ·     1×
```

Cùng một kết luận với báo cáo chính thức (446× trên mẫu đã lọc): **khán giả
nói "amen, thank", kênh đặt tên "blues, gospel"**. Tỷ lệ tuyệt đối khác nhau
tuỳ mẫu, nhưng **hướng thì giống** — đó là dấu hiệu phát hiện thật.

### Xong tuần 0 khi

```
□ Trả lời được 5 câu, có số cụ thể
□ Tự tay thấy bẫy L1 (M2.4 đổi khi lọc is_matured)
□ Tự tay thấy bẫy Simpson (lift thô vs trong-kênh)
□ Ghi 5 con số này ra giấy — đây là ĐÁP ÁN để đối chiếu agent
```

### Số tham chiếu — ngách Christian Blues

Nếu bạn chạy trên chính ngách này, kết quả phải xấp xỉ:

| Câu | Kết quả | Ghi chú |
|---|---|---|
| M2.4 | **1,29–1,30** | không lọc `is_matured` sẽ ra ~0,45 |
| B1 / B4 | **435 / ~160** | |
| `thanks` | lift **1,63** · trong-kênh **2,28** | trong-kênh CAO HƠN thô = hiệu ứng thật |
| `scripture` | lift **0,61** | chạy thử để thấy Simpson |
| `amen` gap | **hàng nghìn lần** | tuỳ mẫu lọc hay không |

> Không có tuần 0 thì bạn không có cách nào biết agent đúng hay sai.

---

## 3. BỘ MỒI — 30 MẪU REGEX ĐÃ KIỂM NGHIỆM

Blueprint bảo A2 *"sinh giả thuyết dạng regex"* nhưng không đưa mẫu nào. Đây
là bộ đã dùng thật trên ngách Christian Blues — đưa vào prompt A2 làm ví dụ.

### Chủ đề trong tiêu đề (16 mẫu)

```python
THEME = {
 "prayer":      r"\bpray(?:er|ing)?\b",
 "healing":     r"\bheal(?:ing|ed)?\b|\brestor",
 "peace_rest":  r"\bpeace\b|\brest\b|\bcalm\b|\bstill\b",
 "grace_mercy": r"\bgrace\b|\bmercy\b",
 "strength":    r"\bstrength\b|\bstrong\b|\bcourage\b",
 "hope_faith":  r"\bhope\b|\bfaith\b|\bbeliev",
 "sorrow_pain": r"\bsorrow\b|\bpain\b|\bbroken\b|\bweary\b|\btears?\b|\blonely\b",
 "morning":     r"\bmorning\b|\bsunrise\b|\bdawn\b",
 "night_sleep": r"\bnight\b|\bsleep\b|\bmidnight\b|\binsomnia\b",
 "thanks":      r"\bthank(?:ful|s|sgiving)?\b|\bgrateful\b|\bblessing",
 "deliverance": r"\bdeliver|\bfreedom\b|\bbreakthrough\b|\bvictory\b",
 "presence":    r"\bpresence\b|\bholy spirit\b|\banoint",
 "scripture":   r"\bpsalm|\bproverb|\bscripture\b|\bword of god\b|\bbible\b",
 "testimony":   r"\btestimony\b|\bstory\b|\bjourney\b",
 "old_school":  r"\bold(?:-| )school\b|\bvintage\b|\bclassic\b|\b19\d0s\b",
 "instrumental":r"\binstrumental\b|\bno lyrics\b|\bbackground\b|\bbgm\b",
}
```

### Tín hiệu trong bình luận (6 mẫu)

```python
PAIN = {
 "finally":     r"\bfinally\b|\bat last\b|\bbeen (?:looking|searching) for\b",
 "cant_stand":  r"\bcan'?t stand\b|\btired of\b|\bhate the lyrics\b",
 "never_heard": r"\bnever heard\b|\bnever found\b|\bfirst time i(?:'ve)? heard\b",
 "struggling":  r"\bstrugglin|\bgoing through\b|\bhard time\b|\bdark (?:place|time)\b",
 "better_than": r"\bbetter than\b|\bnothing (?:else )?compares\b",
 "healing":     r"\bheal(?:ed|ing|s)?\b|\bcomfort(?:ed|ing)?\b|\btears\b",
}
```

### Bối cảnh nghe (8 mẫu)

```python
CTX = {
 "driving":     r"\bdriv(?:e|ing)\b|\bin (?:my|the) (?:car|truck)\b|\bcommut",
 "housework":   r"\b(?:clean|cook|dishes|chores|housework)\b",
 "work":        r"\bat work\b|\bwhile (?:i )?work\b|\bon the job\b",
 "sleep_night": r"\b(?:fall(?:ing)? asleep|bedtime|at night|can'?t sleep)\b",
 "prayer_devo": r"\b(?:pray(?:er|ing)?|devotion|quiet time|bible study)\b",
 "morning":     r"\b(?:every )?morning\b|\bstart (?:my|the) day\b",
 "sick_hosp":   r"\b(?:hospital|chemo|cancer|surgery|in pain|hospice)\b",
 "grief":       r"\b(?:passed away|funeral|lost my|grie(?:f|ving))\b",
}
```

### Cách viết mẫu mới

| Quy tắc | Vì sao |
|---|---|
| Luôn dùng `\b` ở hai đầu | `\bpray\b` không khớp "prayer**s**pray" |
| Gộp biến thể bằng `(?:...)` | `heal(?:ing\|ed)?` bắt heal/healing/healed |
| Bắt cả cụm, không chỉ từ đơn | `"at last"` cùng nghĩa với `"finally"` |
| Tránh từ quá phổ biến | `\bgod\b` khớp 4.438 lần — vô dụng để phân biệt |
| Test trước khi dùng | `df.title.str.contains(pat).sum()` phải ≥20 |

---

## 4. "HELLO WORLD" CỦA AGENT

Trước khi ghép tool thật, chứng minh vòng lặp chạy:

```python
# hello_agent.py
import anthropic, json
client = anthropic.Anthropic()

TOOLS = [{
    "name": "get_number",
    "description": "Trả về một con số bí mật.",
    "input_schema": {"type": "object", "properties": {}},
}]

def runner(name, args):
    return {"number": 42}

messages = [{"role": "user", "content": "Gọi tool và cho tôi biết số đó."}]
for _ in range(5):
    r = client.messages.create(model="claude-sonnet-4-5", max_tokens=1000,
                               tools=TOOLS, messages=messages)
    messages.append({"role": "assistant", "content": r.content})
    if r.stop_reason != "tool_use":
        print("".join(b.text for b in r.content if b.type == "text"))
        break
    results = [{"type": "tool_result", "tool_use_id": b.id,
                "content": json.dumps(runner(b.name, b.input))}
               for b in r.content if b.type == "tool_use"]
    messages.append({"role": "user", "content": results})
```

Chạy ra `"Số đó là 42"` → vòng lặp đúng. **Làm được cái này rồi mới ghép tool thật.**

---

## 5. LỘ TRÌNH 4 TUẦN ĐẦU

### Tuần 1 — M1 + 3 tool

```
□ enrich(), strip_pii(), validate()   ← code sẵn ở 11_CODE_CHAY_DUOC.md
□ describe_niche()
□ test_title_theme()                  ← code sẵn ở 02_M2_TOOL_LAYER.md §3
□ test_comment_signal()
□ Gọi 3 tool bằng Python thuần, so với số tuần 0
```

**Xong khi:** tool trả ra **đúng** số bạn đã tính tay tuần 0.

### Tuần 2 — Verification + hello world

```
□ verify_numbers(), verify_min_sample(), verify_no_pii()
□ Bộ test đỏ 5 ca                     ← 06_M6_VERIFICATION.md §4
□ hello_agent.py chạy được
□ make_simpson_trap() -> test_title_theme() trả "BÁC BỎ (Simpson)"
```

**Xong khi:** test đỏ bắt được cả 5 ca bịa số.

### Tuần 3 — A2 Analyst

```
□ SYSTEM_A2 + SCHEMA_A2               ← 04_M4_AGENTS.md §2, 10_GOI_MODEL.md §7
□ force_json() với submit_result
□ Cho A2 chạy trên ngách tuần 0
```

**Xong khi:** A2 tự tìm ra được ít nhất **2 trong 5** phát hiện bạn tìm tay.

### Tuần 4 — A3 Skeptic

```
□ SYSTEM_A3 + SCHEMA_A3
□ Đưa A3 phát hiện có bẫy Simpson cài sẵn
□ Đo tỷ lệ giết
```

**Xong khi:** A3 giết được bẫy Simpson, tỷ lệ giết 30–50%.

> Hết tuần 4 bạn đã có **hệ thống sinh giả thuyết và tự phản biện** — phần khó
> và giá trị nhất. A1, A4, A5, M5, M7 làm dần được.

---

## 6. NĂM LỖI NGƯỜI MỚI HAY MẮC

| Lỗi | Triệu chứng | Sửa |
|---|---|---|
| Quên `messages.append(assistant)` | agent gọi lại cùng tool vô hạn | xem `10_GOI_MODEL.md §2` |
| Để agent tự tính số | số trong báo cáo không khớp tool | `verify_numbers()` |
| Không có nhóm đối chứng | mọi "công thức thắng" đều nghe hợp lý | luôn có rổ B4 |
| Dừng ở p-value | tin vào hiệu ứng 8,1× thực ra là 0,48× | luôn kiểm lớp 3 |
| Xây agent trước khi làm tay | không biết agent đúng hay sai | làm tuần 0 |

---

## 7. KHI NÀO BIẾT MÌNH ĐANG ĐI ĐÚNG

| Dấu hiệu tốt | Dấu hiệu xấu |
|---|---|
| A3 giết 30–50% phát hiện | A3 không giết cái nào |
| Agent nói "không đủ dữ liệu" | Agent luôn ra được 5 hướng kênh |
| `verify_numbers()` gần như không báo lỗi | Báo lỗi liên tục → agent đang tự tính |
| Số agent tìm ra khớp số bạn tính tay | Lệch nhiều mà không giải thích được |
| Chạy 2 lần ra cùng kết quả | Mỗi lần một khác |

---

## 8. ĐỌC TIẾP THEO THỨ TỰ

```
1. 12_BAT_DAU_TU_DAU.md      ← bạn đang đọc
2. 01_M1_DATA_CONTRACT.md    schema
3. 11_CODE_CHAY_DUOC.md      code sẵn, copy về chạy
4. 02_M2_TOOL_LAYER.md       tool lõi
5. 06_M6_VERIFICATION.md     lưới bắt bịa
6. 10_GOI_MODEL.md           vòng lặp tool-use
7. 04_M4_AGENTS.md           5 system prompt
8. 08_TRI_THUC_NGACH.md      nhúng vào prompt
9. 05_M5_ORCHESTRATOR.md     ghép lại
10. 07_M7_OUTPUT.md          xuất báo cáo
```
