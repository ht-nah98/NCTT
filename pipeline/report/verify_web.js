// Kiểm _web/ho-so.html: cú pháp JS + mọi trang render không lỗi.
// Dựng DOM tối thiểu đủ để chạy đến chỗ tạo mảng PAGES rồi gọi f() từng trang.
const fs = require('fs');
const path = 'niches' in {} ? '' : '_web/ho-so.html';
const h = fs.readFileSync(path, 'utf8');

const blk = (h.match(/<script>([\s\S]*?)<\/script>/g) || [])
  .find(x => x.includes('const PAGES=['));
if (!blk) { console.log('  ✗ không thấy khối PAGES'); process.exit(1); }
const js = blk.replace(/^<script>|<\/script>$/g, '');

function jsonTag(id) {
  const re = new RegExp('<script id="' + id +
    '" type="application/json">([\\s\\S]*?)</script>');
  const m = h.match(re);
  return m ? m[1] : '{}';
}
const store = { P4: { textContent: jsonTag('P4') },
                DV: { textContent: jsonTag('DV') } };
global.document = {
  getElementById: i => store[i] ||
    { textContent: '{}', innerHTML: '', className: '', style: {} },
  querySelectorAll: () => [], addEventListener() {} };
global.window = global;
global.location = { hash: '' };
global.history = { replaceState() {} };
global.scrollTo = () => {};
global.navigator = {};
global.addEventListener = () => {};

let PAGES;
try {
  const cut = js.indexOf('/* ══ HẾT PHẦN V ══ */');
  PAGES = new Function(js.slice(0, cut) + '\nreturn PAGES;')();
} catch (e) { console.log('  ✗ lỗi cú pháp:', e.message); process.exit(1); }

let bad = 0;
PAGES.forEach((p, i) => {
  try {
    const d = p.f();
    const u = /\$\{|undefined|NaN/.exec(d.sum + d.exp);
    if (u) { console.log('  ⚠ trang', i + 1, p.t, '->', u[0]); bad++; }
  } catch (e) { console.log('  ✗ trang', i + 1, p.t, e.message); bad++; }
});
if (bad) { console.log('  ' + bad + ' trang lỗi'); process.exit(1); }
console.log('  ✓ ' + PAGES.length + ' trang sạch');
