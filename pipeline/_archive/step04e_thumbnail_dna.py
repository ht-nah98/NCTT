"""STEP_04e — DNA & GU ẢNH THUMBNAIL (OCR + bảng màu + bố cục nghệ thuật).

CHẠY KHI NÀO: sau STEP_04c
CÁCH CHẠY:    CUDA_VISIBLE_DEVICES="" python3 pipeline/analyze/step04e_thumbnail_dna.py [niche] [--limit N]

VÌ SAO CÓ FILE NÀY (người dùng, 2026-08-17):
  "bạn phân tích cách để tạo ảnh, gu ảnh, và dna của ảnh"

STEP_04c/d đo HÌNH HỌC (mặt to bao nhiêu, chữ chiếm mấy %) và kết luận
"không phân biệt được thắng/thua". Nhưng hình học KHÔNG phải gu ảnh.
File này đo thứ thật sự tạo nên phong cách:

  1. CHỮ THẬT trên ảnh (OCR)     — viết gì, mấy chữ, CHỮ HOA hay thường
  2. BẢNG MÀU                     — hổ phách/vàng, đen trắng, tối
  3. BỐ CỤC NGHỆ THUẬT            — chữ trái/phải, nhân vật bên nào
  4. DẤU VẾT AI                   — lỗi chính tả, watermark, khung Shorts
  5. MÔ-TÍP                       — thánh giá, micro, guitar, mũ

⚠️ BÀI HỌC ĐÃ TRẢ GIÁ (T13, T17): cột `text_area` của STEP_04c dùng MSER,
tương quan với diện tích chữ thật chỉ **0.233** → vô dụng. Ảnh chữ to nhất
báo 0.0%. OCR đo đúng vì nó ĐỌC chữ chứ không đoán theo hình dạng.
"""
import pandas as pd, numpy as np, json, sys, os, re, warnings
from pathlib import Path
warnings.filterwarnings("ignore")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")  # ép CPU: pin_memory CUDA hay OOM
import cv2

args = [a for a in sys.argv[1:] if not a.startswith("--")]
N = Path(args[0] if args else "niches/christian-blues")
LIMIT = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--limit=")), None)
P = N/"00_input/processed"
THUMBS = N/"00_input/raw/thumbs"
OUT = N/"04_outlier"; OUT.mkdir(exist_ok=True)

# --- Mô-típ: chỉ những từ THẬT SỰ xuất hiện trên ảnh ngách này ---
MOTIF = {
    "thánh_giá": r"\bcross\b",
    "cầu_nguyện": r"\b(pray|prayer|praying|amen)\b",
    "chữa_lành": r"\b(heal|healing|healed)\b",
    "ân_điển": r"\b(grace|mercy)\b",
    "chúa_trời": r"\b(god|lord|jesus|christ|holy)\b",
    "đức_tin": r"\b(faith|believe|trust)\b",
    "linh_hồn": r"\b(soul|soulful|spirit)\b",
    "blues": r"\bblues\b",
    "gospel": r"\bgospel\b",
    "thánh_vịnh": r"\b(psalm|scripture|bible|verse)\b",
    "đêm_tối": r"\b(night|dark|storm|shadow)\b",
    "hy_vọng": r"\b(hope|light|morning|dawn|rise)\b",
    "nỗi_đau": r"\b(cry|crying|tears|broken|pain|lonely|weary)\b",
    "kiên_cường": r"\b(still|never|always|strong|stand)\b",
}

_R = None
def reader():
    global _R
    if _R is None:
        import easyocr
        _R = easyocr.Reader(["en", "es"], gpu=False, verbose=False)
    return _R

def dna(vid):
    f = THUMBS/f"{vid}.jpg"
    if not f.exists(): return None
    img = cv2.imread(str(f))
    if img is None: return None
    h, w = img.shape[:2]; area = h*w

    # ---------- 1. CHỮ THẬT (OCR) ----------
    res = [(b, t, c) for b, t, c in reader().readtext(img, detail=1) if c > 0.3]
    # Ảnh Shorts: chữ nằm trong dải giữa hẹp, OCR ở cỡ gốc hay bỏ sót.
    # Thử lại trên dải giữa phóng 2× rồi quy tọa độ về khung gốc.
    if len(res) < 2:
        x0, x1 = int(w*0.28), int(w*0.72)
        crop = cv2.resize(img[:, x0:x1], None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        r2 = [(b, t, c) for b, t, c in reader().readtext(crop, detail=1) if c > 0.3]
        if len(r2) > len(res):
            res = [([[p[0]/2+x0, p[1]/2] for p in b], t, c) for b, t, c in r2]
    ocr_area = sum(abs((b[2][0]-b[0][0])*(b[2][1]-b[0][1])) for b, _, _ in res)/area
    words = " ".join(t for _, t, _ in res)
    letters = re.sub(r"[^A-Za-z]", "", words)
    caps = sum(1 for ch in letters if ch.isupper())/max(len(letters), 1)
    n_words = len(words.split())
    # chữ nằm nửa trái hay phải
    tx = np.mean([np.mean([p[0] for p in b]) for b, _, _ in res])/w if res else np.nan
    ty = np.mean([np.mean([p[1] for p in b]) for b, _, _ in res])/h if res else np.nan
    # cỡ chữ lớn nhất so với ảnh
    big = max((abs((b[2][1]-b[0][1]))/h for b, _, _ in res), default=0)

    # ---------- 2. BẢNG MÀU ----------
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    H, S, V = hsv[:, :, 0].astype(int), hsv[:, :, 1].astype(int), hsv[:, :, 2].astype(int)
    dark = float((V < 70).mean())
    amber = float(((H >= 10) & (H <= 35) & (S > 60) & (V > 60)).mean())
    mono = bool(S.mean() < 28)
    warm = float(img[:, :, 2].mean() - img[:, :, 0].mean())
    # tương phản sáng-tối mạnh (kiểu chiaroscuro)
    chiaro = float((V < 50).mean() * (V > 200).mean() * 100)

    # ---------- 3. KHUNG SHORTS (ảnh dọc nhét vào khung ngang) ----------
    # Hiệu chuẩn trên 14 ảnh soi mắt: ảnh Shorts thật có CẢ HAI biên
    # biến thiên ≤0.25 so với vùng giữa; ảnh ngang thường có ≥1 biên cao.
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(float)
    cstd = g.std(axis=0)
    ce = max(cstd[int(w*.35):int(w*.65)].mean(), 1e-6)
    lo, ro = cstd[:int(w*.10)].mean()/ce, cstd[-int(w*.10):].mean()/ce
    pillar = bool(lo < 0.30 and ro < 0.30)

    # ---------- 4. MÔ-TÍP theo chữ ----------
    lw = words.lower()
    motifs = {k: bool(re.search(p, lw)) for k, p in MOTIF.items()}

    # ---------- 5. DẤU VẾT AI: ký tự lặp bất thường GIỮA từ ----------
    # Chỉ bắt lỗi kiểu "BLIIND" (I lặp giữa từ), KHÔNG bắt đuôi -ING/-LL
    # hợp lệ như CRYING, HEALING, STILL. Bản đầu bắt nhầm cả hai.
    typo = bool(re.search(r"\b\w*([AEIOUaeiou])\1\w*\b",
                          re.sub(r"\b(TOO|SEE|FEEL|NEED|DEEP|KEEP|FREE|SOON|GOOD|BLOOD|"
                                 r"too|see|feel|need|deep|keep|free|soon|good|blood)\b",
                                 "", words)))

    return {"video_id": vid, "ocr_text": words[:300], "ocr_area": ocr_area,
            "n_words": n_words, "caps_ratio": caps, "text_x": tx, "text_y": ty,
            "biggest_line": big, "dark": dark, "amber": amber, "mono": mono,
            "warm": warm, "chiaro": chiaro, "pillarbox": pillar,
            "ai_typo": typo, **motifs}

if __name__ == "__main__":
    v = pd.read_parquet(P/"videos_enriched.parquet")
    have = {f.stem for f in THUMBS.glob("*.jpg")}
    todo = [x for x in v.video_id.astype(str) if x in have]
    if LIMIT: todo = todo[:LIMIT]
    print(f"OCR + phân tích DNA cho {len(todo):,} ảnh (CPU, ~0.5s/ảnh)...\n", flush=True)

    import time
    t0 = time.time(); out = []
    for i, x in enumerate(todo, 1):
        r = dna(x)
        if r: out.append(r)
        if i % 250 == 0:
            el = time.time()-t0
            print(f"  {i:,}/{len(todo):,} ({el/60:.1f}p, còn ~{el/i*(len(todo)-i)/60:.0f}p)", flush=True)

    F = pd.DataFrame(out)
    F.to_parquet(P/"thumb_dna.parquet", index=False)
    print(f"\nXong {len(F):,} ảnh trong {(time.time()-t0)/60:.1f} phút")
    print(f"Đã ghi: {P/'thumb_dna.parquet'}")
    print(f"\n--- GU ẢNH CỦA NGÁCH ---")
    print(f"  chữ IN HOA toàn phần : {(F.caps_ratio>0.9).mean()*100:.1f}%")
    print(f"  số từ trung vị       : {F.n_words.median():.0f}")
    print(f"  diện tích chữ (OCR)  : {F.ocr_area.median()*100:.1f}%")
    print(f"  tông tối (V<70)      : {F.dark.median()*100:.1f}%")
    print(f"  bảng màu hổ phách    : {(F.amber>0.25).mean()*100:.1f}%")
    print(f"  đen trắng            : {F.mono.mean()*100:.1f}%")
    print(f"  khung Shorts         : {F.pillarbox.mean()*100:.1f}%")
    print(f"\n--- MÔ-TÍP (theo chữ trên ảnh) ---")
    for k in MOTIF:
        print(f"  {k:14} {F[k].mean()*100:5.1f}%")
