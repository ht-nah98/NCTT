"""CHUẨN HÓA PHÂN TÍCH ÂM THANH — YAML thô (librosa) → parquet.

CHẠY: python3 pipeline/extract/normalize_audio.py [niche_path]
ĐỌC : <N>/00_input/raw/audio/<video_id>.yaml
GHI : <N>/00_input/processed/audio_features.parquet
       <N>/00_input/processed/audio_sections.parquet

═══════════════════════════════════════════════════════════════════
SỬA MỘT LỖI ĐO CÓ HỆ THỐNG: BẪY NHÂN ĐÔI TEMPO (octave error)
═══════════════════════════════════════════════════════════════════
`librosa.beat.beat_track` nổi tiếng bắt nhầm **bội số 2×** của tempo thật —
nó bám vào lớp đệm (hi-hat, tremolo guitar) thay vì phách chính.

YAML thô báo 103–162 BPM cho nhạc gospel/blues **chậm**. Ba bằng chứng độc
lập cho thấy con số đó gấp đôi:

  1. NHỊP HÒA ÂM — 7,3–13,8 phách mỗi hợp âm. Ở 4/4 thì 8 phách = 2 ô nhịp;
     13,8 phách là vô lý. Chia đôi → 3,6–6,9 phách ≈ 1–2 ô nhịp: chuẩn blues.
  2. GIÂY MỖI HỢP ÂM — 3,2–5,4 giây, quá nhanh cho ballad. Chia đôi →
     6,4–10,9 giây, đúng tốc độ gospel chậm.
  3. ONSET MỖI PHÁCH — cả 5 file đều < 1,0 (0,59–0,78). Ít nốt hơn phách
     nghĩa là lưới phách **dày hơn nhạc thật**.

Sau khi chia đôi: 51,7–80,8 BPM — đúng dải slow blues / gospel ballad.

QUY TẮC: chỉ chia đôi khi BPM > 100 **và** có ≥2/3 dấu hiệu trên. Ghi lại
cả `bpm_raw` lẫn `bpm` để truy vết — không bao giờ xóa số gốc (quy tắc R1).
"""
import sys, yaml, warnings
import pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import niche_root                                    # noqa: E402
warnings.filterwarnings("ignore")

N = niche_root()
SRC = N/"00_input/raw/audio"
P = N/"00_input/processed"
P.mkdir(parents=True, exist_ok=True)

if not SRC.exists() or not list(SRC.glob("*.yaml")):
    sys.exit(f"Không thấy file YAML nào trong {SRC}")


def halve_verdict(d):
    """Quyết định có chia đôi BPM không, kèm LÝ DO truy vết được.

    Trả (bpm_đúng, bpm_gốc, đã_sửa, lý_do).
    """
    bpm = float(d["tempo"]["bpm"])
    h, g = d["harmony"], d["groove"]
    bpc = h.get("harmonic_rhythm_beats_per_chord") or 0
    opb = g.get("onsets_per_beat") or 0
    sec_per_chord = bpc * 60 / bpm if bpm else 0

    signs = []
    if bpc > 6:            signs.append(f"{bpc:.1f} phách/hợp âm (>6)")
    if opb < 1.0:          signs.append(f"{opb:.2f} onset/phách (<1)")
    if sec_per_chord < 6:  signs.append(f"{sec_per_chord:.1f}s/hợp âm (<6)")

    if bpm > 100 and len(signs) >= 2:
        return bpm/2, bpm, True, " · ".join(signs)
    return bpm, bpm, False, "không có dấu hiệu nhân đôi"


rows, secs = [], []
for f in sorted(SRC.glob("*.yaml")):
    vid = f.stem
    d = yaml.safe_load(open(f))
    bpm, bpm_raw, fixed, why = halve_verdict(d)

    k, h, g, m, t = d["key"], d["harmony"], d["groove"], d["meter"], d["tempo"]
    pal = h.get("chord_palette_pct", {}) or {}
    S = d.get("sections", []) or []

    rows.append({
        "video_id": vid,
        # ── nhịp độ ──
        "bpm": round(bpm, 1), "bpm_raw": round(bpm_raw, 1),
        "bpm_halved": fixed, "bpm_reason": why,
        "n_tempo_changes": len(t.get("changes", []) or []),
        # ── nhịp phách & groove ──
        "time_signature": m.get("time_signature"),
        "meter_conf": m.get("confidence"),
        "swing_pct": g.get("swing_pct"), "pulse_feel": g.get("pulse_feel"),
        "syncopation": g.get("syncopation"),
        "subdivision": g.get("subdivision"),
        "onsets_per_sec": g.get("onsets_per_sec"),
        "onsets_per_beat": g.get("onsets_per_beat"),
        # ── điệu thức ──
        "tonic": k.get("tonic"), "mode": k.get("mode"),
        "key_conf": k.get("confidence"),
        # ── hòa âm ──
        "distinct_chords": h.get("distinct_chords"),
        "chord_changes": h.get("chord_changes"),
        "beats_per_chord": h.get("harmonic_rhythm_beats_per_chord"),
        # giây/hợp âm tính theo BPM ĐÃ SỬA — đây mới là con số nghe được
        "sec_per_chord": round((h.get("harmonic_rhythm_beats_per_chord") or 0)*60/bpm, 1)
                         if bpm else None,
        "chord_conf": h.get("chord_confidence"),
        "pct_min": pal.get("min"), "pct_maj": pal.get("maj"), "pct_dim": pal.get("dim"),
        # ── cấu trúc ──
        "n_sections": len(S),
        "duration_sec": round(max((s.get("end_sec") or 0) for s in S), 1) if S else None,
    })

    for s in S:
        secs.append({
            "video_id": vid, "index": s.get("index"),
            "start_sec": s.get("start_sec"), "end_sec": s.get("end_sec"),
            "dur_sec": round((s.get("end_sec") or 0) - (s.get("start_sec") or 0), 1),
            "energy_pct": s.get("energy_pct"),
            "key": s.get("key"), "key_conf": s.get("key_conf"),
            "bars_per_chord": s.get("bars_per_chord"),
            "n_chords": len(s.get("chords", []) or []),
            "chords": " ".join(map(str, s.get("chords", []) or [])),
        })

F = pd.DataFrame(rows)
SE = pd.DataFrame(secs)
F.to_parquet(P/"audio_features.parquet", index=False)
SE.to_parquet(P/"audio_sections.parquet", index=False)

n_fix = int(F.bpm_halved.sum())
print(f"CHUẨN HÓA ÂM THANH · {len(F)} bản nhạc · {len(SE)} đoạn")
if n_fix:
    print(f"  ⚠ Sửa bẫy nhân đôi tempo: {n_fix}/{len(F)} bản")
    for _, r in F[F.bpm_halved].iterrows():
        print(f"      {r.video_id}: {r.bpm_raw:.1f} → {r.bpm:.1f} BPM  ({r.bpm_reason})")
print(f"  → {P/'audio_features.parquet'}")
print(f"  → {P/'audio_sections.parquet'}")
