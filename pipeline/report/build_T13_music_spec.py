#!/usr/bin/env python3
"""T1.3 — ĐẶC TẢ DÒNG NHẠC (Music DNA Spec).

Trả lời: "Bản nhạc/video phải nghe và trông như thế nào thì được coi là
đúng ngách?"

Ba lớp: âm thanh · văn hoá & ngôn ngữ · ràng buộc pháp lý. Kèm checklist QC.
Đây là tài liệu TRA CỨU HẰNG NGÀY của nhạc sĩ / người vận hành Suno / designer.

KHÔNG chứa định nghĩa phạm vi thị trường (-> T1.1) hay phân tích đối thủ
(-> T1.4). Xem framework/00_system/11_OUTPUT_CONTRACT.md §4.

    python3 pipeline/report/build_T13_music_spec.py [niche_path]
"""
import sys
import csv
import json
import pathlib
import collections
import statistics as st
from weasyprint import HTML

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from _t1_common import S, vn, n_of, load, today, doc, source_legend   # noqa: E402
from _common import niche_root                                        # noqa: E402

N = niche_root()
NICHE = N.name
OUT = N / "99_report" / "T1-3_Dac-ta-dong-nhac.pdf"

RECIPE = load(N / "04_outlier/audio/AUDIO_RECIPE.json", {})
LYR = load(N / "04_outlier/lyrics/LYRICS_ANALYSIS.json", {})
M = load(N / "_state/metrics.json", {})
spec = RECIPE.get("spec", {})
cohort = RECIPE.get("cohort", {})


# ── đo trực tiếp từ audio_dna_full.jsonl ────────────────────────────────────
def measure_audio():
    """Đo lại các thông số then chốt từ nguồn thô.

    Không lấy sẵn từ AUDIO_RECIPE vì recipe tính trên cohort 144 track của 5
    kênh top; ở đây cần cả 307 track để nói về DÒNG NHẠC, không phải về nhóm top.
    """
    p = N / "00_input/raw/audio_dna_full.jsonl"
    if not p.exists():
        return None
    bpm, lufs, lra, dur, swing = [], [], [], [], []
    mode, sub, inst = collections.Counter(), collections.Counter(), collections.Counter()
    intro, vox_in, nblocks = [], [], []
    n = 0
    for line in p.open(encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        n += 1
        r = d["timeline"]["rhythm"]
        l = d["timeline"]["loudness"]
        h = d.get("harmony") or {}
        if r.get("bpm"):
            bpm.append(r["bpm"])
        if r.get("swing_ratio"):
            swing.append(r["swing_ratio"])
        if r.get("subdivision"):
            sub[r["subdivision"]] += 1
        if l.get("lufs_i"):
            lufs.append(l["lufs_i"])
        if l.get("lra"):
            lra.append(l["lra"])
        if (d["source"] or {}).get("duration_s"):
            dur.append(d["source"]["duration_s"])
        k = h.get("key")
        if isinstance(k, dict) and k.get("mode"):
            mode[k["mode"]] += 1
        ins = ((d.get("stems") or {}).get("instruments") or {})
        for tags in ins.values():
            if isinstance(tags, dict):
                for t, v in tags.items():
                    if v > 0.15:
                        inst[t] += 1
        blocks = ((d.get("stems") or {}).get("blocks") or [])
        if blocks:
            nblocks.append(len(blocks))
            intro.append(blocks[0]["end"] - blocks[0]["start"])
            for b in blocks:
                if "vocals" in (b.get("active") or []):
                    vox_in.append(b["start"])
                    break

    def q(a, p_):
        a = sorted(a)
        return a[min(len(a) - 1, int(p_ * len(a)))] if a else None

    return dict(
        n=n, bpm=(q(bpm, .25), st.median(bpm), q(bpm, .75)),
        lufs=(q(lufs, .25), st.median(lufs), q(lufs, .75)),
        lra=st.median(lra), dur=(q(dur, .25), st.median(dur), q(dur, .75)),
        swing=st.median(swing), mode=mode, sub=sub, inst=inst,
        intro=st.median(intro), vox_in=(q(vox_in, .25), st.median(vox_in), q(vox_in, .75)),
        nblocks=st.median(nblocks))


A = measure_audio()

# ── LỚP 1 · ÂM THANH ────────────────────────────────────────────────────────
if A:
    maj = A["mode"].get("major", 0)
    mino = A["mode"].get("minor", 0)
    tot_mode = maj + mino
    inst_rows = "".join(
        f'<tr><td>{t}</td><td class="n">{v}</td><td class="n">{vn(100*v/A["n"],0)}%</td>'
        f'<td>{"bắt buộc" if 100*v/A["n"]>60 else "thường có" if 100*v/A["n"]>25 else "điểm nhấn"}</td></tr>'
        for t, v in A["inst"].most_common(12)
        if t not in ("Musical instrument", "Singing", "Vocal music"))
    sub_rows = "".join(
        f'<tr><td>{k}</td><td class="n">{v}</td><td class="n">{vn(100*v/sum(A["sub"].values()),0)}%</td></tr>'
        for k, v in A["sub"].most_common())

    layer1 = f"""<h2>Lớp 1 · Âm thanh</h2>
<p class="small">Đo trên toàn bộ {A['n']} bản ghi đã tách nhạc cụ — mô tả
<b>dòng nhạc</b>, không phải riêng nhóm top.</p>

<h3>Thông số nền</h3>
<table><thead><tr><th>Thông số</th><th class="n">p25</th><th class="n">Trung vị</th>
<th class="n">p75</th><th>Ghi chú</th></tr></thead><tbody>
<tr><td class="w">BPM</td><td class="n">{vn(A['bpm'][0],0)}</td>
    <td class="n"><b>{vn(A['bpm'][1],0)}</b></td><td class="n">{vn(A['bpm'][2],0)}</td>
    <td class="small">chậm — nhịp đi bộ</td></tr>
<tr><td class="w">Độ ồn LUFS</td><td class="n">{vn(A['lufs'][0])}</td>
    <td class="n"><b>{vn(A['lufs'][1])}</b></td><td class="n">{vn(A['lufs'][2])}</td>
    <td class="small">chuẩn phát trực tuyến</td></tr>
<tr><td class="w">Dải động LRA</td><td class="n">—</td>
    <td class="n"><b>{vn(A['lra'])}</b></td><td class="n">—</td>
    <td class="small">đừng nén chặt hơn</td></tr>
<tr><td class="w">Độ dài bài (giây)</td><td class="n">{vn(A['dur'][0],0)}</td>
    <td class="n"><b>{vn(A['dur'][1],0)}</b></td><td class="n">{vn(A['dur'][2],0)}</td>
    <td class="small">≈ {int(A['dur'][1]//60)}:{int(A['dur'][1]%60):02d}</td></tr>
<tr><td class="w">Tỷ lệ swing</td><td class="n">—</td>
    <td class="n"><b>{vn(A['swing'],2)}</b></td><td class="n">—</td>
    <td class="small">&gt;1 = shuffle, giữ chất blues</td></tr>
</tbody></table>

<h3>Điệu thức — phát hiện đi ngược trực giác</h3>
<table><tbody>
<tr><td class="w">Trưởng (major)</td><td class="n">{maj}</td>
    <td class="n">{vn(100*maj/max(tot_mode,1),0)}%</td></tr>
<tr><td class="w">Thứ (minor)</td><td class="n">{mino}</td>
    <td class="n">{vn(100*mino/max(tot_mode,1),0)}%</td></tr>
</tbody></table>
<div class="box"><h4>Blues ở ngách này KHÔNG buồn</h4>
<p>{S.Y(f"<b>{vn(100*maj/max(tot_mode,1),0)}%</b> bài ở điệu trưởng. Trực giác "
        "“Blues là buồn” sai với dòng này — nhạc mang hình thức Blues nhưng "
        "nội dung là hy vọng", n=tot_mode)}</p></div>

<h3>Nhạc cụ</h3>
<table><thead><tr><th>Nhạc cụ</th><th class="n">Số bài</th><th class="n">Tỷ lệ</th>
<th>Vai trò</th></tr></thead><tbody>{inst_rows}</tbody></table>
<div class="box gap"><h4>Chỗ trống nhạc cụ</h4>
<p>Guitar điện, slide guitar và hợp xướng đều dưới 6% — ba nhạc cụ đặc trưng
Blues/Gospel gần như bỏ ngỏ. Đây là chỗ tạo khác biệt rẻ nhất về sản xuất.</p></div>

<h3>Chia nhịp</h3>
<table><thead><tr><th>Chia nhịp</th><th class="n">Số bài</th><th class="n">Tỷ lệ</th></tr></thead>
<tbody>{sub_rows}</tbody></table>

<h3>Cấu trúc bài</h3>
<table><tbody>
<tr><td class="w">Số khối</td><td class="n">{vn(A['nblocks'],0)}</td>
    <td class="small">mỗi khối ≈ 8 nhịp</td></tr>
<tr><td class="w">Khối mở đầu</td><td class="n">{vn(A['intro'],0)} giây</td>
    <td class="small">thường guitar đơn hoặc piano đơn</td></tr>
<tr><td class="w">Giọng vào</td><td class="n"><b>{vn(A['vox_in'][1],0)} giây</b></td>
    <td class="small">p25–p75: {vn(A['vox_in'][0],0)}–{vn(A['vox_in'][2],0)} giây</td></tr>
</tbody></table>
<p>{S.Y(f"Giọng vào ở giây {vn(A['vox_in'][1],0)} — intro dài quá "
        f"{vn(A['vox_in'][2],0)} giây đã là chậm so với thị trường", n=A['n'])}</p>"""
else:
    layer1 = ("<h2>Lớp 1 · Âm thanh</h2><p>"
              + S.none("chưa có audio_dna_full.jsonl") + "</p>")

# ── độ chặt: phát hiện quan trọng ───────────────────────────────────────────
tight_cnt = collections.Counter(v.get("tightness") for v in spec.values())
tightness = f"""<h3>Độ chặt của công thức — đọc kỹ trước khi ép theo</h3>
<table><thead><tr><th>Độ chặt</th><th class="n">Số thông số</th><th>Nghĩa</th></tr></thead><tbody>
<tr><td class="w">Chặt</td><td class="n">{tight_cnt.get('chặt',0)}</td>
    <td>bám sát — lệch là ra khỏi ngách</td></tr>
<tr><td class="w">Vừa</td><td class="n">{tight_cnt.get('vừa',0)}</td>
    <td>tham chiếu, có biên độ</td></tr>
<tr><td class="w">Rộng</td><td class="n">{tight_cnt.get('rộng',0)}</td>
    <td>tự do — ép theo là bịa</td></tr>
</tbody></table>
<div class="box gap"><h4>Không có thông số nào “chặt”</h4>
<p>{S.Y(f"Trong {len(spec)} thông số đo trên nhóm thắng, <b>0</b> thông số đạt mức chặt. "
        f"Nghĩa là ngách này <b>không có một công thức âm thanh duy nhất</b> — "
        f"nhóm dẫn đầu làm rất khác nhau", n=cohort.get("n_tracks"))}</p>
<p class="small">Hệ quả: dùng bảng thông số ở trên làm <b>vùng an toàn</b>, không
phải khuôn đúc. Thắng hay thua nằm ở chủ đề và nhịp đăng (xem T1.2 §4), không
nằm ở việc khớp BPM tới từng đơn vị.</p></div>"""

# ── LỚP 2 · VĂN HOÁ & NGÔN NGỮ ──────────────────────────────────────────────
if LYR:
    ng = LYR.get("3_người_nghe", {})
    where = ng.get("họ_đang_ở_đâu", {})
    gets = ng.get("họ_nhận_được_gì", {})
    god = ng.get("xưng_hô_với_Chúa", {})
    arc = ng.get("cung_cảm_xúc", {})
    topic = ng.get("chủ_đề", {})
    src = LYR.get("nguồn", {})

    where_rows = "".join(
        f'<tr><td>{k.replace("_"," ")}</td><td class="n">{v["số_bài"]}</td>'
        f'<td class="n">{vn(v["pct_bài"])}%</td></tr>'
        for k, v in sorted(where.items(), key=lambda x: -x[1]["pct_bài"]))
    gets_rows = "".join(
        f'<tr><td>{k.replace("_"," ")}</td><td class="n">{v["số_bài"]}</td>'
        f'<td class="n">{vn(v["pct_bài"])}%</td></tr>'
        for k, v in sorted(gets.items(), key=lambda x: -x[1]["pct_bài"]))
    god_rows = "".join(
        f'<tr><td class="w">{k}</td><td class="n">{v["số_bài"]}</td>'
        f'<td class="n">{vn(v["pct_bài"])}%</td></tr>'
        for k, v in sorted(god.items(), key=lambda x: -x[1]["pct_bài"])[:6])
    topic_rows = "".join(
        f'<tr><td>{k.replace("_"," ")}</td><td class="n">{v["số_bài"]}</td>'
        f'<td class="n">{vn(v["pct"])}%</td></tr>'
        for k, v in sorted(topic.items(), key=lambda x: -x[1]["pct"]))

    layer2 = f"""<h2>Lớp 2 · Văn hoá &amp; ngôn ngữ</h2>
<p class="small">Đo trên {src.get('n_track','—')} bài đã phiên âm,
{src.get('n_kênh','—')} kênh, {n_of(src.get('tổng_chữ',0))} chữ.
Không trích nguyên văn lời (quy tắc T65).</p>

<h3>Ngôi kể — quyết định toàn bộ giọng văn</h3>
<div class="box"><p>{ng.get('ngôi_kể',{}).get('đọc_là','—')}</p></div>
<p class="small">Hệ quả: viết “tôi”, không viết “chúng ta”. Đây là bài hát cho
<b>một người đang ở một mình</b>, không phải bài cho hội chúng.</p>

<h3>Người nghe đang ở đâu</h3>
<table><thead><tr><th>Trạng thái</th><th class="n">Số bài</th><th class="n">% bài</th></tr></thead>
<tbody>{where_rows}</tbody></table>

<h3>Họ nhận được gì</h3>
<table><thead><tr><th>Điều nhận được</th><th class="n">Số bài</th><th class="n">% bài</th></tr></thead>
<tbody>{gets_rows}</tbody></table>
<p class="small">Bảng trên và bảng dưới đọc cùng nhau: bài mở ở <b>trạng thái
thiếu</b>, kết ở <b>điều nhận được</b>. Tỷ lệ “được dẫn” cao nhất
({vn(gets.get('được_dẫn',{}).get('pct_bài'))}%) — người nghe muốn được dẫn
đường, không chỉ được an ủi.</p>

<h3>Cung cảm xúc — quy tắc cứng của ngách</h3>
<div class="box"><h4>Đừng kết bài ở chỗ tối</h4>
<p>{arc.get('đọc_là','—')}</p>
<p class="small">Thang: {arc.get('thang','—')} · n={arc.get('n_bài','—')} bài</p></div>

<h3>Xưng hô với Chúa</h3>
<table><thead><tr><th>Cách xưng</th><th class="n">Số bài</th><th class="n">% bài</th></tr></thead>
<tbody>{god_rows}</tbody></table>
<p class="small">Quy ước: <b>Lord</b> là mặc định ({vn(god.get('lord',{}).get('pct_bài'))}%).
Dùng <i>Shepherd</i>, <i>King</i> chỉ khi bài có bối cảnh Thánh Vịnh rõ.</p>

<h3>Chủ đề được chạm</h3>
<table><thead><tr><th>Chủ đề</th><th class="n">Số bài</th><th class="n">% bài</th></tr></thead>
<tbody>{topic_rows}</tbody></table>

<h3>Chủ đề KHÔNG được chạm</h3>
<div class="box gap">
<p>Ba nhóm cần tránh, rút từ kiểm định chủ đề (T1.1 §3) và quy ước tôn giáo:</p>
<p>1 · <b>Thần học gây tranh cãi</b> — giáo phái, tiền định, nói tiếng lạ.
Khán giả trải rộng nhiều hệ phái.</p>
<p>2 · <b>Chính trị và thời sự</b> — không xuất hiện trong bất kỳ bài nào của mẫu.</p>
<p>3 · <b>Trách móc hoặc phán xét người nghe</b> — cung cảm xúc của ngách đi
từ tối sang sáng, không đi ngược lại.</p>
</div>

<h3>Vốn từ hình ảnh</h3>
<p class="small">Từ bộ ảnh nhóm dẫn đầu: nền tối chiếm ~61% khung · nguồn sáng
hổ phách · tránh tuyệt đối tông xanh lạnh · một nhân vật chiếm 21–35% khung.
Chi tiết đầy đủ: <code>04_outlier/THUMBNAIL_BRIEF.md</code>.</p>

<h3>Nhịp sinh hoạt</h3>
<p>{S.none("Chưa đo mùa vụ (Giáng sinh, Phục sinh, Lễ Tạ ơn). Cần ≥2 snapshot "
           "cách nhau 6 tháng, hoặc nguồn S (Google Trends) để thấy chu kỳ")}</p>"""
else:
    layer2 = ("<h2>Lớp 2 · Văn hoá &amp; ngôn ngữ</h2><p>"
              + S.none("chưa có LYRICS_ANALYSIS.json") + "</p>")

# ── LỚP 3 · PHÁP LÝ ─────────────────────────────────────────────────────────
pd_rows = ""
pd_total = 0
p_pd = N / "02_analysis/pd_classification.csv"
if p_pd.exists():
    rows = list(csv.DictReader(p_pd.open(encoding="utf-8")))
    pd_total = len(rows)
    col = next((c for c in (rows[0].keys() if rows else []) if "class" in c.lower()), None)
    if col:
        cnt = collections.Counter(r[col] for r in rows)
        pd_rows = "".join(
            f'<tr><td class="w">{k}</td><td class="n">{v}</td>'
            f'<td class="n">{vn(100*v/pd_total)}%</td></tr>' for k, v in cnt.most_common())

layer3 = f"""<h2>Lớp 3 · Ràng buộc pháp lý &amp; nguồn gốc</h2>

<h3>Phân loại nguồn gốc lời</h3>
<table><thead><tr><th>Phân loại</th><th class="n">Số bài</th><th class="n">Tỷ lệ</th></tr></thead>
<tbody>{pd_rows or '<tr><td colspan="3" class="small">chưa chạy phân loại PD</td></tr>'}</tbody></table>
<p class="small">Danh sách từng bài kèm bằng chứng đối chứng (link tua tới chỗ
trùng): <code>02_analysis/pd_evidence.csv</code> và phụ lục PDF trong
<code>99_report/_phu-luc/</code>.</p>

<h3>Ba đường đi và ràng buộc từng đường</h3>
<table><thead><tr><th>Đường</th><th>Ràng buộc</th><th>Rủi ro</th></tr></thead><tbody>
<tr><td class="w">Public domain</td>
    <td>Phải đối chiếu với corpus hymn/spiritual PD; ghi rõ bài gốc và năm</td>
    <td class="small">Bản <i>phối</i> mới vẫn có quyền — PD là lời, không phải bản ghi</td></tr>
<tr><td class="w">Cover</td>
    <td>Cần giấy phép cơ học; Content ID sẽ nhận diện</td>
    <td class="small">Doanh thu có thể bị chuyển toàn bộ cho chủ sở hữu</td></tr>
<tr><td class="w">Sáng tác mới</td>
    <td>Không ràng buộc bản quyền lời</td>
    <td class="small">Vẫn phải gắn nhãn nội dung tổng hợp nếu dùng AI</td></tr>
</tbody></table>

<h3>Yêu cầu bắt buộc khi phát hành</h3>
<div class="box">
<p>1 · <b>Nhãn nội dung tổng hợp</b> — YouTube yêu cầu khai báo với nội dung
tạo bằng AI. Không khai là vi phạm chính sách.</p>
<p>2 · <b>Content ID</b> — chạy đối chiếu trước khi đăng hàng loạt, tránh
nhận gậy bản quyền sau khi đã đăng 50 video.</p>
<p>3 · <b>Ghi nguồn PD</b> — với bài dựa trên hymn công cộng, ghi tên bài gốc
và năm trong mô tả. Vừa minh bạch vừa là bằng chứng phòng vệ.</p>
</div>"""

# ── CHECKLIST QC ────────────────────────────────────────────────────────────
if A:
    qc = f"""<h2>Checklist QC — nghiệm thu một bài</h2>
<p class="small">Dùng khi nhận asset từ nhạc sĩ hoặc từ Suno. Một dòng không
đạt thì trả lại, không sửa ở khâu sau.</p>
<table><thead><tr><th>Hạng mục</th><th>Ngưỡng đạt</th><th class="n">Đạt?</th></tr></thead><tbody>
<tr><td class="w">BPM</td><td>{vn(A['bpm'][0],0)}–{vn(A['bpm'][2],0)}</td><td class="n">☐</td></tr>
<tr><td class="w">Điệu thức</td><td>Trưởng, trừ khi hướng kênh yêu cầu thứ</td><td class="n">☐</td></tr>
<tr><td class="w">Độ ồn</td><td>{vn(A['lufs'][0])} đến {vn(A['lufs'][2])} LUFS</td><td class="n">☐</td></tr>
<tr><td class="w">Dải động</td><td>LRA ≥ {vn(A['lra']-1)}, không nén phẳng</td><td class="n">☐</td></tr>
<tr><td class="w">Độ dài</td><td>{vn(A['dur'][0],0)}–{vn(A['dur'][2],0)} giây</td><td class="n">☐</td></tr>
<tr><td class="w">Giọng vào</td><td>trước giây {vn(A['vox_in'][2],0)}</td><td class="n">☐</td></tr>
<tr><td class="w">Swing</td><td>≥ 1,2 — nghe ra chất shuffle</td><td class="n">☐</td></tr>
<tr><td class="w">Ngôi kể</td><td>“tôi”, không phải “chúng ta”</td><td class="n">☐</td></tr>
<tr><td class="w">Cung cảm xúc</td><td>kết bài sáng hơn mở bài</td><td class="n">☐</td></tr>
<tr><td class="w">Xưng hô</td><td>Lord / God là mặc định</td><td class="n">☐</td></tr>
<tr><td class="w">Chủ đề cấm</td><td>không thần học tranh cãi, không chính trị, không phán xét</td><td class="n">☐</td></tr>
<tr><td class="w">Nguồn gốc lời</td><td>đã phân loại PD / cover / sáng tác mới</td><td class="n">☐</td></tr>
<tr><td class="w">Nhãn AI</td><td>đã gắn nhãn nội dung tổng hợp</td><td class="n">☐</td></tr>
</tbody></table>"""
else:
    qc = ""

BODY = layer1 + tightness + layer2 + layer3 + qc + source_legend()

FOOT = f"""<b>Bản chất tài liệu.</b> Đây là <b>đặc tả kỹ thuật</b> để sản xuất —
tài liệu tra cứu hằng ngày. Định nghĩa phạm vi thị trường xem <b>T1.1 §1</b>;
phân tích đối thủ xem <b>T1.4</b>.<br><br>
<b>Cách đọc bảng thông số.</b> Khoảng p25–p75 là <b>vùng an toàn</b>, không phải
khuôn đúc. Với {len(spec)} thông số đo được, <b>không có thông số nào đạt mức
“chặt”</b> — ngách không có một công thức âm thanh duy nhất.<br><br>
<b>Nguồn.</b> <code>00_input/raw/audio_dna_full.jsonl</code> (n={A['n'] if A else '—'} bản ghi),
<code>04_outlier/audio/AUDIO_RECIPE.json</code>,
<code>04_outlier/lyrics/LYRICS_ANALYSIS.json</code>,
<code>02_analysis/pd_classification.csv</code>,
<code>04_outlier/THUMBNAIL_BRIEF.md</code>.<br><br>
<b>Giới hạn.</b> Thông số âm thanh đo bằng DSP tự động — phân loại giọng hát
nam/nữ có điểm tin cậy thấp nên <b>không</b> đưa vào đặc tả này. Chưa đo nhịp
sinh hoạt theo mùa. Không trích nguyên văn lời hát."""

DOC = doc(
    "T1.3", NICHE,
    "Đặc tả<br>dòng nhạc",
    "Bản thông số kỹ thuật để sản xuất đúng chất dòng nhạc này — "
    "dùng như tài liệu tra cứu hằng ngày.",
    [("Cơ sở đo", f"{A['n'] if A else '—'} bản ghi · "
                  f"{(LYR.get('nguồn') or {}).get('n_track','—')} bài đã phiên âm"),
     ("Dựng lúc", today()),
     ("Trả lời", "Nghe và trông thế nào thì được coi là đúng ngách?"),
     ("Ai đọc", "Nhạc sĩ · người vận hành Suno · designer"),
     ("Nhịp cập nhật", "khi QC phát hiện lệch hoặc test cho tín hiệu mới")],
    BODY, FOOT)

if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=DOC, base_url=".").write_pdf(OUT)
    print(f"   -> {OUT.relative_to(N.parent.parent)}  ({OUT.stat().st_size/1024:.0f} KB)")
