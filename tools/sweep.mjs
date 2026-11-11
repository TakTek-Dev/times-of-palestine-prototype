// Overflow, broken-image and console sweep over pages x widths.  node tools/sweep.mjs
import { execFileSync } from 'node:child_process';
import { readdirSync } from 'node:fs';
const st = readdirSync('story'), tp = readdirSync('topic');
const pages = ['index.html', 'gaza.html', 'west-bank.html', 'analysis.html', 'explained.html', 'discover.html', 'search.html', 'about.html', 'contact.html', 'brand.html', '404.html',
  'story/' + st[0], 'story/' + st[Math.floor(st.length / 2)], 'story/' + st[st.length - 1], ...(tp.length ? ['topic/' + tp[0]] : [])];
const expr = `({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth,bad:[...document.querySelectorAll('body *')].filter(e=>{const b=e.getBoundingClientRect();return b.right>innerWidth+1&&b.width>0&&!e.closest('.rail,.sheet,.veil,.viewer')}).slice(0,4).map(e=>e.tagName+'.'+String(e.className).slice(0,24)),img:[...document.images].filter(i=>i.complete&&!i.naturalWidth&&i.getAttribute('src')).length})`;
let bad = 0;
for (const w of [375, 768, 1280]) for (const p of pages) {
  const out = execFileSync('node', ['--experimental-websocket', 'tools/probe.mjs', `http://127.0.0.1:8292/${p}`, String(w), '900', expr]).toString().trim();
  const j = JSON.parse(out.split('\n')[0]);
  if (j.sw > j.cw || j.bad.length || j.img || out.includes('\n')) { bad++; console.log(w, p, out); }
}
console.log(pages.length * 3, 'checks,', bad, 'with issues');
