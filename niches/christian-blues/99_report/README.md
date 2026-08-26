# Báo cáo — Christian Blues

## Nộp gì cho sếp

**`BAO-CAO_Christian-Blues.pdf`** (8 trang) — bản trình bày duy nhất.
Kết luận, bảng CUNG↔CẦU, 5 khoảng trống, 24 tiêu đề sẵn dùng, và mục 10 "làm gì tiếp
theo thứ tự". Mở bản này trước, và trong hầu hết trường hợp chỉ cần bản này.

## Khi bị hỏi sâu

| File | Trả lời câu hỏi gì |
|:---|:---|
| `CHI-TIET_Phan-tich-day-du.pdf` (8tr) | Số liệu đầy đủ từng bước + **toàn bộ cảnh báo độ tin cậy gom về mục 6** |
| `HOSO_Ngach_Christian-Blues.pdf` (17tr) | Công thức sản xuất: 161 tham số âm nhạc đo được, dùng brief cho AI/nhạc sĩ |
| `NHAC_Bao-cao-Hop-nhat.pdf` (8tr) | Âm thanh + lời hát: BPM, điệu thức, chủ đề, xưng hô, cung cảm xúc |
| `NHAC_Ban-quyen-PD.pdf` (4tr) | Nhạc thị trường là public domain hay sáng tác mới? Có lối tắt bản quyền không? |

## `_phu-luc/` — không trình, chỉ tra khi cần

| File | Nội dung |
|:---|:---|
| `RUBRIC_Khung-cham-diem.pdf` | Cách chấm 12,05/20: ngưỡng từng trục, trọng số |
| `ARCH_Kien-truc-He-thong.pdf` | Kiến trúc pipeline — dành cho người tiếp quản code |
| `PHU-LUC_Bo-doi-chieu-PD.pdf` | 36 hymn public domain + nguồn từng bài (link kiểm chứng) |
| `PHU-LUC_Doi-chung-Track.pdf` | 9 track khớp hymn + link YouTube tua tới chỗ trùng |
| `STEP04b_Phan-tich-Thumbnail.pdf` | Kiểm định thumbnail |
| `STEP04g_Brief-Thumbnail.pdf` | Brief tái tạo thumbnail |

## Các file rời khác (`.png`, `.csv`, `.json`)

**Không phải báo cáo** — là dữ liệu trung gian mà builder đọc vào lúc dựng PDF:

- `_synthesis.json` — nguồn số cho `BAO-CAO_` và `CHI-TIET_`
- `p*.png`, `s*.png` — biểu đồ nhúng vào PDF
- `backtest_*`, `cross_period_growth.csv`, `_data_audit.json` — dữ liệu kiểm định

Đừng gửi kèm khi nộp. Xoá đi thì `run_all.sh` dựng lại được.

## Dựng lại toàn bộ

```bash
bash pipeline/run_all.sh          # ~80 giây, dựng lại mọi PDF
```

Mọi con số trong PDF đọc động từ `_state/metrics.json`, `_state/scores.json`,
`99_report/_synthesis.json` lúc dựng — không gõ tay (quy tắc T27).

## Lịch sử dọn dẹp — 2026-08-26

Trước: 18 PDF / 188 trang. Sau: 5 PDF trình + 6 phụ lục.

- **Xoá 7 báo cáo STEP rời (79 trang)** — mỗi bản tự lặp "Tóm tắt điều hành" và
  "Độ tin cậy" riêng; gộp vào `CHI-TIET_` còn 8 trang. Script vẫn giữ, chạy
  `run_all.sh` không dựng lại chúng nữa.
- **Xoá `STEP04c_Tái tạo Thumbs.pdf`** — bản sao 100% của `STEP04g` (diff 0 dòng
  trên 332), và không script nào sinh ra nó.
- **Đổi tên** `TONG-HOP_Duc-Ket.pdf` → `BAO-CAO_Christian-Blues.pdf`.
