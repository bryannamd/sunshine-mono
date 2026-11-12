"""0.4.2: flat Latin terminals and compact corner arcs; keep 0.4.1 Hangul exact."""
from pathlib import Path
import argparse, copy, json, math, shutil
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen, RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
import ttfautohint
from ttfautohint import StemWidthMode
import release_sunshine
from build_rounded import digest
from verify_rounded import outline
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'fonts/latin-balance'
BASE=ROOT/'fonts/final-radius'
VERSION='0.4.2'
VARIANTS={'f':'f.cv41-11','t':'t.cv54-7','r':'r.cv52-9',
          'uni0237':'uni0237.cv45-6','J':'J.cv20-6','l':'l'}


def recording(font,name):
    gs=font.getGlyphSet();p=DecomposingRecordingPen(gs);gs[name].draw(p);return p.value


def compact_arcs(ops,radius):
    """Replace the two tangent quarter-turns of a flat hook; preserve stroke widths."""
    arcs=[];start=None
    for i,(op,args) in enumerate(ops):
        if op=='qCurveTo' and len(args)>=4:
            end=args[-1];first,last=args[0],args[-2]
            if first[0]==start[0] and last[1]==end[1]:v=(start[0],end[1])
            elif first[1]==start[1] and last[0]==end[0]:v=(end[0],start[1])
            else: v=None
            if v and abs(start[0]-end[0])>10 and abs(start[1]-end[1])>10:
                arcs.append((i,start,end,v))
        if args and op in ('moveTo','lineTo','qCurveTo'):start=args[-1]
    assert len(arcs)==2,arcs
    outer=max(arcs,key=lambda a:abs(a[1][0]-a[2][0])*abs(a[1][1]-a[2][1]))
    inner=next(a for a in arcs if a!=outer)
    vx=abs(outer[3][0]-inner[3][0]);hy=abs(outer[3][1]-inner[3][1])
    assert 0<vx<radius and 0<hy<radius,(vx,hy,radius)
    edits={};starts={}
    for arc in arcs:
        i,s,e,v=arc;rx=radius if arc==outer else radius-vx;ry=radius if arc==outer else radius-hy
        def endpoint(p):
            return (v[0]+(math.copysign(rx,p[0]-v[0]) if p[0]!=v[0] else 0),
                    v[1]+(math.copysign(ry,p[1]-v[1]) if p[1]!=v[1] else 0))
        ns,ne=endpoint(s),endpoint(e);k=1-math.tan(math.pi/8);m=1-math.sqrt(.5)
        c1=tuple(v[j]+k*(ns[j]-v[j]) for j in (0,1))
        mid=tuple(v[j]+m*(ns[j]+ne[j]-2*v[j]) for j in (0,1))
        c2=tuple(v[j]+k*(ne[j]-v[j]) for j in (0,1))
        assert ops[i-1][0] in ('moveTo','lineTo')
        starts[i-1]=(ops[i-1][0],(ns,))
        edits[i]=[('qCurveTo',(c1,mid)),('qCurveTo',(c2,ne))]
    result=[]
    for i,item in enumerate(ops):result.extend(edits.get(i,[starts.get(i,item)]))
    return result,{'outer_radius':radius,'vertical_stem':vx,'horizontal_stem':hy}


def build_geometry():
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=copy.deepcopy(json.loads((BASE/'manifest.json').read_text()))
    manifest['version']=VERSION
    manifest['latin_balance']={'variants':VARIANTS,'radii':{'Regular':100,'Bold':132},'hangul_base':'0.4.1'}
    for rec in manifest['fonts']:
        style=rec['style'];font=TTFont(BASE/rec['unhinted_ttf'],recalcTimestamp=False)
        radius=100 if style=='Regular' else 132
        original={base:recording(font,base) for base in VARIANTS}
        replacements={};design={}
        for base,variant in VARIANTS.items():
            ops=recording(font,variant)
            if base!='r':ops,design[base]=compact_arcs(ops,radius)
            p=TTGlyphPen(None);r=RecordingPen();r.value=ops;r.replay(p)
            replacements[base]=p.glyph()
        # Keep identical base aliases consistent. Composite accented glyphs then
        # inherit these changes without changing their accents or positioning.
        aliases={base:[] for base in VARIANTS}
        for name in font.getGlyphOrder():
            if name.startswith('mmkr'):continue
            ops=recording(font,name)
            for base,old in original.items():
                if ops==old and font['hmtx'][name][0]==font['hmtx'][base][0]:aliases[base].append(name)
        changed=[]
        for base,names in aliases.items():
            for name in names:
                font['glyf'][name]=copy.deepcopy(replacements[base]);changed.append(name)
                font['glyf'][name].recalcBounds(font['glyf'])
                advance=font['hmtx'][name][0]
                font['hmtx'][name]=(advance,font['glyf'][name].xMin)
        affected=set(changed)
        while True:
            more={name for name in font.getGlyphOrder() if font['glyf'][name].isComposite()
                  and any(c.glyphName in affected for c in font['glyf'][name].components)}-affected
            if not more:break
            affected.update(more)
        for name in affected-set(changed):
            font['glyf'][name].recalcBounds(font['glyf'])
            font['hmtx'][name]=(font['hmtx'][name][0],font['glyf'][name].xMin)
        path=OUT/rec['unhinted_ttf'];font.save(path)
        rec.update({'unhinted_sha256':digest(path),'latin_changed_glyphs':changed,'latin_affected_glyphs':sorted(affected),'latin_aliases':aliases,'latin_corner_design':design})
        print(style,'Latin defaults/aliases changed:',len(changed),design,flush=True)
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    shutil.copytree(BASE/'licenses',OUT/'licenses',dirs_exist_ok=True)


def verify_geometry(manifest):
    report=[]
    for rec in manifest['fonts']:
        old=TTFont(BASE/rec['unhinted_ttf']);new=TTFont(OUT/rec['unhinted_ttf'])
        cmap=new.getBestCmap();changed=set(rec['latin_affected_glyphs'])
        for name in old.getGlyphOrder():
            assert old['hmtx'][name][0]==new['hmtx'][name][0],name
            if name not in changed:
                assert old['glyf'][name].compile(old['glyf'])==new['glyf'][name].compile(new['glyf']),name
        for cp in list(range(0xAC00,0xD7A4))+list(range(0x1100,0x1200))+list(range(0x3130,0x3190)):
            if cp in cmap:assert outline(old,cmap[cp])==outline(new,cmap[cp])
        for ch in 'ftlrjJ':assert outline(old,cmap[ord(ch)])!=outline(new,cmap[ord(ch)]),ch
        for cp in range(32,127):
            if chr(cp) not in 'ftlrjJ':assert outline(old,cmap[cp])==outline(new,cmap[cp]),chr(cp)
        for ch in 'ftlrjJ':
            g=new['glyf'][cmap[ord(ch)]];g.recalcBounds(new['glyf'])
            assert 0<=g.xMin<g.xMax<=550,ch
        for tag in ('GSUB','GPOS','GDEF'):assert old.getTableData(tag)==new.getTableData(tag)
        report.append({'style':rec['style'],'changed_ascii':'ftlrjJ','other_ascii_unchanged':True,
                       'hangul_and_jamo_unchanged':True,'advances_unchanged':True,
                       'layout_tables_unchanged':True,'aliases':rec['latin_aliases'],'corner_design':rec['latin_corner_design']})
    (ROOT/'docs/latin-balance-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('Latin geometry, exact Hangul preservation, widths and layout verified',flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--geometry-only',action='store_true');parser.add_argument('--from-geometry',action='store_true');args=parser.parse_args()
    if not args.from_geometry:build_geometry()
    manifest=json.loads((OUT/'manifest.json').read_text());verify_geometry(manifest)
    if args.geometry_only:return
    for rec in manifest['fonts']:
        style=rec['style'];path=OUT/f'MMCodingB3-{style}.ttf'
        ttfautohint.ttfautohint(in_file=str(OUT/rec['unhinted_ttf']),out_file=str(path),hinting_range_min=8,hinting_range_max=50,hinting_limit=200,increase_x_height=0,default_script='latn',fallback_script='none',gray_stem_width_mode=StemWidthMode.NATURAL,gdi_cleartype_stem_width_mode=StemWidthMode.NATURAL,dw_cleartype_stem_width_mode=StemWidthMode.NATURAL,no_info=True,TTFA_info=True)
        font=TTFont(path,recalcTimestamp=False)
        old=TTFont(ROOT/f'fonts/releases/0.4.1/SunshineMono-{style}.ttf')
        for name in old.getGlyphOrder():
            if name.startswith('mmkr'):
                font['glyf'][name]=copy.deepcopy(old['glyf'][name]);font['hmtx'][name]=old['hmtx'][name]
        for attr in ('maxStackElements','maxSizeOfInstructions'):
            setattr(font['maxp'],attr,max(getattr(font['maxp'],attr),getattr(old['maxp'],attr)))
        font['gasp']=copy.deepcopy(old['gasp']);font.save(path)
        final=TTFont(path)
        for name in old.getGlyphOrder():
            if name.startswith('mmkr'):assert old['glyf'][name].compile(old['glyf'])==final['glyf'][name].compile(final['glyf']),name
        rec['ttf_sha256']=digest(path)
        print(style,'Latin hints rebuilt; Hangul outlines AND instructions preserved',flush=True)
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    release_sunshine.VERSION=VERSION;release_sunshine.OUT=ROOT/'fonts/releases'/VERSION
    release_sunshine.main(source_dir=OUT,report_path=ROOT/'docs/latin-balance-release-verification.json',readme_path=ROOT/'docs/latin-balance.md')

if __name__=='__main__':main()
