"""B3: native Iosevka weights, optically matched Hangul, conservative final-corner rounding."""
from pathlib import Path
from array import array
import hashlib
import json
import math
import statistics
import shutil
import pathops
from fontTools.ttLib.removeOverlaps import ttfGlyphFromSkPath

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.pens.recordingPen import DecomposingRecordingPen, RecordingPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "fonts/rounded"
UP = ROOT / "sources/upstream"
SX_ESTIMATE = 0.9605947955390335
# Final consonants containing ㄴ ㄷ ㄹ ㅁ ㅂ ㅌ ㅍ. Avoid rounding ㄱ terminal caps.
ANGULAR_FINALS = {4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 25, 26}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mieum_stems(gs, cmap, sx):
    pen = RecordingPen()
    gs[cmap[0x3141]].draw(pen)
    parts, bpen = [], BoundsPen(gs)
    for op, args in pen.value:
        getattr(bpen, op)(*args)
        if op == "closePath":
            parts.append(bpen.bounds)
            bpen = BoundsPen(gs)
    outer = max(parts, key=lambda b: (b[2]-b[0])*(b[3]-b[1]))
    inner = min(parts, key=lambda b: (b[2]-b[0])*(b[3]-b[1]))
    return (((outer[2]-outer[0])-(inner[2]-inner[0]))*.5*sx,
            ((outer[3]-outer[1])-(inner[3]-inner[1]))*.5)


def h_stems(font):
    points = font["glyf"][font.getBestCmap()[ord("H")]].getCoordinates(font["glyf"])[0]
    xs, ys = sorted(set(x for x, y in points)), sorted(set(y for x, y in points))
    return xs[1]-xs[0], ys[2]-ys[1]


def round_final(glyph, glyf, cp, radius, stem):
    if (cp-0xAC00) % 28 not in ANGULAR_FINALS:
        return []
    coords, ends, flags = glyph.getCoordinates(glyf)
    ymin, ymax = min(y for x, y in coords), max(y for x, y in coords)
    cutoff = ymin + .22*(ymax-ymin)
    output, output_flags, output_ends, changes = [], [], [], []
    start = 0
    for end in ends:
        pts = list(coords[start:end+1]); fs = list(flags[start:end+1]); n = len(pts)
        area = sum(pts[i][0]*pts[(i+1)%n][1]-pts[(i+1)%n][0]*pts[i][1] for i in range(n))
        for i, p in enumerate(pts):
            a, b = pts[(i-1)%n], pts[(i+1)%n]
            u, v = (a[0]-p[0], a[1]-p[1]), (b[0]-p[0], b[1]-p[1])
            lower_left = ((abs(u[0]) <= 1 and u[1] > 0 and v[0] > 0 and abs(v[1]) <= 1)
                          or (u[0] > 0 and abs(u[1]) <= 1 and abs(v[0]) <= 1 and v[1] > 0))
            # CW exterior, convex turn, two actual straight edges, sufficiently long to be a joint.
            cross = (-u[0])*v[1]-(-u[1])*v[0]
            lengths = (math.hypot(*u), math.hypot(*v))
            eligible = (area < 0 and cross < 0 and lower_left and p[1] <= cutoff
                        and all(fs[j%n] & 1 for j in (i-1, i, i+1))
                        and min(lengths) > 1.12*stem)
            if eligible:
                r = min(radius, .3*min(lengths))
                before = (round(p[0]+u[0]/lengths[0]*r), round(p[1]+u[1]/lengths[0]*r))
                after = (round(p[0]+v[0]/lengths[1]*r), round(p[1]+v[1]/lengths[1]*r))
                output.extend([before, p, after]); output_flags.extend([1, 0, 1])
                changes.append({"corner": list(p), "radius": r})
            else:
                output.append(p); output_flags.append(fs[i])
        output_ends.append(len(output)-1)
        start = end+1
    if changes:
        glyph.coordinates = GlyphCoordinates(output)
        glyph.flags = array("B", output_flags)
        glyph.endPtsOfContours = output_ends
        glyph.recalcBounds(glyf)
    return changes


def set_names(font, style, source_copyright):
    bold = style == "Bold"
    family, ps = "MM Coding B3", "MMCodingB3-"+style
    name = font["name"]
    copyright_text = (name.getDebugName(0) or "") + "\n" + source_copyright
    ids = {0,1,2,3,4,5,6,13,14,16,17,18,21,22,25}
    name.names = [n for n in name.names if n.nameID not in ids]
    values = {0:copyright_text,1:family,2:style,3:"0.300;MMCF;"+ps,4:family+" "+style,
              5:"Version 0.300; rounded Hangul study",6:ps,16:family,17:style,
              13:(ROOT/"sources/licenses/iosevka-OFL.txt").read_text()+"\n"+(ROOT/"sources/licenses/source-han-OFL.txt").read_text(),
              14:"https://openfontlicense.org"}
    for nid, text in values.items():
        name.setName(text,nid,3,1,0x409)
    font["OS/2"].usWeightClass = 700 if bold else 400
    font["OS/2"].fsSelection &= ~((1<<0)|(1<<5)|(1<<6))
    font["OS/2"].fsSelection |= (1<<5) if bold else (1<<6)
    font["head"].macStyle = 1 if bold else 0


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    variable = TTFont(UP/"source-han-kr-vf.ttf")
    cmap = variable.getBestCmap()
    syllables = list(range(0xAC00,0xD7A4))
    cps = syllables+[cp for cp in list(range(0x1100,0x1200))+list(range(0x3130,0x3190)) if cp in cmap]
    manifest = {"version":"0.3.0","source_han_sha256":digest(UP/"source-han-kr-vf.ttf"),"fonts":[]}
    for style, filename, radius in [("Regular","iosevka-b2.ttf",24),("Bold","iosevka-b3-bold.ttf",36)]:
        font = TTFont(UP/filename,recalcTimestamp=False)
        target_v,target_h = h_stems(font)
        def score(weight):
            v,h = mieum_stems(variable.getGlyphSet(location={"wght":weight}),cmap,SX_ESTIMATE)
            return ((v-target_v)/target_v)**2+((h-target_h)/target_h)**2
        weight = min(range(300,801),key=score)
        gs = variable.getGlyphSet(location={"wght":weight})
        recordings, boxes = {}, {}
        for cp in cps:
            pen = DecomposingRecordingPen(gs); gs[cmap[cp]].draw(pen)
            recordings[cp] = pen
            bp=BoundsPen(None);pen.replay(bp);boxes[cp]=bp.bounds
        original_ratio=statistics.median((boxes[cp][2]-boxes[cp][0])/(boxes[cp][3]-boxes[cp][1]) for cp in syllables)
        sx=.85/original_ratio
        print(style,"Han weight",weight,"Latin stems",(target_v,target_h),"Han stems",mieum_stems(gs,cmap,sx),flush=True)
        order=list(font.getGlyphOrder()); rounded={}
        for cp in cps:
            name=f"mmkr{cp:04X}"
            original_width=gs[cmap[cp]].width
            advance=0 if original_width==0 else 1100
            pen=TTGlyphPen(None)
            recordings[cp].replay(TransformPen(pen,(sx,0,0,1,(advance-original_width*sx)/2,0)))
            glyph=pen.glyph();font["glyf"][name]=glyph;glyph.recalcBounds(font["glyf"])
            if cp in range(0xAC00,0xD7A4):
                # Variable Source Han uses overlapping stroke contours. Union them
                # before identifying exterior joints; otherwise ㄴ looks like two caps.
                path=pathops.Path()
                glyph.draw(path.getPen(),font["glyf"])
                path.simplify(fix_winding=True,keep_starting_points=True,clockwise=True)
                glyph=ttfGlyphFromSkPath(path)
                font["glyf"][name]=glyph
                changes=round_final(glyph,font["glyf"],cp,radius,target_v)
                if changes:rounded[f"U+{cp:04X}"]=changes
            font["hmtx"].metrics[name]=(advance,getattr(glyph,"xMin",0));order.append(name)
            for table in font["cmap"].tables:
                if table.isUnicode() and table.format in (4,12):table.cmap[cp]=name
        font.setGlyphOrder(order)
        for tag in ("DSIG",):
            if tag in font:del font[tag]
        font["hhea"].ascent=1200;font["hhea"].descent=-300;font["hhea"].lineGap=0
        os2=font["OS/2"];os2.sTypoAscender=1200;os2.sTypoDescender=-300;os2.sTypoLineGap=0
        os2.usWinAscent=max(os2.usWinAscent,1200);os2.usWinDescent=max(os2.usWinDescent,300)
        if os2.version>=4:os2.fsSelection|=1<<7
        os2.recalcUnicodeRanges(font);os2.recalcCodePageRanges(font);os2.usLastCharIndex=min(0xFFFF,max(font.getBestCmap()))
        font["post"].isFixedPitch=1
        set_names(font,style,variable["name"].getDebugName(0) or "")
        path=OUT/f"MMCodingB3-{style}-Unhinted.ttf";font.save(path)
        manifest["fonts"].append({"style":style,"weight":700 if style=="Bold" else 400,
            "latin_input":filename,"latin_sha256":digest(UP/filename),"hangul_variable_weight":weight,
            "horizontal_scale":sx,"vertical_scale":1,"latin_stems":{"vertical":target_v,"horizontal":target_h},
            "hangul_stems":dict(zip(("vertical","horizontal"),mieum_stems(gs,cmap,sx))),
            "radius":radius,"rounded_glyph_count":len(rounded),"unhinted_ttf":path.name,
            "unhinted_sha256":digest(path),"rounded_glyphs":rounded})
        print(style,"rounded syllables",len(rounded),flush=True)
    (OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    (OUT/"licenses").mkdir(exist_ok=True)
    for name in ("source-han-OFL.txt","iosevka-OFL.txt"):
        shutil.copy2(ROOT/"sources/licenses"/name,OUT/"licenses"/name)


if __name__=="__main__":main()
