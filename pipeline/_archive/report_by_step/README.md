# Báo cáo theo BƯỚC — đã ngừng dựng

> Chuyển vào đây ngày **2026-08-28**, khi đầu ra chuyển sang bốn tài liệu
> **T1.1–T1.4**. Xem `framework/00_system/11_OUTPUT_CONTRACT.md`.

## Vì sao bỏ

Bảy script này tổ chức báo cáo **theo bước chạy** (STEP_02, STEP_03…). Ba vấn đề:

1. **79 trang cho một ngách.** Mỗi bản tự lặp "Tóm tắt điều hành" và "Độ tin cậy" riêng.
2. **Cùng một bộ số nền lặp ở 6–7 file.** Sửa một chỗ là lệch sáu chỗ còn lại.
3. **Người đọc phải mở 6 file** mới trả lời được một câu hỏi.

Cách mới tổ chức theo **người đọc** và **loại phát biểu**:

| | Loại phát biểu | Ai đọc |
|---|---|---|
| T1.1 | chỉ sự thật quan sát được | người quyết định đầu tư |
| T1.2 | giả thuyết có cấu trúc về cơ chế | người làm nội dung |
| T1.3 | thông số kỹ thuật để sản xuất | nhạc sĩ / vận hành Suno / designer |
| T1.4 | hồ sơ sâu từng đối thủ | người học chiến thuật |

## Nội dung đã đi đâu

| Script cũ | Nội dung nay nằm ở |
|---|---|
| `build_report.py` · `build_report03.py` | T1.1 §2 Trạng thái cung · T1.4 |
| `build_report04.py` | T1.2 §4 Bản đồ nhân–quả |
| `build_report05.py` | T1.1 §3 Dấu vết cầu · T1.2 §1–2 |
| `build_report06.py` | T1.1 §3 Từ khoá · T1.2 §3 Cơ chế 3 |
| `build_report07.py` | T1.1 §4 Kinh tế ngách · §5 Rủi ro |
| `build_report08.py` | T1.1 §Kết luận · `build_detail.py` |

## Dựng lại khi cần

Các script vẫn chạy được, chỉ không nằm trong `run_all.sh` nữa:

```bash
python3 pipeline/_archive/report_by_step/build_report03.py niches/<ngách>
```

Lưu ý: chúng đọc `_state/metrics.json` theo cấu trúc cũ. Nếu schema đổi thì
phải sửa trước khi chạy.
