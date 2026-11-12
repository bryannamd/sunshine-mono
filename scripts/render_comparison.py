"""Create an offline, self-contained specimen from the actual prototype WOFF2 files."""
from pathlib import Path
import base64
import html
import json
import argparse
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--refine-b", action="store_true")
args = parser.parse_args()
font_dir = ROOT / ("fonts/refinement" if args.refine_b else "fonts/prototypes")
manifest = json.loads((font_dir / "manifest.json").read_text())
if args.refine_b:
    original = json.loads((ROOT / "fonts/prototypes/manifest.json").read_text())
    baseline = next(f for f in original["fonts"] if f["id"] == "B")
    baseline["label"] = "Iosevka 550 · 기존안"
    for kind in ("ttf", "woff2"):
        shutil.copy2(ROOT / "fonts/prototypes" / baseline[kind], font_dir / baseline[kind])
    manifest["fonts"].insert(0, baseline)
css = []
for item in manifest["fonts"]:
    data = base64.b64encode((font_dir / item["woff2"]).read_bytes()).decode()
    css.append('@font-face{font-family:"' + item["family"] + '";src:url(data:font/woff2;base64,'
               + data + ') format("woff2");font-weight:400;font-style:normal;font-display:block}')
template = (ROOT / "scripts/specimen-template.html").read_text()
if args.refine_b:
    replacements = {
        "네 가지 시안": "B · B2 문자 구분 비교",
        "네 가지 영문": "두 가지 영문",
        "네 시안": "두 시안",
        '<option value="A">시안 A</option>': '',
        '<option value="C">시안 C</option><option value="D">시안 D</option>': '<option value="B2">시안 B2</option>',
        '../fonts/prototypes/': '../fonts/refinement/',
        'MMCoding-prototypes-0.1.0.zip': 'MMCoding-B-B2-comparison.zip',
        'prototype-build.md': 'glyph-refinement.md',
        'Cascadia Mono는 프로그래밍 리거처가 없는 판입니다.': 'B2는 점 있는 0, 받침 있는 1, 꼬리 있는 l을 선택했습니다. I는 기존 형태를 유지했습니다.',
        'const total = 1234567890; // 0O 1Il rn m': 'const total = 1001; // 0O 1Il null ill\nconst isValid = value !== null; // IIl1 lI10',
        '0 O o Q    1 I l | !    rn m    cl d': '0 O o Q    1 I l | !    rn m    cl d\nnull  ill  Il1  lI1  1001  O0O0  hello',
        'section.append(header,meta,pre);grid.append(section);': 'const zoom=document.createElement("div");zoom.className="glyph-zoom";zoom.style.fontFamily=`"${item.family}"`;zoom.textContent="0 O  1 I l";zoom.setAttribute("aria-label",`${item.id} 주요 자형 확대`);section.append(header,meta,zoom,pre);grid.append(section);',
        '.license-text{': '.glyph-zoom{font-size:clamp(40px,4vw,64px);line-height:1.5;padding:12px 18px;background:var(--paper);overflow:auto;font-synthesis:none;white-space:pre;margin-bottom:1px}.license-text{',
        '같은 한글에 두 가지 영문을 조합했습니다. 이름을 가리고 첫인상을 고른 뒤, 작은 글자와 긴 주석에서 다시 비교해 보세요.': 'Iosevka 550의 비례와 한글을 유지하고, 0·1·l의 구분을 다듬었습니다. 확대 자형과 실제 코드에서 기존 B안과 비교하세요.',
    }
    for old, new in replacements.items():
        if old not in template:
            raise ValueError(f"Specimen template changed; missing {old!r}")
        template = template.replace(old, new)
page = template.replace("/* FONT_FACES */", "\n".join(css)).replace("/* FONT_DATA */", json.dumps(manifest, ensure_ascii=False))
licenses = []
for path in sorted((ROOT / "sources/licenses").glob("*.txt")):
    if args.refine_b and path.name not in ("source-han-OFL.txt", "iosevka-OFL.txt"):
        continue
    licenses.append('<details><summary>' + html.escape(path.stem) + '</summary><div class="license-text">'
                    + html.escape(path.read_text()) + '</div></details>')
page = page.replace("<!-- FONT_LICENSES -->", "\n".join(licenses))
output = ROOT / "docs" / ("b2-comparison.html" if args.refine_b else "prototype-comparison.html")
output.write_text(page)
print(f"Created {output.name} (embedded fonts; works offline)")
if args.refine_b:
    with zipfile.ZipFile(font_dir / "MMCoding-B-B2-comparison.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for item in manifest["fonts"]:
            for kind in ("ttf", "woff2"):
                archive.write(font_dir / item[kind], item[kind])
        for filename in ("source-han-OFL.txt", "iosevka-OFL.txt"):
            archive.write(ROOT / "sources/licenses" / filename, "licenses/" + filename)
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        archive.writestr("README.txt", "MM Coding B / B2 comparison prototypes.\n"
                         "B2: dotted zero, one with base, serifed I, serifed flat-tailed l.\n"
                         "Iosevka native variants, not copied JetBrains outlines.\n"
                         "550-unit Latin / 1100-unit Hangul. Regular, unhinted prototypes.\n"
                         "Retain the included OFL licenses when redistributing.\n")
    with zipfile.ZipFile(font_dir / "MMCoding-B-B2-comparison.zip") as archive:
        assert archive.testzip() is None
    print("Created and verified B/B2 font and license archive")
