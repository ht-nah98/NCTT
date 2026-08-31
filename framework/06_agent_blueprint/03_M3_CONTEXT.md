# M3 · CONTEXT BUILDER

> Nạp gì vào đầu agent, nạp bao nhiêu, nạp lúc nào. Đây là chỗ quyết định
> agent thông minh hay ngu — cùng một prompt, context khác nhau cho kết quả
> khác hẳn.
>
> **Xong khi:** mỗi agent nhận đúng thứ nó cần, không tràn, không thiếu.

---

## 1. VẤN ĐỀ

Dữ liệu thô là **145.150 comment và 7.193 video**. Không thể nhét vào context.
Mà nhét được cũng không nên — agent sẽ chìm trong nhiễu.

Câu hỏi thật: *"agent cần biết gì để ra quyết định đúng?"*

---

## 2. BA TẦNG CONTEXT

```
TẦNG 1 · CỐ ĐỊNH      system prompt + tri thức ngách       ~3.000 token
                       (không đổi giữa các lần chạy)

TẦNG 2 · THEO NGÁCH   describe_niche() + caveats + schema  ~1.500 token
                       (đổi theo ngách, cố định trong một lần chạy)

TẦNG 3 · THEO LƯỢT    kết quả tool vừa gọi                 ~500-2.000 token
                       (đổi mỗi lượt)
```

**Không bao giờ** nạp dữ liệu thô vào tầng nào. Agent đọc **kết quả tool**,
không đọc bảng gốc.

---

## 3. TẦNG 1 — TRI THỨC NGÁCH NHÚNG VÀO PROMPT

Đây là thứ khiến agent hiểu ngách nhạc, không phải một agent phân tích chung chung.

```python
DOMAIN_KNOWLEDGE = """
## BỐI CẢNH NGÁCH NHẠC YOUTUBE

### Đặc thù về dữ liệu
- View phân bố ĐUÔI DÀI: trung bình luôn cao hơn trung vị nhiều lần.
  LUÔN dùng trung vị, không dùng trung bình.
- Video cần ~60 ngày để "chín". Video mới chưa tích đủ view.
- Kênh lớn thì video nào cũng nhiều view -> phải chuẩn hoá theo chính kênh đó.

### Đặc thù về hành vi khán giả
- Nhạc là nội dung nghe NỀN hoặc nghe CHỦ ĐỘNG. Hai loại này ràng buộc
  sản xuất khác hẳn nhau:
  · nghe nền  -> độ dài quan trọng, lời không quan trọng
  · nghe chủ động -> lời quan trọng, sai chất là bị phát hiện ngay
- Khán giả tìm nhạc chủ yếu qua ĐỀ XUẤT, không qua tìm kiếm. Tỷ lệ điển hình
  gần 7:1. Nghĩa là tối ưu từ khoá tìm kiếm KHÔNG phải đòn bẩy chính.
- Comment chỉ đến từ người chịu bình luận — mẫu thiên lệch, không đại diện.

### Đặc thù về sản xuất
- Hai mô hình đối lập cùng thắng được: "nhiều & ngắn" và "ít & dài".
  Phải chọn MỘT trước khi sản xuất.
- Thumbnail thường KHÔNG phân biệt được thắng/thua trong ngách nhạc.
  Nó là vé vào cửa, không phải đòn bẩy.

### Năm bẫy đã đảo ngược kết luận trong thực tế
L1 · Dữ liệu chưa chín: so nhóm chưa chín với nhóm đã chín.
     Hậu quả thật: M2.4 = 0,45 (dừng) vs 1,30 (đi tiếp).
L2 · Nghịch lý Simpson: hiệu ứng mạnh trong mẫu, ngược lại trong từng kênh.
     Hậu quả thật: lift 8,1× trong mẫu, 0,48× toàn thị trường.
L3 · Artefact mẫu số: tỷ lệ có view ở mẫu số tự động tương quan âm với view.
     Hậu quả thật: engagement_rate cho hiệu ứng "mạnh nhất" nhưng là toán học.
L4 · Thiên lệch sống sót: dữ liệu chỉ có kênh còn tồn tại.
     Hậu quả: mọi tỷ lệ thành công đều lạc quan quá mức.
L5 · Chỉ số không đo được vẫn ra số: với 1 snapshot, mọi chỉ số dạng
     "thời gian đạt X view" đều vô nghĩa.
"""
```

> **Vì sao nhúng 5 bẫy vào prompt:** agent không tự biết những bẫy này. Chúng
> là tri thức trả giá mới có. Không nhúng vào, agent sẽ mắc lại từng cái một.

---

## 4. TẦNG 2 — CONTEXT THEO NGÁCH

```python
def build_niche_context(data) -> str:
    """Nạp một lần đầu phiên, dùng cho mọi lượt."""
    d = describe_niche(data)
    return f"""
## NGÁCH ĐANG PHÂN TÍCH: {d['niche']}

Quy mô : {d['n_channels']} kênh · {d['n_videos']} video · {d['n_comments']} comment
Đã chín: {d['n_matured']} video ({d['matured_pct']}%)
Thời gian: {d['date_range'][0]} → {d['date_range'][1]}
Ngày crawl: {d['crawl_date']}
Nguồn: {d['source_class']}

## GIỚI HẠN BẮT BUỘC MANG THEO
{chr(10).join(f"- {c}" for c in d['caveats'])}

## TOOL BẠN CÓ
{format_tool_schemas(group=agent_group)}
"""
```

**Chi tiết quan trọng:** `caveats` nạp vào **ngay từ đầu**, không đợi agent hỏi.
Agent phải biết dữ liệu yếu chỗ nào **trước khi** phân tích, không phải sau.

---

## 5. TẦNG 3 — QUẢN LÝ KẾT QUẢ TOOL

Vấn đề: sau 15 lượt gọi tool, context phồng lên và agent bắt đầu quên đầu bài.

### Chiến lược nén

```python
def compact_tool_history(history: list, keep_full: int = 3) -> list:
    """Giữ nguyên 3 kết quả gần nhất, nén phần còn lại thành 1 dòng.

    Vì sao 3: agent cần chi tiết để so sánh kết quả liền kề. Xa hơn thì
    chỉ cần nhớ ĐÃ KIỂM GÌ và KẾT QUẢ RA SAO, không cần toàn bộ số.
    """
    if len(history) <= keep_full:
        return history

    old, recent = history[:-keep_full], history[-keep_full:]
    summary = [{
        "role": "compacted",
        "content": "Đã kiểm trước đó:\n" + "\n".join(
            f"- {h['tool']}({h['args'].get('label','')}) "
            f"-> {h['result'].get('verdict', h['result'].get('error','?'))} "
            f"(n={h['result'].get('n','?')}, lift={h['result'].get('lift','?')})"
            for h in old)
    }]
    return summary + recent
```

### Ngân sách token

| Agent | Ngân sách | Vượt thì |
|---|---|---|
| A1 Scout | 15k | dừng, đã đủ để phán quyết |
| A2 Analyst | 80k | nén lịch sử, tiếp tục |
| A3 Skeptic | 60k | nén, nhưng giữ nguyên phát hiện đang xét |
| A4 Synthesizer | 40k | dừng, đã đủ |
| A5 Writer | 50k | chia nhỏ theo tài liệu |

---

## 6. ĐIỀU TUYỆT ĐỐI KHÔNG NẠP

| Không nạp | Vì sao |
|---|---|
| Bảng dữ liệu thô | tràn context, agent chìm trong nhiễu |
| `author_name`, `comment_id` thật | quy tắc R6 |
| Toàn văn 6.413 comment | agent phải gọi tool, không đọc trực tiếp |
| Kết quả của agent khác chưa qua kiểm | lan truyền lỗi |
| Prompt của agent khác | mỗi agent phải giữ vai riêng |

### Ngoại lệ có kiểm soát: trích dẫn comment

A5 Writer cần trích comment để minh hoạ. Cách làm an toàn:

```python
def get_quotes(data, signal: str, top_n: int = 3) -> list:
    """Trả comment tiêu biểu, ĐÃ BỎ ĐỊNH DANH."""
    hits = data.comments[data.comments.text.str.contains(signal, case=False)]
    top = hits.nlargest(top_n, "like_count")
    return [{
        "text": t[:250],                    # cắt ngắn
        "likes": int(l),
        # KHÔNG trả comment_id, KHÔNG trả author
    } for t, l in zip(top.text, top.like_count)]
```

---

## 7. TRACE — GHI LẠI MỌI QUYẾT ĐỊNH

```python
@dataclass
class TraceEntry:
    turn: int
    agent: str
    action: str              # "tool_call" | "reasoning" | "output"
    tool: str | None
    args: dict | None
    result_summary: str      # nén, không lưu toàn bộ
    tokens_in: int
    tokens_out: int
    timestamp: str
```

Ghi vào `_trace.jsonl`. Ba việc dùng được:

| Dùng để | Cách |
|---|---|
| Gỡ lỗi khi agent sai | lần ngược xem nó đọc gì trước khi kết luận sai |
| Cải thiện prompt | tìm chỗ agent hay lạc hướng |
| Tính chi phí | cộng `tokens_in + tokens_out` |

---

## 8. NGHIỆM THU M3

```
□ Tri thức ngách nhúng đủ 5 bẫy L1-L5
□ caveats nạp vào context NGAY từ lượt đầu
□ Nén lịch sử hoạt động, kiểm bằng cách chạy 20 lượt tool
□ Không có author_name / comment_id thật trong bất kỳ context nào
□ Trace ghi đủ mọi lượt, đọc lại hiểu được agent đã nghĩ gì
□ Ngân sách token có cưỡng chế, không chỉ ghi trên giấy
```
