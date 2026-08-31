#!/usr/bin/env python3
"""Sáu bản vá nội dung cho chương II · Khán giả.

Sinh ra từ đợt review chương II. Chạy sau patch_chapter2_data.py.

  1. Trang 04: câu chốt đang lấy nhóm n=4 (bị chấm YẾU) làm «nhóm phản ứng
     mạnh nhất». Đổi sang nhóm duy nhất được XÁC NHẬN.
  2. Trang 04: gắn nhãn phán quyết lên từng thẻ nhóm.
  3. Trang 04: ghi rõ 4 nhóm chỉ phủ 16,7% bình luận.
  4. Trang 05: 13,5% là trên TỔNG bình luận; trong nhóm có nêu bối cảnh thì
     cầu nguyện chiếm 61%.
  5. Trang 06: bỏ khuyến nghị dùng amen/thank — cả 7 từ đều ≤1,00× nền.
  6. Trang 06: thay bằng từ đã qua kiểm định (finally 5,0× · never heard 9,0×).
"""
import pathlib, sys

WEB = pathlib.Path(__file__).resolve().parent.parent.parent / "_web/ho-so.html"
PATCHES = []


def patch(name, old, new):
    PATCHES.append((name, old, new))


# ── 1 · TRANG 04: câu chốt lấy nhóm đã qua kiểm định ────────────────────────
patch("04 · câu chốt dùng nhóm XÁC NHẬN",
""" f(){const ps=[...P.pers].sort((a,b)=>b.n-a.n), top=ps[0];
  const hot=ps.filter(p=>p.lk>=P.base_lk*3);
  const hottest=[...ps].sort((a,b)=>b.lk-a.lk)[0];
  return{
  sum:`<div class="verd" style="--vc:var(--ind)">
   <div class="vk">Chân dung</div>
   <div class="vs">Đông nhất không phải gắn bó nhất.</div>
   <div class="vb"><p>Nhóm lớn nhất là <b>${esc(PERSVI[top.k][0])}</b> —
    ${dc(top.p,1)}% bình luận. Nhưng nhóm phản ứng mạnh nhất là
    <b>${esc(PERSVI[hottest.k][0])}</b>, like trung vị <b>${dc(hottest.lk,0)}</b>,
    gấp <b>${dc(hottest.lk/P.base_lk,0)}×</b> mặt bằng.</p>
    <p>Viết cho nhóm đông để có lượng, nhưng nhóm nhỏ mới là người
    <b>chia sẻ và quay lại</b>.</p></div></div>""",
""" f(){const ps=[...P.pers].sort((a,b)=>b.n-a.n), top=ps[0];
  const SV={}; P.sig.forEach(s=>SV[s.s]=s.v);
  /* Câu chốt phải dựa trên nhóm ĐÃ QUA KIỂM ĐỊNH. Nhóm like cao nhất là
     p_music nhưng chỉ n=4 và bị chấm YẾU — một bình luận may mắn là trung vị
     nhảy vọt. Lấy nhóm có like cao nhất TRONG SỐ được XÁC NHẬN. */
  const ok=ps.filter(p=>SV[p.k]==='XÁC NHẬN').sort((a,b)=>b.lk-a.lk);
  const solid=ok[0]||ps[0];
  const hottest=[...ps].sort((a,b)=>b.lk-a.lk)[0];
  const shaky=hottest.k!==solid.k?hottest:null;
  const cov=P.x2.cover.pers;
  return{
  sum:`<div class="verd" style="--vc:var(--ind)">
   <div class="vk">Chân dung</div>
   <div class="vs">Đông nhất không phải gắn bó nhất.</div>
   <div class="vb"><p>Nhóm lớn nhất là <b>${esc(PERSVI[top.k][0])}</b> —
    ${dc(top.p,1)}% bình luận, nhưng like trung vị chỉ <b>${dc(top.lk,0)}</b>,
    đúng bằng mặt bằng.</p>
   <p>Nhóm phản ứng mạnh nhất <b>mà đủ mẫu để tin</b> là
    <b>${esc(PERSVI[solid.k][0])}</b> — ${vn(solid.n)} người, like trung vị
    <b>${dc(solid.lk,0)}</b>, gấp <b>${dc(solid.lk/P.base_lk,0)}×</b> mặt bằng.
    Đây là nhóm duy nhất được kiểm định <b>XÁC NHẬN</b>.</p>
    <p>Viết cho nhóm đông để có lượng, nhưng nhóm nhỏ mới là người
    <b>chia sẻ và quay lại</b>.</p></div></div>
   ${shaky?`<div class="caution"><div class="ct">Một con số dễ đọc nhầm</div>
    <div class="cd">Nhóm <b>${esc(PERSVI[shaky.k][0])}</b> có like trung vị
     <b>${dc(shaky.lk,0)}</b> — cao nhất bảng, gấp ${dc(shaky.lk/P.base_lk,0)}×
     mặt bằng. Nhưng nhóm đó chỉ có <b>${shaky.n} người</b>
     (${dc(shaky.p,2)}% bình luận) và bị kiểm định chấm
     <b>${esc(SV[shaky.k]||'—')}</b>. Với cỡ mẫu ấy, một bình luận được nhiều
     like là đủ kéo trung vị lên — <b>đừng dùng làm căn cứ</b>.</div></div>`:''}""")

# ── 2 · TRANG 04: nhãn phán quyết trên từng thẻ + độ phủ ────────────────────
patch("04 · nhãn phán quyết + độ phủ",
"""   <div class="cards">${ps.map(p=>{const v=PERSVI[p.k];const h=p.lk>=P.base_lk*3;
    return `<div class="cd2${h?' hot':''}"><div class="c1">${esc(v[0])}</div>
     <div class="c2">${esc(v[1])}</div>
     <div class="c3"><span>${vn(p.n)} người · ${dc(p.p,2)}%</span>
      <span class="num">${dc(p.lk,0)} like</span></div>
     ${h?`<div class="c4">gấp ${dc(p.lk/P.base_lk,1)}× mặt bằng</div>`:''}</div>`}).join('')}</div>
   ${act(`<b>Mô tả video nêu thẳng bối cảnh khó khăn và sự an ủi</b>,
    đừng chỉ mô tả thể loại nhạc.`,'tỉ lệ bình luận có «finally» hoặc «never heard»')}`,""",
"""   <div class="cards">${ps.map(p=>{const v=PERSVI[p.k];
    const vd=SV[p.k]||''; const h=vd==='XÁC NHẬN';
    return `<div class="cd2${h?' hot':''}"><div class="c1">${esc(v[0])}
      <span class="tag ${h?'pos':vd==='YẾU'?'warn2':'neg'}">${esc(vd||'chưa kiểm')}</span></div>
     <div class="c2">${esc(v[1])}</div>
     <div class="c3"><span>${vn(p.n)} người · ${dc(p.p,2)}%</span>
      <span class="num">${dc(p.lk,0)} like</span></div>
     <div class="c4">${p.lk>=P.base_lk*3?`gấp ${dc(p.lk/P.base_lk,1)}× mặt bằng`
       :'ngang mặt bằng'}${p.n<20?` · chỉ ${p.n} người, chưa đủ tin`:''}</div>
     </div>`}).join('')}</div>
   <div class="scale"><b>Bốn nhóm này chỉ phủ ${dc(cov,1)}% bình luận.</b>
    Phần còn lại (${dc(100-cov,1)}%) không rơi vào nhóm nào — người viết không
    để lộ đủ manh mối. Đây là <b>bốn nhóm nhận ra được</b>, không phải bản đồ
    đầy đủ của khán giả.</div>
   ${act(`<b>Mô tả video nêu thẳng bối cảnh khó khăn và sự an ủi</b>,
    đừng chỉ mô tả thể loại nhạc.`,'tỉ lệ bình luận có «finally» hoặc «never heard»')}`,""")

# ── 3 · TRANG 05: mẫu số của con số bối cảnh ────────────────────────────────
patch("05 · mẫu số bối cảnh",
"""   ${fig('Hình 6 · Nghe trong bối cảnh nào',
    chBars(ctx.map(c=>({k:CTXVI[c.k]||c.k,v:c.n,lb:dc(c.p,1)+'%',hi:c===top})),470),
    `Đếm trên ${vn(AG.sample)} bình luận. Cầu nguyện bỏ xa các bối cảnh còn lại —
     và đó là bối cảnh <b>chưa kênh nào định vị riêng</b>.`)}
   ${srcs(['<b>Nguồn</b> 05_audience/_metrics_raw.json → age · context'])}`}""",
"""   ${fig('Hình 6 · Nghe trong bối cảnh nào',
    chBars(ctx.map(c=>({k:CTXVI[c.k]||c.k,v:c.n,lb:dc(c.p,1)+'%',hi:c===top})),470),
    `Đếm trên ${vn(AG.sample)} bình luận. Cầu nguyện bỏ xa các bối cảnh còn lại —
     và đó là bối cảnh <b>chưa kênh nào định vị riêng</b>.`)}
   <div class="scale"><b>Phần trăm trên hình có mẫu số là TOÀN BỘ bình luận.</b>
    Nhưng chỉ <b>${dc(P.x2.cover.ctx,1)}%</b> bình luận có nêu bối cảnh nghe —
    phần lớn người ta chỉ khen nhạc, không kể đang làm gì. Nên đọc đúng là:
    <i>${dc(top.p,1)}% tổng bình luận nhắc tới cầu nguyện</i>, chứ không phải
    ${dc(top.p,1)}% khán giả nghe lúc cầu nguyện.</div>
   <p><b>Tính lại trên đúng mẫu số</b> — trong ${vn(P.x2.cover.ctx_n)} bình luận
    <b>có nêu</b> bối cảnh, cầu nguyện chiếm
    <b>${dc(P.x2.cover.top_share,1)}%</b> (${vn(P.x2.cover.top_n)} lượt), bỏ xa
    bối cảnh thứ nhì. Con số này <b>mạnh hơn</b> ${dc(top.p,1)}% rất nhiều, và
    là con số đúng để nói «bối cảnh nghe chính của ngách».</p>
   <div class="caution"><div class="ct">Nhưng vẫn còn một thiên lệch</div>
    <div class="cd">Người nghe lúc cầu nguyện có lẽ <b>hay kể ra hơn</b> người
     nghe lúc lái xe hay làm việc nhà — vì nó gắn với cảm xúc mạnh. Nên
     ${dc(P.x2.cover.top_share,1)}% là mức <b>trần</b>, không phải con số chính
     xác. Kết luận an toàn: cầu nguyện là bối cảnh <b>được nhắc nhiều nhất</b>,
     không phải bối cảnh <b>phổ biến nhất</b>.</div></div>
   ${srcs(['<b>Nguồn</b> 05_audience/_metrics_raw.json → age · context',
     '<b>Độ phủ</b> '+vn(P.x2.cover.ctx_n)+' / '+vn(AG.sample)
      +' bình luận có nêu bối cảnh'])}`}""")

# ── 4+5 · TRANG 06: bỏ khuyến nghị sai, thay bằng từ đã kiểm định ───────────
patch("06 · thay việc cần làm",
"""   ${act(`<b>Đưa "${esc(top.w[0].toUpperCase()+top.w.slice(1))}" và "${esc(v[1].w)}"
    vào tiêu đề 3 video tới.</b>`,
    'view/ngày sau 14 ngày, so với 3 video trước · tăng ≥20% thì áp cho toàn kênh')}`,""",
"""   <div class="caution"><div class="ct">Đừng dùng bảng này để chọn từ đặt tiêu đề</div>
    <div class="cd">Bảy từ ở trên có khoảng cách lớn <b>vì chúng là từ đệm</b>,
     không phải vì chúng mạnh. Kiểm bằng lượt thích thì cả bảy đều
     <b>≤ ${dc(Math.max(...P.x2.words.map(w=>w.lift)),2)}×</b> mặt bằng — xem
     mặt «Giải thích».</div></div>
   ${act(`<b>Dùng «${esc(P.x2.sigw[0].w)}» và «${esc(P.x2.sigw[1].w)}» làm
    cảm xúc trung tâm của tiêu đề</b> — không phải chép nguyên từ, mà viết câu
    gợi đúng cảm giác đó: <i>thứ tìm lâu rồi giờ mới thấy</i>.`,
    'view/ngày sau 14 ngày, so với 3 video trước · tăng ≥20% thì áp cho toàn kênh')}`,""")

patch("06 · kiểm chứng 7 từ",
"""   <h2>Từ họ dùng nhiều nhất</h2>
   ${fig('Hình 8 · Mười từ phổ biến trong bình luận',
    chBars(P.vocab.slice(0,10).map(x=>({k:x.w,v:x.n,lb:vn(x.n)+' lần',
     hi:P.voice.some(y=>y.w===x.w&&y.r>50)})),470),
    `Từ tô đậm là từ khán giả dùng nhiều mà tiêu đề gần như không dùng.`)}
   ${srcs(['<b>Nguồn</b> 06_keyword/03_voice_gap.csv · _metrics_raw.json → vocab_top'])}`}""",
"""   <h2>Kiểm lại: khoảng cách lớn có nghĩa là từ mạnh không?</h2>
   <p><b>Không.</b> Chỉ số khoảng cách đo <i>khán giả viết bao nhiêu lần chia cho
    tiêu đề dùng bao nhiêu lần</i>. Từ nào phổ biến trong bình luận thì tỉ lệ tự
    động cao — kể cả từ đệm không mang sức mạnh nào.</p>
   <p>Nên phải kiểm thêm một bước: <b>bình luận chứa từ đó có được nhiều lượt
    thích hơn không?</b> Tần suất đo «có người nói»; lượt thích đo «người khác
    đọc và gật đầu».</p>
   <table class="tb"><thead><tr><th>Từ</th><th class="num">Khoảng cách</th>
    <th class="num">Lượt thích</th><th class="num">So mặt bằng</th>
    <th>Kết luận</th></tr></thead><tbody>
   ${P.x2.words.map(w=>`<tr><td><b>${esc(w.w)}</b></td>
    <td class="num">${vn(w.r)}×</td><td class="num">${dc(w.like,1)}</td>
    <td class="num"><b style="color:var(${w.lift>1.5?'--pos':'--neg'})">${
      dc(w.lift,2)}×</b></td>
    <td><span class="tag ${w.lift>1.5?'pos':'neg'}">${
      w.lift>1.5?'DÙNG ĐƯỢC':'KHÔNG'}</span></td></tr>`).join('')}
   </tbody></table>
   <p class="pull">Cả bảy từ đều bằng hoặc thấp hơn mặt bằng. Khoảng cách
    ${vn(P.x2.words[0].r)}× của «${esc(P.x2.words[0].w)}» không phải cơ hội —
    nó chỉ nói rằng đó là từ ai cũng viết.</p>

   <h2>Vậy từ nào thật sự mạnh</h2>
   <p>Đây là các cụm <b>đã qua kiểm định</b> ở trang «Họ là ai» — cùng phép đo,
    cùng mặt bằng ${dc(P.x2.base_like,1)} lượt thích.</p>
   <table class="tb"><thead><tr><th>Cụm</th><th class="num">Số bình luận</th>
    <th class="num">Lượt thích</th><th class="num">So mặt bằng</th></tr></thead><tbody>
   ${P.x2.sigw.map(w=>`<tr><td><b>${esc(w.w)}</b></td>
    <td class="num">${vn(w.n)}</td><td class="num">${dc(w.like,1)}</td>
    <td class="num"><b style="color:var(--pos)">${dc(w.lift,2)}×</b></td></tr>`).join('')}
   </tbody></table>
   <div class="scale"><b>Cách dùng đúng.</b> Đừng chép nguyên chữ «finally» vào
    tiêu đề — cụm đó mạnh vì <b>cảm xúc</b> nó mang, không vì mặt chữ. Viết câu
    gợi đúng cảm giác <i>«thứ tìm lâu rồi giờ mới thấy»</i>: đó mới là thứ khán
    giả phản ứng.</div>

   <h2>Mười từ phổ biến trong bình luận</h2>
   ${fig('Hình 8 · Mười từ phổ biến trong bình luận',
    chBars(P.vocab.slice(0,10).map(x=>{
     const t=P.x2.words.find(y=>y.w===x.w);
     return {k:x.w,v:x.n,lb:vn(x.n)+' lần',hi:t&&t.lift>1.5}}),470),
    `Bảng tần suất thuần tuý — <b>không</b> phải bảng xếp hạng từ nên dùng.
     <b>Không từ nào được tô đậm</b>: trong mười từ phổ biến nhất, không từ nào
     vượt mặt bằng lượt thích. Từ hay gặp và từ có sức nặng là hai chuyện
     khác nhau.`)}
   ${srcs(['<b>Nguồn</b> 06_keyword/03_voice_gap.csv · _metrics_raw.json → vocab_top',
     '<b>Kiểm định</b> Mann-Whitney U trên '+vn(P.age.sample)
      +' bình luận đã lọc · mặt bằng '+dc(P.x2.base_like,1)+' lượt thích'])}`}""")


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
