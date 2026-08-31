#!/usr/bin/env python3
"""Sáu bản vá nội dung cho chương III · Nội dung.

Chạy sau patch_chapter3_data.py.

  1. Trang 08: sửa con số 1,03% bị lật ngược nghĩa.
  2. Trang 07: thêm cột kiểm trong-từng-kênh cho mọi chủ đề; nối scripture
     với phán quyết ở Phần V.
  3. Trang 09: chạy kiểm trùng thật cho 24 tiêu đề.
  4. Trang 08: sửa nhãn tiềm năng của khoảng trống #1 cho khớp chứng cứ.
  5. Trang 07: hiện đủ 16 chủ đề thay vì cắt còn 8.
  6. Trang 07: ghi rõ chủ đề chồng lấn nhau.
"""
import pathlib, sys

WEB = pathlib.Path(__file__).resolve().parent.parent.parent / "_web/ho-so.html"
PATCHES = []


def patch(name, old, new):
    PATCHES.append((name, old, new))


# ── 1 · TRANG 07: bảng đủ 16 chủ đề + cột trong-từng-kênh + chồng lấn ───────
patch("07 · bảng 16 chủ đề, thêm cột trong-kênh",
"""   <table class="tb"><thead><tr><th>Chủ đề</th><th>Video</th><th>Đang làm</th>
    <th>Lift</th></tr></thead><tbody>
   ${P.themes.slice(0,8).map(t=>`<tr>
    <td>${esc(t.t)} ${rec.has(t.t)?'<span class="tag pos">nên thử</span>':
      avo.has(t.t)?'<span class="tag neg">tránh</span>':''}</td>
    <td class="num">${vn(t.n)}</td><td class="num">${dc(t.sh,2)}%</td>
    <td class="num" style="color:var(${t.lift>=1.2?'--pos':t.lift<1?'--neg':'--mut'})">${
      dc(t.lift,2)}×</td></tr>`).join('')}</tbody></table>
   ${srcs(['<b>Nguồn</b> 06_keyword/02_theme_scores.csv · '+P.themes.length+' chủ đề kiểm định'])}`}""",
"""   <h2>Cả ${P.themes.length} chủ đề — kèm kiểm trong từng kênh</h2>
   <p>Cột <b>lift</b> so video có chủ đề với video không có, trên toàn thị trường.
    Cột <b>trong kênh</b> hỏi câu chặt hơn: <i>cùng một kênh, khi làm chủ đề này
    có thắng chính mình không?</i> Hai cột lệch nhau nghĩa là tín hiệu đến từ
    <b>kênh nào làm</b>, không phải <b>chủ đề gì</b>.</p>
   <table class="tb"><thead><tr><th>Chủ đề</th><th class="num">Video</th>
    <th class="num">Đang làm</th><th class="num">Lift</th>
    <th class="num">Trong kênh</th><th>Đọc là</th></tr></thead><tbody>
   ${P.themes.map(t=>{const w=P.x3.within[t.t]||{};
    const flip=w.within!=null&&((t.lift>=1.2&&w.within<1)||(t.lift<0.85&&w.within>=1.1));
    return `<tr>
    <td><b>${esc(t.t)}</b> ${rec.has(t.t)?'<span class="tag pos">nên thử</span>':
      avo.has(t.t)?'<span class="tag neg">tránh</span>':''}</td>
    <td class="num">${vn(t.n)}</td><td class="num">${dc(t.sh,2)}%</td>
    <td class="num" style="color:var(${t.lift>=1.2?'--pos':t.lift<1?'--neg':'--mut'})">${
      dc(t.lift,2)}×</td>
    <td class="num">${w.within!=null
      ?`<b style="color:var(${w.within>=1.1?'--pos':w.within<0.9?'--neg':'--mut'})">${
        dc(w.within,2)}×</b><br><span style="color:var(--fnt);font-size:11px">${
        w.n_better}/${w.n_ch} kênh</span>`
      :'<span style="color:var(--fnt);font-size:11px">chưa đủ kênh</span>'}</td>
    <td style="font-size:12px;color:var(--mut)">${
      w.within==null?'không kiểm được'
      :flip&&t.lift<0.85?'<b style="color:var(--warn)">mặt bằng kém nhưng trong kênh vẫn tốt</b>'
      :flip?'<b style="color:var(--warn)">lift thô đến từ kênh, không từ chủ đề</b>'
      :w.within>=1.1?'nhất quán — tin được'
      :w.within<0.9?'kém ở cả hai phép đo':'ngang mặt bằng'}</td></tr>`}).join('')}
   </tbody></table>

   <div class="scale"><b>Các chủ đề chồng lấn nhau.</b> Cộng cột «đang làm» được
    <b>${dc(P.x3.overlap,1)}%</b>, lớn hơn 100% — vì một video có thể vừa nói về
    cầu nguyện vừa nói về chữa lành. Đây <b>không</b> phải cách chia thị trường
    thành các phần rời nhau.</div>

   <h2>Một chủ đề bị chấm «tránh» oan</h2>
   <p><b>scripture</b> có lift thô <b>${dc(P.themes.find(t=>t.t==='scripture').lift,2)}×</b>
    nên bị xếp vào nhóm tránh. Nhưng kiểm trong từng kênh lại cho
    <b>${dc(P.x3.within.scripture.within,2)}×</b> —
    ${P.x3.within.scripture.n_better}/${P.x3.within.scripture.n_ch} kênh làm chủ
    đề này <b>thắng chính mình</b>.</p>
   <p>Nghĩa là: nhiều kênh yếu cùng làm scripture nên kéo tụt mặt bằng, nhưng kênh
    nào làm giỏi thì vẫn ăn. Đây là <b>nghịch lý Simpson theo chiều ngược lại</b> —
    hồ sơ đã dùng phép kiểm này để loại bốn chủ đề trông đẹp mà rỗng, nhưng chưa
    dùng để cứu chủ đề trông xấu mà thật.</p>
   <div class="scale"><b>Phần V xếp chủ đề này là «khó, ai làm giỏi thì ăn»</b> —
    không phải «tránh». Xem trang <b>Thánh Vịnh phổ nhạc Blues</b> ở chương
    «Chọn hướng» để biết làm thế nào cho đúng.</div>
   ${srcs(['<b>Nguồn</b> 06_keyword/02_theme_scores.csv · '+P.themes.length+' chủ đề kiểm định',
     '<b>Kiểm trong kênh</b> đo lại trực tiếp từ videos.parquet — chỉ tính kênh có '
      +'ít nhất 5 video mỗi phía'])}`}""")

# ── 2 · TRANG 08: sửa con số bị lật nghĩa ──────────────────────────────────
patch("08 · sửa 1,03% bị lật nghĩa",
"""   <div class="vb"><p><b>${dc(P.ctx.find(c=>c.k==='prayer_devo').p,1)}%</b> bình luận nhắc
    cầu nguyện — bối cảnh số một. Nhưng chỉ <b>1,03%</b> video làm nội dung có lời
    cho mục này.</p>
   <p>Instrumental đã được chứng minh <b>thất bại</b> ở ngách này (lift 0,17×).</p></div></div>""",
"""   <div class="vb"><p><b>${dc(P.ctx.find(c=>c.k==='prayer_devo').p,1)}%</b> bình luận nhắc
    cầu nguyện — bối cảnh số một, bỏ xa phần còn lại.</p>
   <p><b>Nhưng phía cung không còn trống.</b> Đo lại trực tiếp: đã có
    <b>${dc(P.x3.prayer.lyric_pct,1)}%</b> video
    (${vn(P.x3.prayer.lyric_n)} video) làm nhạc <b>có lời</b> cho bối cảnh này.
    Cơ hội ở đây <b>không phải</b> «chưa ai làm», mà là <b>làm khác đi</b> —
    xem chương «Chọn hướng».</p>
   <p>Thứ thật sự trống là chỗ <b>không nên bước vào</b>: chỉ
    ${dc(P.x3.prayer.ins_pct,2)}% video làm instrumental cho cầu nguyện, và chúng
    chạy <b>${dc(P.x3.prayer.ratio,1)}× kém hơn</b> nhóm có lời
    (${dc(P.x3.prayer.ins_vpd,2)} so với ${dc(P.x3.prayer.lyric_vpd,2)} view/ngày).
    Trống vì <b>không ăn</b>, không phải vì chưa ai nghĩ ra.</p></div></div>""")

# ── 3 · TRANG 08: bảng phía cung + sửa nhãn tiềm năng ──────────────────────
patch("08 · bảng cung thật + nhãn tiềm năng",
"""  exp:`<p class="lead2">Mỗi khoảng trống có bằng chứng phía cầu, mức khai thác phía cung,
    và hiệu quả đo được của những ai đã làm.<span class="qm" data-h="gap">?</span></p>""",
"""  exp:`<p class="lead2">Mỗi khoảng trống có bằng chứng phía cầu, mức khai thác phía cung,
    và hiệu quả đo được của những ai đã làm.<span class="qm" data-h="gap">?</span></p>

   <div class="caution"><div class="ct">Đọc nhãn «tiềm năng» cùng với nhãn «tin cậy»</div>
    <div class="cd">Hai nhãn nói hai chuyện khác nhau. <b>Tiềm năng</b> ước lượng
     phần thưởng nếu đúng; <b>tin cậy</b> nói bằng chứng có chắc không. Khoảng
     trống <b>#1</b> gắn tiềm năng CAO nhưng tin cậy <b>Thấp</b> — vì trong từng
     kênh chỉ 1,05× (4/8 kênh). Đọc riêng nhãn tiềm năng sẽ hiểu nhầm là chắc ăn.
     <b>Chỉ khoảng trống #3 và #5 có tin cậy Cao.</b></div></div>

   <h2>Phía cung của khoảng trống «cầu nguyện» — đo lại trực tiếp</h2>
   <p>Đây là chỗ hồ sơ từng ghi sai. Bảng dưới đo thẳng từ dữ liệu video.</p>
   <table class="tb"><thead><tr><th>Nhóm</th><th class="num">Video</th>
    <th class="num">Tỷ lệ</th><th class="num">View/ngày</th></tr></thead><tbody>
   <tr><td><b>Cầu nguyện + có lời</b></td>
    <td class="num">${vn(P.x3.prayer.lyric_n)}</td>
    <td class="num"><b>${dc(P.x3.prayer.lyric_pct,1)}%</b></td>
    <td class="num"><b style="color:var(--pos)">${dc(P.x3.prayer.lyric_vpd,2)}</b></td></tr>
   <tr><td>Cầu nguyện + instrumental</td>
    <td class="num">${vn(P.x3.prayer.ins_n)}</td>
    <td class="num">${dc(P.x3.prayer.ins_pct,2)}%</td>
    <td class="num"><b style="color:var(--neg)">${dc(P.x3.prayer.ins_vpd,2)}</b></td></tr>
   <tr><td>Còn lại</td><td class="num">—</td><td class="num">—</td>
    <td class="num">${dc(P.x3.prayer.rest_vpd,2)}</td></tr>
   </tbody></table>
   <p class="pull">Gần một nửa thị trường đã làm nhạc có lời cho cầu nguyện.
    Đây không phải chỗ trống — đây là chỗ đông nhất.</p>
   <p>Kết luận đúng rút ra từ bảng: <b>đừng làm instrumental</b>
    (${dc(P.x3.prayer.ratio,1)}× kém hơn). Còn muốn tìm chỗ chưa ai chiếm thì
    phải chia nhỏ hơn mức «có lời hay không lời» — đó chính là việc mà chương
    <b>Chọn hướng</b> làm.</p>""")

# ── 4 · TRANG 09: kiểm trùng thật ──────────────────────────────────────────
patch("09 · kiểm trùng 24 tiêu đề",
"""   <table class="tb"><thead><tr><th style="width:6%">#</th><th>Tiêu đề</th>
    <th style="width:22%">Căn cứ</th><th style="width:12%">Dài</th></tr></thead><tbody>
   ${P.ideas.map(i=>`<tr><td class="num">${i.n}</td><td>${esc(i.t)}</td>
    <td style="font-size:12px;color:var(--mut)">${esc(i.b)}</td>
    <td class="num">${esc(i.l)}</td></tr>`).join('')}</tbody></table>""",
"""   <div class="scale"><b>Đã kiểm trùng với thị trường.</b>
    <b>${P.x3.n_exact}/${P.ideas.length}</b> tiêu đề trùng nguyên văn với video đã
    có. Nhưng <b>${P.x3.n_dup}/${P.ideas.length}</b> chứa một cụm 4–6 từ đã xuất
    hiện ở ít nhất 3 video khác — cột <b>Trùng cụm</b> đánh dấu, sửa lại trước
    khi dùng.</div>
   <table class="tb"><thead><tr><th style="width:5%">#</th><th>Tiêu đề</th>
    <th style="width:20%">Căn cứ</th><th style="width:9%">Dài</th>
    <th style="width:22%">Trùng cụm</th></tr></thead><tbody>
   ${P.ideas.map(i=>{const d=P.x3.dups.find(x=>x.n===i.n)||{};
    return `<tr><td class="num">${i.n}</td><td>${esc(i.t)}</td>
    <td style="font-size:12px;color:var(--mut)">${esc(i.b)}</td>
    <td class="num">${esc(i.l)}</td>
    <td style="font-size:11.5px">${d.gram
      ?`<span class="tag neg">${d.cnt} video</span><br>
        <span style="font-family:var(--mono);font-size:10.5px;color:var(--mut)">«${
         esc(d.gram)}»</span>`
      :'<span class="tag pos">sạch</span>'}</td></tr>`}).join('')}</tbody></table>""")

# ── 5 · TRANG 09: giải thích cách kiểm ─────────────────────────────────────
patch("09 · giải thích kiểm trùng",
"""   <div class="caution"><div class="ct">Đây là điểm khởi đầu, không phải bản cuối</div>
    <div class="cd">Tiêu đề sinh tự động cần người đọc lại — nhất là để tránh trùng
     với tiêu đề đã có trên thị trường (xem trang <b>Rủi ro</b>).</div></div>
   ${srcs(['<b>Nguồn</b> 99_report/_synthesis.json → ideas · 09_playbook/CHANNEL_PLAYBOOK.json → title.patterns'])}`}""",
"""   <h2>Kiểm trùng lặp — cách làm và kết quả</h2>
   <p>Trang <b>Rủi ro</b> nói trùng tiêu đề là khoản phạt nặng nhất của ngách.
    Nên ${P.ideas.length} tiêu đề này phải tự kiểm trước khi đem dùng.</p>
   <p><b>Cách kiểm:</b> cắt mỗi tiêu đề thành mọi cụm 4, 5, 6 từ liên tiếp, rồi
    tra xem cụm đó đã xuất hiện ở bao nhiêu video trong toàn ngách. Từ 3 video
    trở lên thì coi là cụm <b>đã có người dùng</b>.</p>
   <table class="tb"><thead><tr><th>Phép kiểm</th><th class="num">Kết quả</th>
    <th>Nghĩa là</th></tr></thead><tbody>
   <tr><td>Trùng nguyên văn cả tiêu đề</td>
    <td class="num"><b style="color:var(--pos)">${P.x3.n_exact}/${P.ideas.length}</b></td>
    <td>không tiêu đề nào bị chép lại nguyên</td></tr>
   <tr><td>Chứa cụm 4–6 từ đã có (≥3 video)</td>
    <td class="num"><b style="color:var(--neg)">${P.x3.n_dup}/${P.ideas.length}</b></td>
    <td>cần viết lại phần cụm đó trước khi đăng</td></tr>
   </tbody></table>
   ${P.x3.n_dup?`<p><b>Cụm bị lặp nhiều nhất trong chính ${P.ideas.length} tiêu đề
    này:</b> ${(()=>{const c={};P.x3.dups.forEach(d=>{if(d.gram)c[d.gram]=(c[d.gram]||0)+1});
    return Object.entries(c).sort((a,b)=>b[1]-a[1]).slice(0,3)
     .map(([g,n])=>`«${esc(g)}» (dùng ${n} lần)`).join(' · ')})()}.
    Bản thân việc một khuôn được dùng lại nhiều lần cũng là rủi ro — dù cụm đó
    chưa phổ biến trên thị trường.</p>`:''}
   <div class="caution"><div class="ct">Đây là điểm khởi đầu, không phải bản cuối</div>
    <div class="cd">Kiểm trùng ở trên chỉ bắt được <b>trùng mặt chữ</b>. Trùng
     <b>ý tưởng</b> — cùng góc, cùng cảm xúc, cùng lời hứa — thì máy không đo
     được, vẫn cần người đọc lại.</div></div>
   ${srcs(['<b>Nguồn</b> 99_report/_synthesis.json → ideas · 09_playbook/CHANNEL_PLAYBOOK.json → title.patterns',
     '<b>Kiểm trùng</b> đối chiếu với '+vn(P.x3.prayer.n_all)
      +' video đã đủ 60 ngày · cụm 4–6 từ, ngưỡng ≥3 video'])}`}""")



# ── 6 · TRANG 08: tiêu đề và việc-cần-làm còn nói theo con số cũ ───────────
patch("08 · tiêu đề + việc cần làm",
"""   <div class="vs">Cầu lớn nhất chưa ai định vị riêng: nhạc CÓ LỜI cho cầu nguyện.</div>""",
"""   <div class="vs">Cầu lớn nhất đã đông người làm — cơ hội nằm ở cách làm khác.</div>""")

patch("08 · sửa việc cần làm",
"""   ${act(`<b>Làm nhạc CÓ LỜI cho bối cảnh cầu nguyện.</b> Đây là khoảng trống
    độ tin cậy cao nhất.`,'view trung vị so với dải 1–3h của thị trường')}`,""",
"""   ${act(`<b>Đừng chọn khoảng trống theo nhãn «tiềm năng CAO» — chọn theo nhãn
    «tin cậy».</b> Chỉ hai khoảng trống có tin cậy <b>Cao</b>: mix dài 1–3h
    (#3) và định vị «yêu nhạc blues, cần lời sạch» (#5). Ba khoảng còn lại cần
    thử ở quy mô nhỏ trước.`,
    'view/ngày sau 10 video, so với mặt bằng kênh mình — KHÔNG so thị trường')}`,""")


def main():
    html = WEB.read_text(encoding="utf-8")
    done, skip = [], []
    for name, old, new in PATCHES:
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
