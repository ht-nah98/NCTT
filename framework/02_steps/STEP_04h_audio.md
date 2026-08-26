# STEP_04h — BRIEF ÂM NHẠC

> Nhánh **tùy chọn**, chạy được bất cứ lúc nào sau STEP_01. Không ảnh hưởng điểm số.

---

## 1. BƯỚC NÀY TRẢ LỜI CÂU HỎI GÌ

| Bước | Câu hỏi |
|---|---|
| STEP_04g | Nhóm top dựng **ẢNH** thế nào? |
| **STEP_04h** | Nhóm top dựng **NHẠC** thế nào? |

Cùng một logic: **tầng MÔ TẢ**, mục tiêu là **tái tạo được**.

```
STEP_04  KIỂM ĐỊNH  "đặc điểm X có GÂY RA thành công?"   → cần nhóm đối chứng
STEP_04h  MÔ TẢ      "nhóm thắng đang làm thế nào?"        → n nhỏ vẫn trả lời được
```

⚠️ Với n=5 **không được** kiểm định nhân quả. Không có nhóm đối chứng thì mọi
kết luận kiểu "BPM chậm nên thắng" đều là mê tín (quy tắc A1).

---

## 2. ĐẦU VÀO

`<N>/00_input/raw/audio/<video_id>.yaml` — kết quả phân tích DSP bằng `librosa`.

Tên file **phải** là `video_id` để ghép với `videos_enriched.parquet`.

Sáu khối bắt buộc: `tempo` · `meter` · `groove` · `key` · `harmony` · `sections`.

---

## 3. 🔴 BẪY NHÂN ĐÔI TEMPO — SỬA TRƯỚC KHI TIN BẤT CỨ SỐ NÀO

`librosa.beat.beat_track` thường bắt nhầm **bội số 2×** của tempo thật: nó bám vào
lớp đệm (hi-hat, tremolo guitar) thay vì phách chính.

Ngách christian-blues: YAML thô báo **103–162 BPM** cho nhạc gospel **chậm**.

**Ba dấu hiệu nhận biết** (cần ≥2 để kết luận):

| Dấu hiệu | Ngưỡng | Vì sao |
|---|---|---|
| `beats_per_chord` | > 6 | Ở 4/4, 8 phách = 2 ô nhịp. 13,8 phách là vô lý |
| `onsets_per_beat` | < 1,0 | Ít nốt hơn phách = lưới phách dày hơn nhạc thật |
| giây mỗi hợp âm | < 6 | Ballad đổi hợp âm mỗi 6–11 giây |

Sau khi chia đôi: **51,7–80,8 BPM** — đúng dải slow blues / gospel ballad.

> `normalize_audio.py` tự phát hiện và ghi lại **cả `bpm_raw` lẫn lý do sửa**.
> Không bao giờ xóa số gốc (quy tắc R1).

---

## 4. CHẠY

```bash
python3 pipeline/extract/normalize_audio.py <niche>   # YAML → parquet + sửa tempo
python3 pipeline/analyze/step04h_audio.py    <niche>   # → AUDIO_BRIEF.json
python3 pipeline/report/build_report04h.py   <niche>   # → PDF
```

Đã nằm trong `run_all.sh` — tự bỏ qua nếu không có file `.yaml`.

---

## 5. ĐẦU RA

### `04_outlier/audio/AUDIO_BRIEF.json`

| Khóa | Nội dung |
|---|---|
| `recipe` | **Công thức tái tạo** — BPM, điệu thức, nhịp hòa âm, prompt tiếng Anh |
| `tempo` `key` `harmony` `groove` `structure` | Khoảng quan sát từng nhóm thông số |
| `energy_curve` | Đường cong năng lượng từng bản + phân bố dạng |
| `by_model` | So sánh nhạc của mô hình ngắn vs dài |
| `tracks` | Bảng từng bản — truy vết về `video_id` |
| `limits` | **Những gì chưa đo được** |

Khối `recipe` được STEP_10 nạp vào `CHANNEL_PLAYBOOK.json → music`.

---

## 6. VỚI n NHỎ: BÁO CÁO KHOẢNG, ĐỪNG BÁO CÁO TRUNG BÌNH

Trung bình giấu mất độ phân tán. Ví dụ thật:

- Tỷ lệ hợp âm thứ: **7,6% → 72,9%**. Trung bình ~44% gợi ý "cân bằng" — sai hoàn toàn,
  thực tế mỗi bản một kiểu.
- Đường cong năng lượng: **3 dạng khác nhau trên 5 bản** — không có khuôn chuẩn.

**Chỗ nào dữ liệu phân tán thì nói thẳng là phân tán**, đừng ép ra quy luật (T38).

---

## 7. GIỚI HẠN ĐÃ BIẾT

| Thiếu | Hệ quả | Khắc phục |
|---|---|---|
| **Nhóm đối chứng** | Không kết luận được nhân quả | Phân tích thêm ~30 bản nhóm thua (B4) |
| **Cỡ mẫu n=5** | Số là khoảng quan sát, không phải chuẩn ngành | Chạy DSP cho ≥30 bản top |
| **Nhạc cụ / giọng hát / âm sắc** | Không biết "nghe giống hay không" | Tách stem (Demucs) + phân loại nhạc cụ |
| **Lời bài hát** | Không biết hát gì | Whisper transcribe |
| **LUFS / dải động** | Không biết chuẩn âm lượng | `pyloudnorm` trên file gốc |

> Brief cho **khung xương** bản nhạc. Nó chưa cho biết bản nhạc **nghe như thế nào** —
> đó là khoảng trống lớn nhất còn lại.

---

## 8. TIÊU CHÍ XONG

- [ ] `audio_features.parquet` + `audio_sections.parquet` sinh được
- [ ] Bẫy nhân đôi tempo đã kiểm, có ghi `bpm_raw` + lý do
- [ ] `AUDIO_BRIEF.json` đủ khối `recipe`
- [ ] `CHANNEL_PLAYBOOK.json` có khối `music`
- [ ] Mọi con số truy vết được về `video_id`
- [ ] Đã ghi rõ **những gì chưa đo được**

---

## 9. LIÊN KẾT

| Tài liệu | Quan hệ |
|---|---|
| `STEP_04b_thumbnail.md` | Bước song song — cùng tầng MÔ TẢ, cùng mục tiêu tái tạo |
| `STEP_10_playbook.md` | Nhận khối `music` từ bước này |
| `00_system/01_ARCHITECTURE.md` §2.4 | Phân biệt tầng kiểm định và tầng mô tả |
