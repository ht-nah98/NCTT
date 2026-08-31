#!/usr/bin/env python3
"""T1.1 — HỒ SƠ NGÁCH CHI TIẾT (fact base — chỉ sự thật).

Trả lời: "Ngách này thực tế trông như thế nào trên YouTube?"

NGUYÊN TẮC: tài liệu này CHỈ chứa thứ quan sát được. Không diễn giải động cơ
khán giả (-> T1.2), không thông số sản xuất (-> T1.3), không hồ sơ đối thủ
(-> T1.4). Xem framework/00_system/11_OUTPUT_CONTRACT.md §2.

Mọi phát biểu mang mã nguồn Y·P·S·V·K·N và cỡ mẫu. Mục chưa có dữ liệu ghi
"[—] chưa có nguồn" thay vì bỏ trống — làm lỗ hổng hữu hình (quy tắc N6).

    python3 pipeline/report/build_T11_niche_facts.py [niche_path]
"""
import sys
import pathlib
import re
from weasyprint import HTML

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from _t1_common import S, vn, n_of, load, today, doc, source_legend, cite  # noqa: E402
from _common import niche_root                                        # noqa: E402

N = niche_root()
NICHE = N.name
OUT = N / "99_report" / "T1-1_Ho-so-ngach.pdf"

M = load(N / "_state/metrics.json", {})
SC = load(N / "_state/scores.json", {})
AUD = load(N / "05_audience/_metrics_raw.json", {})
CMP = load(N / "03_competitor/_metrics_raw.json", {})
KW = load(N / "06_keyword/_metrics_raw.json", {})
AUDIT = load(N / "99_report/_data_audit.json", {})

mk = M.get("market", {})
mo = M.get("momentum", {})
en = M.get("entry", {})
ai = M.get("ai_fit", {})
au = M.get("audience", {})
kw = M.get("keyword", {})
mn = M.get("money", {})
rk = M.get("risk", {})


def brief_field(label, default="—"):
    """Rút một dòng từ bảng NICHE_BRIEF.md."""
    p = N / "NICHE_BRIEF.md"
    if not p.exists():
        return default
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.startswith("|") and label in line:
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 2 and cells[0].strip() == label:
                return re.sub(r"\*\*", "", cells[1]) or default
    return default


# ── 1 · PHẠM VI ─────────────────────────────────────────────────────────────
scope = f"""<h2>1 · Định nghĩa phạm vi</h2>
<table><tbody>
<tr><td class="w">Tên ngách</td><td>{brief_field("Tên ngách")}</td></tr>
<tr><td class="w">Ngách cha</td><td>{brief_field("Ngách cha")}</td></tr>
<tr><td class="w">Thị trường</td><td>{brief_field("Thị trường mục tiêu")}</td></tr>
<tr><td class="w">Ngôn ngữ</td><td>{brief_field("Ngôn ngữ chính")}</td></tr>
<tr><td class="w">Ngày crawl</td><td>{brief_field("Ngày crawl")}</td></tr>
</tbody></table>

<h3>Tiêu chí vào/ra</h3>
<p>{S.Y("Kênh vào mẫu khi có video thuộc chủ đề Christian/Gospel Blues và đạt "
        "ngưỡng lọc 4 rổ B1–B4", n=mk.get("M1_2_total_channels"))}</p>
<p>{S.Y(f"Trong đó <b>{mk.get('M1_2_active_channels','—')} kênh đang hoạt động</b>, "
        f"{(mk.get('M1_2_total_channels') or 0) - (mk.get('M1_2_active_channels') or 0)} "
        "kênh đã ngừng")}</p>

<h3>Ranh giới với dòng lân cận</h3>
<p class="small">Ngách cha Christian/Gospel bị khoá chặt (top 20% chiếm 81,98% view).
Christian Blues là nhánh con có cấu trúc thị phần thoáng hơn — xem §2.</p>
<p>{S.none("Chưa đo ranh giới định lượng với Southern Gospel, Blues thế tục, "
           "Worship đương đại — cần crawl thêm ba dòng lân cận để so")}</p>"""

# ── 2 · TRẠNG THÁI CUNG ─────────────────────────────────────────────────────
tier = en.get("tier_dist") or CMP.get("tier_dist") or {}
tier_rows = "".join(
    f'<tr><td>{k}</td><td class="n">{v}</td>'
    f'<td class="n">{vn(100*v/sum(tier.values()))}%</td></tr>'
    for k, v in tier.items()) if tier else ""

model = ai.get("model_dist", {})
model_rows = "".join(
    f'<tr><td>{k}</td><td class="n">{v}</td>'
    f'<td class="n">{vn(100*v/sum(model.values()))}%</td></tr>'
    for k, v in model.items()) if model else ""

fast = en.get("M3_3_alt_fastest_success") or []
fast_rows = "".join(
    f'<tr><td class="w">{r["handle"]}</td>'
    f'<td class="n">{vn(r["age_m"])} tháng</td>'
    f'<td class="n">{n_of(r["vpm"])}</td></tr>' for r in fast[:5])

supply = f"""<h2>2 · Trạng thái cung</h2>

<h3>Quy mô</h3>
<table><tbody>
<tr><td class="w">Kênh trong mẫu</td><td class="n">{mk.get('M1_2_total_channels','—')}</td>
    <td>{S.Y("đang hoạt động: " + str(mk.get('M1_2_active_channels','—')))}</td></tr>
<tr><td class="w">View mỗi tháng</td><td class="n">{n_of(mk.get('M1_1_views_per_month',0))}</td>
    <td>{S.Y("toàn ngách")}</td></tr>
<tr><td class="w">View trung vị / video</td><td class="n">{n_of(mk.get('M1_3_median_view',0))}</td>
    <td>{S.Y("dùng trung vị vì phân bố đuôi dài")}</td></tr>
<tr><td class="w">View trung bình / video</td><td class="n">{n_of(mk.get('M1_3_mean_view',0))}</td>
    <td class="small">gấp {vn((mk.get('M1_3_mean_view') or 0)/(mk.get('M1_3_median_view') or 1))}×
        trung vị — xác nhận đuôi dài</td></tr>
</tbody></table>

<h3>Động lượng — cầu so với cung</h3>
<table><thead><tr><th>Chỉ số</th><th class="n">Giá trị</th><th>Nghĩa</th></tr></thead><tbody>
<tr><td class="w">M2.1 · tăng trưởng cầu</td><td class="n">{vn(mo.get('M2_1_view_growth'),2)}×</td>
    <td>view giữa hai cửa sổ đều đã chín</td></tr>
<tr><td class="w">M2.2 · tăng trưởng cung</td><td class="n">{vn(mo.get('M2_2_supply_growth'),2)}×</td>
    <td>số video mới</td></tr>
<tr><td class="w">M2.4 · khoảng cách</td><td class="n"><b>{vn(mo.get('M2_4_demand_supply_gap'),2)}×</b></td>
    <td>{'<span class="ok">cầu vượt cung</span>' if (mo.get('M2_4_demand_supply_gap') or 0) >= 1
         else '<span class="wa">cung vượt cầu</span>'}</td></tr>
<tr><td class="w">M2.3 · tỷ lệ kênh mới</td><td class="n">{vn(mo.get('M2_3_new_channel_rate'))}%</td>
    <td>kênh dưới 24 tháng tuổi</td></tr>
</tbody></table>
<div class="box"><h4>Bẫy đã tránh — dữ liệu chưa chín</h4>
<p>{S.Y(f"Tính thô (không lọc tuổi video) cho M2.4 = "
        f"<b>{vn(mk.get('_naive_M2_4'),2)}</b> → vùng 'dừng lại'. "
        f"Nhưng chỉ {vn(mk.get('_naive_maturity_pct'),0)}% video trong cửa sổ đó đã đủ "
        f"60 ngày tuổi. Tính lại trên hai cửa sổ đều chín → "
        f"<b>{vn(mo.get('M2_4_demand_supply_gap'),2)}</b>. Kết luận đảo ngược.")}</p>
<p class="small">{mk.get('_window_note','')}</p></div>

<h3>Phân tầng &amp; thị phần</h3>
<table><thead><tr><th>Tầng</th><th class="n">Số kênh</th><th class="n">Tỷ lệ</th></tr></thead>
<tbody>{tier_rows or '<tr><td colspan="3" class="small">chưa có dữ liệu phân tầng</td></tr>'}</tbody></table>
<table><tbody>
<tr><td class="w">Gini</td><td class="n">{vn(en.get('M3_1_gini'),2)}</td>
    <td class="small">0 = đều tuyệt đối · 1 = một kênh ăn hết</td></tr>
<tr><td class="w">Top 1 kênh</td><td class="n">{vn(en.get('top1_share'))}%</td><td></td></tr>
<tr><td class="w">Top 5 kênh</td><td class="n">{vn(en.get('top5_share'))}%</td><td></td></tr>
<tr><td class="w">Top 20% kênh</td><td class="n">{vn(en.get('top20pct_share'))}%</td>
    <td class="small">so với ngách cha 81,98% — thoáng hơn rõ rệt</td></tr>
</tbody></table>

<h3>Mô hình sản xuất đang có</h3>
<table><thead><tr><th>Mô hình</th><th class="n">Số kênh</th><th class="n">Tỷ lệ</th></tr></thead>
<tbody>{model_rows}</tbody></table>
<p>{S.Y(f"Nhóm top 20% có <b>{vn(ai.get('M4_1_ai_first_top20_pct'),0)}%</b> là kênh "
        "ai-first — ngách chấp nhận nội dung AI")}</p>

<h3>Kênh breakout — vào nhanh nhất</h3>
<table><thead><tr><th>Kênh</th><th class="n">Tuổi</th><th class="n">View/tháng</th></tr></thead>
<tbody>{fast_rows}</tbody></table>
<p>{S.Y(f"<b>{vn(en.get('M3_2_newcomer_success_pct'),0)}%</b> kênh trẻ đạt ngưỡng thành công "
        f"({en.get('_young_success_n','—')}/{en.get('_young_n','—')} kênh dưới 24 tháng)",
        n=en.get("_young_n"))}</p>
<p class="small">Hồ sơ chi tiết từng kênh: xem <b>T1.4 · Thẻ đối thủ</b>.</p>"""

# ── 3 · DẤU VẾT CẦU (THÔ) ───────────────────────────────────────────────────
vg = (kw.get("voice_gap") or KW.get("voice_gap") or [])[:8]
vg_rows = "".join(
    f'<tr><td class="w">{r["word"]}</td><td class="n">{n_of(r["in_comments"])}</td>'
    f'<td class="n">{n_of(r["in_titles"])}</td>'
    f'<td class="n">{vn(r["ratio"])}×</td></tr>' for r in vg)

ctx = (AUD.get("context") or {})
ctx_rows = "".join(
    f'<tr><td>{k}</td><td class="n">{v["n"]}</td><td class="n">{vn(v["pct"],2)}%</td></tr>'
    for k, v in sorted(ctx.items(), key=lambda x: -x[1]["n"])[:7])

band = mn.get("M5_3_band") or []
band_rows = "".join(
    f'<tr><td>{b["duration_band"]}</td><td class="n">{n_of(b["n"])}</td>'
    f'<td class="n">{n_of(b["med_view"])}</td></tr>' for b in band[:6])

lyr = AUDIT.get("lyrics_col", {})

demand = f"""<h2>3 · Dấu vết cầu (thô)</h2>
<p class="small">Mục này chỉ đặt <b>số liệu</b> lên bàn. Diễn giải vì sao khán giả
hành xử như vậy thuộc <b>T1.2</b>.</p>

<h3>Khoảng trống từ vựng — comment so với tiêu đề</h3>
<table><thead><tr><th>Từ</th><th class="n">Trong comment</th>
<th class="n">Trong tiêu đề</th><th class="n">Tỷ lệ</th></tr></thead>
<tbody>{vg_rows}</tbody></table>
<p>{S.Y("Khoảng cách lớn nhất là <b>amen</b>: 2.233 lần trong comment, 5 lần trong tiêu đề",
        n=au.get("n_analyzed"), weak=True)}</p>
<p class="small">Đây là <b>tín hiệu gián tiếp</b> về cầu chưa được đáp ứng. YouTube
không đo được cầu trực tiếp — muốn xác nhận cần nguồn <b>S</b> (Google Trends,
autocomplete) hoặc <b>V</b> (Reddit).</p>

<h3>Bối cảnh nghe — theo comment tự khai</h3>
<table><thead><tr><th>Bối cảnh</th><th class="n">n</th><th class="n">% mẫu</th></tr></thead>
<tbody>{ctx_rows}</tbody></table>
<p>{S.Y(f"Bối cảnh nổi bật nhất: <b>{au.get('top_context','—')}</b> "
        f"({vn(au.get('top_context_pct'),1)}% mẫu)", n=au.get("n_analyzed"))}</p>

<h3>Phân bố comment</h3>
<table><tbody>
<tr><td class="w">Comment thu thập</td><td class="n">{n_of(au.get('n_total',0))}</td><td></td></tr>
<tr><td class="w">Sau lọc nhiễu</td><td class="n">{n_of(au.get('n_analyzed',0))}</td>
    <td class="small">bỏ {n_of(au.get('n_noise',0))} dòng nhiễu</td></tr>
<tr><td class="w">Tự khai tuổi</td><td class="n">{au.get('age_n','—')}</td>
    <td class="wa">chỉ {vn(100*(au.get('age_n') or 0)/(au.get('n_analyzed') or 1),1)}% —
        không đại diện</td></tr>
</tbody></table>
<div class="box gap"><h4>Giới hạn của dữ liệu comment</h4>
<p>Comment chỉ chứa <b>người chịu bình luận</b> — mẫu thiên lệch, không phải toàn
bộ khán giả. Con số tuổi trung vị {vn(au.get('age_median'),0)} là của
{au.get('age_n','—')} người tự khai, <b>không</b> phải của ngách. Trích con số đó
mà bỏ cỡ mẫu là sai lệch nghiêm trọng.</p></div>

<h3>Độ dài video</h3>
<table><thead><tr><th>Dải</th><th class="n">Số video</th><th class="n">View trung vị</th></tr></thead>
<tbody>{band_rows}</tbody></table>

<h3>Tỷ lệ có lời / không lời</h3>
<p>{S.Y(f"Trong mẫu đã phiên âm: <b>{lyr.get('co_loi','—')}</b> bài có lời, "
        f"<b>{lyr.get('khong_loi','—')}</b> bài không lời, {lyr.get('missing','—')} thiếu dữ liệu",
        n=lyr.get("total"))}</p>

<h3>Từ khoá &amp; tag</h3>
<table><tbody>
<tr><td class="w">Tag duy nhất</td><td class="n">{n_of(kw.get('tag_unique',0))}</td><td></td></tr>
<tr><td class="w">Độ phủ tag</td><td class="n">{vn(kw.get('tag_coverage_pct'))}%</td>
    <td class="small">video có gắn tag</td></tr>
<tr><td class="w">Chủ đề đã kiểm định</td><td class="n">{kw.get('themes_tested','—')}</td>
    <td class="small">xác nhận: {len(kw.get('themes_recommended') or [])} ·
        nên tránh: {len(kw.get('themes_avoid') or [])}</td></tr>
</tbody></table>"""

# ── 4 · KINH TẾ NGÁCH ───────────────────────────────────────────────────────
rpm = mn.get("M5_2_rpm", {})
econ = f"""<h2>4 · Kinh tế ngách</h2>
<table><thead><tr><th>Kịch bản</th><th class="n">RPM</th>
<th class="n">Doanh thu tháng (ước)</th></tr></thead><tbody>
<tr><td>Thấp</td><td class="n">${vn(rpm.get('low'),1)}</td>
    <td class="n">${n_of((mn.get('rev_base_monthly_usd') or 0)*(rpm.get('low',0))/(rpm.get('base') or 1))}</td></tr>
<tr><td class="w">Cơ sở</td><td class="n">${vn(rpm.get('base'),1)}</td>
    <td class="n"><b>${n_of(mn.get('rev_base_monthly_usd',0))}</b></td></tr>
<tr><td>Cao</td><td class="n">${vn(rpm.get('high'),1)}</td>
    <td class="n">${n_of((mn.get('rev_base_monthly_usd') or 0)*(rpm.get('high',0))/(rpm.get('base') or 1))}</td></tr>
</tbody></table>
<p class="small">Cơ sở tính: {rpm.get('basis','—')}</p>
<p>{cite(M, "M5_2_rpm_range",
        f"Dung lượng đo từ YouTube, còn RPM lấy từ benchmark ngoài — "
        f"đây là chỉ số <b>duy nhất</b> trong tài liệu trộn hai nhóm nguồn")}</p>
<table><tbody>
<tr><td class="w">Tỷ lệ tiếng Anh</td><td class="n">{vn(mn.get('M5_1_en_pct'))}%</td>
    <td class="small">trong số đã khai ngôn ngữ</td></tr>
<tr><td class="w">Kênh Tier-1</td><td class="n">{vn(mn.get('M5_1_tier1_of_declared'))}%</td>
    <td class="small">thị trường RPM cao</td></tr>
<tr><td class="w">Độ dài trung vị</td><td class="n">{mn.get('M5_3_median_duration_min','—')} phút</td>
    <td class="small">đủ chỗ cho nhiều điểm quảng cáo</td></tr>
</tbody></table>
<div class="box gap"><h4>Độ nhạy — con số này yếu ở đâu</h4>
<p>{S.none("RPM là ước lượng từ benchmark ngoài, KHÔNG phải số thật của kênh nào. "
           "Chỉ nguồn N (Analytics kênh nhà) mới cho RPM thật")}</p>
<p class="small">Khoảng dao động ${vn(rpm.get('low'),1)}–${vn(rpm.get('high'),1)} tức
sai số <b>4 lần</b> giữa hai đầu. Không dùng con số này làm căn cứ duy nhất
để quyết định đầu tư.</p></div>"""

# ── 5 · RỦI RO & RÀO CẢN ────────────────────────────────────────────────────
risks = mn.get("risks") or []
risk_rows = "".join(
    f'<tr><td class="w">{r["risk"]}</td><td class="n">{r.get("penalty","")}</td>'
    f'<td class="small">{r.get("evidence","")[:220]}</td></tr>' for r in risks)

pd_cls = None
p_pd = N / "02_analysis/pd_classification.csv"
if p_pd.exists():
    import csv
    rows = list(csv.DictReader(open(p_pd, encoding="utf-8")))
    col = next((c for c in (rows[0].keys() if rows else []) if "class" in c.lower()), None)
    if col:
        from collections import Counter
        pd_cls = Counter(r[col] for r in rows)

pd_block = ""
if pd_cls:
    pd_rows = "".join(f'<tr><td>{k}</td><td class="n">{v}</td></tr>'
                      for k, v in pd_cls.most_common())
    pd_block = f"""<h3>Nguồn gốc lời hát — rủi ro bản quyền</h3>
<table><thead><tr><th>Phân loại</th><th class="n">Số bài</th></tr></thead>
<tbody>{pd_rows}</tbody></table>
<p class="small">Chi tiết từng bài và bằng chứng đối chứng: xem <b>T1.3 §Lớp 3</b>.</p>"""

risk = f"""<h2>5 · Rủi ro &amp; rào cản</h2>
<table><thead><tr><th>Rủi ro</th><th class="n">Điểm trừ</th><th>Bằng chứng</th></tr></thead>
<tbody>{risk_rows or '<tr><td colspan="3" class="small">chưa ghi nhận</td></tr>'}</tbody></table>
{pd_block}
<h3>Bão hoà</h3>
<p>{S.Y(f"Trùng lặp tiêu đề chéo kênh: <b>{vn(rk.get('cross_title_pct'))}%</b> video "
        f"({rk.get('cross_title_count','—')} tiêu đề dùng chung), "
        f"{rk.get('channels_high_dup','—')} kênh trùng nhiều")}</p>
<h3>Chính sách nền tảng</h3>
<p class="small">Dữ liệu YouTube API phải làm mới hoặc xoá trong 30 ngày —
điều khoản không thương lượng. Nội dung AI cần nhãn "nội dung tổng hợp"
theo chính sách hiện hành.</p>"""

# ── kết luận Go/No-Go ───────────────────────────────────────────────────────
total = SC.get("total_score", "?")
gate = ("ĐI TIẾP" if (mo.get("M2_4_demand_supply_gap") or 0) >= 1.0
        else "CÂN NHẮC" if (mo.get("M2_4_demand_supply_gap") or 0) >= 0.5
        else "DỪNG")
verdict = f"""<h2>Kết luận cho quyết định đầu tư</h2>
<table><tbody>
<tr><td class="w">Điểm ngách</td><td class="n"><b>{total} / 20</b></td>
    <td class="small">so sánh được với ngách khác cùng rubric</td></tr>
<tr><td class="w">Cổng quyết định</td>
    <td class="{'ok' if gate=='ĐI TIẾP' else 'wa'}"><b>{gate}</b></td>
    <td class="small">dựa trên M2.4 = {vn(mo.get('M2_4_demand_supply_gap'),2)}×</td></tr>
</tbody></table>
<div class="box"><h4>Ba điều chắc chắn nhất</h4>
<p>1 · {cite(M, "M2_4_demand_supply_gap",
        f"Cầu tăng nhanh hơn cung {vn(mo.get('M2_4_demand_supply_gap'),2)}× — "
        "ngách chưa bão hoà")}</p>
<p>2 · {S.Y(f"Kênh mới vẫn vào được: {vn(en.get('M3_2_newcomer_success_pct'),0)}% "
            "kênh trẻ đạt ngưỡng, nhanh nhất 0,6 tháng", n=en.get("_young_n"))}</p>
<p>3 · {S.Y(f"Ngách chấp nhận nội dung AI: {vn(ai.get('M4_1_ai_first_top20_pct'),0)}% "
            "nhóm dẫn đầu là ai-first")}</p></div>
<div class="box gap"><h4>Điều tài liệu này KHÔNG trả lời được</h4>
<p>Cầu nào có mà chưa ai phục vụ, và cầu sẽ dịch chuyển về đâu trong 6–12 tháng.
Cả hai câu này cần nguồn <b>S</b> và <b>P</b> — hiện chưa có. Xem chú giải cuối tài liệu.</p></div>"""

BODY = scope + supply + demand + econ + risk + verdict + source_legend()

FOOT = f"""<b>Nguồn dữ liệu.</b>
<code>_state/metrics.json</code>, <code>_state/scores.json</code>,
<code>02_market/</code>, <code>03_competitor/</code>, <code>05_audience/</code>,
<code>06_keyword/</code>, <code>07_monetization/</code>,
<code>99_report/_data_audit.json</code>.<br><br>
<b>Bản chất tài liệu.</b> Đây là <b>fact base</b> — chỉ chứa thứ quan sát được.
Diễn giải cơ chế xem <b>T1.2</b>; thông số sản xuất xem <b>T1.3</b>;
hồ sơ đối thủ xem <b>T1.4</b>.<br><br>
<b>Giới hạn.</b> Toàn bộ dữ liệu đến từ nguồn <b>Y</b> (YouTube). Các phát biểu
về khoảng trống cầu mang cảnh báo <i>suy gián tiếp</i> vì YouTube chỉ thấy cung
đã tồn tại. Dữ liệu comment là mẫu thiên lệch (chỉ người chịu bình luận).
Snapshot <code>video_stats</code> = 1 → độ tin cậy trục động lượng ở mức "vừa"."""

DOC = doc(
    "T1.1", NICHE,
    "Hồ sơ ngách<br>chi tiết",
    "Bản mô tả những gì quan sát được về ngách tại một thời điểm — "
    "mỗi phát biểu có nguồn và mức tin cậy.",
    [("Phiên bản", f"đo ngày {brief_field('Ngày crawl')} · "
                   f"n={mk.get('M1_2_total_channels','—')} kênh"),
     ("Dựng lúc", today()),
     ("Trả lời", "Ngách này thực tế trông như thế nào trên YouTube?"),
     ("Ai đọc", "Người quyết định đầu tư ngách"),
     ("Nhịp cập nhật", "theo snapshot dữ liệu, 30–90 ngày")],
    BODY, FOOT)

if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=DOC, base_url=".").write_pdf(OUT)
    print(f"   -> {OUT.relative_to(N.parent.parent)}  ({OUT.stat().st_size/1024:.0f} KB)")
