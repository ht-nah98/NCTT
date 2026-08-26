"""STEP_04f — ĐO LẠI THUMBNAIL CHO ĐÚNG (bản v2, thay thế 04c).

CHẠY: CUDA_VISIBLE_DEVICES="" python3 pipeline/analyze/step04f_thumbnail_v2.py [niche] [--workers=N]

═══ VÌ SAO PHẢI LÀM LẠI ═══
Người dùng đối chiếu báo cáo 04b với ảnh thật và chỉ ra 3 sai lầm (2026-08-17):

  1. "NGƯỜI chiếm 1/3–1/4 khung" nhưng báo cáo ghi **3.2%**
     → SAI vì YuNet chỉ khoanh KHUÔN MẶT (trán→cằm), không tính đầu/tóc/mũ/thân.
        Người xem nhìn thấy CẢ NHÂN VẬT. Sửa: YOLO11-seg phân vùng người thật.
        Kiểm 9 ảnh soi mắt: lệch trung bình **5.0 điểm %** (chấp nhận được).

  2. "CHỮ chiếm 1/5–1/6 khung" nhưng báo cáo ghi 11.4% với tương quan thật chỉ 0.233
     → SAI vì MSER đoán chữ theo hình dạng. Sửa: OCR (EasyOCR) ĐỌC chữ.

  3. Ngách hướng tới VIDEO DÀI, không phải Shorts
     → Lọc theo **duration_sec > 60**, không lọc theo khung ảnh.
        (Ảnh khung dọc ≠ video Shorts: nhóm đó có thời lượng trung vị 2.608s = 43 phút.)

Xem lessons_learned T17–T20.

ĐẦU RA: 00_input/processed/thumb_v2.parquet
"""
import pandas as pd, numpy as np, sys, os, time, warnings
from pathlib import Path
warnings.filterwarnings("ignore")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")   # CPU: tránh CUDA OOM
import cv2

args = [a for a in sys.argv[1:] if not a.startswith("--")]
N = Path(args[0] if args else "niches/christian-blues")
LIMIT = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--limit=")), None)
P = N/"00_input/processed"
THUMBS = N/"00_input/raw/thumbs"
MIN_DUR = 60          # video dài: bỏ Shorts

_Y = _O = None
def yolo():
    global _Y
    if _Y is None:
        from ultralytics import YOLO
        _Y = YOLO("yolo11n-seg.pt")
    return _Y

def ocr():
    global _O
    if _O is None:
        import easyocr
        _O = easyocr.Reader(["en", "es"], gpu=False, verbose=False)
    return _O

def measure(vid):
    f = THUMBS/f"{vid}.jpg"
    if not f.exists(): return None
    img = cv2.imread(str(f))
    if img is None: return None
    h, w = img.shape[:2]; area = h*w

    # ---------- 1. NGƯỜI (phân vùng thật, không phải hộp mặt) ----------
    r = yolo().predict(img, verbose=False, conf=0.25, classes=[0])[0]
    person_area = 0.0; n_person = 0; pcx = pcy = np.nan
    if r.masks is not None and len(r.masks.data):
        u = np.zeros((h, w), bool)
        for mk in r.masks.data.cpu().numpy():
            u |= cv2.resize(mk, (w, h)) > 0.5
        person_area = float(u.mean()); n_person = int(len(r.masks.data))
        ys, xs = np.nonzero(u)
        if len(xs): pcx, pcy = float(xs.mean()/w), float(ys.mean()/h)
        # người lớn nhất
        big = max((cv2.resize(mk, (w, h)) > 0.5).mean() for mk in r.masks.data.cpu().numpy())
        person_max = float(big)
    else:
        person_max = 0.0

    # ---------- 2. CHỮ (OCR đọc thật) ----------
    res = [(b, t, c) for b, t, c in ocr().readtext(img, detail=1) if c > 0.3]
    if len(res) < 2:      # ảnh khung dọc: chữ trong dải giữa, thử phóng 2×
        x0, x1 = int(w*0.28), int(w*0.72)
        crop = cv2.resize(img[:, x0:x1], None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        r2 = [(b, t, c) for b, t, c in ocr().readtext(crop, detail=1) if c > 0.3]
        if len(r2) > len(res):
            res = [([[p[0]/2+x0, p[1]/2] for p in b], t, c) for b, t, c in r2]
    text_area = sum(abs((b[2][0]-b[0][0])*(b[2][1]-b[0][1])) for b, _, _ in res)/area
    words = " ".join(t for _, t, _ in res)
    letters = "".join(ch for ch in words if ch.isalpha())
    caps = sum(1 for ch in letters if ch.isupper())/max(len(letters), 1)
    tcx = float(np.mean([np.mean([p[0] for p in b]) for b, _, _ in res])/w) if res else np.nan
    tcy = float(np.mean([np.mean([p[1] for p in b]) for b, _, _ in res])/h) if res else np.nan
    big_line = max((abs(b[2][1]-b[0][1])/h for b, _, _ in res), default=0.0)

    # ---------- 3. NGƯỜI vs CHỮ: bố cục trái/phải ----------
    split = np.nan
    if not np.isnan(pcx) and not np.isnan(tcx):
        split = float(abs(pcx-tcx))     # cách nhau càng xa = bố cục tách đôi

    # ---------- 4. MÀU ----------
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    H, S, V = hsv[:, :, 0].astype(int), hsv[:, :, 1].astype(int), hsv[:, :, 2].astype(int)

    return {"video_id": vid,
            "person_area": person_area, "person_max": person_max, "n_person": n_person,
            "person_cx": pcx, "person_cy": pcy,
            "text_area": text_area, "n_lines": len(res), "caps_ratio": caps,
            "text_cx": tcx, "text_cy": tcy, "big_line": big_line, "ocr_text": words[:300],
            "split_lr": split,
            "dark": float((V < 70).mean()),
            "amber": float(((H >= 10) & (H <= 35) & (S > 60) & (V > 60)).mean()),
            "mono": bool(S.mean() < 28),
            "warm": float(img[:, :, 2].mean()-img[:, :, 0].mean())}

if __name__ == "__main__":
    v = pd.read_parquet(P/"videos_enriched.parquet")
    have = {f.stem for f in THUMBS.glob("*.jpg")}
    long_form = v[v.duration_sec > MIN_DUR]
    todo = [x for x in long_form.video_id.astype(str) if x in have]
    if LIMIT: todo = todo[:LIMIT]
    print(f"Video trong ngách   : {len(v):,}")
    print(f"Bỏ Shorts (≤{MIN_DUR}s)   : {len(v)-len(long_form):,}")
    print(f"Video dài có ảnh    : {len(todo):,}")
    print(f"\nĐo NGƯỜI (YOLO-seg) + CHỮ (OCR)... ~1.2s/ảnh\n", flush=True)

    t0 = time.time(); out = []
    for i, x in enumerate(todo, 1):
        r = measure(x)
        if r: out.append(r)
        if i % 250 == 0:
            el = time.time()-t0
            print(f"  {i:,}/{len(todo):,} ({el/60:.1f}p, còn ~{el/i*(len(todo)-i)/60:.0f}p)", flush=True)

    F = pd.DataFrame(out)
    F.to_parquet(P/"thumb_v2.parquet", index=False)
    print(f"\nXong {len(F):,} ảnh trong {(time.time()-t0)/60:.1f} phút → {P/'thumb_v2.parquet'}")
    print(f"\n═══ CHUẨN HÌNH ẢNH (đo lại cho đúng) ═══")
    print(f"  NGƯỜI chiếm            : {F.person_area.median()*100:.1f}% khung  "
          f"(≈1/{1/max(F.person_area.median(),1e-9):.0f})")
    print(f"  CHỮ chiếm              : {F.text_area.median()*100:.1f}% khung  "
          f"(≈1/{1/max(F.text_area.median(),1e-9):.0f})")
    print(f"  có người               : {(F.n_person>0).mean()*100:.1f}%")
    print(f"  có chữ                 : {(F.n_lines>0).mean()*100:.1f}%")
    print(f"  chữ IN HOA toàn phần   : {(F.caps_ratio>0.9).mean()*100:.1f}%")
    print(f"  tông tối               : {F.dark.median()*100:.1f}%")
    print(f"  bảng màu hổ phách      : {(F.amber>0.25).mean()*100:.1f}%")
    print(f"  đen trắng              : {F.mono.mean()*100:.1f}%")
