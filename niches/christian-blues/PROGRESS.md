# PROGRESS · CHRISTIAN BLUES

> Bộ nhớ chung. Đọc trước khi làm, cập nhật sau khi làm xong.
> ✅ XONG · 🔄 ĐANG CHẠY · ⬜ CHƯA · 🛑 CHẶN

| Step | Tên | Trạng thái | Ngày | Output |
|---|---|---|---|---|
| 00 | Setup | ✅ | 2026-08-15 | `NICHE_BRIEF.md` |
| 01 | Nền móng | ✅ | 2026-08-15 | `processed/*.parquet` · `quality_audit.csv` |
| 02 | Quy mô & động lượng | ✅ | 2026-08-15 | `02_market/` · PDF báo cáo |
| 03 | Đối thủ | ✅ | 2026-08-15 | `03_competitor/` · PDF báo cáo |
| 04 | Sàng lọc đối chứng | ✅ | 2026-08-15 | `04_outlier/` · PDF báo cáo |
| 04b | **Thumbnail (ảnh thật)** | ✅ | 2026-08-17 | `04_outlier/10_*` `11_*` · `99_report/STEP04b_*.pdf` |
| 04g | **BRIEF tái tạo thumbnail** | ✅ | 2026-08-17 | `THUMBNAIL_BRIEF.md` · `99_report/STEP04g_Brief-Thumbnail.pdf` |
| 04h | **BRIEF tái tạo âm nhạc** | ✅ | 2026-08-18 | `04_outlier/audio/AUDIO_BRIEF.json` · `99_report/STEP04h_Brief-Am-nhac.pdf` · khối `music` |
| — | **Refactor + đúc kết** | ✅ | 2026-08-17 | `run_all.sh` v2 · `_common.py` · `collect_metrics.py` · `apply_thresholds.py` |
| 05 | Chân dung khách hàng | ✅ | 2026-08-15 | `05_audience/` · PDF báo cáo |
| 06 | Từ khóa & đóng gói | ✅ | 2026-08-15 | `06_keyword/` · PDF báo cáo |
| 07 | Kiếm tiền & rủi ro | ✅ | 2026-08-15 | `07_monetization/` · `_state/scores.json` · PDF |
| 08 | Tổng hợp | ✅ | 2026-08-15 | `99_report/STEP08_Bao-cao-Tong-hop.pdf` |
| 10 | **Playbook khởi tạo kênh** | ✅ | 2026-08-17 | `09_playbook/CHANNEL_PLAYBOOK.json` · mục 7 báo cáo tổng hợp |
| 10b | **Hồ sơ 5 kênh hình mẫu** | ✅ | 2026-08-17 | `09_playbook/CHANNEL_PROFILES.json` · mục 7.5b–7.5c |
| 11 | **Brief âm nhạc (DSP)** | ✅ | 2026-08-18 | `04_outlier/audio/AUDIO_BRIEF.json` · `99_report/STEP11_*.pdf` · khối `music` |

---

## NHẬT KÝ

### STEP_00 · Setup — ✅ XONG
- **Chạy lúc:** 2026-08-15
- **Output:** `NICHE_BRIEF.md` · `00_input/EARLY_FINDINGS.md`
- **Phát hiện chính:**
  - Ngách rất trẻ: 39/53 kênh (74%) < 12 tháng
  - ⚠️ **Tín hiệu pha loãng:** view trung vị 4.542 → 1.341 (−70%) trong khi cung tăng 6.3×
  - Định dạng 1-6m hiệu quả hơn 1-3h **34% VPD**, nhưng thị trường đổ 43% video vào 1-3h
  - Công thức "Psalm + Blues + Lyrics" lặp ở **3 kênh khác nhau**
  - Comment 1.444 like nêu đúng lý do ngách tồn tại
- **Độ tin cậy:** Vừa — mới khảo sát sơ bộ, chưa qua pipeline chuẩn
- ⚠️ **Cảnh báo cho bước sau:**
  - `video_stats` chỉ 1 snapshot → trục T2 tối đa "vừa"
  - `media_probe` 0.6% → **không dùng kết luận nhạc lý**
  - STEP_02 **bắt buộc tách H1 (kênh rác) vs H2 (cả ngách suy)** trước khi kết luận bão hòa

### STEP_01+02 · Nền móng + Quy mô & Động lượng — ✅ XONG
- **Chạy lúc:** 2026-08-15
- **Output:** `00_input/processed/*.parquet` · `02_market/*` · `99_report/STEP01-02_*.pdf`
- **Phát hiện chính:**
  - 🔴 **SỬA LỖI LỚN:** khảo sát STEP_00 báo M2.4≈0.35 (pha loãng) là **SAI**. Nguyên nhân: so sánh cửa sổ 0-90d trong đó chỉ 36% video đã chín. Tính lại trên cửa sổ đều chín → **M2.4 = 1.305** (cầu tăng nhanh hơn cung 30.5%)
  - ✅ Vượt cổng quyết định (ngưỡng ≥1.0) → ĐI TIẾP
  - Phán quyết pha loãng: **H0** — không có pha loãng thật. VPD cả 3 phân khúc đều tăng (toàn ngách ×1.15, top20 ×2.03, còn lại ×1.83)
  - T1 = 2/5 (7.45tr view/tháng — ngách cỡ vừa)
  - T2 = 4/5 (M2.1=1.618, M2.4=1.305)
  - Bộ lọc: 965 video (13.4%) phủ **80.6% tổng view** · 6.794 comment (4.7%)
  - Khoảng trống định dạng: 43% video là mix 1-3h nhưng 1-6m có VPD cao hơn 34%
- **Độ tin cậy:** Vừa — chỉ 1 snapshot, mọi động lượng suy từ `published_at`
- ⚠️ **Cảnh báo cho bước sau:**
  - Kết quả T2 **nhạy với cách chọn cửa sổ** — luôn dùng video `is_matured`
  - Top20 tăng ×2.03 có thể là "winner-takes-most" → STEP_03 phải đo Gini + tỷ lệ kênh mới thành công
  - Giả thuyết định dạng ngắn **chưa có đối chứng** → STEP_04 kiểm bằng rổ B4
  - VPD tăng có thể do survivorship (5 kênh đã ngừng đăng) — cần theo dõi

---

### STEP_03 · Bản đồ đối thủ — ✅ XONG
- **Chạy lúc:** 2026-08-15
- **Output:** `03_competitor/02_channel_table.csv` · 4 biểu đồ · `99_report/STEP03_Ban-do-Doi-thu.pdf`
- **Phát hiện chính:**
  - ✅ **Cửa gia nhập MỞ:** M3.2 = **61.5%** (24/39 kênh <12 tháng đạt ≥100k view/tháng) → 5đ tối đa
  - ✅ **Bác bỏ winner-takes-most:** kênh lớn nhất chỉ chiếm **18.5%** tổng view
  - Gini = 0.626 · top20% = 63.1% (ngách cha Christian/Gospel = 82% → bị khóa)
  - **T3 = 4.4/5** · **T4 = 5/5**
  - M4.1 = **65%** top20 là AI-first → mô hình AI đã được chứng minh thực nghiệm
  - Phân tầng: 3 dẫn đầu · 16 thách thức · 19 đang lên · 11 hụt hơi · 4 ngừng
  - **Đánh đổi nhịp đăng:** tương quan với view/video = −0.311 nhưng với view/tháng = +0.420. Nhóm đăng dày nhất đạt tổng view **gấp 5.3×** nhóm thưa nhất
  - 3 hình mẫu thành công khác nhau: `vintage_gospel_vgx` (ít mà tinh, 70k view/video với 43 video) · `goldensoulworship` (vừa nhiều vừa tốt, 2.8 tháng tuổi) · `stillworshipmusic` (công nghiệp hóa, 511 video)
- **Độ tin cậy:** Cao cho T3 (đếm trực tiếp), Vừa cho T4 (phân loại gián tiếp)
- ⚠️ **Cảnh báo cho bước sau:**
  - **M3.3 KHÔNG đo được** với 1 snapshot — `view_count` là tích lũy, cumsum vô nghĩa. Đã thay bằng tuổi trung vị nhóm thành công (6.9 tháng)
  - Thiên lệch sống sót: kênh đã xóa không có trong dữ liệu → 61.5% có thể lạc quan
  - Đánh đổi nhịp đăng mới là **tương quan**, STEP_04 phải kiểm nhân quả bằng rổ B4

### STEP_04 · Sàng lọc đối chứng — ✅ XONG
- **Chạy lúc:** 2026-08-15
- **Output:** `04_outlier/` (6 CSV + 4 biểu đồ) · `99_report/STEP04_Sang-loc-Doi-chung.pdf`
- **Phát hiện chính — KẾT QUẢ ÂM TÍNH có giá trị:**
  - 🔴 **26 đặc trưng kiểm định → 0 đặc trưng đứng vững.** Video thắng và thua gần như giống hệt nhau ở mọi thứ đo được từ metadata
  - 🔴 **"Psalm/Kinh Thánh" KHÔNG phải công thức thắng** — nghịch lý Simpson:
    - Trong mẫu B1/B4: lift **8.1×**, p<0.001 (nhìn rất thuyết phục)
    - Toàn thị trường: lift **0.48×** (kém hơn 52%), p<0.00001
    - Trong từng kênh: chỉ **6/13** kênh tốt hơn, trung vị lift 0.82×
  - 🔴 **Loại bỏ "tỷ lệ tương tác"** — artefact toán học (B1 view gấp 82× B4 nên mẫu số lớn kéo tỷ lệ xuống). Spearman(view,eng) = −0.202 xác nhận
  - ⚠️ **Định dạng: CHƯA KẾT LUẬN.** VPD nói ngắn tốt hơn, nhưng tỷ lệ thắng B1/B4 nói 30-60m cao nhất (80.6%). Hai thước đo mâu thuẫn → cần dữ liệu retention
  - Từ khóa: hầu hết ("prayer", "god", "praise") xuất hiện ở CẢ hai nhóm → từ vựng chung, không phân biệt. Ngoại lệ yếu: `grace` (10 kênh thắng / 2 lần ở thua), `strength` (10/3)
- **Độ tin cậy:** Cao cho kết luận âm tính về **tiêu đề/metadata** (đo trực tiếp).
  ⚠️ **Thấp cho 8 đặc trưng thumbnail** — đo bằng proxy từ Excel nguồn, trong đó
  `text_score` đã được chứng minh hỏng (tương quan 0,233 với chữ thật). Kết luận
  thumbnail thật nằm ở STEP_04b/04g. Đã gắn cờ `measure="proxy"` trong CSV + PDF (T29)
- ⚠️ **Cảnh báo cho bước sau:**
  - **Metadata đã cạn tín hiệu.** Yếu tố quyết định nằm ở chất lượng nhạc / retention / CTR — dữ liệu hiện không đo được
  - Kết hợp STEP_03: khi không có công thức nội dung, **nhịp đăng đều và dày** là đòn bẩy đáng tin nhất (gấp 5.3× tổng view)
  - STEP_05 (comment) là nguồn tín hiệu lớn còn lại

### STEP_05 · Chân dung khách hàng — ✅ XONG
- **Chạy lúc:** 2026-08-15
- **Output:** `05_audience/` (quote bank 120 trích dẫn + 4 biểu đồ) · `99_report/STEP05_Chan-dung-Khach-hang.pdf`
- **Phát hiện chính:**
  - ✅ **Xác nhận nỗi đau lõi bằng thống kê:** comment chứa "finally" được like gấp **6.6×**, "never heard" gấp **6.2×** (p<0.0001)
  - ✅ **Ngách sống bằng ĐỀ XUẤT, không phải tìm kiếm** — tỷ lệ 83:12 ≈ **7:1** → SEO ít giá trị
  - ✅ **Nhạc CHỨC NĂNG, không phải giải trí** — bối cảnh số 1 là cầu nguyện/tĩnh tâm (868 cmt, 13.5%). Bệnh viện (105) + tang chế (70) > lái xe (35) + việc nhà (30)
  - 🔑 **GIẢI ĐƯỢC câu hỏi treo từ STEP_04 về định dạng:** khán giả nghe lúc cầu nguyện/bệnh tật → cần âm thanh liền mạch kéo dài → **mix 1-3h KHÔNG phải sai lầm**, nó phục vụ đúng bối cảnh
  - Tuổi tự khai trung vị **70** (n=82), 78% từ 60+ → hỗ trợ giả thuyết RPM cao
  - ⚠️ **"healing" KHÔNG phải tín hiệu** — 757 comment (nhiều nhất) nhưng like TV=3, dưới trung bình 4 → là từ vựng chung như "prayer"/"god" ở STEP_04
  - 3 persona: Tín đồ cao tuổi (n=70, like TV 24) · Người yêu blues có đức tin (n=37, nhạc công like TV **106** — cao nhất) · Người tìm chữa lành (n=967, đông nhất nhưng like TV thấp)
- **Độ tin cậy:** Cao cho tín hiệu "finally"/đề xuất; **Thấp** cho tuổi (chỉ 1.28% tự khai, thiên lệch)
- ⚠️ **Cảnh báo cho bước sau:**
  - Tuổi 70 gần như chắc chắn **cao hơn thực tế** — người lớn tuổi hay viết dài, tự giới thiệu
  - Người bình luận ≠ người xem; dữ liệu không cho biết vì sao người ta **không** xem
  - STEP_06 phải đổi trọng tâm: từ khóa để **chọn đề tài**, không phải SEO

### STEP_07 · Kiếm tiền & Rủi ro — ✅ XONG
- **Chạy lúc:** 2026-08-15
- **Output:** `07_monetization/` · **`_state/scores.json`** (chấm điểm cuối) · `99_report/STEP07_Kiem-tien-Rui-ro.pdf`
- **ĐIỂM CUỐI: 12.20/20 → "Theo dõi"**
  - T1=2.0 (20%) · T2=4.0 (25%) · T3=4.4 (25%) · T4=5.0 (15%) · T5=3.0 (10%) · T6=−2
- **Phát hiện chính:**
  - 🔑 **ĐẢO NGƯỢC kinh tế học định dạng:** video 1-6m chỉ **1 ad slot**, mix 1-3h có **~11.7 ad slot** (gấp 12×). Cộng với bối cảnh nghe (STEP_05) → **mix dài là chủ lực đúng đắn**. Khép lại tranh luận định dạng kéo dài từ STEP_01
  - RPM ước tính **$1.5–6.0** (cơ sở $3.0) — **ĐỘ TIN CẬY THẤP**, không đo được từ API
  - Doanh thu kênh trung vị: **~$319/tháng** (106,406 view/tháng)
  - ⚠️ **Rủi ro chính: trùng lặp nội dung.** 132 tiêu đề dùng chung nhiều kênh, 5 kênh có ≥30% video trùng (cao nhất `faithbluesworship` 55.4%)
  - ⚠️ **Nghịch lý:** video trùng title lại có VPD **cao hơn 68%** (15.47 vs 9.21) — copy title hiệu quả ngắn hạn nhưng rủi ro chính sách dài hạn
  - ✅ Mô tả trùng: **0 mẫu dùng chéo kênh** → chỉ là template nội bộ, KHÔNG phải rủi ro
  - ✅ Bản quyền thánh ca: chỉ 0.3% video → không đáng lo
- **So với bảng chấm thủ công cũ (12/20):** trùng số nhưng **khác lý do hoàn toàn**. Bảng cũ chấm cửa gia nhập 2đ (hệ thống: 4.4đ) và bỏ sót cả động lượng lẫn rủi ro
- ⚠️ **Rủi ro lớn nhất với kết luận:** T2 dựa trên 1 snapshot. Nếu snapshot mới cho M2.4 thấp hơn → tổng có thể xuống dưới 10 → **"Bỏ qua"**

### STEP_06 · Từ khóa & Đóng gói — ✅ XONG
- **Chạy lúc:** 2026-08-15
- **Output:** `06_keyword/` (3 CSV + 4 biểu đồ) · `99_report/STEP06_Tu-khoa-Dong-goi.pdf`
- **ĐỔI TRỌNG TÂM:** từ SEO → **chọn đề tài**, vì STEP_05 cho thấy đề xuất thắng tìm kiếm 7:1
- **Phát hiện chính:**
  - ✅ **KHOẢNG TRỐNG RÕ NHẤT: old-school / vintage / black gospel** — lift **2.37×** (cao nhất) nhưng chỉ **3.96%** thị trường khai thác. 20 kênh dùng → không phải hiện tượng 1 kênh. Khớp khán giả 70 tuổi (lớn lên cùng black gospel 1950-70)
  - ✅ Tạ ơn / biết ơn: lift 1.62× (nhưng mẫu nhỏ n=55, 3 kênh test)
  - 🔴 **NÊN TRÁNH: nhạc không lời/nhạc nền** — lift **0.17×** (kém nhất). Khán giả muốn LỜI HÁT, không phải nhạc nền
  - 🔴 **NÊN TRÁNH: Kinh Thánh/Thánh Vịnh** — lift 0.61× trên 652 video. Xác nhận lại kết luận STEP_04 bằng dữ liệu toàn thị trường
  - ⚠️ **Lớp kiểm Simpson loại 4 chủ đề** tưởng tốt: testimony (lift 1.51 nhưng 8/22 kênh), healing, strength, night_sleep
  - Tag chỉ có ở video thắng: **tên PHONG CÁCH NHẠC cụ thể** ("slow blues", "delta blues", "blues guitar") — không phải từ tôn giáo chung chung
  - Cấu trúc tiêu đề: **không khác biệt** B1 vs B4 (nhất quán STEP_04)
  - Khoảng trống ngôn ngữ: "amen" 2233 lần trong comment vs 5 lần trong title — nhưng đây là từ PHẢN HỒI, không phải từ TÌM KIẾM → chỉ dùng cho giọng điệu mô tả
- **Độ tin cậy:** Cao cho "tránh Kinh Thánh"; Vừa cho "old-school" (within-channel chỉ 4/8)
- ⚠️ **Cảnh báo:** chủ đề nhận diện bằng regex trên TIÊU ĐỀ, không phải nội dung nhạc thật

### STEP_04h · Brief âm nhạc (nhánh tái tạo) — ✅ XONG
- **Chạy lúc:** 2026-08-18
- **Nguồn:** 5 file DSP (librosa) do team khác cung cấp → `00_input/raw/audio/*.yaml`
- **Output:** `04_outlier/audio/AUDIO_BRIEF.json` · `99_report/STEP04h_Brief-Am-nhac.pdf` · khối `music` trong `CHANNEL_PLAYBOOK.json`
- **Mẫu:** 5 bản **top 0,07% lượt xem** (1,18tr–1,70tr view) — cả 5 đều khớp `videos_enriched.parquet`
- **🔴 SỬA LỖI ĐO — bẫy nhân đôi tempo (5/5 bản):**
  - YAML thô báo **103,4–161,5 BPM** cho nhạc gospel *chậm* → sai
  - Ba kiểm chéo độc lập: `beats_per_chord` 7,3–13,8 (>6) · `onsets_per_beat` 0,59–0,78 (<1) · giây/hợp âm 3,2–5,4 (<6)
  - Sau khi chia đôi: **51,7–80,8 BPM** — đúng dải slow blues/gospel ballad
  - Giữ nguyên `bpm_raw` + lý do sửa để truy vết (T38)
- **Phát hiện chính:**
  - 🟢 **5/5 bản ở điệu TRƯỞNG** (key_conf 0,74–0,96) — trái trực giác "blues phải dùng điệu thứ". Màu buồn đến từ **hợp âm thứ xen vào**, không từ điệu thức
  - ⚠️ **Bảng màu hợp âm KHÔNG có chuẩn**: thứ chiếm 7,6%–72,9%, chỉ 2/5 thiên về thứ
  - ⚠️ **Đường cong năng lượng cũng không có khuôn**: 3 dạng khác nhau trên 5 bản
  - Hợp âm đổi mỗi **6,4–10,9 giây**; syncopation thấp (0,022–0,192) — nhịp đơn giản
  - Bản dài (≥15p) dùng **gấp đôi vốn hợp âm** (24 vs 11) và gấp 2,4× số đoạn (20 vs 8,5)
- **Độ tin cậy:** **Thấp** — tầng MÔ TẢ, n=5, **không có nhóm đối chứng**. Không dùng làm bằng chứng nhân quả
- **Còn thiếu:** nhạc cụ · giọng hát · lời · LUFS. Brief cho *khung xương*, chưa cho biết bản nhạc **nghe như thế nào**

### STEP_08 · Tổng hợp & Chiến lược — ✅ XONG
- **Chạy lúc:** 2026-08-15
- **Output:** `99_report/STEP08_Bao-cao-Tong-hop.pdf` · `backtest_rubric.csv` · `_synthesis.json`
- **KẾT LUẬN CUỐI: 12.05/20 → "Theo dõi" → khuyến nghị VÀO CÓ ĐIỀU KIỆN**
  - ⚠️ *Sửa 17/08: từ 12.2 → 12.05. Nguyên nhân: M3.3 "KHÔNG ĐO ĐƯỢC" trước đây được chấm 5/5 điểm tối đa; nay chia lại trọng số cho phần đo được. Không đổi xếp loại. Xem T25.*
- **Backtest rubric trên 24 dòng nhạc FMG:**
  - Sai lệch trung bình T1 = **0.48đ**, T3 = **0.52đ** → rubric KHÔNG mâu thuẫn với đánh giá thủ công
  - ✅ **Chứng minh sửa được lỗi L1:** 4 dòng nhạc có top20% = 57.6–61.8% (gần bằng nhau) nhưng bảng cũ cho **2, 3, 4, 5 điểm**; rubric mới cho cả 4 **cùng 4 điểm**
- **Kiểm 5 giả thuyết ban đầu:** H1 ĐÚNG · H2 ĐÚNG (sau khi sửa lỗi) · H3 ĐÚNG · H4 ĐÚNG · H5 CHƯA XÁC MINH (RPM)
- **Bản đồ khoảng trống (5 khoảng trống, 18 bằng chứng truy vết được):**
  - ⚠️ *Sửa 17/08: mỗi khoảng trống trước đây chỉ có **1 câu văn xuôi** làm bằng chứng, không chỉ được nguồn. Nay `demand` là list — mỗi mục có `claim` + `src` (file + khóa) + `id` (`comment_id` để mở đúng dòng trong `03_quote_bank.csv`). Tổng **5 → 18 bằng chứng**. Xem T31.*
  - 🔴 *Sửa 17/08: `old_school` hạ tin cậy **Vừa → Thấp**. Lift 2,37× nhìn mạnh nhưng phán quyết STEP_06 là **YẾU** — trong từng kênh chỉ 1,05× (4/8 kênh) = bẫy Simpson. `conf` nay suy từ `verdict` thật thay vì gán tay. Xem T32.*
  - CAO: Old-school/vintage black gospel · Nhạc CÓ LỜI cho cầu nguyện · Định vị "yêu nhạc blues, cần lời sạch"
  - VỪA: Mix dài chất lượng cao · Nhánh Tây Ban Nha/Bồ Đào Nha
- **Mốc chuẩn từ 53 kênh thật:** P25=41.5k · P50=106.4k · P75=241.4k · P90=463.5k view/tháng
- **Kế hoạch 90 ngày** với tiêu chí đo và điều kiện dừng cho từng mốc 30/60/90
- **24 đề tài đầu tiên** kết hợp chủ đề thắng × bối cảnh nghe × định dạng dài
- ⚠️ **Kịch bản có thể lật ngược kết luận:**
  - T2 giảm còn 1 (snapshot mới xấu) → **9.2 = "Bỏ qua"** ← rủi ro lớn nhất
  - RPM thật $6 → 12.6 (vẫn "Theo dõi")
  - YouTube siết chính sách AI → 10.2

### AUDIT BỔ SUNG · Kiểm dùng hết dữ liệu chưa — ✅ XONG (2026-08-15)
- **Câu hỏi:** đã dùng hết 10 sheet trong file xlsx chưa?
- **Trả lời: 7/10 sheet dùng cho phân tích. 3 sheet còn lại đã kiểm và khai thác bổ sung:**

| Sheet | Trạng thái ban đầu | Sau audit |
|---|---|---|
| `crawl_jobs` (5,490) | ❌ Chưa dùng | ✅ Dùng để **kiểm phủ crawl** |
| `Dung lượng thị trường` (66) | ❌ Chưa dùng | ✅ Dùng để **kiểm chứng độc lập M2.4** |
| `video_master` (7,193) | 🟡 Chuẩn hóa nhưng không phân tích | ✅ Xác nhận **dư thừa** — đã tự dựng tương đương |
| `README` (17) | Metadata | Đã đọc từ đầu |

- **3 phát hiện mới:**
  - ✅ **Dữ liệu crawl SẠCH:** 5,490 job đều `done`, **0 lỗi, 0 lần thử lại** → không video nào bị bỏ sót do lỗi kỹ thuật
  - ⚠️ **1,809 video (25%) CHƯA crawl comment** — nhưng chỉ chiếm **1.7% tổng view** (view TV=244) → không ảnh hưởng kết luận STEP_05
  - 🔑 **KIỂM CHỨNG ĐỘC LẬP M2.4:** sheet có mốc **T3/2026**, hoàn toàn tách biệt cách tính của STEP_02. Kết quả: tăng trưởng trung vị **1.62×**, **33/50 kênh tăng** → **ỦNG HỘ M2.4=1.305**, bác bỏ lo ngại pha loãng
  - ℹ️ Cột "Có lời/không lời": **53/53 kênh đều CÓ LỜI** → xác nhận gián tiếp kết luận STEP_06 (instrumental lift 0.17× — không ai làm vì không hiệu quả)
- **Kết luận:** không có dữ liệu nào bị bỏ sót gây ảnh hưởng kết luận. Trục T2 nay có **2 nguồn độc lập cùng ủng hộ**

### PHIÊN LÀM VIỆC ĐỘC LẬP — ✅ XONG (2026-08-15)
> Người dùng giao toàn quyền, đi ra ngoài. Các việc đã hoàn thành:

**1. Bổ sung phần giải thích RUBRIC** (yêu cầu trực tiếp)
- Thêm **§0 "Rubric là gì"** vào đầu `03_SCORING_RUBRIC.md` — 7 tiểu mục cho người chưa quen
- Giải thích: định nghĩa · vì sao cần · 3 thành phần · cách tính · 3 nguyên tắc bất di bất dịch · giới hạn
- Thêm mục **4b RUBRIC** vào `README.md`
- Tạo artifact trực quan riêng cho rubric

**2. Kiểm nhất quán rubric — PHÁT HIỆN: tất cả đều khớp**
- Viết `pipeline/scoring/verify_rubric.py` — tự kiểm tài liệu ↔ code ↔ điểm đã chấm
- Kết quả: **6/6 trục khớp**, tổng 12.20 khớp, đủ trường truy vết
- Chạy được bất cứ lúc nào sau khi sửa rubric

**3. Chuẩn bị sẵn pipeline THUMBNAIL** (chờ dữ liệu)
- Viết `pipeline/analyze/step04b_thumbnail.py` — phân tích ảnh thật
- **Đã test bằng ảnh giả:** phát hiện đúng tín hiệu cài sẵn (mặt 6.57×, p<0.0001), bác bỏ đúng tín hiệu giả
- Đo được: khuôn mặt · bố cục · chữ · màu · **trùng lặp hình ảnh giữa kênh** (pHash)
- Có guard: tự dừng nếu <30 ảnh/nhóm, báo rõ nguyên nhân
- Tạo `00_input/raw/thumbs/README.md` hướng dẫn đặt file
- Cập nhật `STEP_04_outlier.md` và `A3_outlier_miner.md`

**4. Script chạy lại toàn bộ**
- `pipeline/run_all.sh` — chạy từ dữ liệu thô → chấm điểm → tự kiểm
- **Đã chạy thử: tái lập đúng 12.20/20**

**5. Kiểm tính toàn vẹn hệ thống**
- 27 script Python: **compile OK**
- Tham chiếu tài liệu: **0 gãy**
- File trạng thái: hợp lệ

## ⏳ CHỜ DỮ LIỆU BỔ SUNG

| # | Dữ liệu | Trạng thái | Ảnh hưởng khi có |
|---|---|---|---|
| D1 | **Ảnh thumbnail thật** (`raw/thumbs/*.jpg`) | ✅ **ĐÃ NHẬN 17/08/2026** — 7.193 ảnh, khớp 100% | ✅ **Đã phân tích xong** → `99_report/STEP04b_Phan-tich-Thumbnail.pdf` |
| D2 | Snapshot lần 2 (`video_stats`) | ⬜ Chưa chạy | **Cập nhật STEP_02** — nâng T2 từ tin cậy Vừa lên Cao. Có thể lật ngược điểm tổng |
| D3 | `media_probe` mở rộng (hiện 0.6%) | 🔺 **Ưu tiên tăng** | Mở khóa phân tích tempo/tông/đặc trưng âm thanh. **Giờ là khoảng trống lớn nhất** — ảnh đã loại trừ, phần lớn khác biệt nằm ở nội dung nghe |

---

## 🖼️ STEP_04b — PHÂN TÍCH THUMBNAIL (17/08/2026) ✅

**Dữ liệu:** 7.193 ảnh (100% ngách, không thiếu không thừa) · phân tích 4.139 video đủ tuổi ≥500 view

### Kết quả: 0/12 đặc trưng xác nhận

| Nhóm so sánh | Vượt lớp 1 | Sống sót 3 lớp |
|---|---|---|
| Top 10% theo **lượt xem** | 0 | 0 |
| Top 10% theo **tỷ lệ like** | 3 XÁC NHẬN + 4 YẾU | 0 (1 cái "không đáng kể") |

**Cơ chế:** kênh giải thích **39.1%** biến thiên tỷ lệ like (tương quan cấp kênh r=−0.55).
Không phải "ảnh đơn giản → nhiều like" mà là "kênh mạnh → nhiều like, và kênh mạnh
tình cờ dùng ảnh đơn giản". Nghịch lý Simpson.

### ⚠️ Lỗi công cụ đã phát hiện và sửa

| Lỗi | Bản đầu (SAI) | Sau khi sửa |
|---|---|---|
| Bộ dò mặt (Haar → **YuNet**) | 35.8% có mặt | **90.2%** |
| Bộ dò chữ (Canny → **MSER**) | chữ chiếm 90.7% ảnh | **11.4%** |
| `except: return None` | che một `NameError` | trả mã lỗi + đếm + dừng nếu <90% |

Phát hiện nhờ: đối chiếu `n_faces` với `skin_ratio` (p=0.34 → nghi ngờ) rồi **mở 12 ảnh xem tận mắt**.
→ Bài học T12–T16, quy tắc sống còn thứ 4 (mới).

### Phát hiện phụ: trùng lặp hình ảnh giữa kênh
**53 cặp** ảnh gần trùng giữa các kênh khác nhau (10 cặp **giống hệt từng pixel**, đã soi mắt xác nhận),
**18 kênh** dính líu, 87 video (1.2% ngách). Chưa đủ đổi điểm T6 nhưng cần theo dõi.
→ `04_outlier/11_cross_channel_dups.csv`

### Chuẩn hình ảnh của ngách (vé vào cửa, không phải lợi thế)
90.2% có mặt người · 70.5% đúng 1 mặt · 88.2% có chữ · mặt chiếm ~3.2% ảnh ·
chữ ~11.4% ảnh · 3 khối chữ · mặt nằm nửa trên (0.31) · 97% dùng 1280×720

**Script mới:** `step04c_thumbnail_full.py` (trích 7.193 ảnh, 107s, 8 tiến trình) ·
`step04d_thumbnail_top.py` (phân tích nhóm dẫn đầu) · `charts04b.py` · `build_report04b.py`

## CÂU HỎI MỞ
| # | Câu hỏi | Phát sinh ở | Trạng thái |
|---|---|---|---|
| 1 | Pha loãng do kênh rác hay cả ngách? | STEP_00 | ✅ **H0 — không pha loãng thật** |
| 2 | Còn Thánh Vịnh nào chưa khai thác? | STEP_00 | ⬜ → STEP_04 |
| 3 | `vintage_gospel_vgx` làm gì đặc biệt? | STEP_00 | ⚠️ Thống kê không giải thích được → cần nghe nhạc thủ công |
| 7 | Đăng dày là nhân quả hay tương quan? | STEP_03 | ⚠️ Vẫn là tương quan — metadata không giải thích được |
| 8 | Định dạng nào tốt nhất? | STEP_02 | ✅ **Giải được** — bối cảnh nghe ủng hộ mix dài |
| 9 | Yếu tố quyết định thật nằm ở đâu? | STEP_04 | 🔄 **Thu hẹp thêm**: STEP_04b loại trừ cả hình ảnh thumbnail (0/12). Còn lại: chất lượng nhạc + bối cảnh nghe |
| 10 | RPM thực tế nhóm 60+ Mỹ? | STEP_05 | ⚠️ Ước tính $1.5-6.0, **cần kênh thử nghiệm để xác minh** |
| 6 | Top20 tăng ×2.03 — winner-takes-most? | STEP_02 | ✅ **Bác bỏ** — top1 chỉ 18.5% |
| 4 | Có chạy thêm snapshot được không? | STEP_00 | ⬜ **cần bạn quyết** |
| 5 | Nhánh LatAm có đáng mở? | STEP_00 | ⬜ → STEP_02 |

## QUYẾT ĐỊNH ĐÃ CHỐT
| Ngày | Quyết định | Lý do |
|---|---|---|
| 2026-08-15 | Tách `framework/` khỏi `niches/` | Tái sử dụng cho ngách sau, không làm lại từ đầu |
| 2026-08-15 | Dùng ngưỡng lọc mặc định nhóm 5–10k video | Cỡ ngách 7.193 khớp nhóm này; kết quả 13.2% đạt mục tiêu |
| 2026-08-15 | Gộp STEP_01 + STEP_02 | STEP_02 có cổng quyết định — biết sớm để dừng sớm |
| 2026-08-15 | Mốc crawl = video mới nhất, không phải nửa đêm | Tránh báo sai "published_at ở tương lai" |
| 2026-08-15 | Động lượng chỉ tính trên cửa sổ đều chín (≥60d) | Cửa sổ chưa chín cho kết luận NGƯỢC (0.447 vs 1.305) |
| 2026-08-15 | **ĐI TIẾP sang STEP_03** | M2.4 = 1.305 vượt ngưỡng cổng ≥1.0 |
| 2026-08-15 | Loại bỏ M3.3, thay bằng tuổi trung vị nhóm thành công | Dữ liệu 1 snapshot không đo được time-to-traction |
| 2026-08-15 | **ĐI TIẾP sang STEP_04** | T3=4.4, T4=5.0 — cửa mở, mô hình AI đã chứng minh |
| 2026-08-15 | Loại `engagement_rate` khỏi kiểm định | Artefact toán học, không phải đặc trưng nội dung |
| 2026-08-15 | Dùng Fisher exact cho biến nhị phân | Trung vị của biến 0/1 luôn = 0 nên vô nghĩa |
| 2026-08-15 | Bắt buộc kiểm ngoài mẫu cho mọi phát hiện B1/B4 | Nghịch lý Simpson suýt tạo ra khuyến nghị sai |
| 2026-08-15 | **ĐI TIẾP sang STEP_05** | Metadata cạn tín hiệu — comment là nguồn còn lại |
| 2026-08-15 | Chỉ ghi nhân khẩu khi TỰ KHAI, không suy đoán | Ranh giới đạo đức + độ chính xác |
| 2026-08-15 | Loại 381 comment nhiễu (kinh dài, chép lyrics) | Không nói gì về người viết |
| 2026-08-15 | **ĐI TIẾP sang STEP_06** — đổi trọng tâm sang chọn đề tài | Đề xuất thắng tìm kiếm 7:1 → SEO ít giá trị |
| 2026-08-15 | Bỏ qua STEP_06, chạy thẳng STEP_07 | Người dùng yêu cầu ưu tiên kiếm tiền & rủi ro |
| 2026-08-15 | **Chốt định dạng chủ lực = mix dài 1-3h** | Gấp 12× ad slot + đúng bối cảnh nghe |
| 2026-08-15 | Điểm cuối 12.20/20 = "Theo dõi" | Dễ vào nhưng trần thấp — hợp mô hình nhiều kênh song song |
| 2026-08-15 | **Chốt định vị: old-school / vintage black gospel** | Lift 2.37× cao nhất, chỉ 3.96% thị trường khai thác |
| 2026-08-15 | **Luôn có lời hát, KHÔNG làm instrumental** | Lift 0.17× — kém nhất trong 16 chủ đề |
| 2026-08-15 | Áp lớp kiểm Simpson cho MỌI chủ đề | Đã loại 4 chủ đề tưởng tốt |
