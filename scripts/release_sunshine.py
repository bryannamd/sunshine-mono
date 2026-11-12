"""Rename verified B3 fonts and create the official Sunshine Mono release bundle.

Only naming and head revision metadata change. Outlines, metrics, OpenType
layout and TrueType instructions must remain byte-identical to the B3 input.
"""
from pathlib import Path
import hashlib,json,shutil,zipfile
from fontTools.ttLib import TTFont
import freetype
from verify_rounded import shape,OPERATORS,SIZES
ROOT=Path(__file__).resolve().parents[1]
VERSION='0.3.0'
OUT=ROOT/'fonts/releases'/VERSION
URL='https://github.com/bryannamd/sunshine-mono'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(source_dir=None, report_path=None, readme_path=None, extra_licenses=(),
         source_description='Iosevka and Source Han Sans', extra_credit=''):
 OUT.mkdir(parents=True,exist_ok=True)
 report={'version':VERSION,'family':'Sunshine Mono','credit':'Sunshine Mono by SunWorks','fonts':[], 'windows_directwrite_verified':False,'desktop_apps_verified':False}
 for style in ('Regular','Bold'):
  source=(source_dir or ROOT/'fonts/rounded')/f'MMCodingB3-{style}.ttf'
  original=TTFont(source,recalcTimestamp=False)
  font=TTFont(source,recalcTimestamp=False);ps=f'SunshineMono-{style}'
  copyright_text=(font['name'].getDebugName(0) or '')+'\nSunshine Mono modifications Copyright 2026 SunWorks.'
  ids={0,1,2,3,4,5,6,8,9,10,11,12,16,17,18,21,22,25}
  font['name'].names=[n for n in font['name'].names if n.nameID not in ids]
  major,minor,patch=map(int,VERSION.split('.'))
  revision=major+minor/10+patch/1000
  values={0:copyright_text,1:'Sunshine Mono',2:style,3:f'{VERSION};SunWorks;{ps}',4:f'Sunshine Mono {style}',5:f'Version {revision:.3f}',6:ps,8:'SunWorks',9:'SunWorks; based on Iosevka by Renzhi Li and Source Han Sans by Adobe',10:'Sunshine Mono by SunWorks. Korean and Latin monospace font for code and terminals.',11:URL,12:URL,16:'Sunshine Mono',17:style}
  values[9]+=extra_credit
  for nid,value in values.items():
   font['name'].setName(value,nid,3,1,0x409)
   font['name'].setName(value,nid,1,0,0)
  font['head'].fontRevision=revision
  target=OUT/f'{ps}.ttf';font.save(target)
  font.flavor='woff2';font.save(OUT/f'{ps}.woff2')
  renamed=TTFont(target,recalcTimestamp=False)
  assert set(original.keys())==set(renamed.keys())
  unchanged=[]
  for tag in original.keys():
   if tag in ('GlyphOrder','name','head'):continue
   assert original.getTableData(tag)==renamed.getTableData(tag),tag
   unchanged.append(tag)
  for nid,value in values.items():assert renamed['name'].getDebugName(nid)==value
  assert not any('MM Coding' in n.toUnicode() or 'MMCoding' in n.toUnicode() for n in renamed['name'].names)
  assert renamed['OS/2'].usWeightClass==(700 if style=='Bold' else 400)
  assert bool(renamed['head'].macStyle&1)==(style=='Bold')
  cmap=renamed.getBestCmap()
  for cp in range(0xAC00,0xD7A4):assert renamed['hmtx'][cmap[cp]][0]==1100
  for cp in range(32,127):assert renamed['hmtx'][cmap[cp]][0]==550
  for op in OPERATORS:
   off,w1=shape(target,op,False);on,w2=shape(target,op,True)
   assert off!=on and w1==w2==550*len(op)
  face=freetype.Face(str(target));count=0
  for size in SIZES:
   face.set_pixel_sizes(0,size)
   for cp in list(range(0xAC00,0xD7A4))+list(range(32,127)):
    face.load_char(cp,freetype.FT_LOAD_RENDER|freetype.FT_LOAD_TARGET_NORMAL|freetype.FT_LOAD_PEDANTIC);count+=1
  web=TTFont(OUT/f'{ps}.woff2')
  assert web['name'].getDebugName(1)=='Sunshine Mono'
  assert web.getBestCmap()==cmap
  report['fonts'].append({'style':style,'ttf':target.name,'sha256':sha(target),'source_b3_sha256':sha(source),'unchanged_tables':unchanged,'strict_freetype_renders':count,'ligatures_verified':list(OPERATORS)})
  print(style,'metadata and unchanged tables verified;',count,'renders passed',flush=True)
 (OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 (report_path or ROOT/'docs/sunshine-release-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 shutil.copy2(readme_path or ROOT/'docs/sunshine-install.md',OUT/'README.md')
 (OUT/'licenses').mkdir(exist_ok=True)
 for name in ('iosevka-OFL.txt','source-han-OFL.txt',*extra_licenses):shutil.copy2(ROOT/'sources/licenses'/name,OUT/'licenses'/name)
 (OUT/'NOTICE.txt').write_text('Sunshine Mono by SunWorks\nBased on '+source_description+'.\nFont software licensed under SIL Open Font License 1.1.\nOriginal copyrights and license texts are retained in licenses/ and embedded font metadata.\nSource: '+URL+'\n')
 # Explicit allowlist avoids accidentally distributing old or unhinted test fonts.
 files=[OUT/f'SunshineMono-{s}.{ext}' for s in ('Regular','Bold') for ext in ('ttf','woff2')]
 files += [OUT/'README.md',OUT/'NOTICE.txt',OUT/'manifest.json',*sorted((OUT/'licenses').glob('*.txt'))]
 archive=OUT/f'SunshineMono-{VERSION}.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for p in files:z.write(p,str(Path(f'SunshineMono-{VERSION}')/p.relative_to(OUT)))
 with zipfile.ZipFile(archive) as z:assert z.testzip() is None
 checks=[archive,*files]
 (OUT/'SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.relative_to(OUT)}\n' for p in checks))
 print('Packaged',archive)
if __name__=='__main__':main()
