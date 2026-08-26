# Nhánh A — LỜI HÁT từ audio đã cắt sẵn

Ba bước, đi vòng qua bức tường 403 của `L2`. Đầu vào là thư mục track **đã
cắt theo từng bài**, không phải video YouTube.

```
A1_ingest            track_audio.parquet        quét, ffprobe, → wav16   [~3 phút]
A2_transcribe_tracks transcripts_track/*.json   phiên âm TỪNG BÀI        [~1 giờ]
A3_merge             transcripts/*.json         gộp về khuôn của L3      [giây]
L5_features          lyrics_*.parquet           (dùng lại, không sửa)
```

## Vì sao có nhánh này

`L2_download` chết vì **403 theo độ dài** (README chính, đo 2026-08-19):
video >2 phút bị YouTube từ chối từ fragment thứ hai. Thực tế trong ngách:
`MANIFEST.jsonl` ghi **5/5 video thất bại**, cả luồng chỉ ra được 1 transcript.

Nhánh A nhận audio lấy sẵn từ ngoài — và đầu vào đó **tốt hơn** thứ `L2` định
làm ra:

| | `L2` → `L3` | `A1` → `A2` |
|---|---|---|
| Đơn vị | cả video (có video 8307s) | **một bài** |
| Ranh giới | suy từ chapter, đoạn vắt qua phải đoán | **cắt sẵn trên đĩa** |
| Tên bài | text của chapter | tên bài sạch trong `_index.json` |
| Đoạn gán đúng track | một phần | **100%** |
| Trạng thái | 403, tắc | 21,3 giờ đã chạy xong |

## Chạy

```bash
python3 pipeline/lyrics/A1_ingest.py            niches/<ngách> [--share <thư-mục>]
python3 pipeline/lyrics/A2_transcribe_tracks.py niches/<ngách> --model small --threads 18
python3 pipeline/lyrics/A3_merge.py             niches/<ngách>
python3 pipeline/lyrics/L5_features.py          niches/<ngách>
```

`--share` mặc định `~/Downloads/audio-dna-share`. Thư mục nguồn phải có
`tracks/_index.json` và các thư mục `tracks/<video_id>/`.

## Cấu trúc thư mục nguồn mong đợi

```
audio-dna-share/
  tracks/
    _index.json              ← track_id, file, title, duration_s, video_id, channel_id
    <video_id>/
      01 - Tên bài.m4a
      02 - Tên bài.webm
  audio_cache/               ← CỐ Ý BỎ QUA (video chưa cắt, 2,5GB, trùng nội dung)
```

## Tham chiếu tại chỗ, không chép

File gốc **nằm nguyên ở thư mục nguồn**. Ngách chỉ giữ `wav16` (~600MB) và
sổ `track_audio.parquet` có `src_path` + `src_sha1` để truy vết.

```bash
python3 pipeline/lyrics/A1_ingest.py niches/<ngách> --verify
```

Lệnh trên báo file gốc hay `wav16` nào đã mất. Xoá thư mục nguồn thì `wav16`
vẫn dùng được — chỉ mất khả năng dựng lại từ đầu.

## Ba điều đã đo, đừng đoán lại

**`_index.json` ghi sai độ dài.** 105/307 track lệch >2s so với số đo thật
bằng `ffprobe`, cao nhất +10s (đệm của bộ mã hoá, mốc chapter làm tròn). `A1`
**luôn dùng số đo thật** — `words_per_min` của `L5` chia cho thời lượng, lệch
10s trên bài 224s là sai 4%.

**Không dùng VAD Silero.** Kế thừa nguyên T62 của `L3` (xem thêm T69): giọng HÁT ngân dài
chồng nhạc đệm bị Silero xếp là "không phải speech", một video có giọng suốt
98% thời lượng trả về **0 đoạn** — và **không báo lỗi**. Dùng `no_speech_prob`
của Whisper thay thế.

**RTF thật ≈ 0,043** (20 nhân, `small`, int8) — nhanh hơn con số 0,06 ghi ở
README chính, vì bài lẻ ngắn hơn file 2 tiếng. 21,3 giờ audio ≈ 55 phút.

## `A3` không ghi đè dữ liệu của `L3`

Hai nhánh đo cùng đại lượng theo hai cách khác nhau: `L3` suy ranh giới từ
chapter, `A2` dùng ranh giới cắt sẵn. Trộn im lặng là cách chắc chắn để sau
này không ai biết một con số đến từ đâu.

`A3` gặp `transcripts/<video>.json` do `L3` sinh ra thì **bỏ qua và báo**.
Muốn thay thì `--overwrite`. Mọi transcript của nhánh A đều mang
`source_branch: "A"` và `boundary_source: "pre_split"`.

## Phủ sóng — đọc trước khi kết luận

Thư mục nguồn **không trùng khớp** `COHORT.json`:

| | Số lượng |
|---|---|
| Video trong nguồn | 29 (6 kênh) |
| Video trong `COHORT.json` | 50 |
| Trùng nhau | 18 |
| Chỉ có trong nguồn | 11 |
| Chỉ có trong cohort | 32 |

Nghĩa là nhánh A **không phủ hết ngách**. Thống kê từ `lyrics_features.parquet`
mô tả 6 kênh này, không phải toàn bộ 50 video đã chọn ở `L1`. Khi trích số vào
báo cáo, ghi rõ cỡ mẫu — đừng viết "ngách christian-blues có repeat_ratio X".

## Hai tầng dữ liệu — giữ nguyên như `L5`

| File | Nội dung | Dùng ở đâu |
|---|---|---|
| `lyrics_raw.parquet` | văn bản đầy đủ | **chỉ nội bộ** |
| `lyrics_features.parquet` | chỉ thông số | thứ duy nhất vào báo cáo |

Lời bài hát có bản quyền. Chép nguyên văn vào báo cáo vừa rủi ro vừa **vô
dụng** — chép lời kênh khác không tái tạo được gì. Đưa *mật độ chữ, tỷ lệ lặp,
ngôi kể*, không đưa nội dung.
