# STEP_10 — PLAYBOOK KHỞI TẠO KÊNH (CÔNG THỨC THẮNG)

> Chạy **sau STEP_08**. Nếu có ảnh thumbnail, chạy sau **STEP_04g** để lấy thêm brief ảnh.

---

## 1. BƯỚC NÀY TRẢ LỜI CÂU HỎI GÌ

| Bước | Câu hỏi |
|---|---|
| STEP_04 | **ĐỪNG LÀM GÌ?** → loại bỏ giả thuyết sai (sàng lọc đối chứng) |
| STEP_08 | **CÓ NÊN VÀO?** → điểm số, xếp loại |
| **STEP_10** | **VÀO THÌ LÀM GÌ?** → thông số sản xuất cụ thể |

**Đây mới là "công thức thắng" của ngách** — danh xưng này trước kia gán nhầm cho STEP_04
(bài học T29). STEP_10 tổng hợp được vì nó chạy **sau** khi đã có thumbnail thật (04b),
chân dung khách hàng (05) và từ khóa (06). STEP_04 chỉ loại trừ, không tổng hợp.

Đầu ra là **hợp đồng máy đọc** để nạp thẳng vào workflow sinh nội dung tự động:
tiêu đề, mô tả, thẻ, thời lượng, nhịp đăng, thumbnail, kênh mẫu.

---

## 2. ⚠️ TẦNG MÔ TẢ, KHÔNG PHẢI TẦNG KIỂM ĐỊNH

Đây là điểm dễ hiểu nhầm nhất.

```
STEP_04b  KIỂM ĐỊNH  "đặc điểm X có GÂY RA thành công?"     → thường: không chứng minh được
STEP_10   MÔ TẢ      "nhóm thắng ĐANG LÀM thế nào?"          → công thức sao chép được
```

Playbook **không hứa** làm theo sẽ thắng. Nó giúp:
- sản xuất **nhanh** (không phải tự nghĩ từ đầu)
- **không lạc lõng** so với chuẩn ngách
- có **mốc đối chiếu** khi kênh chạy

Xem `00_system/01_ARCHITECTURE.md` §2.4.

---

## 3. NGUỒN DỮ LIỆU

| Tham số | Giá trị | Vì sao |
|---|---|---|
| Nhóm chuẩn | **top 5% lượt xem** | Mô tả nhóm dẫn đầu, không phải trung bình ngách (gồm cả kênh 23 view) |
| Lọc thời lượng | `duration_sec > 60` | Loại Shorts nếu ngách hướng video dài |
| Lọc độ chín | `is_matured` (≥60 ngày) | Bẫy L1 |

Đổi ngưỡng ở đầu `step10_playbook.py` (`TOP_Q`, `MIN_DUR`).

---

## 4. CHẠY

```bash
python3 pipeline/analyze/step10_playbook.py <niche>
python3 pipeline/_archive/report_by_step/build_report08.py   # đã archive 2026-08-28
```

Đã nằm trong `run_all.sh` — không cần chạy tay.

---

## 5. ĐẦU RA

### `09_playbook/CHANNEL_PLAYBOOK.json` — hợp đồng máy đọc

| Khóa | Nội dung | Dùng để |
|---|---|---|
| `title` | khuôn câu + tỷ lệ + từ vựng + hashtag | sinh tiêu đề |
| `description` | 6 khối có thứ tự, số ký tự, quy tắc | sinh mô tả |
| `tags` | nhóm lõi + mở rộng | gắn thẻ |
| `format` | thời lượng mục tiêu, ad slot | đặt độ dài bản nhạc |
| `cadence` | video/tuần | lập lịch sản xuất |
| `strategy` | **hai mô hình sản xuất đối lập** | chọn hướng trước khi bắt đầu |
| `thumbnail` | tỷ lệ người/chữ/màu | sinh ảnh + kiểm tự động |
| `reference_channels` | 5 kênh mẫu + số liệu | đối chiếu định kỳ |

### `09_playbook/CHANNEL_PROFILES.json` — hồ sơ 5 kênh hình mẫu (STEP_10b)

Sinh bởi `step10b_channel_profiles.py`. Mỗi kênh có:

| Khối | Nội dung |
|---|---|
| `định_vị` | tên kênh, **mô tả kênh**, từ khóa kênh — cách họ tự giới thiệu |
| `quy_mô` | view, video, sub, tỷ lệ hit, hệ số biến thiên |
| `sản_xuất` | mô hình, thời lượng, nhịp đăng, **view 10 video đầu**, kiểu khởi đầu |
| `công_thức_tiêu_đề` | kiểu chủ đạo, dấu phân cách, ví dụ top |
| `cấu_trúc_mô_tả` | độ dài, emoji, membership, tracklist |
| `quỹ_đạo` | view trung vị theo từng tháng |

Khối `bài_học` tổng hợp so sánh chéo: kênh cũ hồi sinh, kiểu khởi đầu, tỷ lệ hit.

> **Nguồn mới:** `channels_enriched.parquet` (mô tả kênh) — trước STEP_10b chưa bước nào dùng.

### `09_playbook/_playbook_data.json`
Số liệu thô đầy đủ (ví dụ tiêu đề thật, dòng mở đầu mô tả, phân bố…) để dựng báo cáo.

---

## 6. CÁCH PHÂN LOẠI TIÊU ĐỀ

Hàm `title_shape()` phân loại theo **kiểu câu** — vì đó là cái quyết định cách sinh tự động:

| Kiểu | Nhận diện | Ví dụ |
|---|---|---|
| `kinh_thánh` | tên sách + số chương | *Psalm 51 (Lyrics) \| Create in Me a Clean Heart* |
| `mệnh_đề_điều_kiện` | mở đầu bằng When/If/What | *When Fear Takes Over, Play This Gospel Blues* |
| `playlist` | chứa playlist/mix/collection | *Soul Saving "BLUES" Gospel Music … PLAYLIST* |
| `có_thời_lượng` | chứa số + hour/min | *Be Still \| 100 Minutes of Relaxing Black Gospel* |
| `có_trích_dẫn` | có dấu ngoặc kép | *"No More Chains Over Me" \| Deep Black Gospel* |
| `câu_cảm_xúc` | còn lại | *Somebody Been Praying For Me \| Deep Gospel Blues* |

**Ngách khác có thể cần kiểu khác** — sửa hàm này khi áp dụng cho ngách mới.

---

## 7. HAI MÔ HÌNH SẢN XUẤT

Bước này tự phát hiện các chiến lược đối lập trong nhóm top bằng cách chia theo
thời lượng trung vị của kênh (ngưỡng 15 phút).

Kết quả ở `christian-blues`:

| Mô hình | Thời lượng | Video/tháng | Tỷ lệ hit | Ví dụ |
|---|---|---|---|---|
| nhiều & ngắn | ~6p | 8,6 | 9% | `stillworshipmusic` (437 video ~3p → 16,7tr view) |
| ít & dài | ~62p | 7,1 | 11% | `oldiesgospelradio` (184 video ~108p → 8,6tr view) |

**Cả hai đều thành công.** Đây là lựa chọn chiến lược, không phải câu hỏi đúng/sai.

---

## 8. TIÊU CHÍ XONG

- [ ] `CHANNEL_PLAYBOOK.json` sinh được, đủ 8 khóa cấp 1
- [ ] Mục 7 hiện trong PDF STEP_08
- [ ] Mọi con số **truy vết được** về nhóm top (không có giá trị bịa)
- [ ] Đã ghi rõ **ba thứ playbook KHÔNG cung cấp** (nhạc, tên kênh, bảo đảm kết quả)
- [ ] `CHANNEL_PROFILES.json` có đủ 5 hồ sơ + khối `bài_học`
- [ ] `PROGRESS.md` cập nhật

---

## 9. GIỚI HẠN ĐÃ BIẾT

| Thiếu | Vì sao | Khắc phục |
|---|---|---|
| **Âm nhạc** | `media_probe` phủ 0,6% — dưới ngưỡng 30% | Cần crawl đặc trưng âm thanh |
| **Tên kênh** | Không có quy tắc suy ra tự động | STEP_10b cho **mô tả + tên 5 kênh mẫu** để tham chiếu. Mẫu quan sát: 2–3 từ ghép, gợi không gian thờ phượng (*Still Worship*, *Holy Groove*, *Oldies Gospel Radio*) |
| **Bảo đảm kết quả** | Bản chất tầng mô tả | Không khắc phục được — ghi rõ giới hạn |

---

## 10. LIÊN KẾT

| Tài liệu | Quan hệ |
|---|---|
| `STEP_08_synthesis.md` | Bước cha — playbook là mục 7 của báo cáo tổng hợp |
| `STEP_04b_thumbnail.md` | Cung cấp khối `thumbnail` (tùy chọn) |
| `STEP_05_audience.md` | Cung cấp bối cảnh nghe → quy tắc viết mô tả |
| `00_system/01_ARCHITECTURE.md` §2.4 | Phân biệt tầng mô tả và tầng kiểm định |
