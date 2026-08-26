# HỆ THỐNG NGHIÊN CỨU THỊ TRƯỜNG NGÁCH YOUTUBE

> **Đây là file đọc đầu tiên.** Mọi agent và mọi người bắt đầu từ đây.
> Phiên bản hệ thống: **v2.0** · Cập nhật: 2026-08-15

---

## 1. HỆ THỐNG NÀY LÀ GÌ

Một quy trình nghiên cứu ngách YouTube **tái sử dụng được**: cùng một khung, chạy cho ngách nào cũng được, ra kết quả so sánh được với nhau.

**Nguyên tắc kiến trúc cốt lõi:**

```
framework/   = KHUNG CHUNG      → không đổi giữa các ngách
niches/      = DỮ LIỆU RIÊNG    → mỗi ngách một thư mục
```

Nghiên cứu ngách mới = tạo thư mục mới trong `niches/`, **không sửa gì trong `framework/`**.
Nếu phải sửa `framework/` → nghĩa là khung còn thiếu, phải nâng cấp khung chứ không vá riêng cho một ngách.

---

## 2. BẢN ĐỒ THƯ MỤC

```
.
├── README.md                    ← BẠN ĐANG Ở ĐÂY
│
├── framework/                   ═══ KHUNG CHUNG — DÙNG LẠI CHO MỌI NGÁCH ═══
│   ├── 00_system/               Thiết kế hệ thống
│   │   ├── 01_ARCHITECTURE.md       Kiến trúc + workflow diagram tổng
│   │   ├── 02_DATA_MODEL.md         Schema dữ liệu, quan hệ bảng
│   │   ├── 03_SCORING_RUBRIC.md     Cơ chế chấm điểm 6 trục
│   │   ├── 04_SELECTION_LOGIC.md    Logic lọc chọn lọc
│   │   └── 05_FILE_CONTRACTS.md     Hợp đồng file: ai đọc gì, ghi gì
│   │
│   ├── 01_agents/               Đặc tả từng agent
│   │   ├── A0_data_engineer.md
│   │   ├── A1_market_analyst.md
│   │   ├── A2_competitor_analyst.md
│   │   ├── A3_outlier_miner.md
│   │   ├── A4_audience_researcher.md
│   │   ├── A5_keyword_analyst.md
│   │   ├── A6_monetization_analyst.md
│   │   └── A7_synthesizer.md
│   │
│   ├── 02_steps/                Quy trình từng bước (runbook)
│   │   ├── STEP_00_setup.md
│   │   ├── STEP_01_foundation.md
│   │   ├── STEP_02_market.md
│   │   ├── STEP_03_competitor.md
│   │   ├── STEP_04_outlier.md
│   │   ├── STEP_04b_thumbnail.md    (tùy chọn — khi có raw/thumbs/)
│   │   ├── STEP_05_audience.md
│   │   ├── STEP_06_keyword.md
│   │   ├── STEP_07_monetization.md
│   │   ├── STEP_08_synthesis.md
│   │   └── STEP_10_playbook.md      ← đầu vào cho workflow sản xuất
│   │
│   ├── 03_templates/            Mẫu output chuẩn
│   └── 04_reference/            Tài liệu tham chiếu, bài học
│
└── niches/                      ═══ DỮ LIỆU RIÊNG TỪNG NGÁCH ═══
    └── christian-blues/
        ├── NICHE_BRIEF.md           Định nghĩa ngách + cấu hình
        ├── PROGRESS.md              Trạng thái: bước nào xong, bước nào chưa
        ├── 00_input/raw/            Dữ liệu thô (bất biến)
        ├── 00_input/processed/      Parquet đã chuẩn hóa
        ├── 02_market/ … 07_*/       Output từng agent
        ├── 99_report/               Báo cáo cuối
        └── _state/                  metrics.json, scores.json
```

---

## 3. CÁCH CHẠY MỘT NGÁCH MỚI

```
1. Đọc framework/00_system/01_ARCHITECTURE.md      hiểu toàn cảnh
2. Copy framework/03_templates/NICHE_BRIEF.md      → niches/<tên-ngách>/
3. Điền NICHE_BRIEF.md                             định nghĩa ngách
4. Đặt dữ liệu crawl vào 00_input/raw/
5. Chạy tuần tự STEP_00 → STEP_08
6. Mỗi step xong → cập nhật PROGRESS.md
```

**Không cần nhớ gì thêm.** Mỗi `STEP_*.md` tự chứa: đọc file nào, làm gì, ghi file nào, tiêu chí xong.

---

## 4. TÁM BƯỚC — TỔNG QUAN

| Step | Tên | Agent | Trả lời câu hỏi |
|---|---|---|---|
| **00** | Setup | — | Ngách này là gì? Dữ liệu có gì? |
| **01** | Nền móng | A0 | Dữ liệu sạch chưa? Lọc còn bao nhiêu? |
| **02** | Quy mô & động lượng | A1 | Ngách đang lên hay xuống? |
| **03** | Đối thủ | A2 | Ai đang thắng? Còn cửa không? |
| **04** | Sàng lọc đối chứng | A3 | Đặc trưng nào KHÔNG phân biệt thắng/thua? |
| **04b** | Thumbnail (ảnh thật) | A3 | Ảnh có quyết định kết quả không? *(chạy khi có `raw/thumbs/`)* |
| **04g** | Brief tái tạo ảnh | A3 | Nhóm dẫn đầu dựng ảnh thế nào? → công thức sản xuất |
| **05** | Chân dung khách hàng | A4 | Khách là ai? Vì sao xem? |
| **06** | Từ khóa & đóng gói | A5 | Nội dung truyền tải thế nào? |
| **07** | Kiếm tiền & rủi ro | A6 | Ra tiền không? Rủi ro gì? |
| **08** | Tổng hợp | A7 | Vào hay không? |
| **10** | **Playbook khởi tạo kênh** | A7 | **Vào thì LÀM GÌ?** → title · description · tag · thời lượng · nhịp đăng · 5 kênh mẫu |
| **10** | **Playbook khởi tạo kênh** | A7 | **Vào thì làm gì?** → title, description, tag, thời lượng, nhịp đăng, 5 kênh mẫu |

> **STEP_01 + STEP_02 nên chạy gộp** — vì STEP_02 trả lời câu hỏi sống còn (*ngách còn đáng vào không?*). Nếu kết quả xấu thì dừng sớm, tiết kiệm 6 bước sau. Xem `STEP_01_foundation.md` §Gộp bước.

---

## 4b. RUBRIC — CƠ CHẾ CHẤM ĐIỂM

**Rubric = bảng tiêu chí chấm điểm có ngưỡng cố định**, để hai người chấm cùng dữ liệu ra cùng kết quả.

```
SCORE = (T1×20% + T2×25% + T3×25% + T4×15% + T5×10%) × 4 − T6
```

| Trục | Tên | Trọng số | Đo gì |
|---|---|---|---|
| T1 | Quy mô | 20% | Views/tháng — ngách đủ lớn không |
| T2 | Động lượng | 25% | Cầu tăng nhanh hơn cung không |
| T3 | Cửa gia nhập | 25% | Người mới còn cửa không |
| T4 | Phù hợp AI | 15% | % kênh top là AI-first |
| T5 | Kiếm tiền | 10% | RPM ước tính |
| T6 | Rủi ro | điểm **trừ** | Trùng lặp, policy, phụ thuộc |

| Điểm | Xếp loại |
|---|---|
| 16–20 | Ưu tiên cao |
| 13–15.9 | Tiềm năng |
| 10–12.9 | Theo dõi |
| < 10 | Bỏ qua |

📖 **Đọc đầy đủ:** `framework/00_system/03_SCORING_RUBRIC.md` — bắt đầu từ **§0 "Rubric là gì"**.

---

## 4c. CHẠY LẠI TOÀN BỘ

```bash
bash pipeline/run_all.sh                   # chạy lại từ dữ liệu thô → chấm điểm → PDF  (~50s)
bash pipeline/run_all.sh --with-thumbs     # thêm nhánh phân tích ảnh          (~15 phút)
python3 pipeline/_common.py niches/<mới>   # dựng khung thư mục cho ngách mới
python3 pipeline/scoring/verify_rubric.py  # kiểm tài liệu rubric có khớp code không
```

---

## 4d. BẢN MÔ PHỎNG SẢN PHẨM (`_web/`)

Năm trang HTML tĩnh mô phỏng sản phẩm sẽ trông thế nào khi thành phần mềm.
Dữ liệu nhúng thẳng vào file nên **mở là chạy, không cần cài gì**.

```bash
bash _web/serve.sh          # tự chọn cổng trống rồi mở trình duyệt
```

| Trang | Nội dung |
|:---|:---|
| `index.html` | Trang chủ, dẫn vào ba bản |
| `data-tho.html` | **Bước 1** — chọn dự án → danh sách kênh → 6 bảng dữ liệu thô (142 cột) + tab **Sơ đồ dữ liệu** |
| `chuan-hoa.html` | **Bước 2** — hai trạm: làm dày (13 cột tính thêm) rồi lọc chọn (4 rổ), kèm bảng trải phẳng 7.193 dòng và xuất CSV |
| `ba-tram.html` | Bản trình bày "Ba trạm chưng cất dữ liệu" |
| `ban-du-lieu.html` | Bản cũ, giữ để đối chiếu |

**Sơ đồ dữ liệu** (tab trong Bước 1) vẽ 9 bảng và 9 cạnh nối, **độ dày đường
nối tỉ lệ với độ phủ thật đã đo** — thumbnail 100% nét đậm, audio 0,4% nét
đứt. Vẽ vậy để người đọc và AI không tưởng mọi bảng đều đầy như nhau.

Số liệu trên web đọc từ `00_input/processed/*.parquet` lúc dựng, không gõ
tay (quy tắc T27). Ở ngưỡng mặc định, Bước 2 ra đúng **B1=435 · B2=366 ·
B3=264 · B4=161 · hợp nhất 965**, khớp từng nhãn với `selected_videos.parquet`.

Riêng cột `+/−`, `%` và `30 phiên` ở Bước 1 là **dữ liệu mô phỏng** — hệ
thống mới có một phiên crawl thật. Trang có băng đỏ báo rõ và công tắc tắt.

---

## 4e. DỮ LIỆU KHÔNG CÓ TRONG REPO NÀY

Kho này **công khai**, nên một số file ở lại trên máy và không được đẩy lên.
Chúng vẫn nằm nguyên trên đĩa người chạy, chỉ không vào git.

| Không đẩy | Vì sao | Ảnh hưởng |
|:---|:---|:---|
| `selected_comments.parquet`<br>`_comments_tagged.parquet`<br>`03_quote_bank.csv` | Có `author_name` là **tên tài khoản YouTube thật**, nội dung bình luận nguyên văn, và các cột `disabled` · `widow` · `veteran` · `recovery`. Ghép định danh với thuộc tính sức khoẻ / hoàn cảnh rồi công khai là phát tán hồ sơ về người thật (quy tắc R6) | **STEP_05** (khán giả) cần crawl lại bằng khoá API riêng |
| `comments.parquet` | 145.150 bình luận do người thật viết | như trên |
| `lyrics_raw.parquet` | Lời hát nguyên văn — tác phẩm có bản quyền (T65). Đặc trưng đã trích sang `lyrics_features.parquet` | Không ảnh hưởng: phân tích lời dùng bản đặc trưng |
| `00_input/raw/*.xlsx` | File nguồn 21 MB của bên thứ ba | Không ảnh hưởng: đã trích sang parquet |
| Audio, thumbnail gốc, model | Dung lượng (2,3 GB + 1,1 GB) | Thumbnail **không tái tạo được** bằng script; đặc trưng đã có sẵn trong `thumbnails.parquet` |

Các bước còn lại chạy bình thường với dữ liệu trong repo.

---

## 5. QUY TẮC BẤT BIẾN

| # | Quy tắc | Lý do |
|---|---|---|
| R1 | `00_input/raw/` **không bao giờ bị sửa** | Nguồn sự thật, phải tái lập được |
| R2 | Agent phân tích **không tự chấm điểm** | Chống "tự chấm tự khen" |
| R3 | Mọi điểm số phải có **metric → ngưỡng → bằng chứng → nguồn** | Truy vết được |
| R4 | Mỗi bước ghi **đúng file đã khai báo** trong `05_FILE_CONTRACTS.md` | Bước sau biết chỗ đọc |
| R5 | Kết luận phải kèm **độ tin cậy** (cao/vừa/thấp) | Biết chỗ nào chắc |
| R6 | Thuộc tính nhân khẩu chỉ ghi khi **người dùng tự khai** | Đạo đức nghiên cứu |
| R7 | Sửa ngưỡng rubric → **chạy lại toàn bộ ngách** | Giữ tính so sánh được |

---

## 6. TRẠNG THÁI HIỆN TẠI

| Ngách | Trạng thái | Điểm | Kết luận | Bước tiếp theo |
|---|---|---|---|---|
| `christian-blues` | ✅ **STEP_00→08 + 04b hoàn tất** | **12.05/20** | Theo dõi — vào có điều kiện | Chạy snapshot lần 2 · nghiên cứu âm nhạc |

**9 báo cáo PDF** + **`09_playbook/CHANNEL_PLAYBOOK.json`** (máy đọc) tại `niches/christian-blues/99_report/`. Điểm số truy vết được tại `_state/scores.json`.

Chi tiết: `niches/christian-blues/PROGRESS.md`
