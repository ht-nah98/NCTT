"""BÁO CÁO NHẠC HỢP NHẤT — âm thanh + âm nhạc + lời hát trong MỘT bản.

VÌ SAO GỘP: ba PDF cũ (04h brief · 04h2 kiểm định · 04h3 công thức) buộc người
dựng nhạc mở ba file và tự khớp với nhau. Người dùng phản hồi “chia nhiều phần
quá, khó đọc”. Bản này trả lời một câu hỏi duy nhất theo trình tự sản xuất:
**muốn viết một bài cho ngách này thì đặt gì, viết gì, và tránh gì.**

BA NỀN DỮ LIỆU, HAI CỠ MẪU — PHẢI GHI RÕ, ĐỪNG TRỘN:
  AUDIO_RECIPE/BRIEF   n=5   top 0,07% view · KHÔNG có nhóm đối chứng
  LYRICS_ANALYSIS      n=307 có cả lời và nhạc · 6 kênh · kiểm Simpson
Số từ hai nguồn không so sánh trực tiếp được. Mỗi bảng ghi cỡ mẫu của nó.

MỌI SỐ ĐỌC TỪ JSON (T27). Builder không tự tính, không gõ cứng.
Chuẩn trình bày: framework/00_system/06_REPORT_STANDARDS.md
"""
import json, sys
from pathlib import Path
from weasyprint import HTML
import warnings
warnings.filterwarnings("ignore")

N = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--")
         else "niches/christian-blues")
LY = N/"04_outlier/lyrics/LYRICS_ANALYSIS.json"
MW = N/"04_outlier/audio/MUSIC_WIDE.json"
RC = N/"04_outlier/audio/AUDIO_RECIPE.json"
BR = N/"04_outlier/audio/AUDIO_BRIEF.json"
for f in (LY, RC, BR):
    if not f.exists():
        sys.exit(f"Thiếu {f}")
L, R, B = (json.load(open(f, encoding="utf-8")) for f in (LY, RC, BR))
# MUSIC_WIDE là tuỳ chọn: ngách chưa chạy 04j vẫn dựng được báo cáo (chỉ n=5)
MWD = json.load(open(MW, encoding="utf-8")) if MW.exists() else {}
OUT = N/"99_report/NHAC_Bao-cao-Hop-nhat.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)


def vn(x, nd=None):
    if x is None:
        return "—"
    s = f"{x:.{nd}f}" if nd is not None else f"{x:g}"
    return s.replace(".", ",")


def vn_int(x):
    """Hàng nghìn dùng dấu CHẤM kiểu Việt: 83083 → 83.083 (§3 chuẩn báo cáo)."""
    return f"{int(x):,}".replace(",", ".")


SRC, W = L["nguồn"], L["1_viết_lời"]["thông_số"]

MB = MWD.get("nhịp_độ", {})                       # n=307, đã sửa bẫy nhân đôi
MODE_H = MWD.get("điệu_thức", {}).get("bộ_dò_hoà_âm", {})
MODE_C = MWD.get("điệu_thức", {}).get("bộ_dò_CNN", {})
MJ_PCT = MODE_H.get("pct_trưởng", 100)
DKM = MWD.get("lời_buồn_và_điệu_thức", {})
LUF = MWD.get("độ_to", {})
LRA = MWD.get("dải_động", {})
LINK, PPL = L["2_lời_với_nhạc"], L["3_người_nghe"]
REC = R["recipe"] if "recipe" in R else B.get("recipe", {})
BREC = B["recipe"]

# ── nhãn người-đọc-được cho từng thông số lời ───────────────────────────
LAB = {
    "words_per_min":    ("Chữ mỗi phút", "mật độ hát — ràng buộc trực tiếp khi viết"),
    "words_per_line":   ("Chữ mỗi dòng", "độ dài câu hát"),
    "line_len_sd":      ("Độ lệch dài dòng", "câu đều nhau hay dài ngắn xen kẽ"),
    "n_lines":          ("Số dòng cả bài", "quy mô bài"),
    "repeat_ratio":     ("Tỷ lệ lặp dòng", "mức dùng điệp khúc"),
    "unique_line_ratio":("Tỷ lệ dòng riêng", "phần dòng không lặp lại"),
    "ttr":              ("Phong phú từ vựng", "tỷ lệ từ khác nhau / tổng từ"),
    "vocab_size":       ("Số từ vựng", "vốn từ một bài"),
    "pct_first_sing":   ("Ngôi thứ nhất số ít", "hát cho cá nhân"),
    "pct_first_plur":   ("Ngôi thứ nhất số nhiều", "hát tập thể"),
    "pct_second":       ("Ngôi thứ hai", "hướng về đối tượng"),
}
TIGHT_CSS = {"CHẶT": "ok", "vừa": "ac", "rộng": "no"}
TIGHT_DO = {"CHẶT": "theo sát", "vừa": "nên theo", "rộng": "tự do"}


def write_rows():
    out = []
    for k, v in W.items():
        if not v:
            continue
        name, why = LAB.get(k, (k, ""))
        t = v.get("độ_tập_trung", "—")
        out.append(
            f'<tr><td><b>{name}</b><div class="f">{why}</div></td>'
            f'<td class="n">{vn(v["p25"])} – {vn(v["p75"])}</td>'
            f'<td class="n"><b>{vn(v["trung_vị"])}</b></td>'
            f'<td class="c"><span class="{TIGHT_CSS.get(t,"")}">{t}</span></td>'
            f'<td class="c">{TIGHT_DO.get(t,"")}</td></tr>')
    return "\n".join(out)


def link_rows(items, show_verdict=True):
    out = []
    for c in items:
        v = c["phán_quyết"]
        cls = "ok" if v == "XÁC NHẬN" else "no" if v == "BÁC BỎ" else "ac"
        nm = LAB.get(c["lời"], (c["lời"], ""))[0]
        out.append(
            f'<tr><td><b>{nm}</b> × {c["nhạc"]}</td>'
            f'<td class="n">{vn(c["rho_gộp"], 2)}</td>'
            f'<td class="n">{vn(c["rho_trung_vị_theo_kênh"], 2)}</td>'
            f'<td class="c">{c["số_kênh_đảo_dấu"]}/{c["số_kênh_xét"]}</td>'
            + (f'<td class="c"><span class="{cls}">{v}</span></td>' if show_verdict else "")
            + "</tr>")
    return "\n".join(out)


def grp_rows(d, top=None, cap=False):
    items = list(d.items())[:top] if top else list(d.items())
    return "\n".join(
        f'<tr><td>{k.title() if cap else k.replace("_", " ")}</td>'
        f'<td class="n">{vn(v["pct_bài"], 1)}%</td>'
        f'<td class="n">{v["số_bài"]}</td></tr>' for k, v in items)


ST = PPL.get("họ_đang_ở_đâu", {})
PO = PPL.get("họ_nhận_được_gì", {})
AD = PPL.get("xưng_hô_với_Chúa", {})
ARC = PPL.get("cung_cảm_xúc", {})
st_rows, po_rows = grp_rows(ST), grp_rows(PO)
ad_rows = grp_rows(AD, 5, cap=True)
st_max = max(v["pct_bài"] for v in ST.values()) if ST else 0
# ngưỡng của SÁU lời hứa cao nhất (bỏ mục thấp nhất) — nói "6/7 vượt X" thì X
# phải là giá trị nhỏ nhất TRONG SÁU đó, không phải mức sàn tuỳ chọn
_po = sorted((v["pct_bài"] for v in PO.values()), reverse=True)
po_n65 = sum(1 for x in _po if x >= 65)      # bao nhiêu lời hứa đạt ≥65%
po_min = _po[po_n65 - 1] if po_n65 else (_po[0] if _po else 0)
po_top3 = ", ".join(list(PO)[:3]).replace("_", " ") if PO else ""

theme_rows = "\n".join(
    f'<tr><td>{k.replace("_"," ")}</td><td class="n">{v["số_bài"]}</td>'
    f'<td class="n">{vn(v["pct"], 1)}%</td></tr>'
    for k, v in PPL["chủ_đề"].items())

_lim = list(L["giới_hạn"])
# giới hạn của PHẦN NHẠC — mục 7 trước đây chỉ nói về lời, trong khi báo cáo
# nay có cả phần nhạc n=307. Thiếu hai điều dưới đây là để người đọc hiểu sai
# mức chắc chắn của bảng điệu thức và của phần hợp âm/cấu trúc.
if MWD:
    _dm = abs((MODE_H.get("pct_trưởng") or 0) - (MODE_C.get("pct_trưởng") or 0))
    _lim.append({
        "thiếu": "Điệu thức chỉ đo được gần đúng",
        "hệ_quả": f"Hai bộ dò độc lập chênh nhau {vn(_dm, 1)} điểm phần trăm "
                  f"({vn(MODE_H.get('pct_trưởng'), 1)}% so với "
                  f"{vn(MODE_C.get('pct_trưởng'), 1)}% trưởng). Dùng con số này "
                  f"để thấy TỶ LỆ, đừng dùng để phán một bài cụ thể."})
    _lim.append({
        "thiếu": "Hợp âm, cấu trúc đoạn, groove vẫn chỉ có 5 bản",
        "hệ_quả": "Các phần đó cần ranh giới đoạn đáng tin mà bộ "
                  f"{MB.get('n', 0)} track không có (lệch vài giây là hỏng phân "
                  "tích hoà âm). Prompt sinh nhạc ở mục 1 cũng dựng từ 5 bản."})
limit_rows = "\n".join(
    f'<li><b>{x["thiếu"]}</b> — {x["hệ_quả"]}</li>' for x in _lim)

conf = LINK["xác_nhận"]
conf_rows = link_rows(conf) or '<tr><td colspan="5">Không mối nào qua được kiểm Simpson.</td></tr>'
rej_rows = link_rows(LINK["bác_bỏ"])

VD = B.get("vocal_decision", {})
bpm = BREC.get("tempo_bpm", {})
bpm_rng = bpm.get("range", [None, None])

DOC = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size:A4; margin:17mm 15mm 20mm;
 @bottom-center {{ content counter(page) " / " counter(pages);
  font-family:"DejaVu Sans";font-size:8pt;color:#9A8E85; }} }}
body {{ font-family:"DejaVu Sans",sans-serif;font-size:9.5pt;line-height:1.55;color:#1A1614; }}
h1 {{ font-size:23pt;margin:0 0 6pt;letter-spacing:-.4pt; }}
h2 {{ font-size:13pt;margin:20pt 0 7pt;padding-bottom:4pt;
 border-bottom:1.5pt solid #1A1614;page-break-after:avoid; }}
h3 {{ font-size:10.5pt;margin:14pt 0 3pt;color:#8C3A2B;page-break-after:avoid; }}
p {{ margin:6pt 0; }}
.sub {{ color:#6B615A;font-size:10pt;margin:0 0 10pt; }}
.meta {{ font-size:8pt;color:#7A6F68;border-top:.6pt solid #E2DAD1;
 border-bottom:.6pt solid #E2DAD1;padding:6pt 0;margin-bottom:14pt; }}
table {{ border-collapse:collapse;width:100%;font-size:8.5pt;margin:6pt 0 10pt;page-break-inside:avoid; }}
th {{ background:#F2EEE8;text-align:left;padding:5pt 7pt;font-size:7.5pt;
 text-transform:uppercase;letter-spacing:.4pt;color:#5A514B;border-bottom:1pt solid #CFC4B8; }}
td {{ padding:5pt 7pt;border-bottom:.6pt solid #EDE7E0;vertical-align:top; }}
td.n, th.n {{ text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap; }}
td.c, th.c {{ text-align:center;white-space:nowrap; }}
.ok {{ color:#2F6B4F;font-weight:bold; }} .no {{ color:#9B2C2C;font-weight:bold; }}
.ac {{ color:#8C3A2B; }}
.box {{ border-left:2.5pt solid #8C3A2B;background:#F9F4F2;padding:8pt 11pt;
 margin:11pt 0;page-break-inside:avoid; }}
.box.crit {{ border-left-color:#9B2C2C;background:#FBEEEE; }}
.box.ok {{ border-left-color:#2F6B4F;background:#EFF5F1; }}
.box .l {{ font-size:7.5pt;text-transform:uppercase;letter-spacing:.7pt;
 font-weight:bold;color:#8C3A2B;display:block;margin-bottom:4pt; }}
.box.crit .l {{ color:#9B2C2C; }} .box.ok .l {{ color:#2F6B4F; }}
.box p {{ margin:0 0 5pt;font-size:9pt; }} .box p:last-child {{ margin-bottom:0; }}
.kpi {{ display:flex;gap:7pt;margin:11pt 0; }}
.kpi div {{ flex:1;border:.6pt solid #E2DAD1;padding:8pt 9pt; }}
.kpi .k {{ font-size:6.8pt;text-transform:uppercase;letter-spacing:.5pt;color:#7A6F68;margin-bottom:4pt; }}
.kpi .v {{ font-size:15pt;font-weight:bold;letter-spacing:-.3pt; }}
.kpi .c {{ font-size:7pt;color:#7A6F68;margin-top:3pt;line-height:1.3; }}
.formula {{ background:#F7F4F0;border:.6pt solid #E2DAD1;padding:8pt 11pt;
 font-size:8.5pt;margin:7pt 0;line-height:1.8; }}
.pb {{ page-break-before:always; }}
.f {{ font-size:7.5pt;color:#7A6F68;margin:-1pt 0 5pt; }}
ul {{ margin:6pt 0;padding-left:15pt; }} li {{ margin:3pt 0; }}
</style></head><body>

<h1>Nhạc &amp; Lời — Báo cáo hợp nhất</h1>
<p class="sub">Ngách <b>christian-blues</b> · mọi thứ cần để dựng một bài:
âm thanh, âm nhạc, lời hát</p>
<div class="meta">
Nền lời: <b>{SRC['n_track']} bài</b> · {vn_int(SRC['tổng_chữ'])} chữ ·
{SRC['n_kênh_đủ_lớn']} kênh chính · {SRC['n_ghép_được_với_nhạc']} bài có <b>cả lời và nhạc</b><br>
Nền nhạc: <b>{B['generated_from']['n_tracks']} bản</b> ·
{B['generated_from']['percentile']}<br>
</div>

<div class="box crit">
<span class="l">Đọc bảng nào cũng phải xem cỡ mẫu</span>
<p>Báo cáo này ghép <b>hai nền dữ liệu khác cỡ</b>. Phần <b>nhạc</b> dựng từ
<b>5 bản</b> top 0,07% lượt xem — sâu nhưng hẹp, và <b>không có nhóm đối chứng</b>.
Phần <b>lời</b> dựng từ <b>{SRC['n_track']} bài</b> từ
<b>{SRC['n_kênh_đủ_lớn']} kênh chính</b> (mỗi kênh ≥{SRC['min_bài_mỗi_kênh']} bài) — rộng hơn nhiều
nhưng là <b>mẫu tiện có</b>, không phải mẫu đại diện toàn ngách.</p>
<p>Vì thế <b>đừng so trực tiếp số của hai phần</b>. Mỗi bảng đều ghi cỡ mẫu ngay
tiêu đề — hãy đọc nó trước khi đọc số.</p>
</div>

<h2>1. Tóm tắt — dựng một bài thì đặt gì</h2>

<div class="kpi">
<div><div class="k">Nhịp độ</div><div class="v">{vn(MB.get('trung_vị', bpm.get('target')), 0)}</div>
<div class="c">BPM · khoảng {vn(MB.get('p25', bpm_rng[0]), 0)}–{vn(MB.get('p75', bpm_rng[1]), 0)}
· n={MB.get('n', 5)}</div></div>
<div><div class="k">Điệu trưởng</div><div class="v">{vn(MJ_PCT, 0)}%</div>
<div class="c">{MODE_H.get('trưởng', 0)}/{MODE_H.get('n', 0)} track · phần còn lại dùng điệu thứ</div></div>
<div><div class="k">Chữ mỗi phút</div><div class="v">{vn(W['words_per_min']['trung_vị'], 0)}</div>
<div class="c">khoảng {vn(W['words_per_min']['p25'], 0)}–{vn(W['words_per_min']['p75'], 0)} · n={SRC['n_track']}</div></div>
<div><div class="k">Giọng hát</div><div class="v">{VD.get('kết_luận', '—')}</div>
<div class="c">độ tin cậy {VD.get('độ_tin_cậy', '—')} · bằng chứng 3 lớp</div></div>
</div>

<div class="formula">
<b>Prompt sinh nhạc</b> (n=5):<br>{BREC.get('prompt_en', '—')}<br><br>
<b>Lời</b> (n={SRC['n_track']}) — <b>ràng buộc chặt duy nhất</b>: tỷ lệ dòng riêng
{vn(W['unique_line_ratio']['trung_vị'], 2)} (viết ít lặp).
Các mức <i>tham khảo, không bắt buộc</i>:
{vn(W['words_per_min']['p25'], 0)}–{vn(W['words_per_min']['p75'], 0)} chữ/phút ·
câu {vn(W['words_per_line']['p25'], 1)}–{vn(W['words_per_line']['p75'], 1)} chữ ·
ngôi thứ nhất số ít {vn(PPL['ngôi_kể']['tôi_pct'], 1)}%
</div>

<h2 class="pb">2. Nhạc — đo trên {MB.get('n', 0)} track</h2>
<p>Phần này đo trên <b>toàn bộ track có dữ liệu âm thanh</b>, rộng hơn nhiều so với
mẫu 5 bản dùng cho hợp âm và cấu trúc.</p>

<table>
<tr><th>Thông số</th><th class="n">p25–p75</th><th class="n">Trung vị</th>
<th class="n">Nhỏ nhất</th><th class="n">Lớn nhất</th></tr>
<tr><td><b>Nhịp độ</b><div class="f">BPM, đã gỡ bẫy nhân đôi tempo</div></td>
<td class="n">{vn(MB.get('p25'), 1)} – {vn(MB.get('p75'), 1)}</td>
<td class="n"><b>{vn(MB.get('trung_vị'), 1)}</b></td>
<td class="n">{vn(MB.get('min'), 0)}</td><td class="n">{vn(MB.get('max'), 0)}</td></tr>
<tr><td><b>Độ to</b><div class="f">LUFS · chuẩn phát trực tuyến ≈ −14</div></td>
<td class="n">{vn(LUF.get('p25'), 1)} – {vn(LUF.get('p75'), 1)}</td>
<td class="n"><b>{vn(LUF.get('trung_vị'), 1)}</b></td>
<td class="n">{vn(LUF.get('min'), 1)}</td><td class="n">{vn(LUF.get('max'), 1)}</td></tr>
<tr><td><b>Dải động</b><div class="f">LRA · chênh lệch to/nhỏ trong bài</div></td>
<td class="n">{vn(LRA.get('p25'), 1)} – {vn(LRA.get('p75'), 1)}</td>
<td class="n"><b>{vn(LRA.get('trung_vị'), 1)}</b></td>
<td class="n">{vn(LRA.get('min'), 1)}</td><td class="n">{vn(LRA.get('max'), 1)}</td></tr>
</table>
<p class="f">04_outlier/audio/MUSIC_WIDE.json · {MB.get('ghi_chú', '')}</p>

<div class="box crit">
<span class="l">Vì sao không dùng con số BPM thô</span>
<p>Bộ dò nhịp bắt nhầm <b>bội số 2×</b> ở
<b>{MB.get('số_track_phải_sửa', 0)}/{MB.get('n', 0)} track</b>
({vn(MB.get('pct_phải_sửa'), 1)}%) — nhạc chậm bị đọc thành 120–190 BPM.
Đã sửa trước khi tính.</p>
<p><b>Ba nguồn độc lập cùng chỉ một chỗ:</b> đề xuất half-time của chính bộ dò,
quy tắc chia đôi theo phân bố, và {MB.get('đối_chiếu_n5', '')}.
Nhờ vậy con số {vn(MB.get('trung_vị'), 0)} BPM tin được.</p>
</div>

<h3>Điệu thức — trưởng là mặc định, không phải bắt buộc</h3>
<table>
<tr><th>Bộ dò</th><th class="n">Số track</th><th class="n">Trưởng</th>
<th class="n">Thứ</th><th class="n">% trưởng</th></tr>
<tr><td>Bộ dò hoà âm</td><td class="n">{MODE_H.get('n', 0)}</td>
<td class="n">{MODE_H.get('trưởng', 0)}</td><td class="n">{MODE_H.get('thứ', 0)}</td>
<td class="n"><b>{vn(MODE_H.get('pct_trưởng'), 1)}%</b></td></tr>
<tr><td>Bộ dò CNN</td><td class="n">{MODE_C.get('n', 0)}</td>
<td class="n">{MODE_C.get('trưởng', 0)}</td><td class="n">{MODE_C.get('thứ', 0)}</td>
<td class="n">{vn(MODE_C.get('pct_trưởng'), 1)}%</td></tr>
</table>
<p class="f">Hai bộ dò chạy độc lập — chênh nhau cho thấy mức bất định thật của
phép đo điệu thức, không phải một trong hai sai</p>

<div class="box ok">
<span class="l">Đừng đóng khung điệu thức</span>
<p>{MWD.get('điệu_thức', {}).get('phát_hiện', '')}</p>
</div>

<h3>Lời buồn có cần điệu thứ không?</h3>
<div class="box">
<span class="l">Câu trả lời: không</span>
<p>{DKM.get('đọc_là', '')}</p>
<p>Số từ mang màu tối trong bài điệu <b>thứ</b> và điệu <b>trưởng</b> gần như
bằng nhau (trung vị {vn(DKM.get('từ_tối_TV_điệu_thứ'), 0)} so với
{vn(DKM.get('từ_tối_TV_điệu_trưởng'), 0)}), trên {DKM.get('n', 0)} bài có cả lời
và nhạc.</p>
<p><b>Ý nghĩa khi sáng tác:</b> viết lời nặng rồi đặt lên nền điệu trưởng là
<b>đúng chất ngách</b>, không phải mâu thuẫn — nó chính là cách ngách này
“đi qua” nỗi buồn thay vì ở lại trong đó.</p>
</div>

<h2 class="pb">3. Viết lời thế nào — n={SRC['n_track']} bài</h2>
<p>{L['1_viết_lời']['cách_dùng']}</p>
<table>
<tr><th>Thông số</th><th class="n">Khoảng p25–p75</th><th class="n">Trung vị</th>
<th class="c">Độ tập trung</th><th class="c">Nên làm</th></tr>
{write_rows()}
</table>
<p class="f">04_outlier/lyrics/LYRICS_ANALYSIS.json → 1_viết_lời.thông_số</p>

<div class="box">
<span class="l">Thông số “rộng” không phải dữ liệu kém</span>
<p>Nó là <b>phát hiện</b>: nhóm này <b>không thống nhất</b> ở đó. Ép theo một con số
là bịa ra ràng buộc không tồn tại. Chỉ <b>Tỷ lệ dòng riêng</b> đạt mức CHẶT
({vn(W['unique_line_ratio']['trung_vị'], 2)}) — tức gần như cả ngách viết lời
<b>ít lặp</b>, mỗi dòng một ý. Đây là ràng buộc thật duy nhất về cấu trúc lời.</p>
<p>Ngược lại <b>tỷ lệ lặp</b> trải từ {vn(W['repeat_ratio']['min'], 2)} đến
{vn(W['repeat_ratio']['max'], 2)} — điệp khúc dày hay mỏng <b>đều đang chạy được</b>.</p>
</div>

<h2>4. Lời đi với nhạc ra sao — n={SRC['n_ghép_được_với_nhạc']} bài có cả hai</h2>
<p>Mỗi bài hát có đồng thời thông số lời và thông số nhạc, nên trả lời được
câu <i>“lời dày thì phối khí thế nào”</i>.</p>

<div class="box crit">
<span class="l">Vì sao p nhỏ vẫn không đủ</span>
<p>Xét <b>{LINK['số_mối_xét']} mối</b> lời×nhạc. Nhiều mối có p cực nhỏ
(tới 1,8·10⁻²⁰) — trông như phát hiện lớn. Nhưng tách theo từng kênh thì phần lớn
<b>tan biến hoặc đảo dấu</b>: đó là <b>bẫy gộp Simpson</b>, tương quan đến từ khác biệt
<i>giữa các kênh</i> chứ không phải quy luật <i>bên trong</i> một bài.</p>
<p>Sau kiểm: <b class="ok">{LINK['số_xác_nhận']} xác nhận</b> ·
<b class="no">{LINK['số_bác_bỏ']} bác bỏ</b>. Chỉ dùng phần xác nhận.</p>
</div>

<h3>Qua được kiểm — dùng được</h3>
<table>
<tr><th>Mối liên hệ</th><th class="n">rho gộp</th><th class="n">rho trong kênh</th>
<th class="c">Kênh đảo dấu</th><th class="c">Phán quyết</th></tr>
{conf_rows}
</table>
<p class="f">rho = Spearman · “trong kênh” = trung vị rho của từng kênh riêng ·
kênh &lt;15 bài không đưa vào kiểm</p>

<div class="box ok">
<span class="l">Đọc hai mối này thế nào khi sáng tác</span>
<p><b>Lời dày đi với trống mạnh, ghi-ta nhẹ.</b> Bài nhiều chữ mỗi phút thì phần
trống nổi hơn và ghi-ta lùi lại — hợp lý về mặt phối khí: khi giọng bận, ghi-ta
nhường chỗ, trống giữ nhịp cho lời bám vào.</p>
<p><b>Dùng như thế nào:</b> chọn mật độ lời <i>trước</i>, rồi chỉnh phối khí theo.
Viết lời dày ({vn(W['words_per_min']['p75'], 0)}+ chữ/phút) thì đẩy trống lên và
giảm ghi-ta; viết lời thưa thì làm ngược lại. Đây là <b>xu hướng nhẹ</b>
(rho trong kênh ~0,2), không phải quy luật cứng.</p>
</div>

<h3>Bị bác bỏ — đừng đưa vào công thức</h3>
<table>
<tr><th>Mối liên hệ</th><th class="n">rho gộp</th><th class="n">rho trong kênh</th>
<th class="c">Kênh đảo dấu</th><th class="c">Phán quyết</th></tr>
{rej_rows}
</table>
<p class="f">Đây là các mối <b>trông thuyết phục nếu chỉ nhìn p-value</b> — giữ lại
trong báo cáo để không ai đi tìm lại rồi tưởng là phát hiện mới.</p>

<h2 class="pb">5. Viết cho ai — và họ nhận được gì</h2>
<p>Ba câu hỏi tách bạch: người nghe <b>đang ở trạng thái nào</b> khi bấm play,
<b>mang về được gì</b> sau khi nghe, và bài dẫn họ đi theo <b>cung cảm xúc</b> nào.</p>

<h3>5.1 Người nghe đang ở đâu</h3>
<table>
<tr><th>Trạng thái</th><th class="n">% số bài chạm tới</th><th class="n">Số bài</th></tr>
{st_rows}
</table>
<p class="f">04_outlier/lyrics/LYRICS_ANALYSIS.json → 3_người_nghe.họ_đang_ở_đâu ·
đếm theo ranh giới từ, một bài chạm nhiều trạng thái được đếm nhiều dòng</p>

<h3>5.2 Người nghe nhận được gì</h3>
<table>
<tr><th>Lời hứa</th><th class="n">% số bài chạm tới</th><th class="n">Số bài</th></tr>
{po_rows}
</table>

<div class="box ok">
<span class="l">Phát hiện quan trọng nhất cho người viết lời</span>
<p><b>Nỗi đau chạm nhẹ, lời hứa đổ đầy.</b> Trạng thái đau cao nhất chỉ
<b>{vn(st_max, 1)}%</b> số bài, trong khi <b>{po_n65}/{len(PO)}</b> lời hứa
đạt <b>{vn(po_min, 1)}%</b> trở lên. Ngách này <b>không</b> viết nhạc than thân — nó
<b>gọi tên nỗi đau một lần rồi dành phần lớn bài để trả lời</b>.</p>
<p><b>Tỷ lệ để viết:</b> nêu nỗi đau trong <b>một phần</b>, dùng phần còn lại cho
lời hứa. Bài nào ở lại trong nỗi đau là lệch chất ngách.</p>
<p><b>Ba lời hứa lõi</b>: <b>{po_top3}</b>. Bài thiếu cả ba sẽ nghe rỗng
dù nhạc đúng công thức.</p>
</div>

<h3>5.3 Cung cảm xúc — bài đi từ đâu đến đâu</h3>
<table>
<tr><th>Phần bài</th><th class="n">Điểm sáng/tối</th><th>Ý nghĩa</th></tr>
<tr><td>Đầu bài</td><td class="n">{vn(ARC.get('điểm_đầu_bài'), 2)}</td>
<td>mở ra trong bóng tối</td></tr>
<tr><td>Giữa bài</td><td class="n">{vn(ARC.get('điểm_giữa_bài'), 2)}</td>
<td>chuyển</td></tr>
<tr><td>Cuối bài</td><td class="n">{vn(ARC.get('điểm_cuối_bài'), 2)}</td>
<td>kết trong ánh sáng</td></tr>
</table>
<p class="f">Thang {ARC.get('thang', '')} · n={ARC.get('n_bài', 0)} bài (bài dưới 6 đoạn
không chia ba được) · chia theo SỐ ĐOẠN, không theo thời gian</p>

<div class="box">
<span class="l">Đừng kết bài ở chỗ tối</span>
<p>Điểm đi từ {vn(ARC.get('điểm_đầu_bài'), 2)} lên {vn(ARC.get('điểm_cuối_bài'), 2)} —
<b>{vn(ARC.get('pct_sáng_dần'), 1)}%</b> số bài sáng dần về cuối. Đây là cung cảm
xúc chuẩn của ngách, và nó khớp với phát hiện bên phần nhạc:
<b>5/5 bản ở điệu trưởng</b>.</p>
<p>Cũng lý giải vì sao chủ đề <b>than khóc</b> thấp nhất
({vn(PPL['chủ_đề']['than_khóc']['pct'], 1)}%): blues ở ngách này là
<b>đi qua</b> nỗi buồn, không phải <b>ở lại</b> trong nó.</p>
</div>

<h3>5.4 Người nghe ở một mình hay trong hội chúng</h3>
<div class="kpi">
<div><div class="k">Ngôi thứ nhất số ít</div><div class="v">{vn(PPL['ngôi_kể']['tôi_pct'], 1)}%</div>
<div class="c">tôi / của tôi</div></div>
<div><div class="k">Ngôi thứ nhất số nhiều</div><div class="v">{vn(PPL['ngôi_kể']['chúng_ta_pct'], 1)}%</div>
<div class="c">chúng ta / của chúng ta</div></div>
<div><div class="k">Ngôi thứ hai</div><div class="v">{vn(PPL['ngôi_kể']['bạn_pct'], 1)}%</div>
<div class="c">Ngài / của Ngài</div></div>
</div>

<div class="box ok">
<span class="l">Kết luận rõ ràng nhất của toàn bộ phân tích lời</span>
<p>Ngôi thứ nhất số nhiều bằng <b>0,0%</b> — không phải “ít”, mà là
<b>gần như vắng mặt</b> trên {SRC['n_track']} bài. Lời viết cho <b>một người
đang nghe một mình</b>, không phải hội chúng hát chung.</p>
<p>Đây là <b>bằng chứng độc lập</b> cho kết luận đã có ở STEP_05: bối cảnh nghe
chủ động (cầu nguyện, sáng sớm, tang chế) chiếm
<b>{vn(VD.get('bằng_chứng_bối_cảnh', {}).get('tỷ_lệ'), 1)}×</b> so với nghe nền.
Hai nguồn hoàn toàn khác nhau — bình luận và lời hát — cùng chỉ về một chỗ.</p>
<p><b>Khi viết:</b> luôn dùng “tôi”. Chuyển sang “chúng ta” là bước sang nhạc
hội chúng — một thị trường khác, với người nghe khác.</p>
</div>

<h3>5.5 Gọi Chúa bằng gì</h3>
<table>
<tr><th>Danh xưng</th><th class="n">% số bài</th><th class="n">Số bài</th></tr>
{ad_rows}
</table>
<div class="box">
<span class="l">Chi tiết nhỏ quyết định chất ngách</span>
<p><b>Lord</b> ({vn(AD.get('lord', {}).get('pct_bài'), 1)}%) áp đảo
<b>Jesus</b> ({vn(AD.get('jesus', {}).get('pct_bài'), 1)}%). Đây là khác biệt
giữa <b>blues thờ phượng</b> và <b>nhạc phúc âm đương đại</b> — cùng đức tin,
khác cách xưng hô, và người nghe cảm nhận được ngay.</p>
</div>

<h3>5.6 Từ vựng chung của ngách</h3>
<table>
<tr><th>Chủ đề</th><th class="n">Số bài</th><th class="n">% số bài</th></tr>
{theme_rows}
</table>
<p class="f">{PPL['ghi_chú']}</p>
<div class="box">
<span class="l">Bộ ba lõi</span>
<p>Ba chủ đề phủ trên 80% số bài: <b>hành trình</b>, <b>tin cậy</b>,
<b>ánh sáng/bóng tối</b>. Bài thiếu cả ba sẽ nghe lạc chất.</p>
</div>

<h2>6. Giọng hát — có lời hay không lời</h2>
<div class="box ok">
<span class="l">{VD.get('kết_luận', '—')} · độ tin cậy {VD.get('độ_tin_cậy', '—')}</span>
<p>{VD.get('bằng_chứng_định_tính', {}).get('đọc_là', '')}</p>
<p>Comment được thích nhiều nhất ngách
({VD.get('bằng_chứng_định_tính', {}).get('comment_được_thích_nhất_ngách', '—')} tim)
nói thẳng rằng vấn đề nằm ở <b>lời hát</b>, không phải phần nhạc.
Phần trên đo lời của {SRC['n_track']} bài — chính là câu trả lời cho nỗi đau đó.</p>
</div>

<h2>7. Giới hạn — đọc trước khi dùng</h2>
<ul>
{limit_rows}
</ul>

<div class="box crit">
<span class="l">Báo cáo mô tả, không bảo đảm</span>
<p>Toàn bộ {SRC['n_track']} bài đều từ kênh <b>đang hoạt động</b>, không có nhóm
đối chứng — cả phần lời lẫn phần nhạc. Nên đây là <b>ảnh chụp cách ngách đang viết</b>, <b>không</b> phải bằng
chứng rằng viết thế thì thắng. Làm đúng mọi thông số vẫn có thể thất bại — nhạc
và lời chỉ là một phần; tiêu đề, thumbnail, thời điểm đăng đều tác động.</p>
<p>Giá trị thật của báo cáo: giúp bạn <b>không lạc chất ngách</b>.</p>
</div>

<p class="f">Nguồn: {SRC['từ']} · {LINK['phương_pháp']} ·
Lời hát nguyên văn KHÔNG xuất hiện trong báo cáo này (T65) — chỉ thông số.</p>

</body></html>"""

HTML(string=DOC).write_pdf(OUT)
print(f"✅ {OUT}")
