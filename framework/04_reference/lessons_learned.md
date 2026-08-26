# BÀI HỌC TÍCH LŨY

> File **sống** — cập nhật sau mỗi ngách. Mục đích: ngách sau không lặp lỗi ngách trước.
> Phiên bản: v2.0 · Cập nhật 2026-08-15 · Nguồn: ngách `christian-blues` (STEP_00→08 + audit)

---

## CÁCH DÙNG FILE NÀY

Bài học được xếp theo **mức độ nguy hiểm**, không theo thứ tự thời gian:

| Nhóm | Nội dung | Đọc khi nào |
|---|---|---|
| 🔴 **Tầng 1** | 5 bẫy có thể đảo ngược kết luận | **Đọc trước mỗi ngách mới** |
| 🟠 **Tầng 2** | Quy tắc phân tích bắt buộc | Trước khi viết code phân tích |
| 🟡 **Tầng 3** | Bẫy kỹ thuật & vận hành | Khi gặp lỗi lạ |
| 🔵 **Tầng 4** | Nguyên tắc diễn giải & báo cáo | Khi viết báo cáo |

---

# 🔴 TẦNG 1 — NĂM BẪY CÓ THỂ ĐẢO NGƯỢC KẾT LUẬN

Đây là những lỗi mà nếu mắc phải, **toàn bộ khuyến nghị sẽ sai**. Cả 5 đều đã thực sự xảy ra
trong ngách christian-blues và đều **trông rất thuyết phục** khi nhìn lần đầu.

## L1 · Bẫy dữ liệu chưa chín (maturation trap)

**Đã xảy ra:** Khảo sát sơ bộ kết luận *"ngách đang bị pha loãng, M2.4 = 0.35, nên dừng"*.
Tính lại đúng cách: **M2.4 = 1.305** — ngách khỏe. **Kết luận ngược hoàn toàn.**

**Nguyên nhân:** so sánh cửa sổ 0–90 ngày (chỉ 36% video đã đủ 60 ngày tuổi) với cửa sổ
90–180 ngày (100% đã chín). Video mới chưa kịp tích view.

> Giống như so chiều cao đứa trẻ 5 tuổi với người 30 tuổi rồi kết luận loài người đang lùn đi.

**Quy tắc bắt buộc:**
- Mọi so sánh hiệu quả chỉ dùng video `is_matured = True` (≥60 ngày)
- Hai cửa sổ so sánh phải **đều đã chín hoàn toàn**
- Phân tích *nguồn cung* thì dùng toàn bộ; phân tích *hiệu quả* thì chỉ dùng đã chín

## L2 · Nghịch lý Simpson

**Đã xảy ra:** "Tên Kinh Thánh trong tiêu đề" có lift **8.1×** trong mẫu outlier (p<0.001).
Nhưng trên toàn thị trường lift chỉ **0.48×** — *kém hơn 52%*.

**Nguyên nhân:** vài kênh *chuyên* chủ đề đó (như `holygroove-1` có 76.6% video Thánh Vịnh)
có một số video cực nổ. **Cái thắng là *kênh*, không phải *đặc điểm*.**

**Quy tắc bắt buộc — kiểm 3 lớp cho MỌI phát hiện:**

```
Lớp 1: trong mẫu outlier/đối chứng   → phát hiện ban đầu
Lớp 2: trên TOÀN BỘ dữ liệu           → còn đúng không?
Lớp 3: TRONG TỪNG KÊNH                → loại hiệu ứng kênh
```

Chỉ tin khi **cả 3 lớp cùng hướng**. Ở STEP_06, lớp 3 loại **4/16 chủ đề (25%)** dù chúng
đều có ý nghĩa thống kê ở lớp 1–2.

## L3 · Artefact toán học từ mẫu số

**Đã xảy ra:** `engagement_rate` cho hiệu ứng **mạnh nhất** trong 26 đặc trưng
(Cliff's delta = −0.682, p<0.001). Nhưng đó không phải phát hiện.

**Nguyên nhân:** `engagement = (like + comment) / view`. Nhóm thắng có view trung vị 71.314,
nhóm thua 863 — **gấp 82 lần**. Mẫu số lớn hơn → tỷ lệ nhỏ hơn, một cách máy móc.

**Xác nhận:** Spearman(view, engagement) = **−0.202** trên toàn bộ dữ liệu.

**Quy tắc:** với mọi tỷ lệ có view ở mẫu số, hỏi *"chỉ số này có bị chi phối bởi mẫu số không?"*
trước khi coi là phát hiện.

## L4 · Thiên lệch sống sót ở cấp KÊNH

**Đã xảy ra:** M3.2 = 61.5% kênh mới đạt traction — con số rất đẹp. Nhưng dữ liệu **chỉ có
53 kênh còn tồn tại**. Kênh đã thất bại và bị xóa không xuất hiện.

**Hệ quả:** tỷ lệ thành công thật của người mới **thấp hơn** con số báo cáo.

**Quy tắc:** luôn ghi rõ giới hạn này khi báo cáo tỷ lệ thành công. Không có cách sửa từ dữ liệu
— chỉ có cách nói thật.

## L5 · Chỉ số không đo được nhưng vẫn ra số

**Đã xảy ra:** M3.3 "thời gian đạt 100k view" tính ra **0.4 tháng** — vô lý.

**Nguyên nhân:** `view_count` là view **tích lũy đến ngày crawl**, không phải view tại thời
điểm đăng. Nên `cumsum` luôn vượt 100k sau vài video.

**Quy tắc:**
- Với 1 snapshot, **mọi chỉ số dạng "cumsum đến khi đạt X" đều vô nghĩa**
- Khi chỉ số không đo được: **THAY bằng chỉ số đo được có ý nghĩa tương đương**, đừng bỏ trống,
  đừng báo số sai. (M3.3 → thay bằng "tuổi trung vị nhóm đã thành công")
- **Con số vô lý là tín hiệu tốt** — nó buộc ta kiểm lại. Luôn hỏi *"con số này có hợp lý không?"*

---

# 🟠 TẦNG 2 — QUY TẮC PHÂN TÍCH BẮT BUỘC

## Về so sánh

| # | Quy tắc | Vì sao |
|---|---|---|
| A1 | **Luôn có nhóm đối chứng.** Không có thì mọi "công thức thắng" đều là mê tín | Video thua có thể *cũng* có đặc điểm đó. Ở STEP_04, 26/26 đặc trưng bị bác bỏ nhờ đối chứng |
| A2 | **Chuẩn hóa theo chính kênh** trước khi so sánh | 50k view trên kênh trung vị 40k là bình thường; trên kênh trung vị 500 là bùng nổ 100× |
| A3 | **Chuẩn hóa theo tuổi video** (dùng VPD) | Video 1 năm và video 1 tháng không so trực tiếp được |
| A4 | **Dùng trung vị, không dùng trung bình** | View phân bố đuôi dài. Ngách này: TB = 17.009 nhưng TV = 1.687 — chênh 10× |
| A5 | Yêu cầu **CẢ p-value CẢ effect size** | Mẫu lớn cho p nhỏ ngay cả khi chênh lệch vô nghĩa. Ngưỡng: p<0.01 **và** \|Cliff's delta\|≥0.30 |
| A6 | **Biến nhị phân dùng kiểm định tỷ lệ** (Fisher), không dùng trung vị | Trung vị của biến 0/1 hầu như luôn = 0 → mọi so sánh ra "không khác biệt" |

## Về diễn giải chỉ số

| # | Quy tắc | Ví dụ thật |
|---|---|---|
| A7 | **Tần suất cao ≠ tín hiệu mạnh** | "healing" xuất hiện 757 lần (nhiều nhất) nhưng like TV=3, *dưới* mức nền 4. "finally" chỉ 58 lần nhưng like gấp **6.6×** |
| A8 | **Hai chỉ số có thể ngược chiều — báo cáo cả hai** | Nhịp đăng dày: view/video **giảm** (−0.311) nhưng tổng view/tháng **tăng** (+0.420). Chỉ báo một chiều là dẫn dắt sai |
| A9 | **Hiệu suất (VPD) và doanh thu có thể ngược chiều** | Video 1–6m có VPD cao hơn nhưng chỉ **1 ad slot**; mix 1–3h VPD thấp hơn nhưng **~11.7 ad slot** |
| A10 | **Tổng tăng ≠ ngách khỏe** | Phải xem view trung vị *mỗi video*, không chỉ tổng view thị trường |
| A11 | **Bối cảnh sử dụng giải thích được lựa chọn định dạng** | Khi thống kê mâu thuẫn, hỏi *"khán giả nghe LÚC NÀO"*. Nghe lúc cầu nguyện/bệnh tật → cần mix dài liền mạch |

## Về chọn lọc dữ liệu

| # | Quy tắc | Chi tiết |
|---|---|---|
| A12 | **Bốn rổ video, không bỏ rổ đối chứng** | B1 outlier · B2 đang lên · B3 đại diện · **B4 đối chứng**. B4 là thứ giữ cho kết luận có giá trị |
| A13 | **Kiểm phủ view sau khi lọc** | Mục tiêu: video đã lọc phải chiếm **≥70% tổng view**. Ngách này: 13.4% video phủ **80.6%** view |
| A14 | **Loại nhiễu trước khi phân tích comment** | Kinh cầu nguyện chép dài, bản chép lyrics, spam — chúng lọt bộ lọc "comment dài" nhưng không nói gì về người viết |
| A15 | **Chọn lọc ở cấp workflow, không chỉ cấp dữ liệu** | A4 đọc output A3 để biết *comment nào đáng đọc* — thay vì quét cả 145k |
| A16 | **Nhãn rổ ĐỌC TỪ `selected_videos.parquet`, không tái tạo lại từ ngưỡng** | Tái tạo bộ lọc từ `_selection_params.json` cho ra **B1=496 · B4=132**, nhưng số thật là **B1=435 · B4=161** — vì `apply_filters.py` chỉ tính B1/B4 trên `v[v.is_matured]` và dùng cột `outlier_ratio` có sẵn, không tính lại. Lệch hai chiều 74/60 dòng. Cột `bucket` đã nằm sẵn trong file kết quả: đọc nó. Đây là T27 áp cho nhãn phân loại, không chỉ cho con số |

---

# 🟡 TẦNG 3 — BẪY KỸ THUẬT & VẬN HÀNH

## Lỗi code đã gặp

| # | Lỗi | Triệu chứng | Cách tránh |
|---|---|---|---|
| T1 | Đặt tên file trùng module stdlib | `select.py` → pandas báo "circular import" khó hiểu | Tránh: `select`, `json`, `time`, `types`, `random`, `email` |
| T2 | Cột hash/ID đọc thành int | `phash` 59-bit → `OverflowError` khi ghi parquet | Ép `astype(str)` cho mọi cột ID/hash trước khi ghi |
| T3 | Merge 2 bảng cùng tên cột | `KeyError: 'channel_id'` sau merge | `drop` cột trùng trước khi merge |
| T4 | Mốc thời gian gõ tay | Video đăng cùng ngày bị báo "ở tương lai" | Lấy mốc **từ dữ liệu**: `published_at.max().ceil("h")` |
| T5 | Thư viện thiếu | `statsmodels` không có | Fisher exact của `scipy` thay được, chính xác hơn với mẫu nhỏ |

## Về kiểm kê dữ liệu

| # | Bài học | Ví dụ thật |
|---|---|---|
| T6 | **Kiểm HẾT sheet trước khi kết luận "đã dùng hết dữ liệu"** | Audit tìm ra 3/10 sheet chưa dùng, trong đó 2 sheet có giá trị thật |
| T7 | **Sheet nhật ký crawl dùng để kiểm phủ** | `crawl_jobs` cho biết: 0 lỗi, nhưng **1.809 video chưa crawl comment** (chỉ chiếm 1.7% view → không ảnh hưởng) |
| T8 | **Sheet cũ của người dùng có thể là nguồn kiểm chứng ĐỘC LẬP** | Sheet "Dung lượng thị trường" có mốc T3/2026 → xác nhận M2.4 bằng nguồn tách biệt: tăng trưởng 1.62×, 33/50 kênh tăng |
| T9 | **Bảng "ghép sẵn" thường dư thừa** | `video_master` là join của 4 bảng khác — tự dựng từ nguồn gốc thì kiểm soát tốt hơn |
| T10 | **Bảng phủ dưới 30% không kết luận được gì** | `media_probe` 40/7.193 = 0.6% → loại khỏi mọi phân tích |
| T11 | **1 snapshot giới hạn rất nhiều** | Không đo được tốc độ tăng view thật; mọi động lượng phải suy từ `published_at`, tin cậy tối đa "Vừa" |

## Về công cụ đo (thêm 17/08/2026 — sau sự cố thumbnail)

| # | Bài học | Ví dụ thật |
|---|---|---|
| T12 | **Bộ dò mặt Haar cascade KHÔNG dùng được cho thumbnail** | Haar `frontalface` chỉ nhận mặt nhìn thẳng đủ sáng. Thumbnail thật hay có mặt nghiêng/ngẩng/nhắm mắt/tương phản mạnh → báo **35.8%** có mặt trong khi thực tế **90.2%**. Dùng **YuNet** (CNN, có sẵn trong OpenCV ≥4.5.4). Kiểm 12 ảnh soi mắt: YuNet 11/12, Haar 6/12 |
| T13 | **Canny + dilate KHÔNG đo được diện tích chữ** | Nó gộp tóc, nhạc cụ, nếp áo thành "khối chữ" → báo chữ chiếm **90.7%** ảnh (vô lý). Dùng **MSER** + lọc tỷ lệ ký tự → **11.4%**, khớp quan sát mắt |
| T14 | **`except: return None` che lỗi chết người** | Một `NameError` (đổi Canny→MSER nhưng còn tham chiếu `edges`) khiến **toàn bộ** ảnh trả None, mà script vẫn in "chạy xong". Luôn trả **mã lỗi** và **đếm** ở cuối; dừng nếu tỷ lệ thành công < 90% |
| T15 | **Kiểm chéo công cụ đo bằng biến độc lập TRƯỚC khi tin kết quả** | `n_faces` phải tương quan với `skin_ratio` (đo độc lập từ crawl). Thực tế p=0.34 → lộ ra bộ dò hỏng. Nếu bỏ qua bước này, báo cáo đã kết luận trên dữ liệu rác |
| T16 | **Với dữ liệu ảnh/âm thanh: MỞ RA XEM/NGHE vài mẫu** | Chỉ mất 2 phút dựng contact sheet 12 ảnh, nhưng đó là thứ duy nhất chứng minh dứt khoát bộ dò sai. Thống kê không tự phát hiện được lỗi cảm quan |
| T17 | **MSER cũng KHÔNG đo được diện tích chữ — phải OCR** | Sửa Canny→MSER (T13) vẫn chưa đủ. Đối chiếu 14 ảnh soi mắt: tương quan chỉ **0.233**; ảnh chữ TO NHẤT báo **0.0%**. Chỉ **OCR** (EasyOCR) mới đúng, vì nó **đọc** chữ thay vì đoán theo hình dạng. Bonus: có luôn nội dung chữ để phân tích |
| T18 | **Ảnh Shorts nhét trong khung ngang làm hỏng mọi tỷ lệ "% diện tích"** | **13.2%** ảnh ngách này là ảnh dọc đặt giữa hai dải nền mờ. Mẫu số gồm cả dải mờ → "mặt chiếm 3% ảnh" là vô nghĩa. Phải dò và loại/chuẩn hóa. Ngưỡng đã hiệu chuẩn: **cả hai** biên có độ biến thiên cột < 0.30 lần vùng giữa |
| T19 | **Hình học KHÔNG phải "gu ảnh"** | Đo mặt to bao nhiêu %, chữ chiếm mấy % → kết luận "ảnh không phân biệt thắng/thua". Nhưng gu ảnh nằm ở **nội dung chữ, bảng màu, mô-típ, quy trình tạo ảnh** — thứ hình học không chạm tới. Người dùng phải chỉ ra tôi mới nhận ra đo sai đối tượng |
| T20 | **Đo KHUÔN MẶT ≠ đo NGƯỜI — lệch 10 lần** | YuNet khoanh mặt (trán→cằm) = **3.2%** khung. Người xem thấy **cả nhân vật** (đầu, tóc, mũ, thân) = **27.6%**. Báo cáo ghi "mặt vừa phải, không cận cảnh" — diễn giải bố cục từ con số không đo bố cục. Dùng **YOLO-seg** phân vùng lớp `person`; kiểm 9 ảnh soi mắt, lệch trung bình 5.0 điểm % |
| T22 | **Script không tự tạo thư mục output → ngách mới chết ngay** | 6/15 script quên `mkdir`. Ngách gốc chạy được vì thư mục đã có sẵn từ lần chạy tay đầu tiên. Sửa: `run_all.sh` gọi `pipeline/_common.py` dựng khung trước |
| T23 | **Mắt xích gom chỉ số bị THIẾU mà không ai biết** | Mỗi bước ghi `_metrics_raw.json` riêng, nhưng KHÔNG bước nào gom vào `_state/metrics.json` — tôi đã **chép tay**. Hệ thống trông tự động vì file cũ vẫn còn. Sửa: thêm `collect_metrics.py` |
| T24 | **`scoring_engine` đọc điểm trục mà KHÔNG script nào tính chúng** | `T1_score`…`T6_penalty` được điền TAY theo bảng ngưỡng. Vi phạm ngầm R2 (không tự chấm) và R3 (truy vết được). Sửa: thêm `apply_thresholds.py` code hóa ngưỡng từ §4 rubric |
| T25 | 🔴 **Chỉ số "KHÔNG ĐO ĐƯỢC" bị chấm 5/5 điểm tối đa** | M3.3 ghi rõ *"KHÔNG ĐO ĐƯỢC — cần ≥2 snapshot"* nhưng công thức hardcode `0.2*5`, đẩy T3 từ 4.0 → 4.4. **Thiếu dữ liệu thì CHIA LẠI trọng số cho phần đo được, đừng gán mặc định.** Sửa xong: tổng 12.20 → **12.05** |
| T26 | **Chỉ "chạy lại được" KHÔNG chứng minh pipeline tự động** | Chạy lại 5 lần đều ra 12.20 — nhưng vì file trung gian đã tồn tại. **Phép thử thật: chạy trên thư mục ngách TRỐNG.** Nó lộ ra T22, T23, T24, T25 chỉ trong một lần |
| T27 | **PDF ghi cứng điểm → lệch với `scores.json` mà không ai biết** | Sửa bẫy L5 làm T3 đổi 4.4→4.25, tổng 12.20→12.05. Nhưng `build_report03.py` ghi cứng "T3 = 4,4/5" trong HTML nên PDF vẫn in số cũ. **Builder phải ĐỌC `scores.json`, không gõ số.** Thêm `verify_reports.py` dò lại PDF sau mỗi lần dựng |
| T28 | **Làm tròn 1 chữ số che sai lệch** | STEP_07/08 in `{total:.1f}` → "12,1" trong khi điểm thật 12,05. Nhìn không sai nhưng không khớp `scores.json`. Với điểm số, **in đủ chữ số** (`:g`) thay vì làm tròn |
| T29 | 🔴 **Tên bước hứa nhiều hơn nội dung → người đọc mất niềm tin vào cả hệ thống** | STEP_04 tên *"Công thức thắng"* nhưng dòng đầu báo cáo là *"0/20 đặc trưng đứng vững"* — nó **bác bỏ**, không rút ra công thức. Tệ hơn: nó nằm **trước** thumbnail/khán giả/từ khóa, nên người dùng hỏi *"sao có công thức thắng trước cả phân tích?"*. **Tên phải mô tả cái bước đó LÀM, không phải cái ta mong nó làm.** Đổi thành **SÀNG LỌC ĐỐI CHỨNG**; danh xưng "công thức thắng" chuyển về STEP_10 — nơi thật sự tổng hợp |
| T30 | 🔴 **Kết luận dựa trên thước đo đã biết là hỏng vẫn nằm im trong báo cáo** | 8 đặc trưng thumbnail của STEP_04 lấy proxy từ Excel nguồn; STEP_04b/04g sau đó chứng minh `text_score` chỉ tương quan **0,233** với chữ thật. Runbook có ghi cảnh báo, nhưng **PDF thì không** — người đọc thấy 8 dòng "BÁC BỎ" trông chắc như 7 dòng đo trực tiếp. **Kết luận yếu phải TRÔNG yếu.** Sửa: gắn cờ `measure="proxy"` ngay trong dữ liệu (`04_feature_tests.csv`) để mọi báo cáo dùng lại được, thêm cột **THƯỚC ĐO** trong bảng. **Đánh dấu ở DỮ LIỆU, đừng ghi chú ở một PDF** |
| T31 | 🔴 **Một câu văn xuôi không phải bằng chứng** | Bản đồ khoảng trống ghi mỗi ô đúng MỘT câu (*"Comment 1.444♥ nêu đúng nỗi đau này (STEP_05)"*) — người đọc không có cách nào kiểm chứng: comment nào? ở file nào? Sửa: `demand` thành **list**, mỗi mục có `claim` + `src` (đường dẫn file + khóa) + `id` (`comment_id` để mở đúng dòng). 5 khoảng trống: 5 → **18 bằng chứng**, mỗi cái truy ngược được. **Bằng chứng không truy vết được thì chỉ là lời khẳng định.** Thiếu bằng chứng thì ghi thẳng *"CHƯA CÓ"* thay vì viết mơ hồ |
| T32 | 🔴 **Gán tay độ tin cậy làm giấu mất bẫy Simpson** | Khoảng trống `old_school` gán `conf="Vừa"` và khoe *"lift 2,37× — cao nhất 16 chủ đề"*, trong khi `02_theme_scores.csv` ghi phán quyết **YẾU**: trong từng kênh chỉ **1,05×**, 4/8 kênh. Báo cáo còn gọi đây là *"phát hiện có giá trị nhất"*. Sửa: `conf` **suy ra từ `verdict` thật**, tự đổi thành **Thấp**; thêm hộp giải thích vì sao. **Số hấp dẫn và số đã qua kiểm 3 lớp phải hiện CẢ HAI** |
| T33 | 🔴 **Căn lề tùy hứng làm người đọc mất mạch** | Bảng ngưỡng in cột điểm căn PHẢI sát cột điều kiện căn TRÁI → mắt phải nhảy qua lại mỗi dòng. Nguyên nhân: dùng class `.n` (căn phải) cho cả **nhãn** (mức điểm 0–5, «Cao/Vừa/Thấp»), không chỉ cho số. **Quy tắc:** `.n` chỉ dành cho số **so sánh được theo cột** (%, tiền, view) · `.c` cho nhãn/mã ngắn · còn lại căn trái. Người dùng phát hiện, không phải tôi |
| T34 | **Bảng ngưỡng dọc 6 dòng khó theo dõi hơn bảng ngang** | Mỗi mức điểm một dòng thì không so sánh được các mức với nhau. Chuyển thành **điểm làm cột** (5·4·3·2·1·0), mỗi metric một hàng → 6 dòng còn 3, ngưỡng thẳng hàng dưới từng mức, thêm được hàng «diễn giải». **Trục nào cần so sánh thì trục đó nên nằm ngang** |
| T35 | 🟢 **Nghiên cứu độc lập của team khác là nguồn kiểm chứng quý** | Team FMG làm chân dung khán giả riêng (1.017 comment, mẫu tách rời). Tuổi trung vị **69 vs 70** của ta — trùng đến mức khó do ngẫu nhiên; bối cảnh nghe số 1 cũng trùng. Quan trọng hơn: họ **có dữ liệu ngôn ngữ** mà ta thiếu (TBN 6,0%) → lấp đúng chỗ khoảng trống ghi *«CHƯA CÓ bằng chứng»*, nâng tin cậy Thấp→Vừa. **Chênh lệch cũng phải giải thích** (6,0% vs 1,73% = khác phương pháp lọc), và **trùng nhau KHÔNG tự động nâng lên Cao** — hai nghiên cứu cùng sai một hướng vẫn là sai |
| T36 | 🔴 **Tài liệu ngưỡng mô tả mơ hồ hơn code thực thi** | Rubric §T6 ghi *«Trùng lặp title/mô tả giữa các kênh → −2»* nhưng **không nói bao nhiêu phần trăm**; code dùng ngưỡng cụ thể `cross_title_pct >= 5`. Tương tự T5: code lấy **giá trị GIỮA** của khoảng RPM `[1.5, 3.0, 6.0]` nhưng tài liệu chỉ ghi «RPM ước tính». **Người đọc không tái tạo được điểm** → rubric mất tính khách quan, thứ duy nhất nó tồn tại để bảo đảm. Sửa: mỗi rủi ro ghi rõ metric + ngưỡng kích hoạt; nêu quy ước lấy giá trị giữa. **Tài liệu phải đủ chi tiết để chấm lại bằng tay** |
| T37 | 🟢 **Dấu vết dẫn xuất đã có sẵn nhưng không ai hiển thị** | `apply_thresholds.py` ghi `_meta.derivation` vào metrics.json (*«T1 ← M1.1 = 7450226»*, *«T6 ← trùng nội dung 6.3% (−2)»*) — nhưng **không báo cáo nào in ra**. Thêm bảng «từ số thô đến điểm» vào PDF rubric: mỗi trục hiện giá trị đo được → ngưỡng chạm → điểm. Người đọc **tự chấm lại được**. **Trước khi tính thêm dữ liệu mới, hãy kiểm xem thứ cần thiết đã nằm sẵn trong file chưa** |
| T38 | 🔴 **Bẫy nhân đôi tempo (octave error) của librosa** | `beat_track` bám vào lớp đệm (hi-hat, tremolo) thay vì phách chính → báo **103–162 BPM** cho nhạc gospel *chậm*. Bắt được nhờ **ba kiểm chéo độc lập**: `beats_per_chord` >6 (ở 4/4 thì 8 phách = 2 ô nhịp, 13,8 là vô lý) · `onsets_per_beat` <1 (ít nốt hơn phách = lưới quá dày) · giây/hợp âm <6 (ballad đổi mỗi 6–11s). Chia đôi → **51,7–80,8 BPM**, đúng dải slow blues. **Cùng họ với T12 (Haar cascade): công cụ DSP cho ra số trông hợp lý nhưng sai hệ thống — luôn kiểm chéo bằng đại lượng độc lập** |
| T39 | 🔴 **Với n nhỏ, trung bình giấu mất độ phân tán** | Tôi suýt viết *«hợp âm thứ chiếm đa số»* vào brief âm nhạc. Thực tế tỷ lệ trải từ **7,6% đến 72,9%** — chỉ 2/5 bản thiên về thứ. Đường cong năng lượng cũng có **3 dạng khác nhau trên 5 bản**. **Chỗ nào dữ liệu phân tán thì báo cáo KHOẢNG và nói thẳng là không có chuẩn**, đừng ép ra quy luật để brief trông gọn |
| T40 | 🔴 **Hai hệ đánh số cãi nhau khi thêm bước mới** | Thêm nhánh nhạc: đặt script `step11_audio.py` (vì `step10` đã có) nhưng thư mục `08_audio/` (vì 08 còn trống) — **hai quyết định mâu thuẫn trong cùng một lần thêm**. Hệ quả người dùng thấy: thư mục báo cáo nhảy **08 → 11**, mất 09 và 10. **Số bước phải phản ánh VỊ TRÍ TRONG LUỒNG, không phải thứ tự tôi viết code.** Nhạc cùng tầng MÔ TẢ với brief ảnh (04g) → đúng chỗ là **04h**, không phải 11. Kiểm nhanh: `ls 99_report/` đọc từ trên xuống có nhảy cóc không |
| T41 | 🔴 **Thêm dữ liệu mới nhưng quên gỡ câu «chưa có dữ liệu» cũ** | Sau khi có brief nhạc, STEP_08 vẫn in *«Âm nhạc: dữ liệu hiện có không mô tả được nhạc — khoảng trống lớn nhất»* ngay dưới mục 7.6 vừa mô tả nhạc. Hai đoạn **mâu thuẫn cách nhau một trang**. **Khi lấp một khoảng trống, phải grep lại mọi chỗ từng khai báo nó còn trống** |
| T42 | 🟢 **Câu trả lời có sẵn nhưng nằm sai chỗ nên không ai thấy** | Người dùng hỏi *«nên làm nhạc có lời hay không lời?»* — dự án **đã trả lời được từ lâu**, nhưng bằng chứng nằm rải ở STEP_06 (lift 0,17× thấp nhất 16 chủ đề) và STEP_05 (bối cảnh nghe chủ động gấp 11,5× nghe nền), **không nơi nào gộp lại**. Brief âm nhạc — nơi người ta thực sự hỏi — lại không nhắc một chữ. **Tổ chức báo cáo theo CÂU HỎI người dùng đặt ra, không theo nguồn dữ liệu.** Đã gom thành khối `vocal_decision` + mục 1 của báo cáo 04h |
| T43 | 🟢 **Sơ đồ vẽ tay lại từ tài liệu gốc sẽ trôi — phải có bộ dò** | Dựng PDF cho `01_ARCHITECTURE.md`: 10 khối ```mermaid``` không render được (không có `mmdc`, mà nếu có thì ra PNG → in mờ). Vẽ lại bằng **Graphviz → SVG** nên chữ trong sơ đồ vẫn chọn/tìm được. Đánh đổi: sửa `.md` mà quên sửa builder thì PDF nói khác tài liệu. Đã thêm `drift_check()` đối chiếu số khối mermaid + mã bước. **Bộ dò bắt ngay lỗi thật:** đếm file runbook ra **12** trong khi tiêu đề ghi «10 bước» — vì `STEP_04b`/`04h` là *nhánh tùy chọn*, không phải bước chính. Đếm gộp là sai. Nay hiện «10 + 2 nhánh tùy chọn» |
| T44 | 🟢 **Phân khúc được nhận ra nhưng không đi tiếp vào kết quả** | Luồng mới của R&D (CDKH làm đầu vào, «hồ sơ bệnh án → bắt bệnh») lộ ra `step05_audience.py` đã phân sẵn 4 persona, nhưng `step10_playbook.py` **không đọc lại** → một công thức duy nhất cho cả ngách. **Bài học:** nhận diện được phân khúc mà đầu ra vẫn gộp thì coi như chưa phân khúc. Kiểm bằng câu hỏi: *biến này có tới được sản phẩm cuối không?* |
| T45 | 🔴 **Chốt định dạng bàn giao TRƯỚC khi bên kia gửi file** | Sắp nhận CDKH từ R&D. Nếu chờ file rồi mới đọc thì thành ngồi đoán tên trường. Đã viết `07_CDKH_CONTRACT.md` kèm **từ vựng đóng** (trích thẳng từ code) và 5 câu cần R&D xác nhận. **Bài học:** hợp đồng dữ liệu liên bộ phận là việc làm trước, không phải việc làm sau. |
| T46 | 🔴 **Nhiều dòng dữ liệu KHÔNG bằng nhiều mẫu độc lập** | DNA nhạc v2 có 307 track nhưng chỉ **29 video / 6 kênh**; nhiều track chia chung một con số view. Dùng track làm đơn vị thổi phồng n gấp ~10. **Bài học:** trước khi kiểm định, hỏi *đơn vị độc lập thật là gì?* rồi gộp về đó. Ở đây: track → video (trung vị). |
| T47 | 🔴 **Tương quan gộp p=7,6e-11 vẫn có thể sai hoàn toàn** | `stem_piano` gộp cho rho=+0,36 p<1e-10 — trông như phát hiện chắc chắn. Tách theo kênh: 2/6 kênh **đảo dấu**, phán quyết BÁC BỎ. 6 kênh chênh nhau 33,9× view nên tương quan gộp đang đo *sự khác nhau giữa kênh*. **Bài học:** p nhỏ không chống được nghịch lý Simpson; luôn kiểm trong từng kênh trước. |
| T48 | 🟢 **XÁC NHẬN phải đòi cả ý nghĩa lẫn nhất quán** | `drums_over_vocals` có q nhỏ nhất bảng nhưng 1/6 kênh đi ngược → hạ xuống YẾU; `stem_drums` q lớn hơn nhưng 0/6 kênh đi ngược → XÁC NHẬN. **Bài học:** quy luật sản xuất mà một kênh làm ngược vẫn thắng thì chưa phải quy luật. Điều kiện kép: q<0,05 **và** mọi kênh cùng dấu. |
| T49 | 🔴 **Tỉ lệ hợp thành không đọc như biến độc lập** | 5 stem là tỉ lệ, tổng ≈0,91 → trống tăng thì thứ khác buộc giảm; corr(drums,guitar)=−0,75 là do ràng buộc, không phải quan hệ thật. **Bài học:** dữ liệu compositional phải chuẩn hóa CLR (log-ratio tâm) hoặc đọc dạng tỉ lệ trực tiếp trước khi kết luận. |
| T50 | 🔴 **«0/1 kênh có ý nghĩa» là THIẾU MẪU, không phải BÁC BỎ** | Kiểm đặc trưng phân loại ở mức video (n=29) chỉ còn 1–2 kênh đủ nhóm. Ban đầu code gắn nhãn BÁC BỎ — khẳng định mạnh hơn dữ liệu cho phép. Đã thêm phán quyết **KHÔNG ĐỦ MẪU**. **Bài học:** không biết ≠ biết là không. |
| T51 | 🟢 **Báo cáo cho cấp duyệt cần khung khác báo cáo cho người nghiên cứu** | 15 báo cáo hiện có đầy p-value và kiểm định — đúng cho người phân tích, sai cho người duyệt. Sếp cần: kết luận + mức tin cậy + ràng buộc lên quyết định. **Bài học:** cùng một dữ liệu phải có hai bản trình bày; đừng bắt cấp duyệt tự dịch. |
| T52 | 🔴 **Bộ kiểm số liệu báo động giả trên KỊCH BẢN giả định** | Hồ sơ ngách cố ý in «nếu M2.4 sai → 9,20/20» để cho thấy độ nhạy; `verify_reports.py` tưởng là điểm cũ. Đã mở rộng EXCUSE cho ngữ cảnh giả định (`nếu`, `kịch bản`, `rơi xuống`) và **thử lại 6 ca** để chắc vẫn bắt được số cũ thật. **Bài học:** nới lỏng bộ kiểm phải kèm ca thử chứng minh chưa nới quá tay. |
| T53 | 🔴 **Điểm số float in thẳng ra PDF bị mất phần thập phân** | `{S['total_score']}` cho ra «12» thay vì «12,05» — sếp đọc hai con số này khác hẳn nhau. Phải qua hàm `vn(x, 2)`. **Bài học:** mọi số hiển thị đều đi qua hàm định dạng, không f-string trần. |
| T54 | 🔴 **Biểu đồ nói ngược chú thích khi chuẩn hóa sai đại lượng** | Hình «chặt/rộng» chuẩn hóa min-max nên thanh nhãn CHẶT lại DÀI HƠN thanh nhãn rộng (`stereo_width` rộng = 0,135 vs `swing_phase` chặt = 0,384). Phải vẽ **thẳng đại lượng dùng để phân loại** (IQR÷trung vị). **Bài học:** trục biểu đồ phải là chính con số sinh ra nhãn, không phải một phép chuẩn hóa khác. |
| T55 | 🟢 **Kết luận viết cứng trên hình sẽ lệch khi dữ liệu đổi** | Chú thích ghi «lệch cao độ chặt nhất» nhưng xếp hạng thật là `buoc_lien` (0,09). Đã sửa thành đọc `keys[0]` sau khi sắp xếp. **Bài học:** mọi câu kết luận trên hình phải suy từ dữ liệu vừa vẽ, giống quy tắc T27 cho số trong PDF. |
| T56 | 🟢 **Ảnh mẫu THẬT đắt hơn mọi biểu đồ với người duyệt** | Lưới 8 thumbnail thật của video top cho thấy mô-típ lặp lại (nền tối, một người, chữ lớn, tông hổ phách) trong 3 giây — điều mà bảng số liệu thumbnail không truyền đạt nổi. **Bài học:** khi có dữ liệu gốc dạng ảnh, hiển thị ảnh trước, thống kê sau. |
| T57 | 🔴 **Báo cáo nghiên cứu không được phán quyết thay người duyệt** | Hình điểm số vẽ vùng nền «BỎ / THEO DÕI / VÀO» và hộp mở đầu ghi «VÀO CÓ ĐIỀU KIỆN» — trong khi mọi con số đều là ƯỚC LƯỢNG (RPM sai số 4 lần, M2.4 chỉ 1 snapshot). Người dùng chỉ ra: quyết định vào hay không là của sếp. Đã gỡ vùng ngưỡng, gỡ phán quyết ở **4 chỗ** (hình, hộp mở đầu, ô KPI, §9.2). **Bài học:** ranh giới là *trình bày dữ kiện + độ bất định*, dừng trước khi khuyến nghị. |
| T58 | 🟢 **Số đè lên cột khi đặt nhãn theo toạ độ dữ liệu** | «11,5×» đặt giữa vùng vẽ nên chồng lên cột CHỦ ĐỘNG. Sửa: nới trần trục 1,7×, đặt bội số **trên mũi tên nối hai cột**. **Bài học:** nhãn phải neo vào khoảng trống đã tính trước, không neo vào giá trị dữ liệu. |
| T59 | 🔴 **Chú thích biểu đồ lệch vì neo vào axes thay vì figure** | Hình hai cột: `note()` neo vào `a1` nên căn giữa theo **nửa trái**, lệch hẳn. Sửa: neo vào `fig.text(0.5, …)` và suy mép dưới từ cụm axes. Cùng lỗi khiến nhãn 2 dòng của cột phải tràn sang biểu đồ trái. **Bài học:** mọi chú thích chung của hình phải neo vào figure. |
| T60 | 🔴 **`.replace('.', ',')` áp lên CẢ CÂU làm cụt câu** | Chú thích «…chỉ 6,9 tháng.» thành «…6,9 tháng,» — dấu chấm kết câu bị đổi thành phẩy, câu treo lơ lửng. **Bài học:** chỉ đổi dấu thập phân của riêng con số (`f'{x:.1f}'.replace(...)`), không bao giờ áp lên chuỗi có dấu câu. |
| T61 | 🟢 **Tiếng lóng nội bộ lọt vào tài liệu cho cấp duyệt** | Người dùng chỉ ra «cửa sổ đã chín» — sếp không hiểu. Soát ra 5 nhóm thuật ngữ trong hồ sơ: *cửa sổ đã/chưa chín · VPD · Spearman · Simpson · Gini*. Đã dịch sang lời thường («chỉ tính video đủ 3 tháng», «lượt xem mỗi ngày», «mức liên hệ trên thang 0–1»), giữ nguyên ở các báo cáo dành cho người nghiên cứu. **Bài học:** cùng dữ liệu, hai tầng ngôn ngữ — soát tiếng lóng theo ĐỐI TƯỢNG ĐỌC, không theo file. |
| T62 | 🔴 **Silero VAD loại sạch GIỌNG HÁT, và không báo lỗi** | Bật `vad_filter=True` trong faster-whisper: video có giọng suốt **98%** thời lượng trả về **0 đoạn**. Silero huấn luyện cho giọng NÓI; giọng HÁT có cao độ kéo dài + nhạc đệm chồng lên → bị xếp "không phải speech". Nguy hiểm nhất: video bị gắn nhãn "nhạc nền không lời" **trông y hệt dữ liệu hợp lệ**. Sửa: bỏ VAD, dùng `no_speech_prob` của chính Whisper — đo trên nội dung ĐÃ phiên âm, không loại bỏ trước khi nghe. **Bài học:** công cụ lọc trước khi đo là chỗ hỏng âm thầm; luôn thử bật/tắt trên một mẫu đã biết đáp án. |
| T63 | 🟡 **403 của YouTube có ngưỡng theo ĐỘ DÀI, không phải rate-limit** | Đo 2026-08-19: video 39s/48s/51s tải được cả ba; 120s/160s/34ph→138ph **403 trên cả ba format**. Loại trừ: nghỉ 60s không đổi, video đối chứng **ngoài corpus** cũng 403. Cơ chế: video dài tải nhiều fragment, YouTube từ chối từ request thứ hai. **Bài học:** khi một quyết định cũ (repo audio-dna D-006 "403 là rate-limit tạm thời", 17/8) mâu thuẫn với quan sát, thiết kế phép thử TÁCH BẠCH được hai giả thuyết thay vì thử lại nhiều lần. |
| T64 | 🟡 **Phiên bản công cụ mạng là nghi phạm đầu tiên, không phải cuối cùng** | `yt-dlp 2024.08.06` trả *"Please sign in"* trên mọi video — tưởng bị chặn tài khoản. Thực ra bản cũ hơn một năm, YouTube đã vô hiệu client cũ. Nâng lên 2026.07.04 là hết. Thêm: gọi `python3 -m yt_dlp` chứ không gọi lệnh trong PATH (có thể trỏ bản cũ khác). **Bài học:** với công cụ chạy đua với máy chủ bên ngoài, kiểm phiên bản TRƯỚC khi chẩn đoán chính sách. |
| T65 | 🟢 **Hai tầng dữ liệu cho nội dung có bản quyền** | Lời hát: `lyrics_raw.parquet` (văn bản đầy đủ, **chỉ nội bộ**, để tính toán) tách khỏi `lyrics_features.parquet` (chỉ thông số, thứ duy nhất vào báo cáo). Chép nguyên văn lời vào brief vừa rủi ro bản quyền vừa **vô dụng cho sản xuất** — chép lời kênh khác không tái tạo được gì, chỉ đạo nhái. Nguyên tắc y hệt audio: đưa nhạc sĩ KHOẢNG BPM và tỷ lệ stem, không đưa mp3 của bản thắng. **Bài học:** ranh giới không nằm ở chỗ có lưu hay không, mà ở chỗ cái gì được PHÁT TÁN. |
| T66 | 🔴 **Trường CHẨN ĐOÁN lọt vào brief sản xuất** | Đổ 184 trường vào công thức tái tạo thì `harmony.key.coverage` và `semantic.genre_entropy` lọt thẳng vào nhóm **BẮT BUỘC** — nhưng chúng đo độ tin cậy của công cụ đo, không mô tả bản nhạc. Brief sẽ bảo người dựng chỉnh một con số họ không đặt được. Sửa: hàm `is_production_param()` lọc theo mẫu tên (`confidence|coverage|n_beats|_cv$`…), loại 20 trường. **Bài học:** tự động hoá việc chọn trường thì phải hỏi «người dùng cuối THAY ĐỔI được cái này không», không chỉ hỏi «cột này có đủ dữ liệu không». |
| T67 | 🟡 **Bản xuất gọn bị nhầm là toàn bộ dữ liệu** | `audio_dna.xlsx` 45 cột được dùng suốt như thể là bộ dữ liệu đầy đủ; bản gốc `merged.jsonl` có **594 trường trên cùng 307 track đó**. Giai điệu 4→35, hoà âm 2→10, stem 5→88. Công thức tái tạo từ 26 lên **161 thông số** mà không cần thêm một dòng dữ liệu nào. **Bài học:** khi nhận file Excel/CSV, hỏi ngay nó có phải bản xuất từ nguồn khác không — bản xuất luôn mất trường. |
| T68 | 🟡 **Tiền tố lặp khi làm phẳng JSON lồng nhau** | Mỗi phase gói dữ liệu trong khối trùng tên phase → `melody.melody.stepwise_ratio`, `stems.stems.drums.attack_ms`. Không sai dữ liệu nhưng tên dài vô ích, và phép kiểm đầu tiên trả về **bảng trống** vì tôi tra theo tên đoán. Sửa trong `flatten()`: `if prefix.rstrip('.').endswith(k)` thì bỏ tầng lặp. **Bài học:** bảng kết quả trống rỗng là dấu hiệu tên cột sai, không phải dữ liệu thiếu — kiểm tên thật trước khi kết luận. |
| T69 | 🔴 **Ngưỡng `no_speech_prob` bê nguyên từ giọng NÓI sang giọng HÁT gắn nhãn sai hàng loạt** | `A2` kế thừa ngưỡng của `L3` (`no_speech_prob<=0,60` → `voice_ratio<0,15` là nhạc nền) và gắn nhãn **"NHẠC NỀN" cho 7/25 track đầu — cả bảy đều hát đầy đủ 99–189 chữ**. Đo trên 533 đoạn của chính ngách này: `no_speech_prob` **trung vị 0,57** (p25=0,45 · p75=0,67), tức ngưỡng 0,60 cắt ngang giữa vùng giọng hát BÌNH THƯỜNG. Đây là T62 đội lốt mới: cùng gốc rễ (Whisper không chắc chắn về giọng HÁT), chỉ đổi vỏ từ Silero sang một hằng số. Và cùng kiểu nguy hiểm — **không có lỗi nào được ném ra**, track sai trông y hệt track đúng. Sửa: phân loại bằng **mật độ chữ** (`wpm<12` hoặc `<25` chữ), thứ thật sự phân biệt hát với nhạc đệm; bài hát thật trong ngách thấp nhất **32 chữ/phút** nên ngưỡng 12 nằm giữa hai vùng, không sát mép. **Bài học:** hằng số ngưỡng là **giả định về phân phối dữ liệu**, không phải cấu hình — chép sang nguồn dữ liệu mới thì phải ĐO LẠI phân phối, và chọn đại lượng phân loại nằm ngoài vùng mà công cụ đo vốn đã yếu. |
| T70 | 🟢 **Độ dài trong sổ metadata lệch so với file thật** | `_index.json` của bộ track cắt sẵn ghi `duration_s` lệch **>2s ở 105/307 track**, cao nhất **+10s** (đệm bộ mã hoá + mốc chapter làm tròn). `words_per_min` chia cho thời lượng → lệch 10s trên bài 224s là **sai 4%** ngay ở thông số cốt lõi. Sửa: `A1_ingest` luôn `ffprobe` đo lại, ghi cả hai cột (`duration_s` đo thật, `index_duration_s` theo sổ) và báo số track lệch. **Bài học:** với file media, sổ metadata là gợi ý — con số dùng để CHIA phải đo từ chính file. |
| T71 | 🔴 **p=1,8·10⁻²⁰ vẫn là bẫy gộp — 24/35 mối lời×nhạc bị bác bỏ** | Ghép 307 track có CẢ lời và nhạc, xét 35 mối tương quan. Nhiều mối p cực nhỏ: `words_per_line × guitar` rho=+0,50 p=1,8e-20 — trông như phát hiện lớn. Tách theo 6 kênh: rho co về −0,13…+0,27, **1/6 kênh đảo dấu**. Chỉ **2/35 mối** qua được kiểm (0 kênh đảo dấu + rho trong kênh ≥0,15); **24 mối bị bác bỏ**. Nếu tin p-value thì đã đưa ~12 «phát hiện» giả vào công thức sáng tác. **Bài học:** với dữ liệu gộp nhiều kênh/nguồn, p-value đo được *có* tương quan chứ không đo tương quan đó thuộc tầng nào. Kiểm tách nhóm là BẮT BUỘC, và phán quyết phải dựa vào «bao nhiêu nhóm đảo dấu», không dựa vào p. |
| T72 | 🟡 **Chèn khối `if` vào giữa khối `if` khác đẩy lệch dòng `ok`** | Nối bước 04i vào `run_all.sh` bằng cách chèn `fi` + khối mới: `bash -n` báo **cú pháp sạch**, nhưng dòng `ok "AUDIO_RECIPE.json"` rơi vào khối lời hát — sẽ báo «đã dựng công thức nhạc» cả khi nhánh nhạc không chạy. **Bài học:** `bash -n` chỉ kiểm cú pháp, không kiểm dòng nào thuộc khối nào. Sau khi chèn khối điều kiện, phải ĐỌC LẠI vùng vừa sửa — lỗi kiểu này im lặng và chỉ lộ ra khi chạy trên ngách thiếu dữ liệu. |
| T73 | 🔴 **Đếm từ khoá bằng `.count()` thổi phồng nặng vì khớp chuỗi con** | Đo «người nghe đang ở đâu»: `sin` khớp cả **sing** — từ dày đặc trong nhạc worship → «tội lỗi» nhảy **48,4% → 75,3%**; `king` khớp **making/taking** → **15,9% → 47,1%**. Sai gần gấp ba, và **không có lỗi nào được ném ra** — bảng trông hoàn toàn hợp lý. Bắt được vì đối chiếu với phép đo tay chạy trước đó. Sửa: `re.compile(r"\b…\b")`, cụm nhiều từ vẫn khớp bình thường. **Bài học:** đếm từ khoá trên văn bản tự nhiên phải dùng ranh giới từ ngay từ đầu; và luôn đo tay một mẫu TRƯỚC khi viết hàm, để có số đối chiếu. |
| T74 | 🟡 **Chỉ số bịa ra khi công cụ đo không cấp được ranh giới cần thiết** | Định đo VẦN cuối dòng — thông số rất đáng giá cho người viết lời. Nhưng Whisper gộp nhiều câu hát vào một segment (`…far from home | In a dry land…`), nên «cuối dòng» không tồn tại trong dữ liệu. Đo đại được 0,08 trong khi mắt thường thấy vần rất rõ (alone/home, praise/days). Thử tách câu theo chữ hoa thì hỏng nặng hơn — cắt cả tên riêng («Oh | God, | You are my»). **Đã bỏ hẳn chỉ số này** thay vì đăng một con số sai. **Bài học:** khi công cụ đo không cấp được đơn vị mà chỉ số cần, bỏ chỉ số — đừng dùng proxy tệ rồi chú thích nhỏ. Một con số sai trong báo cáo nguy hiểm hơn một ô trống. |
| T75 | 🟢 **«Độ tập trung rộng» áp lên PHÁT HIỆN làm đảo ngược ý nghĩa** | Ngôi kể nằm chung bảng với 10 thông số đo lường, nên «chúng ta = 0,0%» bị gán nhãn **rộng → tự do**, đọc thành «muốn viết gì cũng được». Thực ra đó là **kết luận rõ ràng nhất của cả phân tích**: lời viết cho người nghe MỘT MÌNH. Người dùng phát hiện khi đọc bản in. Sửa: tách ngôi kể khỏi bảng ràng buộc, đưa sang mục «viết cho ai». **Bài học:** khung phân loại (CHẶT/vừa/rộng) chỉ đúng với thông số có thể ĐIỀU CHỈNH. Áp lên biến mô tả đối tượng thì nói ngược nội dung. |
| T76 | 🔴 **Kết luận từ n=5 đặt ở trang 1 bị đọc thành quy luật của cả ngách** | Brief nhạc ghi «5/5 bản ở điệu TRƯỞNG» — đúng với mẫu, nhưng in ở ô nổi bật trang 1 thì người đọc hiểu là chuẩn ngách. Đo trên **307 track: chỉ 65,5% trưởng**, tức **1/3 ngách đang dùng điệu THỨ và vẫn chạy**. Người viết nhạc theo báo cáo sẽ tưởng điệu thứ là lạc chất. Sửa: thêm `step04j_music_wide.py` đo lại các thông số ĐO ĐƯỢC trên toàn bộ track, đặt hai cỡ mẫu cạnh nhau. **Bài học:** cỡ mẫu phải đi kèm con số Ở CHÍNH CHỖ IN NÓ, không chỉ nằm trong mục phương pháp. Và khi có sẵn dữ liệu rộng hơn trong cùng thư mục, dùng nó — đừng để kết luận n=5 đứng một mình. |
| T77 | 🟡 **Suýt “sửa” một con số đúng vì quên bẫy đã ghi trong chính dự án** | Review báo cáo, tôi thấy BPM ghi 71,8 (n=5) trong khi 307 track cho **88,2** → định báo là sai. Kiểm tiếp: **28% track >120 BPM** — dấu hiệu bẫy nhân đôi tempo đã ghi ở T38–39. Sau khi gỡ bẫy: **TV=75,0**, khớp với 71,8. **Con số trong báo cáo đúng; con số của tôi mới sai.** Xác nhận bằng ba nguồn độc lập (đề xuất half-time của DSP · quy tắc chia đôi theo chỗ lõm histogram · bản n=5 sửa tay). **Bài học:** trước khi tuyên bố một số cũ là sai, tra `lessons_learned` xem đại lượng đó đã có bẫy nào chưa. Dữ liệu thô rộng hơn KHÔNG tự động đúng hơn dữ liệu hẹp đã được kiểm tay. |
| T78 | 🔴 **Khớp theo TIÊU ĐỀ suýt kết luận sai về bản quyền lời hát** | Hai video khác nhau của cùng kênh đều đặt tên **"Amazing Grace"**. Nếu chấm theo tên bài, cả hai đều bị tính là "hát lại nhạc cũ hết bản quyền". Đọc nội dung thật: video 1 không trùng một dòng nào với bản 1779, chỉ mượn đúng cụm từ giữa bài — **sáng tác mới hoàn toàn**; video 2 mượn 2 dòng mở đầu rồi rẽ sang lời mới từ dòng ba. Đo n-gram thật trên 308 track: điểm khớp cao nhất toàn corpus chỉ **0,444** — không track nào tái hiện đủ để coi là "hát lại nguyên bản". **Bài học:** tiêu đề bài hát là quảng cáo, không phải bằng chứng nội dung — bất kỳ phân loại nào dựa trên bản quyền/nguồn gốc phải đối chiếu VĂN BẢN THẬT, không suy từ tên. |
| T79 | 🟡 **Phóng tác Kinh Thánh không trích nguyên văn KJV — regex cụm cố định bỏ sót 66/73 video** | Định nhận diện lời phỏng theo Psalm bằng cách khớp cụm cố định kiểu KJV ("the LORD is my shepherd"). Nhưng thị trường **phóng tác** ("The Lord's my shepherd") chứ không trích nguyên văn — regex cụm cố định chỉ bắt 7/73 video có "Psalm" trong tiêu đề. Sửa: tin vào tiêu đề tự khai (`Psalm \d+`) do chính nhà sản xuất công bố, thay vì suy luận nội dung bằng từ khoá chủ đề (dễ dương tính giả) hay cụm cố định (dễ bỏ sót phóng tác). **Bài học:** khi nội dung là biến thể tự do của một văn bản gốc, tín hiệu đáng tin nhất là thứ tác giả TỰ CÔNG BỐ (tiêu đề, mô tả), không phải khớp mẫu trên phần nội dung đã bị viết lại. |
| T80 | 🔴 **Mở rộng công thức tái tạo 26→161 tham số (T67) làm gãy ngầm builder trình sếp** | `build_niche_profile.py` tham chiếu `SPEC['bpm']`, `SPEC['lech_cent']`, `SPEC['bam_luoi_semitone']` — tên trường của bộ 26 tham số cũ. Sau khi tích hợp `audio_dna_full` (T67, đổi tên trường thành `timeline.rhythm.bpm`, `melody.autotune.cent_deviation_std`…), builder này **ném KeyError và dừng lại giữa `run_all.sh`**, để lại PDF cũ từ trước ngày tích hợp mà không ai biết — `verify_reports.py` không phát hiện vì nó chỉ so điểm số, không kiểm file có được ghi lại hay chưa. Tồn tại 6 ngày không bị phát hiện. **Bài học:** đổi tên trường dữ liệu nguồn phải `grep` toàn bộ `pipeline/report/` tìm mọi nơi tham chiếu tên cũ — không chỉ sửa builder đã biết là phụ thuộc nó. Và `verify_reports.py` cần thêm một tầng kiểm: dấu **mtime** của PDF so với dữ liệu nguồn, không chỉ so điểm số bên trong. |
| T81 | 🔴 **Link nguồn tự sinh theo quy tắc đặt tên: 5/39 chết, không cái nào báo lỗi** | Bổ sung cột nguồn cho corpus PD, tôi suy URL Wikipedia từ tên bài theo quy tắc (thay dấu cách bằng `_`). Kiểm HTTP thật: **5/39 trả 404** — `Savior` vs `Saviour` (chính tả Anh-Anh), hai bài không hề có trang riêng, hai bài sai hậu tố định danh. Trước đó thử Hymnary.org thì **mọi URL đều trả 403 kể cả slug bịa** — nguồn chặn bot thì không phân biệt được link thật với link chết, nên loại luôn nguồn đó. Sửa: tra slug đúng qua Wikipedia search API, hai bài không có trang thì trỏ về nguồn thay thế hợp lý (trang tác giả, tuyển tập gốc) thay vì bịa URL. **Bài học:** URL suy theo quy tắc là **giả thuyết, không phải dữ liệu** — phải kiểm HTTP từng cái trước khi in ra tài liệu giao cho người dùng, và chỉ chọn nguồn nào phân biệt được 200 với 404. Đã gắn cờ kiểm lại: `python3 pipeline/report/build_pd_corpus_list.py --check`. |
| T82 | 🔴 **Báo cáo nêu kết quả nhưng không cho người đọc đường ĐỐI CHỨNG** | Báo cáo PD nói "1 video mượn Amazing Grace" nhưng không có `video_id`, không link, không timestamp — người đọc muốn tự nghe kiểm thì bó tay, buộc phải TIN con số. Sửa: `step_pd_evidence.py` xuất mọi track có điểm khớp **> 0 (kể cả 8 track DƯỚI ngưỡng)** kèm cụm 4 từ trùng nguyên văn + link YouTube tua tới giây có cụm đó. Đồng thời bắt 2 lỗi trong chính báo cáo cũ: (a) câu "1 video (**13 track**)" — 13 là TỔNG track của video chứ không phải số track khớp (**chỉ 1**), đọc lên thành "mượn 13 bài"; (b) cột `title` là tên TRACK trong compilation, **không phải tên video YouTube** — in mỗi tên track thì không ai tìm ra video. **Bài học:** báo cáo phân loại phải kèm đường đối chứng tới dữ liệu gốc, và phải liệt kê cả trường hợp DƯỚI ngưỡng — giấu đi thì bảng mất tác dụng kiểm chứng, chỉ còn tác dụng thuyết phục. |
| T83 | 🟡 **Cụm n-gram toàn từ thông dụng là trùng NGẪU NHIÊN, không phải trích dẫn** | Track *Green Pastures Blues* bị chấm khớp *I'll Fly Away* chỉ vì chung cụm **"when this life is"** — bốn từ tiếng Anh phổ thông nhất, trùng do ngôn ngữ chứ không do vay mượn. Thêm bộ lọc `is_distinctive()`: cụm phải chứa ít nhất 1 từ đặc hiệu (`amazing`, `foretaste`, `faithfulness`) mới tính là bằng chứng trích dẫn. Bắt được 1/9 dương tính giả. **Ranh giới không tuyệt đối** — cụm `every time i feel` vẫn lọt vì `feel` không nằm trong danh sách từ thông dụng, dù thực tế cũng rất phổ thông; đã ghi thẳng điểm yếu này vào báo cáo thay vì giấu. **Bài học:** khớp n-gram cần thêm tầng lọc ĐẶC HIỆU, không chỉ tầng ngưỡng điểm — và khi bộ lọc có vùng xám, nêu đúng ca nào nằm trong vùng xám để người đọc tự phán quyết. |
| T84 | 🔴 **Mỗi bước một báo cáo = 188 trang không ai đọc** | 99_report tích tụ **18 PDF / 188 trang**. Mỗi báo cáo STEP tự mở bằng "Tóm tắt điều hành" và tự đóng bằng "Độ tin cậy và điều chưa biết" — **7 lần lặp cùng cấu trúc**; bộ số nền (53 kênh / 7.193 video / 12,05 điểm) xuất hiện ở **6-7 file khác nhau**. Người đọc phải mở 7 file mới ghép được bức tranh, nên phản hồi là «sếp tôi còn chả thèm nhìn». Sửa: gộp 7 STEP (79 trang) vào `build_detail.py` (**8 trang**) — tham số mẫu nói MỘT LẦN ở đầu, mọi cảnh báo độ tin cậy gom về MỘT mục cuối, thân bài chỉ còn kết quả. Thêm `_phu-luc/` cho tài liệu không trình, và README.md chỉ rõ nộp bản nào. **188 → 96 trang, 18 → 11 file.** **Bài học:** một báo cáo cho mỗi bước phân tích là cấu trúc thuận cho NGƯỜI VIẾT, không thuận cho người đọc — cấu trúc đúng là theo câu hỏi người đọc cần trả lời, và mỗi tham số/cảnh báo chỉ được nói ở đúng một chỗ. |
| T85 | 🟡 **`.gitignore` vô hiệu với file đã stage — 7.194 ảnh và 42 `.pyc` vẫn bị theo dõi** | `.gitignore` có `__pycache__/` từ lâu nhưng `git ls-files` vẫn liệt kê 42 file `.pyc`: quy tắc ignore **không áp dụng cho file đã được add trước đó**. Cùng lỗi với `raw/thumbs/` — **7.194 ảnh / 1,1 GB, chiếm 97% số file repo (7.194/7.439)**. Sửa: `git rm -r --cached` (thêm `-f` khi nội dung stage khác đĩa) rồi bổ sung quy tắc; ảnh **ở lại trên đĩa**, chỉ bỏ khỏi theo dõi vì không tái tạo được bằng pipeline. **7.439 → 203 file.** **Bài học:** thêm dòng vào `.gitignore` KHÔNG đủ — phải `git check-ignore -v <file>` để xác nhận có hiệu lực, và `git ls-files | wc -l` để phát hiện thứ đã lọt vào từ trước. |
| T86 | 🟡 **Dời file đầu ra bằng tay thì lần chạy sau builder tự tạo lại ở chỗ cũ** | Dời 4 PDF phụ lục vào `_phu-luc/` bằng `mv`, chạy lại `run_all.sh` thì chúng **xuất hiện lại ở gốc** — builder ghi đường dẫn cứng `99_report/<tên>.pdf`. Kết quả: mỗi file tồn tại hai bản, đúng thứ vừa đi dọn. Suýt mắc lỗi nặng hơn: gom `_synthesis.json` + PNG vào `_data/` — **4 script đọc chúng từ `99_report/` sẽ gãy ngay**; phát hiện kịp và trả về chỗ cũ. Sửa đúng: sửa `out =` ở 6 builder + `mkdir(parents=True)`, và mở rộng glob của `verify_reports.py` để quét cả thư mục con. **Bài học:** sắp xếp lại thư mục đầu ra phải sửa ở NƠI SINH RA FILE, không phải ở thư mục đích — và trước khi dời bất kỳ file nào, `grep` xem có script nào đang đọc nó. |
| T21 | **Hỏi người dùng muốn ĐẦU RA gì trước khi chọn phương pháp** | Tôi làm 3 vòng kiểm định thống kê (04b/04d) trong khi thứ người dùng cần là **brief tái tạo được**. Kiểm định trả lời "làm thế này có thắng không?" (không chứng minh được); brief trả lời "nhóm thắng đang làm thế nào?" (mô tả chính xác được). **Hai câu hỏi khác nhau, cùng dữ liệu, phương pháp khác hẳn** |

---

# 🔵 TẦNG 4 — DIỄN GIẢI & BÁO CÁO

## Về chấm điểm

| # | Bài học |
|---|---|
| B1 | **Bảng chấm tay luôn không nhất quán** — không phải lỗi người chấm, mà lỗi hệ thống. Bằng chứng: 4 dòng nhạc có top20% = 57.6–61.8% (gần bằng nhau) nhưng bảng cũ cho **2, 3, 4, 5 điểm**. Rubric có ngưỡng cho cả 4 **cùng 4 điểm** |
| B2 | **Điểm tổng trùng nhau ≠ hai cách chấm tương đương.** Bảng thủ công và hệ thống cùng ra 12/20 nhưng phân bổ trục khác hẳn. **Luôn so từng trục, đừng so tổng** |
| B3 | **Động lượng quan trọng hơn quy mô hiện tại.** Ngách vừa mà đang lên tốt hơn ngách lớn đang đứng |
| B4 | **Ngách lớn mà bị khóa thì vô dụng với người mới.** Luôn đo cửa gia nhập, không chỉ đo quy mô |
| B5 | **"Theo dõi" ≠ ngách xấu.** Điểm 12.2 với T3=4.4 nghĩa là *dễ vào nhưng trần thấp* → hợp mô hình nhiều kênh song song |
| B6 | **Backtest rubric trước khi tin điểm.** Chạy ngược trên tập ngách đã biết. Sai lệch <0.55 điểm = rubric không mâu thuẫn với đánh giá thủ công |

## Về kết quả âm tính

| # | Bài học |
|---|---|
| B7 | **Kết quả âm tính có giá trị ngang kết quả dương tính.** 26 đặc trưng bị bác bỏ = 26 hướng đầu tư sai đã loại trừ |
| B8 | **Nhưng phải nói rõ:** "không tìm thấy khác biệt" **≠** "không có khác biệt". Có thể công thức phức tạp hơn (tương tác nhiều biến) |
| B9 | **Khi metadata cạn tín hiệu, đó cũng là kết luận.** Nó chỉ ra yếu tố quyết định nằm ở biến không đo được (chất lượng nội dung, retention) — và hướng nguồn lực về đúng chỗ |

## Về khán giả

| # | Bài học |
|---|---|
| B10 | **Comment like cao = phiếu bầu cộng đồng**, không phải ý kiến một người. Comment 1.444 like = 1.444 người đồng thanh — mạnh hơn khảo sát |
| B11 | **Mẫu "finally / at last" + like cao = lý do ngách tồn tại.** Đây là thứ đáng tìm nhất trong comment |
| B12 | **Người tự khai nhân khẩu là nhóm thiên lệch.** Chỉ 1.28% khai tuổi, nhóm đó có like TV=12 vs 4 → tuổi tính ra luôn **cao hơn** thực tế |
| B13 | **Chỉ ghi nhân khẩu khi TỰ KHAI.** Suy đoán từ tên là sai cả về đạo đức lẫn độ chính xác |
| B14 | **Đo tỷ lệ đề xuất vs tìm kiếm SỚM.** Nếu đề xuất thắng >3:1 (ngách này 7:1), toàn bộ công sức SEO là lãng phí |

## Về nghiên cứu từ khóa

| # | Bài học |
|---|---|
| B15 | **Bản đồ khoảng trống = hiệu quả (lift) × mức cạnh tranh (thị phần).** Old-school: lift 2.37× nhưng chỉ 3.96% thị trường → cơ hội thật |
| B16 | **Từ dùng để PHẢN HỒI ≠ từ dùng để TÌM KIẾM.** "amen" xuất hiện 2.233 lần trong comment nhưng vô dụng trong tiêu đề. Dùng cho giọng điệu mô tả |
| B17 | **Tag mô tả PHONG CÁCH cụ thể phân biệt tốt hơn tag chủ đề chung.** "delta blues", "slow blues" chỉ có ở video thắng; "prayer", "worship" có ở cả hai nhóm |
| B18 | **Chủ đề lặp ở ≥3 kênh khác nhau = công thức thật.** Ở 1 kênh = có thể may mắn |

## Về kiếm tiền & rủi ro

| # | Bài học |
|---|---|
| B19 | **RPM KHÔNG đo được từ YouTube API.** Mọi con số tiền là ước tính — phải ghi độ tin cậy Thấp và đưa **khoảng**, không đưa một số |
| B20 | **Kịch bản doanh thu lấy từ phân bố THẬT của ngách** (phân vị 25/50/90 của các kênh), không phải con số tưởng tượng |
| B21 | **Phân biệt mô tả trùng NỘI BỘ kênh vs CHÉO kênh.** Nội bộ = template bình thường; chéo kênh = rủi ro reused content. Không phân biệt sẽ báo động giả |
| B22 | **Rủi ro và hiệu quả có thể cùng chiều — đó là đánh đổi thật.** Video copy tiêu đề đối thủ có VPD cao hơn 68% nhưng tăng rủi ro chính sách. Trình bày cả hai mặt |

## Về quy trình

| # | Bài học |
|---|---|
| B23 | **Khảo sát sơ bộ không thay được pipeline chuẩn.** STEP_00 cho kết luận sai vì bỏ qua `is_matured` |
| B24 | **Ghi giả thuyết TRƯỚC khi phân tích** vào `NICHE_BRIEF.md`, đối chiếu ở STEP_08 — chống thiên lệch xác nhận. Ngách này: 4/5 giả thuyết đúng, 1 chưa xác minh |
| B25 | **Cổng quyết định sau STEP_02 tiết kiệm nhiều nhất.** Nếu cầu không tăng nhanh hơn cung, mọi phân tích sau là *tối ưu hóa một con tàu đang chìm* |
| B26 | **Mỗi kết luận phải kèm bằng chứng phản bác.** Mục "điều gì có thể làm kết luận này sai" là bắt buộc, không phải tùy chọn |
| B27 | **Qua kiểm định thống kê chưa đủ — phải qua NGƯỠNG ĐÁNG KỂ THỰC TẾ.** "Mặt lớn nhất" qua cả 3 lớp Simpson, nhưng chênh trong cùng kênh chỉ **3.5%** (26/41 kênh, phân vị 25% còn <1.0). Ghi **"QUA KIỂM ĐỊNH NHƯNG KHÔNG ĐÁNG KỂ"** thay vì "XÁC NHẬN" — nếu <10% thì người làm nội dung đổi theo cũng không thấy khác biệt |
| B28 | **Tách "được thuật toán đẩy" khỏi "được khán giả ủng hộ".** Cùng gọi là top nhưng đo hai thứ khác nhau: kênh giải thích **39.1%** biến thiên tỷ lệ like nhưng chỉ **0.9%** biến thiên lượt xem. Nghĩa là ủng hộ gắn với thương hiệu, còn view thì thuật toán phân phối gần như độc lập — **tin tốt cho người mới** |

---

# TỔNG KẾT: BẢY QUY TẮC SỐNG CÒN

Nếu chỉ nhớ được bảy điều:

1. **Chỉ so sánh dữ liệu đã chín** (≥60 ngày) — bẫy L1 suýt làm dừng một ngách khỏe
2. **Luôn có nhóm đối chứng** — không có thì mọi công thức đều là mê tín
3. **Kiểm 3 lớp: mẫu → toàn bộ → từng kênh** — bẫy Simpson đảo ngược 8.1× thành 0.48×
4. **Kiểm chính công cụ đo trước khi tin số nó cho ra** — Haar cascade báo 35.8% có mặt, sự thật 90.2%. Đối chiếu với biến độc lập, và **mở vài mẫu ra xem tận mắt**
5. **Ghi độ tin cậy và bằng chứng phản bác cho mọi kết luận** — biết chỗ nào chắc, chỗ nào không
6. **Thử pipeline trên ngách TRỐNG trước khi tin là nó tự động** — "chạy lại được" chỉ chứng minh file cũ còn đó. Phép thử này lộ ra 4 lỗi ẩn (T22–T25) trong một lần chạy
7. **Tên bước và độ tin cậy phải khớp nội dung** — bước tên *"Công thức thắng"* mà kết quả là 0/20 bác bỏ sẽ làm người đọc nghi ngờ cả hệ thống. Kết luận dựa trên thước đo proxy phải **được đánh dấu trong dữ liệu**, để mọi báo cáo hiển thị đúng mức tin cậy (T29–T30)

---

## LỊCH SỬ CẬP NHẬT

| Ngày | Ngách | Số bài học | Ghi chú |
|---|---|---|---|
| 2026-08-15 | `christian-blues` | 50 | Ngách đầu tiên chạy đủ STEP_00→08 + audit dữ liệu |
| 2026-08-17 | `christian-blues` | 60 | Phân tích 7.193 thumbnail thật. Thêm T12–T16 (lỗi công cụ đo), B27–B28. **Quy tắc sống còn tăng từ 4 lên 5** |
| 2026-08-17 | `christian-blues` | 71 | **Soát báo cáo.** Thêm T27–T28 (PDF lệch điểm) + `verify_reports.py` tự dò |
| 2026-08-17 | `christian-blues` | 69 | **Refactor + đúc kết.** Thêm T17–T21 (đo sai đối tượng), T22–T26 (nợ kỹ thuật ẩn). Điểm sửa **12.20 → 12.05** sau khi bỏ chấm điểm cho chỉ số không đo được. Quy tắc sống còn **5 → 6** |
| 2026-08-21 | `christian-blues` | 308+307 | **Cân lại hai nền dữ liệu của báo cáo nhạc.** Review phát hiện phần lời có 308 mẫu còn phần nhạc chỉ 5 → lệch hẳn một bên. Thêm `step04j_music_wide.py`: BPM/điệu thức/độ to/dải động trên **307 track**, gỡ bẫy nhân đôi tempo cho **117/307 track (38%)**. Sửa 3 lỗi review bắt được: «5/5 điệu trưởng» → **65,5%** (T76); tóm tắt tự mâu thuẫn với bảng độ tập trung; số kênh/bài không nhất quán. Thêm phát hiện âm tính: **lời buồn KHÔNG cần điệu thứ** (p=0,57 · 4/6 kênh ngược chiều) — bác bỏ giả định trực giác của người viết nhạc. Mục Giới hạn thêm 2 mục cho phần nhạc. Báo cáo 7→8 trang. Thêm T76–T77 |
| 2026-08-26 | `christian-blues` | — | **Dọn báo cáo + cấu trúc repo.** Phản hồi: «tạo ra 1 mả file báo cáo, nhiều thông tin trùng lặp… sếp tôi còn chả thèm nhìn». Khảo sát: **18 PDF / 188 trang**, bộ số nền lặp ở 6-7 file, `STEP04c` là **bản sao 100%** của `STEP04g` (diff 0/332 dòng) và không script nào sinh ra nó. Gộp còn **2 tầng**: `BAO-CAO_Christian-Blues.pdf` (8tr, thêm mục 10 «làm gì tiếp theo thứ tự» + mục 11 bản đồ tài liệu) và `CHI-TIET_Phan-tich-day-du.pdf` (8tr, gộp 7 STEP, gom mọi cảnh báo về mục 6); 6 tài liệu kỹ thuật vào `_phu-luc/`; thêm `99_report/README.md`. **188 → 96 trang, 18 → 11 file.** Git: gỡ 7.194 ảnh + 42 `.pyc`, **7.439 → 203 file** (T85). Sửa 6 builder ghi thẳng vào `_phu-luc/` (T86). Pipeline 62 giây, điểm 12,05 không đổi. Thêm T84–T86 |
| 2026-08-26 | `christian-blues` | 308 | **Đường đối chứng cho kết luận bản quyền.** Theo yêu cầu «video nào, track nào đang trùng để tôi nghe đối chứng»: `step_pd_evidence.py` + `PHU-LUC_Doi-chung-Track.pdf` — **9 track** có điểm khớp >0 (1 vượt ngưỡng, 8 dưới) trên **8 video / 4 kênh**, mỗi dòng có cụm 4 từ trùng nguyên văn và **link YouTube tua tới giây** (9/9 link bấm được, 8/8 video kiểm chứng còn sống). Bộ lọc `is_distinctive()` bắt **1 dương tính giả** (T83). Sửa 2 lỗi trong báo cáo PD cũ: «1 video (13 track)» → **1 track / video 13 track**, và bổ sung tên video YouTube bên cạnh tên track (T82). 17→18 báo cáo, 78 giây, điểm 12,05 không đổi |
| 2026-08-26 | `christian-blues` | 39 | **Phụ lục truy nguyên bộ đối chiếu PD.** Theo yêu cầu «cho tôi danh sách 36 bài PD, có link và nguồn từng bài»: bổ sung `author`/`kind`/`source_url` cho cả 39 mục trong `hymns_pd.json`, dựng `build_pd_corpus_list.py` → `PHU-LUC_Bo-doi-chieu-PD.pdf` (5 trang, **43 link bấm được**, 38 URL duy nhất). Kiểm HTTP bắt **5/39 link tự suy bị chết** trước khi in (T81); thêm cờ `--check` để rà lại định kỳ. Tách nhóm an toàn: **15 spiritual khuyết danh** (không có người thừa kế đòi quyền) vs **21 thánh ca PD do hết hạn**. Nêu 2 cái bẫy trong chính bảng: *How Great Thou Art* PD phần thơ gốc nhưng **bản dịch Hine 1949 còn bản quyền**; *Deep River* PD phần dân ca nhưng **bản phối Burleigh 1917 là tác phẩm riêng**. Thêm T81 |
| 2026-08-25 | `christian-blues` | 308 | **Phân loại bản quyền lời (Public Domain vs sáng tác mới) + đúc kết cuối.** Dựng `pipeline/analyze/step_pd_classify.py` + corpus 39 hymn/spiritual PD (`framework/04_reference/pd_corpus/hymns_pd.json`): so n-gram thay vì khớp tiêu đề, tránh bẫy T78. Kết quả trên 30 video/308 track: **76,7% sáng tác mới hoàn toàn, 20,0% phóng tác Psalm** (PD ý, giai điệu mới), chỉ **3,3% mượn câu mở đầu 1 hymn PD** — không video nào "hát lại nguyên bản". Dựng 2 báo cáo cuối theo yêu cầu «đúc kết, không giải thích thừa»: `TONG-HOP_Duc-Ket.pdf` (bảng CUNG↔CẦU kiểu FMG, kết bằng phán quyết `=>`) và `NHAC_Ban-quyen-PD.pdf`. Sửa ~15 chỗ số kiểu Mỹ gõ cứng trong `step08_synthesis.py` (nguồn `_synthesis.json` cho mọi báo cáo tổng hợp). Phát hiện và sửa T80 (builder trình sếp gãy ngầm 6 ngày do đổi tên trường T67). Thêm T78–T80 |
| 2026-08-21 | `christian-blues` | 308 | **Đào sâu lời hát + dọn báo cáo final.** Theo phản hồi: bỏ ký hiệu lạ (`«»`, `%` dính tên cột), bỏ mọi nhắc tới bản cũ (đây là bản gửi đi). Thêm **5 chiều mới** trả lời «viết cho ai, họ được gì»: trạng thái người nghe · lời hứa · cung cảm xúc 3 phần · xưng hô với Chúa · tách ngôi kể khỏi bảng ràng buộc. Phát hiện: **nỗi đau ≤51,9% nhưng 5/7 lời hứa ≥65,3%** (chạm nhẹ đau, đổ đầy giải pháp); cung cảm xúc **−0,07 → +0,22** (đừng kết bài ở chỗ tối); **Lord 78,6% vs Jesus 33,1%**. Bắt 3 lỗi: T73 (đếm chuỗi con sai gấp 3), T74 (bỏ chỉ số vần vì Whisper không cấp ranh giới câu), T75 (nhãn «rộng» làm đảo ý ngôi kể). Thêm T73–T75 |
| 2026-08-21 | `christian-blues` | 308 | **Báo cáo nhạc HỢP NHẤT + phân tích lời.** Theo phản hồi «3 bản nhạc chia nhiều phần quá, khó đọc»: gộp 04h+04h2+04h3 thành `NHAC_Bao-cao-Hop-nhat.pdf` (5 trang), 3 bản cũ vào `_archive/` kèm bảng tra chỗ nội dung chuyển đi. Thêm `step04i_lyrics.py` ghép **307 track có cả lời và nhạc** — thứ báo cáo cũ (n=5, không đối chứng) không làm được. Kiểm Simpson bác bỏ **24/35 mối** lời×nhạc dù p tới 1,8e-20; chỉ 2 mối dùng được. Phát hiện: ngôi «tôi» 9,5% vs «chúng ta» 0% (khớp bối cảnh nghe chủ động STEP_05); `unique_line_ratio` là ràng buộc CHẶT duy nhất; «than khóc» thấp nhất 58% — ngách ĐI QUA nỗi buồn, không ở lại. Thêm T71–T72 |
| 2026-08-21 | `christian-blues` | 307 | **Nhánh A — lời hát từ audio đã cắt sẵn.** Dựng `A1_ingest`/`A2_transcribe_tracks`/`A3_merge`: đi vòng qua bức tường 403 của `L2` (5/5 video hỏng, cả luồng ra 1 transcript). Đầu vào **307 track đã cắt theo bài / 21,3 giờ / 6 kênh**, ranh giới `pre_split` hạng gold, **100% đoạn gán đúng track** thay vì suy từ chapter. `A3` xuất đúng khuôn của `L3` nên `L5` không sửa dòng nào. Bắt T69 (ngưỡng giọng NÓI gắn nhãn sai 7/25 track hát đầy đủ) và T70 (sổ metadata lệch 105/307). Phủ sóng **29/50 video cohort** — phải ghi cỡ mẫu khi trích báo cáo. Thêm T69–T70 |
| 2026-08-19 | `christian-blues` | 95 | **Khai thác bản dữ liệu đầy đủ.** `audio_dna.xlsx` (45 cột) hoá ra là bản xuất gọn; nạp `merged.jsonl` **594 trường / 307 track** qua `normalize_audio_full.py`. Công thức tái tạo **26 → 161 thông số**: giai điệu 4→35, hoà âm 2→10, stem 5→88. Lọc 20 trường chẩn đoán khỏi brief. Phát hiện: bước liền bậc 0,728 và crest giọng 17,5 dB đều **CHẶT**. Thêm T66–T68 |
| 2026-08-19 | `christian-blues` | 94 | **Luồng LỜI HÁT (L1–L5).** Dựng `pipeline/lyrics/`: chọn mẫu → tải audio → ranh giới chapter → phiên âm faster-whisper CPU → thông số. Tự đứng độc lập, không phụ thuộc repo ngoài. Chapter YouTube thay tracklist (14/50 video → 188 track). Chặn được T62 (VAD xoá sạch giọng hát). Đo T63 (403 theo độ dài). Hai tầng dữ liệu T65. Thêm T62–T65 |
| 2026-08-19 | `christian-blues` | 93 | **Bổ sung chỉ số + dọn ngôn ngữ hồ sơ.** Thêm `step03b_production_norms.py` lấp đủ 7 dòng §5.5 (nhịp đăng 4,7 vs 3,3 · tracklist KHÔNG phải yếu tố thắng · **độ dài chia đôi 12/24 kênh** — bẫy gộp kênh). Thêm 2 hình (động lượng, chuẩn sản xuất) → 9 hình / 17 trang. Sửa chú thích lệch, câu cụt, 5 nhóm tiếng lóng. Thêm T59–T61 |
| 2026-08-19 | `christian-blues` | 92 | **Gỡ phán quyết khỏi hồ sơ + sửa bố cục hình.** Theo phản hồi người dùng: bỏ vùng «BỎ/THEO DÕI/VÀO», gỡ «VÀO CÓ ĐIỀU KIỆN» và «Theo dõi» ở 4 chỗ — hồ sơ chỉ cung cấp dữ kiện + độ bất định. Sửa chồng nhãn hình 2.2. Thêm T57–T58 |
| 2026-08-19 | `christian-blues` | 91 | **Trực quan hóa hồ sơ ngách.** Thêm `charts_profile.py` — 7 hình vẽ cho CẤP DUYỆT (kịch bản điểm, van hiệu chỉnh, chân dung, cung, công thức nhạc, khoảng trống tiếng nói, **lưới 8 thumbnail thật**). Bắt 2 lỗi tự kiểm: hình nói ngược chú thích, kết luận viết cứng. Hồ sơ 13 → 15 trang. Thêm T54–T56 |
| 2026-08-19 | `christian-blues` | 90 | **Hồ sơ ngách bản trình sếp.** Bám khung template v1.0 của R&D: 9 mục, cột TC (A/B/C), 13 trang. Ghi rõ **10 mục CHƯA CÓ DỮ LIỆU** kèm cách lấy thay vì đoán. Chốt van hiệu chỉnh (nghe chủ động 11,5×), giải nghịch lý sub↔view (Spearman 0,544 — không phải nghịch lý). Thêm T51–T53 |
| 2026-08-19 | `christian-blues` | 89 | **Kiểm định nhạc trên dữ liệu v2 (307 track).** Thêm `normalize_audio_dna.py` + `step04h2_audio_test.py` + PDF. Chặn 5 bẫy Simpson (gồm `stem_piano` p=7,6e-11 → BÁC BỎ). 1 XÁC NHẬN (`stem_drums`, 0/6 kênh đảo dấu). Phát hiện brief BPM cũ (n=5) lệch: 52–81 vs thật 67–154. Thêm T46–T50 |
| 2026-08-19 | `christian-blues` | 88 | **Chuẩn bị luồng mới (CDKH làm đầu vào).** Đọc flow R&D; viết `07_CDKH_CONTRACT.md` (từ vựng đóng + ràng buộc đạo đức + 5 câu cần chốt) và `08_FLOW_NGHIEP_VU.md` (bản dịch nghiệp vụ, 4 câu hỏi). Phát hiện playbook chưa tách theo phân khúc. **Chưa sửa code.** Thêm T44–T45 |
| 2026-08-18 | `christian-blues` | 86 | **PDF kiến trúc hệ thống.** 9 sơ đồ mermaid → Graphviz SVG (vector, chữ tìm được); `drift_check()` chống trôi sơ đồ; sửa đếm bước chính 12 → **10 + 2 nhánh**. Thêm T43 |
| 2026-08-18 | `christian-blues` | 85 | **Chốt câu hỏi có lời/không lời.** Gom bằng chứng 3 lớp từ STEP_05+06 vào `vocal_decision`; thêm mục 1 báo cáo 04h và hộp trong STEP_08 §7.6. Thêm T42 |
| 2026-08-18 | `christian-blues` | 84 | **Sửa luồng đánh số.** STEP_11 → **STEP_04h** (cùng nhánh tái tạo với 04g); `08_audio/` → `04_outlier/audio/`; brief ảnh đổi tên `STEP04g_` để thư mục báo cáo đọc liền mạch. Nhạc vào STEP_08 mục 7.6. Thêm T40–T41 |
| 2026-08-18 | `christian-blues` | 82 | **Pipeline âm nhạc (STEP_04h).** 5 bản top 0,07% → AUDIO_BRIEF + công thức tái tạo. Sửa bẫy nhân đôi tempo 5/5 bản. Thêm T38–T39 |
| 2026-08-17 | `christian-blues` | 80 | **Tối ưu rubric.** Đồng bộ tài liệu với code (ngưỡng T6, quy ước RPM); thêm bảng dẫn xuất «từ số thô đến điểm». Thêm T36–T37 |
| 2026-08-17 | `christian-blues` | 78 | **Đối chiếu nguồn ngoài + chuẩn căn lề.** Nghiên cứu FMG xác nhận tuổi 69≈70; nâng khoảng trống TBN Thấp→Vừa. Thêm T33–T35 |
| 2026-08-17 | `christian-blues` | 75 | **Truy vết bằng chứng.** Bản đồ khoảng trống: 5 → 18 bằng chứng có `src`+`id`; `conf` suy từ phán quyết thật (old_school Vừa → **Thấp**). Thêm T31–T32 |
| 2026-08-17 | `christian-blues` | 73 | **Chuẩn hóa tên bước.** Người dùng phát hiện nghịch lý: "công thức thắng" nằm trước mọi phân tích hợp thành nó. STEP_04 → **SÀNG LỌC ĐỐI CHỨNG**; 8 đặc trưng thumbnail gắn cờ `proxy`; danh xưng công thức thắng chuyển về STEP_10. Thêm T29–T30. Quy tắc sống còn **6 → 7** |
