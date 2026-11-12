"""0.4.1: a local bottom-left fillet on the left consonant of selected finals.

Apply a bounded geometric cut to 0.4.0, preserving the optical design and every
other corner. Locate the original vertex in the matching Source Han instance,
so previous small fillets and short tangent segments cannot hide the corner.
"""
from pathlib import Path
import argparse
import copy
import json
import math
import shutil
import unicodedata
import pathops
from fontTools.ttLib import TTFont
from fontTools.ttLib.removeOverlaps import ttfGlyphFromSkPath
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from build_rounded import digest
import hint_rounded
import release_sunshine
from verify_rounded import shape, outline

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'fonts/optical'
OUT = ROOT / 'fonts/final-radius'
VERSION = '0.4.1'
# Single ㄴ ㄷ ㄹ ㅁ ㅂ, or those consonants on the LEFT of a compound final.
FINALS = {4:'ㄴ', 5:'ㄵ', 6:'ㄶ', 7:'ㄷ', 8:'ㄹ', 9:'ㄺ', 10:'ㄻ', 11:'ㄼ',
          12:'ㄽ', 13:'ㄾ', 14:'ㄿ', 15:'ㅀ', 16:'ㅁ', 17:'ㅂ', 18:'ㅄ'}
RADII = {'Regular': 88, 'Bold': 112}


def as_path(glyph, glyf):
    path = pathops.Path()
    glyph.draw(path.getPen(), glyf)
    return path


def find_corner(glyph):
    coords, ends, flags = glyph.getCoordinates(None)
    ymin, ymax = min(y for x,y in coords), max(y for x,y in coords)
    candidates = []
    start = 0
    for end in ends:
        points = list(coords[start:end+1]); on = list(flags[start:end+1]); n = len(points)
        for i, (x,y) in enumerate(points):
            if y > ymin+.22*(ymax-ymin) or not all(on[j%n]&1 for j in (i-1,i,i+1)):
                continue
            a,b = points[(i-1)%n],points[(i+1)%n]
            u,v = (a[0]-x,a[1]-y),(b[0]-x,b[1]-y)
            up,right = (u,v) if u[1]>v[1] else (v,u)
            # Exterior convex lower-left joint. Allow slightly inclined source strokes.
            if (-u[0])*v[1]-(-u[1])*v[0] >= 0:
                continue
            if (up[1]>0 and abs(up[0])<.35*up[1]
                    and right[0]>0 and abs(right[1])<.35*right[0]):
                candidates.append((x,y))
        start=end+1
    if not candidates:
        raise ValueError('No lower-left final corner')
    # In ㄻ/ㄼ etc., both consonants have corners. Change only the leftmost one.
    return min(candidates)


def cutter(x, y, radius):
    # Two quadratic segments approximate a circular quarter arc (<0.4% radial error).
    # Subtract the lower-left area outside the rounded corner, like border-radius.
    k = 1-math.tan(math.pi/8)
    m = 1-math.sqrt(.5)
    p = pathops.Path()
    p.moveTo(x,y);p.lineTo(x,y+radius)
    p.quadTo(x,y+k*radius,x+m*radius,y+m*radius)
    p.quadTo(x+k*radius,y,x+radius,y)
    p.close()
    return p


def rectangle(x,y,r,pad=2):
    p=pathops.Path();p.moveTo(x-pad,y-pad);p.lineTo(x+r+pad,y-pad)
    p.lineTo(x+r+pad,y+r+pad);p.lineTo(x-pad,y+r+pad);p.close()
    return p


def build_geometry():
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=copy.deepcopy(json.loads((BASE/'manifest.json').read_text()))
    variable=TTFont(ROOT/'sources/upstream/source-han-kr-vf.ttf')
    source_cmap=variable.getBestCmap()
    manifest['version']=VERSION
    manifest['optical_design']['rounding_unchanged']=False
    manifest['final_radius_design']={'target_finals':FINALS,'radii':RADII,
                                    'base_version':'0.4.0','left_consonant_only':True}
    for record in manifest['fonts']:
        style=record['style']; radius=RADII[style]
        font=TTFont(BASE/record['unhinted_ttf'],recalcTimestamp=False)
        cmap=font.getBestCmap();gs=variable.getGlyphSet(location={'wght':record['hangul_variable_weight']})
        sx=record['horizontal_scale']; changes={}
        for cp in range(0xAC00,0xD7A4):
            final=(cp-0xAC00)%28
            if final not in FINALS:continue
            source=gs[source_cmap[cp]];pen=TTGlyphPen(None)
            source.draw(TransformPen(pen,(sx,0,0,1,(1100-source.width*sx)/2,0)))
            path=as_path(pen.glyph(),None)
            path.simplify(fix_winding=True,keep_starting_points=True,clockwise=True)
            x,y=find_corner(ttfGlyphFromSkPath(path))
            name=cmap[cp];old=as_path(font['glyf'][name],font['glyf'])
            new=pathops.op(old,cutter(x,y,radius),pathops.PathOp.DIFFERENCE)
            glyph=ttfGlyphFromSkPath(new)
            removed=abs(old.area)-abs(new.area)
            assert removed>100,(style,chr(cp),removed)
            font['glyf'][name]=glyph
            changes[f'U+{cp:04X}']={'final':FINALS[final],'corner':[x,y],
                                   'radius':radius,'removed_area':round(removed,3)}
        assert len(changes)==5985
        path=OUT/record['unhinted_ttf'];font.save(path)
        record.update({'unhinted_sha256':digest(path),'final_radius_glyphs':changes,
                       'final_radius_glyph_count':len(changes),'final_radius':radius})
        print(style,'new lower-left fillets:',len(changes),flush=True)
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    shutil.copytree(BASE/'licenses',OUT/'licenses',dirs_exist_ok=True)
    verify_geometry(manifest)


def verify_geometry(manifest):
    report=[]
    for record in manifest['fonts']:
        old=TTFont(BASE/record['unhinted_ttf']);new=TTFont(OUT/record['unhinted_ttf'])
        cmap=new.getBestCmap(); counts={v:0 for v in FINALS.values()}
        assert old['hmtx'].metrics==new['hmtx'].metrics
        changed_names={cmap[int(k[2:],16)] for k in record['final_radius_glyphs']}
        for name in old.getGlyphOrder():
            if name not in changed_names:
                assert old['glyf'][name].compile(old['glyf'])==new['glyf'][name].compile(new['glyf']),name
        for key,change in record['final_radius_glyphs'].items():
            cp=int(key[2:],16);name=cmap[cp]
            a=as_path(old['glyf'][name],old['glyf']);b=as_path(new['glyf'][name],new['glyf'])
            delta=pathops.op(a,b,pathops.PathOp.XOR)
            outside=pathops.op(delta,rectangle(*change['corner'],change['radius']),pathops.PathOp.DIFFERENCE)
            # Boolean intersections create fractional controls. TTF rounds them
            # to integers; permit at most one design unit along the old boundary.
            edge=pathops.Path();edge.addPath(a)
            edge.stroke(2,pathops.LineCap.ROUND_CAP,pathops.LineJoin.ROUND_JOIN,4)
            residual=pathops.op(outside,edge,pathops.PathOp.DIFFERENCE)
            assert abs(residual.area)<1,(record['style'],chr(cp),'changed outside corner',residual.area)
            assert abs(a.area)>abs(b.area)
            g=new['glyf'][name]
            assert 0<=g.xMin<g.xMax<=1100 and -300<=g.yMin<g.yMax<=1200
            counts[change['final']]+=1
        assert all(n==399 for n in counts.values())
        report.append({'style':record['style'],'radius':record['final_radius'],
                       'coverage':counts,'changed_glyphs':5985,
                       'changes_confined_to_left_corner':True,'outline_rounding_tolerance_units':1,
                       'other_glyphs_unchanged':True,
                       'metrics_unchanged':True})
        print(record['style'],'localized outline and all 15 final types verified',flush=True)
    (ROOT/'docs/final-radius-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--geometry-only',action='store_true')
    parser.add_argument('--from-geometry',action='store_true')
    args=parser.parse_args()
    if not args.from_geometry:build_geometry()
    if args.geometry_only:return
    manifest=json.loads((OUT/'manifest.json').read_text())
    if args.from_geometry:verify_geometry(manifest)
    policies={r['style']:r['hinting']['profile'] for r in manifest['fonts']}
    hint_rounded.main(out=OUT,policies=policies)
    release_sunshine.VERSION=VERSION
    release_sunshine.OUT=ROOT/'fonts/releases'/VERSION
    release_sunshine.main(source_dir=OUT,report_path=ROOT/'docs/final-radius-release-verification.json',
                          readme_path=ROOT/'docs/final-radius.md')
    for record in manifest['fonts']:
        path=release_sunshine.OUT/f"SunshineMono-{record['style']}.ttf"
        font=TTFont(path);raw=TTFont(OUT/record['unhinted_ttf']);cmap=font.getBestCmap()
        for cp in range(0xAC00,0xD7A4):
            assert outline(font,cmap[cp])==outline(raw,raw.getBestCmap()[cp])
        for text in ('간 갅 갆 갇 갈 갉 갊 갋 갌 갍 갎 갏 감 갑 값','한글 입력값 없습니다'):
            assert shape(path,text)==shape(path,unicodedata.normalize('NFD',text))
    print('Final hinted outlines and NFC/NFD verified',flush=True)


if __name__=='__main__':main()
