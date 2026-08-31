#!/usr/bin/env python3
"""Sáu bản vá nội dung cho chương IV · Công thức tái tạo.

Chạy sau patch_chapter4_data.py.

  1. Trang 14: thay bảng view-trong-top bằng tỷ lệ vào top.
  2. Trang 14: tách «5,3x tổng view» thành phần phép nhân và phần đòn bẩy.
  3. Trang 15: ghi rõ mẫu 12/53 kênh và hai mô hình chênh 1,07x.
  4. Trang 16: thêm cột độ chín, cảnh báo kênh dưới 60%.
  5. Trang 10: nói rõ 41 kênh là mẫu top 5%, không phải toàn ngách.
  6. Trang 14: nối với bảng độ dài ở chương I.
"""
import pathlib, sys

WEB = pathlib.Path(__file__).resolve().parent.parent.parent / "_web/ho-so.html"
PATCHES = []


def patch(name, old, new):
    PATCHES.append((name, old, new))


# ── 1 · TRANG 10: nói rõ mẫu là top 5% ─────────────────────────────────────
patch("10 · nói rõ cỡ mẫu",
"""   ${figs([{v:vn(B.from.n_videos),l:'video top 5% được đo'},
     {v:B.from.n_channels,l:'kênh'},
     {v:'≥'+kk(B.from.view_threshold),l:'ngưỡng lọt mẫu'}])}</div>`,""",
"""   ${figs([{v:vn(B.from.n_videos),l:'video top 5% được đo'},
     {v:B.from.n_channels+'/'+P.x4.n_ch_all,l:'kênh có video lọt mẫu',c:'--cop'},
     {v:'≥'+kk(B.from.view_threshold),l:'ngưỡng lọt mẫu'}])}</div>
   <div class="scale"><b>Đây là mẫu của nhóm thắng, không phải của cả ngách.</b>
    ${B.from.n_channels} kênh trên tổng ${P.x4.n_ch_all} kênh có ít nhất một video
    vượt ${vn(B.from.view_threshold)} view. Mọi tỉ lệ trong chương này mô tả
    <b>nhóm đã thành công</b> — nên chúng nói được «người thắng trông như thế nào»,
    <b>không</b> nói được «làm thế thì sẽ thắng». Muốn biết vế sau thì phải so
    nhóm thắng với nhóm thua, và đó là việc chương <b>Chọn hướng</b> làm.</div>`,""")

# ── 2 · TRANG 14: thay bảng thời lượng ─────────────────────────────────────
patch("14 · tỷ lệ vào top thay view-trong-top",
"""   ${fig('Hình 13 · Bốn dải thời lượng đều chạy được',
    chBars((F.duration_options||[]).map(o=>({k:o.band,v:o.view_median,lb:kk(o.view_median),
     hi:o.share===Math.max(...F.duration_options.map(x=>x.share))})),470),
    esc(F.note||''))}""",
"""   <h2>Bốn dải thời lượng — đo lại cho đúng</h2>
   <div class="caution"><div class="ct">Bảng cũ đã lọc theo view rồi mới so view</div>
    <div class="cd">Con số «view trung vị» trước đây tính trên
     <b>nhóm đã lọt top</b> (≥${vn(P.pb.from.view_threshold)} view). Đã sàng theo
     view rồi thì mọi nhóm còn lại tất nhiên đều đông view như nhau — phép đo đó
     <b>không thể</b> cho biết dải nào dễ thắng hơn.</div></div>
   <p>Phép đo đúng là hỏi ngược: <b>trong toàn bộ video mỗi dải, bao nhiêu phần
    trăm lọt được vào top?</b></p>
   <table class="tb"><thead><tr><th>Dải thời lượng</th><th class="num">Tổng video</th>
    <th class="num">Lọt top</th><th class="num">Tỷ lệ vào top</th>
    <th class="num">View/ngày cả dải</th></tr></thead><tbody>
   ${P.x4.entry.bands.map(b=>`<tr><td><b>${esc(b.nm)}</b></td>
    <td class="num">${vn(b.n)}</td><td class="num">${vn(b.n_top)}</td>
    <td class="num"><b style="color:var(${b.rate>=P.x4.entry.hi-0.2?'--pos':'--mut'})">${
      dc(b.rate,2)}%</b></td>
    <td class="num">${dc(b.vpd,1)}</td></tr>`).join('')}
   </tbody></table>
   <p><b>Kết luận cũ vẫn đúng, nhưng giờ có căn cứ đúng.</b> Tỷ lệ vào top nằm
    trong khoảng <b>${dc(P.x4.entry.lo,2)}–${dc(P.x4.entry.hi,2)}%</b> — chênh
    nhau chỉ ${dc(P.x4.entry.spread,2)}×. Không dải nào dễ thắng hơn hẳn.</p>
   <div class="scale"><b>Nhưng cột cuối kể chuyện khác.</b> Tính trên
    <b>toàn bộ</b> video chứ không riêng nhóm thắng, video ngắn có view/ngày cao
    hơn hẳn (${dc(P.x4.entry.bands[0].vpd,1)} so với
    ${dc(P.x4.entry.bands[2].vpd,1)} của dải 40–80 phút). Hai điều này không mâu
    thuẫn: <b>cơ hội vào top thì như nhau, nhưng mức trung bình thì khác nhau</b>.
    Chương <b>Phán quyết</b> có bảng đầy đủ — ngắn ăn view gấp
    ${dc(P.x.dur.ratio,2)}×, dài ăn doanh thu gấp ${dc(P.x.dur.rev_ratio,1)}× nhờ
    số điểm chèn quảng cáo.</div>
   <p class="pull">Chọn thời lượng theo mục tiêu và bối cảnh nghe, không theo kỳ
    vọng thuật toán ưu ái dải nào.</p>""")

# ── 3 · TRANG 14: tách con số nhịp đăng ────────────────────────────────────
patch("14 · tách 5,3x tổng view",
"""   <p><b>Nhịp đăng:</b> nhóm dẫn đầu ${dc(C.videos_per_week,1)} video/tuần,
    nhóm mạnh tay ${dc(C.videos_per_week_aggressive,1)}. ${esc(C.note||'')}</p>
   ${srcs(['<b>Nguồn</b> CHANNEL_PLAYBOOK.json → description · tags · format · cadence'])}`}""",
"""   <h2>Nhịp đăng — con số «gấp 5,3 lần» cần tách làm hai</h2>
   <p>Nhóm dẫn đầu đăng <b>${dc(C.videos_per_week,1)} video/tuần</b>, nhóm mạnh tay
    <b>${dc(C.videos_per_week_aggressive,1)}</b>. Ghi chú gốc nói nhóm đăng dày đạt
    tổng view gấp 5,3 lần nhóm thưa. Nhưng <b>phần lớn con số đó là phép nhân</b>:
    đăng nhiều video hơn thì tổng view cao hơn, gần như theo định nghĩa.</p>
   <table class="tb"><thead><tr><th>Nhóm</th><th class="num">Video đã chín</th>
    <th class="num">Tổng view</th><th class="num">View/ngày mỗi video</th>
    </tr></thead><tbody>
   <tr><td>Đăng thưa — dưới ${dc(P.x4.cad.q25,1)} video/tuần</td>
    <td class="num">${vn(P.x4.cad.n_lo)}</td>
    <td class="num">${vn(P.x4.cad.tot_lo)}</td>
    <td class="num">${dc(P.x4.cad.vpd_lo,1)}</td></tr>
   <tr><td>Đăng dày — trên ${dc(P.x4.cad.q75,1)} video/tuần</td>
    <td class="num">${vn(P.x4.cad.n_hi)}</td>
    <td class="num">${vn(P.x4.cad.tot_hi)}</td>
    <td class="num">${dc(P.x4.cad.vpd_hi,1)}</td></tr>
   <tr><td><b>Chênh lệch</b></td><td class="num">—</td>
    <td class="num"><b>${dc(P.x4.cad.tot_ratio,1)}×</b></td>
    <td class="num"><b style="color:var(--pos)">${dc(P.x4.cad.vpd_ratio,2)}×</b></td></tr>
   </tbody></table>
   <p>Nhóm đăng dày có <b>${vn(P.x4.cad.n_hi)}</b> video đã chín, nhóm thưa chỉ
    <b>${vn(P.x4.cad.n_lo)}</b> — hơn ${dc(P.x4.cad.n_hi/P.x4.cad.n_lo,1)} lần.
    Nên tổng view gấp ${dc(P.x4.cad.tot_ratio,1)}× là điều phải xảy ra.</p>
   <p class="pull">Con số đáng nói là ${dc(P.x4.cad.vpd_ratio,2)}× — mỗi video của
    kênh đăng dày vẫn được nhiều view hơn một chút. Đó mới là đòn bẩy thật, và nó
    nhỏ hơn nhiều so với ấn tượng «gấp 5 lần».</p>
   <div class="scale"><b>Vì sao vẫn nên đăng dày.</b> Không phải vì mỗi video sẽ
    bùng nổ, mà vì <b>nhiều lượt thử hơn</b>: cùng tỷ lệ trúng, ai đăng nhiều hơn
    thì có nhiều video trúng hơn. Mô hình «mở 2–3 kênh song song» ở chương
    <b>Phán quyết</b> dựa trên đúng logic này.</p>
   ${srcs(['<b>Nguồn</b> CHANNEL_PLAYBOOK.json → description · tags · format · cadence',
     '<b>Thời lượng &amp; nhịp đăng</b> đo lại trực tiếp từ videos.parquet — '
      +P.x4.cad.n_ch+' kênh có ít nhất 90 ngày hoạt động và 10 video'])}`}""")

# ── 4 · TRANG 15: cỡ mẫu mô hình kênh ──────────────────────────────────────
patch("15 · cỡ mẫu mô hình",
"""  exp:`<p class="lead2">Hai mô hình này đòi hỏi <b>khối lượng công việc và loại nội dung
    khác hẳn nhau</b>. Chọn nhầm giữa chừng là làm lại từ đầu.</p>""",
"""  exp:`<p class="lead2">Hai mô hình này đòi hỏi <b>khối lượng công việc và loại nội dung
    khác hẳn nhau</b>. Chọn nhầm giữa chừng là làm lại từ đầu.</p>

   <div class="caution"><div class="ct">Đọc cỡ mẫu trước khi coi đây là hai con đường tách bạch</div>
    <div class="cd">Hai mô hình dựng từ <b>${P.x4.n_ch_prof} kênh</b> trong tổng
     <b>${P.x4.n_ch_all} kênh</b> của ngách — ${prof.map(p=>p.n_kênh_trong_top12).join(' và ')}
     kênh mỗi bên. Với cỡ mẫu ấy, mọi con số dưới đây là <b>mô tả vài kênh cụ thể</b>,
     không phải quy luật của ngách.<br><br>
     Và chúng <b>không cách nhau xa</b>: view mỗi video chênh chỉ
     <b>${dc(P.x4.prof_gap,2)}×</b>
     (${vn(prof[0].view_mỗi_video)} so với ${vn(prof[1].view_mỗi_video)}). Cả hai
     đều chạy được — điều quan trọng là <b>chọn một và làm cho tới</b>, chứ không
     phải chọn đúng cái mạnh hơn.</div></div>""")

# ── 5 · TRANG 16: cột độ chín ──────────────────────────────────────────────
patch("16 · cột độ chín",
"""   <table class="tb"><thead><tr><th>Kênh</th><th>View/video</th><th>Video</th>
    <th>Tuổi</th></tr></thead><tbody>
   ${eff.map(e=>`<tr><td style="font-family:var(--mono);color:var(--ind)">@${esc(e.h)}</td>
    <td class="num"><b>${kk(e.vpv)}</b></td><td class="num">${vn(e.n)}</td>
    <td class="num">${dc(e.age,1)} th</td></tr>`).join('')}</tbody></table>""",
"""   <table class="tb"><thead><tr><th>Kênh</th><th class="num">View/video</th>
    <th class="num">Video</th><th class="num">Tuổi</th>
    <th class="num">Đã đủ 60 ngày</th></tr></thead><tbody>
   ${eff.map(e=>{const mt=P.x4.mature[e.h]||{};
    const young=mt.pct!=null&&mt.pct<60;
    return `<tr><td style="font-family:var(--mono);color:var(--ind)">@${esc(e.h)}</td>
    <td class="num"><b>${kk(e.vpv)}</b>${young?' <span class="tag warn2">tính thiếu</span>':''}</td>
    <td class="num">${vn(e.n)}</td>
    <td class="num">${dc(e.age,1)} th</td>
    <td class="num" style="color:var(${young?'--warn':'--mut'})">${
      mt.pct!=null?dc(mt.pct,0)+'%':'—'}<br>
     <span style="color:var(--fnt);font-size:11px">${vn(mt.mat||0)}/${vn(mt.n||0)}</span></td>
    </tr>`}).join('')}</tbody></table>
   ${(()=>{const y=eff.filter(e=>(P.x4.mature[e.h]||{}).pct<60);
    return y.length?`<div class="caution"><div class="ct">Một con số bị tính thiếu</div>
     <div class="cd">${y.map(e=>'<b>@'+esc(e.h)+'</b>').join(', ')} mới
      ${dc(y[0].age,1)} tháng tuổi, chỉ
      <b>${dc(P.x4.mature[y[0].h].pct,0)}%</b> video đã đủ 60 ngày. Video mới chưa
      kịp tích view, nên view/video của kênh này <b>thấp hơn thực lực</b> — xếp
      hạng ở đây là mức sàn, không phải mức thật.<br><br>
      Đây chính là <b>bẫy độ chín</b>: so kênh trẻ với kênh già bằng view trung
      bình luôn thiệt cho kênh trẻ, vì view cần thời gian mới tích được.</div></div>`
    :''})()}""")

# ── 6 · TRANG 16: giải thích ngưỡng chín trong phần Giải thích ─────────────
patch("16 · ghi chú độ chín ở mặt giải thích",
"""   <p>Đây là cách nhanh nhất để hiểu công thức ở chương này trông ra sao ngoài thực tế.
    Công thức mô tả <b>trung bình của nhóm dẫn đầu</b>; nhìn kênh cụ thể mới thấy
    họ <b>chệch khỏi trung bình ở đâu</b> — và chỗ chệch đó thường là chỗ đáng học nhất.</p>""",
"""   <p>Đây là cách nhanh nhất để hiểu công thức ở chương này trông ra sao ngoài thực tế.
    Công thức mô tả <b>trung bình của nhóm dẫn đầu</b>; nhìn kênh cụ thể mới thấy
    họ <b>chệch khỏi trung bình ở đâu</b> — và chỗ chệch đó thường là chỗ đáng học nhất.</p>
   <div class="scale"><b>Vì sao chỉ tính video đã đủ 60 ngày.</b> Một video mới đăng
    hôm qua có view thấp không phải vì nó dở, mà vì nó chưa có thời gian. Trộn video
    mới vào phép tính sẽ kéo tụt mọi kênh đang đăng đều — nhất là kênh trẻ, vốn có
    tỷ lệ video mới cao nhất. Cột <b>«đã đủ 60 ngày»</b> cho biết mỗi kênh có bao
    nhiêu phần dữ liệu thật sự dùng được.</div>""")


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
