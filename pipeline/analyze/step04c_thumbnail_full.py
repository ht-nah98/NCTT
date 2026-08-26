"""STEP_04c — TRÍCH ĐẶC TRƯNG ẢNH CHO TOÀN BỘ NGÁCH (không chỉ mẫu đã lọc).

CHẠY KHI NÀO: khi có ảnh của TOÀN BỘ video trong 00_input/raw/thumbs/
CÁCH CHẠY:    python3 pipeline/analyze/step04c_thumbnail_full.py [niche_path] [--workers N]

KHÁC GÌ STEP_04b:
  04b = so sánh B1 vs B4 trên mẫu đã lọc (965 video)  → trả lời "ảnh thắng khác ảnh thua ở đâu"
  04c = trích đặc trưng cho TẤT CẢ video              → cho phép:
          · kiểm lớp 2/3 chống nghịch lý Simpson trên toàn thị trường
          · phân cụm phong cách ảnh theo dòng nhạc
          · đo trùng lặp hình ảnh ở quy mô ngách (rủi ro T6)

ĐẦU RA: 00_input/processed/thumb_features_full.parquet  (1 dòng / video)
        Đây là FACT layer (tầng 1) — không chấm điểm, không diễn giải.
"""
import pandas as pd, numpy as np, sys, os, time
from pathlib import Path
from multiprocessing import Pool, cpu_count
import warnings
warnings.filterwarnings("ignore")
try:
    import cv2
except ImportError:
    sys.exit("Cần: pip install opencv-python")

args = [a for a in sys.argv[1:] if not a.startswith("--")]
N = Path(args[0] if args else "niches/christian-blues")
NW = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--workers=")),
          max(1, min(cpu_count(), 8)))
P = N/"00_input/processed"
THUMBS = N/"00_input/raw/thumbs"
# Tạo thư mục output nếu chưa có — ngách mới không có sẵn (bài học T22)
P.mkdir(parents=True, exist_ok=True)
if not THUMBS.exists():
    sys.exit(f"CHƯA CÓ ẢNH tại {THUMBS}")

MODEL = Path(__file__).resolve().parents[1]/"_models/face_detection_yunet.onnx"
if not MODEL.exists():
    sys.exit(f"Thiếu model dò mặt: {MODEL}\n"
             f"Tải: https://github.com/opencv/opencv_zoo/raw/main/"
             f"models/face_detection_yunet/face_detection_yunet_2023mar.onnx")

_DET = None
def _face(w, h):
    """YuNet (mạng nơ-ron) — nạp một lần mỗi tiến trình.

    VÌ SAO KHÔNG DÙNG HAAR: Haar frontalface chỉ nhận mặt nhìn thẳng, đủ sáng.
    Thumbnail ngách này chủ yếu là mặt NGHIÊNG / NGẨNG / NHẮM MẮT / tương phản
    mạnh → Haar bỏ sót ~64% và còn đếm nhân đôi. Kiểm trên 12 ảnh đã soi mắt:
    YuNet 11/12 đúng, Haar 6/12. Xem lessons_learned T12.
    """
    global _DET
    if _DET is None:
        _DET = cv2.FaceDetectorYN.create(str(MODEL), "", (320, 320), 0.6, 0.3, 5000)
    _DET.setInputSize((w, h))
    return _DET

def analyze(vid):
    f = THUMBS/f"{vid}.jpg"
    if not f.exists():
        return None
    try:
        img = cv2.imread(str(f))
        if img is None:
            return None
        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        area = h*w

        # --- Khuôn mặt (YuNet) ---
        _, det = _face(w, h).detect(img)
        fb = [] if det is None else [(d[0], d[1], d[2], d[3]) for d in det]
        nf = len(fb)
        face_area = sum(fw*fh for _, _, fw, fh in fb)/area if nf else 0.0
        face_cx = np.mean([x+fw/2 for x, _, fw, _ in fb])/w if nf else np.nan
        face_cy = np.mean([y+fh/2 for _, y, _, fh in fb])/h if nf else np.nan
        face_max = max((fw*fh for _, _, fw, fh in fb), default=0)/area

        # --- Chữ: MSER (vùng cực trị ổn định) + lọc hình dạng ký tự ---
        # VÌ SAO KHÔNG DÙNG Canny+dilate: nó gộp cả vùng ảnh nhiều cạnh (tóc,
        # nhạc cụ, nếp áo) thành "khối chữ" → cho ra 90% diện tích ảnh là chữ,
        # vô lý. MSER bắt nét chữ đặc trưng hơn nhiều. Xem lessons_learned T13.
        mser = cv2.MSER_create(delta=5, min_area=int(area*2e-4),
                               max_area=int(area*0.05))
        regions, _ = mser.detectRegions(gray)
        boxes = []
        for r in regions:
            x, y, bw, bh = cv2.boundingRect(r.reshape(-1, 1, 2))
            ar = bw/max(bh, 1)
            if 0.1 < ar < 3.0 and bh > h*0.02 and bh < h*0.45:
                boxes.append((x, y, bw, bh))
        # gộp ký tự gần nhau thành dòng chữ
        mask = np.zeros((h, w), np.uint8)
        for x, y, bw, bh in boxes:
            mask[y:y+bh, x:x+bw] = 255
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE,
                                cv2.getStructuringElement(cv2.MORPH_RECT, (25, 5)))
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        tb = [cv2.boundingRect(c) for c in cnts]
        tb = [b for b in tb if b[2] > w*.06 and b[3] > h*.03
              and 1.2 < b[2]/max(b[3], 1) < 25 and b[2]*b[3] < area*.35]
        text_area = sum(bw*bh for _, _, bw, bh in tb)/area if tb else 0.0
        text_cy = np.mean([y+bh/2 for _, y, _, bh in tb])/h if tb else np.nan
        text_top = sum(1 for _, y, _, bh in tb if (y+bh/2)/h < 0.33)

        # --- Bố cục: trọng tâm năng lượng cạnh ---
        edges = cv2.Canny(gray, 100, 200)
        ys, xs = np.nonzero(edges)
        cx = xs.mean()/w if len(xs) else .5
        cy = ys.mean()/h if len(ys) else .5

        mh, mw = int(h*.25), int(w*.25)
        center = gray[mh:h-mh, mw:w-mw]
        center_std = float(center.std()) if center.size else 0.0

        # --- Màu (HSV) ---
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hue_hist = cv2.calcHist([hsv], [0], None, [12], [0, 180]).flatten()
        dom_hue = int(np.argmax(hue_hist))
        hue_conc = float(hue_hist.max()/max(hue_hist.sum(), 1))

        # --- pHash (DCT thật, mạnh hơn so-sánh-hàng-xóm) ---
        small = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA)
        dct = cv2.dct(np.float32(small))[:8, :8]
        med = np.median(dct[1:, 1:])          # bỏ hệ số DC khi lấy ngưỡng
        ph = "".join("1" if b > med else "0" for b in dct.flatten())

        return {"video_id": vid, "n_faces": nf, "face_area": face_area,
                "face_max": face_max, "face_cx": face_cx, "face_cy": face_cy,
                "text_area": text_area, "n_text_blocks": len(tb),
                "text_cy": text_cy, "text_top": text_top,
                "comp_cx": cx, "comp_cy": cy, "center_std": center_std,
                "dom_hue": dom_hue, "hue_conc": hue_conc,
                "phash64": ph, "aspect": w/max(h, 1), "px_w": w, "px_h": h}
    except Exception as e:
        # KHÔNG nuốt lỗi im lặng: trả về mã lỗi để đếm được ở cuối.
        # (Bản đầu `except: return None` đã che một NameError khiến TOÀN BỘ
        #  ảnh trả None mà vẫn trông như "chạy xong". Xem lessons_learned T14.)
        return {"video_id": vid, "_error": f"{type(e).__name__}: {e}"}

if __name__ == "__main__":
    v = pd.read_parquet(P/"videos_enriched.parquet")
    ids = v.video_id.astype(str).tolist()
    have = {f.stem for f in THUMBS.glob("*.jpg")}
    todo = [x for x in ids if x in have]
    print(f"Video trong dataset : {len(ids):,}")
    print(f"Có file ảnh         : {len(todo):,} ({len(todo)/max(len(ids),1)*100:.1f}%)")
    if len(todo) < 100:
        sys.exit(f"DỪNG: chỉ {len(todo)} ảnh — quá ít để phân tích toàn ngách.")
    print(f"Đang trích đặc trưng bằng {NW} tiến trình...\n")

    t0 = time.time()
    out = []
    with Pool(NW) as pool:
        for i, r in enumerate(pool.imap_unordered(analyze, todo, chunksize=32), 1):
            if r:
                out.append(r)
            if i % 1000 == 0:
                el = time.time()-t0
                print(f"  {i:,}/{len(todo):,}  ({el:.0f}s, còn ~{el/i*(len(todo)-i):.0f}s)",
                      flush=True)

    F = pd.DataFrame(out)
    if F.empty:
        sys.exit("Không đọc được ảnh nào.")

    # --- CHỐT AN TOÀN: lỗi phải hiện ra, không được im lặng ---
    if "_error" in F.columns:
        bad = F[F._error.notna()]
        if len(bad):
            print(f"\n⚠ {len(bad):,} ảnh lỗi. Kiểu lỗi hay gặp:")
            for k, n in bad._error.str.split(":").str[0].value_counts().head().items():
                print(f"    {n:>6,}  {k}")
        F = F[F._error.isna()].drop(columns=["_error"])
        if len(F) < len(todo)*0.9:
            sys.exit(f"DỪNG: chỉ {len(F):,}/{len(todo):,} ảnh xử lý được (<90%). "
                     f"Sửa lỗi trước khi dùng kết quả.")

    F.to_parquet(P/"thumb_features_full.parquet", index=False)
    print(f"\nXong {len(F):,}/{len(todo):,} ảnh trong {time.time()-t0:.0f}s")
    print(f"Lỗi đọc: {len(todo)-len(F):,}")
    print(f"Đã ghi: {P/'thumb_features_full.parquet'}")
    print(f"\nTóm tắt nhanh:")
    print(f"  có ≥1 khuôn mặt : {(F.n_faces>0).mean()*100:.1f}%")
    print(f"  có khối chữ     : {(F.n_text_blocks>0).mean()*100:.1f}%")
    print(f"  diện tích chữ TB: {F.text_area.median()*100:.1f}% ảnh")
