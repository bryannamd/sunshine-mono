"""FreeType diagnostic proof: actual native-sized bitmaps, never a Windows screenshot."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import freetype
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/proofs';OUT.mkdir(exist_ok=True)
TEXT='한글 값 읽기 난 단 달 맘 밥 뚫 꽉 햇 에헤 Hmn 0O1Il'
def render(face,text,ppem,hinted):
 face.set_pixel_sizes(0,ppem)
 flags=freetype.FT_LOAD_RENDER|freetype.FT_LOAD_TARGET_NORMAL
 if not hinted:flags|=freetype.FT_LOAD_NO_HINTING
 im=Image.new('L',(int(len(text)*ppem*1.15)+10,ppem*2),0);x=2
 for ch in text:
  face.load_char(ch,flags);s=face.glyph;b=s.bitmap
  if b.width and b.rows:
   bitmap=Image.frombytes('L',(abs(b.pitch),b.rows),bytes(b.buffer)).crop((0,0,b.width,b.rows))
   im.paste(bitmap,(round(x)+s.bitmap_left,int(ppem*1.3)-s.bitmap_top))
  x+=s.advance.x/64
 return im.crop((0,0,round(x)+4,ppem*2))
for style in ['Regular','Bold']:
 face=freetype.Face(str(ROOT/f'fonts/rounded/MMCodingB3-{style}.ttf'))
 canvas=Image.new('RGB',(2300,1050),'#f7f6f2');draw=ImageDraw.Draw(canvas)
 draw.text((20,15),f'{style} / FreeType grayscale / left: no hints / right: hinted',fill='black',font_size=20)
 y=60
 for ppem in (12,13,14,16,24,26,28,32):
  draw.text((20,y),f'{ppem} PPEM',fill='black',font_size=14)
  for col,on in enumerate([False,True]):
   mask=render(face,TEXT,ppem,on)
   # 2x nearest neighbor makes exact sampled pixels inspectable.
   if ppem<20:mask=mask.resize((mask.width*2,mask.height*2),Image.Resampling.NEAREST)
   canvas.paste('#151719',(20+col*1140,y+24,20+col*1140+mask.width,y+24+mask.height),mask)
  y+=120
 canvas.save(OUT/f'b3-{style.lower()}-freetype.png')
print('Raster proofs written')
