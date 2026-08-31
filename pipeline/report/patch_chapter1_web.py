#!/usr/bin/env python3
"""Sáu bản vá nội dung cho chương I · Phán quyết.

Sinh ra từ đợt review chương I. Chạy được nhiều lần (mỗi lần kiểm chuỗi gốc
còn nguyên rồi mới thay), chạy SAU patch_chapter1_data.py.

  1. Việc #3 «độ dài 1–3 giờ» -> nói rõ hai mục tiêu trái chiều
  2. Tách khoản phạt −2 thành hai nửa; sửa «gỡ 2đ» thành «gỡ 1đ»
  3. Trang 01: chốt điểm thấp vì trục KHÔNG sửa được
  4. Trang 01: thêm bảng 5 giả thuyết H1–H5
  5. Trang 01: ghi rõ RPM $3,0 có biên độ $1,5–6,0
  6. Trang 03: nêu tên 5 kênh trùng lặp nặng
"""
import pathlib, sys

WEB = (pathlib.Path(__file__).resolve().parent.parent.parent
       / "_web/ho-so.html")
PATCHES = []


def patch(name, old, new):
    PATCHES.append((name, old, new))


# ── 1 · TRANG 01: điểm thấp vì trục nào ─────────────────────────────────────
patch("01 · chốt trục kéo tụt",
"""   <div class="vb"><p><b>${esc(P.model)}</b></p>
    <p>Quy mô ngách chỉ <b>${kk(P.kpi.vpm)} view/tháng</b> nên một kênh không ăn hết.
     Nhưng <b>${dc(P.kpi.newok,1)}%</b> kênh mới đã vượt ngưỡng — cửa vào còn mở.</p></div>""",
"""   <div class="vb"><p><b>${esc(P.model)}</b></p>
    <p>Quy mô ngách chỉ <b>${kk(P.kpi.vpm)} view/tháng</b> nên một kênh không ăn hết.
     Nhưng <b>${dc(P.kpi.newok,1)}%</b> kênh mới đã vượt ngưỡng — cửa vào còn mở.</p>
    <p><b>Điểm thấp vì ngách nhỏ, không phải vì ngách dở.</b> Trục kéo tụt nhiều
     nhất là <b>${esc(worst.nm)}</b> (${dc(worst.sc,2)}/5, góp ${
      dc(worst.sc*worst.w*4,2)}đ) — và đó là trục <b>không sửa được</b>: thị trường
     lớn bao nhiêu là chuyện của thị trường. Trục mạnh nhất
     <b>${esc(best.nm)}</b> (${dc(best.sc,2)}/5) mới là thứ mình khai thác được.</p></div>""")

# ── 2 · TRANG 01: RPM có biên độ ────────────────────────────────────────────
patch("01 · biên độ RPM",
"""   ${srcs(['<b>Nguồn</b> _state/scores.json · rubric v'+P.rubric+' · chấm '+P.at,
     '<b>Công thức</b> pipeline/scoring/scoring_engine.py'])}`}""",
"""   <h2>Năm giả thuyết ban đầu — cái nào đã xác minh</h2>
   <p>Hồ sơ này bắt đầu từ năm giả thuyết. Trục điểm chỉ đáng tin đến mức
    giả thuyết chống lưng cho nó đáng tin.</p>
   <table class="tb"><thead><tr><th>Kết luận</th><th>Giả thuyết &amp; bằng chứng</th>
    </tr></thead><tbody>
   ${P.hyps.map(x=>`<tr><td><span class="tag ${
     x.v.startsWith('ĐÚNG')?'pos':x.v==='SAI'?'neg':'warn2'}">${esc(x.v)}</span></td>
    <td><b>${esc(x.h)}</b><br><span style="color:var(--mut);font-size:12.5px">${
     esc(x.e)}</span></td></tr>`).join('')}
   </tbody></table>
   <div class="caution"><div class="ct">H3 đúng ở mục tiêu nào</div>
    <div class="cd"><b>«Tối ưu» ở đây nghĩa là tối ưu doanh thu, không phải view.</b>
     Đo bằng view thì ngược lại: video dưới 10 phút ăn gấp
     <b>${dc(P.x.dur.ratio,2)}×</b> video trên 1 giờ, và kiểm trong từng kênh vẫn
     giữ (<b>${P.x.dur.n_better}/${P.x.dur.n_ch} kênh</b>). H3 vẫn đúng vì nhân
     với số điểm chèn quảng cáo thì video dài hơn <b>${dc(P.x.dur.rev_ratio,1)}×</b>
     — nhưng đó là hai thước đo khác nhau. Xem bảng đầy đủ ở trang
     «Làm gì trước», mặt Giải thích.</div></div>
   <div class="caution"><div class="ct">Điểm yếu lớn nhất của bảng điểm</div>
    <div class="cd"><b>H5 chưa xác minh</b>, mà H5 chính là thứ chống lưng cho trục
     «Khả năng kiếm tiền» — trục duy nhất có mức tin cậy <b>thấp</b>.
     RPM <b>$${dc(P.kpi.rpm,1)}</b> là con số <b>ước tính</b>, khoảng dao động
     <b>$1,5–6,0</b> — rộng gấp bốn lần. YouTube không công khai RPM theo ngách,
     và tuổi tự khai chỉ lấy được từ 1,28% mẫu bình luận. Nếu RPM thật rơi về
     $1,5 thì trục này tụt, kéo điểm tổng xuống dưới ${dc(P.score-0.8,2)}.</div></div>
   ${srcs(['<b>Nguồn</b> _state/scores.json · rubric v'+P.rubric+' · chấm '+P.at,
     '<b>Công thức</b> pipeline/scoring/scoring_engine.py',
     '<b>Giả thuyết</b> 99_report/_synthesis.json → hypotheses'])}`}""")

# ── 3 · TRANG 01: sửa «gỡ 2 điểm» thành «gỡ 1 điểm» ─────────────────────────
patch("01 · sửa điểm gỡ được (2 -> 1)",
"""   ${figs([{v:dc(P.score,2),l:`trên ${P.max} điểm`,c:VC},
     {v:dc(NEED,2),l:`điểm nữa là lên bậc «${NEXT?NEXT[1]:'—'}»`,c:'--cop'},
     {v:Math.abs(P.t6.p),l:'điểm lấy lại được chỉ bằng bỏ nội dung trùng lặp',c:'--pos'}])}</div>
   ${act(`<b>Rà ${vn(P.risk.cnt)} video trùng tiêu đề chéo kênh.</b>
    Riêng việc này đưa ${dc(P.score,2)} lên ${dc(P.score-P.t6.p,2)} — vượt mốc
    ${NEXT?NEXT[0]:''} của bậc trên.`,'điểm rubric sau khi rà xong')}`,""",
"""   ${figs([{v:dc(P.score,2),l:`trên ${P.max} điểm`,c:VC},
     {v:dc(NEED,2),l:`điểm nữa là lên bậc «${NEXT?NEXT[1]:'—'}»`,c:'--cop'},
     {v:Math.abs(FIXP),l:'điểm lấy lại được — phần còn lại không gỡ được',c:'--pos'}])}</div>
   ${act(`<b>Rà ${vn(P.risk.cnt)} video trùng tiêu đề chéo kênh.</b>
    Việc này đưa ${dc(P.score,2)} lên ${dc(P.score-FIXP,2)}. Khoản phạt còn lại
    (${dc(P.t6.p-FIXP,0)} điểm, rủi ro chủ đề tôn giáo) <b>không gỡ được bằng
    cách làm</b> — xem trang «Rủi ro».`,'điểm rubric sau khi rà xong')}`,""")

# ── 4 · Khai báo FIXP ───────────────────────────────────────────────────────
patch("khai báo FIXP",
"""  const worst=[...P.axes].sort((a,b)=>a.sc-b.sc)[0];
  const best=[...P.axes].sort((a,b)=>b.sc-a.sc)[0];""",
"""  const worst=[...P.axes].sort((a,b)=>a.sc-b.sc)[0];
  const best=[...P.axes].sort((a,b)=>b.sc-a.sc)[0];
  /* Khoản phạt −2 gồm hai nửa; chỉ nửa «trùng lặp» gỡ được bằng cách làm.
     Nửa «chủ đề tôn giáo» là rủi ro chính sách nền tảng, không đo được và
     không sửa được -> không được hứa gỡ cả 2 điểm. */
  const FIXP=P.x.pen.filter(x=>x.fix).reduce((a,b)=>a+b.p,0);""")

# ── 5 · TRANG 02: việc #3, hai mục tiêu trái chiều ──────────────────────────
patch("02 · độ dài hai nhánh",
"""  exp:`<p class="lead2">Vì sao xếp thứ tự này — số liệu chống lưng cho từng việc.</p>
   <div class="numlist">${P.acts.map(a=>`<div class="nli">
    <div class="nn">${a.n}</div><div class="nx2">
     <div class="nt">${esc(a.t)}</div>
     <div class="nd">${esc(a.why)}</div>
     <div class="nm2">Đo bằng: ${esc(a.kpi)}</div></div></div>`).join('')}</div>
   ${srcs(['<b>Nguồn</b> 99_report/BAO-CAO_Christian-Blues.pdf mục 10 · _state/metrics.json'])}`}""",
"""  exp:`<p class="lead2">Vì sao xếp thứ tự này — số liệu chống lưng cho từng việc.</p>
   <div class="numlist">${P.acts.map(a=>`<div class="nli">
    <div class="nn">${a.n}</div><div class="nx2">
     <div class="nt">${esc(a.t)}</div>
     <div class="nd">${esc(a.why)}</div>
     <div class="nm2">Đo bằng: ${esc(a.kpi)}</div></div></div>`).join('')}</div>

   <h2>Việc số 3 cần đọc kỹ — độ dài phục vụ hai mục tiêu trái ngược</h2>
   <p>Việc #3 khuyên làm video <b>1–3 giờ</b>. Lý do là số điểm chèn quảng cáo.
    Nhưng nếu đo bằng <b>view</b> thì kết luận ngược lại — và cả hai đều đúng,
    chỉ khác mục tiêu.</p>
   <table class="tb"><thead><tr><th>Dải độ dài</th><th class="num">Số video</th>
    <th class="num">View/ngày</th><th class="num">Điểm chèn QC</th>
    <th class="num">View/ngày × điểm chèn</th></tr></thead><tbody>
   ${P.x.dur.bands.map((b,i)=>`<tr>
     <td><b>${esc(b.nm)}</b></td><td class="num">${vn(b.n)}</td>
     <td class="num"><b style="color:var(${i===0?'--pos':'--mut'})">${dc(b.vpd,2)}</b></td>
     <td class="num">~${b.slot}</td>
     <td class="num"><b style="color:var(${i===2?'--pos':'--mut'})">${dc(b.rel,1)}</b></td>
    </tr>`).join('')}
   </tbody></table>
   <div class="scale"><b>Đọc hai cột cuối cùng lúc.</b> Muốn <b>view</b> thì làm
    ngắn — dưới 10 phút ăn gấp <b>${dc(P.x.dur.ratio,2)}×</b> video trên 1 giờ.
    Muốn <b>doanh thu</b> thì làm dài — nhân với số điểm chèn quảng cáo thì video
    dài hơn <b>${dc(P.x.dur.rev_ratio,1)}×</b>. Hai chiến lược khác nhau, không
    phải cái đúng cái sai.</div>
   <p><b>Đã kiểm trong từng kênh.</b> Chênh lệch trên có thể chỉ do kênh nào
    làm loại nào. Nên kiểm lại: trong <b>${P.x.dur.n_ch} kênh</b> làm cả video
    ngắn lẫn video dài, có <b>${P.x.dur.n_better}/${P.x.dur.n_ch} kênh</b> mà
    video ngắn ăn hơn chính video dài của mình, trung vị
    <b>${dc(P.x.dur.within,2)}×</b>. Hiệu ứng có thật, không phải ảo giác gộp kênh.</p>
   <p class="pull">Chọn độ dài là chọn mục tiêu: view để lớn nhanh, hay doanh thu
    trên mỗi lượt xem.</p>
   <div class="caution"><div class="ct">Cảnh báo cho người mới</div>
    <div class="cd">Nếu làm 1–3 giờ theo việc #3 rồi thấy view thấp hơn kỳ vọng,
     <b>đó không phải dấu hiệu làm sai</b> — đó là đặc tính của dải độ dài này.
     Đo bằng doanh thu trên 1.000 view, đừng đo bằng view.</div></div>
   ${srcs(['<b>Nguồn</b> 99_report/BAO-CAO_Christian-Blues.pdf mục 10 · _state/metrics.json',
     '<b>Độ dài</b> đo lại trực tiếp từ videos.parquet — '
      +vn(P.x.dur.bands.reduce((a,b)=>a+b.n,0))+' video đã đủ 60 ngày',
     '<b>Điểm chèn QC</b> ước tính ~1 điểm mỗi 8 phút, theo chính sách YouTube — '
      +'không đo được trực tiếp từ API'])}`}""")

# ── 6 · TRANG 03: tách khoản phạt + nêu tên 5 kênh ──────────────────────────
patch("03 · tách phạt + tên kênh",
"""   <p>Khoản phạt ${R.p} điểm là <b>phần gỡ được dễ nhất</b> trong toàn bộ bảng điểm.
    Bốn trục còn lại phụ thuộc thị trường — không đổi được. Riêng trục này phụ thuộc
    <b>cách mình làm</b>.<span class="qm" data-h="dup">?</span></p>
   ${srcs(['<b>Nguồn</b> 07_monetization/02_risk_register.csv · _state/metrics.json → risk'])}`}""",
"""   <h2>Khoản phạt ${R.p} điểm gồm hai nửa — chỉ một nửa gỡ được</h2>
   <p>Đây là chỗ dễ đọc nhầm nhất của cả hồ sơ. Bảng điểm trừ ${R.p} điểm, nhưng
    <b>không phải cả ${Math.abs(R.p)} điểm đều lấy lại được</b>.</p>
   <table class="tb"><thead><tr><th>Khoản trừ</th><th class="num">Điểm</th>
    <th>Gỡ được không</th></tr></thead><tbody>
   ${P.x.pen.map(x=>`<tr><td><b>${esc(x.nm)}</b><br>
     <span style="color:var(--mut);font-size:12.5px">${esc(x.ev)}</span></td>
    <td class="num"><b style="color:var(--neg)">${x.p}</b></td>
    <td>${x.fix
      ?'<span class="tag pos">GỠ ĐƯỢC</span><br><span style="color:var(--mut);font-size:12px">Rà tiêu đề và viết lại — nằm trong tầm tay.</span>'
      :'<span class="tag neg">KHÔNG</span><br><span style="color:var(--mut);font-size:12px">'+esc(x.why)+'</span>'}</td>
    </tr>`).join('')}
   </tbody></table>
   <p>Nghĩa là rà xong ${vn(R.cnt)} tiêu đề trùng thì điểm lên
    <b>${dc(P.score-P.x.pen.filter(x=>x.fix).reduce((a,b)=>a+b.p,0),2)}/${P.max}</b>,
    <b>không phải ${dc(P.score-R.p,2)}</b>. Phần còn lại là rủi ro chính sách nền
    tảng — không đo được từ dữ liệu, và không đổi được bằng cách làm.</p>

   <h2>Năm kênh đang trùng nặng nhất</h2>
   <p>Nêu tên để tra tận nơi — xem họ trùng cái gì, và tránh lặp lại.</p>
   <table class="tb"><thead><tr><th>Kênh</th><th class="num">Video trùng</th>
    <th class="num">Tổng video</th><th class="num">Tỷ lệ</th></tr></thead><tbody>
   ${P.x.dupch.map(c=>`<tr>
     <td><a class="shc" href="https://youtube.com/@${esc(c.ch)}" target="_blank"
      rel="noopener">@${esc(c.ch)}</a></td>
     <td class="num">${vn(c.d)}</td><td class="num">${vn(c.n)}</td>
     <td class="num"><b style="color:var(--neg)">${dc(c.pct,1)}%</b></td></tr>`).join('')}
   </tbody></table>
   <p class="small" style="color:var(--mut)">Đây là kênh công khai trên YouTube;
    tỷ lệ tính bằng số video dùng tiêu đề mà ít nhất một kênh khác cũng dùng.</p>
   ${srcs(['<b>Nguồn</b> 07_monetization/02_risk_register.csv · _state/metrics.json → risk',
     '<b>Kênh trùng</b> đo lại trực tiếp từ videos.parquet, ngưỡng ≥30% và ≥10 video'])}`}""")


def main():
    html = WEB.read_text(encoding="utf-8")
    done, skip = [], []
    for name, old, new in PATCHES:
        # Đã vá rồi thì chuỗi GỐC không còn nguyên vẹn trong file. Không so
        # bằng đầu chuỗi mới — bốn bản vá mở đầu y hệt bản gốc nên sẽ báo
        # nhầm là đã vá.
        if old not in html:
            if new in html:
                skip.append(name)
                continue
            print(f"✗ KHÔNG THẤY chuỗi gốc: {name}")
            sys.exit(1)
        html = html.replace(old, new, 1)
        done.append(name)
    WEB.write_text(html, encoding="utf-8")
    for d in done:
        print(f"  ✓ {d}")
    for s in skip:
        print(f"  · bỏ qua (đã vá): {s}")
    print(f"\n{len(done)} bản vá · {WEB.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
