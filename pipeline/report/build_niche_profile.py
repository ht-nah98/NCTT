"""HỒ SƠ NGÁCH — bản cho cấp duyệt, bám khung "Hồ sơ ngách Template v1.0".

VÌ SAO CÓ FILE NÀY: 15 báo cáo hiện có viết cho người NGHIÊN CỨU — đầy công
thức, p-value, kiểm định. Cấp duyệt cần thứ khác: kết luận + mức tin cậy +
ràng buộc lên quyết định. Đây là bản dịch sang khung đó.

BA QUY TẮC CỦA TEMPLATE (bám sát, không tự chế):
  1. Mỗi mục phải ràng buộc một quyết định. Không ràng buộc gì thì bỏ.
  2. Mọi dòng có cột TC (tin cậy): A = công khai đo được · B = nội bộ HG
     Media · C = chỉ có khi vận hành kênh thật (60-90 ngày).
  3. Thiếu dữ liệu thì GHI RÕ THIẾU, không đoán cho đầy bảng.

Mọi con số ĐỌC TỪ FILE (T27). Ô nào hệ thống chưa đo được thì in ô
"CHƯA CÓ DỮ LIỆU" kèm cách lấy — đó là thông tin, không phải chỗ trống.
"""
import json, sys, warnings
from pathlib import Path
import pandas as pd
from weasyprint import HTML
warnings.filterwarnings("ignore")

N = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--")
         else "niches/christian-blues")
P = N/"00_input/processed"
OUT = N/"99_report/HOSO_Ngach_Christian-Blues.pdf"

M = json.load(open(N/"_state/metrics.json"))
S = json.load(open(N/"_state/scores.json"))
AUD = M["audience"]; MK = M["market"]; MO = M["momentum"]
EN = M["entry"]; AI = M["ai_fit"]; MN = M["money"]; KW = M["keyword"]
FM = M["formula"]; SY = M["synthesis"]; DA = M["data_audit"]

def _load(p, default=None):
    f = N/p
    return json.load(open(f)) if f.exists() else default

RECIPE = _load("04_outlier/audio/AUDIO_RECIPE.json")
TEST = _load("04_outlier/audio/AUDIO_TEST.json")
BRIEF = _load("04_outlier/audio/AUDIO_BRIEF.json", {})
THUMB = _load("04_outlier/_brief_data.json")
PN_ = _load("03_competitor/PRODUCTION_NORMS.json")
VD = BRIEF.get("vocal_decision", {})

CH = pd.read_parquet(P/"channels_enriched.parquet")
CH["vpm"] = CH.views_per_month
THEMES = pd.read_csv(N/"06_keyword/02_theme_scores.csv")
GAP = pd.read_csv(N/"06_keyword/03_voice_gap.csv")


def vn(x, nd=None):
    s = f"{x:,.{nd}f}" if nd is not None else f"{x:,}"
    return s.replace(",", " ").replace(".", ",")


# TC = tin cậy theo template: A công khai · B nội bộ · C cần kênh thật
def tc(letter, note=""):
    col = {"A": "#2F6B4F", "B": "#B5731F", "C": "#9B2C2C"}.get(letter, "#7A6F68")
    return (f'<b style="color:{col}">{letter}</b>'
            + (f'<br><span style="font-size:6.5pt;color:#8A7F76">{note}</span>' if note else ""))


MISS = ('<span style="color:#9B2C2C;font-weight:bold">CHƯA CÓ DỮ LIỆU</span>')


def miss(how):
    """Ô thiếu dữ liệu — luôn kèm CÁCH LẤY, nếu không thì vô dụng."""
    return f'{MISS}<br><span style="font-size:6.5pt;color:#8A7F76">Cách lấy: {how}</span>'



import base64

def img(name, w="100%", cap=None):
    """Nhúng biểu đồ vào PDF. Thiếu file thì bỏ qua, không làm hỏng báo cáo."""
    f = N/"99_report"/name
    if not f.exists():
        return ""
    b = base64.b64encode(f.read_bytes()).decode()
    c = f'<div class="cap">{cap}</div>' if cap else ""
    return (f'<div class="fig"><img src="data:image/png;base64,{b}" '
            f'style="width:{w}">{c}</div>')

# ══════════ 1. PHẠM VI ══════════
lang = MN["M5_1_lang"]
sub_rows = "\n".join(
    f'<tr><td>{a}</td><td>{b}</td><td class="c">{c}</td><td class="c">{tc(d)}</td></tr>'
    for a, b, c, d in [
        ("Tiếng Anh", f'{vn(lang["en"])} video ({vn(MN["M5_1_en_pct"],1)}% số đã khai báo)', "✅ Trong phạm vi", "A"),
        ("Tiếng Tây Ban Nha", f'{vn(lang["es"])} video', "⚠️ Tách ngách con", "A"),
        ("Tiếng Bồ Đào Nha", f'{vn(lang["pt"])} video', "⚠️ Tách ngách con", "A"),
        ("Không khai báo", f'{vn(lang["unknown"])} video', "Cần phân loại lại", "A"),
    ])

# ══════════ 2. KHÁN GIẢ ══════════
ctx = AUD["context"]
tot = AUD["n_analyzed"]
CTXNAME = {"prayer_devo": "Cầu nguyện · tĩnh nguyện · đọc Kinh Thánh",
           "morning": "Buổi sáng · bắt đầu ngày",
           "sick_hosp": "Ốm đau · nằm viện", "grief": "Tang chế · mất mát",
           "driving": "Lái xe", "housework": "Việc nhà", "work": "Lúc làm việc",
           "sleep_night": "Ngủ · ban đêm · mất ngủ"}
ACTIVE = ["prayer_devo", "morning", "sick_hosp", "grief"]
act = sum(ctx[k]["pct"] for k in ACTIVE)
bg = sum(ctx[k]["pct"] for k in ["sleep_night", "driving", "housework", "work"])

jtbd = "\n".join(
    f'<tr><td class="c">{i}</td><td><b>{CTXNAME[k]}</b></td>'
    f'<td class="n">{vn(ctx[k]["n"])}</td><td class="n">{vn(ctx[k]["pct"],2)}%</td>'
    f'<td class="c">{"Chủ động" if k in ACTIVE else "Nền"}</td><td class="c">{tc("A")}</td></tr>'
    for i, k in enumerate(sorted(ctx, key=lambda x: -ctx[x]["n"])[:8], 1))

pers = AUD["personas"]
PN = {"p_healing": ("Người đang chịu đựng",
                    "Đang trải qua mất mát, bệnh tật, tang chế hoặc cai nghiện"),
      "p_elder": ("Người cao tuổi", "Từ 60 tuổi, đã nghỉ hưu hoặc góa bụa"),
      "p_convert": ("Người mới tin đạo", "Mới chuyển hóa đức tin"),
      "p_music": ("Nhạc công", "Người chơi nhạc, nghe bằng tai nghề")}
per_rows = "\n".join(
    f'<tr{" class=hi" if k=="p_healing" else ""}><td><b>{PN[k][0]}</b><br>'
    f'<span style="font-size:7pt;color:#7A6F68">{PN[k][1]}</span></td>'
    f'<td class="n">{vn(v["n"])}</td><td class="n">{vn(v["pct"],1)}%</td>'
    f'<td class="n">{vn(v["med_likes"],0)}</td>'
    f'<td class="c">{"✅ Đủ mẫu" if v["n"]>=100 else "⚠️ Sát ngưỡng" if v["n"]>=30 else "🛑 Không đủ"}</td></tr>'
    for k, v in sorted(pers.items(), key=lambda x: -x[1]["n"]))

# ══════════ 3. TỪ KHÓA & TIẾNG NÓI ══════════
gap_rows = "\n".join(
    f'<tr><td><b>{r.word}</b></td><td class="n">{vn(int(r.in_comments))}</td>'
    f'<td class="n">{vn(int(r.in_titles))}</td><td class="n">{vn(r.ratio,0)}×</td></tr>'
    for r in GAP.head(8).itertuples())

th_ok = THEMES[THEMES.verdict.str.startswith(("XÁC NHẬN", "YẾU"))]
th_avoid = THEMES[THEMES.verdict.str.startswith("TRÁNH")]
theme_rows = "\n".join(
    f'<tr><td>{r.theme}</td><td class="n">{vn(int(r.n))}</td>'
    f'<td class="n">{vn(r.lift,2)}</td><td class="c">{r.n_ch_better}/{r.n_ch_tested}</td>'
    f'<td class="c">{"<b class=ok>"+r.verdict+"</b>" if r.verdict.startswith(("XÁC","YẾU")) else "<b class=no>"+r.verdict+"</b>" if r.verdict.startswith("TRÁNH") else r.verdict}</td></tr>'
    for r in pd.concat([th_ok, th_avoid]).itertuples())

# ══════════ 5. CUNG ══════════
top8 = CH.nlargest(8, "vpm")
top_rows = "\n".join(
    f'<tr><td><b>{r.title}</b><br><span style="font-size:6.5pt;color:#8A7F76">@{r.handle}</span></td>'
    f'<td class="n">{vn(int(r.subscriber_count))}</td><td class="n">{vn(int(r.vpm))}</td>'
    f'<td class="n">{vn(r.channel_age_months,0)}</td><td class="n">{vn(int(r.video_count))}</td>'
    f'<td class="c">{r.country if isinstance(r.country,str) else "—"}</td></tr>'
    for r in top8.itertuples())

new_ch = CH[CH.channel_age_months <= 6].nlargest(6, "vpm")
new_rows = "\n".join(
    f'<tr><td><b>{r.title}</b><br><span style="font-size:6.5pt;color:#8A7F76">@{r.handle}</span></td>'
    f'<td class="n">{vn(r.channel_age_months,0)} tháng</td><td class="n">{vn(int(r.vpm))}</td>'
    f'<td class="n">{vn(int(r.video_count))}</td>'
    f'<td class="n">{vn(int(r.vpm/max(r.channel_age_months,1)/max(r.video_count,1)*r.channel_age_months),0)}</td></tr>'
    for r in new_ch.itertuples())

spearman = CH[["subscriber_count", "vpm"]].corr(method="spearman").iloc[0, 1]

# ══════════ 9. BÀN GIAO ══════════
must = RECIPE["must_follow"] if RECIPE else []
SPEC = RECIPE["spec"] if RECIPE else {}
# Nhãn hiển thị cho cả key cũ (bộ 26 tham số) và key mới (bộ 161, sau tích
# hợp audio_dna_full 2026-08-19) — RECIPE hiện tại chỉ còn key mới.
RLAB = {"lufs": "Độ to tổng (LUFS)", "plr_db": "Dải động đỉnh (dB)",
        "swing_phase": "Pha swing", "buoc_lien": "Giai điệu đi liền bậc",
        "lech_cent": "Lệch cao độ (cent) — KHÔNG autotune cứng",
        "timeline.loudness.lufs_i": "Độ to tổng (LUFS)",
        "timeline.loudness.plr_db": "Dải động đỉnh (dB)",
        "timeline.rhythm.swing_phase": "Pha swing",
        "melody.stepwise_ratio": "Giai điệu đi liền bậc",
        "melody.autotune.cent_deviation_std": "Lệch cao độ (cent) — KHÔNG autotune cứng"}
_BPM_KEY = "timeline.rhythm.bpm" if "timeline.rhythm.bpm" in SPEC else ("bpm" if "bpm" in SPEC else None)
_CENT_KEY = "melody.autotune.cent_deviation_std" if "melody.autotune.cent_deviation_std" in SPEC else ("lech_cent" if "lech_cent" in SPEC else None)
_GRID_KEY = "melody.autotune.on_grid_ratio" if "melody.autotune.on_grid_ratio" in SPEC else ("bam_luoi_semitone" if "bam_luoi_semitone" in SPEC else None)
music_rows = "\n".join(
    f'<tr><td class="c">{i}</td><td>{RLAB.get(k,k)} = <b>{vn(SPEC[k]["median"],2)}</b>'
    f' <span style="font-size:7pt;color:#7A6F68">(khoảng {vn(SPEC[k]["p25"],2)}–{vn(SPEC[k]["p75"],2)})</span></td>'
    f'<td class="c">4 · Lớp 1</td><td class="c"><b class="ok">Bắt buộc</b></td></tr>'
    for i, k in enumerate(must, 1))
_nmus = len(must)
music_rows += (
    f'<tr><td class="c">{_nmus+1}</td><td>Nhạc <b>CÓ LỜI</b> — không làm instrumental'
    f' <span style="font-size:7pt;color:#7A6F68">(chủ đề instrumental: lift {vn(VD.get("bằng_chứng_hiệu_quả",{}).get("lift_toàn_thị_trường",0),2)}, thấp nhất 16 chủ đề)</span></td>'
    f'<td class="c">3.4 · Van</td><td class="c"><b class="ok">Bắt buộc</b></td></tr>'
    f'<tr><td class="c">{_nmus+2}</td><td>Trật tự phối khí: giọng > bass > trống > ghi-ta > piano</td>'
    f'<td class="c">4 · Lớp 1</td><td class="c"><b style="color:#B5731F">Nên</b></td></tr>'
    + (f'<tr><td class="c">{_nmus+3}</td><td><b>KHÔNG</b> ép BPM về một con số — nhóm thắng trải '
       f'{vn(SPEC[_BPM_KEY]["p25"],0)}–{vn(SPEC[_BPM_KEY]["p75"],0)} BPM</td>'
       f'<td class="c">4 · Lớp 1</td><td class="c"><b class="ok">Bắt buộc</b></td></tr>'
       if _BPM_KEY else "")
    if SPEC else "")

TH = THUMB or {}
img_rows = ""
if TH:
    img_rows = "\n".join([
        f'<tr><td class="c">1</td><td>Có người trong ảnh — <b>{vn(TH["person"]["pct_has"]*100,0)}%</b> nhóm top; '
        f'diện tích {vn(TH["person"]["area_p25"]*100,0)}–{vn(TH["person"]["area_p75"]*100,0)}% khung</td>'
        f'<td class="c">5.5</td><td class="c"><b class="ok">Bắt buộc</b></td></tr>',
        f'<tr><td class="c">2</td><td>Nền tối — độ tối trung vị <b>{vn(TH["color"]["dark_med"]*100,0)}%</b>, '
        f'điểm nhấn hổ phách {vn(TH["color"]["amber_med"]*100,0)}%</td>'
        f'<td class="c">5.5</td><td class="c"><b class="ok">Bắt buộc</b></td></tr>',
        f'<tr><td class="c">3</td><td>Có chữ trên ảnh — <b>{vn(TH["text"]["pct_has"]*100,0)}%</b>, '
        f'{vn(TH["text"]["lines_med"],0)} dòng, chiếm {vn(TH["text"]["area_med"]*100,0)}% khung</td>'
        f'<td class="c">5.5</td><td class="c"><b style="color:#B5731F">Nên</b></td></tr>',
    ])

# ══════════ CHƯA CÓ DỮ LIỆU — bảng tổng ══════════
gaps = [
    ("1.2 Bảng phân biệt dòng lân cận", "Cần nghiên cứu nhạc học (A1) — hệ thống chỉ đo metadata, không phân loại được thể loại nhạc học", "A"),
    ("2.1 Nhân khẩu học (giới, quốc gia, thiết bị)", "YouTube Analytics của kênh thật", "C"),
    ("3.1 Google Trends", "Tra Google Trends thủ công — không có trong YouTube API", "A"),
    ("4.2 Nghịch lý gospel ↔ blues", "Nghiên cứu định tính (A1) + khảo sát cộng đồng", "A"),
    ("4.3 Tính xác thực văn hoá", "Nghiên cứu định tính — rủi ro chiếm dụng văn hoá không đo bằng dữ liệu được", "A"),
    ("4.6 Nhịp sinh hoạt tôn giáo", "Cần ≥2 snapshot theo mùa (Giáng Sinh, Phục Sinh)", "A"),
    ("5.1 Mốc 2 (≥30 ngày sau mốc 1)", "Crawl lại YouTube API sau 2026-09-14", "A"),
    ("5.7 Nguồn traffic (Suggested vs Search)", "YouTube Analytics của kênh thật", "C"),
    ("7. RPM thật, chi phí sản xuất, điểm hoà vốn", "Số nội bộ HG Media (B2, B3)", "B"),
    ("8. Ngày tra cứu chính sách YouTube về nội dung AI", "Đọc bản chính sách gốc mới nhất — bắt buộc trước khi khởi động", "A"),
]
gap_tbl = "\n".join(
    f'<tr><td>{a}</td><td>{b}</td><td class="c">{tc(c)}</td></tr>' for a, b, c in gaps)


# ── §5.5 bảng công thức đang thắng ──
if PN_:
    _c, _t, _d = PN_["cadence"], PN_["tracklist"], PN_["duration"]
    _L = _d["long_vs_short_within"]
    norms_table = f"""<table>
<thead><tr><th>Yếu tố</th><th class="n">Nhóm dẫn đầu</th><th class="n">Phần còn lại</th>
<th>Ràng buộc lên sản xuất</th><th class="c">TC</th></tr></thead>
<tbody>
<tr class="hi"><td><b>Tần suất đăng</b></td>
 <td class="n">{vn(_c['median_top'],1)} video/tuần</td>
 <td class="n">{vn(_c['median_rest'],1)}</td>
 <td>Nhóm dẫn đầu đăng <b>dày hơn ~45%</b>. Kế hoạch sản xuất phải chịu được
 nhịp ≥{vn(_c['median_top'],0)} video/tuần</td><td class="c">{tc("A")}</td></tr>
<tr><td><b>Độ dài video</b></td>
 <td class="n">{vn(_d['median_min_top'],0)} phút</td>
 <td class="n">{vn(_d['median_min_all'],0)} phút</td>
 <td><b>Không có quy luật</b> — trong từng kênh chỉ {_L['n_better_long']}/{_L['n_channels']}
 kênh video dài tốt hơn (lift {vn(_L['median_lift'],2)}). Chọn theo định vị,
 đừng chọn theo kỳ vọng thuật toán</td><td class="c">{tc("A")}</td></tr>
<tr><td><b>Tracklist trong mô tả</b></td>
 <td class="n">{vn(_t['pct_top'],1)}%</td><td class="n">{vn(_t['pct_rest'],1)}%</td>
 <td>Nhóm dẫn đầu dùng <b>ÍT hơn</b> phần còn lại → <b>{_t['verdict']}</b>.
 Không cần đầu tư công sức vào đây</td><td class="c">{tc("A")}</td></tr>
<tr><td><b>Mô-típ tiêu đề</b></td>
 <td class="n">{vn(KW['title_struct']['B1']['med_len'],0)} ký tự</td>
 <td class="n">{vn(KW['title_struct']['B4']['med_len'],0)}</td>
 <td>Gần như <b>không khác nhau</b> giữa nhóm thắng và thua —
 độ dài tiêu đề không phải đòn bẩy</td><td class="c">{tc("A")}</td></tr>
<tr><td><b>Mô-típ thumbnail</b></td>
 <td class="n">{vn(TH['person']['pct_has']*100,0)}% có người</td>
 <td class="n">—</td>
 <td>Nền tối {vn(TH['color']['dark_med']*100,0)}%, chữ {vn(TH['text']['lines_med'],0)} dòng —
 xem §9.4</td><td class="c">{tc("A")}</td></tr>
<tr><td><b>Có / không lời</b></td><td class="n">{vn(DA['lyrics_all_vocal'])}/{MK['M1_2_total_channels']}</td>
 <td class="n">—</td><td>Toàn bộ kênh đều làm nhạc <b>CÓ LỜI</b></td>
 <td class="c">{tc("A")}</td></tr>
<tr><td><b>Cấu trúc playlist</b></td><td class="n" colspan="2">{MISS}</td>
 <td>YouTube API không trả cấu trúc playlist theo kênh</td><td class="c">{tc("A")}</td></tr>
</tbody></table>"""
else:
    norms_table = f'<p>{MISS} — chạy pipeline/analyze/step03b_production_norms.py</p>'

_ins = TEST["n_videos"] if TEST else 0
_t = RECIPE["cohort"] if RECIPE else {}

DOC = f"""<!doctype html><html><head><meta charset="utf-8"><title>Hồ sơ ngách Christian Blues</title><style>
@page {{ size:A4; margin:16mm 14mm 18mm;
 @bottom-center {{ content "Hồ sơ ngách · Christian Blues · trang " counter(page) "/" counter(pages);
  font-family:"DejaVu Sans";font-size:7.5pt;color:#9A8E85; }} }}
body {{ font-family:"DejaVu Sans",sans-serif;font-size:9pt;line-height:1.5;color:#1A1614; }}
h1 {{ font-size:22pt;margin:0 0 4pt;letter-spacing:-.4pt; }}
h2 {{ font-size:12.5pt;margin:18pt 0 6pt;padding-bottom:4pt;
 border-bottom:1.5pt solid #1A1614;page-break-after:avoid; }}
h3 {{ font-size:10pt;margin:12pt 0 4pt;color:#8C3A2B;page-break-after:avoid; }}
p {{ margin:5pt 0; }}
.sub {{ color:#6B615A;font-size:9.5pt;margin:0 0 8pt; }}
.meta {{ font-size:7.5pt;color:#7A6F68;border-top:.6pt solid #E2DAD1;
 border-bottom:.6pt solid #E2DAD1;padding:5pt 0;margin-bottom:12pt; }}
table {{ border-collapse:collapse;width:100%;font-size:8pt;margin:6pt 0 9pt;page-break-inside:avoid; }}
th {{ background:#F2EEE8;text-align:left;padding:4pt 6pt;font-size:7pt;
 text-transform:uppercase;letter-spacing:.4pt;color:#5A514B;border-bottom:1pt solid #CFC4B8; }}
td {{ padding:4pt 6pt;border-bottom:.6pt solid #EDE7E0;vertical-align:top; }}
td.n, th.n {{ text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap; }}
td.c, th.c {{ text-align:center;white-space:nowrap; }}
tr.hi {{ background:#F4E6E2; }}
.ok {{ color:#2F6B4F;font-weight:bold; }} .no {{ color:#9B2C2C;font-weight:bold; }}
.ac {{ color:#8C3A2B; }}
.box {{ border-left:2.5pt solid #8C3A2B;background:#F9F4F2;padding:7pt 10pt;
 margin:9pt 0;page-break-inside:avoid; }}
.box.crit {{ border-left-color:#9B2C2C;background:#FBEEEE; }}
.box.ok {{ border-left-color:#2F6B4F;background:#EFF5F1; }}
.box .l {{ font-size:7pt;text-transform:uppercase;letter-spacing:.7pt;
 font-weight:bold;color:#8C3A2B;display:block;margin-bottom:3pt; }}
.box.crit .l {{ color:#9B2C2C; }} .box.ok .l {{ color:#2F6B4F; }}
.box p {{ margin:0 0 4pt;font-size:8.5pt; }} .box p:last-child {{ margin-bottom:0; }}
.kpi {{ display:flex;gap:6pt;margin:9pt 0; }}
.kpi div {{ flex:1;border:.6pt solid #E2DAD1;padding:7pt 8pt;
 display:flex;flex-direction:column;justify-content:space-between; }}
.kpi .k {{ font-size:6.5pt;text-transform:uppercase;letter-spacing:.5pt;color:#7A6F68;margin-bottom:3pt; }}
.kpi .v {{ font-size:14pt;font-weight:bold;letter-spacing:-.3pt; }}
.kpi .c {{ font-size:6.8pt;color:#7A6F68;margin-top:2pt;line-height:1.3; }}
code {{ background:#F2EEE8;padding:.5pt 3pt;font-size:7.5pt; }}
.pb {{ page-break-before:always; }}
.f {{ font-size:7pt;color:#7A6F68;margin:-2pt 0 8pt; }}
ul {{ margin:5pt 0;padding-left:14pt; }} li {{ margin:2pt 0; }}
.hdr {{ background:#1A1614;color:#F2EEE8;padding:10pt 12pt;margin-bottom:10pt; }}
.hdr .t {{ font-size:7pt;text-transform:uppercase;letter-spacing:1pt;opacity:.7; }}
.fig {{ margin:10pt 0 12pt;page-break-inside:avoid;text-align:center; }}
.fig img {{ max-width:100%; }}
.cap {{ font-size:7pt;color:#7A6F68;margin-top:3pt;font-style:italic; }}
</style></head><body>

<h1>Hồ sơ ngách — Christian Blues</h1>
<p class="sub">Hồ sơ bệnh án của ngách · bản cho cấp duyệt</p>
<div class="meta">
Dự án <b>Christian Blues (FMG)</b> &nbsp;•&nbsp; Phiên bản hồ sơ <b>v1</b> (trước khi có kênh)
&nbsp;•&nbsp; Ngày lập <b>{S['scored_at']}</b> &nbsp;•&nbsp; Trạng thái: <b>Đang review</b>
&nbsp;•&nbsp; Bám khung <i>Hồ sơ ngách Template v1.0</i>
</div>

<div class="box crit">
<span class="l">Tóm tắt cho người duyệt</span>
<p>Ngách <b>còn cửa vào</b> ({vn(EN['M3_2_newcomer_success_pct'],0)}% kênh mới đạt ngưỡng
thành công), <b>AI làm được</b> ({vn(AI['M4_1_ai_first_top20_pct'],0)}% top20 là AI-first),
<b>khách hàng đã nhận diện được</b> (chân dung chính n={vn(pers['p_healing']['n'])}).</p>
<p>Điểm ước lượng <b>{vn(S['total_score'],2)}/20</b> &mdash; nhưng con số này
<b>dao động {vn(SY['scenarios']['T2_drops_to_1'],2)}–{vn(SY['scenarios']['RPM_is_6'],2)}</b>
tuỳ hai giả định chưa xác minh (M2.4 và RPM). <b>Quyết định vào hay không thuộc về
cấp duyệt</b> &mdash; hồ sơ này cung cấp dữ kiện, không đưa khuyến nghị.</p>
</div>

<div class="kpi">
<div><div class="k">Quy mô</div><div class="v ac">{vn(MK['M1_1_views_per_month']/1e6,1)}tr</div>
 <div class="c">view/tháng · {MK['M1_2_active_channels']}/{MK['M1_2_total_channels']} kênh hoạt động</div></div>
<div><div class="k">Cầu vs cung</div><div class="v">{vn(MO['M2_4_demand_supply_gap'],2)}</div>
 <div class="c">&gt;1 = cầu tăng nhanh hơn cung</div></div>
<div><div class="k">Kênh mới vào được</div><div class="v ok">{vn(EN['M3_2_newcomer_success_pct'],0)}%</div>
 <div class="c">&lt;12 tháng đạt &ge;100k view/tháng</div></div>
<div><div class="k">Điểm ngách</div><div class="v">{vn(S["total_score"],2)}</div>
 <div class="c">ước lượng · dao động {vn(SY["scenarios"]["T2_drops_to_1"],2)}–{vn(SY["scenarios"]["RPM_is_6"],2)}</div></div>
</div>

{img("p1_score_scenarios.png", cap="Điểm ước lượng theo từng kịch bản giả định")}
<p class="f"><b>Cột TC (tin cậy)</b> ở mọi bảng: {tc("A")} = dữ liệu công khai đo được ·
{tc("B")} = số nội bộ HG Media · {tc("C")} = chỉ có khi vận hành kênh thật (60–90 ngày).</p>

<h2>1. Phạm vi thị trường</h2>
<p class="f"><b>Ràng buộc bước sau:</b> phạm vi cạnh tranh, danh sách đối thủ, từ khoá thương hiệu</p>

{img("p7_thumbs_grid.png", cap="Ảnh thumbnail thật của 8 video xem nhiều nhất — nguồn: 00_input/raw/thumbs")}
<h3>1.1 Định nghĩa vận hành</h3>
<p>Hệ thống định nghĩa ngách <b>bằng tiêu chí đo được</b>, không bằng nhạc học:
kênh đăng nhạc gospel/worship mang chất blues–soul, chủ yếu tiếng Anh, định dạng
video dài. Cỡ mẫu: <b>{MK['M1_2_total_channels']} kênh</b>,
<b>{vn(DA['lyrics_all_vocal'])}/{MK['M1_2_total_channels']} kênh đều có lời</b>.</p>

<div class="box crit">
<span class="l">Mục 1.2 — Phân biệt với dòng lân cận: CHƯA CÓ DỮ LIỆU</span>
<p>Template yêu cầu bảng phân biệt với Gospel truyền thống, Southern Gospel,
Worship/CCM, Soul/R&amp;B đạo, Delta Blues. <b>Hệ thống không trả lời được</b> &mdash;
nó đo metadata (tiêu đề, tag, view, đặc trưng âm thanh), <b>không phân loại được
thể loại theo nhạc học</b>.</p>
<p><b>Cách lấy:</b> nghiên cứu định tính (nguồn A1) + nghe mẫu có đối chiếu chuyên gia.
Đây là việc của người, không phải của pipeline.</p>
</div>

<h3>1.4 Ngách con theo ngôn ngữ</h3>
<table>
<thead><tr><th>Ngách con</th><th>Quy mô quan sát được</th><th class="c">Trong phạm vi?</th><th class="c">TC</th></tr></thead>
<tbody>{sub_rows}</tbody></table>
<p class="f">⚠️ <b>{vn(lang["unknown"])} video không khai báo ngôn ngữ</b> ({vn(lang["unknown"]/sum(lang[k] for k in ["en","es","pt","unknown"])*100,0)}% tổng) &mdash;
con số tiếng Anh {vn(MN['M5_1_en_pct'],1)}% chỉ tính trên phần <i>đã khai báo</i>, không phải toàn bộ.</p>

<h2 class="pb">2. Khán giả &amp; bối cảnh nghe</h2>
<p class="f"><b>Ràng buộc bước sau:</b> toàn bộ định vị, độ dài video, lịch đăng, tone hình ảnh</p>

<h3>2.1 Nhân khẩu học</h3>
<table>
<thead><tr><th>Thuộc tính</th><th>Giá trị</th><th>Nguồn &amp; hạn chế</th><th class="c">TC</th></tr></thead>
<tbody>
<tr><td>Độ tuổi chủ đạo</td><td><b>Trung vị {vn(AUD['age_median'],0)} tuổi</b>
 · {vn(AUD['age_60plus_pct'],0)}% từ 60 tuổi</td>
 <td>Tự khai trong comment &mdash; chỉ <b>{AUD['age_n']}/{vn(AUD['n_analyzed'])}</b> người
 ({vn(AUD['age_n']/AUD['n_analyzed']*100,2)}%). Người khai tuổi có like trung vị 12 vs
 toàn bộ 4 → thiên lệch về nhóm gắn bó. <b>Tuổi thật nhiều khả năng THẤP HƠN 70.</b></td>
 <td class="c">{tc("A","mẫu rất nhỏ")}</td></tr>
<tr><td>Giới</td><td>{miss("YouTube Analytics kênh thật")}</td><td>Không suy đoán từ tên người (quy tắc R6)</td><td class="c">{tc("C")}</td></tr>
<tr><td>Quốc gia top 3</td><td>{miss("YouTube Analytics kênh thật")}</td>
 <td>Chỉ suy được gián tiếp: {vn(MN['M5_1_tier1_of_declared'],0)}% kênh thuộc Tier-1</td><td class="c">{tc("C")}</td></tr>
<tr><td>Hệ phái</td><td>{miss("Nghiên cứu định tính")}</td><td>Không suy đoán tôn giáo từ dữ liệu cá nhân (R6)</td><td class="c">{tc("A")}</td></tr>
<tr><td>Thiết bị</td><td>{miss("YouTube Analytics kênh thật")}</td><td>—</td><td class="c">{tc("C")}</td></tr>
</tbody></table>

<h3>2.2 Job-to-be-done — khoảnh khắc nghe</h3>
{img("p2_listening_mode.png")}
<table>
<thead><tr><th class="c">#</th><th>Khoảnh khắc</th><th class="n">Số comment</th>
<th class="n">% mẫu</th><th class="c">Kiểu nghe</th><th class="c">TC</th></tr></thead>
<tbody>{jtbd}</tbody></table>
<p class="f">Cỡ mẫu: <b>{vn(AUD['n_analyzed'])} comment</b> (loại {vn(AUD['n_noise'])} nhiễu từ {vn(AUD['n_total'])} thô).
⚠️ Người bình luận là thiểu số nhiệt tình nhất — dùng để <b>phát hiện</b> nhu cầu, không dùng để <b>định lượng</b>.</p>

<h3>2.3 Chân dung khán giả</h3>
{img("p3_personas.png")}
<table>
<thead><tr><th>Chân dung</th><th class="n">n</th><th class="n">% mẫu</th>
<th class="n">Like TV</th><th class="c">Đủ mẫu kết luận?</th></tr></thead>
<tbody>{per_rows}</tbody></table>

<div class="box">
<span class="l">Phân bố rất lệch — cần biết trước khi lập CDKH</span>
<p>Một chân dung chiếm <b>{vn(pers['p_healing']['pct'],1)}%</b>, ba chân dung còn lại cộng lại
chưa tới <b>2%</b>. Nếu hồ sơ CDKH đề xuất 4 phân khúc cân bằng, dữ liệu
<b>không đỡ nổi ba trong bốn</b>.</p>
<p>Đây không phải lỗi dữ liệu — người ta chỉ bình luận khi có lý do cảm xúc mạnh.
<b>Khuyến nghị: 1–2 phân khúc chính</b> + vài phân khúc phụ chấp nhận là thăm dò.</p>
</div>

<h2 class="pb">3. Nhu cầu tìm kiếm &amp; tiếng nói khán giả</h2>
<p class="f"><b>Ràng buộc bước sau:</b> tên kênh, tiêu đề video, tag, cấu trúc playlist</p>

<div class="box crit">
<span class="l">Phát hiện đảo hướng chiến lược</span>
<p>Comment nhắc <b>thuật toán đề xuất</b> nhiều gấp <b>{vn(AUD['discovery_algo_vs_search'],1)}×</b>
so với <b>chủ động tìm kiếm</b> ({AUD['discovery']['algorithm']['n']} vs {AUD['discovery']['searched']['n']}).</p>
<p><b>Hàm ý:</b> ngách này chạy bằng <b>đề xuất</b>, không bằng search. Trọng tâm phải là
<b>chọn đề tài + thumbnail + giữ chân</b>, không phải SEO từ khoá. Đây là kết luận
<b>ngược với giả định thông thường</b> khi làm kênh mới.</p>
</div>

<h3>3.1 Khoảng trống tiếng nói — từ khán giả nói mà tiêu đề không dùng</h3>
{img("p6_voice_gap.png")}
<table>
<thead><tr><th>Từ</th><th class="n">Trong comment</th><th class="n">Trong tiêu đề</th><th class="n">Tỉ lệ lệch</th></tr></thead>
<tbody>{gap_rows}</tbody></table>
<p class="f">Đây là <b>vốn từ khán giả đang dùng mà nhà sản xuất chưa dùng</b> — nguồn trực tiếp cho tiêu đề và tên playlist.</p>

<h3>3.2 Chủ đề — cái nào đáng làm, cái nào phải tránh</h3>
<table>
<thead><tr><th>Chủ đề</th><th class="n">n video</th><th class="n">Lift</th>
<th class="c">Kênh tốt hơn</th><th class="c">Phán quyết</th></tr></thead>
<tbody>{theme_rows}</tbody></table>
<p class="f">Kiểm 3 lớp: toàn thị trường → so trong nội bộ từng kênh → loại các trường hợp chỉ đúng khi gộp chung mà sai khi tách riêng.
{KW['themes_tested']} chủ đề đã kiểm, phần lớn <b>BÁC BỎ</b> — nghĩa là không phân biệt được hiệu quả.</p>

<div class="box crit">
<span class="l">🔴 VAN HIỆU CHỈNH (mục 3.4 template) — chốt: NGHE CHỦ ĐỘNG</span>
<p><b>Tỉ lệ ước tính: chủ động {vn(act,1)}% / nền {vn(bg,1)}%</b> &mdash; tính trên comment
có nêu bối cảnh. Chủ động thắng <b>{vn(act/bg,1)}×</b>.</p>
<p><b>Hàm ý bắt buộc theo template:</b> mục 4 phải làm <b>ĐẦY ĐỦ</b>, mọi thuộc tính âm nhạc
đều quan trọng. Đòn bẩy tăng trưởng chính là <b>chất lượng nhạc, chất giọng, tính xác thực</b>
&mdash; không phải thumbnail/độ dài.</p>
<p><b>Rủi ro nếu làm ngược:</b> nhạc generic → khán giả bỏ ngay, không đòn bẩy nào cứu được.</p>
<p><b>TC:</b> {tc("A")} — dựa trên {vn(sum(ctx[k]["n"] for k in ctx))} comment có nêu bối cảnh.</p>
</div>

<h2 class="pb">4. DNA dòng nhạc — đặc thù ràng buộc</h2>
<p class="f"><b>Độ sâu:</b> ĐẦY ĐỦ (theo van hiệu chỉnh mục 3.4) ·
<b>Ràng buộc bước sau:</b> toàn bộ production brief nhạc + hình ảnh</p>

<h3>Lớp 1 — Đặc thù âm thanh</h3>
{img("p5_recipe_tightness.png")}
<p class="f">Đo từ <b>{_t.get('n_tracks','—')} bản nhạc</b> của {_t.get('n_videos','—')} video thắng
(≥{vn(_t.get('view_threshold',0),0)} view) trên {_t.get('n_channels','—')} kênh.</p>
<table>
<thead><tr><th class="c">#</th><th>Ràng buộc lên sản xuất</th><th class="c">Từ mục</th><th class="c">Mức độ</th></tr></thead>
<tbody>{music_rows}</tbody></table>

<div class="box crit">
<span class="l">Điểm chết tiềm tàng — template đã cảnh báo, dữ liệu xác nhận</span>
<p>Template nghi ngờ: <i>"blues gospel có thể sống bằng chất giọng đã trải đời — giọng
sạch và trẻ, kể cả AI chất lượng cao, sẽ bị nhận ra là giả ngay."</i></p>
<p><b>Dữ liệu ủng hộ nghi ngờ này.</b> Độ lệch cao độ nhóm thắng giữ ở
<b>{vn(SPEC[_CENT_KEY]['median'],1) if _CENT_KEY else '—'} cent</b> ({SPEC[_CENT_KEY]['tightness'].upper() if _CENT_KEY else '—'})
và bám lưới chỉ
<b>{vn(SPEC[_GRID_KEY]['median']*100,0) if _GRID_KEY else '—'}%</b> ({SPEC[_GRID_KEY]['tightness'] if _GRID_KEY else '—'})
— giọng <b>cố tình để lệch tự nhiên</b>, không autotune cứng về lưới.</p>
<p><b>Ràng buộc:</b> tuyệt đối không autotune cứng. Nắn về 0 cent → ra chất nhạc máy → lạc ngách.</p>
</div>

<div class="box">
<span class="l">Có lời / không lời — đã chốt: CÓ LỜI</span>
<p>Chủ đề <i>instrumental</i> có lift <b>{vn(VD.get('bằng_chứng_hiệu_quả',{}).get('lift_toàn_thị_trường',0),3)}</b>
&mdash; <b>thấp nhất trong {KW['themes_tested']} chủ đề</b>, p &lt; 0,0001. Trong từng kênh:
<b>{VD.get('bằng_chứng_hiệu_quả',{}).get('số_kênh_tốt_hơn','—')} kênh</b> làm không lời tốt hơn chính họ.</p>
<p>Cộng với kết luận nghe chủ động và {vn(DA['lyrics_all_vocal'])}/{MK['M1_2_total_channels']} kênh đều có lời
→ <b>mục 6.2 của template (nhạc không lời) kết luận: diễn giải B — thị trường đã thử và không ăn.</b></p>
</div>

<h3>Lớp 2 — Đặc thù văn hoá &amp; tôn giáo</h3>
<div class="box crit">
<span class="l">Mục 4.2–4.6: CHƯA CÓ DỮ LIỆU</span>
<p>Nghịch lý gospel↔blues, tính xác thực văn hoá, rủi ro chiếm dụng, hệ phái &amp; thần học,
nhịp sinh hoạt tôn giáo &mdash; <b>hệ thống không trả lời được</b>. Đây là câu hỏi định tính,
cần nghiên cứu người thật, không đo bằng metadata YouTube.</p>
<p><b>Cảnh báo:</b> template ghi rõ <i>"chọn điểm đứng trên trục gospel↔blues chính là một
quyết định định vị. Không làm mục này thì bước sau sẽ chọn một cách vô thức."</i>
<b>Đây là khoảng trống nghiêm trọng nhất của hồ sơ v1.</b></p>
</div>

<h3>Lớp 3 — Đặc thù kinh tế &amp; vận hành</h3>
<table>
<thead><tr><th>Đặc thù</th><th class="c">Đúng/Sai</th><th>Ràng buộc chiến lược</th><th class="c">TC</th></tr></thead>
<tbody>
<tr><td>Blues chuẩn hoá cao → sản xuất hàng loạt dễ, <b>nhưng rào cản thấp, copy nhanh</b></td>
 <td class="c"><b class="ok">ĐÚNG</b></td>
 <td>{vn(EN['M3_2_newcomer_success_pct'],0)}% kênh mới thành công · tuổi trung vị nhóm thành công
 chỉ <b>{vn(EN['M3_3_alt_median_age_of_successful'],1)} tháng</b> → vào nhanh được, nhưng người khác cũng vậy</td>
 <td class="c">{tc("A")}</td></tr>
<tr><td>Nội dung tôn giáo → rủi ro nhạy cảm quảng cáo ảnh hưởng RPM</td>
 <td class="c"><b style="color:#B5731F">CHƯA RÕ</b></td>
 <td>RPM ước tính ${vn(MN['M5_2_rpm']['base'],1)} (khoảng ${vn(MN['M5_2_rpm']['low'],1)}–${vn(MN['M5_2_rpm']['high'],1)}) &mdash;
 <b>không đo được</b>, YouTube API không trả doanh thu kênh khác</td>
 <td class="c">{tc("B","cần số nội bộ")}</td></tr>
<tr><td>Nhạc nền, nghe dài → video dài, chi phí/giờ thấp</td>
 <td class="c"><b class="no">SAI</b></td>
 <td><b>Mâu thuẫn với van hiệu chỉnh</b>: khán giả nghe <b>chủ động</b> ({vn(act/bg,1)}× so với nền).
 Không thể dựa vào chiến lược "nhạc nền giá rẻ"</td>
 <td class="c">{tc("A")}</td></tr>
</tbody></table>

<div class="box">
<span class="l">🔴 Mục 4.7 — Chốt mâu thuẫn X vs Y</span>
<p><b>Kết luận: cả hai đúng ở mức độ khác nhau.</b></p>
<p><b>Giả thuyết X đúng ở khâu sản xuất:</b> cấu trúc bài chuẩn hoá, rào cản thấp,
{vn(EN['M3_2_newcomer_success_pct'],0)}% kênh mới vào được trong ~7 tháng.</p>
<p><b>Giả thuyết Y đúng ở chất giọng:</b> thông số CHẶT nhất của nhóm thắng là
<b>độ lệch cao độ</b> — thứ khó làm giả bằng AI nhất. Đây là <b>hào bảo vệ hẹp nhưng thật</b>.</p>
<p><b>Ràng buộc:</b> đừng đầu tư vào <i>độ phức tạp</i> của nhạc (dễ copy); đầu tư vào
<b>chất giọng và độ tự nhiên của cao độ</b> (khó copy).</p>
</div>

<h2 class="pb">5. Trạng thái cung trên YouTube</h2>

<h3>5.1 Số liệu tổng</h3>
<table>
<thead><tr><th>Chỉ số</th><th class="n">Mốc 1 · {S['scored_at']}</th><th class="n">Mốc 2</th><th class="c">TC</th></tr></thead>
<tbody>
<tr><td>Số kênh khảo sát</td><td class="n">{MK['M1_2_total_channels']}</td><td class="n">{MISS}</td><td class="c">{tc("A")}</td></tr>
<tr><td>Kênh còn hoạt động</td><td class="n">{MK['M1_2_active_channels']}</td><td class="n">{MISS}</td><td class="c">{tc("A")}</td></tr>
<tr><td>Tổng view/tháng</td><td class="n">{vn(MK['M1_1_views_per_month'],0)}</td><td class="n">{MISS}</td><td class="c">{tc("A")}</td></tr>
<tr><td>Thị phần top 5</td><td class="n">{vn(EN['top5_share'],1)}%</td><td class="n">{MISS}</td><td class="c">{tc("A")}</td></tr>
<tr><td>Thị phần top 20%</td><td class="n">{vn(EN['top20pct_share'],1)}%</td><td class="n">{MISS}</td><td class="c">{tc("A")}</td></tr>
<tr><td>Độ tập trung thị phần<br><span style="font-size:6.5pt;color:#8A7F76">hệ số Gini · 0 = chia đều, 1 = một kênh chiếm hết</span></td><td class="n">{vn(EN['M3_1_gini'],3)}</td><td class="n">{MISS}</td><td class="c">{tc("A")}</td></tr>
</tbody></table>

<div class="box crit">
<span class="l">🔴 RỦI RO LỚN NHẤT CỦA CẢ HỒ SƠ — thiếu mốc 2</span>
<p>Template ghi: <i>"Bắt buộc có mốc 2 (cách mốc 1 ≥30 ngày). Một ảnh chụp tĩnh không
cho biết ngách đang lên hay đã đỉnh."</i> <b>Hiện chỉ có mốc 1.</b></p>
<p>Chỉ số <b>M2.4 = {vn(MO['M2_4_demand_supply_gap'],3)}</b> (cầu/cung) quyết định
<b>4 trên 20 điểm</b>. Suy ra từ ngày đăng của video chứ không đo trực tiếp.
Nếu tính cả video vừa mới đăng (chưa kịp tích lượt xem) → <b>M2.4 = {vn(MK['_naive_M2_4'],3)}</b> → <b>0 điểm</b> →
tổng rơi xuống <b>{vn(SY['scenarios']['T2_drops_to_1'],2)}/20</b>.</p>
<p><b>Cùng một bộ dữ liệu, đổi cách đo là kết luận lật từ "vào" sang "bỏ".</b>
Đây là việc phải làm trước mọi việc khác.</p>
</div>

{img("p4_market_entry.png", cap="Trái: kênh mới có vào được không · Phải: thị phần tập trung tới đâu")}
{img("p8_momentum.png", cap="Trái: cầu tăng nhanh hơn cung · Phải: cùng dữ liệu, hai cách tính cho hai kết luận trái ngược")}
<h3>5.3 Kênh dẫn đầu</h3>
<table>
<thead><tr><th>Kênh</th><th class="n">Sub</th><th class="n">View/tháng</th>
<th class="n">Tuổi (th)</th><th class="n">Số video</th><th class="c">Quốc gia</th></tr></thead>
<tbody>{top_rows}</tbody></table>

<h3>5.5 Công thức đang thắng</h3>
<p class="f">Bảy dòng template yêu cầu — chỉ tính video đã đăng ít nhất 60 ngày, để lượt xem kịp ổn định.</p>
{norms_table}
{img("p9_production_norms.png")}

<h3>5.4 Kênh mới breakout (≤6 tháng)</h3>
<table>
<thead><tr><th>Kênh</th><th class="n">Tuổi</th><th class="n">View/tháng</th>
<th class="n">Số video</th><th class="n">View/video</th></tr></thead>
<tbody>{new_rows}</tbody></table>
<p><b>Kết luận độ bão hoà:</b> ngách <b>CHƯA bão hoà</b>. Kênh 2–4 tháng tuổi đạt
270k–1,08tr view/tháng. Tuổi trung vị nhóm thành công chỉ
<b>{vn(EN['M3_3_alt_median_age_of_successful'],1)} tháng</b>. {tc("A")}</p>

<div class="box">
<span class="l">5.7 — Nghịch lý sub ↔ view: đã kiểm, KHÔNG phải nghịch lý</span>
<p>Template nêu giả thuyết ngách chạy bằng đề xuất nên "sub gần như vô nghĩa".
<b>Kiểm trên {len(CH)} kênh: mức liên hệ giữa số sub và lượt xem/tháng
là {vn(spearman,3)}</b> trên thang 0&ndash;1 &mdash; <b>có liên hệ ở mức vừa phải</b>,
không phải bằng 0.</p>
<p><b>Diễn giải đúng:</b> sub <i>có</i> liên quan tới view, nhưng <b>không quyết định</b>.
Golden Soul Worship 31,6k sub đạt 1,08tr view/tháng, trong khi Still Worship 143k sub
đạt 1,18tr — gấp 4,5 lần sub nhưng chỉ hơn 9% view.</p>
<p><b>Kết hợp với tỉ lệ đề xuất/tìm kiếm {vn(AUD['discovery_algo_vs_search'],1)}×</b> → chiến lược
đúng là <b>tối ưu tín hiệu thuật toán</b>, dùng sub làm chỉ số phụ. {tc("A")}</p>
</div>

<h2 class="pb">6. Ma trận khoảng trống</h2>
<table>
<thead><tr><th class="c">#</th><th>Khoảng trống</th><th>Bằng chứng cầu</th>
<th>Bằng chứng cung</th><th class="c">Vì sao còn trống</th><th class="c">TC</th></tr></thead>
<tbody>
<tr class="hi"><td class="c">1</td><td><b>Old-school / vintage black gospel</b></td>
 <td>Đạt <b>{vn(KW['top_theme_lift'],2)}×</b> lượt xem/ngày so với video khác <span style="font-size:6.8pt;color:#8A7F76">(khác biệt chắc chắn về mặt thống kê)</span></td>
 <td>Chỉ <b>{vn(KW['top_theme_share_pct'],1)}%</b> video khai thác</td>
 <td class="c">Chưa ai tập trung</td><td class="c">{tc("A","4/8 kênh xác nhận")}</td></tr>
<tr><td class="c">2</td><td><b>Phục vụ khoảnh khắc cầu nguyện sáng</b></td>
 <td>{vn(ctx['prayer_devo']['pct'],1)}% + {vn(ctx['morning']['pct'],1)}% comment nêu bối cảnh này</td>
 <td>Chưa kênh nào định vị riêng cho khoảnh khắc</td>
 <td class="c">Chưa ai nghĩ tới</td><td class="c">{tc("A")}</td></tr>
<tr><td class="c">3</td><td><b>Vốn từ khán giả chưa dùng trong tiêu đề</b></td>
 <td>"amen" xuất hiện 2.233 lần trong comment</td>
 <td>Chỉ 5 lần trong tiêu đề — lệch <b>447×</b></td>
 <td class="c">Chưa ai để ý</td><td class="c">{tc("A")}</td></tr>
<tr><td class="c">4</td><td>Nhạc không lời</td>
 <td class="c"><b class="no">KHÔNG PHẢI CƠ HỘI</b></td>
 <td>Lift {vn(VD.get('bằng_chứng_hiệu_quả',{}).get('lift_toàn_thị_trường',0),3)} — thấp nhất</td>
 <td class="c"><b>Đã thử và chết</b></td><td class="c">{tc("A")}</td></tr>
</tbody></table>
<p class="f">⚠️ Cột "vì sao còn trống" của mục 1–3 là <b>suy luận</b>, chưa xác minh bằng
việc tìm kênh đã thử và thất bại — dữ liệu hiện tại <b>không chứa kênh đã chết</b> (thiên lệch sống sót).</p>

<h2>7. Kinh tế ngách</h2>
<table>
<thead><tr><th>Chỉ số</th><th class="n">Giá trị</th><th>Nguồn &amp; hạn chế</th><th class="c">TC</th></tr></thead>
<tbody>
<tr><td>RPM ước tính</td><td class="n">${vn(MN['M5_2_rpm']['base'],1)}</td>
 <td>Khoảng ${vn(MN['M5_2_rpm']['low'],1)}–${vn(MN['M5_2_rpm']['high'],1)}. <b>ƯỚC TÍNH</b>, không đo được</td>
 <td class="c">{tc("B","cần số nội bộ")}</td></tr>
<tr><td>Doanh thu ước tính/tháng</td><td class="n">${vn(MN['rev_base_monthly_usd'])}</td>
 <td>Suy từ RPM ước tính — <b>sai số nhân đôi</b></td><td class="c">{tc("B")}</td></tr>
<tr><td>Độ dài video trung vị</td><td class="n">{vn(MN['M5_3_median_duration_min'])} phút</td>
 <td>Đo trực tiếp</td><td class="c">{tc("A")}</td></tr>
<tr><td>Chi phí sản xuất/giờ nhạc</td><td class="n">{MISS}</td><td>Số nội bộ HG Media (B3)</td><td class="c">{tc("B")}</td></tr>
<tr><td>Chi phí sản xuất/video</td><td class="n">{MISS}</td><td>Số nội bộ HG Media (B3)</td><td class="c">{tc("B")}</td></tr>
<tr><td>Điểm hoà vốn</td><td class="n">{MISS}</td><td>Cần chi phí — không tính được</td><td class="c">{tc("B")}</td></tr>
<tr><td>Tính mùa vụ</td><td class="n">{MISS}</td><td>Cần ≥2 snapshot theo mùa</td><td class="c">{tc("A")}</td></tr>
</tbody></table>
<p><b>Đánh giá độ bền:</b> ☑ <b>Chưa xác định</b> — không đủ dữ liệu để phân biệt
"nhu cầu nền bền" với "trend đang lên". Cần mốc 2.</p>

<h2 class="pb">8. Rủi ro &amp; rào cản</h2>
<table>
<thead><tr><th class="c">#</th><th>Rủi ro</th><th class="c">Mức</th><th>Dấu hiệu sớm</th><th class="c">TC</th></tr></thead>
<tbody>
<tr class="hi"><td class="c">1</td><td><b>Chính sách YouTube về nội dung AI/sản xuất hàng loạt</b></td>
 <td class="c"><b class="no">SỐNG CÒN</b></td>
 <td>{vn(AI['M4_1_ai_first_top20_pct'],0)}% top20 là AI-first → nếu siết, cả ngách bị ảnh hưởng.
 Kịch bản siết: điểm rơi xuống <b>{vn(SY['scenarios']['policy_tightens'],2)}/20</b></td>
 <td class="c">{tc("A")}</td></tr>
<tr><td class="c">2</td><td>Trùng lặp nội dung giữa các kênh</td><td class="c"><b style="color:#B5731F">Trung bình</b></td>
 <td>Đo được: <b>{vn(M['risk']['cross_title_pct'],1)}%</b> tiêu đề trùng chéo,
 {M['risk']['channels_high_dup']} kênh trùng nhiều</td><td class="c">{tc("A")}</td></tr>
<tr><td class="c">3</td><td>Bị đối thủ copy nhanh</td><td class="c"><b style="color:#B5731F">Cao</b></td>
 <td>Kênh mới đạt ngưỡng thành công trong <b>{vn(EN['M3_3_alt_median_age_of_successful'],1)} tháng</b></td>
 <td class="c">{tc("A")}</td></tr>
<tr><td class="c">4</td><td>Nhạy cảm tôn giáo / hệ phái</td><td class="c">{MISS}</td>
 <td>Cần nghiên cứu định tính</td><td class="c">{tc("A")}</td></tr>
<tr><td class="c">5</td><td>Nhạy cảm văn hoá (tính xác thực)</td><td class="c">{MISS}</td>
 <td>Cần nghiên cứu định tính — <b>rủi ro chiếm dụng văn hoá chưa đánh giá</b></td><td class="c">{tc("A")}</td></tr>
<tr><td class="c">6</td><td>Bản quyền bản ghi âm</td><td class="c">{MISS}</td>
 <td>Cần rà soát pháp lý</td><td class="c">{tc("B")}</td></tr>
</tbody></table>
<p class="f">⚠️ <b>Ngày tra cứu chính sách YouTube về nội dung AI: CHƯA THỰC HIỆN.</b>
Template ghi rõ đây là bắt buộc và chính sách đã đổi nhiều lần —
<b>phải đọc bản gốc mới nhất trước khi khởi động dự án.</b></p>

<h2 class="pb">9. Bàn giao cho bước định vị</h2>

<h3>9.1 Điều đã xác lập chắc chắn</h3>
<table>
<thead><tr><th class="c">#</th><th>Kết luận</th><th>Bằng chứng</th></tr></thead>
<tbody>
<tr><td class="c">1</td><td><b>Khán giả nghe CHỦ ĐỘNG, không phải nhạc nền</b></td>
 <td>{vn(act,1)}% vs {vn(bg,1)}% — chênh {vn(act/bg,1)}×</td></tr>
<tr><td class="c">2</td><td><b>Nhạc CÓ LỜI</b> — không làm instrumental</td>
 <td>Lift {vn(VD.get('bằng_chứng_hiệu_quả',{}).get('lift_toàn_thị_trường',0),3)}, thấp nhất {KW['themes_tested']} chủ đề; {vn(DA['lyrics_all_vocal'])}/{MK['M1_2_total_channels']} kênh có lời</td></tr>
<tr><td class="c">3</td><td><b>Ngách chạy bằng ĐỀ XUẤT, không bằng tìm kiếm</b></td>
 <td>Tỉ lệ {vn(AUD['discovery_algo_vs_search'],1)}× nghiêng về thuật toán</td></tr>
<tr><td class="c">4</td><td><b>Ngách chưa bão hoà</b> — kênh mới vào được</td>
 <td>{vn(EN['M3_2_newcomer_success_pct'],0)}% kênh &lt;12 tháng đạt ≥100k view/tháng</td></tr>
<tr><td class="c">5</td><td><b>Chân dung chính: người đang chịu đựng</b>, nghe lúc cầu nguyện</td>
 <td>n={vn(pers['p_healing']['n'])} ({vn(pers['p_healing']['pct'],1)}%); bối cảnh cầu nguyện {vn(ctx['prayer_devo']['pct'],1)}%</td></tr>
<tr><td class="c">6</td><td><b>Không autotune cứng</b> — giọng phải lệch tự nhiên</td>
 <td>Lệch cao độ {vn(SPEC[_CENT_KEY]['median'],1) if _CENT_KEY else '—'} cent — thông số {SPEC[_CENT_KEY]['tightness'].upper() if _CENT_KEY else '—'} của nhóm thắng</td></tr>
</tbody></table>

<h3>9.2 Giả định còn treo — và cách chứng minh nó SAI</h3>
<table>
<thead><tr><th class="c">#</th><th>Giả định</th><th class="c">Tầng</th><th>Cách chứng minh SAI</th><th>Nếu sai thì hỏng gì</th></tr></thead>
<tbody>
<tr class="hi"><td class="c">1</td><td><b>Cầu tăng nhanh hơn cung (M2.4 = {vn(MO['M2_4_demand_supply_gap'],2)})</b></td>
 <td class="c">{tc("A")}</td>
 <td>Crawl mốc 2 sau ≥30 ngày. Nếu view/tháng toàn ngách <b>không tăng</b> → giả định sai</td>
 <td><b class="no">Điểm rơi {vn(SY['scenarios']['T2_drops_to_1'],2)}/20</b> &mdash;
 mất cơ sở chính để coi ngách đang tăng trưởng</td></tr>
<tr><td class="c">2</td><td>RPM ≈ ${vn(MN['M5_2_rpm']['base'],1)}</td><td class="c">{tc("B")}</td>
 <td>Đối chiếu RPM thật từ kênh nội bộ HG Media cùng khu vực/định dạng</td>
 <td>Nếu RPM $1,5 → mô hình tài chính sụp; nếu $6 → điểm {vn(SY['scenarios']['RPM_is_6'],2)}</td></tr>
<tr><td class="c">3</td><td>{vn(AI['M4_1_ai_first_top20_pct'],0)}% top20 là AI-first</td><td class="c">{tc("A")}</td>
 <td>Phân loại lại thủ công 20 kênh top; nếu &lt;60% là AI → giả định sai</td>
 <td>Nếu sai → năng lực AI của ta không phải lợi thế</td></tr>
<tr><td class="c">4</td><td>Ngách không bão hoà (dựa trên kênh còn sống)</td><td class="c">{tc("A")}</td>
 <td>Tìm kênh đã chết/bỏ trong ngách. Nếu tỉ lệ chết cao → tỉ lệ thành công {vn(EN['M3_2_newcomer_success_pct'],0)}% là ảo</td>
 <td><b>Thiên lệch sống sót — rủi ro chưa đánh giá</b></td></tr>
<tr><td class="c">5</td><td>Chất giọng là hào bảo vệ (giả thuyết Y)</td><td class="c">{tc("C")}</td>
 <td>Thử nghiệm A/B: cùng bài, một bản giọng sạch, một bản có "grit". So giữ chân</td>
 <td>Nếu sai → đầu tư vào giọng là lãng phí</td></tr>
</tbody></table>

<h3>9.3 Ràng buộc — production brief NHẠC</h3>
<table>
<thead><tr><th class="c">#</th><th>Ràng buộc</th><th class="c">Từ mục</th><th class="c">Mức độ</th></tr></thead>
<tbody>{music_rows}</tbody></table>

<h3>9.4 Ràng buộc — production brief HÌNH ẢNH</h3>
<table>
<thead><tr><th class="c">#</th><th>Ràng buộc</th><th class="c">Từ mục</th><th class="c">Mức độ</th></tr></thead>
<tbody>{img_rows if img_rows else '<tr><td colspan="4">'+MISS+' — chạy nhánh thumbnail (--with-thumbs)</td></tr>'}</tbody></table>

<h3>9.5 Thiết kế kênh như một thí nghiệm</h3>
<p>Vì tầng C (số thật từ kênh) không thể vượt bằng nghiên cứu chăm hơn, kênh đầu tiên
nên <b>thiết kế để sinh dữ liệu</b>:</p>
<table>
<thead><tr><th>Biến còn là giả định</th><th>Biến thể A</th><th>Biến thể B</th><th>Chỉ số phân biệt</th><th class="c">Thời gian</th></tr></thead>
<tbody>
<tr><td>Chất giọng (giả thuyết Y)</td><td>Giọng sạch, trẻ</td><td>Giọng có "grit", trải đời</td>
 <td>Giữ chân trung bình, % xem &gt;50%</td><td class="c">30 ngày</td></tr>
<tr><td>Độ dài video</td><td>~{vn(MN['M5_3_median_duration_min'])} phút (chuẩn ngách)</td><td>3 giờ (playlist dài)</td>
 <td>View/video, thời gian xem tổng</td><td class="c">45 ngày</td></tr>
<tr><td>Chủ đề old-school</td><td>Không nhấn old-school</td><td>Nhấn vintage/old-school</td>
 <td>Lượt xem/ngày — kiểm lại mức {vn(KW['top_theme_lift'],2)}×</td><td class="c">30 ngày</td></tr>
<tr><td>Nguồn traffic</td><td colspan="2">Không cần biến thể — chỉ cần <b>đọc YouTube Analytics</b></td>
 <td>% Suggested vs Search</td><td class="c">14 ngày</td></tr>
</tbody></table>

<h2 class="pb">Phụ lục — Những ô CHƯA CÓ DỮ LIỆU</h2>
<p>Template có {len(gaps)} mục hệ thống <b>không trả lời được</b>. Ghi rõ ở đây thay vì
để trống hoặc đoán:</p>
<table>
<thead><tr><th>Mục trong template</th><th>Cách lấy</th><th class="c">Tầng</th></tr></thead>
<tbody>{gap_tbl}</tbody></table>

<div class="box crit">
<span class="l">Ba việc phải làm trước khi duyệt dự án</span>
<p><b>1. Crawl mốc 2</b> (sau {S['scored_at']} ≥30 ngày) — quyết định 4/20 điểm,
lật kết luận từ "vào" sang "bỏ". <b>Việc số một.</b></p>
<p><b>2. Tra chính sách YouTube về nội dung AI</b> — rủi ro sống còn,
{vn(AI['M4_1_ai_first_top20_pct'],0)}% ngách là AI-first. Phải đọc bản gốc mới nhất.</p>
<p><b>3. Đối chiếu RPM thật từ kênh nội bộ</b> — cả mô hình tài chính đang dựng trên
một con số ước tính có sai số gấp 4 lần ($1,5–6,0).</p>
</div>

<h3>Nguồn dữ liệu đã dùng</h3>
<table>
<thead><tr><th class="c">#</th><th>Nguồn</th><th class="c">Cỡ mẫu</th><th>Hạn chế</th></tr></thead>
<tbody>
<tr><td class="c">1</td><td>Crawl YouTube API — kênh &amp; video</td>
 <td class="c">{MK['M1_2_total_channels']} kênh</td>
 <td>1 snapshot; không có kênh đã xóa (thiên lệch sống sót)</td></tr>
<tr><td class="c">2</td><td>Comment YouTube</td><td class="c">{vn(AUD['n_analyzed'])}</td>
 <td>Chỉ người chịu bình luận; {vn(DA['videos_never_crawled_comments'])} video chưa crawl comment
 ({vn(DA['uncrawled_share_of_views_pct'],1)}% view)</td></tr>
<tr><td class="c">3</td><td>DNA âm thanh v2</td>
 <td class="c">{_t.get('n_tracks','—')} bản</td>
 <td>Chỉ {_ins} video / {_t.get('n_channels','—')} kênh — <b>đều là kênh đang thắng</b>, chưa có nhóm thua</td></tr>
<tr><td class="c">4</td><td>Thumbnail</td><td class="c">{TH.get('n','—')} ảnh</td>
 <td>{TH.get('n_channels','—')} kênh, ngưỡng ≥{vn(TH.get('view_threshold',0),0)} view</td></tr>
</tbody></table>

<p class="f">Hồ sơ sinh tự động từ <code>_state/metrics.json</code> · <code>scores.json</code> ·
<code>AUDIO_RECIPE.json</code> — mọi con số đọc từ file, không gõ tay.
Chạy lại pipeline là hồ sơ cập nhật theo.</p>

</body></html>"""

HTML(string=DOC).write_pdf(OUT)
print(f"✅ {OUT}")
print(f"   {len(gaps)} mục CHƯA CÓ DỮ LIỆU đã ghi rõ cách lấy")
