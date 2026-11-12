"""Standalone real-font specimen and distributable study archive."""
from pathlib import Path
import base64,json,html,zipfile
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'fonts/rounded'
css=[]
for family,weight,path in [('B2',400,ROOT/'fonts/refinement/MMCodingB2-Regular.woff2'),('B3',400,OUT/'MMCodingB3-Regular.woff2'),('B3',700,OUT/'MMCodingB3-Bold.woff2')]:
 css.append('@font-face{font-family:'+family+';font-weight:'+str(weight)+';src:url(data:font/woff2;base64,'+base64.b64encode(path.read_bytes()).decode()+') format("woff2")}')
code='''// 받침과 영문이 자연스럽게 이어지는 코드
const 값 = 목록.filter(x => x !== null);
if (읽기 >= 10 && 쓰기 <= 20) return 값;
0O o0  1I l1  Il|  {} [] ()  ,.;: '"`
!= !== == === => -> <= >= || :: := <=>
~/프로젝트 $ git diff --stat
┌────────────┬────────────┐
│ Regular    │ 한글 두 칸 │
└────────────┴────────────┘'''
sections=[]
for title,family,weight in [('B2 · 이전 Regular','B2',400),('B3 · Regular','B3',400),('B3 · Bold','B3',700)]:
 rows=''.join(f'<div class="size-row"><span>{s}px</span><div class="sample" style="font-size:{s}px">한글 값 읽기 난 단 달 맘 밥 · Hamburgefonts 0O1Il != =&gt;</div></div>' for s in (12,13,14,16))
 sections.append(f'<section style="--family:{family};--weight:{weight}"><h2>{title}</h2><div class="large sample">난 단 달 맘 밥 값</div><pre class="sample code">{html.escape(code)}</pre>{rows}</section>')
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MM Coding · B3 형태와 굵기</title><style>'''+''.join(css)+'''
:root{color-scheme:dark;--bg:#17191c;--panel:#202328;--fg:#e6e5e1;--muted:#a7acae;--border:#3c4147;--size:14px}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.6 system-ui,sans-serif}body.light{color-scheme:light;--bg:#f4f2ec;--panel:#fffef9;--fg:#23272b;--muted:#62696c;--border:#cbc9c0}main{max-width:1500px;margin:auto;padding:40px 24px}header{max-width:800px}h1{font-size:32px;letter-spacing:-1px;margin:8px 0}p{color:var(--muted)}.eyebrow{font-size:12px;letter-spacing:2px;color:#93b5a4}nav{display:flex;gap:16px;flex-wrap:wrap;align-items:center;margin:24px 0}button,select{background:var(--panel);border:1px solid var(--border);border-radius:4px;color:var(--fg);padding:8px 12px;font:inherit}input{accent-color:#93b5a4}a{color:inherit;text-underline-offset:4px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}section{min-width:0;background:var(--panel);border:1px solid var(--border);padding:18px}h2{font:600 14px system-ui;margin:0 0 20px}.sample{font-family:var(--family);font-weight:var(--weight);font-synthesis:none;font-feature-settings:"calt" 1,"liga" 1}.no-ligs .sample{font-feature-settings:"calt" 0,"liga" 0}.large{font-size:36px;white-space:nowrap;overflow:auto;padding:8px 0 22px}.code{font-size:var(--size);line-height:1.65;overflow:auto;padding-bottom:12px;min-height:260px}.size-row{border-top:1px solid var(--border);padding:12px 0;overflow:auto}.size-row span{color:var(--muted);font-size:11px}.size-row .sample{white-space:nowrap}footer{margin-top:26px;color:var(--muted);font-size:13px}@media(max-width:1100px){.grid{grid-template-columns:1fr}.code{min-height:0}}@media(max-width:500px){main{padding:24px 12px}h1{font-size:27px}}
</style><main><header><div class="eyebrow">MM CODING / STUDY 03</div><h1>작은 글자까지, 같은 목소리로.</h1><p>Iosevka 550과 본고딕의 획을 맞추고, 받침 왼쪽 아래를 부드럽게 다듬었습니다. 실제 Regular와 Bold를 나란히 비교하세요.</p></header><nav><label>코드 크기 <select id="size"><option>12</option><option>13</option><option selected>14</option><option>16</option><option>18</option></select></label><label><input type="checkbox" id="ligs" checked> 코딩 리거처</label><button id="theme">밝은 배경</button><a href="../fonts/rounded/MMCoding-B3-0.3.0.zip">폰트 내려받기</a></nav><div class="grid">'''+''.join(sections)+'''</div><footer>실제 폰트를 내장한 비교 화면 · 영문 550 / 한글 1100 units · 브라우저 100% 확대에서 비교하세요.<br>12·13·14·16px 및 2배 픽셀 크기의 실험 힌팅 포함. macOS와 Windows의 렌더링은 다를 수 있습니다. Windows 실기 검증은 아직 진행하지 않았습니다.<br><a href="rounded-weights.md">설계·검증 기록</a></footer></main><script>document.querySelector('#size').onchange=e=>document.documentElement.style.setProperty('--size',e.target.value+'px');document.querySelector('#ligs').onchange=e=>document.body.classList.toggle('no-ligs',!e.target.checked);document.querySelector('#theme').onclick=e=>{let light=document.body.classList.toggle('light');e.target.textContent=light?'어두운 배경':'밝은 배경'};</script></html>'''
(ROOT/'docs/b3-comparison.html').write_text(page)
with zipfile.ZipFile(OUT/'MMCoding-B3-0.3.0.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in OUT.iterdir():
  if p.suffix in ('.ttf','.woff2','.json'):z.write(p,p.name)
 for p in (OUT/'licenses').iterdir():z.write(p,'licenses/'+p.name)
 for p in [ROOT/'docs/rounded-weights.md',ROOT/'sources/b3-hint-profiles.json']:z.write(p,p.name)
 for p in (ROOT/'docs').glob('b3-*verification.json'):z.write(p,p.name)
 for p in (ROOT/'docs/proofs').glob('b3-*.png'):z.write(p,'proofs/'+p.name)
print('B3 specimen and archive written')
