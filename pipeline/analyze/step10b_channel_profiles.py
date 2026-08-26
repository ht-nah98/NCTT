"""STEP_10b — HỒ SƠ CHI TIẾT 5 KÊNH HÌNH MẪU.

CHẠY: python3 pipeline/analyze/step10b_channel_profiles.py [niche_path]
      (sau step10_playbook.py)

VÌ SAO CÓ FILE NÀY (yêu cầu người dùng 2026-08-17):
  "bổ sung top 5 kênh thành công, là hình mẫu cho những kết luận và ngách
   chúng ta đánh"

STEP_10 chỉ cho bảng số (view, video, tỷ lệ hit). Bước này dựng HỒ SƠ ĐẦY ĐỦ
để sao chép được:
  · tên kênh + mô tả kênh + từ khóa kênh  ← cách họ tự định vị
  · quỹ đạo tăng trưởng theo tháng        ← họ mất bao lâu để bật lên
  · công thức tiêu đề riêng của kênh      ← khác gì chuẩn ngách
  · cấu trúc mô tả video                  ← có membership? tracklist?
  · thời lượng, nhịp đăng, độ ổn định
  · BÀI HỌC rút ra — cái gì sao chép được, cái gì không

NGUỒN: channels_enriched.parquet (mô tả kênh — chưa bước nào dùng)
       + videos_enriched.parquet

ĐẦU RA: 09_playbook/CHANNEL_PROFILES.json
"""
import json, re, sys, warnings
from collections import Counter
from pathlib import Path
import pandas as pd
import numpy as np
warnings.filterwarnings("ignore")

N = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--")
         else "niches/christian-blues")
P = N/"00_input/processed"
OUT = N/"09_playbook"; OUT.mkdir(parents=True, exist_ok=True)

MIN_DUR, TOP_Q, TOP_N = 60, 0.95, 5

v = pd.read_parquet(P/"videos_enriched.parquet")
ch = pd.read_parquet(P/"channels_enriched.parquet")
pool = v[(v.duration_sec > MIN_DUR) & v.is_matured].copy()
thr = pool.view_count.quantile(TOP_Q)

rank = (pool.groupby("handle").view_count.sum()
        .sort_values(ascending=False).head(TOP_N))

STOP = {"the","and","for","you","your","this","that","with","from","are",
        "was","has","have","will","can","all","but","not","its","music"}


def kw(texts, n=12, minlen=3):
    c = Counter()
    for t in texts:
        c.update(w for w in re.findall(r"[A-Za-z']{%d,}" % minlen, str(t).lower())
                 if w not in STOP)
    return [w for w, _ in c.most_common(n)]


def title_shape(s):
    s = str(s)
    if re.search(r"\b(psalm|isaiah|ecclesiastes|proverbs|john|matthew)\s*\d*", s, re.I):
        return "kinh_thánh"
    if re.match(r"^(when|if|what|why|how)\b", s.strip(), re.I):
        return "mệnh_đề_điều_kiện"
    if re.search(r"\bplaylist\b|\bmix\b|\bcollection\b", s, re.I):
        return "playlist"
    if re.search(r"\b\d+\s*(hour|hours|min|minutes)\b", s, re.I):
        return "có_thời_lượng"
    if re.search(r'["“].+["”]', s):
        return "có_trích_dẫn"
    return "câu_cảm_xúc"


profiles = []
for h in rank.index:
    d = pool[pool.handle == h].copy()
    dall = v[v.handle == h].copy()
    row = ch[ch.handle == h]
    row = row.iloc[0] if len(row) else None

    dm = d.duration_sec/60
    hits = d[d.view_count >= thr]

    # ---- quỹ đạo: view trung vị theo tháng đăng ----
    d["month"] = pd.to_datetime(d.published_at).dt.to_period("M").astype(str)
    traj = (d.groupby("month")
            .agg(n=("video_id", "size"), med_view=("view_count", "median"))
            .reset_index().sort_values("month"))
    # tháng đầu tiên có video vượt ngưỡng top 5%
    first_hit = hits.published_at.min() if len(hits) else None
    ch_start = dall.published_at.min()
    months_to_hit = (None if first_hit is None or pd.isna(ch_start)
                     else round((first_hit - ch_start).days/30.4, 1))

    # ---- công thức tiêu đề riêng ----
    shapes = d.title.map(title_shape).value_counts(normalize=True).round(3).to_dict()
    seps = Counter()
    for t in d.title.dropna():
        for s in ["|", "—", "-", ":", "·"]:
            if s in str(t):
                seps[s] += 1

    # ---- cấu trúc mô tả video ----
    de = d.description.dropna().astype(str)
    dl = list(de)
    share = lambda fn: round(sum(1 for x in dl if fn(x))/max(len(dl), 1), 2)

    # ---- độ ổn định: hệ số biến thiên view ----
    cv = float(d.view_count.std()/max(d.view_count.mean(), 1))

    # ---- 10 video ĐẦU TIÊN: người mới thực sự trải qua gì ----
    early = dall.sort_values("published_at").head(10)
    early_views = [int(x) for x in early.view_count]

    # ---- lịch đăng ----
    days = pd.to_datetime(dall.published_at).dt.date
    span = max((days.max()-days.min()).days, 1)

    prof = {
        "handle": h,
        "channel_name": str(row.title) if row is not None else None,
        "url": str(row.source_url) if row is not None else None,
        "subscribers": int(row.subscriber_count) if row is not None
        and pd.notna(row.subscriber_count) else None,
        "channel_created": str(row.published_at.date()) if row is not None
        and pd.notna(row.published_at) else None,
        "first_video": str(pd.to_datetime(dall.published_at).min().date()),
        "latest_video": str(pd.to_datetime(dall.published_at).max().date()),
        "country": str(row.country) if row is not None and pd.notna(row.country) else None,

        "quy_mô": {
            "tổng_view": int(d.view_count.sum()),
            "số_video": int(len(dall)),
            "video_đủ_tuổi": int(len(d)),
            "view_trung_vị": int(d.view_count.median()),
            "video_đỉnh": int(d.view_count.max()),
            "tỷ_lệ_hit": round(len(hits)/max(len(d), 1), 3),
            "hệ_số_biến_thiên": round(cv, 2),
        },

        "sản_xuất": {
            "mô_hình": "nhiều_và_ngắn" if dm.median() < 15 else "ít_và_dài",
            "thời_lượng_trung_vị_phút": round(float(dm.median()), 1),
            "thời_lượng_khoảng": [round(float(dm.quantile(.25)), 1),
                                  round(float(dm.quantile(.75)), 1)],
            "video_mỗi_tuần": round(len(dall)/(span/7), 1),
            "số_ngày_hoạt_động": int(span),
            "tháng_đến_video_đầu_tiên_vượt_ngưỡng": months_to_hit,
            "view_10_video_đầu": early_views,
            "view_trung_vị_10_video_đầu": int(np.median(early_views)) if early_views else 0,
            "khởi_đầu": ("nổ_ngay" if early_views and max(early_views[:3]) >= thr
                         else "leo_dần"),
        },

        "định_vị": {
            "mô_tả_kênh": (str(row.description)[:900] if row is not None
                           and pd.notna(row.description) else None),
            "từ_khóa_kênh": (str(row.keywords)[:400] if row is not None
                             and pd.notna(row.keywords) else None),
        },

        "công_thức_tiêu_đề": {
            "kiểu_chủ_đạo": max(shapes, key=shapes.get) if shapes else None,
            "phân_bố": shapes,
            "dấu_phân_cách": seps.most_common(1)[0][0] if seps else None,
            "độ_dài_trung_vị": int(d.title.str.len().median()),
            "ví_dụ_top": [{"title": r.title, "views": int(r.view_count)}
                          for _, r in d.nlargest(4, "view_count").iterrows()],
        },

        "cấu_trúc_mô_tả": {
            "độ_dài_trung_vị": int(de.str.len().median()) if len(de) else 0,
            "có_emoji": share(lambda x: bool(re.search(
                "[\U0001F300-\U0001FAFF☀-➿]", x))),
            "có_membership": share(lambda x: bool(re.search(
                r"/join|member|patreon", x, re.I))),
            "có_tracklist": share(lambda x: bool(re.search(r"\n\s*\d{1,2}:\d{2}", x))),
            "có_bản_quyền": share(lambda x: bool(re.search(
                r"copyright|all rights|©|ai[- ]generated", x, re.I))),
            "từ_khóa": kw(de, 10, 4),
        },

        "quỹ_đạo": traj.to_dict("records"),
    }
    profiles.append(prof)

# ══════════ BÀI HỌC — rút từ so sánh giữa các kênh ══════════
best_hit = max(profiles, key=lambda p: p["quy_mô"]["tỷ_lệ_hit"])
most_view = max(profiles, key=lambda p: p["quy_mô"]["tổng_view"])
fastest = [p for p in profiles
           if p["sản_xuất"]["tháng_đến_video_đầu_tiên_vượt_ngưỡng"] is not None]
fastest = min(fastest, key=lambda p: p["sản_xuất"]["tháng_đến_video_đầu_tiên_vượt_ngưỡng"]) \
    if fastest else None
revived = [p for p in profiles
           if p["channel_created"] and p["first_video"]
           and (pd.to_datetime(p["first_video"]) - pd.to_datetime(p["channel_created"])).days > 365]

LESSONS = {
    "tỷ_lệ_hit_cao_nhất": {"handle": best_hit["handle"],
                           "giá_trị": best_hit["quy_mô"]["tỷ_lệ_hit"],
                           "ý_nghĩa": "Tỷ lệ % video lọt top 5% ngách — chỉ số chất lượng, "
                                      "quan trọng hơn tổng view"},
    "tổng_view_lớn_nhất": {"handle": most_view["handle"],
                           "giá_trị": most_view["quy_mô"]["tổng_view"]},
    "bật_nhanh_nhất": ({"handle": fastest["handle"],
                        "tháng": fastest["sản_xuất"]["tháng_đến_video_đầu_tiên_vượt_ngưỡng"]}
                       if fastest else None),
    "kênh_cũ_hồi_sinh": [{"handle": p["handle"], "lập": p["channel_created"],
                          "video_đầu": p["first_video"]} for p in revived],
    "phân_bố_mô_hình": dict(Counter(p["sản_xuất"]["mô_hình"] for p in profiles)),
    "kiểu_khởi_đầu": dict(Counter(p["sản_xuất"]["khởi_đầu"] for p in profiles)),
    "khởi_đầu_chi_tiết": [
        {"handle": p["handle"], "kiểu": p["sản_xuất"]["khởi_đầu"],
         "view_3_video_đầu": p["sản_xuất"]["view_10_video_đầu"][:3],
         "view_trung_vị_10_đầu": p["sản_xuất"]["view_trung_vị_10_video_đầu"]}
        for p in profiles],
}

DATA = {"niche": N.name,
        "cohort": {"top_n": TOP_N, "xếp_theo": "tổng view (video dài, đã đủ tuổi)",
                   "ngưỡng_hit": int(thr)},
        "profiles": profiles, "bài_học": LESSONS}
json.dump(DATA, open(OUT/"CHANNEL_PROFILES.json", "w"),
          indent=2, ensure_ascii=False, default=str)

print(f"HỒ SƠ {TOP_N} KÊNH HÌNH MẪU · {N.name}\n")
for p in profiles:
    q, s = p["quy_mô"], p["sản_xuất"]
    print(f"── {p['channel_name'] or p['handle']}  (@{p['handle']})")
    print(f"   {q['tổng_view']:>11,} view · {q['số_video']:>3} video · "
          f"{p['subscribers'] or 0:,} sub · hit {q['tỷ_lệ_hit']*100:.0f}%")
    print(f"   {s['mô_hình']:14} · {s['thời_lượng_trung_vị_phút']:>5.0f}p · "
          f"{s['video_mỗi_tuần']:.1f} video/tuần"
          + (f" · bật sau {s['tháng_đến_video_đầu_tiên_vượt_ngưỡng']:.1f} tháng"
             if s['tháng_đến_video_đầu_tiên_vượt_ngưỡng'] is not None else ""))
    print(f"   tiêu đề: {p['công_thức_tiêu_đề']['kiểu_chủ_đạo']} · "
          f"mô tả {p['cấu_trúc_mô_tả']['độ_dài_trung_vị']} ký tự"
          f"{' · CÓ membership' if p['cấu_trúc_mô_tả']['có_membership'] > .3 else ''}"
          f"{' · CÓ tracklist' if p['cấu_trúc_mô_tả']['có_tracklist'] > .3 else ''}")
    print()

print("BÀI HỌC:")
print(f"  tỷ lệ hit cao nhất : @{LESSONS['tỷ_lệ_hit_cao_nhất']['handle']} "
      f"({LESSONS['tỷ_lệ_hit_cao_nhất']['giá_trị']*100:.0f}%)")
if LESSONS["bật_nhanh_nhất"]:
    print(f"  bật nhanh nhất     : @{LESSONS['bật_nhanh_nhất']['handle']} "
          f"({LESSONS['bật_nhanh_nhất']['tháng']} tháng)")
if LESSONS["kênh_cũ_hồi_sinh"]:
    for r in LESSONS["kênh_cũ_hồi_sinh"]:
        print(f"  kênh cũ hồi sinh   : @{r['handle']} (lập {r['lập']}, "
              f"video đầu {r['video_đầu']})")
print(f"  mô hình            : {LESSONS['phân_bố_mô_hình']}")
print(f"\nĐã ghi: {OUT}/CHANNEL_PROFILES.json")
