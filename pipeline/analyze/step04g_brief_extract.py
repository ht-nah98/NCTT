"""STEP_04g — RÚT BRIEF TÁI TẠO THUMBNAIL TỪ NHÓM ẢNH THÀNH CÔNG NHẤT.

CHẠY: CUDA_VISIBLE_DEVICES="" python3 pipeline/analyze/step04g_brief_extract.py [niche]

═══ MỤC ĐÍCH (yêu cầu người dùng 2026-08-17) ═══
  "Tôi cần biết cấu trúc của bức ảnh để tôi tái tạo lại... cho tôi brief
   để sau tôi build hệ thống tạo ảnh tự động từ brief thì có thể sản xuất
   hàng loạt cho kiểu ảnh này"

KHÁC 04b/04d: hai file kia trả lời "ảnh có phân biệt thắng/thua không?"
(câu trả lời: không). File này trả lời câu KHÁC HẲN:
  **"Ảnh của nhóm thành công nhất được dựng như thế nào?"**

Đây là mô tả CÔNG THỨC, không phải kiểm định nhân quả. Hai việc khác nhau:
  · kiểm định  → "làm thế này có thắng không?"  (không chứng minh được)
  · brief      → "nhóm thắng đang làm thế nào?" (mô tả được, chính xác)

NGUỒN: top 5% theo view, video DÀI (>60s), đã đủ tuổi ≥60 ngày.
Lý do dùng top thay vì toàn bộ: brief phải mô tả chuẩn của nhóm dẫn đầu,
không phải trung bình của cả ngách (gồm cả kênh 23 view).

ĐẦU RA: 04_outlier/_brief_data.json  (nguyên liệu dựng brief)
"""
import pandas as pd, numpy as np, json, sys, os, time, warnings, re
from pathlib import Path
warnings.filterwarnings("ignore")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
import cv2

N = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--")
         else "niches/christian-blues")
P = N/"00_input/processed"; THUMBS = N/"00_input/raw/thumbs"
OUT = N/"04_outlier"; OUT.mkdir(exist_ok=True)
TOP_Q = 0.95        # top 5%
MIN_DUR = 60        # video dài

_Y = _O = _F = None
def yolo():
    global _Y
    if _Y is None:
        from ultralytics import YOLO; _Y = YOLO("yolo11n-seg.pt")
    return _Y
def ocr():
    global _O
    if _O is None:
        import easyocr; _O = easyocr.Reader(["en", "es"], gpu=False, verbose=False)
    return _O
def face():
    global _F
    if _F is None:
        _F = cv2.FaceDetectorYN.create(
            str(Path(__file__).resolve().parents[1]/"_models/face_detection_yunet.onnx"),
            "", (320, 320), 0.6, 0.3, 5000)
    return _F

def dominant_colors(img, k=5):
    """k-means trên pixel → bảng màu chủ đạo (hex + tỷ lệ)."""
    small = cv2.resize(img, (80, 45)).reshape(-1, 3).astype(np.float32)
    crit = (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 12, 1.0)
    _, lab, cen = cv2.kmeans(small, k, None, crit, 3, cv2.KMEANS_PP_CENTERS)
    out = []
    for i, c in enumerate(cen):
        b, g, r = [int(x) for x in c]
        out.append({"hex": f"#{r:02X}{g:02X}{b:02X}", "share": float((lab == i).mean())})
    return sorted(out, key=lambda x: -x["share"])

def analyze(vid):
    f = THUMBS/f"{vid}.jpg"
    if not f.exists(): return None
    img = cv2.imread(str(f))
    if img is None: return None
    h, w = img.shape[:2]; area = h*w

    # ---- NGƯỜI (phân vùng thật) ----
    r = yolo().predict(img, verbose=False, conf=0.25, classes=[0])[0]
    person = 0.0; pcx = pcy = np.nan; nper = 0
    if r.masks is not None and len(r.masks.data):
        u = np.zeros((h, w), bool)
        for mk in r.masks.data.cpu().numpy():
            u |= cv2.resize(mk, (w, h)) > 0.5
        person = float(u.mean()); nper = int(len(r.masks.data))
        ys, xs = np.nonzero(u)
        if len(xs): pcx, pcy = float(xs.mean()/w), float(ys.mean()/h)

    # ---- MẶT (để biết cận cảnh hay toàn thân) ----
    face().setInputSize((w, h)); _, d = face().detect(img)
    fa = float(max((x[2]*x[3] for x in d), default=0)/area) if d is not None else 0.0
    nface = 0 if d is None else int(len(d))
    fcy = float(np.mean([x[1]+x[3]/2 for x in d])/h) if d is not None and len(d) else np.nan

    # ---- CHỮ (OCR) ----
    res = [(b, t, c) for b, t, c in ocr().readtext(img, detail=1) if c > 0.3]
    if len(res) < 2:
        x0, x1 = int(w*0.28), int(w*0.72)
        crop = cv2.resize(img[:, x0:x1], None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        r2 = [(b, t, c) for b, t, c in ocr().readtext(crop, detail=1) if c > 0.3]
        if len(r2) > len(res):
            res = [([[p[0]/2+x0, p[1]/2] for p in b], t, c) for b, t, c in r2]
    text_area = sum(abs((b[2][0]-b[0][0])*(b[2][1]-b[0][1])) for b, _, _ in res)/area
    words = " ".join(t for _, t, _ in res)
    lets = "".join(c for c in words if c.isalpha())
    caps = sum(1 for c in lets if c.isupper())/max(len(lets), 1)
    tcx = float(np.mean([np.mean([p[0] for p in b]) for b, _, _ in res])/w) if res else np.nan
    tcy = float(np.mean([np.mean([p[1] for p in b]) for b, _, _ in res])/h) if res else np.nan
    bigline = float(max((abs(b[2][1]-b[0][1])/h for b, _, _ in res), default=0))

    # ---- MÀU ----
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    H, S, V = hsv[:, :, 0].astype(int), hsv[:, :, 1].astype(int), hsv[:, :, 2].astype(int)

    # ---- ÁNH SÁNG: tương phản mạnh (chiaroscuro) ----
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dark_sh = float((g < 60).mean()); bright_sh = float((g > 190).mean())

    # ---- ĐỘ SÂU TRƯỜNG ẢNH (nền mờ) ----
    lap = cv2.Laplacian(g, cv2.CV_64F)
    ctr = lap[int(h*.25):int(h*.75), int(w*.25):int(w*.75)].var()
    edge = np.concatenate([lap[:int(h*.15)].ravel(), lap[int(h*.85):].ravel()]).var()
    bokeh = float(ctr/max(edge, 1))

    return {"video_id": vid,
            "person_area": person, "n_person": nper, "person_cx": pcx, "person_cy": pcy,
            "face_area": fa, "n_face": nface, "face_cy": fcy,
            "text_area": text_area, "n_lines": len(res), "caps_ratio": caps,
            "text_cx": tcx, "text_cy": tcy, "big_line": bigline, "ocr_text": words[:250],
            "dark": float((V < 70).mean()),
            "amber": float(((H >= 10) & (H <= 35) & (S > 60) & (V > 60)).mean()),
            "blue": float(((H >= 95) & (H <= 130) & (S > 60)).mean()),
            "sat": float(S.mean()), "mono": bool(S.mean() < 28),
            "warm": float(img[:, :, 2].mean()-img[:, :, 0].mean()),
            "dark_share": dark_sh, "bright_share": bright_sh, "bokeh": bokeh,
            "palette": dominant_colors(img)}

if __name__ == "__main__":
    v = pd.read_parquet(P/"videos_enriched.parquet")
    have = {f.stem for f in THUMBS.glob("*.jpg")}
    pool = v[(v.duration_sec > MIN_DUR) & v.is_matured]
    thr = pool.view_count.quantile(TOP_Q)
    top = pool[pool.view_count >= thr]
    top = top[top.video_id.astype(str).isin(have)]
    print(f"Ngưỡng top {(1-TOP_Q)*100:.0f}%: {thr:,.0f} view")
    print(f"Số ảnh phân tích  : {len(top):,} (từ {top.handle.nunique()} kênh)")
    print(f"View trung vị nhóm: {top.view_count.median():,.0f}\n", flush=True)

    t0 = time.time(); rows = []
    for i, x in enumerate(top.video_id.astype(str), 1):
        r = analyze(x)
        if r: rows.append(r)
        if i % 50 == 0:
            print(f"  {i}/{len(top)} ({(time.time()-t0)/60:.1f}p)", flush=True)

    F = pd.DataFrame(rows).merge(
        top[["video_id", "handle", "view_count", "title", "duration_sec"]]
        .assign(video_id=lambda d: d.video_id.astype(str)), on="video_id")
    F.to_parquet(OUT/"_brief_features.parquet", index=False)

    q = lambda c, p: float(F[c].quantile(p))
    B = {"n": len(F), "n_channels": int(F.handle.nunique()),
         "view_threshold": float(thr), "view_median": float(F.view_count.median()),
         "person": {"pct_has": float((F.n_person > 0).mean()),
                    "area_p25": q("person_area", .25), "area_med": q("person_area", .5),
                    "area_p75": q("person_area", .75),
                    "one_person": float((F.n_person == 1).mean()),
                    "cx_med": float(F.person_cx.median()), "cy_med": float(F.person_cy.median())},
         "face": {"pct_has": float((F.n_face > 0).mean()),
                  "area_med": q("face_area", .5), "cy_med": float(F.face_cy.median()),
                  "one_face": float((F.n_face == 1).mean())},
         "text": {"pct_has": float((F.n_lines > 0).mean()),
                  "area_p25": q("text_area", .25), "area_med": q("text_area", .5),
                  "area_p75": q("text_area", .75),
                  "lines_med": float(F.n_lines.median()),
                  "all_caps": float((F.caps_ratio > 0.9).mean()),
                  "cx_med": float(F.text_cx.median()), "cy_med": float(F.text_cy.median()),
                  "big_line_med": q("big_line", .5)},
         "color": {"dark_med": q("dark", .5), "amber_med": q("amber", .5),
                   "blue_med": q("blue", .5), "mono_pct": float(F.mono.mean()),
                   "warm_med": q("warm", .5), "sat_med": q("sat", .5),
                   "dark_share": q("dark_share", .5), "bright_share": q("bright_share", .5)},
         "depth": {"bokeh_med": q("bokeh", .5), "bokeh_pct_strong": float((F.bokeh > 2).mean())},
         "layout": {"person_left_text_right": float(((F.person_cx < 0.5) & (F.text_cx > 0.5)).mean()),
                    "person_right_text_left": float(((F.person_cx > 0.5) & (F.text_cx < 0.5)).mean()),
                    "text_top": float((F.text_cy < 0.4).mean()),
                    "text_middle": float(((F.text_cy >= 0.4) & (F.text_cy <= 0.6)).mean()),
                    "text_bottom": float((F.text_cy > 0.6).mean())}}

    # bảng màu gộp toàn nhóm
    allc = [c for p in F.palette for c in p]
    pal = {}
    for c in allc:
        # gom về lưới 32 để nhóm màu gần nhau
        r_, g_, b_ = (int(c["hex"][i:i+2], 16)//32*32 for i in (1, 3, 5))
        k = f"#{r_:02X}{g_:02X}{b_:02X}"
        pal[k] = pal.get(k, 0)+c["share"]
    B["palette_top"] = [{"hex": k, "share": v/len(F)}
                        for k, v in sorted(pal.items(), key=lambda x: -x[1])[:10]]

    # từ ngữ trên ảnh
    txt = " ".join(F.ocr_text.fillna("")).upper()
    wc = {}
    for w_ in re.findall(r"[A-Z']{3,}", txt):
        wc[w_] = wc.get(w_, 0)+1
    B["words_top"] = [{"w": k, "n": v} for k, v in sorted(wc.items(), key=lambda x: -x[1])[:30]]

    json.dump(B, open(OUT/"_brief_data.json", "w"), indent=2, ensure_ascii=False)
    print(f"\nXong {len(F)} ảnh trong {(time.time()-t0)/60:.1f} phút")
    print(f"\n═══ BRIEF (nhóm top {(1-TOP_Q)*100:.0f}%) ═══")
    print(f"NGƯỜI  {B['person']['area_med']*100:.0f}% khung "
          f"(khoảng {B['person']['area_p25']*100:.0f}–{B['person']['area_p75']*100:.0f}%) · "
          f"{B['person']['pct_has']*100:.0f}% ảnh có người · {B['person']['one_person']*100:.0f}% một người")
    print(f"CHỮ    {B['text']['area_med']*100:.0f}% khung "
          f"(khoảng {B['text']['area_p25']*100:.0f}–{B['text']['area_p75']*100:.0f}%) · "
          f"{B['text']['lines_med']:.0f} dòng · IN HOA {B['text']['all_caps']*100:.0f}%")
    print(f"MÀU    tối {B['color']['dark_med']*100:.0f}% · hổ phách {B['color']['amber_med']*100:.0f}% · "
          f"đen trắng {B['color']['mono_pct']*100:.0f}%")
    print(f"BỐ CỤC người trái/chữ phải {B['layout']['person_left_text_right']*100:.0f}% · "
          f"người phải/chữ trái {B['layout']['person_right_text_left']*100:.0f}%")
    print(f"\nĐã ghi: _brief_data.json · _brief_features.parquet")
