# SÁU NHÓM NGUỒN — Y·P·S·V·K·N

> Chuẩn phân loại nguồn dữ liệu. Mọi phát biểu trong T1.1–T1.4 **bắt buộc**
> mang một mã nguồn. Không có mã → không được đưa vào tài liệu.
>
> Phiên bản: v1.0 · Lập 2026-08-28 · Nguồn: đúc kết sau 49 vòng cải tiến

---

## 1. VÌ SAO CẦN BẢNG NÀY

YouTube trả lời được **một** loại câu hỏi, và mù với hai loại còn lại:

| Câu hỏi nghiên cứu | YouTube nhìn thấy | Kết luận |
|---|---|---|
| Cái gì đang tồn tại, ai đang thắng, thắng bằng công thức nào? | **Đầy đủ** | YouTube là nguồn duy nhất cần thiết |
| Cầu nào có mà cung trên YouTube chưa đáp ứng? | **Rất kém** — chỉ suy gián tiếp qua vocab gap và autocomplete | Bắt buộc nguồn ngoài |
| Cầu sẽ dịch chuyển về đâu trong 6–12 tháng? | **Gần như mù** — YouTube chỉ hiện xu hướng *sau khi* cung đã hình thành | Bắt buộc nguồn ngoài |

Đây là lý do một hệ thống chỉ đọc YouTube sẽ **luôn** trả lời tốt câu 1 và
**luôn** đoán mò ở câu 2–3, dù chạy bao nhiêu vòng cải tiến.

---

## 2. BẢNG SÁU NHÓM NGUỒN

| Mã | Nhóm nguồn | Quan sát được cái gì |
|---|---|---|
| **Y** | YouTube | Cung đã tồn tại và đang thắng |
| **P** | Nền tảng khác (Spotify, app, podcast, TikTok) | Cung thay thế — cầu đã được phục vụ ở nơi khác |
| **S** | Tín hiệu tìm kiếm (Google Trends, autocomplete) | Cầu hiển thị qua hành vi, độc lập với ai phục vụ |
| **V** | Tiếng nói người dùng (Reddit, review app, forum) | Cầu phát ngôn, ngôn ngữ thật, cấm kỵ |
| **K** | Khoa học & báo cáo ngành | Cơ chế công năng, ràng buộc sinh lý |
| **N** | Nội bộ HG Media / FMG | RPM thật, Analytics kênh nhà |

---

## 3. TRẠNG THÁI HIỆN TẠI — NÓI THẲNG

Tính đến 2026-08-28, hệ thống mới chạm **hai** trong sáu nhóm:

| Mã | Trạng thái | Ghi chú |
|---|---|---|
| **Y** | ✅ Đầy đủ | 53 kênh · 6.413 comment · 307 bản ghi · 259 thumbnail |
| **P** | ❌ Chưa có | Chưa crawl Spotify/TikTok/podcast |
| **S** | ❌ Chưa có | Chưa lấy Google Trends / autocomplete |
| **V** | ❌ Chưa có | Chưa crawl Reddit / forum |
| **K** | ⚠️ Rời rạc | Có trích AARP/NEFE/APA/Luminate nhưng **không có quy trình**, không lưu vết |
| **N** | ❌ Chưa có | Chưa nối Analytics kênh nhà, RPM vẫn là ước lượng ngoài |

> **Hệ quả phải chấp nhận:** mọi kết luận về "khoảng trống" và "xu hướng
> 6–12 tháng" trong các tài liệu hiện tại đều đang dựa trên **Y đơn độc**,
> tức là dùng đúng loại nguồn mà bảng §1 nói là *rất kém* và *gần như mù*
> cho hai câu hỏi đó.
>
> Điều này **không** làm sai phần trả lời câu 1 (cung, đối thủ, công thức
> thắng) — phần đó Y là đủ. Nó chỉ giới hạn phần cầu và dự báo.

---

## 4. QUY TẮC SỬ DỤNG

| # | Quy tắc |
|---|---|
| **N1** | Mọi phát biểu trong T1.1–T1.4 phải mang mã nguồn, dạng `[Y]`, `[K]`, `[Y+S]`… |
| **N2** | Phát biểu về **khoảng trống cầu** chỉ dựa `[Y]` → phải ghi kèm `⚠ suy gián tiếp` |
| **N3** | Phát biểu về **xu hướng tương lai** chỉ dựa `[Y]` → **cấm**, phải có `[S]` hoặc `[P]` |
| **N4** | Nguồn `[K]` phải ghi tên báo cáo + năm + cỡ mẫu, không được ghi chung chung |
| **N5** | Nguồn `[K]` nói về dân số chung **không** thay được bằng chứng nội bộ về ngách |
| **N6** | Thiếu nguồn cho một mục → ghi `[—] chưa có nguồn`, **không** bỏ trống mục đó |

Quy tắc **N5** là bài học trực tiếp: bản định vị 14 hướng trước đây cho điểm
tin cậy 5/5 cho hai hướng nhờ dẫn AARP/NEFE, trong khi bằng chứng nội bộ của
chính hai hướng đó là **BÁC BỎ**. Báo cáo ngành nói "người Mỹ cô đơn" không
chứng minh "kênh làm chủ đề cô đơn sẽ có view".

Quy tắc **N6** làm lỗ hổng **hữu hình**. Một mục ghi `[—] chưa có nguồn` là
thông tin; một mục bỏ trống là ảo giác đã đầy đủ.

---

## 5. GHI MÃ NGUỒN Ở ĐÂU

### 5.1 Trong `metrics.json`

Thêm trường `source_class` vào `_meta` của mỗi chỉ số:

```json
"_meta": {
  "M2_4_demand_supply_gap": {
    "source": "processed/videos.parquet",
    "source_class": "Y",
    "computed_by": "A1",
    "confidence": "medium"
  }
}
```

### 5.2 Trong tài liệu T1.x

Đặt mã ngay sau phát biểu:

```
Cầu tăng 1,62× trong khi cung tăng 1,24× → gap 1,30  [Y]
41% người Mỹ 60+ tự nhận cô đơn năm 2025  [K · AARP 2025, n=2.000]
Chưa đo được kênh nhà chuyển đổi thế nào  [—] chưa có nguồn
```

---

## 6. LỘ TRÌNH BỔ SUNG NGUỒN

Xếp theo **tỷ lệ giá trị trên công sức**, không theo thứ tự bảng chữ cái:

| Ưu tiên | Mã | Việc cụ thể | Vì sao trước |
|---|---|---|---|
| 1 | **S** | Google Trends + autocomplete cho 20–30 cụm từ khóa ngách | Rẻ nhất, không cần khoá API, trả lời trực tiếp câu 2 và 3 |
| 2 | **N** | Nối Analytics kênh nhà khi kênh chạy | Là nguồn **duy nhất** cho retention/CTR/traffic source thật |
| 3 | **V** | Crawl Reddit theo subreddit liên quan | Cho ngôn ngữ thật và điều cấm kỵ — bổ khuyết đúng chỗ comment YouTube thiên lệch |
| 4 | **P** | Playlist Spotify + podcast cùng chủ đề | Cho biết cầu đã được phục vụ ở đâu ngoài YouTube |
| 5 | **K** | Chuẩn hoá quy trình trích báo cáo ngành | Đã dùng rời rạc, cần lưu vết để kiểm chứng lại được |

---

## 7. LIÊN KẾT

| Cần gì | Đọc file |
|---|---|
| Bốn tài liệu đầu ra dùng mã này | `11_OUTPUT_CONTRACT.md` |
| Chuẩn báo cáo & trích nguồn | `06_REPORT_STANDARDS.md` |
| Giao kèo CDKH với R&D | `07_CDKH_CONTRACT.md` |
| Ai đọc file gì | `05_FILE_CONTRACTS.md` |
