# Báo cáo nhạc — bản cũ, đã thay thế

Ba PDF này đã gộp thành **`../NHAC_Bao-cao-Hop-nhat.pdf`** (2026-08-21).

| Bản cũ | Nội dung | Nay nằm ở |
|---|---|---|
| `STEP04h_Brief-Am-nhac.pdf` | brief âm nhạc, quyết định có lời | mục 1, 5 |
| `STEP04h2_Kiem-dinh-am-thanh.pdf` | kiểm định thống kê, bẫy Simpson | mục 3 |
| `STEP04h3_Cong-thuc-Tai-tao-Nhac.pdf` | công thức tái tạo theo khâu sản xuất | mục 1 |

**Vì sao gộp:** ba bản buộc người dựng nhạc mở ba file và tự khớp với nhau.
Bản hợp nhất thêm phần **lời hát** (308 bài) mà cả ba bản cũ đều không có.

**Vì sao giữ lại:** bản cũ có chi tiết ở cấp thông số mà bản hợp nhất lược bớt
cho dễ đọc (bảng 161 thông số tái tạo, đường cong năng lượng từng bản). Cần
đào sâu thì đọc `04_outlier/audio/AUDIO_RECIPE.json` — nguồn của cả hai.

Dựng lại bản cũ: `python3 pipeline/report/build_report04h{,2,3}.py <ngách>`
