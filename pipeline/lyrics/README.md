# Luồng LỜI HÁT — từ video YouTube ra thông số cách viết lời

Năm bước rời, mỗi bước ghi ra đĩa và chạy lại được từ giữa chừng. Không bước
nào phụ thuộc repo ngoài.

```
L1_select      COHORT.json        chọn & khoá danh sách video
L2_download    audio/mp3, wav16   tải audio          [mạng, hàng giờ]
L4_tracks      tracks.parquet     ranh giới bài hát  [chỉ metadata]
L3_transcribe  transcripts/*.json phiên âm           [CPU, hàng giờ]
L5_features    lyrics_*.parquet   gộp ra thông số
```

`L4` chạy trước `L3` (đặt tên theo thứ tự ra đời, không phải thứ tự chạy):
`L3` cần `tracks.parquet` để gán lời về từng bài.

## Chạy

```bash
python3 pipeline/lyrics/L1_select.py     <niche>
python3 pipeline/lyrics/L4_tracks.py     <niche>          # metadata, ~1 phút
python3 pipeline/lyrics/L2_download.py   <niche>          # nền, hàng giờ
python3 pipeline/lyrics/L3_transcribe.py <niche> --model medium --threads 16
python3 pipeline/lyrics/L5_features.py   <niche>
```

`L5` đã nối vào `run_all.sh`, tự chạy khi có transcript. Bốn bước kia gọi mạng
và tốn CPU nên **cố ý không** đưa vào — chạy tay khi cần dữ liệu mới.

## ⚠ `L2` đang tắc — xem NHÁNH A trước

`L2` chết vì **403 theo độ dài** (mục "Cạm bẫy" bên dưới): `MANIFEST.jsonl`
ghi **5/5 video thất bại**, cả luồng chỉ ra được 1 transcript. Chưa có lời
giải trong khuôn khổ hiện tại.

Nếu đã có audio **cắt sẵn theo từng bài** lấy từ nguồn khác thì dùng
**[nhánh A](README_A.md)** (`A1_ingest` → `A2_transcribe_tracks` → `A3_merge`):
đi vòng qua 403, ranh giới hạng `gold` do người cắt đặt, 100% đoạn gán đúng
track. `A3` xuất ra đúng khuôn này nên `L5` dùng chung, không sửa gì.

## Hai tầng dữ liệu — đọc trước khi dùng

| File | Nội dung | Dùng ở đâu |
|---|---|---|
| `lyrics_raw.parquet` | văn bản đầy đủ | **chỉ nội bộ**, để tính toán |
| `lyrics_features.parquet` | chỉ thông số | thứ duy nhất vào báo cáo |

Lời bài hát là tác phẩm có bản quyền. Lưu nội bộ để phân tích thì bình thường,
nhưng chép nguyên văn vào báo cáo hay brief sản xuất thì vừa rủi ro vừa **vô
dụng** — chép lời kênh khác không tái tạo được gì, chỉ đạo nhái.

Nguyên tắc y hệt phần audio: đưa nhạc sĩ **khoảng BPM và tỷ lệ stem**, không
đưa file mp3 của bản thắng. Với lời cũng vậy — đưa *mật độ chữ, tỷ lệ lặp,
ngôi kể*, không đưa nội dung.

## Thông số đo được

| Nhóm | Trường | Vì sao đáng đo |
|---|---|---|
| Mật độ | `words_per_min`, `words_per_line`, `line_len_sd` | ràng buộc trực tiếp lúc viết |
| Lặp | `repeat_ratio`, `unique_line_ratio` | nhạc worship sống bằng điệp khúc; mức lặp tái tạo được |
| Từ vựng | `vocab_size`, `ttr` | đơn giản hay cầu kỳ |
| Ngôi kể | `pct_first_sing/plur/second` | "tôi" hay "chúng ta" đổi hẳn cảm giác bài hát |

## Cạm bẫy đã trả giá

**Silero VAD loại sạch giọng hát.** Bật `vad_filter=True` thì một video có
giọng suốt 98% thời lượng trả về **0 đoạn**. Silero huấn luyện cho giọng NÓI;
giọng HÁT có cao độ kéo dài và nhạc đệm chồng lên nên bị xếp là "không phải
speech". Nguy hiểm nhất: **nó không báo lỗi** — video bị gắn nhãn "nhạc nền"
trông y hệt dữ liệu hợp lệ. Đã bỏ VAD, thay bằng `no_speech_prob` của Whisper,
đo trên nội dung đã phiên âm thật.

**403 có ngưỡng theo độ dài** (đo 2026-08-19). Video <1 phút tải được; >2 phút
403 trên cả ba format. Nghỉ 60s không đổi; video đối chứng ngoài corpus cũng
403. Cơ chế: video dài tải nhiều fragment, YouTube từ chối từ request thứ hai.
Đây là ràng buộc thật của `L2`, chưa có lời giải trong khuôn khổ hiện tại.

**`yt-dlp` cũ trả "Please sign in".** Bản 2024.08.06 hỏng hoàn toàn. Gọi qua
`python3 -m yt_dlp`, không gọi lệnh trong PATH (có thể trỏ bản cũ).

## Ranh giới bài hát

Chỉ 20,7% video có tracklist trong mô tả → không cắt lời về từng bài được.
`L4` lấy **chapter YouTube** thay thế: 14/50 video có chapter → 188 track,
ranh giới do chính chủ kênh đặt.

36 video còn lại không có chapter → để nguyên cả video làm một đơn vị,
`tier="weak"`. Với lời hát thì ranh giới lệch vài giây chỉ làm một hai dòng
rơi nhầm bài — chấp nhận được, khác hẳn phân tích BPM/hoà âm.

## Chi phí đo thật (20 nhân CPU, không GPU)

| Bước | Tốc độ | 39,7 giờ audio |
|---|---|---|
| `L3` model `small` | ×0,06 | ~2,5 giờ |
| `L3` model `medium` | ~×0,18 | ~7 giờ |

Nhanh hơn ước tính ban đầu rất nhiều nhờ `faster-whisper` + `int8` + 20 nhân.
Không cần cắt mẫu, không cần Demucs.
