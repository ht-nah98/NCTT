# GỌI MODEL — vòng lặp tool-use

> File này lấp lỗ hổng lớn nhất của blueprint: **cách thực sự gọi model và
> chạy vòng lặp tool**. Không có phần này thì không có agent, chỉ có prompt.
>
> Phiên bản: v1.0 · Lập 2026-08-28
>
> ⚠️ Code viết theo API contract của Anthropic SDK. Máy đang dùng **chưa cài**
> `anthropic` — chạy `pip install anthropic` rồi đối chiếu lại phiên bản.

---

## 1. AGENT LÀ GÌ — VÒNG LẶP, KHÔNG PHẢI MỘT LỜI GỌI

Đây là điều người mới hay hiểu sai nhất.

```
❌ HIỂU SAI: gọi model một lần, nhận câu trả lời
   response = client.messages.create(...)
   print(response.content[0].text)

✅ ĐÚNG: vòng lặp cho tới khi model nói "xong"
   while True:
       response = gọi model
       nếu model muốn dùng tool:
           chạy tool
           gửi kết quả về cho model
           tiếp tục vòng lặp
       ngược lại:
           xong, trả kết quả
```

Model **không tự chạy được tool**. Nó chỉ nói *"tôi muốn gọi `test_title_theme`
với tham số này"*. Bạn phải chạy, rồi đưa kết quả về. Đó là toàn bộ bí mật của
"AI agent".

---

## 2. VÒNG LẶP TỐI THIỂU — CHẠY ĐƯỢC NGAY

```python
# agent_loop.py
import anthropic, json, logging

log = logging.getLogger(__name__)
client = anthropic.Anthropic()          # đọc ANTHROPIC_API_KEY từ biến môi trường

MODEL = "claude-sonnet-4-5"             # đổi theo model bạn có quyền dùng


def run_agent(system_prompt: str,
              user_message: str,
              tools: list[dict],
              tool_runner,
              max_turns: int = 25,
              temperature: float = 0.3) -> dict:
    """Vòng lặp tool-use đầy đủ.

    system_prompt : chuỗi system prompt của agent (từ 04_M4_AGENTS.md)
    user_message  : nhiệm vụ cụ thể lượt này
    tools         : list schema JSON, dạng {"name","description","input_schema"}
    tool_runner   : hàm (tên_tool, tham_số) -> dict kết quả
    max_turns     : chặn vòng lặp vô hạn

    Trả về: {"text": ..., "tool_calls": [...], "turns": n, "usage": {...}}
    """
    messages = [{"role": "user", "content": user_message}]
    tool_calls = []
    tokens_in = tokens_out = 0

    for turn in range(max_turns):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=8000,
            temperature=temperature,
            system=system_prompt,
            tools=tools,
            messages=messages,
        )
        tokens_in  += resp.usage.input_tokens
        tokens_out += resp.usage.output_tokens

        # BẮT BUỘC: đưa nguyên phản hồi của model vào lịch sử.
        # Bỏ bước này thì model "quên" nó vừa gọi tool gì.
        messages.append({"role": "assistant", "content": resp.content})

        # Model nói xong -> thoát vòng lặp
        if resp.stop_reason != "tool_use":
            text = "".join(b.text for b in resp.content if b.type == "text")
            return {"text": text, "tool_calls": tool_calls, "turns": turn + 1,
                    "usage": {"in": tokens_in, "out": tokens_out},
                    "stop_reason": resp.stop_reason}

        # Model muốn gọi tool. Có thể gọi NHIỀU tool trong một lượt.
        results = []
        for block in resp.content:
            if block.type != "tool_use":
                continue
            log.info(f"[lượt {turn+1}] gọi {block.name}({block.input})")
            try:
                out = tool_runner(block.name, block.input)
            except Exception as e:
                out = {"error": type(e).__name__, "detail": str(e)[:300]}

            tool_calls.append({"turn": turn + 1, "tool": block.name,
                               "args": block.input, "result": out})
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,          # PHẢI khớp id model gửi
                "content": json.dumps(out, ensure_ascii=False, default=str),
            })

        messages.append({"role": "user", "content": results})

    raise RuntimeError(f"Vượt {max_turns} lượt mà agent chưa dừng")
```

### Bốn chi tiết dễ sai — đọc kỹ

| Chi tiết | Sai thì bị gì |
|---|---|
| `messages.append({"role":"assistant","content": resp.content})` | model quên nó vừa gọi tool gì, gọi lại vô hạn |
| `tool_use_id` phải khớp `block.id` | API trả lỗi 400 |
| Một lượt có thể có **nhiều** `tool_use` block | xử lý thiếu → model treo chờ kết quả |
| `content` của tool_result phải là **chuỗi** | dict thô sẽ lỗi serialize |

---

## 3. ÉP MODEL TRẢ JSON ĐÚNG SCHEMA

Agent phải trả JSON theo schema (M4). Có ba cách, xếp theo độ tin cậy:

### Cách 1 — dùng tool giả làm khuôn (tin cậy nhất)

```python
def force_json(system: str, user: str, schema: dict, tools: list,
               tool_runner, **kw) -> dict:
    """Thêm một tool 'submit_result'. Model BUỘC phải gọi nó để kết thúc.

    Vì sao tin cậy nhất: schema được API kiểm, không phải mình parse chuỗi.
    """
    submit = {
        "name": "submit_result",
        "description": "Nộp kết quả cuối cùng. BẮT BUỘC gọi khi đã xong.",
        "input_schema": schema,
    }
    captured = {}

    def runner(name, args):
        if name == "submit_result":
            captured.update(args)
            return {"status": "đã nhận"}
        return tool_runner(name, args)

    run_agent(system, user, tools + [submit], runner, **kw)
    if not captured:
        raise ValueError("Agent kết thúc mà không gọi submit_result")
    return captured
```

### Cách 2 — parse text, có sửa lỗi thường gặp

```python
def parse_json_loose(text: str) -> dict:
    """Model hay bọc JSON trong khối markdown, hoặc kèm lời dẫn trước/sau."""
    import re
    m = re.search(r'`{3}(?:json)?\s*\n(.*?)`{3}', text, re.S)
    if m:
        text = m.group(1)
    else:
        s, e = text.find("{"), text.rfind("}")
        if s >= 0 and e > s:
            text = text[s:e+1]
    return json.loads(text)
```

### Cách 3 — mồi câu trả lời (prefill)

```python
messages.append({"role": "assistant", "content": "{"})   # ép bắt đầu bằng {
# nhớ nối lại "{" vào đầu kết quả khi parse
```

**Khuyến nghị:** dùng **cách 1** cho A1–A4 (schema chặt), **cách 2** cho A5
(văn bản dài, khó nhét hết vào schema).

---

## 4. XỬ LÝ LỖI THỰC TẾ

```python
import time, anthropic

def call_with_retry(fn, max_retries: int = 4):
    """Lỗi mạng và rate limit là chuyện thường ngày, không phải ngoại lệ."""
    for attempt in range(max_retries):
        try:
            return fn()
        except anthropic.RateLimitError:
            wait = 2 ** attempt * 5              # 5, 10, 20, 40 giây
            log.warning(f"Rate limit, chờ {wait}s")
            time.sleep(wait)
        except anthropic.APIStatusError as e:
            if e.status_code >= 500:             # lỗi phía server
                time.sleep(2 ** attempt)
                continue
            raise                                # 4xx là lỗi mình, đừng retry
        except anthropic.APIConnectionError:
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Thất bại sau {max_retries} lần thử")
```

### Bảng lỗi thường gặp

| Lỗi | Nguyên nhân | Xử lý |
|---|---|---|
| `RateLimitError` | gọi quá nhanh | lùi theo cấp số nhân |
| `400 invalid tool_use_id` | id không khớp | kiểm lại vòng lặp §2 |
| `stop_reason == "max_tokens"` | trả lời bị cắt giữa chừng | tăng `max_tokens`, hoặc chia nhỏ nhiệm vụ |
| Model gọi tool không tồn tại | tên sai | trả `{"error": "...", "available": [...]}` cho model tự sửa |
| Model lặp cùng tool 3 lần | kẹt | chặn ở `tool_runner`, trả kết quả cũ kèm nhắc |

```python
def make_tool_runner(data, tools_registry):
    """Bọc registry: chặn gọi lặp và ghi trace."""
    seen = {}

    def runner(name, args):
        key = (name, json.dumps(args, sort_keys=True))
        seen[key] = seen.get(key, 0) + 1
        if seen[key] > 2:
            return {"error": "ĐÃ GỌI TOOL NÀY VỚI THAM SỐ NÀY RỒI",
                    "previous_result": trace_lookup(key),
                    "hint": "Dùng kết quả cũ hoặc đổi hướng phân tích."}
        if name not in tools_registry:
            return {"error": f"tool '{name}' không tồn tại",
                    "available": sorted(tools_registry)}
        return tools_registry[name]["fn"](data, **args)

    return runner
```

---

## 5. GHÉP VÀO 5 AGENT

```python
# agents.py
from prompts import SYSTEM_A1, SYSTEM_A2, SYSTEM_A3, SYSTEM_A4, SYSTEM_A5
from schemas import SCHEMA_A1, SCHEMA_A2, SCHEMA_A3, SCHEMA_A4, SCHEMA_A5

AGENTS = {
    "A1": dict(system=SYSTEM_A1, schema=SCHEMA_A1, temp=0.0, group="A", budget=15_000),
    "A2": dict(system=SYSTEM_A2, schema=SCHEMA_A2, temp=0.7, group="BCD", budget=80_000),
    "A3": dict(system=SYSTEM_A3, schema=SCHEMA_A3, temp=0.2, group="C",  budget=60_000),
    "A4": dict(system=SYSTEM_A4, schema=SCHEMA_A4, temp=0.3, group="D",  budget=40_000),
    "A5": dict(system=SYSTEM_A5, schema=SCHEMA_A5, temp=0.5, group="E",  budget=50_000),
}


def run(agent_id: str, data, context: str, task: str) -> dict:
    cfg = AGENTS[agent_id]
    tools = get_schemas(groups=cfg["group"])          # chỉ nạp tool cần
    runner = make_tool_runner(data, TOOLS)

    result = force_json(
        system=cfg["system"] + "\n\n" + context,
        user=task,
        schema=cfg["schema"],
        tools=tools,
        tool_runner=runner,
        temperature=cfg["temp"],
    )
    return result
```

---

## 6. VÍ DỤ CHẠY THẬT — TỪ ĐẦU ĐẾN CUỐI

```python
# demo.py — chạy A1 Scout trên một ngách
from m1_data_contract import load
from agent_loop import run_agent, force_json
from tools.registry import TOOLS, get_schemas
from prompts import SYSTEM_A1
from schemas import SCHEMA_A1

data = load("data/christian-blues")

context = f"""
## NGÁCH: {data.meta['niche']}
Quy mô: {data.videos.channel_id.nunique()} kênh · {len(data.videos)} video
Đã chín: {len(data.matured)} video

## GIỚI HẠN BẮT BUỘC MANG THEO
{chr(10).join('- ' + c for c in data.meta.get('caveats', []))}
"""

result = force_json(
    system=SYSTEM_A1 + "\n\n" + context,
    user="Khảo sát ngách này. Ngách có đáng phân tích sâu không?",
    schema=SCHEMA_A1,
    tools=get_schemas(groups="A"),
    tool_runner=make_tool_runner(data, TOOLS),
    temperature=0.0,
)

print(json.dumps(result, ensure_ascii=False, indent=2))
# -> {"verdict": "GO", "confidence": "vừa", "key_metrics": {...}, ...}
```

---

## 7. SCHEMA JSON CHO 5 AGENT

Đây là phần blueprint còn thiếu. Dùng trực tiếp với `force_json()`.

```python
# schemas.py
SCHEMA_A1 = {
    "type": "object",
    "required": ["verdict", "confidence", "key_metrics", "reasoning", "caveats"],
    "properties": {
        "verdict":    {"type": "string", "enum": ["GO", "GO_CAUTION", "NO_GO"]},
        "confidence": {"type": "string", "enum": ["cao", "vừa", "thấp"]},
        "key_metrics": {
            "type": "object",
            "properties": {"M2_4": {"type": "number"},
                           "gini": {"type": "number"},
                           "newcomer_pct": {"type": "number"}}},
        "reasoning": {"type": "string"},
        "caveats":   {"type": "array", "items": {"type": "string"}},
        "next_questions": {"type": "array", "items": {"type": "string"}},
    },
}

SCHEMA_A2 = {
    "type": "object",
    "required": ["findings"],
    "properties": {
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "hypothesis", "tool_called",
                             "tool_result", "reading"],
                "properties": {
                    "id":          {"type": "string"},
                    "hypothesis":  {"type": "string"},
                    "source":      {"type": "string"},
                    "tool_called": {"type": "string"},
                    "tool_result": {"type": "object"},
                    "reading":     {"type": "string"},
                    "warnings_carried": {"type": "array",
                                         "items": {"type": "string"}},
                }}},
        "not_tested": {
            "type": "array",
            "items": {"type": "object",
                      "properties": {"hypothesis": {"type": "string"},
                                     "why_not":    {"type": "string"}}}},
    },
}

SCHEMA_A3 = {
    "type": "object",
    "required": ["reviewed", "summary"],
    "properties": {
        "reviewed": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "survives", "checks"],
                "properties": {
                    "id":       {"type": "string"},
                    "survives": {"type": "boolean"},
                    "checks": {
                        "type": "object",
                        "required": ["sample_size", "simpson",
                                     "reverse_causation"],
                        "properties": {
                            "sample_size":       {"type": "string"},
                            "simpson":           {"type": "string"},
                            "denominator":       {"type": "string"},
                            "maturation":        {"type": "string"},
                            "reverse_causation": {"type": "string"},
                            "survivorship":      {"type": "string"}}},
                    "verdict_adjusted": {"type": "string"},
                    "must_state":       {"type": "string"}}}},
        "killed":  {"type": "array", "items": {"type": "string"}},
        "summary": {"type": "string"},
    },
}

SCHEMA_A4 = {
    "type": "object",
    "required": ["directions"],
    "properties": {
        "directions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["rank", "title", "based_on", "confidence",
                             "why_trust", "risk"],
                "properties": {
                    "rank":       {"type": "integer"},
                    "title":      {"type": "string"},
                    "based_on":   {"type": "array", "items": {"type": "string"}},
                    "confidence": {"type": "string",
                                   "enum": ["1/5","2/5","3/5","4/5","5/5"]},
                    "customer":   {"type": "string"},
                    "why_trust":  {"type": "string"},
                    "risk":       {"type": "string"},
                    "how_to_verify": {"type": "string"}}}},
        "avoid":    {"type": "array", "items": {"type": "object"}},
        "unknowns": {"type": "array", "items": {"type": "string"}},
    },
}

SCHEMA_A5 = {
    "type": "object",
    "required": ["document", "blocks"],
    "properties": {
        "document": {"type": "string",
                     "enum": ["T1.1", "T1.2", "T1.3", "T1.4"]},
        "blocks": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["type"],
                "properties": {
                    "type": {"type": "string",
                             "enum": ["heading","paragraph","table",
                                      "warning","chart"]},
                    "text":    {"type": "string"},
                    "level":   {"type": "integer"},
                    "cites":   {"type": "array", "items": {"type": "string"}},
                    "n":       {"type": "integer"},
                    "source_class": {"type": "string"},
                    "headers": {"type": "array", "items": {"type": "string"}},
                    "rows":    {"type": "array", "items": {"type": "array"}},
                    "spec":    {"type": "object"}}}},
    },
}
```

---

## 7b. BỐN HÀM CÒN LẠI

Các đoạn trên gọi `call_model`, `build_ctx`, `trace_lookup`,
`analyst_skeptic_loop`. Đây là định nghĩa của chúng.

```python
def call_model(system, messages, tools, temperature=0.3, max_tokens=8000):
    """Bọc một lời gọi API, có retry. Mọi chỗ khác gọi qua hàm này."""
    return call_with_retry(lambda: client.messages.create(
        model=MODEL, max_tokens=max_tokens, temperature=temperature,
        system=system, tools=tools, messages=messages))


def build_ctx(data) -> str:
    """Context tầng 2 — nạp một lần đầu phiên (xem M3 §4)."""
    d = describe_niche(data)
    caveats = "\n".join(f"- {c}" for c in d["caveats"])
    return (f"## NGÁCH: {d['niche']}\n"
            f"Quy mô: {d['n_channels']} kênh · {d['n_videos']} video · "
            f"{d['n_comments']} comment\n"
            f"Đã chín: {d['n_matured']} video ({d['matured_pct']}%)\n"
            f"Thời gian: {d['date_range'][0]} → {d['date_range'][1]}\n"
            f"Nguồn: {d['source_class']}\n\n"
            f"## GIỚI HẠN BẮT BUỘC MANG THEO\n{caveats}\n")


# Sổ ghi mọi lời gọi tool trong phiên. make_tool_runner() ghi vào đây.
TRACE: list[dict] = []

def trace_lookup(key: tuple) -> dict:
    """Tìm kết quả cũ của một lời gọi đã thực hiện, để trả lại khi agent lặp."""
    name, args_json = key
    for t in reversed(TRACE):
        if t["tool"] == name and json.dumps(t["args"], sort_keys=True) == args_json:
            return t["result"]
    return {}


def analyst_skeptic_loop(data, scout, max_rounds=3):
    """Vòng lặp A2 sinh giả thuyết ↔ A3 phá. Xem M5 §3."""
    ctx = build_ctx(data)
    findings, survived = [], []
    for _ in range(max_rounds):
        new = run("A2", data, ctx,
                  task=f"Sinh giả thuyết mới. Đã kiểm: "
                       f"{[f['id'] for f in findings]}. Đừng lặp lại.")
        if not new.get("findings"):
            break
        findings += new["findings"]

        review = run("A3", data, ctx,
                     task=f"Phá từng phát hiện sau: "
                          f"{json.dumps(new['findings'], ensure_ascii=False)}")
        survived += [f for f in review["reviewed"] if f["survives"]]
        if len(survived) >= 5:
            break
    return {"findings": findings, "survived": survived}
```

`tool_runner` không phải hàm riêng — nó là **tham số** truyền vào `run_agent()`,
sinh bởi `make_tool_runner()` ở §4.

---

## 8. ĐẾM TIỀN

```python
# giá tham khảo, KIỂM LẠI trên trang giá chính thức trước khi dùng
PRICE = {                     # USD cho 1 triệu token
    "claude-sonnet-4-5": {"in": 3.00, "out": 15.00},
    "claude-haiku-4-5":  {"in": 0.80, "out": 4.00},
}

def cost(usage: dict, model: str) -> float:
    p = PRICE[model]
    return usage["in"]/1e6*p["in"] + usage["out"]/1e6*p["out"]
```

Ghi vào trace mỗi lượt để biết agent nào tốn nhất. Thường là **A2** (gọi tool
nhiều) và **A5** (sinh văn bản dài).

---

## 9. MẸO TIẾT KIỆM

| Mẹo | Tiết kiệm |
|---|---|
| Chỉ nạp tool theo nhóm agent cần | 30–40% token đầu vào |
| Nén lịch sử tool sau 3 kết quả (M3 §5) | 50%+ ở vòng lặp dài |
| Dùng model nhỏ cho A1 Scout | A1 việc đơn giản, không cần model lớn |
| Prompt caching cho phần system cố định | 90% chi phí phần lặp lại |
| Checkpoint từng agent (M5 §5) | sửa A5 không phải chạy lại A1–A4 |

**Prompt caching** đáng làm nhất — phần `system` + tri thức ngách ~5.000 token
lặp lại ở **mọi** lượt gọi:

```python
system=[{
    "type": "text",
    "text": SYSTEM_A2 + DOMAIN_KNOWLEDGE,
    "cache_control": {"type": "ephemeral"},     # đánh dấu để cache
}]
```

---

## 10. NGHIỆM THU

```
□ Vòng lặp chạy được, model gọi tool và nhận kết quả
□ Xử lý được NHIỀU tool_use trong một lượt
□ force_json() trả về đúng schema, không cần parse tay
□ Retry hoạt động khi gặp rate limit
□ Chặn được gọi lặp cùng tool cùng tham số
□ Đếm được token và chi phí mỗi lần chạy
□ max_turns chặn được vòng lặp vô hạn
```

**Phép thử đầu tiên nên làm:** viết một tool giả `get_number()` trả về `42`,
cho agent nhiệm vụ *"gọi tool và cho tôi biết số đó"*. Nếu vòng lặp chạy đúng,
agent sẽ gọi tool rồi trả lời "42". Đây là "hello world" của agent — làm được
cái này rồi hãy ghép tool thật.
