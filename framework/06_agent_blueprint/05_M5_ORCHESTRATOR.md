# M5 · ORCHESTRATOR

> Điều phối: agent nào chạy khi nào, dừng ở đâu, sai thì làm gì.
>
> **Xong khi:** chạy tự động end-to-end, có cổng dừng, không cháy token.

---

## 1. LUỒNG CHÍNH

```
        load(niche)
             ↓
    ┌────────────────┐
    │  A1 · SCOUT    │
    └────────┬───────┘
             ↓
        ╔════════╗   NO_GO   ┌──────────────────────┐
        ║ CỔNG 1 ║──────────→│ DỪNG · ghi lý do     │
        ╚════╤═══╝           │ KHÔNG chạy tiếp      │
             │ GO            └──────────────────────┘
             ↓
    ┌────────────────┐
    │  A2 · ANALYST  │ ←──────┐
    └────────┬───────┘        │ vòng lặp tối đa 3 lần
             ↓                │
    ┌────────────────┐        │
    │  A3 · SKEPTIC  │────────┘ nếu <3 phát hiện sống sót
    └────────┬───────┘           thì A2 sinh thêm giả thuyết
             ↓
        ╔════════╗   0 sống sót  ┌────────────────────────┐
        ║ CỔNG 2 ║──────────────→│ DỪNG · báo "không đủ   │
        ╚════╤═══╝               │ bằng chứng để kết luận"│
             │ ≥3 sống sót       └────────────────────────┘
             ↓
    ┌──────────────────┐
    │ A4 · SYNTHESIZER │
    └────────┬─────────┘
             ↓
    ┌────────────────┐
    │  A5 · WRITER   │
    └────────┬───────┘
             ↓
    ┌────────────────┐
    │ M6 · VERIFY    │──── fail ──→ trả A5 viết lại (tối đa 2 lần)
    └────────┬───────┘
             ↓
        4 tài liệu T1.x
```

---

## 2. HAI CỔNG DỪNG — TIẾT KIỆM TOKEN VÀ TRÁNH KẾT LUẬN RỖNG

### Cổng 1 — sau A1

```python
if scout["verdict"] == "NO_GO":
    return {
        "status": "stopped_at_gate_1",
        "reason": scout["reasoning"],
        "metrics": scout["key_metrics"],
        "message": "Ngách không đạt ngưỡng cầu/cung. Phân tích tiếp là "
                   "tối ưu hoá con tàu đang chìm."
    }
```

**Tiết kiệm:** dừng ở đây tốn ~15k token thay vì ~500k.

### Cổng 2 — sau A3

```python
survived = [f for f in skeptic["reviewed"] if f["survives"]]
if len(survived) < 3:
    return {
        "status": "stopped_at_gate_2",
        "n_survived": len(survived),
        "message": "Không đủ phát hiện đứng vững sau phản biện. Đây là kết "
                   "quả HỢP LỆ, không phải lỗi hệ thống — nghĩa là dữ liệu "
                   "hiện có không đủ để kết luận chắc chắn.",
        "suggestion": "Thu thập thêm dữ liệu, hoặc thêm nguồn ngoài (S/V/P)."
    }
```

> **Quan trọng:** cổng 2 dừng lại là **thành công**, không phải thất bại. Một
> hệ thống luôn ra được 5 hướng kênh dù dữ liệu yếu là hệ thống đang bịa.

---

## 3. VÒNG LẶP A2 ↔ A3

```python
MAX_ROUNDS = 3

findings, survived = [], []
for round_i in range(MAX_ROUNDS):
    new = run_agent("A2", ctx, exclude_ids=[f["id"] for f in findings])
    findings += new["findings"]

    review = run_agent("A3", ctx, findings=new["findings"])
    survived += [f for f in review["reviewed"] if f["survives"]]

    log.info(f"Vòng {round_i+1}: +{len(new['findings'])} phát hiện, "
             f"{len(survived)} sống sót tổng cộng")

    if len(survived) >= 5:
        break                      # đủ rồi, dừng sớm tiết kiệm token
    if not new["findings"]:
        break                      # A2 cạn ý tưởng
```

**`exclude_ids`** quan trọng: không cho A2 sinh lại giả thuyết đã kiểm. Không
có nó, agent sẽ lặp vô hạn cùng vài ý tưởng.

---

## 4. XỬ LÝ LỖI

| Lỗi | Xử lý |
|---|---|
| Agent trả JSON sai schema | retry 2 lần kèm thông báo lỗi cụ thể, rồi dừng |
| Agent gọi tool không tồn tại | trả danh sách tool hợp lệ, cho gọi lại |
| Tool ném exception | trả `{"error": ...}` cho agent tự xử lý |
| Vượt ngân sách token | nén lịch sử; vẫn vượt → dừng, xuất phần đã có |
| Agent lặp cùng một tool 3 lần | chặn, báo "đã gọi rồi, kết quả: ..." |

```python
def run_agent(name, ctx, max_retries=2, **kw):
    for attempt in range(max_retries + 1):
        raw = call_model(SYSTEM[name], ctx, TOOLS[name], **kw)
        ok, err = validate_schema(raw, SCHEMA[name])
        if ok:
            return raw
        ctx += f"\n\nLỖI ĐỊNH DẠNG: {err}\nTrả lại đúng schema."
    raise AgentError(f"{name} không trả đúng schema sau {max_retries+1} lần")
```

---

## 5. CHẠY LẠI ĐƯỢC — CHECKPOINT

Agent tốn tiền. Đừng chạy lại từ đầu khi chỉ hỏng bước cuối.

```python
def run_pipeline(niche: str, resume: bool = True):
    ckpt = pathlib.Path(f"runs/{niche}/checkpoints")
    ckpt.mkdir(parents=True, exist_ok=True)

    def stage(name: str, fn):
        f = ckpt / f"{name}.json"
        if resume and f.exists():
            log.info(f"[bỏ qua] {name} — đã có checkpoint")
            return json.loads(f.read_text())
        out = fn()
        f.write_text(json.dumps(out, ensure_ascii=False, indent=2))
        return out

    data    = load(niche)
    scout   = stage("A1_scout",   lambda: run_agent("A1", build_ctx(data)))
    if scout["verdict"] == "NO_GO":
        return stop_at_gate_1(scout)

    findings = stage("A2_A3_loop", lambda: analyst_skeptic_loop(data, scout))
    ...
```

Sửa prompt A5 rồi chạy lại → chỉ tốn tiền cho A5.

---

## 6. NGÂN SÁCH VÀ CHI PHÍ

```python
BUDGET = {
    "A1": 15_000, "A2": 80_000, "A3": 60_000,
    "A4": 40_000, "A5": 50_000,
}
TOTAL_CAP = 300_000     # cứng, vượt là dừng
```

### Ước tính chi phí một lần chạy

| Kịch bản | Token | Ghi chú |
|---|---|---|
| Dừng ở cổng 1 | ~15k | ngách chìm, phát hiện sớm |
| Dừng ở cổng 2 | ~150k | dữ liệu không đủ mạnh |
| Chạy đủ | ~300–500k | ra 4 tài liệu |

**Khuyến nghị:** chạy A1 cho **mọi** ngách ứng viên trước (15k mỗi ngách), rồi
mới chạy đủ cho ngách qua cổng. Sàng 20 ngách tốn 300k, bằng chạy đủ một ngách.

---

## 7. CODE KHUNG ĐẦY ĐỦ

```python
def run_pipeline(niche: str) -> dict:
    data = load(niche)                          # M1
    base_ctx = build_niche_context(data)        # M3

    # ── A1 · Scout ────────────────────────────────────────────
    scout = run_agent("A1", base_ctx + DOMAIN_KNOWLEDGE)
    if scout["verdict"] == "NO_GO":
        return stop_at_gate_1(scout)

    # ── A2 ↔ A3 · vòng lặp sinh + phá ─────────────────────────
    findings, survived = [], []
    for _ in range(MAX_ROUNDS):
        new = run_agent("A2", base_ctx, scout=scout,
                        exclude_ids=[f["id"] for f in findings])
        if not new["findings"]:
            break
        findings += new["findings"]

        review = run_agent("A3", base_ctx, findings=new["findings"])
        survived += [f for f in review["reviewed"] if f["survives"]]
        if len(survived) >= 5:
            break

    if len(survived) < 3:
        return stop_at_gate_2(survived)

    # ── A4 · Tổng hợp ─────────────────────────────────────────
    synth = run_agent("A4", base_ctx, survived=survived)

    # ── A5 · Viết, có vòng sửa theo verification ──────────────
    docs = {}
    for doc_id in ["T1.1", "T1.2", "T1.3", "T1.4"]:
        for attempt in range(3):
            draft = run_agent("A5", base_ctx, doc=doc_id, synth=synth,
                              findings=survived)
            errs = verify(draft, survived, data)      # M6
            if not errs:
                docs[doc_id] = draft
                break
            base_ctx += f"\n\nLỖI KIỂM CHỨNG: {errs}\nSửa và viết lại."
        else:
            log.error(f"{doc_id} không qua kiểm chứng sau 3 lần")

    return {"status": "completed", "docs": docs,
            "n_findings": len(findings), "n_survived": len(survived)}
```

---

## 8. NGHIỆM THU M5

```
□ Cổng 1 chặn được ngách chìm giả lập (M2.4 = 0,3)
□ Cổng 2 chặn được khi A3 giết hết phát hiện
□ Vòng lặp A2↔A3 không lặp vô hạn (kiểm bằng exclude_ids)
□ Checkpoint hoạt động: xoá A5, chạy lại chỉ tốn A5
□ Vượt ngân sách thì dừng, không cháy tiền
□ Trace ghi đủ, đọc lại biết agent đã làm gì
□ Chạy end-to-end 1 ngách ra 4 tài liệu
```
