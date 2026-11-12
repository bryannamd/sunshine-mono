"""0.5.1: open crowded Hangul by local component translations, not thinner strokes.

Work from the same Source Han instance to separate originally overlapping vowel
and final strokes. Reapply existing outline cuts (including approved fillets).
Only conservative, classifiable groups are moved; vowel components stay put.
"""
from pathlib import Path
from array import array
import argparse,copy,json,statistics
import pathops
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.ttLib.tables.ttProgram import Program
from fontTools.ttLib.removeOverlaps import ttfGlyphFromSkPath
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from hint_rounded import make_hint
from build_rounded import digest
import release_sunshine
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'fonts/small-size'
VERSION='0.5.1'
DOUBLE_LEADS={1,4,8,10,13}
HORIZONTAL_VOWELS={8,12,13,17,18}
COMPLEX_FINALS={2,3,5,6,9,10,11,12,13,14,15,18,20}
SAFE_SINGLE_FINALS={1,4,7,8,16,17,21}


def path_of(glyph,glyf=None):
    p=pathops.Path();glyph.draw(p.getPen(),glyf);return p


def joined(parts,indices):
    p=pathops.Path()
    for i in indices:p.addPath(parts[i])
    if indices:p.simplify(fix_winding=True,keep_starting_points=True,clockwise=True)
    return p


def translated(p,dx,dy):return p.transform(1,0,0,1,dx,dy)


def raw_parts(source,sx):
    p=TTGlyphPen(None);source.draw(TransformPen(p,(sx,0,0,1,(1100-source.width*sx)/2,0)))
    g=p.glyph();coords,ends,flags=g.getCoordinates(None);parts=[];start=0
    for end in ends:
        part=Glyph();part.numberOfContours=1
        part.coordinates=GlyphCoordinates(coords[start:end+1]);part.flags=array('B',flags[start:end+1])
        part.endPtsOfContours=[end-start];parts.append(path_of(part));start=end+1
    return parts


def modify(parts,old,lead,vowel,final,style):
    boxes=[p.bounds for p in parts];all_indices=set(range(len(parts)))
    raw=joined(parts,all_indices)
    cuts=pathops.op(raw,old,pathops.PathOp.DIFFERENCE)
    groups=[];final_indices=set();initial_indices=set();note={}
    # Finals' bottom-reaching strokes identify the block. The 60-unit allowance
    # includes detached accents in compound ㄶ/ㅀ, but not full-height vowels.
    final_target=final in COMPLEX_FINALS or (lead in DOUBLE_LEADS and final in SAFE_SINGLE_FINALS)
    if final_target:
        seeds=[i for i,b in enumerate(boxes) if b[1]<0]
        if seeds:
            ceiling=max(boxes[i][3] for i in seeds)
            if ceiling<360:
                final_indices={i for i,b in enumerate(boxes) if b[3]<=ceiling+60 and b[1]<ceiling}
                # Reject an implausibly high final block rather than move a vowel.
                if max(boxes[i][3] for i in final_indices)>400:final_indices=set()
    if final_indices:
        block=joined(parts,final_indices);body=joined(parts,all_indices-final_indices)
        bounds=block.bounds;mid=(bounds[0]+bounds[2])/2
        spread=(6 if style=='Regular' else 8) if final in COMPLEX_FINALS else 0
        left={i for i in final_indices if (boxes[i][0]+boxes[i][2])/2<mid} if spread else set(final_indices)
        right=final_indices-left
        # An inner counter is never an independently movable consonant. Keep
        # nested contours with their enclosing contour, even around the midpoint.
        for i in sorted(final_indices,key=lambda i:(boxes[i][2]-boxes[i][0])*(boxes[i][3]-boxes[i][1]),reverse=True):
            for j in final_indices-{i}:
                a,b=boxes[i],boxes[j]
                if a[0]<=b[0] and a[1]<=b[1] and a[2]>=b[2] and a[3]>=b[3] and a!=b:
                    if i in left:left.add(j);right.discard(j)
                    else:right.add(j);left.discard(j)
        # A compound must have a real left and right group, including their holes.
        if spread and (not left or not right):return None
        finals=[]
        for indices,dx in ((left,-spread),(right,spread)):
            if not indices:continue
            p=pathops.op(joined(parts,indices),cuts,pathops.PathOp.DIFFERENCE)
            finals.append((indices,dx,p))
        before_overlap=abs(pathops.op(block,body,pathops.PathOp.INTERSECTION).area)
        dy=None
        for amount in range(18,49,2):
            candidate=pathops.Path()
            for _,dx,p in finals:candidate.addPath(translated(p,dx,-amount+10))
            if abs(pathops.op(candidate,body,pathops.PathOp.INTERSECTION).area)<.5:
                dy=amount;break
        if dy is None:return None
        for indices,dx,p in finals:groups.append((indices,dx,-dy,p))
        note.update({'final_down':dy,'final_spread_each':spread,'original_body_final_overlap_area':round(before_overlap,3)})
    # Horizontal-vowel syllables provide an unambiguous top block. Other initial
    # layouts are preserved rather than guessing which vertical stroke is a vowel.
    if lead in DOUBLE_LEADS and vowel in HORIZONTAL_VOWELS and final:
        seeds={i for i,b in enumerate(boxes) if b[1]>400 and b[3]>680 and i not in final_indices}
        if seeds:
            initial_indices=set(seeds)
            for i,b in enumerate(boxes):
                if i in final_indices:continue
                if any(boxes[j][0]<=b[0] and boxes[j][1]<=b[1] and boxes[j][2]>=b[2] and boxes[j][3]>=b[3] for j in seeds):initial_indices.add(i)
            block=joined(parts,initial_indices);b=block.bounds;mid=(b[0]+b[2])/2
            left={i for i in initial_indices if (boxes[i][0]+boxes[i][2])/2<mid};right=initial_indices-left
            for i in initial_indices:
                for j in initial_indices-{i}:
                    a,b=boxes[i],boxes[j]
                    if a[0]<=b[0] and a[1]<=b[1] and a[2]>=b[2] and a[3]>=b[3] and a!=b:
                        if i in left:left.add(j);right.discard(j)
                        else:right.add(j);left.discard(j)
            if left and right:
                spread=4 if style=='Regular' else 6
                for indices,dx in ((left,-spread),(right,spread)):
                    groups.append((indices,dx,0,pathops.op(joined(parts,indices),cuts,pathops.PathOp.DIFFERENCE)))
                note['initial_spread_each']=spread
            else:initial_indices=set()
    if not groups:return None
    stationary=all_indices-final_indices-initial_indices
    body=pathops.op(joined(parts,stationary),cuts,pathops.PathOp.DIFFERENCE)
    result=pathops.Path();result.addPath(body)
    movement=[]
    for indices,dx,dy,p in groups:
        q=translated(p,dx,dy);result.addPath(q)
        movement.append({'contours':sorted(indices),'dx':dx,'dy':dy,'old_bounds':list(p.bounds),'new_bounds':list(q.bounds)})
    result.simplify(fix_winding=True,keep_starting_points=True,clockwise=True)
    glyph=ttfGlyphFromSkPath(result)
    if not (0<=glyph.xMin<glyph.xMax<=1100 and -150<=glyph.yMin<glyph.yMax<=1200):return None
    # Moving components may remove tiny overlaps, but must never fill counters
    # or lose whole strokes. Retain the original if the ink area changes >3%.
    area_change=abs(path_of(glyph).area)/abs(old.area)-1
    if abs(area_change)>.03:return None
    old_counters=sum(c.clockwise for c in pathops.simplify(old).contours)
    new_counters=sum(c.clockwise for c in pathops.simplify(path_of(glyph)).contours)
    if old_counters!=new_counters:return None
    # Component transformations are translations only: neither stroke thickness,
    # vowel geometry, nor the shape/radius of each moved fillet is scaled.
    note['movements']=movement;note['ink_area_change']=area_change
    return glyph,note


def build():
    OUT.mkdir(parents=True,exist_ok=True)
    variable=TTFont(ROOT/'sources/upstream/source-han-kr-vf.ttf');vcmap=variable.getBestCmap()
    specs=json.loads((ROOT/'fonts/final-radius/manifest.json').read_text())['fonts'];report=[]
    for spec in specs:
        style=spec['style'];base=ROOT/f'fonts/releases/0.5.0/SunshineMono-{style}.ttf'
        font=TTFont(base,recalcTimestamp=False);old=TTFont(base);cmap=font.getBestCmap()
        gs=variable.getGlyphSet(location={'wght':spec['hangul_variable_weight']})
        changed={};skipped=[];geometry_errors=[];longest=0
        for cp in range(0xAC00,0xD7A4):
            index=cp-0xAC00;lead=index//588;vowel=index//28%21;final=index%28
            if not final or not (final in COMPLEX_FINALS or lead in DOUBLE_LEADS):continue
            parts=raw_parts(gs[vcmap[cp]],spec['horizontal_scale'])
            name=cmap[cp];original=path_of(old['glyf'][name],old['glyf'])
            try:
                result=modify(parts,original,lead,vowel,final,style)
            except pathops.PathOpsError:
                # Keep the already verified glyph when a degenerate intersection
                # cannot be resolved reliably; never emit a damaged replacement.
                geometry_errors.append(chr(cp));result=None
            if result is None:skipped.append(chr(cp));continue
            glyph,note=result;font['glyf'][name]=glyph
            # New point order needs new local Hangul instructions, while Latin and
            # Fira's added glyphs and the global interpreter tables stay untouched.
            program,covered=make_hint(glyph,font['glyf'],spec['hangul_stems']['horizontal'],spec['hinting']['profile'])
            glyph.program=program or Program()
            if program:longest=max(longest,len(program.getBytecode()))
            font['hmtx'][name]=(1100,glyph.xMin)
            note['hinted_sizes']=covered;changed[f'U+{cp:04X}']=note
        font['maxp'].maxStackElements=max(font['maxp'].maxStackElements,256)
        font['maxp'].maxSizeOfInstructions=max(font['maxp'].maxSizeOfInstructions,longest)
        path=OUT/f'MMCodingB3-{style}.ttf';font.save(path)
        final_font=TTFont(path);changed_names={cmap[int(k[2:],16)] for k in changed}
        for name in old.getGlyphOrder():
            if name not in changed_names:
                assert old['glyf'][name].compile(old['glyf'])==final_font['glyf'][name].compile(final_font['glyf']),name
            assert old['hmtx'][name][0]==final_font['hmtx'][name][0]
        for tag in ('GSUB','GPOS','GDEF','cvt ','prep','fpgm'):
            if tag in old:assert old.getTableData(tag)==final_font.getTableData(tag),tag
        r={'style':style,'changed_glyphs':len(changed),'changed_finals':sum('final_down' in n for n in changed.values()),
           'spread_initials':sum('initial_spread_each' in n for n in changed.values()),
           'separated_overlapping_final_blocks':sum(n.get('original_body_final_overlap_area',0)>.5 for n in changed.values()),
           'final_down_median':statistics.median(n['final_down'] for n in changed.values() if 'final_down' in n),
           'unchanged_other_glyphs':True,'advances_and_layout_preserved':True,'translations_only':True,
           'counter_counts_preserved':True,'max_ink_area_change':max(abs(n['ink_area_change']) for n in changed.values()),
           'skipped':skipped,'geometry_errors':geometry_errors,'glyph_changes':changed,'base_sha256':digest(base),'sha256':digest(path)}
        report.append(r);print(style,{k:v for k,v in r.items() if k not in ('glyph_changes','skipped')},flush=True)
    (OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'docs/small-size-verification.json').write_text(json.dumps([{k:v for k,v in r.items() if k!='glyph_changes'} for r in report],ensure_ascii=False,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser();p.add_argument('--build-only',action='store_true');p.add_argument('--from-built',action='store_true');a=p.parse_args()
    if not a.from_built:build()
    if a.build_only:return
    release_sunshine.VERSION=VERSION;release_sunshine.OUT=ROOT/'fonts/releases'/VERSION
    release_sunshine.main(source_dir=OUT,report_path=ROOT/'docs/small-size-release-verification.json',readme_path=ROOT/'docs/small-size-study.md',extra_licenses=('fira-OFL.txt',),source_description='Iosevka, Source Han Sans, and Fira Code',extra_credit='; Fira Code ligatures by The Fira Code Project Authors')

if __name__=='__main__':main()
