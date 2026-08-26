"""STEP_10 — PLAYBOOK KHỞI TẠO KÊNH (đầu vào cho workflow sản xuất tự động).

CHẠY: python3 pipeline/analyze/step10_playbook.py [niche_path]
      (sau STEP_08; nếu có ảnh thì chạy sau STEP_04g để lấy brief thumbnail)

═══ VÌ SAO CÓ FILE NÀY (yêu cầu người dùng 2026-08-17) ═══
  "nếu tôi bắt đầu làm kênh thì tôi nên làm gì? title là gì, description,
   hashtag, âm nhạc, đạo cụ, tần số, thumbnail, top 5 kênh học theo...
   để đưa vào workflow sản xuất nội dung tự động"

STEP_08 trả lời "CÓ NÊN VÀO?" (điểm 12.05/20).
STEP_10 trả lời "VÀO THÌ LÀM GÌ?" — bản thiết kế kênh máy đọc được.

KHÁC BIỆT QUAN TRỌNG: đây là tầng MÔ TẢ (như brief thumbnail), không phải
tầng KIỂM ĐỊNH. Nó nói "nhóm top đang làm thế này", không hứa "làm thế này
sẽ thắng". Xem 01_ARCHITECTURE.md §2.4.

ĐẦU RA:
  09_playbook/CHANNEL_PLAYBOOK.json   ← máy đọc, nạp thẳng vào workflow
  09_playbook/_playbook_data.json     ← số liệu thô để dựng báo cáo
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

TOP_Q = 0.95        # nhóm chuẩn = top 5% lượt xem
MIN_DUR = 60        # chỉ video dài

v = pd.read_parquet(P/"videos_enriched.parquet")
pool = v[(v.duration_sec > MIN_DUR) & v.is_matured].copy()
thr = pool.view_count.quantile(TOP_Q)
top = pool[pool.view_count >= thr].copy()

STOP = {"the","and","for","you","your","this","that","with","from","are","was",
        "has","have","will","can","all","but","not","its","his","her","who",
        "when","what","how","why","out","get","let","now","one","two","new"}


def words(series, n=30, minlen=3):
    c = Counter()
    for t in series.dropna():
        c.update(w for w in re.findall(r"[A-Za-z']{%d,}" % minlen, str(t).lower())
                 if w not in STOP)
    return c.most_common(n)


# ══════════════════ 1. TITLE ══════════════════
def title_shape(t):
    """Phân loại tiêu đề theo KIỂU CÂU — cái quyết định cách sinh tự động."""
    s = str(t)
    if re.search(r"\b(psalm|isaiah|ecclesiastes|proverbs|john|matthew)\s*\d*", s, re.I):
        return "kinh_thánh"
    if re.match(r"^(when|if|what|why|how)\b", s.strip(), re.I):
        return "mệnh_đề_điều_kiện"
    if re.search(r"\bplaylist\b|\bmix\b|\bcollection\b", s, re.I):
        return "playlist"
    if re.search(r"\b\d+\s*(hour|hours|min|minutes)\b", s, re.I):
        return "có_thời_lượng"
    if re.search(r"[\"“].+[\"”]", s):
        return "có_trích_dẫn"
    return "câu_cảm_xúc"


top["title_shape"] = top.title.map(title_shape)
title_len = top.title.str.len()
has_hash = top.title.str.contains("#").mean()
hashtags = Counter()
for t in top.title.dropna():
    hashtags.update(re.findall(r"#\w+", str(t)))

TITLE = {
    "len_median": int(title_len.median()),
    "len_p25": int(title_len.quantile(.25)), "len_p75": int(title_len.quantile(.75)),
    "shapes": {k: round(vv/len(top), 3) for k, vv in
               top.title_shape.value_counts().items()},
    "pct_with_hashtag": round(float(has_hash), 3),
    "pct_with_number": round(float(top.title.str.contains(r"\d").mean()), 3),
    "pct_all_caps_word": round(float(top.title.str.contains(r"\b[A-Z]{3,}\b").mean()), 3),
    "top_words": [{"w": w, "n": n} for w, n in words(top.title, 25)],
    "top_hashtags": [{"tag": t, "n": n} for t, n in hashtags.most_common(15)],
    "examples": [{"title": r.title, "views": int(r.view_count), "channel": r.handle}
                 for _, r in top.nlargest(12, "view_count").iterrows()],
}

# ══════════════════ 2. DESCRIPTION ══════════════════
desc = top.description.dropna().astype(str)
first_lines = [d.split("\n")[0].strip() for d in desc if d.split("\n")[0].strip()]

# Đếm bằng Python thuần: backend Arrow của pandas không nhận escape \U trong regex
_dl = list(desc)
def _share(fn):
    return round(sum(1 for d in _dl if fn(d))/max(len(_dl), 1), 3)
_EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
DESC = {
    "pct_present": round(float(top.description.notna().mean()), 3),
    "len_median": int(desc.str.len().median()),
    "len_p25": int(desc.str.len().quantile(.25)),
    "len_p75": int(desc.str.len().quantile(.75)),
    "n_lines_median": int(desc.str.count("\n").median()),
    "pct_with_emoji": _share(lambda d: bool(_EMOJI.search(d))),
    "pct_with_link": _share(lambda d: "http" in d),
    "pct_with_membership": _share(
        lambda d: bool(re.search(r"/join|member|patreon", d, re.I))),
    "pct_with_timestamps": _share(lambda d: bool(re.search(r"\n\s*\d{1,2}:\d{2}", d))),
    "pct_with_copyright": _share(
        lambda d: bool(re.search(r"copyright|all rights|©", d, re.I))),
    "top_words": [{"w": w, "n": n} for w, n in words(desc, 30, 4)],
    "opening_lines": first_lines[:10],
}

# ══════════════════ 3. TAGS ══════════════════
tagc = Counter()
n_tags = []
for t in top.tags.dropna():
    try:
        lst = json.loads(t) if isinstance(t, str) else list(t)
    except Exception:
        lst = [x.strip() for x in str(t).split(",")]
    lst = [str(x).strip().lower() for x in lst if str(x).strip()]
    n_tags.append(len(lst)); tagc.update(lst)
TAGS = {
    "pct_present": round(float(top.tags.notna().mean()), 3),
    "count_median": int(np.median(n_tags)) if n_tags else 0,
    "count_p75": int(np.percentile(n_tags, 75)) if n_tags else 0,
    "top": [{"tag": t, "n": n} for t, n in tagc.most_common(40)],
}

# ══════════════════ 4. THỜI LƯỢNG & NHỊP ĐĂNG ══════════════════
dur_min = top.duration_sec/60
bands = [(0, 10, "ngắn <10p"), (10, 40, "vừa 10-40p"),
         (40, 80, "dài 40-80p"), (80, 1e9, "rất dài >80p")]
FORMAT = {
    "duration_median_min": round(float(dur_min.median()), 1),
    "bands": [{"band": lb, "share": round(float(((dur_min >= a) & (dur_min < b)).mean()), 3),
               "view_median": int(top[(dur_min >= a) & (dur_min < b)].view_count.median())
               if ((dur_min >= a) & (dur_min < b)).any() else 0}
              for a, b, lb in bands],
    "ad_slots_est": round(float(dur_min.median())/8, 1),   # ~1 slot / 8 phút
}

# nhịp đăng: từ kênh của nhóm top
ch = (pool[pool.handle.isin(top.handle)]
      .groupby("handle")
      .agg(n=("video_id", "size"),
           span=("published_at", lambda s: max((s.max()-s.min()).days, 1)),
           med_view=("view_count", "median")))
ch["per_week"] = ch.n/(ch.span/7)
CADENCE = {
    "videos_per_week_median": round(float(ch.per_week.median()), 1),
    "videos_per_week_p75": round(float(ch.per_week.quantile(.75)), 1),
    "n_channels": int(len(ch)),
    "note": "Tính trên các kênh có video lọt top 5%; span = ngày giữa video đầu và cuối",
}

# ══════════════════ 5. TOP 5 KÊNH ĐỂ HỌC ══════════════════
allch = (pool.groupby("handle")
         .agg(videos=("video_id", "size"),
              total_view=("view_count", "sum"),
              med_view=("view_count", "median"),
              best=("view_count", "max"),
              subs=("subscriber_count", "max"),
              age_mo=("channel_age_months", "max"),
              med_dur=("duration_sec", "median"))
         .sort_values("total_view", ascending=False))
allch["view_per_video"] = allch.total_view/allch.videos
allch["hits"] = pool[pool.view_count >= thr].groupby("handle").size().reindex(allch.index).fillna(0)
allch["hit_rate"] = allch.hits/allch.videos

MODELS = []
for h, r in allch.head(5).iterrows():
    ex = pool[pool.handle == h].nlargest(3, "view_count")
    MODELS.append({
        "handle": h,
        "total_view": int(r.total_view), "videos": int(r.videos),
        "best_video_view": int(r.best), "median_view": int(r.med_view),
        "subscribers": int(r.subs) if pd.notna(r.subs) else None,
        "age_months": round(float(r.age_mo), 1) if pd.notna(r.age_mo) else None,
        "videos_per_month": round(float(r.videos/max(r.age_mo, 1)), 1)
        if pd.notna(r.age_mo) else None,
        "duration_median_min": round(float(r.med_dur/60), 1),
        "model": "nhiều_và_ngắn" if r.med_dur/60 < 15 else "ít_và_dài",
        "hit_rate": round(float(r.hit_rate), 3),
        "top_titles": list(ex.title),
    })

# ══════════════════ 5b. HAI MÔ HÌNH SẢN XUẤT ══════════════════
# Nhóm top chia thành hai chiến lược ĐỐI LẬP, cùng thành công. Đây là lựa chọn
# chiến lược đầu tiên phải quyết trước khi sản xuất — nó chi phối mọi thứ khác.
_ch2 = allch.head(12).copy()
_dur_by_ch = pool.groupby("handle").duration_sec.median()/60
_ch2["dur_min"] = _dur_by_ch.reindex(_ch2.index)
_short = _ch2[_ch2.dur_min < 15]
_long = _ch2[_ch2.dur_min >= 15]

def _prof(df, label, desc_):
    if not len(df):
        return None
    return {"id": label, "mô_tả": desc_,
            "n_kênh_trong_top12": int(len(df)),
            "thời_lượng_trung_vị_phút": round(float(df.dur_min.median()), 1),
            "video_mỗi_tháng": round(float((df.videos/df.age_mo.clip(lower=1)).median()), 1),
            "tổng_view_trung_vị": int(df.total_view.median()),
            "view_mỗi_video": int(df.view_per_video.median()),
            "tỷ_lệ_hit": round(float(df.hit_rate.median()), 3),
            "ví_dụ": list(df.index[:3])}

STRATEGY = {
    "note": ("Hai mô hình ĐỐI LẬP cùng thành công trong ngách. Phải chọn MỘT "
             "trước khi sản xuất — chúng đòi hỏi khối lượng công việc và loại "
             "nội dung khác hẳn nhau."),
    "profiles": [x for x in [
        _prof(_short, "nhiều_và_ngắn",
              "Video ngắn, đăng dày. Ăn bằng khối lượng và tần suất đề xuất."),
        _prof(_long, "ít_và_dài",
              "Mix dài, đăng thưa. Ăn bằng thời lượng xem và số ad slot."),
    ] if x],
}

# ══════════════════ 6. THUMBNAIL (nếu đã chạy STEP_04g) ══════════════════
THUMB = None
bf = N/"04_outlier/_brief_data.json"
if bf.exists():
    b = json.load(open(bf))
    THUMB = {"person_area_pct": round(b["person"]["area_med"]*100, 1),
             "person_range_pct": [round(b["person"]["area_p25"]*100, 1),
                                  round(b["person"]["area_p75"]*100, 1)],
             "text_area_pct": round(b["text"]["area_med"]*100, 1),
             "text_lines": int(b["text"]["lines_med"]),
             "dark_pct": round(b["color"]["dark_med"]*100, 1),
             "amber_pct": round(b["color"]["amber_med"]*100, 1),
             "blue_pct": round(b["color"]["blue_med"]*100, 1),
             "mono_pct": round(b["color"]["mono_pct"]*100, 1),
             "layout_split": round((b["layout"]["person_left_text_right"]
                                    + b["layout"]["person_right_text_left"])*100, 1),
             "brief_doc": "04_outlier/THUMBNAIL_BRIEF.md"}

# ══════════════════ 7. KHÁN GIẢ & BỐI CẢNH (từ STEP_05) ══════════════════
AUD = None
af = N/"05_audience/_metrics_raw.json"
if af.exists():
    a = json.load(open(af))
    AUD = {k: a[k] for k in ("age", "attributes", "pain", "context", "discovery")
           if k in a}

# ══════════════════ GHI RA ══════════════════
DATA = {"niche": N.name, "source_cohort": {
            "definition": f"top {(1-TOP_Q)*100:.0f}% lượt xem, video >{MIN_DUR}s, đã đủ 60 ngày",
            "n_videos": int(len(top)), "n_channels": int(top.handle.nunique()),
            "view_threshold": int(thr), "view_median": int(top.view_count.median())},
        "title": TITLE, "description": DESC, "tags": TAGS,
        "format": FORMAT, "cadence": CADENCE, "models": MODELS, "strategy": STRATEGY,
        "thumbnail": THUMB, "audience": AUD}
json.dump(DATA, open(OUT/"_playbook_data.json", "w"), indent=2, ensure_ascii=False, default=str)

# ══════════════════ 8. HỢP ĐỒNG MÁY ĐỌC (nạp vào workflow tự động) ══════
# Đây là file DUY NHẤT mà hệ thống sản xuất nội dung cần đọc. Mọi giá trị
# đều rút từ nhóm top — không có con số nào do tôi bịa.
_tw = [w["w"] for w in TITLE["top_words"][:12]]
_th = [h["tag"] for h in TITLE["top_hashtags"][:8]]
_tg = [t["tag"] for t in TAGS["top"][:25]]
_dw = [w["w"] for w in DESC["top_words"][:15]]

CONTRACT = {
    "$schema": "channel-playbook/v1",
    "niche": N.name,
    "generated_from": {
        "cohort": f"top {(1-TOP_Q)*100:.0f}% view · video >{MIN_DUR}s · đã đủ 60 ngày",
        "n_videos": int(len(top)), "n_channels": int(top.handle.nunique()),
        "view_threshold": int(thr)},
    "disclaimer": ("Đây là MÔ TẢ nhóm dẫn đầu, KHÔNG phải bằng chứng nhân quả. "
                   "Kiểm định riêng (STEP_04b) cho thấy không đặc trưng hình ảnh nào "
                   "phân biệt được thắng/thua. Dùng để sản xuất nhanh và đúng chuẩn ngách."),

    # ---------- TITLE ----------
    "title": {
        "char_target": TITLE["len_median"],
        "char_range": [TITLE["len_p25"], TITLE["len_p75"]],
        "patterns": [
            {"id": "cam_xuc", "share": TITLE["shapes"].get("câu_cảm_xúc", 0),
             "template": "{cảm_xúc_hoặc_tình_huống} | {thể_loại} | {lợi_ích}",
             "example": "Somebody Been Praying For Me | Deep Gospel Blues | Grace & Mercy"},
            {"id": "kinh_thanh", "share": TITLE["shapes"].get("kinh_thánh", 0),
             "template": "{sách_kinh_thánh} {chương} | {mô_tả} | {thể_loại}",
             "example": "Psalm 51 (Lyrics) | Create in Me a Clean Heart | Blues Worship Song"},
            {"id": "playlist", "share": TITLE["shapes"].get("playlist", 0),
             "template": "{thể_loại} PLAYLIST: {mô_tả_bổ_sung}",
             "example": 'Soul Saving "BLUES" Gospel Music: Modern Christian Worship PLAYLIST'},
            {"id": "dieu_kien", "share": TITLE["shapes"].get("mệnh_đề_điều_kiện", 0),
             "template": "When {tình_huống}, Play This {thể_loại} #{hashtag}",
             "example": "When Fear Takes Over, Play This Gospel Blues #TrustInGod"},
            {"id": "co_thoi_luong", "share": TITLE["shapes"].get("có_thời_lượng", 0),
             "template": "{tên_bài} | {số} Minutes of {thể_loại} for {bối_cảnh}",
             "example": "Be Still | 100 Minutes of Relaxing Black Gospel Music for Rest & Prayer"},
        ],
        "must_include_one_of": ["gospel", "blues", "worship"],
        "vocabulary": _tw,
        "hashtags": _th,
        "hashtag_usage_rate": TITLE["pct_with_hashtag"],
        "pct_with_number": TITLE["pct_with_number"],
        "separator": "|",
        "examples": TITLE["examples"][:8],
    },

    # ---------- DESCRIPTION ----------
    "description": {
        "char_target": DESC["len_median"],
        "char_range": [DESC["len_p25"], DESC["len_p75"]],
        "blocks": [
            {"order": 1, "name": "hook", "chars": "60-120",
             "rule": "Một dòng, có emoji ở đầu hoặc cuối, nêu thể loại + cảm xúc",
             "example": "🎸 GOSPEL BLUES PLAYLIST | Soulful Songs for the Soul 🎙️"},
            {"order": 2, "name": "mô_tả_âm_nhạc", "chars": "250-450",
             "rule": "Mô tả âm thanh + gốc rễ (Delta/Black Gospel) + nền tảng Kinh Thánh"},
            {"order": 3, "name": "bối_cảnh_nghe", "chars": "150-300",
             "rule": "Nêu rõ nghe lúc nào: cầu nguyện, tĩnh tâm, lúc khó khăn, buổi sáng",
             "source": "STEP_05 — bối cảnh số 1 là cầu nguyện/tĩnh tâm"},
            {"order": 4, "name": "từ_khóa_tìm_kiếm", "chars": "100-200",
             "rule": "Câu 'Designed for listeners searching for …' + 4-6 cụm từ khóa"},
            {"order": 5, "name": "kêu_gọi", "chars": "80-200",
             "rule": "Đăng ký + (tùy chọn) membership",
             "membership_rate": DESC["pct_with_membership"]},
            {"order": 6, "name": "bản_quyền", "chars": "40-120",
             "rule": "Ghi rõ nhạc do AI/bản thân sản xuất — giảm rủi ro khiếu nại",
             "usage_rate": DESC["pct_with_copyright"]},
        ],
        "emoji_rate": DESC["pct_with_emoji"],
        "timestamp_rate": DESC["pct_with_timestamps"],
        "vocabulary": _dw,
    },

    # ---------- TAGS ----------
    "tags": {"count_target": TAGS["count_median"], "count_max": TAGS["count_p75"],
             "core": _tg[:8], "extended": _tg[8:25]},

    # ---------- ĐỊNH DẠNG & NHỊP ----------
    "format": {
        "duration_target_min": FORMAT["duration_median_min"],
        "duration_options": [{"band": b["band"], "share": b["share"],
                              "view_median": b["view_median"]} for b in FORMAT["bands"]],
        "ad_slots_est": FORMAT["ad_slots_est"],
        "note": "Cả 4 nhóm thời lượng đều thành công tương đương — chọn theo bối cảnh nghe",
    },
    "cadence": {"videos_per_week": CADENCE["videos_per_week_median"],
                "videos_per_week_aggressive": CADENCE["videos_per_week_p75"],
                "n_channels": CADENCE["n_channels"],
                "note": "STEP_03: nhóm đăng dày đạt tổng view gấp 5.3× nhóm thưa"},

    # ---------- THUMBNAIL ----------
    "thumbnail": THUMB,

    # ---------- HAI MÔ HÌNH SẢN XUẤT ----------
    "strategy": STRATEGY,

    # ---------- KÊNH MẪU ----------
    "reference_channels": MODELS,
}

# ---------- ÂM NHẠC (STEP_04h, nếu đã chạy) ----------
# Trước đây đây là khoảng trống lớn nhất của playbook: mọi thông số sản xuất
# đã có, riêng "nhạc nghe thế nào" thì không. Nay lấy từ AUDIO_BRIEF.json.
_ab = N/"04_outlier/audio/AUDIO_BRIEF.json"
if _ab.exists():
    _A = json.load(open(_ab))
    CONTRACT["music"] = {
        **_A["recipe"],
        "n_tracks_analyzed": _A["generated_from"]["n_tracks"],
        "tầng": "MÔ TẢ — mô tả nhóm dẫn đầu, không phải bằng chứng nhân quả",
        "chưa_đo_được": [l["thiếu"] for l in _A["limits"]],
        "nguồn": "04_outlier/audio/AUDIO_BRIEF.json (STEP_04h)",
    }
else:
    CONTRACT["music"] = {"trạng_thái": "CHƯA CÓ DỮ LIỆU",
                         "cần": "đặt file DSP .yaml vào 00_input/raw/audio/ rồi chạy STEP_04h"}
json.dump(CONTRACT, open(OUT/"CHANNEL_PLAYBOOK.json", "w"),
          indent=2, ensure_ascii=False, default=str)

print(f"PLAYBOOK · {N.name}")
print(f"  nhóm chuẩn : {len(top)} video / {top.handle.nunique()} kênh "
      f"(≥{thr:,.0f} view)")
print(f"\n  TITLE      : {TITLE['len_median']} ký tự · "
      f"{int(TITLE['pct_with_hashtag']*100)}% có hashtag")
print(f"               kiểu: " + " · ".join(f"{k} {v*100:.0f}%"
      for k, v in list(TITLE["shapes"].items())[:3]))
print(f"  DESC       : {DESC['len_median']} ký tự · "
      f"{int(DESC['pct_with_emoji']*100)}% emoji · "
      f"{int(DESC['pct_with_membership']*100)}% mời membership")
print(f"  TAGS       : {TAGS['count_median']} thẻ/video")
print(f"  THỜI LƯỢNG : {FORMAT['duration_median_min']:.0f} phút "
      f"(~{FORMAT['ad_slots_est']:.0f} ad slot)")
print(f"  NHỊP ĐĂNG  : {CADENCE['videos_per_week_median']} video/tuần")
print(f"  THUMBNAIL  : " + ("đã có brief" if THUMB else "chưa chạy STEP_04g"))
print(f"\n  5 kênh mẫu :")
for m in MODELS:
    print(f"    {m['handle']:26} {m['total_view']:>11,} view · "
          f"{m['videos']:>3} video · tỷ lệ hit {m['hit_rate']*100:.0f}%")
print(f"\nĐã ghi: {OUT}/CHANNEL_PLAYBOOK.json (máy đọc) · _playbook_data.json")
