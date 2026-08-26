"""Sinh PDF cho KIẾN TRÚC HỆ THỐNG — framework/00_system/01_ARCHITECTURE.md.

CHẠY: python3 pipeline/report/build_arch_pdf.py [niche_path]

VÌ SAO KHÔNG DÙNG MERMAID: file nguồn có 10 khối ```mermaid```. Không có mmdc
trong máy, và kể cả có thì nó xuất PNG → in ra mờ. Thay vào đó dựng lại bằng
**Graphviz → SVG**, WeasyPrint nhúng SVG thành nét vector: chữ trong sơ đồ vẫn
CHỌN và TÌM KIẾM được trong PDF, phóng to không vỡ.

ĐÁNH ĐỔI ĐÃ BIẾT: sơ đồ được viết lại bằng tay ở đây, nên khi sửa mermaid trong
file .md phải sửa cả đây. Bộ kiểm ở cuối file dò lệch để không quên (xem T43).

Tài liệu KHUNG CHUNG — không thuộc ngách nào. Nhưng đọc scores.json để hiện
đúng trạng thái ngách mẫu, theo quy tắc "đọc từ file, không gõ lại số" (T27).
"""
import base64, json, re, sys, warnings
from pathlib import Path
import graphviz
from weasyprint import HTML
warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
SRC  = ROOT/"framework/00_system/01_ARCHITECTURE.md"
N    = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--")
            else "niches/christian-blues")
if not N.is_absolute():
    N = ROOT/N

# ── Bảng màu — trùng với các báo cáo khác trong 99_report/ ────────────────
INK, MUTED, RULE = "#1A1614", "#6B615A", "#E2DAD1"
ACC, WARN, BAD, GOOD = "#8C3A2B", "#E65100", "#9B2C2C", "#2F6B4F"
FONT = "DejaVu Sans"


def vn(x, nd=None):
    s = f"{x:.{nd}f}" if nd is not None else f"{x:g}"
    return s.replace(".", ",")


# ══════════════════════════════════════════════════════════════════════════
# SƠ ĐỒ · dựng lại 10 khối mermaid bằng Graphviz
# ══════════════════════════════════════════════════════════════════════════
def _g(rankdir="TB", **kw):
    g = graphviz.Digraph(format="svg")
    g.attr(rankdir=rankdir, bgcolor="transparent", pad="0.12",
           nodesep=kw.pop("nodesep", "0.30"), ranksep=kw.pop("ranksep", "0.38"), **kw)
    g.attr("node", shape="box", style="filled,rounded", fillcolor="#F7F4F0",
           color=RULE, fontname=FONT, fontsize="9", fontcolor=INK,
           margin="0.11,0.07", penwidth="0.9")
    g.attr("edge", fontname=FONT, fontsize="7.5", color="#9A8E85",
           fontcolor=MUTED, penwidth="0.9", arrowsize="0.6")
    return g


def svg(g, width="100%"):
    """Graphviz → thẻ <img> data-URI. WeasyPrint vẽ SVG thành vector."""
    s = g.pipe().decode("utf-8")
    s = re.sub(r'<svg width="\d+pt" height="\d+pt"', "<svg", s, count=1)
    b = base64.b64encode(s.encode()).decode()
    return (f'<div class="dg"><img src="data:image/svg+xml;base64,{b}" '
            f'style="width:{width}"></div>')


def d_layers():                                    # §1.2 bốn tầng
    g = _g("LR", nodesep="0.22")
    for i, (n, t, s) in enumerate([
            ("F", "TẦNG 1 · FACT", "số liệu thô\nkhông diễn giải"),
            ("M", "TẦNG 2 · METRIC", "chỉ số chuẩn hóa\ncó công thức"),
            ("S", "TẦNG 3 · SCORE", "điểm 0–5\nngưỡng cố định"),
            ("I", "TẦNG 4 · INSIGHT", "diễn giải\nngười/AI viết")]):
        g.node(n, f"{t}\n{s}", fillcolor=["#ECEFF1", "#E3F2FD", "#FFF3E0", "#E8F5E9"][i])
    g.edge("F", "M"); g.edge("M", "S"); g.edge("S", "I")
    g.edge("I", "S", label="CẤM sửa ngược", style="dashed", color=BAD,
           fontcolor=BAD, constraint="false")
    return svg(g, "96%")


def d_workflow():                                  # §2 workflow 10 bước
    g = _g("TB", ranksep="0.30", nodesep="0.26")
    nd = g.node
    nd("S0", "STEP_00 · SETUP\nĐịnh nghĩa ngách, kiểm kê")
    nd("S1", "STEP_01 · NỀN MÓNG\nChuẩn hóa, làm giàu, lọc")
    nd("S2", "STEP_02 · QUY MÔ & ĐỘNG LƯỢNG\nNgách lên hay xuống?")
    nd("GATE", "CỔNG QUYẾT ĐỊNH\nNgách còn đáng vào?", shape="diamond",
       fillcolor="#FFF3E0", color=WARN, penwidth="1.6", style="filled")
    nd("STOP", "DỪNG\nGhi lý do, lưu hồ sơ", fillcolor="#FFEBEE", color=BAD)
    nd("S3", "STEP_03 · ĐỐI THỦ\nAi thắng? Còn cửa?")
    nd("S4", "STEP_04 · SÀNG LỌC ĐỐI CHỨNG\nĐặc trưng nào KHÔNG phân biệt?")
    nd("S5", "STEP_05 · KHÁN GIẢ\nKhách là ai?")
    nd("S6", "STEP_06 · TỪ KHÓA\nTruyền tải thế nào?")
    nd("S7", "STEP_07 · KIẾM TIỀN\nRa tiền không?")
    nd("S8", "STEP_08 · TỔNG HỢP\nVào hay không?", fillcolor="#E8F5E9", color=GOOD, penwidth="1.4")
    nd("S10", "STEP_10 · PLAYBOOK — CÔNG THỨC THẮNG\nVào thì LÀM GÌ?",
       fillcolor="#E8F5E9", color=GOOD, penwidth="1.4")
    nd("WF", "CHANNEL_PLAYBOOK.json\n→ workflow sản xuất tự động",
       fillcolor="#E8F5E9", color=GOOD, penwidth="1.6")
    for n, l in [("S4B", "STEP_04b · KIỂM ĐỊNH ẢNH\nẢnh có phân biệt thắng/thua?"),
                 ("S4G", "STEP_04g · BRIEF ẢNH\nNhóm top dựng ảnh thế nào?"),
                 ("S4H", "STEP_04h · BRIEF NHẠC\nNhóm top dựng nhạc thế nào?")]:
        nd(n, l, style="filled,rounded,dashed", fillcolor="#FAF7F4")
    nd("OUT", "BRIEF tái tạo\n(không vào điểm số)", style="filled,rounded,dashed",
       fillcolor="#F3E5F5", color="#6A1B9A")

    for a, b in [("S0", "S1"), ("S1", "S2"), ("S2", "GATE"), ("S3", "S4"),
                 ("S4", "S5"), ("S4", "S6"), ("S3", "S7"),
                 ("S5", "S8"), ("S6", "S8"), ("S7", "S8"), ("S8", "S10"), ("S10", "WF")]:
        g.edge(a, b)
    g.edge("GATE", "STOP", label="Không", color=BAD, fontcolor=BAD)
    g.edge("GATE", "S3", label="Có", color=GOOD, fontcolor=GOOD)
    for a, b in [("S4", "S4B"), ("S4", "S4H")]:
        g.edge(a, b, style="dashed")
    g.edge("S4B", "S4G", style="dashed")
    g.edge("S4G", "OUT", style="dashed"); g.edge("S4G", "S10", style="dashed")
    g.edge("S4H", "S10", style="dashed")
    return svg(g, "100%")


def d_twoq():                                      # §2.4 hai loại câu hỏi
    g = _g("LR", nodesep="0.30")
    g.node("Q", "Người dùng\nmuốn gì?", shape="diamond", fillcolor="#FFF3E0",
           color=WARN, penwidth="1.4")
    g.node("A", "KIỂM ĐỊNH\n———\nso nhóm thắng vs thua\nkiểm 3 lớp chống Simpson\nngưỡng p < 0,01 và δ ≥ 0,30",
           fillcolor="#E3F2FD", color="#1565C0")
    g.node("B", "BRIEF\n———\nmô tả nhóm top\ntrung vị + khoảng tứ phân vị\nkhông cần đối chứng",
           fillcolor="#F3E5F5", color="#6A1B9A")
    g.node("A2", "Kết quả thường là\nKHÔNG CHỨNG MINH ĐƯỢC", fillcolor="#FFEBEE", color=BAD)
    g.node("B2", "Kết quả là\nCÔNG THỨC SAO CHÉP ĐƯỢC", fillcolor="#E8F5E9", color=GOOD)
    g.edge("Q", "A", label="Làm thế này\nCÓ THẮNG không?")
    g.edge("Q", "B", label="Nhóm thắng\nĐANG LÀM thế nào?")
    g.edge("A", "A2"); g.edge("B", "B2")
    return svg(g, "100%")


def d_dataflow(width="100%"):                       # §3 luồng dữ liệu
    g = _g("TB", ranksep="0.34")
    g.node("RAW", "00_input/raw/*.xlsx\nBẤT BIẾN", fillcolor="#ECEFF1", penwidth="1.4")
    with g.subgraph(name="cluster_a0") as c:
        c.attr(label="A0 · DATA ENGINEER (STEP_01)", fontname=FONT, fontsize="8",
               fontcolor=MUTED, color=RULE, style="rounded")
        for n, l in [("T1", "normalize\nxlsx → parquet"), ("T2", "enrich\n+age_days +vpd"),
                     ("T3", "select\náp 4 rổ + 3 tầng"), ("T4", "validate\n5 kiểm tra")]:
            c.node(n, l)
    g.node("P4", "selected_videos.parquet\n~13% tổng số", fillcolor="#F2EEE8")
    g.node("P5", "selected_comments.parquet\n~5% tổng số", fillcolor="#F2EEE8")
    g.node("PX", "channels · videos · comments\n.parquet", fillcolor="#F2EEE8")
    with g.subgraph(name="cluster_an") as c:
        c.attr(label="TẦNG PHÂN TÍCH", fontname=FONT, fontsize="8",
               fontcolor=MUTED, color=RULE, style="rounded")
        c.attr(rank="same")
        for n, l in [("A1", "A1\nQuy mô"), ("A2", "A2\nĐối thủ"), ("A3", "A3\nOutlier"),
                     ("A4", "A4\nKhán giả"), ("A5", "A5\nTừ khóa"), ("A6", "A6\nKiếm tiền")]:
            c.node(n, l)
    g.node("MET", "_state/metrics.json\nchỉ số thô, chưa chấm", fillcolor="#E3F2FD")
    g.node("SCO", "_state/scores.json\nđiểm + truy vết", fillcolor="#FFF3E0", penwidth="1.4")
    g.node("REP", "99_report/*.pdf", fillcolor="#E8F5E9", color=GOOD)
    g.edge("RAW", "T1"); g.edge("T1", "T2"); g.edge("T2", "T3"); g.edge("T3", "T4")
    g.edge("T4", "PX"); g.edge("T4", "P4"); g.edge("T4", "P5")
    for a in ["A1", "A2", "A6"]: g.edge("PX", a)
    for a in ["A2", "A3", "A5"]: g.edge("P4", a)
    g.edge("P5", "A4")
    for a in ["A1", "A2", "A3", "A4", "A5", "A6"]: g.edge(a, "MET")
    g.edge("MET", "SCO", label="scoring_engine")
    g.edge("SCO", "REP")
    return svg(g, width)


def d_ritual():                                    # §4.1 nghi thức khởi động
    g = _g("LR", nodesep="0.18", ranksep="0.30")
    steps = [("R1", "1 · README.md\nhiểu hệ thống"), ("R2", "2 · 01_agents/<mã>.md\nhiểu vai của mình"),
             ("R3", "3 · NICHE_BRIEF.md\nhiểu ngách"),
             ("R4", "4 · PROGRESS.md\nbiết bước trước ra gì"),
             ("R5", "5 · output bước phụ thuộc\ntheo FILE_CONTRACTS"),
             ("R6", "6 · 02_steps/STEP_<n>.md\nlàm theo runbook")]
    for n, l in steps:
        g.node(n, l, fillcolor="#FFF3E0" if n == "R4" else "#F7F4F0",
               penwidth="1.6" if n == "R4" else "0.9",
               color=WARN if n == "R4" else RULE)
    g.node("WORK", "THỰC THI", fillcolor="#E3F2FD", penwidth="1.4")
    for n, l in [("W1", "7 · ghi output\nđúng đường dẫn"), ("W2", "8 · ghi metric\nvào metrics.json"),
                 ("W3", "9 · cập nhật\nPROGRESS.md")]:
        g.node(n, l, fillcolor="#E8F5E9")
    seq = [s[0] for s in steps] + ["WORK", "W1", "W2", "W3"]
    for a, b in zip(seq, seq[1:]): g.edge(a, b)
    return svg(g, "100%")


def d_a4():                                        # §4.3 ví dụ A4
    g = _g("LR", nodesep="0.20")
    with g.subgraph(name="cluster_in") as c:
        c.attr(label="A4 ĐỌC", fontname=FONT, fontsize="8", fontcolor=MUTED,
               color=RULE, style="rounded")
        c.node("I1", "selected_comments.parquet\n~6.800 comment")
        c.node("I2", "04_outlier/ · biết video nào thắng")
        c.node("I3", "03_competitor/ · biết kênh nào là AI")
    g.node("A4", "A4 · AUDIENCE\nRESEARCHER", fillcolor="#E3F2FD", penwidth="1.4")
    with g.subgraph(name="cluster_out") as c:
        c.attr(label="A4 GHI", fontname=FONT, fontsize="8", fontcolor=MUTED,
               color=RULE, style="rounded")
        c.node("O1", "05_audience/01_personas.md", fillcolor="#E8F5E9")
        c.node("O2", "05_audience/02_voice_of_customer.md", fillcolor="#E8F5E9")
        c.node("O3", "metrics.json · +audience.*", fillcolor="#E8F5E9")
    for i in ["I1", "I2", "I3"]: g.edge(i, "A4")
    for o in ["O1", "O2", "O3"]: g.edge("A4", o)
    return svg(g, "100%")


def d_tiers():                                     # §6.1 phân tầng công cụ
    g = _g("LR", nodesep="0.24")
    g.node("D", "Toàn bộ\ndữ liệu", fillcolor="#ECEFF1")
    for n, l, f in [("T1", "TẦNG 1 · PYTHON\n100% dữ liệu\nđếm, thống kê, tương quan", "#E8F5E9"),
                    ("T2", "TẦNG 2 · LỌC\nquy tắc cứng\n7.193 → 965", "#E3F2FD"),
                    ("T3", "TẦNG 3 · LLM NHẸ\nphân loại hàng loạt\ngắn nhãn 6.800 comment", "#FFF3E0"),
                    ("T4", "TẦNG 4 · LLM MẠNH\n~300 mẫu tinh hoa\ntổng hợp insight", "#F3E5F5")]:
        g.node(n, l, fillcolor=f)
    for a, b in [("D", "T1"), ("T1", "T2"), ("T2", "T3"), ("T3", "T4")]: g.edge(a, b)
    return svg(g, "100%")


def d_pipeline():                                  # §8 pipeline code
    g = _g("TB", ranksep="0.32")
    g.node("NRM", "extract/normalize.py")
    g.node("ENR", "transform/enrich.py")
    g.node("FLT", "transform/apply_filters.py")
    for n, l in [("A2", "step02_market"), ("A3", "step03_competitor"),
                 ("A4", "step04_outlier"), ("A5", "step05_audience"),
                 ("A6", "step06_keyword"), ("A7", "step07_monetization"),
                 ("A8", "step08_synthesis")]:
        g.node(n, l)
    with g.subgraph(name="cluster_th") as c:
        c.attr(label="nhánh ảnh + nhạc (tùy chọn)", fontname=FONT, fontsize="8",
               fontcolor=MUTED, color=RULE, style="rounded,dashed")
        for n, l in [("T1", "step04c_thumbnail_full"), ("T2", "step04b_thumbnail"),
                     ("T3", "step04d_thumbnail_top"), ("T4", "step04g_brief_extract"),
                     ("T5", "step04h_audio")]:
            c.node(n, l, style="filled,rounded,dashed", fillcolor="#FAF7F4")
    g.node("SE", "scoring_engine.py\nfile DUY NHẤT ghi scores.json",
           fillcolor="#FFF3E0", color=WARN, penwidth="1.8")
    g.node("VR", "verify_rubric.py", fillcolor="#E8F5E9", color=GOOD)
    g.node("BR", "report/build_report*.py", fillcolor="#E8F5E9")
    g.edge("NRM", "ENR"); g.edge("ENR", "FLT"); g.edge("FLT", "A2")
    g.edge("A2", "A3"); g.edge("A3", "A4")
    g.edge("A4", "A5"); g.edge("A4", "A6"); g.edge("A3", "A7")
    for a in ["A5", "A6", "A7"]: g.edge(a, "A8")
    g.edge("A8", "SE"); g.edge("SE", "VR"); g.edge("SE", "BR")
    g.edge("FLT", "T1", style="dashed"); g.edge("T1", "T2"); g.edge("T2", "T3")
    g.edge("T1", "T4"); g.edge("A4", "T5", style="dashed")
    for t in ["T3", "T4", "T5"]: g.edge(t, "BR", style="dashed")
    return svg(g, "100%")


def d_docs():                                      # §9 quan hệ tài liệu
    g = _g("TB", ranksep="0.32")
    g.node("RM", "README.md\nđiểm vào", fillcolor="#E8F5E9", color=GOOD)
    g.node("ARCH", "01_ARCHITECTURE.md\nbạn đang đọc", fillcolor="#E3F2FD",
           color="#1565C0", penwidth="1.8")
    for n, l in [("DM", "02_DATA_MODEL"), ("RUB", "03_SCORING_RUBRIC"),
                 ("SEL", "04_SELECTION_LOGIC"), ("FC", "05_FILE_CONTRACTS")]:
        g.node(n, l)
    g.node("AG", "01_agents/A0…A7"); g.node("ST", "02_steps/STEP_00…10")
    g.node("NB", "NICHE_BRIEF.md", fillcolor="#F2EEE8")
    g.node("PR", "PROGRESS.md", fillcolor="#F2EEE8")
    g.edge("RM", "ARCH")
    for n in ["DM", "RUB", "SEL", "FC"]: g.edge("ARCH", n)
    g.edge("FC", "AG"); g.edge("AG", "ST")
    g.edge("ST", "NB", label="đọc cấu hình"); g.edge("ST", "PR", label="cập nhật")
    return svg(g, "100%")


# ══════════════════════════════════════════════════════════════════════════
# SỐ LIỆU SỐNG · đọc từ file, không gõ lại (T27)
# ══════════════════════════════════════════════════════════════════════════
try:
    SC = json.load(open(N/"_state/scores.json"))
    EX_NICHE, EX_SCORE = SC.get("niche", "—"), vn(SC["total_score"], 2)
    EX_DATE = SC.get("scored_at", "—")
except Exception:
    EX_NICHE, EX_SCORE, EX_DATE = "—", "—", "—"

try:
    MT = json.load(open(N/"_state/metrics.json"))
    M24 = MT.get("momentum", {}).get("M2_4_demand_supply_gap")
    M24 = vn(M24, 3) if isinstance(M24, (int, float)) else "—"
except Exception:
    M24 = "—"

# Đếm bước/agent/script THẬT thay vì tin con số trong tiêu đề tài liệu.
# BƯỚC CHÍNH = STEP_NN (hai chữ số, không hậu tố). STEP_04b/04h là NHÁNH
# TÙY CHỌN — chính file runbook của chúng tự khai "bước tùy chọn, không ảnh
# hưởng điểm số". Đếm gộp thì ra 12 và mâu thuẫn với tiêu đề "10 bước" (T43).
_steps = list((ROOT/"framework/02_steps").glob("STEP_*.md"))
N_STEPS  = len([f for f in _steps if re.match(r"STEP_\d\d_", f.name)])
N_BRANCH = len(_steps) - N_STEPS
N_AGENTS = len(list((ROOT/"framework/01_agents").glob("A[0-9]*.md")))
N_SCRIPT = len(list((ROOT/"pipeline").rglob("*.py"))) - len(
           list((ROOT/"pipeline").rglob("_archive/*.py")))

CSS = f"""
@page {{ size:A4; margin:17mm 15mm 20mm;
 @bottom-center {{ content counter(page) " / " counter(pages);
  font-family:"{FONT}";font-size:8pt;color:#9A8E85; }} }}
@page:first {{ @bottom-center {{ content:""; }} }}
body {{ font-family:"{FONT}",sans-serif;font-size:9.5pt;line-height:1.55;color:{INK}; }}
h1 {{ font-size:23pt;margin:0 0 6pt;letter-spacing:-.4pt; }}
h2 {{ font-size:13pt;margin:20pt 0 7pt;padding-bottom:4pt;
 border-bottom:1.5pt solid {INK};page-break-after:avoid; }}
h3 {{ font-size:10.5pt;margin:14pt 0 5pt;color:{ACC};page-break-after:avoid; }}
p {{ margin:6pt 0; }}
.sub {{ color:{MUTED};font-size:10pt;margin:0 0 10pt; }}
.meta {{ font-size:8pt;color:#7A6F68;border-top:.6pt solid {RULE};
 border-bottom:.6pt solid {RULE};padding:6pt 0;margin-bottom:14pt; }}
table {{ border-collapse:collapse;width:100%;font-size:8.5pt;margin:8pt 0;page-break-inside:avoid; }}
th {{ background:#F2EEE8;text-align:left;padding:5pt 7pt;font-size:7.5pt;
 text-transform:uppercase;letter-spacing:.4pt;color:#5A514B;border-bottom:1pt solid #CFC4B8; }}
td {{ padding:5pt 7pt;border-bottom:.6pt solid #EDE7E0;vertical-align:top; }}
/* NGUYÊN TẮC CĂN LỀ — giống mọi báo cáo khác:
   .n số so sánh được theo cột → PHẢI · .c nhãn ngắn → GIỮA · chữ → TRÁI */
td.n {{ text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap; }}
td.c, th.c {{ text-align:center;white-space:nowrap; }}
th.n {{ text-align:right; }}
tr.hi {{ background:#F4E6E2; }}
.ok {{ color:{GOOD};font-weight:bold; }} .no {{ color:{BAD};font-weight:bold; }}
.box {{ border-left:2.5pt solid {ACC};background:#F9F4F2;padding:8pt 11pt;
 margin:11pt 0;page-break-inside:avoid; }}
.box.crit {{ border-left-color:{BAD};background:#FBEEEE; }}
.box.ok {{ border-left-color:{GOOD};background:#EFF5F1; }}
.box .l {{ font-size:7.5pt;text-transform:uppercase;letter-spacing:.7pt;
 font-weight:bold;color:{ACC};display:block;margin-bottom:4pt; }}
.box.crit .l {{ color:{BAD}; }} .box.ok .l {{ color:{GOOD}; }}
.box p {{ margin:0 0 5pt;font-size:9pt; }} .box p:last-child {{ margin-bottom:0; }}
.kpi {{ display:flex;gap:7pt;margin:11pt 0; }}
.kpi div {{ flex:1;border:.6pt solid {RULE};padding:8pt 9pt; }}
.kpi .k {{ font-size:6.8pt;text-transform:uppercase;letter-spacing:.5pt;color:#7A6F68;margin-bottom:4pt; }}
.kpi .v {{ font-size:17pt;font-weight:bold;letter-spacing:-.3pt; }}
.kpi .c {{ font-size:7pt;color:#7A6F68;margin-top:3pt;line-height:1.3; }}
code {{ background:#F2EEE8;padding:.5pt 3pt;font-size:8.5pt; }}
pre {{ background:#F7F4F0;border:.6pt solid {RULE};padding:7pt 9pt;font-size:7.8pt;
 line-height:1.45;margin:7pt 0;white-space:pre-wrap;page-break-inside:avoid; }}
.dg {{ margin:10pt 0 12pt;text-align:center;page-break-inside:avoid; }}
.cap {{ font-size:7.5pt;color:#7A6F68;text-align:center;margin:-6pt 0 12pt; }}
.pb {{ page-break-before:always; }}
.keep {{ page-break-inside:avoid; }}
ul {{ margin:6pt 0;padding-left:15pt; }} li {{ margin:3pt 0; }}
.toc td {{ border-bottom:.6pt dotted {RULE}; }}
.toc td.c {{ color:{MUTED}; }}
"""

DOC = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>

<h1>Kiến trúc hệ thống &amp; workflow</h1>
<p class="sub">Tài liệu thiết kế tổng &mdash; đọc file này trước khi chạy bất kỳ bước nào</p>
<div class="meta">
Tài liệu KHUNG CHUNG &nbsp;•&nbsp; áp dụng cho mọi ngách &nbsp;•&nbsp; phiên bản v2.0
&nbsp;•&nbsp; Nguồn: <code>framework/00_system/01_ARCHITECTURE.md</code>
&nbsp;•&nbsp; Ví dụ minh họa: ngách <b>{EX_NICHE}</b> ({EX_SCORE}/20, chấm {EX_DATE})
</div>

<div class="kpi">
<div><div class="k">Bước quy trình</div><div class="v">{N_STEPS}</div>
<div class="c">+{N_BRANCH} nhánh tùy chọn (04b · 04h)</div></div>
<div><div class="k">Agent chuyên trách</div><div class="v">{N_AGENTS}</div>
<div class="c">A0 → A7, mỗi agent một vai</div></div>
<div><div class="k">Script pipeline</div><div class="v">{N_SCRIPT}</div>
<div class="c">chạy được bằng một lệnh</div></div>
<div><div class="k">Tầng xử lý</div><div class="v">4</div>
<div class="c">fact → metric → score → insight</div></div>
</div>

<div class="box ok">
<span class="l">Đọc nhanh trong 30 giây</span>
<p><b>Hệ thống này làm gì:</b> biến dữ liệu YouTube thô của một ngách thành
<b>một quyết định có bằng chứng</b> &mdash; vào hay không, và nếu vào thì làm gì.</p>
<p><b>Ý tưởng cốt lõi:</b> tách <b>khung</b> (rubric, logic lọc, runbook) khỏi
<b>dữ liệu</b> (từng ngách). Ngách thứ hai chỉ tốn công thu thập dữ liệu, không
tốn công thiết kế lại &mdash; và vì cùng rubric nên <b>so sánh được trực tiếp</b>.</p>
<p><b>Ràng buộc quan trọng nhất:</b> diễn giải <b>không được</b> sửa ngược điểm số.
Muốn đổi điểm thì đổi <i>ngưỡng</i> rồi chạy lại tất cả. Đây chính là thứ bảng
Excel thủ công không làm được, và là lý do nó không nhất quán.</p>
</div>

<h3 style="margin-top:16pt">Nội dung</h3>
<table class="toc"><tbody>
<tr><td class="c">1</td><td>Triết lý thiết kế &mdash; tách khung khỏi dữ liệu, bốn tầng xử lý</td></tr>
<tr><td class="c">2</td><td>Workflow tổng &mdash; {N_STEPS} bước, cổng quyết định, hai loại câu hỏi</td></tr>
<tr><td class="c">3</td><td>Workflow dữ liệu &mdash; từ file thô đến báo cáo</td></tr>
<tr><td class="c">4</td><td>Cách agent đọc file và liên kết thông tin</td></tr>
<tr><td class="c">5</td><td>Tám agent &mdash; bảng tổng</td></tr>
<tr><td class="c">6</td><td>Nguyên tắc phân tích dữ liệu</td></tr>
<tr><td class="c">7</td><td>Quản lý trạng thái</td></tr>
<tr><td class="c">8</td><td>Pipeline code &mdash; script nào chạy lúc nào</td></tr>
<tr><td class="c">9</td><td>Sơ đồ quan hệ tài liệu</td></tr>
<tr><td class="c">10</td><td>Hệ thống này <b>không</b> làm gì</td></tr>
</tbody></table>

<h2 class="pb">1. Triết lý thiết kế</h2>

<h3>1.1 Tách khung khỏi dữ liệu</h3>
<table>
<thead><tr><th style="width:50%"><code>framework/</code> · KHUNG CHUNG</th>
<th><code>niches/</code> · DỮ LIỆU RIÊNG</th></tr></thead>
<tbody>
<tr><td>Rubric chấm điểm &mdash; ngưỡng cố định</td><td><code>christian-blues/</code></td></tr>
<tr><td>Logic lọc &mdash; 4 rổ, 3 tầng</td><td><code>ngách kế tiếp/</code></td></tr>
<tr><td>Đặc tả {N_AGENTS} agent</td><td><code>ngách sau nữa/</code></td></tr>
<tr><td>{N_STEPS} runbook từng bước</td><td>&hellip;</td></tr>
</tbody></table>
<p><b>Hệ quả:</b> ngách thứ hai chỉ tốn công <b>thu thập dữ liệu + chạy quy trình</b>,
không tốn công thiết kế lại. Và vì cùng rubric, hai ngách <b>so sánh được trực tiếp
với nhau</b>.</p>

<h3>1.2 Bốn tầng xử lý &mdash; không được trộn</h3>
{d_layers()}
<p>Tầng 4 <b>không được</b> sửa tầng 3. Muốn đổi điểm → đổi <i>ngưỡng</i> ở tầng 3
→ chạy lại toàn bộ. Đây là điều bảng Excel thủ công không làm được, và là lý do
nó không nhất quán.</p>

<h2 class="pb">2. Workflow tổng &mdash; {N_STEPS} bước</h2>
{d_workflow()}
<p class="cap">Nét đứt = nhánh tùy chọn. STEP_04b/04g chỉ chạy khi có file ảnh,
STEP_04h chỉ chạy khi có file DSP âm thanh. Cả hai <b>không tác động điểm số</b>
&mdash; chúng trả lời câu hỏi khác (xem mục 2.4).</p>

<h3>2.1 Vì sao có CỔNG QUYẾT ĐỊNH sau STEP_02</h3>
<p>Đây là điểm khác biệt lớn nhất so với quy trình tuyến tính thông thường.</p>
<p>STEP_02 trả lời câu hỏi <b>sống còn</b>: <i>cầu có tăng nhanh hơn cung không?</i>
Nếu <b>không</b> → mọi phân tích sau đều là <b>tối ưu hóa một con tàu đang chìm</b>.</p>
<table>
<thead><tr><th>Kết quả STEP_02</th><th class="c">Vùng</th><th>Hành động</th></tr></thead>
<tbody>
<tr><td><code>M2.4 &ge; 1,0</code> &mdash; cầu &ge; cung</td><td class="c ok">ĐI TIẾP</td>
<td>Đi tiếp bình thường</td></tr>
<tr><td><code>M2.4</code> trong <code>[0,5 &ndash; 1,0)</code></td>
<td class="c" style="color:{WARN};font-weight:bold">THẬN TRỌNG</td>
<td>Đi tiếp nhưng <b>đổi câu hỏi</b>: không hỏi &ldquo;vào hay không&rdquo;
mà hỏi &ldquo;vào bằng khác biệt gì&rdquo;</td></tr>
<tr><td><code>M2.4 &lt; 0,5</code></td><td class="c no">DỪNG</td>
<td>Dừng, trừ khi có lý do chiến lược khác</td></tr>
</tbody></table>

<div class="box crit">
<span class="l">Ví dụ thật &mdash; và bài học L1</span>
<p>Khảo sát sơ bộ Christian Blues báo <code>M2.4 &asymp; 0,35</code> → rơi vào vùng
<b>dừng</b>. Nhưng con số đó <b>SAI</b>: nó so cửa sổ 0&ndash;90 ngày (chỉ 36% video
đã chín) với cửa sổ 90&ndash;180 ngày (100% đã chín).</p>
<p>Tính lại trên hai cửa sổ <b>đều chín</b> → <code>M2.4 = {M24}</code>, ngách khỏe.
<b>Cổng quyết định suýt loại nhầm một ngách tốt.</b></p>
</div>

<h3>2.2 Vì sao STEP_05 và STEP_06 chạy sau STEP_04</h3>
<p>Không phải thứ tự tùy tiện:</p>
<ul>
<li><b>STEP_04 chọn ra video thắng</b> → STEP_05 chỉ đọc comment <b>của những video
đó</b> (không phải toàn bộ 145k)</li>
<li><b>STEP_04 loại bỏ giả thuyết sai</b> → STEP_06 không phí công phân tích từ khóa
theo hướng đã bị bác bỏ</li>
</ul>
<p>Đảo thứ tự sẽ phải quét toàn bộ dữ liệu → vi phạm nguyên tắc chọn lọc.</p>

<div class="box crit">
<span class="l">STEP_04 KHÔNG &ldquo;xác định công thức&rdquo; &mdash; bài học T29</span>
<p>Nó chỉ <b>loại trừ</b> &mdash; kết quả điển hình <b>0/20 đặc trưng đứng vững</b>.
Công thức sản xuất là đầu ra của <b>STEP_10</b>, bước tổng hợp sau khi đã có 04b
(thumbnail thật), 05 (khán giả), 06 (từ khóa).</p>
<p>Đây từng là nguồn hiểu nhầm: bước tên <i>&ldquo;Công thức thắng&rdquo;</i> lại nằm
<b>trước</b> mọi phân tích hợp thành công thức. Đã đổi tên thành
<b>SÀNG LỌC ĐỐI CHỨNG</b>.</p>
</div>

<h3>2.3 Nhánh song song</h3>
<table>
<thead><tr><th>Chạy song song được</th><th>Vì sao</th></tr></thead>
<tbody>
<tr><td>STEP_05 ‖ STEP_06</td><td>Cùng đọc output STEP_04, không phụ thuộc nhau</td></tr>
<tr><td>STEP_07 ‖ (STEP_04→06)</td><td>Chỉ cần output STEP_03</td></tr>
<tr><td>STEP_04b/04g ‖ (STEP_05→07)</td><td>Nhánh ảnh độc lập, không tác động điểm số</td></tr>
<tr><td>STEP_04h ‖ (STEP_05→07)</td><td>Nhánh nhạc độc lập, chỉ cần <code>video_id</code></td></tr>
</tbody></table>

<h3 class="pb">2.4 Hai loại câu hỏi &mdash; quyết định phương pháp</h3>
<p class="cap" style="text-align:left;margin:0 0 8pt">Bài học đắt nhất của dự án.
Cùng một bộ dữ liệu, hai câu hỏi khác nhau đòi hai phương pháp khác hẳn.
Chọn nhầm thì làm đúng quy trình mà ra sai thứ người dùng cần.</p>
{d_twoq()}
<table>
<thead><tr><th style="width:22%"></th><th>KIỂM ĐỊNH (STEP_04, 04b)</th>
<th>BRIEF (STEP_04g, 04h)</th></tr></thead>
<tbody>
<tr><td><b>Câu hỏi</b></td><td>Đặc điểm X có gây ra thành công?</td>
<td>Nhóm thành công trông thế nào?</td></tr>
<tr><td><b>Cần đối chứng?</b></td><td class="no">Bắt buộc (rổ B4)</td><td>Không</td></tr>
<tr><td><b>Cần kiểm Simpson?</b></td><td class="no">Bắt buộc 3 lớp</td><td>Không</td></tr>
<tr><td><b>Nguồn</b></td><td>toàn bộ + rổ đối chứng</td><td>chỉ top 5%</td></tr>
<tr><td><b>Đầu ra</b></td><td>xác nhận / bác bỏ</td><td>trung vị + khoảng + prompt mẫu</td></tr>
<tr><td><b>Kết quả điển hình</b></td><td>0/12 xác nhận</td><td>công thức dùng được ngay</td></tr>
<tr><td><b>Dùng để</b></td><td>quyết định vào ngách</td><td>sản xuất hàng loạt</td></tr>
</tbody></table>
<div class="box">
<span class="l">Quy tắc</span>
<p>Hỏi người dùng cần <b>đầu ra</b> gì <i>trước khi</i> chọn phương pháp.
Cần &ldquo;tái tạo được&rdquo; → làm brief. Cần &ldquo;có nên tin không&rdquo; → làm kiểm định.</p>
<p>Hai cái <b>không thay thế nhau</b>, và brief <b>không được</b> trình bày như
bằng chứng nhân quả.</p>
</div>

<h2 class="pb">3. Workflow dữ liệu &mdash; từ file thô đến báo cáo</h2>
<div class="keep">
{d_dataflow(width="88%")}
<div class="box">
<span class="l">Điểm mấu chốt &mdash; quy tắc R2</span>
<p><code>metrics.json</code> và <code>scores.json</code> <b>tách riêng</b>. Agent phân
tích chỉ ghi vào <code>metrics.json</code> (số thô). Chỉ <code>scoring_engine</code>
mới ghi <code>scores.json</code>. Đây là cách chống &ldquo;tự chấm tự khen&rdquo;.</p>
</div>
</div>

<h2 class="pb">4. Cách agent đọc file và liên kết thông tin</h2>

<h3>4.1 Nghi thức khởi động &mdash; mọi agent đều làm</h3>
{d_ritual()}
<p><b>Bước 4 quan trọng nhất:</b> <code>PROGRESS.md</code> là <b>bộ nhớ chung</b>.
Agent không đọc nó sẽ làm lại việc đã có, hoặc dùng giả định sai.</p>

<h3>4.2 Ba cơ chế liên kết thông tin</h3>
<table>
<thead><tr><th>Cơ chế</th><th>Dùng khi</th><th>File</th></tr></thead>
<tbody>
<tr><td><b>Truyền qua file</b></td><td>Bước sau cần output bước trước</td>
<td><code>FILE_CONTRACTS.md</code> khai báo</td></tr>
<tr><td><b>Sổ chỉ số chung</b></td><td>Nhiều agent cùng góp số cho rubric</td>
<td><code>_state/metrics.json</code></td></tr>
<tr><td><b>Nhật ký tiến độ</b></td><td>Biết trạng thái toàn cục</td>
<td><code>PROGRESS.md</code></td></tr>
</tbody></table>

<h3>4.3 Ví dụ liên kết thật &mdash; A4 Audience Researcher</h3>
{d_a4()}
<p>A4 đọc output của A3 để biết <b>comment nào đáng đọc</b> &mdash; thay vì quét
145.150 comment. Đây là cách &ldquo;chọn lọc&rdquo; được thực thi ở <b>cấp workflow</b>,
không chỉ ở cấp lọc dữ liệu.</p>

<h2>5. Tám agent &mdash; bảng tổng</h2>
<table>
<thead><tr><th class="c">Mã</th><th>Tên</th><th class="c">Step</th><th>Đọc</th><th>Ghi</th></tr></thead>
<tbody>
<tr><td class="c"><b>A0</b></td><td>Data Engineer</td><td class="c">01</td>
<td><code>raw/*</code></td><td><code>processed/*.parquet</code></td></tr>
<tr><td class="c"><b>A1</b></td><td>Market Analyst</td><td class="c">02</td>
<td><code>channels</code>, <code>videos</code></td><td><code>02_market/</code></td></tr>
<tr><td class="c"><b>A2</b></td><td>Competitor Analyst</td><td class="c">03</td>
<td><code>channels</code>, <code>selected_videos</code></td><td><code>03_competitor/</code></td></tr>
<tr><td class="c"><b>A3</b></td><td>Outlier Miner</td><td class="c">04</td>
<td><code>selected_videos</code>, <code>thumbnails</code></td><td><code>04_outlier/</code></td></tr>
<tr><td class="c"><b>A4</b></td><td>Audience Researcher</td><td class="c">05</td>
<td><code>selected_comments</code>, A3 output</td><td><code>05_audience/</code></td></tr>
<tr><td class="c"><b>A5</b></td><td>Keyword Analyst</td><td class="c">06</td>
<td><code>selected_videos</code>, A3 output</td><td><code>06_keyword/</code></td></tr>
<tr><td class="c"><b>A6</b></td><td>Monetization Analyst</td><td class="c">07</td>
<td><code>channels</code>, A2 output</td><td><code>07_monetization/</code></td></tr>
<tr><td class="c"><b>A7</b></td><td>Synthesizer</td><td class="c">08</td>
<td>tất cả + <code>scores.json</code></td><td><code>99_report/</code></td></tr>
</tbody></table>
<p class="cap" style="text-align:left">Chi tiết từng agent: <code>framework/01_agents/</code></p>

<h2 class="pb">6. Nguyên tắc phân tích dữ liệu</h2>

<h3>6.1 Phân tầng công cụ &mdash; tiết kiệm chi phí</h3>
{d_tiers()}
<p><b>Quy tắc:</b> thống kê mô tả <b>không bao giờ</b> dùng LLM.
Chỉ dùng LLM cho việc <i>hiểu ngôn ngữ</i>.</p>

<h3>6.2 Sáu quy tắc phân tích bắt buộc</h3>
<table>
<thead><tr><th class="c">#</th><th>Quy tắc</th><th>Chống lỗi gì</th></tr></thead>
<tbody>
<tr><td class="c"><b>D1</b></td><td>Dùng <b>trung vị</b>, không dùng trung bình</td>
<td>View phân bố đuôi dài</td></tr>
<tr><td class="c"><b>D2</b></td><td><b>Chuẩn hóa theo chính kênh</b> trước khi so sánh</td>
<td>Kênh to video nào cũng nhiều view</td></tr>
<tr><td class="c"><b>D3</b></td><td>Chuẩn hóa theo <b>tuổi video</b> (<code>vpd</code>)</td>
<td>Video cũ tích view lâu hơn</td></tr>
<tr><td class="c"><b>D4</b></td><td>Luôn có <b>nhóm đối chứng</b></td><td>Survivorship bias</td></tr>
<tr><td class="c"><b>D5</b></td><td>Ghi <b>giả thuyết trước</b> khi chạy</td><td>Confirmation bias</td></tr>
<tr><td class="c"><b>D6</b></td><td>Báo cáo cả <b>bằng chứng phản bác</b></td><td>Thiên lệch xác nhận</td></tr>
</tbody></table>

<h3>6.3 Ba câu hỏi phải trả lời trước mọi kết luận</h3>
<table>
<thead><tr><th class="c">#</th><th>Câu hỏi</th><th>Vì sao</th></tr></thead>
<tbody>
<tr><td class="c"><b>1</b></td><td><b>So với cái gì?</b></td>
<td>Không có mốc so sánh thì con số vô nghĩa</td></tr>
<tr><td class="c"><b>2</b></td><td><b>Có thể do nguyên nhân khác không?</b></td>
<td>Liệt kê ít nhất một cách giải thích ngược</td></tr>
<tr><td class="c"><b>3</b></td><td><b>Độ tin cậy bao nhiêu?</b></td>
<td>cao / vừa / thấp, kèm lý do</td></tr>
</tbody></table>

<h2 class="pb">7. Quản lý trạng thái</h2>

<h3>7.1 <code>PROGRESS.md</code> &mdash; bộ nhớ chung</h3>
<p>Mỗi bước xong phải cập nhật. Định dạng cố định:</p>
<pre>## STEP_02 · Quy mô &amp; động lượng
- Trạng thái: ✅ XONG | 🔄 ĐANG CHẠY | ⬜ CHƯA | 🛑 CHẶN
- Chạy lúc: 2026-08-15
- Output: 02_market/01_market_sizing.md
- Phát hiện chính: M2.4 = {M24} → cầu vượt cung
- Độ tin cậy: Vừa (chỉ 1 snapshot)
- Cảnh báo cho bước sau: cần tách kênh rác khỏi kênh tốt</pre>

<h3>7.2 <code>_state/metrics.json</code> &mdash; sổ chỉ số</h3>
<p>Mọi agent <b>thêm</b> vào, không ghi đè phần của agent khác:</p>
<pre>{{
  "niche": "{EX_NICHE}",
  "market":   {{ "M1_1_views_month": 10573212, "...": "..." }},
  "momentum": {{ "M2_4_demand_supply_gap": {M24.replace(",", ".")} }},
  "_meta": {{
    "M2_4_demand_supply_gap": {{
      "source":      "processed/videos.parquet",
      "computed_by": "A1",
      "confidence":  "medium",
      "caveat":      "chỉ 1 snapshot, suy từ published_at"
    }}
  }}
}}</pre>
<p>Trường <code>_meta</code> là <b>bắt buộc</b> &mdash; thực thi quy tắc R3 và R5.
Không có nó thì con số mất khả năng truy vết.</p>

<h2 class="pb">8. Pipeline code &mdash; script nào chạy lúc nào</h2>
<p class="cap" style="text-align:left;margin:0 0 8pt">Mục 2 mô tả <i>khái niệm</i>
các bước. Mục này map sang <b>file thật</b> để chạy.</p>
{d_pipeline()}

<h3>8.1 Chạy toàn bộ bằng một lệnh</h3>
<pre>bash pipeline/run_all.sh                          # nhánh lõi + PDF   (~50 giây)
bash pipeline/run_all.sh --with-thumbs            # thêm nhánh ảnh    (~15 phút)
bash pipeline/run_all.sh niches/&lt;ngách&gt; --no-pdf  # ngách khác, bỏ PDF</pre>

<h3>8.2 Quy ước đặt tên</h3>
<table>
<thead><tr><th>Tiền tố</th><th>Nghĩa</th></tr></thead>
<tbody>
<tr><td><code>stepNN_</code></td><td>tương ứng STEP_NN trong <code>02_steps/</code></td></tr>
<tr><td><code>stepNNx_</code></td><td>nhánh phụ của STEP_NN
(<code>04b</code>, <code>04c</code>, <code>04d</code>, <code>04g</code>, <code>04h</code>)</td></tr>
<tr><td><code>build_reportNN.py</code></td><td>sinh PDF cho STEP_NN</td></tr>
<tr><td><code>chartsNN.py</code></td><td>vẽ biểu đồ cho STEP_NN, chạy <b>trước</b>
<code>build_report</code></td></tr>
<tr><td><code>_archive/</code></td><td>script đã loại bỏ, <b>không</b> thuộc pipeline</td></tr>
</tbody></table>

<h3>8.3 Ba bất biến của code</h3>
<table>
<thead><tr><th class="c">#</th><th>Bất biến</th><th>Vì sao</th></tr></thead>
<tbody>
<tr><td class="c"><b>1</b></td><td>Chỉ <code>scoring_engine.py</code> được ghi
<code>scores.json</code></td><td>Chống &ldquo;tự chấm tự khen&rdquo; (R2)</td></tr>
<tr><td class="c"><b>2</b></td><td>Script phân tích không sửa
<code>00_input/raw/</code></td><td>Nguồn sự thật bất biến (R1)</td></tr>
<tr><td class="c"><b>3</b></td><td>Mọi script nhận <code>niche_path</code> làm tham số 1</td>
<td>Chạy được cho ngách bất kỳ</td></tr>
</tbody></table>

<h2 class="pb">9. Sơ đồ quan hệ tài liệu</h2>
{d_docs()}
<table>
<thead><tr><th>Đọc khi</th><th>File</th></tr></thead>
<tbody>
<tr><td>Lần đầu tiếp cận hệ thống</td><td><code>README.md</code> → file này</td></tr>
<tr><td>Cần hiểu schema dữ liệu</td><td><code>02_DATA_MODEL.md</code></td></tr>
<tr><td>Cần hiểu cách chấm điểm</td><td><code>03_SCORING_RUBRIC.md</code></td></tr>
<tr><td>Cần biết agent đọc/ghi gì</td><td><code>05_FILE_CONTRACTS.md</code></td></tr>
<tr><td>Sắp chạy một bước</td><td><code>02_steps/STEP_&lt;n&gt;.md</code></td></tr>
<tr><td>Muốn biết đang ở đâu</td><td><code>niches/&lt;ngách&gt;/PROGRESS.md</code></td></tr>
</tbody></table>

<h2>10. Hệ thống này KHÔNG làm gì</h2>
<p>Nói rõ giới hạn để không kỳ vọng sai:</p>
<table>
<thead><tr><th style="width:38%">Không làm</th><th>Vì sao</th></tr></thead>
<tbody>
<tr><td class="no">Không tự crawl dữ liệu</td>
<td>Crawl là khâu riêng, hệ thống này bắt đầu từ dữ liệu đã có</td></tr>
<tr><td class="no">Không dự đoán view tương lai</td>
<td>Chỉ đo trạng thái hiện tại và xu hướng đã xảy ra</td></tr>
<tr><td class="no">Không thay quyết định kinh doanh</td>
<td>Đưa bằng chứng có cấu trúc, người quyết</td></tr>
<tr><td class="no">Không phân tích được thứ dữ liệu không có</td>
<td>Ví dụ: retention, CTR, traffic source &mdash; YouTube API không trả về
cho kênh người khác</td></tr>
</tbody></table>

</body></html>"""

# ══════════════════════════════════════════════════════════════════════════
# DÒ LỆCH · sơ đồ ở đây vẽ TAY lại từ .md nên có thể trôi khi .md đổi.
# Không chặn việc sinh PDF — chỉ cảnh báo để người sửa .md biết mà sửa cả đây.
# ══════════════════════════════════════════════════════════════════════════
def drift_check():
    md = SRC.read_text(encoding="utf-8")
    warn = []
    # §1.1 CỐ Ý không vẽ: đó là ánh xạ hai cột (framework ↔ niches), bảng
    # đọc nhanh hơn sơ đồ. 9 sơ đồ + 1 bảng = 10 khối mermaid trong .md.
    n_mermaid = md.count("```mermaid")
    n_drawn, n_as_table = 9, 1
    if n_mermaid != n_drawn + n_as_table:
        warn.append(f"file .md có {n_mermaid} khối mermaid, ở đây vẽ {n_drawn} "
                    f"+ {n_as_table} chuyển thành bảng → thiếu "
                    f"{n_mermaid - n_drawn - n_as_table}")
    # các mã bước xuất hiện trong .md nhưng chưa có trong sơ đồ workflow
    import re as _re
    md_steps = set(_re.findall(r"STEP_(\d\d[a-z]?)", md))
    drawn = set(_re.findall(r"STEP_(\d\d[a-z]?)", d_workflow.__doc__ or "")) | {
        "00", "01", "02", "03", "04", "04b", "04g", "04h", "05", "06", "07", "08", "10"}
    missing = md_steps - drawn
    if missing:
        warn.append("bước có trong .md nhưng thiếu ở sơ đồ: " + ", ".join(sorted(missing)))
    return warn


out = ROOT/"niches"/N.name/"99_report/_phu-luc/ARCH_Kien-truc-He-thong.pdf"
out.parent.mkdir(parents=True, exist_ok=True)
out.parent.mkdir(parents=True, exist_ok=True)
HTML(string=DOC).write_pdf(out)
print(f"✅ {out.relative_to(ROOT)}")
for w in drift_check():
    print(f"⚠ LỆCH: {w}")
