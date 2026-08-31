#!/usr/bin/env python3
"""Chèn PHẦN V · CHỌN HƯỚNG (8 trang) vào _web/ho-so.html.

Luồng: build_positioning_cards.py (nguồn số liệu duy nhất)
         -> export_positioning_json.py  -> positioning.json
         -> file này                    -> _web/ho-so.html

Chạy lại được nhiều lần: mỗi lần chạy sẽ gỡ khối cũ rồi chèn khối mới, nên
không bao giờ nhân đôi.

Vì sao KHÔNG làm tab ngang: 7 định vị không ngang hàng (4 nên làm, 1 khó,
2 nên tránh). Tab ngang gợi ý "chọn một trong các thứ tương đương" và làm mất
phán quyết ngay ở thanh điều hướng. Ở đây dùng mục lục có chấm màu, cộng một
trang so sánh đứng trước làm cửa vào.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SRC = ROOT / "niches/christian-blues/99_report/_dinh-vi/positioning.json"
WEB = ROOT / "_web/ho-so.html"
BEGIN = "/* ══ PHẦN V · CHỌN HƯỚNG — SINH TỰ ĐỘNG, ĐỪNG SỬA TAY ══ */"
END = "/* ══ HẾT PHẦN V ══ */"


def main():
    D = json.loads(SRC.read_text(encoding="utf-8"))
    html = WEB.read_text(encoding="utf-8")

    # 1) nhúng dữ liệu vào một thẻ JSON riêng, cạnh thẻ P4 có sẵn
    blob = json.dumps(D, ensure_ascii=False).replace("</", "<\\/")
    tag = f'<script id="DV" type="application/json">{blob}</script>'
    html = re.sub(r'<script id="DV" type="application/json">.*?</script>\n?',
                  "", html, flags=re.S)
    html = html.replace('<script id="P4"', tag + '\n<script id="P4"', 1)

    # 2) chèn CSS
    css = CSS
    html = re.sub(r"/\* ══ CSS PHẦN V.*?/\* ══ HẾT CSS PHẦN V ══ \*/\n?",
                  "", html, flags=re.S)
    html = html.replace("</style>", css + "\n</style>", 1)

    # 3) chèn 8 trang vào cuối mảng PAGES
    html = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?",
                  "", html, flags=re.S)
    anchor = "\n);\n\n/* ══════"
    assert anchor in html, "không thấy chỗ kết thúc mảng PAGES"
    # Chèn SAU dấu đóng mảng: PAGES là const nên không gán lại được, nhưng
    # push() vào mảng đó thì hợp lệ.
    html = html.replace(anchor, "\n);\n" + BEGIN + PAGES_JS + END
                        + "\n\n/* ══════", 1)

    # 4) vá toc(): thêm chấm màu phán quyết cho các trang định vị
    OLD_TOC = ('h+=`<button class="pg" data-p="${i}" '
               'aria-current="${i===PG?\'true\':\'false\'}">\n'
               '    <span class="pn">${String(i+1).padStart(2,\'0\')}</span>\n'
               '    <span class="pt">${esc(p.t)}</span></button>`});')
    NEW_TOC = ('h+=`<button class="pg" data-p="${i}" '
               'aria-current="${i===PG?\'true\':\'false\'}">\n'
               '    <span class="pn">${String(i+1).padStart(2,\'0\')}</span>\n'
               '    ${p.grp?`<span class="dot g${p.grp===\'A\'?1:p.grp===\'B\'?2:3}"'
               '></span>`:\'\'}\n'
               '    <span class="pt">${esc(p.t)}</span></button>`});')
    assert OLD_TOC in html, "không thấy thân hàm toc()"
    html = html.replace(OLD_TOC, NEW_TOC, 1)

    # 5) vá render(): bấm một hàng trong bảng so sánh -> nhảy tới trang đó
    OLD_BIND = """ document.querySelectorAll('[data-go]').forEach(b=>b.onclick=()=>{
  const n=+b.dataset.go; if(n>=0&&n<PAGES.length) go(n)});"""
    NEW_BIND = """ document.querySelectorAll('[data-go]').forEach(b=>b.onclick=()=>{
  const n=+b.dataset.go; if(n>=0&&n<PAGES.length) go(n)});
 /* Bấm một hàng trong bảng so sánh -> mở trang định vị tương ứng. */
 document.querySelectorAll('[data-dv]').forEach(tr=>tr.onclick=()=>{
  const i=PAGES.findIndex(x=>x.dv===tr.dataset.dv); if(i>=0) go(i)});"""
    assert OLD_BIND in html, "không thấy chỗ nối sự kiện trong render()"
    html = html.replace(OLD_BIND, NEW_BIND, 1)

    # 6) mục lục gập/mở theo chương
    # Vì sao: 25 trang trải hết một cột thì phải cuộn mới thấy chương cuối.
    # Gập lại, chương đang đọc tự mở -> luôn thấy toàn bộ 5 chương trong một
    # màn hình. Trạng thái gập lưu ở localStorage nên giữ nguyên khi tải lại.
    OLD_FN = """function toc(){
 let h=`<div class="tochd">
  <div class="kick">Bước 4 · Hồ sơ</div>
  <div class="bt">${esc(P.niche)}</div>
  <div class="bs">${dc(P.score,2)}/${P.max} · ${esc(P.verdict)}</div></div>`;
 CHAPS.forEach(c=>{
  h+=`<div class="chap"><div class="chn">${esc(c)}</div>`;
  PAGES.forEach((p,i)=>{ if(p.ch!==c)return;
   h+=`<button class="pg" data-p="${i}" aria-current="${i===PG?'true':'false'}">
    <span class="pn">${String(i+1).padStart(2,'0')}</span>
    ${p.grp?`<span class="dot g${p.grp==='A'?1:p.grp==='B'?2:3}"></span>`:''}
    <span class="pt">${esc(p.t)}</span></button>`});
  h+=`</div>`;
 });"""

    NEW_FN = """/* Chương nào đang gập — chương chứa trang đang đọc luôn được mở.
   Mặc định gập hết: mở sách ra thấy ngay 5 chương trong một màn hình, chứ
   không phải cuộn qua 25 dòng. Người đọc tự mở chương nào muốn xem. */
let SHUT=new Set(), OPENED=new Set();
try{
 const v=localStorage.getItem('hoso.open');
 if(v!==null) OPENED=new Set(JSON.parse(v));
}catch(e){}
function saveOpen(){
 try{ localStorage.setItem('hoso.open',JSON.stringify([...OPENED])) }catch(e){} }
function toggleChap(c){
 if(c===PAGES[PG].ch) return;          // không gập chương đang đọc
 OPENED.has(c)?OPENED.delete(c):OPENED.add(c); saveOpen(); toc();
}
function toc(){
 let h=`<div class="tochd">
  <div class="kick">Bước 4 · Hồ sơ</div>
  <div class="bt">${esc(P.niche)}</div>
  <div class="bs">${dc(P.score,2)}/${P.max} · ${esc(P.verdict)}</div></div>`;
 CHAPS.forEach(c=>{
  const pages=PAGES.map((p,i)=>[p,i]).filter(([p])=>p.ch===c);
  const here=c===PAGES[PG].ch;
  const open=here||OPENED.has(c);      // chương đang đọc luôn mở
  h+=`<div class="chap${open?'':' shut'}">
   <button class="chn" data-ch="${esc(c)}" aria-expanded="${open}"
    ${here?'aria-current="true"':''}>
    <span class="cha">${open?'▾':'▸'}</span>
    <span class="chl">${esc(c)}</span>
    <span class="chc">${pages.length}</span></button>`;
  if(open) pages.forEach(([p,i])=>{
   h+=`<button class="pg" data-p="${i}" aria-current="${i===PG?'true':'false'}">
    <span class="pn">${String(i+1).padStart(2,'0')}</span>
    ${p.grp?`<span class="dot g${p.grp==='A'?1:p.grp==='B'?2:3}"></span>`:''}
    <span class="pt">${esc(p.t)}</span></button>`});
  h+=`</div>`;
 });"""
    assert OLD_FN in html, "không thấy hàm toc() gốc"
    html = html.replace(OLD_FN, NEW_FN, 1)

    OLD_BIND2 = """ document.querySelectorAll('[data-p]').forEach(b=>b.onclick=()=>{
  go(+b.dataset.p); closeToc()});"""
    NEW_BIND2 = """ document.querySelectorAll('[data-p]').forEach(b=>b.onclick=()=>{
  go(+b.dataset.p); closeToc()});
 document.querySelectorAll('[data-ch]').forEach(b=>b.onclick=()=>{
  toggleChap(b.dataset.ch)});"""
    assert OLD_BIND2 in html, "không thấy chỗ nối click trang trong toc()"
    html = html.replace(OLD_BIND2, NEW_BIND2, 1)

    WEB.write_text(html, encoding="utf-8")
    n = len(D["pos"])
    print(f"✓ chèn {n + 2} trang (1 so sánh + 1 bảng + {n} định vị) vào {WEB.name}")
    print(f"  kích thước: {WEB.stat().st_size/1024:.0f} KB")


CSS = r"""
/* ══ CSS PHẦN V · CHỌN HƯỚNG ══ */
/* Chấm màu phán quyết trong mục lục — người đọc thấy nên/khó/tránh
   trước khi bấm vào, nên không bao giờ lạc vào hướng đã bị khuyên tránh. */
.pg .dot{flex:0 0 7px;height:7px;border-radius:50%;align-self:center;
 margin-left:-4px}
.dot.g1{background:var(--pos)} .dot.g2{background:var(--warn)}
.dot.g3{background:var(--neg)}

/* Bảng so sánh 7 hướng */
.cmp{width:100%;border-collapse:collapse;margin:16px 0;font-size:13px}
.cmp th{font-family:var(--mono);font-size:9px;letter-spacing:.14em;
 text-transform:uppercase;color:var(--mut);text-align:left;font-weight:500;
 padding:0 10px 7px;border-bottom:1px solid var(--rule2)}
.cmp th.n,.cmp td.n{text-align:right;font-variant-numeric:tabular-nums}
.cmp td{padding:11px 10px;border-bottom:1px solid var(--rule);
 vertical-align:top}
.cmp tr:last-child td{border-bottom:none}
.cmp tbody tr{cursor:pointer}
.cmp tbody tr:hover{background:var(--pp3)}
.cmp .nm{font-weight:600;color:var(--ink);display:flex;align-items:center;
 gap:7px}
.cmp .nd2{color:var(--mut);font-size:12px;margin-top:3px;line-height:1.45}
.cmp .go{font-family:var(--mono);font-size:10.5px;color:var(--cop);
 white-space:nowrap;font-weight:600;opacity:.55;transition:opacity .12s}
.cmp tbody tr:hover .go{opacity:1}
.cmp tbody tr:hover .nm{color:var(--cop)}

/* Nhóm phán quyết trên trang so sánh */
.gband{margin:22px 0 8px;padding:9px 13px;border-radius:3px;
 border-left:3px solid var(--gc)}
.gband .gl{font-family:var(--mono);font-size:9.5px;letter-spacing:.16em;
 text-transform:uppercase;color:var(--gc);font-weight:600}
.gband .gd{font-size:12.5px;color:var(--ink2);margin-top:4px;line-height:1.5}

/* Thang đo — cảnh báo hai thang không so trực tiếp được */
.scale{background:var(--ind2);border-radius:3px;padding:11px 14px;
 margin:14px 0;font-size:12.5px;line-height:1.6;color:var(--ink2)}
.scale b{color:var(--ind)}

/* Thẻ mục trong trang định vị */
.sect{border:1px solid var(--rule);border-radius:4px;background:var(--pp2);
 margin:14px 0}
.stitle{font-family:var(--mono);font-size:9px;letter-spacing:.16em;
 text-transform:uppercase;font-weight:600;padding:8px 14px;
 border-bottom:1px solid var(--rule);color:var(--sc,var(--ink2));
 background:var(--pp3);border-radius:4px 4px 0 0}
.sbody{padding:12px 14px}
.sbody>p:first-child{margin-top:0} .sbody>p:last-child{margin-bottom:0}
.sbody table{margin:0}

/* Ý tưởng — đoạn mở đầu mỗi định vị */
.idea{font-size:14px;line-height:1.72;color:var(--ink2)}
.idea b{color:var(--ink)}

/* Bảng hai cột nhãn–giá trị */
.kv{width:100%;border-collapse:collapse;font-size:13px}
.kv td{padding:7px 0;border-bottom:1px solid var(--rule);vertical-align:top;
 line-height:1.6}
.kv tr:last-child td{border-bottom:none}
.kv td.k{width:104px;color:var(--mut);font-size:11.5px;padding-right:14px;
 font-family:var(--mono);letter-spacing:.03em}

/* Danh sách video đối chứng */
.vt{width:100%;border-collapse:collapse;font-size:12px;margin:0}
.vt th{font-family:var(--mono);font-size:8.5px;letter-spacing:.13em;
 text-transform:uppercase;color:var(--mut);text-align:left;font-weight:500;
 padding:0 8px 6px;border-bottom:1px solid var(--rule2)}
.vt th.n,.vt td.n{text-align:right;font-variant-numeric:tabular-nums}
.vt td{padding:7px 8px;border-bottom:1px solid var(--rule)}
.vt tr:last-child td{border-bottom:none}
.vt .vid{font-family:var(--mono);font-size:11px;color:var(--ind)}
.vt .vt2{color:var(--ink2);max-width:290px}
.vt .vch{color:var(--mut);font-size:11px;white-space:nowrap}

/* Vạch ngăn phần thi công / phần chứng minh */
.divx{border-top:2px solid var(--ink);margin:26px 0 4px;padding-top:11px}
.divx .dt{font-family:var(--disp);font-size:17px;font-weight:600;
 color:var(--ink)}
.divx p{font-size:12.5px;color:var(--mut);margin:5px 0 0;line-height:1.55}

/* Ô cảnh báo tránh */
.avoidbx{background:var(--pp3);border-left:3px solid var(--neg);
 border-radius:0 3px 3px 0;padding:10px 13px;margin:12px 0 0;font-size:12.5px;
 line-height:1.6;color:var(--ink2)}
.avoidbx b{color:var(--neg)}

/* Trích dẫn khán giả */
.qz{border-left:2px solid var(--rule2);padding:2px 0 2px 13px;margin:10px 0;
 font-size:13px;line-height:1.65;color:var(--ink2)}
.qz .ql{display:block;font-family:var(--mono);font-size:10px;
 color:var(--fnt);margin-top:5px}

/* Thanh biên độ giỏi–dở */
.sprd{display:flex;align-items:flex-end;gap:3px;height:44px;margin:4px 0 8px}
.sprd i{flex:1;background:var(--rule2);border-radius:1px 1px 0 0;
 min-height:2px;display:block}
.sprd i.hi{background:var(--cop)}
.sprdl{display:flex;justify-content:space-between;font-family:var(--mono);
 font-size:9.5px;color:var(--fnt)}
/* Mục lục gập/mở — 25 trang không trải hết một cột */
.chn{display:flex;align-items:center;gap:9px;width:100%;background:none;
 border:0;cursor:pointer;padding:13px 22px 9px;text-align:left;
 font-family:var(--mono);font-size:11.5px;letter-spacing:.13em;
 text-transform:uppercase;color:var(--mut);font-weight:600;
 transition:color .12s}
.chn:hover{color:var(--ink)}
.chn[aria-current="true"]{color:var(--cop)}
.chn .cha{flex:0 0 10px;font-size:11px;line-height:1;color:var(--rule2)}
.chn:hover .cha{color:var(--mut)}
.chn[aria-current="true"] .cha{color:var(--cop)}
.chn .chl{flex:1}
.chn .chc{font-size:10px;color:var(--rule2);letter-spacing:0;font-weight:400}
/* Vạch ngăn giữa các chương — mắt tách được nhóm khi đã gập lại */
.chap+.chap{border-top:1px solid var(--rule)}
.chap.shut{padding-bottom:0}
.chap.shut .chn{opacity:.72}
/* Bảng tổng quan — ảnh, link, view */
.shg{margin:18px 0 26px}
.shh{display:flex;align-items:baseline;gap:9px;flex-wrap:wrap;
 padding:0 0 9px;border-bottom:1px solid var(--rule2);margin-bottom:2px}
.shh .shn{font-family:var(--disp);font-size:16px;font-weight:600;color:var(--ink)}
.shh .shq{font-size:12.5px;color:var(--mut);flex:1;min-width:180px}
.shh .shx{font-family:var(--mono);font-size:11px;color:var(--mut);
 white-space:nowrap}
.shh .shx b{color:var(--ink)}
.sht{width:100%;border-collapse:collapse;font-size:12.5px}
.sht th{font-family:var(--mono);font-size:8.5px;letter-spacing:.13em;
 text-transform:uppercase;color:var(--fnt);text-align:left;font-weight:500;
 padding:7px 8px 6px;border-bottom:1px solid var(--rule)}
.sht th.n,.sht td.n{text-align:right;font-variant-numeric:tabular-nums}
.sht th.thc{width:104px}
.sht td{padding:8px;border-bottom:1px solid var(--rule);vertical-align:top}
.sht tr:last-child td{border-bottom:none}
.sht tbody tr:hover{background:var(--pp3)}
.sht td.thc{width:104px}
.thi{width:96px;height:54px;object-fit:cover;border-radius:3px;display:block;
 background:var(--pp3);border:1px solid var(--rule)}
a.shl{color:var(--ink);text-decoration:none;line-height:1.45;display:block}
a.shl:hover{color:var(--ind);text-decoration:underline}
a.shc{color:var(--ind);text-decoration:none;white-space:nowrap;font-size:12px}
a.shc:hover{text-decoration:underline}
.shi{font-family:var(--mono);font-size:10px;color:var(--fnt);margin-top:3px}
@media(max-width:760px){
 .sht th.thc,.sht td.thc{width:64px} .thi{width:60px;height:34px}
 .sht{font-size:11.5px}
}
.mtag{display:inline-block;font-family:var(--mono);font-size:8.5px;
 letter-spacing:.06em;background:var(--ind2);color:var(--ind);padding:1px 5px;
 border-radius:2px;vertical-align:1px}
/* ══ HẾT CSS PHẦN V ══ */"""


PAGES_JS = r"""
/* Dữ liệu 7 định vị — sinh từ pipeline/report/export_positioning_json.py.
   Cùng nguồn với 7 file PDF nên số trên web và số trong PDF luôn khớp. */
(function(){
 const DV=JSON.parse(document.getElementById('DV').textContent);
 const GC={A:'--pos',B:'--warn',C:'--neg'};
 const GN={A:'g1',B:'g2',C:'g3'};
 const CH='V · Chọn hướng';

 /* Hai thang đo khác nhau — nói rõ để không ai so 6,25x với 1,63x. */
 const unit=p=>p.kind==='title'
  ?'view/ngày của video, so với mặt bằng ngách'
  :'lượt thích của bình luận, so với nền ngách';
 const unitShort=p=>p.kind==='title'?'view/ngày':'lượt thích';

 const kvt=rows=>`<table class="kv"><tbody>${rows.map(r=>
  `<tr><td class="k">${esc(r[0])}</td><td>${r[1]}</td></tr>`).join('')}</tbody></table>`;

 const sect=(t,inner,c)=>`<div class="sect"><div class="stitle"${
  c?` style="--sc:var(${c})"`:''}>${esc(t)}</div>
  <div class="sbody">${inner}</div></div>`;

 const vtab=(rows,sig)=>`<table class="vt"><thead><tr>
   <th>video_id</th><th>Tiêu đề</th>${sig?'<th class="n">Tín hiệu</th>':''}
   <th class="n">View</th><th class="n">View/ngày</th><th>Kênh</th>
  </tr></thead><tbody>${rows.map(v=>`<tr>
   <td class="vid">${esc(v.id)}</td>
   <td class="vt2">${esc(v.t)}</td>
   ${sig?`<td class="n">${v.sig}</td>`:''}
   <td class="n">${vn(v.view)}</td><td class="n">${dc(v.vpd,1)}</td>
   <td class="vch">@${esc(v.ch)}</td></tr>`).join('')}</tbody></table>`;

 /* ── TRANG 18 · BẢNG SO SÁNH ─────────────────────────────────────── */
 PAGES.push({ch:CH,t:'Bảy hướng kênh — chọn hướng nào?',
  dek:'Hồ sơ trả lời có nên làm ngách này. Phần này trả lời nếu làm thì làm hướng nào.',
  f(){
   const g=k=>DV.pos.filter(p=>p.grp===k);
   const band=(k,items)=>{
    if(!items.length)return'';
    const m=items[0];
    return `<div class="gband" style="--gc:var(${GC[k]});background:${
      k==='A'?'rgba(46,125,91,.06)':k==='B'?'rgba(176,125,63,.07)':'rgba(176,58,56,.06)'}">
     <div class="gl">${esc(m.label)}</div>
     <div class="gd">${esc(m.grp_desc)}</div></div>
    <table class="cmp">${k==='A'?`<thead><tr>
     <th>Hướng kênh · cho ai</th><th class="n">Cỡ mẫu</th>
     <th class="n">Chênh lệch</th><th>Đo bằng</th><th></th>
    </tr></thead>`:''}<tbody>${items.map(p=>`<tr data-dv="${p.id}">
     <td><div class="nm"><span class="dot ${GN[p.grp]}"></span>${esc(p.name)}</div>
      <div class="nd2">${esc(p.need)}</div></td>
     <td class="n"><span style="white-space:nowrap">${vn(p.n)}</span><br>
      <span style="color:var(--fnt);font-size:11px;white-space:nowrap">${
       p.kind==='title'?'video':'bình luận'}</span></td>
     <td class="n"><b style="color:var(${p.lift>=1.3?'--pos':p.lift>=1?'--warn':'--neg'})">${
       dc(p.lift,2)}×</b></td>
     <td style="font-size:11.5px;color:var(--mut)">${unitShort(p)}</td>
     <td class="go">Mở →</td></tr>`).join('')}</tbody></table>`};

   return{
   sum:`<div class="verd" style="--vc:var(--cop)">
    <div class="vk">Từ tổng quát → chi tiết</div>
    <div class="vs">Bốn hướng nên làm, một hướng khó, hai hướng nên tránh.</div>
    <div class="vb"><p>Mười bảy trang trước trả lời <b>«có nên làm ngách này»</b>.
     Bảy trang sau trả lời <b>«nếu làm thì làm hướng nào»</b> — mỗi hướng là một
     bản thi công riêng: khách hàng, thumbnail, nhạc, cấu trúc bài, công thức
     tiêu đề, lịch đăng, và điều kiện dừng.</p>
    <p>Hai hướng cuối được giữ lại <b>đúng vì chúng kém</b>. Biết chỗ không nên
     đi cũng đáng giá ngang biết chỗ nên đi — nhất là khi chúng là hai hướng
     đông người làm nhất ngách.</p></div>
    ${figs([{v:DV.pos.filter(p=>p.grp==='A').length,l:'hướng nên làm',c:'--pos'},
      {v:DV.pos.filter(p=>p.grp==='B').length,l:'hướng khó',c:'--warn'},
      {v:DV.pos.filter(p=>p.grp==='C').length,l:'hướng nên tránh',c:'--neg'}])}</div>

    <div class="scale"><b>Đọc bảng dưới thế nào.</b> Cột «chênh lệch» có
     <b>hai thang khác nhau</b>, không so chéo được. Bốn hướng đo bằng
     <b>view/ngày của video</b> (so với mặt bằng ${dc(DV.base_vpd,2)}); ba hướng
     đo bằng <b>lượt thích của bình luận</b> (so với nền ${dc(DV.base_like,1)}).
     Vậy nên 6,25× ở thang bình luận <b>không</b> có nghĩa là mạnh gấp bốn 1,63×
     ở thang video. So trong cùng một thang thì được.</div>

    ${band('A',g('A'))}${band('B',g('B'))}${band('C',g('C'))}

    ${act(`<b>Chọn một hướng trong nhóm «nên làm» và đọc trang riêng của nó.</b>
     Mỗi trang có đủ thứ để mở kênh: khách hàng là ai, thumbnail vẽ gì, nhạc
     dựng thế nào, tiêu đề đặt ra sao, đăng bao lâu một lần — và mốc nào thì
     dừng lại.`,'view/ngày sau 10 video đầu, so với mặt bằng '+dc(DV.base_vpd,2))}`,

   exp:`<p class="lead2">Bảy hướng này không phải bảy ý tưởng nghĩ ra rồi đi tìm
     số liệu chống lưng. Chúng là bảy nhóm <b>đã có sẵn trong dữ liệu</b> —
     nhóm theo hai chiều: nội dung nhạc, và nhu cầu người nghe.</p>

    <h2>Vì sao có hai thang đo</h2>
    <p>Câu hỏi «hướng này có ăn không» đo được bằng hai cách, tuỳ chỗ định vị
     để lại dấu vết:</p>
    <table class="tb"><thead><tr><th>Thang</th><th>Dùng khi</th>
     <th>So với nền</th></tr></thead><tbody>
    <tr><td><b>View/ngày của video</b></td>
     <td>Định vị lộ ra ngay ở <b>tiêu đề</b> — đếm được bằng từ khoá.</td>
     <td class="num">${dc(DV.base_vpd,2)}</td></tr>
    <tr><td><b>Lượt thích của bình luận</b></td>
     <td>Định vị <b>không lộ ở tiêu đề</b>, chỉ hiện ra khi khán giả tự nói.
      Không đếm được bằng từ khoá tiêu đề.</td>
     <td class="num">${dc(DV.base_like,1)}</td></tr>
    </tbody></table>

    <h2>Vì sao không quy hết về view/ngày cho dễ so</h2>
    <p>Đã thử, và <b>không dùng được</b>. Video được lấy bình luận trong mẫu có
     view/ngày trung vị <b>${dc(DV.cmt_bias.vpd_with,1)}</b>, còn video không
     được lấy chỉ <b>${dc(DV.cmt_bias.vpd_without,1)}</b> —
     chênh <b>${dc(DV.cmt_bias.ratio,1)}×</b> trước khi xét đến định vị nào.
     Video nhiều view thì nhiều bình luận, nên bất kỳ cụm từ nào cũng «thắng».</p>
    <p>Ghép cặp theo số bình luận để triệt tiêu thiên lệch đó thì hướng 04 còn
     3,5× — <b>không phân biệt được</b> với cụm vô nghĩa «amen» (4,3×). Nên
     view/ngày bị loại khỏi việc xếp hạng ba hướng đo bằng bình luận.</p>

    <h2>Kiểm chứng nền giả — thang lượt thích có đáng tin không</h2>
    <p>Trước khi tin con số 4–6×, phải hỏi ngược: <b>một cụm từ vô nghĩa thì
     bao nhiêu?</b> Nếu cụm vô nghĩa cũng cho 5× thì con số của hướng thật
     chẳng chứng minh gì.</p>
    <table class="tb"><thead><tr><th>Cụm từ</th><th class="num">Số bình luận</th>
     <th class="num">Lượt thích</th><th class="num">Chênh lệch</th></tr></thead><tbody>
    ${DV.placebo.items.map(x=>`<tr><td><span class="tag">${esc(x.nm)}</span>
      <span style="color:var(--mut);font-size:12px"> — cụm trung tính</span></td>
      <td class="num">${vn(x.n)}</td><td class="num">${dc(x.like,1)}</td>
      <td class="num">${dc(x.lift,2)}×</td></tr>`).join('')}
    ${DV.pos.filter(p=>p.kind==='signal').map(p=>`<tr>
      <td><b>${esc(p.name)}</b>
       <span style="color:var(--mut);font-size:12px"> — hướng thật</span></td>
      <td class="num">${vn(p.n)}</td><td class="num">${dc(p.like,1)}</td>
      <td class="num"><b style="color:var(--pos)">${dc(p.lift,2)}×</b></td></tr>`).join('')}
    </tbody></table>
    <p>Năm cụm trung tính nằm gọn trong <b>${dc(DV.placebo.lo,2)}–${
      dc(DV.placebo.hi,2)}×</b>. Ba hướng thật nằm ở <b>4,00–6,25×</b>.
     Hai dải <b>không chồng lấn</b> — nên chênh lệch của ba hướng đó không phải
     do may mắn của phép đo.</p>

    <h2>Vì sao vẫn giữ hai hướng «nên tránh»</h2>
    <p>Hai hướng đó là hai hướng <b>đông người làm nhất ngách</b> —
     ${vn(DV.pos.find(p=>p.id==='06').n)} và
     ${vn(DV.pos.find(p=>p.id==='07').n)} video. Người mới rất dễ chọn đúng
     chúng, vì nhìn quanh thấy ai cũng làm. Ghi rõ ra để biết mà tránh, chứ
     không phải xoá đi.</p>

    ${srcs(['<b>Nguồn</b> 99_report/_dinh-vi/positioning.json — sinh từ '
      +'pipeline/report/export_positioning_json.py',
      '<b>Cùng nguồn với</b> 7 file PDF trong 99_report/_dinh-vi/',
      '<b>Mẫu</b> '+vn(DV.n_matured)+' video đã đủ 60 ngày · '
      +vn(DV.n_comments)+' bình luận đã lọc · đo ngày '+DV.crawl,
      '<b>Không đưa lên</b> comment_id và tên tài khoản người bình luận'])}`}
  }});


 /* ── TRANG 19 · BẢNG TỔNG QUAN ───────────────────────────────────── */
 /* Một màn hình nhìn hết 7 hướng: ảnh thật, link bấm được, view.
    Trang 18 so bằng SỐ; trang này so bằng MẮT. */
 PAGES.push({ch:CH,t:'Bảng tổng quan — ảnh, kênh, view',
  dek:'Bảy hướng kênh với ảnh thật và link tra tận nơi. Bấm bất kỳ dòng nào để mở YouTube.',
  f(){
   const grp=k=>DV.pos.filter(p=>p.grp===k);
   const allv0=DV.pos.flatMap(p=>p.sheet);
   const seen={}; allv0.forEach(v=>seen[v.vid]=(seen[v.vid]||0)+1);
   const blk=k=>{
    const items=grp(k); if(!items.length)return'';
    const m=items[0];
    return `<div class="gband" style="--gc:var(${GC[k]});background:${
      k==='A'?'rgba(46,125,91,.06)':k==='B'?'rgba(176,125,63,.07)':'rgba(176,58,56,.06)'}">
     <div class="gl">${esc(m.label)}</div></div>`
    +items.map(p=>`
     <div class="shg">
      <div class="shh">
       <span class="dot g${p.grp==='A'?1:p.grp==='B'?2:3}"></span>
       <span class="shn">${esc(p.name)}</span>
       <span class="shq">${esc(p.need)}</span>
       <span class="shx"><b>${dc(p.lift,2)}×</b> ${unitShort(p)}</span>
      </div>
      <table class="sht"><thead><tr>
       <th class="thc">Ảnh</th><th>Video</th><th>Kênh</th>
       <th class="n">View</th><th class="n">View/ngày</th><th class="n">Vượt kênh</th>
      </tr></thead><tbody>
      ${p.sheet.map(v=>`<tr>
       <td class="thc"><a href="https://youtube.com/watch?v=${v.vid}"
        target="_blank" rel="noopener"><img class="thi" loading="lazy"
        src="${v.th}" alt=""
        onerror="this.src='https://i.ytimg.com/vi/${v.vid}/mqdefault.jpg'"></a></td>
       <td><a class="shl" href="https://youtube.com/watch?v=${v.vid}"
        target="_blank" rel="noopener">${esc(v.t)}</a>
        <div class="shi">${esc(v.vid)}${seen[v.vid]>1
         ?` <span class="mtag">nhiều hướng</span>`:''}</div></td>
       <td><a class="shc" href="https://youtube.com/channel/${v.cid}"
        target="_blank" rel="noopener">@${esc(v.ch)}</a>
        <div class="shi">${kk(v.subs)} người đăng ký</div></td>
       <td class="n"><b>${vn(v.view)}</b></td>
       <td class="n">${vn(Math.round(v.vpd))}</td>
       <td class="n">${dc(v.out,1)}×</td></tr>`).join('')}
      </tbody></table></div>`).join('')};

   const allv=DV.pos.flatMap(p=>p.sheet);
   /* Một video có thể phục vụ nhiều nhu cầu cùng lúc -> nằm ở nhiều hướng.
      Đếm số lần xuất hiện để đánh dấu, và để không nói nhầm "42 video khác
      nhau" khi thực ra chỉ có 34. */
   const uniq=Object.keys(seen).length;
   const multi=Object.entries(seen).filter(([,n])=>n>1);
   return{
   sum:`<div class="verd" style="--vc:var(--cop)">
    <div class="vk">Nhìn một lượt</div>
    <div class="vs">Bảy hướng, ${uniq} video tiêu biểu, ảnh và link thật.</div>
    <div class="vb"><p>Trang trước so bảy hướng bằng <b>số</b>. Trang này so bằng
     <b>mắt</b> — mỗi hướng lấy ${DV.pos[0].sheet.length} video mạnh nhất, kèm
     ảnh thumbnail thật và link bấm được sang YouTube.</p>
    <p>Cột <b>vượt kênh</b> là view của video đó so với video trung vị của
     chính kênh ấy. Trên 1× nghĩa là video này ăn hơn mức thường của kênh —
     dấu hiệu định vị chạm đúng, chứ không phải kênh vốn đã mạnh.</p>
    ${multi.length?`<p><b>${multi.length} video xuất hiện ở nhiều hướng cùng lúc</b>
     (đánh dấu <span class="mtag">nhiều hướng</span>). Một bài hát có thể vừa là
     lời tạ ơn, vừa là Blues thật, vừa nói với người lớn tuổi — các hướng
     <b>không loại trừ nhau</b>. Chỗ chồng lấn thường là chỗ mạnh nhất.</p>`:''}</div>
    ${figs([{v:vn([...new Set(allv.map(v=>v.vid))].reduce((a,id)=>
        a+allv.find(v=>v.vid===id).view,0)),l:'tổng view của '+uniq+' video',c:'--cop'},
      {v:vn(new Set(allv.map(v=>v.ch)).size),l:'kênh khác nhau',c:'--ink'},
      {v:dc(Math.max(...allv.map(v=>v.out)),1)+'×',l:'video vượt kênh nhiều nhất',c:'--pos'}])}</div>
   ${blk('A')}${blk('B')}${blk('C')}
   ${srcs(['<b>Ảnh</b> thumbnail công khai từ i.ytimg.com — tải trực tiếp từ YouTube',
     '<b>View</b> chốt ngày '+DV.crawl+', không cập nhật theo thời gian thực',
     '<b>Chọn video</b> '+DV.pos[0].sheet.length+' video có view/ngày cao nhất mỗi hướng'])}`,

   exp:`<p class="lead2">Bảng này để <b>tra tận nơi</b>. Mọi con số ở các trang
     khác đều quy về được những video cụ thể này — bấm vào là xem được ngay
     video thật trên YouTube.</p>

    <h2>Đọc cột «vượt kênh» thế nào</h2>
    <p>Đây là cột quan trọng nhất của bảng, và cũng dễ đọc nhầm nhất.</p>
    <table class="tb"><thead><tr><th>Giá trị</th><th>Nghĩa là</th></tr></thead><tbody>
    <tr><td class="num"><b>1,0×</b></td><td>Video này ăn <b>đúng bằng</b> mức
     thường của kênh đó. Định vị không thêm gì.</td></tr>
    <tr><td class="num"><b>5,0×</b></td><td>Ăn gấp 5 lần video trung vị của chính
     kênh đó. Cùng kênh, cùng người làm, cùng lượng người đăng ký — khác biệt
     đến từ <b>chính video này</b>.</td></tr>
    <tr><td class="num"><b>0,5×</b></td><td>Ăn kém hơn mức thường của kênh —
     dù view tuyệt đối có thể vẫn to nếu kênh vốn lớn.</td></tr>
    </tbody></table>
    <p>Vì sao không xếp hạng bằng view tuyệt đối: một kênh 2 triệu người đăng ký
     đăng video dở vẫn nhiều view hơn kênh 5 nghìn đăng video hay. So với
     <b>chính kênh đó</b> mới loại được lợi thế quy mô ra khỏi phép đo.</p>

    <h2>Vì sao chỉ lấy ${DV.pos[0].sheet.length} video mỗi hướng</h2>
    <p>Đây là bảng để <b>nhìn lướt</b>, không phải bộ dữ liệu đầy đủ. Danh sách
     dài hơn — kèm cả nhóm làm cùng hướng nhưng thất bại — nằm ở mục 9 trong
     từng trang định vị.</p>

    <div class="scale"><b>Ảnh có thể không hiện.</b> Thumbnail tải thẳng từ máy
     chủ YouTube. Nếu video bị xoá hoặc chuyển riêng tư sau ngày ${DV.crawl}
     thì ô ảnh sẽ trống — bản thân điều đó cũng là thông tin: kênh trong ngách
     này có xoá video.</div>

    ${srcs(['<b>Nguồn</b> 99_report/_dinh-vi/positioning.json → sheet',
      '<b>Số liệu</b> chốt ngày '+DV.crawl+' · '+vn(DV.n_matured)+' video đã đủ 60 ngày'])}`}
  }});

 /* ── 7 TRANG ĐỊNH VỊ ─────────────────────────────────────────────── */
 DV.pos.forEach(p=>{
  PAGES.push({ch:CH,t:p.name,dek:p.need.charAt(0).toUpperCase()+p.need.slice(1)+'.',
   dv:p.id,grp:p.grp,
   f(){
    const b=p.build, gc=GC[p.grp];
    const sp=p.spec;
    /* Tính trước: template literal KHÔNG lồng được trong ${} của cái khác. */
    const specNote='<p class="small" style="margin-top:10px;color:var(--mut);'
     +'font-size:12px"><b>Đo riêng cho hướng này:</b> thời lượng video trung vị '
     +'<b>'+dc(sp.dur,1)+' phút</b> (khoảng '+dc(sp.d25,0)+'–'+dc(sp.d75,0)+'), '
     +'tiêu đề '+dc(sp.tlen,0)+' ký tự, '+dc(sp.pct_num,0)+'% có chứa số, '
     +dc(sp.pct_emoji,0)+'% có emoji, '+dc(sp.pct_pipe,0)+'% dùng dấu |.</p>';

    /* ── MẶT «KẾT LUẬN» = BẢN THI CÔNG ── */
    const sum=`<div class="verd" style="--vc:var(${gc})">
     <div class="vk">${esc(p.label)} · ${esc(p.verdict)}</div>
     <div class="vs">${esc(p.name)}</div>
     <div class="vb"><div class="idea">${b.idea}</div></div>
     ${figs([{v:dc(p.lift,2)+'×',l:unit(p),c:gc},
       {v:vn(p.n),l:p.kind==='title'?'video mang định vị':'bình luận mang tín hiệu',
        c:'--ink'},
       {v:vn(p.kind==='title'?p.n_channels:p.n_videos),
        l:p.kind==='title'?'kênh đang làm':'video dính tín hiệu',c:'--ink'}])}</div>

    ${sect('1 · Khách hàng — ai là người nghe',kvt([
      ['Khách hàng',b.customer],['Chân dung',b.persona]]),gc)}

    ${sect('2 · Thumbnail — vẽ gì',kvt(b.thumb),gc)}

    ${sect('3 · Âm nhạc — dựng thế nào',kvt(b.music),gc)}

    ${sect('4 · Cấu trúc bài & thời lượng',kvt(b.struct)+specNote,gc)}

    ${sect('5 · Công thức tiêu đề',`<div style="font-size:13px;line-height:1.75">${
      b.title}</div>`,gc)}

    ${sect('6 · Lịch đăng & mười video đầu',kvt([
      ['Nhịp đăng',p.cadence
       ?`<b>${dc(p.cadence,1)} video/tuần</b> — nhịp thật của nhóm kênh dẫn đầu hướng này`
       :'chưa đo được'],
      ['Quy mô hiện tại',`${vn(sp.n_ch)} kênh · ${vn(sp.n)} video`],
      ['Mười video đầu',b.first10||'—']]),gc)}

    ${sect('7 · Điều kiện dừng hoặc đổi hướng',kvt([
      ['Sau 10 video',`Nếu view/ngày trung vị dưới <b>${dc(DV.base_vpd,1)}</b>
       (mặt bằng ngách) thì dừng lại soát công thức, đừng đăng tiếp.`],
      ['Sau 30 video',`Nếu chưa có video nào vượt <b>${dc(DV.base_vpd*5,0)}</b>
       view/ngày (gấp 5 lần mặt bằng) thì hướng đi hoặc cách làm có vấn đề.`],
      ['Dấu hiệu đúng','Tỷ lệ bình luận trên view tăng dần, và bình luận bắt đầu '
       +'mang đúng tín hiệu của hướng này.']])
      +`<div class="avoidbx"><b>Tránh trong hướng này.</b> ${b.avoid}</div>`,gc)}`;

    /* ── MẶT «GIẢI THÍCH» = BẰNG CHỨNG ── */
    const ev=p.kind==='title'
     ?`<table class="tb"><thead><tr><th>Phép đo</th><th class="num">Giá trị</th>
        <th>Đọc là</th></tr></thead><tbody>
       <tr><td>Số video mang định vị</td><td class="num">${vn(p.n)}</td>
        <td>${dc(p.share,1)}% thị trường · ${vn(p.n_channels)} kênh</td></tr>
       <tr><td>View/ngày nhóm này</td><td class="num">${dc(p.vpd,2)}</td>
        <td>tính trên video đã đủ 60 ngày</td></tr>
       <tr><td>View/ngày nhóm còn lại</td><td class="num">${dc(p.vpd_other,2)}</td>
        <td>mặt bằng để so</td></tr>
       <tr><td>Chênh lệch</td><td class="num"><b>${dc(p.lift,2)}×</b></td>
        <td style="color:var(${p.lift>1?'--pos':'--neg'})">${
         p.lift>1?'cao hơn':'THẤP HƠN'} mặt bằng</td></tr>
       <tr><td>p-value</td><td class="num">${p.p.toExponential(2).replace('.',',')}</td>
        <td>${p.p<0.05?'có ý nghĩa thống kê':'KHÔNG có ý nghĩa'}</td></tr>
       <tr><td>Kiểm trong từng kênh</td><td class="num"><b>${dc(p.within,2)}×</b></td>
        <td>${p.n_better}/${p.n_ch} kênh làm hướng này tốt hơn chính mình</td></tr>
       </tbody></table>
      <div class="scale"><b>Vì sao phải kiểm trong từng kênh.</b>
       Chênh lệch thô có thể đánh lừa: nếu vài kênh mạnh tình cờ hay làm hướng
       này, con số sẽ đẹp dù bản thân hướng đi không có tác dụng. Kiểm trong
       từng kênh hỏi câu khác — <i>cùng một kênh, khi làm hướng này có thắng
       chính mình không?</i> Ở đây <b>${p.n_better}/${p.n_ch} kênh</b> tốt hơn,
       trung vị <b>${dc(p.within,2)}×</b>. ${p.within>=1.1
        ?'Hiệu ứng nhất quán — tin được.'
        :'Hiệu ứng KHÔNG nhất quán — phần lớn chênh lệch thô đến từ việc kênh nào làm, không phải từ hướng đi.'}</div>`
     :`<table class="tb"><thead><tr><th>Phép đo</th><th class="num">Giá trị</th>
        <th>Đọc là</th></tr></thead><tbody>
       <tr><td>Bình luận mang tín hiệu</td><td class="num">${vn(p.n)}</td>
        <td>trên ${vn(DV.n_comments)} bình luận đã lọc</td></tr>
       <tr><td>Lượt thích trung vị nhóm này</td><td class="num"><b>${dc(p.like,1)}</b></td>
        <td>người khác đọc và đồng tình</td></tr>
       <tr><td>Lượt thích nền của ngách</td><td class="num">${dc(p.base,1)}</td>
        <td>mốc để so</td></tr>
       <tr><td>Chênh lệch</td><td class="num"><b style="color:var(--pos)">${
         dc(p.lift,2)}×</b></td><td>gấp ${dc(p.lift,1)} lần nền</td></tr>
       <tr><td>p-value</td><td class="num">${p.p.toExponential(2).replace('.',',')}</td>
        <td>${p.p<0.05?'có ý nghĩa thống kê':'KHÔNG có ý nghĩa'}</td></tr>
       <tr><td>Số video dính tín hiệu</td><td class="num">${vn(p.n_videos)}</td>
        <td>xem danh sách bên dưới</td></tr>
       </tbody></table>
      <div class="scale"><b>Vì sao đo bằng lượt thích chứ không đếm số lần xuất hiện.</b>
       Tần suất chỉ đo <i>«có người nói»</i>. Lượt thích đo <i>«người khác đọc và
       gật đầu»</i> — hai thứ khác nhau, và thứ hai mới đáng tin. Đối chứng ngay
       trong ngách này: cụm về «chữa lành» xuất hiện nhiều gấp hàng chục lần cụm
       «finally», nhưng lượt thích trung vị chỉ 3 so với nền 4.</div>
      <div class="scale"><b>Đã kiểm bằng nền giả.</b> Năm cụm từ trung tính
       (amen · beautiful · thank you · god bless · love this) cho chênh lệch
       ${dc(DV.placebo.lo,2)}–${dc(DV.placebo.hi,2)}×. Hướng này
       <b>${dc(p.lift,2)}×</b> — nằm ngoài hẳn dải đó, nên không phải nhiễu
       của phép đo.</div>`;

    const spd=p.spread?`
     <div class="sprd">${[['p10',p.spread.p10],['p25',p.spread.p25],
       ['p50',p.spread.p50],['p75',p.spread.p75],['p90',p.spread.p90]]
      .map(([k,v],i)=>`<i class="${i>=3?'hi':''}" style="height:${
       Math.max(2,100*Math.pow(v/p.spread.p90,.42))}%" data-h="${k} = ${dc(v,1)} view/ngày"></i>`).join('')}</div>
     <div class="sprdl"><span>10% kém nhất · ${dc(p.spread.p10,1)}</span>
      <span>giữa · ${dc(p.spread.p50,1)}</span>
      <span>10% giỏi nhất · ${dc(p.spread.p90,1)}</span></div>
     <p style="font-size:12.5px;line-height:1.6;margin:10px 0 0">Cùng một hướng đi,
      nhóm giỏi nhất hơn nhóm kém nhất <b>${dc(p.spread.ratio,1)} lần</b>
      (cao nhất chạm ${dc(p.spread.max,1)}). Chọn đúng hướng mới là điều kiện cần —
      <b>thực thi mới quyết định</b>.</p>`:'<p>Chưa đủ mẫu để đo biên độ.</p>';

    const exp=`<p class="lead2">Từ đây là <b>bằng chứng</b> cho mọi con số ở mặt
      «Kết luận». Nếu chỉ cần bắt tay làm thì mặt kia đã đủ; phần này dành cho
      lúc cần kiểm lại hoặc thuyết phục người khác.</p>

     ${sect('8 · Bằng chứng — vì sao tin (hoặc không tin) được',ev,gc)}

     ${sect('9 · Video đối chứng — tra tận nơi',
       `<p>Tra bằng <code>youtube.com/watch?v=&lt;video_id&gt;</code>.
        ${p.vids.sig?'Cột «tín hiệu» là số bình luận khớp.':''}</p>
        ${vtab(p.vids.top,p.vids.sig)}
        ${p.vids.worst.length?`<h3 style="margin-top:18px">Và đây là nhóm làm cùng
         hướng nhưng thất bại</h3>
         <p class="small" style="color:var(--mut);font-size:12px">Quan trọng ngang
          danh sách trên: cùng hướng đi, cùng ngách, nhưng view/ngày rất thấp.</p>
         ${vtab(p.vids.worst,false)}`:''}`,gc)}

     ${sect('10 · Khoảng cách giữa làm dở và làm giỏi',spd,gc)}

     ${sect('11 · Kênh đang làm hướng này',
       `<p>Tham khảo cách họ đóng gói.</p>
        <table class="vt"><thead><tr><th>Kênh</th><th class="n">Video</th>
        <th class="n">View/ngày</th><th class="n">Tổng view</th></tr></thead><tbody>
        ${p.chans.map(c=>`<tr><td class="vch">@${esc(c.ch)}</td>
         <td class="n">${vn(c.n)}</td><td class="n">${dc(c.vpd,1)}</td>
         <td class="n">${vn(c.view)}</td></tr>`).join('')}</tbody></table>`,gc)}

     ${p.quotes.length?sect('12 · Khán giả nói gì',
       `<p class="small" style="color:var(--mut);font-size:12px">Trích dẫn đã bỏ
        định danh — không kèm tên tài khoản, không kèm mã bình luận.</p>
        ${p.quotes.map(q=>`<div class="qz">“${esc(q.t)}”
         <span class="ql">${vn(q.like)} lượt thích</span></div>`).join('')}`,gc):''}

     ${sect('13 · Giới hạn của kết luận này',`<table class="kv"><tbody>
       <tr><td class="k">Nguồn</td><td>Toàn bộ từ YouTube. Câu «hướng này còn
        trống không» chỉ suy gián tiếp được — YouTube chỉ thấy cung đã tồn tại,
        không thấy cầu chưa được phục vụ.</td></tr>
       <tr><td class="k">Số lần đo</td><td>Chỉ <b>một lần</b> (${DV.crawl}).
        Không đo được tốc độ tăng trưởng thật của từng video.</td></tr>
       <tr><td class="k">Thiên lệch</td><td>Dữ liệu chỉ chứa kênh <b>còn tồn
        tại</b>. Kênh đã thất bại và bị xoá không xuất hiện — mọi tỷ lệ thành
        công đều lạc quan hơn thực tế.</td></tr>
       ${p.kind==='title'&&p.n_ch<5?`<tr><td class="k">Kiểm Simpson</td>
        <td>Chỉ dựa trên <b>${p.n_ch} kênh</b> đủ mẫu. Dưới 5 kênh thì chưa loại
        trừ được hiệu ứng gộp kênh.</td></tr>`:''}
       </tbody></table>`,gc)}

     ${srcs(['<b>Nguồn</b> 99_report/_dinh-vi/positioning.json',
       '<b>Bản đầy đủ</b> 99_report/_dinh-vi/DV-'+p.id+'_*.pdf',
       '<b>Mẫu</b> '+vn(DV.n_matured)+' video đã đủ 60 ngày · đo ngày '+DV.crawl])}`;

    return{sum:sum,exp:exp};
   }});
 });
})()"""


if __name__ == "__main__":
    main()
