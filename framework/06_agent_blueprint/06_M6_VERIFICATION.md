# M6 · VERIFICATION — bắt agent nói dối

> Xây **trước** khi thả agent. Nếu không có lớp này, bạn sẽ không biết agent
> đang bịa — và output đẹp khiến rất khó phát hiện.
>
> **Xong khi:** bắt được số bịa trong output giả lập.

---

## 1. VÌ SAO ĐÂY LÀ MODULE QUAN TRỌNG NHẤT

Mô hình ngôn ngữ **rất giỏi viết câu nghe đúng**. Ba lỗi điển hình:

| Lỗi | Ví dụ | Vì sao nguy hiểm |
|---|---|---|
| **Số bịa** | tool trả `lift 1,62` → agent viết "khoảng 1,7×" | nghe hợp lý, sai sự thật |
| **Nâng cấp phán quyết** | tool trả `YẾU` → agent viết "xác nhận rõ" | đảo ngược kết luận |
| **Nuốt cảnh báo** | tool trả `warning: Simpson` → agent bỏ qua | người đọc tin nhầm |

Cả ba đều **không phát hiện được bằng mắt** khi báo cáo dài 8 trang.

---

## 2. SÁU LỚP KIỂM

### Lớp 1 · Mọi số phải truy được về tool

```python
def verify_numbers(draft: dict, tool_results: list) -> list[str]:
    """Trích mọi số trong văn bản, đối chiếu với kết quả tool."""
    allowed = set()
    for r in tool_results:
        for v in flatten_values(r):
            if isinstance(v, (int, float)):
                allowed.add(round(float(v), 3))
                allowed.add(round(float(v), 1))
                allowed.add(round(float(v), 0))
                allowed.add(round(float(v) * 100, 1))     # dạng phần trăm

    errs = []
    for text in extract_texts(draft):
        for num in re.findall(r'\d+(?:[.,]\d+)?', text):
            val = float(num.replace(".", "").replace(",", "."))
            if val > 1 and val not in allowed:
                errs.append(f"Số {num} không có trong kết quả tool nào: "
                            f"«{text[:80]}»")
    return errs
```

> **Đây là lớp bắt được nhiều lỗi nhất.** Agent hay làm tròn "cho đẹp" —
> `1,62` thành `1,6` thì chấp nhận được, nhưng `1,62` thành `khoảng 2 lần`
> là bịa.

### Lớp 2 · Phán quyết không được nâng cấp

```python
RANK = {"TRÁNH": 0, "BÁC BỎ": 0, "BÁC BỎ (Simpson)": 0,
        "YẾU": 1, "XÁC NHẬN": 2}

CLAIM_WORDS = {
    2: ["xác nhận", "chứng minh", "rõ ràng", "chắc chắn", "mạnh mẽ"],
    1: ["có tín hiệu", "gợi ý", "khả năng", "có thể"],
    0: ["không có bằng chứng", "bác bỏ", "nên tránh", "không chứng minh được"],
}

def verify_claim_strength(draft, findings) -> list[str]:
    errs = []
    for block in draft["blocks"]:
        for fid in block.get("cites", []):
            true_rank = RANK[find_by_id(findings, fid)["verdict"]]
            for rank, words in CLAIM_WORDS.items():
                if rank > true_rank and any(w in block["text"].lower()
                                            for w in words):
                    errs.append(
                        f"{fid}: phán quyết là "
                        f"«{find_by_id(findings, fid)['verdict']}» nhưng câu văn "
                        f"khẳng định ở mức cao hơn: «{block['text'][:80]}»")
    return errs
```

### Lớp 3 · Cảnh báo bắt buộc phải xuất hiện

```python
def verify_warnings(draft, findings) -> list[str]:
    """Mọi warning từ tool và must_state từ Skeptic phải có trong báo cáo."""
    full = " ".join(extract_texts(draft)).lower()
    errs = []
    for f in findings:
        for w in f.get("warnings_carried", []) + [f.get("must_state", "")]:
            if not w:
                continue
            key = key_phrase(w)                # rút cụm từ đặc trưng
            if key.lower() not in full:
                errs.append(f"{f['id']}: thiếu cảnh báo bắt buộc «{w[:80]}»")
    return errs
```

### Lớp 4 · Cỡ mẫu đi kèm mọi phát biểu định lượng

```python
def verify_sample_size(draft) -> list[str]:
    errs = []
    for b in draft["blocks"]:
        if b["type"] != "paragraph":
            continue
        has_number = re.search(r'\d+(?:[.,]\d+)?\s*(?:×|%|lần)', b["text"])
        if has_number and "n" not in b and "n=" not in b["text"]:
            errs.append(f"Phát biểu định lượng thiếu cỡ mẫu: «{b['text'][:80]}»")
    return errs
```

### Lớp 5 · Mẫu nhỏ không được kết luận

```python
def verify_min_sample(draft, findings) -> list[str]:
    errs = []
    for b in draft["blocks"]:
        for fid in b.get("cites", []):
            f = find_by_id(findings, fid)
            if f.get("n", 999) < 30 and "KHÔNG ĐỦ MẪU" not in b["text"]:
                errs.append(f"{fid}: n={f['n']} < 30 nhưng vẫn viết như kết luận")
    return errs
```

### Lớp 6 · Không rò rỉ định danh (R6)

```python
PII_PATTERNS = [
    r'\b[A-Za-z0-9_-]{22,26}\b',          # comment_id YouTube
    r'@[A-Za-z0-9_.\-]{3,}[0-9]{3,}',     # handle thật
    r'\bUC[A-Za-z0-9_-]{22}\b',           # channel_id
]

def verify_no_pii(draft) -> list[str]:
    errs = []
    for text in extract_texts(draft):
        for pat in PII_PATTERNS:
            for m in re.findall(pat, text):
                errs.append(f"RÒ RỈ ĐỊNH DANH: «{m}» — vi phạm R6")
    return errs
```

---

## 3. GỘP LẠI

```python
def verify(draft, findings, data) -> list[str]:
    """Chạy đủ 6 lớp. Trả danh sách lỗi; rỗng nghĩa là đạt."""
    return (verify_numbers(draft, collect_tool_results(findings))
            + verify_claim_strength(draft, findings)
            + verify_warnings(draft, findings)
            + verify_sample_size(draft)
            + verify_min_sample(draft, findings)
            + verify_no_pii(draft))
```

Lỗi được **trả về cho A5 viết lại**, tối đa 3 lần (xem M5 §7).

---

## 4. BỘ TEST ĐỎ — DỰNG TRƯỚC KHI THẢ AGENT

Đây là phần quan trọng nhất của M6. Tự viết output **cố tình sai**, kiểm rằng
verification bắt được.

```python
RED_TEAM = [
    {
        "name": "số bịa",
        "draft": {"blocks": [{"type": "paragraph",
                  "text": "Chủ đề cảm tạ có lift khoảng 2,5 lần.",
                  "cites": ["F01"]}]},
        "findings": [{"id": "F01", "verdict": "XÁC NHẬN", "n": 55,
                      "tool_result": {"lift": 1.62}}],
        "must_catch": "verify_numbers",
    },
    {
        "name": "nâng cấp phán quyết",
        "draft": {"blocks": [{"type": "paragraph",
                  "text": "Dữ liệu chứng minh rõ ràng hướng này hiệu quả.",
                  "cites": ["F02"], "n": 222}]},
        "findings": [{"id": "F02", "verdict": "YẾU", "n": 222}],
        "must_catch": "verify_claim_strength",
    },
    {
        "name": "nuốt cảnh báo Simpson",
        "draft": {"blocks": [{"type": "paragraph",
                  "text": "Chủ đề Kinh Thánh cho lift 8,1 lần.",
                  "cites": ["F03"], "n": 44}]},
        "findings": [{"id": "F03", "verdict": "BÁC BỎ (Simpson)", "n": 44,
                      "tool_result": {"lift": 8.1},
                      "must_state": "6/13 kênh ngược chiều"}],
        "must_catch": "verify_warnings",
    },
    {
        "name": "kết luận từ mẫu nhỏ",
        "draft": {"blocks": [{"type": "paragraph",
                  "text": "Nhóm góa phụ là phân khúc tiềm năng.",
                  "cites": ["F04"], "n": 5}]},
        "findings": [{"id": "F04", "verdict": "XÁC NHẬN", "n": 5}],
        "must_catch": "verify_min_sample",
    },
    {
        "name": "rò rỉ định danh",
        "draft": {"blocks": [{"type": "paragraph",
                  "text": "Bình luận UgxKq2mF8vN3pL9wErt4AaABAg cho thấy..."}]},
        "findings": [],
        "must_catch": "verify_no_pii",
    },
]


def test_red_team():
    for case in RED_TEAM:
        errs = verify(case["draft"], case["findings"], None)
        assert errs, f"KHÔNG BẮT ĐƯỢC: {case['name']}"
        print(f"  ✓ bắt được: {case['name']}")
```

> **Nếu bộ test này không chạy, đừng thả agent.** Bạn sẽ không biết nó đang bịa.

---

## 5. GIÁM SÁT KHI CHẠY THẬT

Ngoài kiểm từng lần, theo dõi xu hướng:

| Chỉ số | Ngưỡng lành mạnh | Bất thường nghĩa là |
|---|---|---|
| Tỷ lệ A3 giết phát hiện | 30–50% | <10%: Skeptic quá nhẹ · >80%: Analyst quá ẩu |
| Số lần A5 phải viết lại | 0–1 | ≥2 thường xuyên: prompt A5 chưa rõ |
| Lỗi `verify_numbers` | ~0 | >0 thường xuyên: agent đang tự tính số |
| Token mỗi lần chạy | 300–500k | vượt nhiều: vòng lặp không hội tụ |

Ghi vào `runs/<niche>/metrics.json` để so giữa các lần chạy.

---

## 6. NGHIỆM THU M6

```
□ 6 lớp kiểm đã viết
□ Bộ test đỏ 5 ca, TẤT CẢ đều bị bắt
□ verify() trả về danh sách lỗi đọc được, không phải True/False
□ Lỗi trả về đủ chi tiết để A5 sửa được
□ Chạy verify trên một báo cáo thật, không có dương tính giả
□ Giám sát ghi được 4 chỉ số ở §5
```

> **Phép thử quyết định:** lấy một báo cáo **đúng** đã có, chạy `verify()`.
> Nếu nó báo lỗi (dương tính giả), lớp kiểm quá chặt và agent sẽ mắc kẹt trong
> vòng viết lại vô tận.
