# KIẾN TRÚC HỆ THỐNG & WORKFLOW

> Tài liệu thiết kế tổng. Đọc file này trước khi chạy bất kỳ bước nào.
> Phiên bản: v2.0

---

## 1. TRIẾT LÝ THIẾT KẾ

### 1.1 Tách khung khỏi dữ liệu

```mermaid
flowchart LR
    subgraph FW["framework/ · KHUNG CHUNG"]
        direction TB
        F1["Rubric chấm điểm"]
        F2["Logic lọc"]
        F3["Đặc tả 8 agent"]
        F4["9 runbook từng bước"]
    end
    subgraph NI["niches/ · DỮ LIỆU RIÊNG"]
        direction TB
        N1["christian-blues/"]
        N2["ngách kế tiếp/"]
        N3["ngách sau nữa/"]
    end
    FW -->|áp dụng| N1
    FW -->|áp dụng| N2
    FW -->|áp dụng| N3
```

**Hệ quả:** ngách thứ hai chỉ tốn công **thu thập dữ liệu + chạy quy trình**, không tốn công thiết kế lại. Và vì cùng rubric, hai ngách **so sánh được trực tiếp với nhau**.

### 1.2 Bốn tầng xử lý — không được trộn

```mermaid
flowchart LR
    F["TẦNG 1 · FACT<br/>số liệu thô<br/><i>không diễn giải</i>"]
    M["TẦNG 2 · METRIC<br/>chỉ số chuẩn hóa<br/><i>có công thức</i>"]
    S["TẦNG 3 · SCORE<br/>điểm 0–5<br/><i>có ngưỡng cố định</i>"]
    I["TẦNG 4 · INSIGHT<br/>diễn giải<br/><i>người/AI viết</i>"]
    F --> M --> S --> I
    I -.->|"❌ CẤM sửa ngược"| S
```

Tầng 4 **không được** sửa tầng 3. Muốn đổi điểm → đổi *ngưỡng* ở tầng 3 → chạy lại toàn bộ.
Đây là điều bảng Excel thủ công không làm được, và là lý do nó không nhất quán.

---

## 2. WORKFLOW TỔNG — 10 BƯỚC

```mermaid
flowchart TB
    S0["STEP_00 · SETUP<br/>Định nghĩa ngách, kiểm kê dữ liệu"]
    S1["STEP_01 · NỀN MÓNG<br/>A0 · Chuẩn hóa, làm giàu, lọc"]
    S2["STEP_02 · QUY MÔ &amp; ĐỘNG LƯỢNG<br/>A1 · Ngách lên hay xuống?"]
    GATE{"CỔNG QUYẾT ĐỊNH<br/>Ngách còn đáng vào?"}
    STOP["DỪNG<br/>Ghi lý do, lưu hồ sơ"]
    S3["STEP_03 · ĐỐI THỦ<br/>A2 · Ai thắng? Còn cửa?"]
    S4["STEP_04 · SÀNG LỌC ĐỐI CHỨNG<br/>A3 · Đặc trưng nào KHÔNG phân biệt thắng/thua?"]
    S5["STEP_05 · KHÁN GIẢ<br/>A4 · Khách là ai?"]
    S6["STEP_06 · TỪ KHÓA<br/>A5 · Truyền tải thế nào?"]
    S7["STEP_07 · KIẾM TIỀN<br/>A6 · Ra tiền không?"]
    S8["STEP_08 · TỔNG HỢP<br/>A7 · Vào hay không?"]

    HAS{"Có file ảnh<br/>raw/thumbs/?"}
    S4B["STEP_04b · KIỂM ĐỊNH ẢNH<br/>Ảnh có phân biệt thắng/thua?"]
    S4G["STEP_04g · BRIEF ẢNH<br/>Nhóm top dựng ảnh thế nào?"]
    HAA{"Có file DSP<br/>raw/audio/?"}
    S4H["STEP_04h · BRIEF NHẠC<br/>Nhóm top dựng nhạc thế nào?"]

    S0 --> S1 --> S2 --> GATE
    GATE -->|"Không"| STOP
    GATE -->|"Có"| S3 --> S4
    S4 --> S5 & S6
    S4 -.-> HAS
    HAS -->|"Có"| S4B --> S4G
    HAS -->|"Không"| S5
    S3 --> S7
    S5 & S6 & S7 --> S8
    S8 --> S10["STEP_10 · PLAYBOOK — CÔNG THỨC THẮNG<br/>Vào thì LÀM GÌ?"]
    S4G -.->|"brief riêng"| OUT["BRIEF tái tạo ảnh<br/>(không vào điểm số)"]
    S4G -.-> S10
    S4 -.-> HAA
    HAA -->|"Có"| S4H
    S4H -.-> S10
    S10 --> WF["CHANNEL_PLAYBOOK.json<br/>→ workflow sản xuất tự động"]

    style GATE fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style HAS fill:#fff3e0,stroke:#e65100
    style STOP fill:#ffebee,stroke:#c62828
    style S8 fill:#e8f5e9,stroke:#2e7d32
    style S4B stroke-dasharray:4 3
    style S4G stroke-dasharray:4 3
    style OUT fill:#f3e5f5,stroke:#6a1b9a,stroke-dasharray:4 3
    style S10 fill:#e8f5e9,stroke:#2e7d32
    style HAA fill:#fff3e0,stroke:#e65100
    style S4H stroke-dasharray:4 3
    style WF fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```

> **Nét đứt = nhánh tùy chọn.** STEP_04b/04g chỉ chạy khi có file ảnh, STEP_04h chỉ chạy khi
> có file DSP âm thanh. Cả hai **không tác động điểm số** — chúng trả lời câu hỏi khác (xem §2.4).

### 2.1 Vì sao có CỔNG QUYẾT ĐỊNH sau STEP_02

Đây là điểm khác biệt lớn nhất so với quy trình tuyến tính thông thường.

STEP_02 trả lời câu hỏi **sống còn**: *cầu có tăng nhanh hơn cung không?*
Nếu **không** → mọi phân tích sau (công thức thắng, chân dung khách hàng, từ khóa) đều là **tối ưu hóa một con tàu đang chìm**.

| Kết quả STEP_02 | Hành động |
|---|---|
| `M2.4 ≥ 1.0` — cầu ≥ cung | ✅ Đi tiếp bình thường |
| `M2.4` trong `[0.5, 1.0)` | ⚠️ Đi tiếp nhưng **đổi câu hỏi**: không hỏi "vào hay không" mà hỏi "vào bằng khác biệt gì" |
| `M2.4 < 0.5` | 🛑 Dừng, trừ khi có lý do chiến lược khác |

> **Ví dụ thật — và bài học:** khảo sát sơ bộ Christian Blues báo `M2.4 ≈ 0.35` → vùng "dừng".
> Nhưng con số đó **SAI**: nó so cửa sổ 0–90 ngày (chỉ 36% video đã chín) với cửa sổ 90–180 ngày
> (100% đã chín). Tính lại trên hai cửa sổ **đều chín** → **`M2.4 = 1.305`**, ngách khỏe.
> Cổng quyết định suýt loại nhầm một ngách tốt. Xem bẫy **L1** trong `lessons_learned.md`.

### 2.2 Vì sao STEP_05 và STEP_06 chạy sau STEP_04

Không phải thứ tự tùy tiện:

- **STEP_04 chọn ra video thắng** → STEP_05 chỉ đọc comment **của những video đó** (không phải toàn bộ 145k)
- **STEP_04 loại bỏ giả thuyết sai** → STEP_06 không phí công phân tích từ khóa theo hướng đã bị bác bỏ

Đảo thứ tự sẽ phải quét toàn bộ dữ liệu → vi phạm nguyên tắc chọn lọc.

> ⚠️ **STEP_04 KHÔNG "xác định công thức".** Nó chỉ **loại trừ** — kết quả điển hình
> 0/20 đặc trưng đứng vững. Công thức sản xuất là đầu ra của **STEP_10**, bước tổng hợp
> sau khi đã có 04b (thumbnail thật), 05 (khán giả), 06 (từ khóa).
>
> Đây từng là nguồn hiểu nhầm: bước tên *"Công thức thắng"* lại nằm **trước** mọi phân tích
> hợp thành công thức. Đã đổi tên thành **SÀNG LỌC ĐỐI CHỨNG** (bài học T29).

### 2.3 Nhánh song song

| Chạy song song được | Vì sao |
|---|---|
| STEP_05 ‖ STEP_06 | Cùng đọc output STEP_04, không phụ thuộc nhau |
| STEP_07 ‖ (STEP_04→06) | Chỉ cần output STEP_03 |
| STEP_04b/04g ‖ (STEP_05→07) | Nhánh ảnh độc lập, không tác động điểm số |
| STEP_04h ‖ (STEP_05→07) | Nhánh nhạc độc lập, chỉ cần `video_id` |

### 2.4 HAI LOẠI CÂU HỎI — quyết định phương pháp

> Bài học đắt nhất của dự án (2026-08-17). Cùng một bộ dữ liệu, hai câu hỏi khác nhau
> đòi hai phương pháp khác hẳn. Chọn nhầm thì làm đúng quy trình mà ra sai thứ người dùng cần.

```mermaid
flowchart LR
    Q{"Người dùng<br/>muốn gì?"}
    Q -->|"Làm thế này<br/>CÓ THẮNG không?"| A["KIỂM ĐỊNH<br/>—<br/>so nhóm thắng vs thua<br/>kiểm 3 lớp chống Simpson<br/>ngưỡng p &lt; 0.01 và δ ≥ 0.30"]
    Q -->|"Nhóm thắng<br/>ĐANG LÀM thế nào?"| B["BRIEF<br/>—<br/>mô tả nhóm top<br/>trung vị + khoảng tứ phân vị<br/>không cần đối chứng"]
    A --> A2["Kết quả thường là<br/>KHÔNG CHỨNG MINH ĐƯỢC"]
    B --> B2["Kết quả là<br/>CÔNG THỨC SAO CHÉP ĐƯỢC"]

    style A fill:#e3f2fd,stroke:#1565c0
    style B fill:#f3e5f5,stroke:#6a1b9a
    style A2 fill:#ffebee,stroke:#c62828
    style B2 fill:#e8f5e9,stroke:#2e7d32
```

| | KIỂM ĐỊNH (STEP_04b) | BRIEF (STEP_04g) |
|---|---|---|
| **Câu hỏi** | Đặc điểm X có gây ra thành công? | Nhóm thành công trông thế nào? |
| **Cần đối chứng?** | **Bắt buộc** (rổ B4) | Không |
| **Cần kiểm Simpson?** | **Bắt buộc** 3 lớp | Không |
| **Nguồn** | toàn bộ + rổ đối chứng | chỉ top 5% |
| **Đầu ra** | xác nhận / bác bỏ | trung vị + khoảng + prompt mẫu |
| **Bước áp dụng** | STEP_04, 04b | STEP_04g (ảnh), **STEP_04h (nhạc)** |
| **Kết quả điển hình** | 0/12 xác nhận | công thức dùng được ngay |
| **Dùng để** | quyết định vào ngách | sản xuất hàng loạt |

**Quy tắc:** hỏi người dùng cần **đầu ra** gì *trước khi* chọn phương pháp.
Nếu họ cần "tái tạo được" → làm brief. Nếu họ cần "có nên tin không" → làm kiểm định.
Hai cái **không thay thế nhau**, và brief **không được** trình bày như bằng chứng nhân quả.

---

## 3. WORKFLOW DỮ LIỆU — TỪ FILE THÔ ĐẾN BÁO CÁO

```mermaid
flowchart TB
    RAW["00_input/raw/*.xlsx<br/><i>BẤT BIẾN</i>"]

    subgraph A0["A0 · DATA ENGINEER (STEP_01)"]
        T1["normalize<br/>xlsx → parquet"]
        T2["enrich<br/>+age_days +vpd<br/>+outlier_ratio"]
        T3["select<br/>áp 4 rổ + 3 tầng"]
        T4["validate<br/>5 kiểm tra"]
    end

    P1["processed/channels.parquet"]
    P2["processed/videos.parquet"]
    P3["processed/comments.parquet"]
    P4["processed/selected_videos.parquet<br/><b>~13% tổng số</b>"]
    P5["processed/selected_comments.parquet<br/><b>~5% tổng số</b>"]

    subgraph AN["TẦNG PHÂN TÍCH"]
        A1["A1 Quy mô"]
        A2["A2 Đối thủ"]
        A3["A3 Outlier"]
        A4["A4 Khán giả"]
        A5["A5 Từ khóa"]
        A6["A6 Kiếm tiền"]
    end

    MET["_state/metrics.json<br/><i>chỉ số thô, chưa chấm</i>"]
    SCO["_state/scores.json<br/><i>điểm + truy vết</i>"]
    REP["99_report/FINAL.md"]

    RAW --> T1 --> T2 --> T3 --> T4
    T4 --> P1 & P2 & P3 & P4 & P5
    P1 --> A1 & A2 & A6
    P2 --> A1
    P4 --> A2 & A3 & A5
    P5 --> A4
    A1 & A2 & A3 & A4 & A5 & A6 --> MET
    MET -->|"scoring_engine<br/>rubric v1.0"| SCO
    SCO --> REP

    style RAW fill:#eceff1
    style MET fill:#e3f2fd
    style SCO fill:#fff3e0
    style REP fill:#e8f5e9
```

**Điểm mấu chốt:** `metrics.json` và `scores.json` **tách riêng**.
Agent phân tích chỉ ghi vào `metrics.json` (số thô). Chỉ `scoring_engine` mới ghi `scores.json`. Đây là cách thực thi quy tắc R2.

---

## 4. CÁCH AGENT ĐỌC FILE VÀ LIÊN KẾT THÔNG TIN

### 4.1 Nghi thức khởi động — mọi agent đều làm

```mermaid
flowchart TB
    START(["Agent được gọi"])
    R1["1 · Đọc README.md<br/>hiểu hệ thống"]
    R2["2 · Đọc framework/01_agents/&lt;mã&gt;.md<br/>hiểu vai của mình"]
    R3["3 · Đọc niches/&lt;ngách&gt;/NICHE_BRIEF.md<br/>hiểu ngách"]
    R4["4 · Đọc niches/&lt;ngách&gt;/PROGRESS.md<br/>biết bước trước ra gì"]
    R5["5 · Đọc output bước phụ thuộc<br/>theo FILE_CONTRACTS"]
    R6["6 · Đọc framework/02_steps/STEP_&lt;n&gt;.md<br/>làm theo runbook"]
    WORK["THỰC THI"]
    W1["7 · Ghi output đúng đường dẫn khai báo"]
    W2["8 · Ghi metric vào _state/metrics.json"]
    W3["9 · Cập nhật PROGRESS.md"]
    END(["Xong"])

    START --> R1 --> R2 --> R3 --> R4 --> R5 --> R6 --> WORK --> W1 --> W2 --> W3 --> END
```

**Bước 4 quan trọng nhất:** `PROGRESS.md` là **bộ nhớ chung**. Agent không đọc nó sẽ làm lại việc đã có, hoặc dùng giả định sai.

### 4.2 Ba cơ chế liên kết thông tin

| Cơ chế | Dùng khi | File |
|---|---|---|
| **Truyền qua file** | Bước sau cần output bước trước | `FILE_CONTRACTS.md` khai báo |
| **Sổ chỉ số chung** | Nhiều agent cùng góp số cho rubric | `_state/metrics.json` |
| **Nhật ký tiến độ** | Biết trạng thái toàn cục | `PROGRESS.md` |

### 4.3 Ví dụ liên kết thật — A4 Audience Researcher

```mermaid
flowchart LR
    subgraph IN["A4 ĐỌC"]
        I1["selected_comments.parquet<br/><i>~6.800 comment</i>"]
        I2["04_outlier/winning_formula.md<br/><i>biết video nào thắng</i>"]
        I3["03_competitor/channel_map.md<br/><i>biết kênh nào là AI</i>"]
    end
    A4["A4 · AUDIENCE<br/>RESEARCHER"]
    subgraph OUT["A4 GHI"]
        O1["05_audience/01_personas.md"]
        O2["05_audience/02_voice_of_customer.md"]
        O3["metrics.json<br/><i>+audience.*</i>"]
    end
    I1 & I2 & I3 --> A4 --> O1 & O2 & O3
```

A4 đọc output của A3 để biết **comment nào đáng đọc** — thay vì quét 145.150 comment.
Đây là cách "chọn lọc" được thực thi ở cấp workflow, không chỉ ở cấp lọc dữ liệu.

---

## 5. TÁM AGENT — BẢNG TỔNG

| Mã | Tên | Step | Đọc | Ghi |
|---|---|---|---|---|
| **A0** | Data Engineer | 01 | `raw/*` | `processed/*.parquet` |
| **A1** | Market Analyst | 02 | `channels`, `videos` | `02_market/` |
| **A2** | Competitor Analyst | 03 | `channels`, `selected_videos` | `03_competitor/` |
| **A3** | Outlier Miner | 04 | `selected_videos`, `thumbnails` | `04_outlier/` |
| **A4** | Audience Researcher | 05 | `selected_comments`, A3 output | `05_audience/` |
| **A5** | Keyword Analyst | 06 | `selected_videos`, A3 output | `06_keyword/` |
| **A6** | Monetization Analyst | 07 | `channels`, A2 output | `07_monetization/` |
| **A7** | Synthesizer | 08 | tất cả + `scores.json` | `99_report/` |

Chi tiết từng agent: `framework/01_agents/`

---

## 6. NGUYÊN TẮC PHÂN TÍCH DỮ LIỆU

### 6.1 Phân tầng công cụ — tiết kiệm chi phí

```mermaid
flowchart LR
    D["Toàn bộ dữ liệu"]
    T1["TẦNG 1 · PYTHON<br/>100% dữ liệu<br/><i>đếm, thống kê, tương quan</i>"]
    T2["TẦNG 2 · LỌC<br/>quy tắc cứng<br/><i>7.193 → 965</i>"]
    T3["TẦNG 3 · LLM NHẸ<br/>phân loại hàng loạt<br/><i>gắn nhãn 6.800 comment</i>"]
    T4["TẦNG 4 · LLM MẠNH<br/>~300 mẫu tinh hoa<br/><i>tổng hợp insight</i>"]
    D --> T1 --> T2 --> T3 --> T4
```

**Quy tắc:** thống kê mô tả **không bao giờ** dùng LLM. Chỉ dùng LLM cho việc *hiểu ngôn ngữ*.

### 6.2 Sáu quy tắc phân tích bắt buộc

| # | Quy tắc | Chống lỗi gì |
|---|---|---|
| D1 | Dùng **trung vị**, không dùng trung bình | View phân bố đuôi dài |
| D2 | **Chuẩn hóa theo chính kênh** trước khi so sánh | Kênh to video nào cũng nhiều view |
| D3 | Chuẩn hóa theo **tuổi video** (`vpd`) | Video cũ tích view lâu hơn |
| D4 | Luôn có **nhóm đối chứng** | Survivorship bias |
| D5 | Ghi **giả thuyết trước** khi chạy | Confirmation bias |
| D6 | Báo cáo cả **bằng chứng phản bác** | Thiên lệch xác nhận |

### 6.3 Ba câu hỏi phải trả lời trước mọi kết luận

1. **So với cái gì?** — Không có mốc so sánh thì con số vô nghĩa
2. **Có thể do nguyên nhân khác không?** — Liệt kê ít nhất một cách giải thích ngược
3. **Độ tin cậy bao nhiêu?** — cao / vừa / thấp, kèm lý do

---

## 7. QUẢN LÝ TRẠNG THÁI

### 7.1 `PROGRESS.md` — bộ nhớ chung

Mỗi bước xong phải cập nhật. Định dạng cố định:

```markdown
## STEP_02 · Quy mô & động lượng
- Trạng thái: ✅ XONG | 🔄 ĐANG CHẠY | ⬜ CHƯA | 🛑 CHẶN
- Chạy lúc: 2026-08-15
- Output: 02_market/01_market_sizing.md
- Phát hiện chính: M2.4 = 0.35 → cảnh báo pha loãng
- Độ tin cậy: Vừa (chỉ 1 snapshot)
- Cảnh báo cho bước sau: cần tách kênh rác khỏi kênh tốt
```

### 7.2 `_state/metrics.json` — sổ chỉ số

Mọi agent **thêm** vào, không ghi đè phần của agent khác:

```json
{
  "niche": "christian-blues",
  "market":     { "M1_1_views_month": 10573212, "...": "..." },
  "momentum":   { "M2_4_demand_supply_gap": 0.35 },
  "entry":      { "M3_2_newcomer_success_rate": null },
  "_meta": {
    "M2_4_demand_supply_gap": {
      "source": "processed/videos.parquet",
      "computed_by": "A1",
      "computed_at": "2026-08-15",
      "confidence": "medium",
      "caveat": "chỉ 1 snapshot, suy từ published_at"
    }
  }
}
```

Trường `_meta` là bắt buộc — thực thi quy tắc R3 và R5.

---

## 8. PIPELINE CODE — SCRIPT NÀO CHẠY LÚC NÀO

> Mục §2 mô tả *khái niệm* các bước. Mục này map sang **file thật** để chạy.

```mermaid
flowchart TB
    subgraph EX["extract/"]
        NRM["normalize.py<br/><small>xlsx → parquet</small>"]
    end
    subgraph TR["transform/"]
        ENR["enrich.py<br/><small>7 kiểm chất lượng<br/>+ 8 cột làm giàu</small>"]
        FLT["apply_filters.py<br/><small>4 rổ B1–B4</small>"]
    end
    subgraph AN["analyze/"]
        A2["step02_market.py"]
        A3["step03_competitor.py"]
        A4["step04_outlier.py"]
        A5["step05_audience.py"]
        A6["step06_keyword.py"]
        A7["step07_monetization.py"]
        A8["step08_synthesis.py"]
        A9["step09_data_audit.py"]
    end
    subgraph TH["analyze/ · nhánh ảnh (tùy chọn)"]
        T1["step04c_thumbnail_full.py<br/><small>trích đặc trưng hình học</small>"]
        T2["step04b_thumbnail.py<br/><small>so B1 vs B4</small>"]
        T3["step04d_thumbnail_top.py<br/><small>nhóm top + kiểm Simpson</small>"]
        T4["step04g_brief_extract.py<br/><small>YOLO-seg + OCR → brief</small>"]
    end
    subgraph SC["scoring/"]
        SE["scoring_engine.py<br/><small>file DUY NHẤT ghi scores.json</small>"]
        VR["verify_rubric.py<br/><small>tự kiểm doc↔code↔điểm</small>"]
        BT["backtest.py"]
    end
    subgraph RP["report/"]
        CH["charts*.py"]
        BR["build_T11…T14 · 4 tài liệu chuẩn<br/>build_final_summary · build_detail"]
    end

    NRM --> ENR --> FLT --> A2 --> A3 --> A4
    A4 --> A5 & A6
    A3 --> A7
    A5 & A6 & A7 --> A8 --> SE --> VR
    A9 -.-> A8
    FLT -.-> T1 --> T2 --> T3
    T1 --> T4
    SE --> CH --> BR
    T3 & T4 -.-> BR
    BT -.->|"hiệu chuẩn"| SE

    style SE fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style VR fill:#e8f5e9,stroke:#2e7d32
    style TH stroke-dasharray:4 3
```

### 8.1 Chạy toàn bộ bằng một lệnh

```bash
bash pipeline/run_all.sh                          # nhánh lõi + PDF   (~50 giây)
bash pipeline/run_all.sh --with-thumbs            # thêm nhánh ảnh    (~15 phút)
bash pipeline/run_all.sh niches/<ngách> --no-pdf  # ngách khác, bỏ PDF
```

### 8.2 Quy ước đặt tên

| Tiền tố | Nghĩa |
|---|---|
| `stepNN_` | tương ứng STEP_NN trong `02_steps/` |
| `stepNNx_` | nhánh phụ của STEP_NN (`04b`, `04c`, `04d`, `04g`) |
| `build_T1N_*.py` | sinh một trong **bốn tài liệu chuẩn** T1.1–T1.4 (xem `11_OUTPUT_CONTRACT.md`) |
| `build_reportNN.py` | ⚠️ **quy ước cũ** — 7 file theo STEP đã chuyển vào `_archive/report_by_step/` (2026-08-28) |
| `chartsNN.py` | vẽ biểu đồ cho STEP_NN, chạy **trước** `build_report` |
| `_archive/` | script đã loại bỏ, **không** thuộc pipeline |

### 8.3 Ba bất biến của code

| # | Bất biến | Vì sao |
|---|---|---|
| 1 | **Chỉ `scoring_engine.py` được ghi `scores.json`** | Chống "tự chấm tự khen" (quy tắc R2) |
| 2 | **Script phân tích không sửa `00_input/raw/`** | Nguồn sự thật bất biến (R1) |
| 3 | **Mọi script nhận `niche_path` làm tham số 1** | Chạy được cho ngách bất kỳ |

---

## 9. SƠ ĐỒ QUAN HỆ TÀI LIỆU

```mermaid
flowchart TB
    RM["README.md<br/><i>điểm vào</i>"]
    ARCH["01_ARCHITECTURE.md<br/><i>bạn đang đọc</i>"]
    DM["02_DATA_MODEL.md"]
    RUB["03_SCORING_RUBRIC.md"]
    SEL["04_SELECTION_LOGIC.md"]
    FC["05_FILE_CONTRACTS.md"]
    AG["01_agents/A0…A7"]
    ST["02_steps/STEP_00…08"]
    NB["NICHE_BRIEF.md"]
    PR["PROGRESS.md"]

    RM --> ARCH
    ARCH --> DM & RUB & SEL & FC
    FC --> AG
    AG --> ST
    ST -->|"đọc cấu hình"| NB
    ST -->|"cập nhật"| PR

    style RM fill:#e8f5e9
    style ARCH fill:#e3f2fd
```

| Đọc khi | File |
|---|---|
| Lần đầu tiếp cận hệ thống | `README.md` → file này |
| Cần hiểu schema dữ liệu | `02_DATA_MODEL.md` |
| Cần hiểu cách chấm điểm | `03_SCORING_RUBRIC.md` |
| Cần biết agent đọc/ghi gì | `05_FILE_CONTRACTS.md` |
| **Bốn tài liệu đầu ra T1.1–T1.4** | **`11_OUTPUT_CONTRACT.md`** |
| **Sáu nhóm nguồn Y·P·S·V·K·N** | **`10_SOURCE_CLASSES.md`** |
| Sắp chạy một bước | `02_steps/STEP_<n>.md` |
| Muốn biết đang ở đâu | `niches/<ngách>/PROGRESS.md` |

---

## 10. HỆ THỐNG NÀY KHÔNG LÀM GÌ

Nói rõ giới hạn để không kỳ vọng sai:

| Không làm | Vì sao |
|---|---|
| Không tự crawl dữ liệu | Crawl là khâu riêng, hệ thống này bắt đầu từ dữ liệu đã có |
| Không dự đoán view tương lai | Chỉ đo trạng thái hiện tại và xu hướng đã xảy ra |
| Không thay quyết định kinh doanh | Đưa bằng chứng có cấu trúc, người quyết |
| Không phân tích được thứ dữ liệu không có | Ví dụ: retention, CTR, traffic source — YouTube API không trả về cho kênh người khác |
