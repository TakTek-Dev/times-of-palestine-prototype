// node --experimental-websocket tools/probe.mjs <url> <width> <height> "<js expression returning JSON-able>"
import { spawn } from 'node:child_process';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { writeFileSync } from 'node:fs';
const [url, w = '1280', h = '900', expr = '1', shot = '', scheme = 'light', fresh = ''] = process.argv.slice(2);
const port = 9300 + Math.floor(Math.random() * 400);
const proc = spawn('C:/Program Files/Google/Chrome/Application/chrome.exe', ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${mkdtempSync(join(tmpdir(), 'tp-probe-'))}`, '--no-first-run', 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws, id = 0; const pending = new Map();
const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
try {
  let target;
  for (let k = 0; k < 50 && !target; k++) { try { target = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((t) => t.type === 'page'); } catch {} await sleep(150); }
  ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((r) => ws.addEventListener('open', r));
  const logs = [];
  ws.addEventListener('message', (ev) => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); } else if (m.method === 'Runtime.exceptionThrown') logs.push('EXC ' + m.params.exceptionDetails.text + ' ' + (m.params.exceptionDetails.exception?.description || '')); else if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') logs.push('LOG ' + m.params.entry.text + ' ' + (m.params.entry.url || '')); });
  await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: +w, height: +h, deviceScaleFactor: 1, mobile: +w < 768 });
  await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: scheme }] });
  if (!fresh) await send('Page.addScriptToEvaluateOnNewDocument', { source: "try{sessionStorage.setItem('tp-on','1')}catch(e){}" });
  await send('Page.navigate', { url }); await sleep(fresh ? +fresh : 2500);
  const r = await send('Runtime.evaluate', { expression: `JSON.stringify(${expr})`, returnByValue: true, awaitPromise: true });
  if (shot) { await sleep(700); writeFileSync(shot, Buffer.from((await send('Page.captureScreenshot', { format: 'png' })).data, 'base64')); }
  console.log(r.result.value ?? JSON.stringify(r)); if (logs.length) console.log(logs.join('\n'));
} finally { try { ws && ws.close(); } catch {} proc.kill(); }
