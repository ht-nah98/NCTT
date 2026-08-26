"""STEP_08 — Tổng hợp: khoảng trống, chiến lược, đề tài, kế hoạch 90 ngày."""
import pandas as pd, numpy as np, json, warnings
import sys
from pathlib import Path
warnings.filterwarnings("ignore")

N=Path(sys.argv[1] if len(sys.argv)>1 else "niches/christian-blues"); P=N/"00_input/processed"; OUT=N/"99_report"
# Tạo thư mục output nếu chưa có — ngách mới không có sẵn (T22)
OUT.mkdir(parents=True, exist_ok=True)
(N/"_state").mkdir(parents=True, exist_ok=True)
v=pd.read_parquet(P/"videos_enriched.parquet")
ch=pd.read_parquet(P/"channels_enriched.parquet")
TH=pd.read_csv(N/"06_keyword/02_theme_scores.csv")
SC=json.load(open(N/"_state/scores.json")); M=json.load(open(N/"_state/metrics.json"))
R={}
m=v[v.is_matured].copy()

def vn(x, nd=1):
    """Số kiểu VN cho văn bản mô tả — dấu phẩy thập phân (T27/mục 3 06_REPORT_STANDARDS)."""
    return f"{x:.{nd}f}".replace(".", ",")

# ---------- BẢN ĐỒ KHOẢNG TRỐNG ----------
# Giao 3 nguồn: nhu cầu (A4) × chưa ai làm (A2/A5) × ta làm được
#
# ⚠ MỖI BẰNG CHỨNG PHẢI TRUY VẾT ĐƯỢC (bài học T31).
#   Bản trước mỗi khoảng trống chỉ có MỘT câu văn xuôi, không chỉ được file nguồn
#   → người đọc không kiểm chứng nổi. Nay dùng `demand` = LIST các mục:
#     {"claim": nói gì, "src": file truy ngược, "id": comment_id/khóa cụ thể}
#   `id` cho phép mở đúng dòng trong `03_quote_bank.csv` để đọc nguyên văn.
#
# LẤY SỐ TỪ DỮ LIỆU, KHÔNG GÕ TAY — số gõ tay sẽ mục nát khi chạy ngách khác.
_A = json.load(open(N/"05_audience/_metrics_raw.json"))
_ctx = _A.get("context", {})
_pain = _A.get("pain", {})
_age = _A.get("age", {})

def _pc(d, k, default=0.0):
    """Lấy pct của một tín hiệu; thiếu thì trả 0 thay vì nổ."""
    return float(d.get(k, {}).get("pct", default))

def _n(d, k):
    return int(d.get(k, {}).get("n", 0))

# Trích câu nói thật làm bằng chứng — có comment_id để truy ngược.
_QB = N/"05_audience/03_quote_bank.csv"
_Q = pd.read_csv(_QB) if _QB.exists() else pd.DataFrame()

def _clip(t, maxlen=150):
    """Cắt ở ranh giới TỪ, thêm … để người đọc biết còn nữa —
    tránh câu đứt giữa chừng ('...weak as he was he taped')."""
    t = " ".join(str(t).split())
    if len(t) <= maxlen: return t
    cut = t[:maxlen]
    sp = cut.rfind(" ")
    return (cut[:sp] if sp > maxlen*0.6 else cut).rstrip(" ,.;:") + "…"

def _quotes(flag, k=3, maxlen=150):
    """k câu được like nhiều nhất mang tín hiệu `flag`, kèm ID truy vết."""
    if _Q.empty or flag not in _Q.columns: return []
    s = _Q[_Q[flag].astype(bool)]
    return [{"text": _clip(r.text, maxlen),
             "likes": int(r.like_count), "comment_id": str(r.comment_id),
             "video_id": str(r.video_id)}
            for _, r in s.nlargest(k, "like_count").iterrows()]

# Chủ đề old_school: lấy phán quyết THẬT từ STEP_06 thay vì gõ "lift 2.37×".
_os = TH[TH.theme == "old_school"]
_os = _os.iloc[0] if len(_os) else None

gaps=[]
gaps.append({"gap":"Old-school / vintage black gospel",
 "demand":[
   {"claim":f"Tuổi tự khai trung vị {vn(_age.get('median',0),0)} — thế hệ lớn lên cùng black gospel 1950-70",
    "src":"05_audience/_metrics_raw.json → age.median",
    "id":f"n={_age.get('n',0)} người tự khai (chỉ {vn(_age.get('n',0)/_A.get('n_analyzed',1)*100,2)}% mẫu)"},
   {"claim":f"{_n(_pain,'never_heard')} comment kiểu \"chưa từng nghe thứ gì như thế này\"",
    "src":"05_audience/03_quote_bank.csv → cột never_heard","id":"lọc never_heard==True"},
 ]+[{"claim":q["text"],"src":"03_quote_bank.csv","id":f"{q['comment_id']} · {q['likes']}♥"}
    for q in _quotes("never_heard",2)],
 "supply":f"Chỉ {vn(_os.share_pct,2)}% video khai thác (STEP_06)" if _os is not None else "Chỉ 3,96% video khai thác (STEP_06)",
 "perf":(f"lift {vn(_os.lift,2)}× — cao nhất 16 chủ đề, NHƯNG phán quyết «{_os.verdict}»: "
         f"trong từng kênh chỉ {vn(_os.within_median_lift,2)}× ({_os.n_ch_better}/{_os.n_ch_tested} kênh tốt hơn)")
        if _os is not None else "lift 2,37× — cao nhất 16 chủ đề",
 "src_perf":"06_keyword/02_theme_scores.csv → theme=old_school",
 "feasible":"AI làm được; 20 kênh đã chứng minh","score":"CAO",
 "conf":"Vừa" if _os is None or _os.verdict=="XÁC NHẬN" else "Thấp"})

gaps.append({"gap":"Nhạc CÓ LỜI cho bối cảnh cầu nguyện",
 "demand":[
   {"claim":f"{vn(_pc(_ctx,'prayer_devo'),1)}% comment nhắc cầu nguyện/tĩnh tâm — bối cảnh số 1 "
            f"({_n(_ctx,'prayer_devo')} comment)",
    "src":"05_audience/_metrics_raw.json → context.prayer_devo","id":"đếm trên 6.413 comment đã lọc nhiễu"},
   {"claim":f"Bối cảnh số 2 bỏ xa: sáng sớm {vn(_pc(_ctx,'morning'),1)}%, bệnh viện {vn(_pc(_ctx,'sick_hosp'),1)}%",
    "src":"05_audience/_metrics_raw.json → context","id":"morning / sick_hosp"},
 ]+[{"claim":q["text"],"src":"03_quote_bank.csv","id":f"{q['comment_id']} · {q['likes']}♥"}
    for q in _quotes("prayer_devo",2)],
 "supply":"1,03% video làm instrumental và thất bại (lift 0,17×)",
 "src_perf":"06_keyword/03_voice_gap.csv",
 "perf":"Ngược lại: có lời mới ăn",
 "feasible":"AI làm vocal được; Gospel là nhóm chấp nhận AI cao nhất","score":"CAO","conf":"Vừa"})

gaps.append({"gap":"Mix dài 1-3h chất lượng cao",
 "demand":[
   {"claim":f"Nghe lúc cầu nguyện ({vn(_pc(_ctx,'prayer_devo'),1)}%) và lúc bệnh tật "
            f"({vn(_pc(_ctx,'sick_hosp'),1)}%) → cần liền mạch, không ngắt quãng",
    "src":"05_audience/_metrics_raw.json → context","id":"prayer_devo + sick_hosp"},
   {"claim":f"{_n(_ctx,'sleep_night')} comment nghe lúc ngủ/đêm — cần độ dài phủ cả giấc",
    "src":"05_audience/_metrics_raw.json → context.sleep_night","id":"sleep_night"},
 ]+[{"claim":q["text"],"src":"03_quote_bank.csv","id":f"{q['comment_id']} · {q['likes']}♥"}
    for q in _quotes("sick_hosp",2)],
 "supply":"43% thị trường đã làm — ĐÔNG","perf":"~11,7 ad slot vs 1 của video ngắn (STEP_07)",
 "src_perf":"07_monetization/_metrics_raw.json → ad_slots",
 "feasible":"Rẻ, dễ nhân bản bằng AI","score":"VỪA","conf":"Cao"})

gaps.append({"gap":"Nhánh Tây Ban Nha / Bồ Đào Nha",
 "demand":[
   {"claim":"8 kênh LatAm đã tồn tại trong mẫu — có cầu, chưa bão hòa",
    "src":"03_competitor/_metrics_raw.json","id":"lọc theo ngôn ngữ kênh"},
   {"claim":"Nghiên cứu độc lập (team FMG, n=1.017 comment): tiếng Tây Ban Nha 6,0%, "
            "Bồ Đào Nha 1,2% — tổng 7,2% khán giả không dùng tiếng Anh",
    "src":"nguồn ngoài: FMG _ Nghiên cứu thị trường Mỹ.xlsx → sheet «Chân dung»",
    "id":"mẫu độc lập, 60 video / 38 kênh"},
   {"claim":"Ta đo lại trên 6.413 comment bằng bộ lọc từ chức năng: TBN 1,73%, BĐN 0,20%. "
            "Thấp hơn FMG (khác phương pháp) nhưng cùng khẳng định có nhóm này",
    "src":"05_audience/_comments_tagged.parquet","id":"đối chiếu chéo 17/08"},
 ],
 "supply":"246 video es-419 + 20 pt trên 7,193 = 3,7%",
 "perf":"Chưa đo được riêng — nhưng cầu 7,2% vs cung 3,7% là chênh gần 2×",
 "src_perf":"đối chiếu FMG (cầu) vs 00_input (cung)",
 # Nâng Thấp → Vừa: đã có bằng chứng phía CẦU từ nguồn độc lập (trước đây trống).
 # Chưa lên Cao vì hiệu quả riêng của nhánh này vẫn chưa đo được.
 "feasible":"AI dịch/hát đa ngôn ngữ được","score":"VỪA","conf":"Vừa"})

gaps.append({"gap":"Định vị 'yêu nhạc blues, cần lời sạch'",
 "demand":[
   {"claim":f"{_n(_pain,'cant_stand')} comment nêu đúng mâu thuẫn «thích nhạc, không chịu nổi lời»",
    "src":"05_audience/03_quote_bank.csv → cột cant_stand","id":"lọc cant_stand==True"},
   {"claim":f"Tín hiệu «finally» ({_n(_pain,'finally')} comment) có like trung vị "
            f"{_pain.get('finally',{}).get('med_likes','?')} — cao hơn hẳn mức nền",
    "src":"05_audience/_metrics_raw.json → pain.finally","id":"med_likes vs nền 4"},
 ]+[{"claim":q["text"],"src":"03_quote_bank.csv","id":f"{q['comment_id']} · {q['likes']}♥"}
    for q in _quotes("cant_stand",2)],
 "supply":"Chưa kênh nào dùng làm định vị chính","perf":"'finally' được like gấp 6,6×",
 "src_perf":"05_audience/04_signal_tests.csv",
 "feasible":"Chỉ là cách viết mô tả kênh","score":"CAO","conf":"Cao"})
R["gaps"]=gaps

# ---------- 24 ĐỀ TÀI ĐẦU ----------
# Kết hợp: chủ đề thắng (old_school, thanks) × bối cảnh nghe (STEP_05) × format dài
ideas=[
 ("Old School Gospel Blues for Morning Prayer","old-school + cầu nguyện buổi sáng","2h"),
 ("Thank You Lord for Bringing Me Through | Vintage Blues Worship","tạ ơn + old-school","1h"),
 ("1950s Black Gospel Blues | When You Can't Sleep","old-school + đêm khuya","3h"),
 ("Grateful Heart, Weary Body | Old Time Gospel Soul","tạ ơn + đau buồn","2h"),
 ("Vintage Delta Blues Worship | Songs My Grandmother Sang","old-school + hoài niệm","2h"),
 ("Old School Gospel for the Hospital Room","old-school + bệnh tật","3h"),
 ("Thank You for Another Morning | Classic Gospel Blues","tạ ơn + buổi sáng","1h"),
 ("Blues Worship Like Church Used to Sound","old-school + hoài niệm","2h"),
 ("When the Night Feels Long | Old Time Gospel Blues","old-school + đêm","3h"),
 ("Grateful in the Storm | Vintage Gospel Soul","tạ ơn + khó khăn","1h"),
 ("1960s Gospel Blues for Quiet Time","old-school + tĩnh tâm","2h"),
 ("Old School Gospel Blues for the Long Drive","old-school + lái xe","3h"),
 ("Thank You Lord, I'm Still Here | Classic Blues Worship","tạ ơn + sống sót","1h"),
 ("Vintage Black Gospel | Music for Grieving Hearts","old-school + tang chế","2h"),
 ("Old Time Religion, Slow Blues Style","old-school + phong cách","2h"),
 ("Counting My Blessings | Vintage Gospel Blues","tạ ơn","1h"),
 ("Gospel Blues from the Old Church Piano","old-school + nhạc cụ","2h"),
 ("Thankful for Grace | Slow Delta Blues Worship","tạ ơn + ân điển","1h"),
 ("Old School Gospel Blues While You Clean the House","old-school + việc nhà","3h"),
 ("The Blues That Praise | 1950s Gospel Revival","old-school","2h"),
 ("Thank You for Every Mercy | Vintage Soul Gospel","tạ ơn","1h"),
 ("Old Fashioned Gospel Blues for Sunday Morning","old-school + chủ nhật","2h"),
 ("Grateful After the Storm | Classic Blues Worship","tạ ơn + vượt khó","1h"),
 ("Deep Old School Gospel Blues | Hammond Organ & Guitar","old-school + nhạc cụ","3h"),
]
R["ideas"]=[{"n":i+1,"title":t,"basis":b,"len":L} for i,(t,b,L) in enumerate(ideas)]

# ---------- CHỈ SỐ THEO DÕI ----------
# Mốc dựa trên phân bố THẬT của kênh trong ngách
vpm=ch.views_per_month.dropna()
young=ch[ch.channel_age_months<12]
R["benchmarks"]={
 "p25_vpm":float(vpm.quantile(.25)),"p50_vpm":float(vpm.quantile(.50)),
 "p75_vpm":float(vpm.quantile(.75)),"p90_vpm":float(vpm.quantile(.90)),
 "young_median_vpm":float(young.views_per_month.median()),
 "young_success_threshold":100000,
 "median_upload_per_month":float((v.groupby("channel_id").size()/ch.set_index("channel_id").channel_age_months).median()),
 "median_view_per_video":float(m.view_count.median()),
 "top_quartile_view_per_video":float(m.view_count.quantile(.75))}

# ---------- KIỂM GIẢ THUYẾT BAN ĐẦU ----------
R["hypotheses"]=[
 {"h":"H1 · Ngách trẻ, cửa cho người mới còn rộng","verdict":"ĐÚNG",
  "evidence":"74% kênh <12 tháng; M3.2=61,5% kênh mới đạt ≥100k view/tháng (STEP_03)"},
 {"h":"H2 · Cầu tăng nhanh hơn cung","verdict":"ĐÚNG (sau khi sửa lỗi)",
  "evidence":"M2.4=1,305. Khảo sát sơ bộ báo 0,35 là SAI do so cửa sổ chưa chín (STEP_02)"},
 {"h":"H3 · Mix dài 1-3h là định dạng tối ưu","verdict":"ĐÚNG",
  "evidence":"Ban đầu nghi ngờ (VPD thấp), nhưng bối cảnh nghe + ~11,7 ad slot xác nhận (STEP_05, 07)"},
 {"h":"H4 · Gospel chấp nhận AI cao → lợi thế","verdict":"ĐÚNG",
  "evidence":"65% top20 là AI-first và đang thắng (STEP_03) + khảo sát Wavelength"},
 {"h":"H5 · Khán giả lớn tuổi Mỹ → RPM cao","verdict":"CHƯA XÁC MINH",
  "evidence":"Tuổi tự khai trung vị 70 nhưng chỉ 1,28% mẫu; RPM không đo được từ API"},
]
json.dump(R,open(OUT/"_synthesis.json","w"),indent=2,ensure_ascii=False,default=str)

print("=== BẢN ĐỒ KHOẢNG TRỐNG ===")
for g in gaps: print(f"  [{g['score']:4}] {g['gap']:42} tin cậy {g['conf']}")
print("\n=== MỐC CHUẨN TỪ DỮ LIỆU THẬT ===")
b=R["benchmarks"]
print(f"  view/tháng: P25={b['p25_vpm']:,.0f}  P50={b['p50_vpm']:,.0f}  P75={b['p75_vpm']:,.0f}  P90={b['p90_vpm']:,.0f}")
print(f"  kênh <12th trung vị: {b['young_median_vpm']:,.0f} view/tháng")
print(f"  nhịp đăng trung vị: {b['median_upload_per_month']:.1f} video/tháng")
print(f"  view/video: trung vị {b['median_view_per_video']:,.0f}, P75 {b['top_quartile_view_per_video']:,.0f}")
print("\n=== KIỂM GIẢ THUYẾT BAN ĐẦU ===")
for h in R["hypotheses"]: print(f"  {h['verdict']:22} {h['h']}")
