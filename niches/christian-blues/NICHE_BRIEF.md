# NICHE BRIEF · CHRISTIAN BLUES

> Điền ở STEP_00, trước khi phân tích. Mọi agent đọc file này.

## 1. ĐỊNH NGHĨA
| Trường | Giá trị |
|---|---|
| Tên ngách | Christian Blues / Gospel Blues |
| Ngách cha | Christian/Gospel (85.2tr view/tháng, top20% = 81.98% — bị khóa chặt) |
| Thị trường mục tiêu | Mỹ (Tier-1); nhánh phụ LatAm (BR/PE/CO) |
| Ngôn ngữ chính | en-US · nhánh es-419, pt-BR |
| Mô hình sản xuất dự kiến | AI-first, có lời |

## 2. DỮ LIỆU
| Trường | Giá trị |
|---|---|
| Ngày crawl | 2026-08-13 |
| Nguồn | YouTube Data API v3 |
| Số kênh | 53 |
| Số video | 7.193 |
| Số comment | 145.150 (52.487 tác giả · phủ 5.330/7.193 video = 74%) |
| Snapshot `video_stats` | **1** ⚠️ → hạ tin cậy trục T2 xuống "vừa" |
| Bảng thiếu/yếu | `media_probe` chỉ 40/7.193 (0.6%) — **không dùng kết luận** |
| Cột thiếu | `tags` 23% · `default_audio_language` 39% · `channel_country` 674 dòng |

## 3. GIẢ THUYẾT BAN ĐẦU ⚠️
> Ghi TRƯỚC khi phân tích. Đối chiếu ở STEP_08.

| # | Giả thuyết | Kết quả |
|---|---|---|
| H1 | Ngách trẻ, cửa cho người mới còn rộng | 🟡 Sơ bộ ỦNG HỘ — 74% kênh < 12 tháng |
| H2 | Cầu đang tăng nhanh hơn cung | 🔴 Sơ bộ **BÁC BỎ** — M2.4 ≈ 0.35, view trung vị giảm 70% |
| H3 | Định dạng mix dài 1-3h là tối ưu | 🔴 Sơ bộ **BÁC BỎ** — 1-6m có VPD cao hơn 34% |
| H4 | Gospel là nhóm chấp nhận AI cao → lợi thế | 🟢 ỦNG HỘ (nguồn Wavelength) |
| H5 | Khán giả chủ đạo là người lớn tuổi Mỹ → RPM cao | 🟡 Sơ bộ ỦNG HỘ — cần định lượng ở STEP_05 |

## 4. NGƯỠNG LỌC ĐÃ CHỌN
Cỡ ngách 7.193 video → nhóm **5.000–10.000**, dùng ngưỡng mặc định.

| Tham số | Giá trị | Kết quả thực tế |
|---|---|---|
| B1 outlier_ratio | ≥ 5 + đã chín (≥60 ngày) | 435 video |
| B1 view tối thiểu | ≥ 20.000 | |
| B2 vpd | ≥ P90 (174,7194), age ≤ 90 ngày | 366 video |
| B3 top mỗi kênh | 5 | 264 video |
| B4 outlier_ratio | ≤ 0.2, view ≥ 500 + đã chín | 161 video |
| **Tổng video** | | **965 (13,4%)** ✅ trong mục tiêu |
| C1 like tối thiểu | ≥ 25 | 1.535 |
| C2 độ dài / like | ≥ 200 ký tự / ≥ 2 | 4.159 |
| C3 ngẫu nhiên | 1.500 | |
| **Tổng comment** | | **~6.800 (4.7%)** ✅ trong mục tiêu |

## 5. CÂU HỎI RIÊNG CỦA NGÁCH
1. **Pha loãng là do kênh rác hay cả ngách?** (câu hỏi sống còn — STEP_02)
2. Còn Thánh Vịnh nào chưa ai khai thác? (công thức Psalm lặp ở 3 kênh)
3. `vintage_gospel_vgx` làm gì mà 48 video ra 3.81tr view?
4. Vì sao thị trường đổ vào mix 1-3h khi 1-6m hiệu quả hơn?
5. Nhánh LatAm (BR/PE/CO) có đáng mở không?
6. Rủi ro policy khi kết hợp AI + nội dung tôn giáo?

## 6. RÀNG BUỘC
- Điều khoản YouTube API: làm mới hoặc xóa dữ liệu trong **30 ngày** (hạn ~2026-09-12)
- `author_hash` đã băm SHA-256 có salt — không truy ngược
- Chỉ ghi nhân khẩu khi người dùng tự khai
