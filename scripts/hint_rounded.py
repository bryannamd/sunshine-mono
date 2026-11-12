"""Latin autohint + authored PPEM policies for confidently detected Hangul horizontal stems.

This is an experimental TrueType branch, not a claim of hand-reviewed hints for every glyph.
macOS proofing still uses the actual outlines. Windows DirectWrite must be tested separately.
"""
from pathlib import Path
from collections import defaultdict
import json
import hashlib

import ttfautohint
from ttfautohint import StemWidthMode
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables.ttProgram import Program

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"fonts/rounded"


def stem_pairs(glyph,glyf,expected):
    coords,ends,flags=glyph.getCoordinates(glyf)
    segments=[];start=0
    for end in ends:
        for i in range(start,end+1):
            j=start if i==end else i+1
            x,y=coords[i];xx,yy=coords[j]
            if flags[i]&1 and flags[j]&1 and abs(y-yy)<=1 and abs(xx-x)>65:
                segments.append((round((y+yy)/2),min(x,xx),max(x,xx),1 if xx>x else -1))
        start=end+1
    candidates=[]
    for i,a in enumerate(segments):
        for b in segments[i+1:]:
            gap=abs(a[0]-b[0]);overlap=min(a[2],b[2])-max(a[1],b[1])
            if a[3]!=b[3] and .78*expected<=gap<=1.22*expected and overlap>80:
                candidates.append((abs(gap-expected)/expected-overlap/100000,min(a[0],b[0]),max(a[0],b[0])))
    selected=[];used=set()
    for _,lo,hi in sorted(candidates):
        if lo not in used and hi not in used:
            selected.append((lo,hi));used.update((lo,hi))
    return coords,flags,selected


def make_hint(glyph,glyf,expected,profile):
    coords,flags,pairs=stem_pairs(glyph,glyf,expected)
    if not pairs:return None,[]
    assembly=["SVTCA[0]","PUSHB[ ]","1","SZPS[ ]","PUSHB[ ]","1","SLOOP[ ]"]
    covered=[]
    for size_text,desired_width in profile.items():
        ppem=int(size_text);anchors={}
        for lo,hi in pairs:
            bottom=round(lo*ppem/1000*4)/4
            anchors[lo]=bottom;anchors[hi]=bottom+desired_width
        levels=sorted(anchors)
        if any(anchors[b]<=anchors[a] for a,b in zip(levels,levels[1:])):continue
        moves=[]
        for index,(x,y) in enumerate(coords):
            if not flags[index]&1:continue
            match=next((level for level in levels if abs(y-level)<=.5),None)
            if match is not None:
                delta=round((anchors[match]-y*ppem/1000)*64)
                # Larger corrections risk distorting crowded syllables: leave them unhinted at this size.
                if abs(delta)>24:break
                moves.append((index,delta))
        else:
            if not moves:continue
            assembly += ["MPPEM[ ]","PUSHB[ ]",str(ppem),"EQ[ ]","IF[ ]"]
            for index,delta in moves:
                assembly += ["PUSHW[ ]",str(index),str(delta),"SHPIX[ ]"]
            assembly += ["IUP[0]","EIF[ ]"]
            covered.append(ppem)
    if not covered:return None,[]
    program=Program();program.fromAssembly(assembly)
    return program,covered


def main():
    manifest=json.loads((OUT/"manifest.json").read_text())
    policies=json.loads((ROOT/"sources/b3-hint-profiles.json").read_text())
    for record in manifest["fonts"]:
        style=record["style"];source=OUT/record["unhinted_ttf"]
        path=OUT/f"MMCodingB3-{style}.ttf"
        ttfautohint.ttfautohint(in_file=str(source),out_file=str(path),
            hinting_range_min=8,hinting_range_max=50,hinting_limit=200,
            increase_x_height=0,default_script="latn",fallback_script="none",
            gray_stem_width_mode=StemWidthMode.NATURAL,
            gdi_cleartype_stem_width_mode=StemWidthMode.NATURAL,
            dw_cleartype_stem_width_mode=StemWidthMode.NATURAL,
            no_info=True,TTFA_info=True)
        font=TTFont(path,recalcTimestamp=False);cmap=font.getBestCmap();coverage=defaultdict(int)
        count=0;longest=0
        for cp in range(0xAC00,0xD7A4):
            glyph=font["glyf"][cmap[cp]]
            program,covered=make_hint(glyph,font["glyf"],record["hangul_stems"]["horizontal"],policies[style])
            if program is not None:
                glyph.program=program;count+=1;longest=max(longest,len(program.getBytecode()))
                for ppem in covered:coverage[ppem]+=1
        font["maxp"].maxStackElements=max(font["maxp"].maxStackElements,256)
        font["maxp"].maxSizeOfInstructions=max(font["maxp"].maxSizeOfInstructions,longest)
        font["gasp"]=newTable("gasp");font["gasp"].version=1;font["gasp"].gaspRange={65535:15}
        font.save(path)
        font.flavor="woff2";font.save(OUT/f"MMCodingB3-{style}.woff2")
        record.update({"ttf":path.name,"woff2":f"MMCodingB3-{style}.woff2",
                       "ttf_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                       "hinting":{"latin":"ttfautohint natural modes; x-height increase disabled",
                                  "hangul":"custom y-only SHPIX/IUP by physical PPEM; conservative horizontal-stem detection",
                                  "profile":policies[style],"hinted_hangul_glyphs":count,
                                  "coverage_by_ppem":dict(sorted(coverage.items())),
                                  "windows_directwrite_verified":False}})
        print(style,"Hangul hint coverage",dict(sorted(coverage.items())),flush=True)
    (OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")


if __name__=="__main__":main()
