"""Structural, shaping and strict FreeType interpreter validation of B3."""
from pathlib import Path
import json, unicodedata
import freetype
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'fonts/rounded'
SIZES=(12,13,14,16,24,26,28,32)
OPERATORS=('!=','!==','==','===','=>','->','<=','>=','||','::',':=','<=>','/*','*/','//')
def shape(path,text,on=True):
 f=hb.Font(hb.Face(path.read_bytes())); f.scale=(1000,1000)
 b=hb.Buffer();b.add_str(text);b.guess_segment_properties();hb.shape(f,b,{'calt':on,'liga':on})
 return [g.codepoint for g in b.glyph_infos],sum(p.x_advance for p in b.glyph_positions)
def outline(f,name):
 gs=f.getGlyphSet();p=DecomposingRecordingPen(gs);gs[name].draw(p);return p.value

def main():
 manifest=json.loads((OUT/'manifest.json').read_text());results=[]
 for r in manifest['fonts']:
  path=OUT/r['ttf'];f=TTFont(path);raw=TTFont(OUT/r['unhinted_ttf']);native=TTFont(ROOT/'sources/upstream'/r['latin_input']);c=f.getBestCmap()
  assert f['OS/2'].usWeightClass==r['weight']
  assert bool(f['head'].macStyle&1)==(r['style']=='Bold')
  for cp in range(0xAC00,0xD7A4):
   assert cp in c and f['hmtx'][c[cp]][0]==1100
   assert outline(f,c[cp])==outline(raw,raw.getBestCmap()[cp])
  for cp in range(32,127):
   assert f['hmtx'][c[cp]][0]==550
   assert outline(f,c[cp])==outline(native,native.getBestCmap()[cp])
  for axis in ('vertical','horizontal'):
   assert abs(r['hangul_stems'][axis]/r['latin_stems'][axis]-1)<.03
  for ch in '난단달맘밥값': assert f'U+{ord(ch):04X}' in r['rounded_glyphs'],ch
  for key,changes in r['rounded_glyphs'].items():
   cp=int(key[2:],16);assert (cp-0xAC00)%28 in {4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,25,26}
   g=f['glyf'][c[cp]]
   assert all(change['corner'][1]<=g.yMin+.22*(g.yMax-g.yMin)+1 for change in changes)
  ligatures=[]
  for op in OPERATORS:
   a,wa=shape(path,op,False);b,wb=shape(path,op,True)
   assert wa==wb==len(op)*550
   assert a!=b,op
   ligatures.append(op)
  for text in ('한글 코드 값 읽기','괜찮은 폰트','가각갂간갅갆갇갈'):
   assert shape(path,text)==shape(path,unicodedata.normalize('NFD',text))
  face=freetype.Face(str(path));renders=0
  for size in SIZES:
   face.set_pixel_sizes(0,size)
   for cp in list(range(0xAC00,0xD7A4))+list(range(32,127)):
    face.load_char(cp,freetype.FT_LOAD_RENDER|freetype.FT_LOAD_TARGET_NORMAL|freetype.FT_LOAD_PEDANTIC);renders+=1
  results.append({'style':r['style'],'strict_freetype_renders':renders,'ligatures_cell_width_verified':ligatures,'ascii_outlines_unchanged':True,'hinted_outlines_unchanged':True,'nfc_nfd_equivalent':True,'windows_directwrite_tested':False})
  print(results[-1],flush=True)
 (ROOT/'docs/b3-verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
