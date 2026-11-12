"""0.5.0: transplant Fira Code 6.2 operator calt, preserving Sunshine base glyphs.

Use Fira's real contextual rules (including their exclusions), not a greedy list
of replacement strings. Only ASCII operator/punctuation inputs are admitted.
"""
from pathlib import Path
import argparse, copy, hashlib, io, json, math, string, xml.etree.ElementTree as ET
from functools import lru_cache
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.ttLib.reorderGlyphs import reorderGlyphs
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
import freetype
import uharfbuzz as hb
import release_sunshine

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'fonts/fira-ligatures'
SOURCE=ROOT/'sources/upstream/fira-code-6.2-vf.ttf'
VERSION='0.5.0'
SOURCE_SHA='04149681350f161aca538858b88d17443c586cacca83c165939a13423fe91a26'
INPUTS=' '+string.punctuation
SAMPLES='''!= !== == === =!= =:= =/= <= >= && &&& &= ++ +++ *** ;; !! ?? ??? ?: ?. ?= <: :< :> >: <:< <> <<< >>> << >> || -| _|_ |- ||- |= ||= ## ### #### #{ #[ ]# #( #? #_ #_( #: #! #= ^= <$> <$ $> <+> <+ +> <*> <* *> </ </> /> <!-- <#-- --> -> ->> <<- <- <=< =<< <<= <== <=> <==> ==> => =>> >=> >>= >>- >- -< -<< >-> <-< <-| <=| |=> |-> <-> <~~ <~ <~> ~~ ~~> ~> ~- -~ ~@ [||] |] [| |} {| [< >] |> <| ||> <|| |||> <||| <|> ... .. .= ..< .? :: ::: := ::= :? :?> // /// /* */ /= //= /== @_ __ \\ \\\\ ** -- --- +> <+ +++ --> ----> <---- <====> ===== ====> <----> <~~~~>'''.split()
SAMPLES=list(dict.fromkeys(SAMPLES))


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def plus_metrics(font,weight=None):
    gs=font.getGlyphSet(location={'wght':weight} if weight is not None else None)
    p=DecomposingRecordingPen(gs);gs[font.getBestCmap()[ord('+')]].draw(p)
    points=[point for op,args in p.value if op!='closePath' for point in args]
    xs=sorted(set(x for x,y in points));ys=sorted(set(y for x,y in points))
    assert len(xs)==4 and len(ys)==4,(xs,ys)
    return xs[2]-xs[1],ys[2]-ys[1],(ys[2]+ys[1])/2


@lru_cache(maxsize=12)
def shaping_font(path):
    f=hb.Font(hb.Face(Path(path).read_bytes()));f.scale=(1000,1000)
    return f,TTFont(path,lazy=True).getGlyphOrder()


def raw_shape(path,text,on=True):
    f,order=shaping_font(path)
    b=hb.Buffer();b.add_str(text);b.guess_segment_properties()
    hb.shape(f,b,{'calt':on,'liga':on})
    return ([order[g.codepoint] for g in b.glyph_infos],
            [(p.x_advance,p.y_advance,p.x_offset,p.y_offset) for p in b.glyph_positions])


def rename_gsub(donor,names,order):
    buffer=io.BytesIO();donor.saveXML(buffer,tables=['GSUB'])
    root=ET.fromstring(buffer.getvalue())
    for node in root.iter():
        for key,value in list(node.attrib.items()):
            if value in names:node.set(key,names[value])
    carrier=TTFont();carrier.setGlyphOrder(order)
    carrier.importXML(io.BytesIO(ET.tostring(root,encoding='utf-8')))
    reorderGlyphs(carrier,order)
    return carrier['GSUB'].table


def offset_nested_lookups(value,offset):
    if isinstance(value,list):
        for item in value:offset_nested_lookups(item,offset)
    elif hasattr(value,'__dict__'):
        for key,item in vars(value).items():
            if key=='LookupListIndex' and isinstance(item,int):setattr(value,key,item+offset)
            else:offset_nested_lookups(item,offset)


def build():
    assert sha(SOURCE)==SOURCE_SHA
    OUT.mkdir(parents=True,exist_ok=True)
    vf=TTFont(SOURCE)
    options=subset.Options();options.layout_features=['calt'];options.glyph_names=True
    options.drop_tables+=['GPOS','DSIG'];options.notdef_outline=False
    sub=subset.Subsetter(options=options);sub.populate(unicodes=[ord(c) for c in INPUTS]);sub.subset(vf)
    manifest={'version':VERSION,'source':'Fira Code 6.2','source_sha256':SOURCE_SHA,
              'input_scope':'ASCII operators and punctuation; no letter or digit substitutions','fonts':[]}
    for style in ('Regular','Bold'):
        base=ROOT/f'fonts/releases/0.4.2/SunshineMono-{style}.ttf'
        font=TTFont(base,recalcTimestamp=False);target_v,target_h,target_y=plus_metrics(font)
        sx=550/vf['hmtx'][vf.getBestCmap()[ord('+')]][0]
        weight=min(range(300,701),key=lambda w:abs(plus_metrics(vf,w)[0]*sx-target_v))
        donor=instantiateVariableFont(vf,{'wght':weight},inplace=False)
        source_v,source_h,source_y=plus_metrics(donor)
        sy=target_h/source_h;dy=target_y-source_y*sy
        # Retain the fitted donor for reproducible shaping comparison.
        donor_path=OUT/f'FiraCode-OperatorReference-{style}.ttf';donor.save(donor_path)
        cmap=font.getBestCmap();dcmap=donor.getBestCmap()
        names={name:'fc_'+name for name in donor.getGlyphOrder()}
        for cp,name in dcmap.items():
            if cp in cmap:names[name]=cmap[cp]
        old_order=font.getGlyphOrder();order=list(old_order);gs=donor.getGlyphSet();imported=[]
        for name in donor.getGlyphOrder():
            target=names[name]
            if target in old_order:continue
            p=TTGlyphPen(None);recording=DecomposingRecordingPen(gs);gs[name].draw(recording)
            recording.replay(TransformPen(p,(sx,0,0,sy,0,dy)))
            g=p.glyph();g.recalcBounds(None)
            font['glyf'][target]=g
            advance=round(donor['hmtx'][name][0]*sx)
            font['hmtx'][target]=(advance,getattr(g,'xMin',0));order.append(target);imported.append(target)
        font.setGlyphOrder(order)
        imported_table=rename_gsub(donor,names,order)
        table=font['GSUB'].table;offset=len(table.LookupList.Lookup)
        for lookup in imported_table.LookupList.Lookup:
            assert lookup.LookupFlag==0
            offset_nested_lookups(lookup,offset)
        table.LookupList.Lookup.extend(imported_table.LookupList.Lookup)
        table.LookupList.LookupCount=len(table.LookupList.Lookup)
        donor_calt=next(r.Feature for r in imported_table.FeatureList.FeatureRecord if r.FeatureTag=='calt')
        target_features=[r.Feature for r in table.FeatureList.FeatureRecord if r.FeatureTag=='calt']
        assert target_features
        for feature in target_features:
            feature.LookupListIndex=[i+offset for i in donor_calt.LookupListIndex]
            feature.LookupCount=len(feature.LookupListIndex)
        if 'GDEF' in font and font['GDEF'].table.GlyphClassDef:
            defs=font['GDEF'].table.GlyphClassDef.classDefs
            source_defs=donor['GDEF'].table.GlyphClassDef.classDefs if 'GDEF' in donor and donor['GDEF'].table.GlyphClassDef else {}
            for name in donor.getGlyphOrder():
                if names[name] in imported:defs[names[name]]=source_defs.get(name,1)
        license_text=(ROOT/'sources/licenses/fira-OFL.txt').read_text()
        for nid,suffix in [(0,license_text.split('\n\n')[0]),(13,license_text)]:
            value=(font['name'].getDebugName(nid) or '')+'\n'+suffix
            for platform,encoding,language in [(3,1,0x409),(1,0,0)]:font['name'].setName(value,nid,platform,encoding,language)
        path=OUT/f'MMCodingB3-{style}.ttf';font.save(path)
        manifest['fonts'].append({'style':style,'base_sha256':sha(base),'path':path.name,
            'donor_reference':donor_path.name,'variable_weight':weight,'x_scale':sx,'y_scale':sy,'y_shift':dy,
            'target_plus_stems':[target_v,target_h],'fitted_plus_stems':[source_v*sx,source_h*sy],
            'symbol_center':target_y,'imported_glyphs':imported,'glyph_mapping':names})
        print(style,'Fira weight',weight,'fit',sx,sy,'shift',dy,'imported',len(imported),flush=True)
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')


def verify():
    manifest=json.loads((OUT/'manifest.json').read_text());report=[]
    for rec in manifest['fonts']:
        style=rec['style'];path=OUT/rec['path'];base=ROOT/f'fonts/releases/0.4.2/SunshineMono-{style}.ttf'
        old=TTFont(base);new=TTFont(path);names=rec['glyph_mapping'];reference=OUT/rec['donor_reference']
        assert old.getBestCmap()==new.getBestCmap()
        for name in old.getGlyphOrder():
            assert old['glyf'][name].compile(old['glyf'])==new['glyf'][name].compile(new['glyf']),name
            assert old['hmtx'][name]==new['hmtx'][name],name
        for tag in ('GPOS','cvt ','fpgm','prep','gasp'):
            if tag in old:assert old.getTableData(tag)==new.getTableData(tag),tag
        checks=[]
        # Compare actual glyph sequences to Fira, both bare and in punctuation contexts.
        for sample in SAMPLES:
            off,_=raw_shape(reference,sample,False);on,_=raw_shape(reference,sample,True)
            active=off!=on
            for text in (sample,' '+sample+' ','('+sample+')'):
                dn,dp=raw_shape(reference,text,True);an,ap=raw_shape(path,text,True)
                assert an==[names[n] for n in dn],(style,text,an,dn)
                assert sum(p[0] for p in ap)==len(text)*550,(style,text,ap)
                assert all(p[1:]==(0,0,0) for p in ap),(style,text,ap)
            checks.append({'text':sample,'active':active})
        for text in ('function filter true false job J 0O1Il 0123456789','한글 받침 간 갅 갆 갇 갈 갉 갊 감 갑 값','function f(입력값) { return 입력값; }'):
            assert raw_shape(base,text,False)==raw_shape(path,text,False),text
        full_cmap=TTFont(SOURCE).getBestCmap();full_names=names.copy()
        full_names.update({n:new.getBestCmap()[cp] for cp,n in full_cmap.items() if cp in new.getBestCmap()})
        for sample in SAMPLES:
            for text in ('a'+sample+'b','x '+sample+' y'):
                dn,_=raw_shape(SOURCE,text,True);an,_=raw_shape(path,text,True)
                assert an==[full_names.get(n,'UNSUPPORTED:'+n) for n in dn],(style,text)
        # Exercise arbitrary runs, not only the supported showcase strings.
        import random
        rng=random.Random(5042)
        for _ in range(300):
            text=''.join(rng.choice(INPUTS) for _ in range(rng.randint(1,18)))
            dn,_=raw_shape(reference,text,True);an,ap=raw_shape(path,text,True)
            assert an==[names[n] for n in dn],(style,text,an,dn)
            assert sum(p[0] for p in ap)==len(text)*550,(style,text)
        face=freetype.Face(str(path));renders=0
        for size in (12,13,14,16,24,26,28,32):
            face.set_pixel_sizes(0,size)
            for name in rec['imported_glyphs']:
                face.load_glyph(new.getGlyphID(name),freetype.FT_LOAD_RENDER|freetype.FT_LOAD_PEDANTIC);renders+=1
        result={'style':style,'all_original_glyphs_and_hints_byte_identical':True,
                'original_cmap_metrics_and_gpos_preserved':True,'samples':checks,
                'active_samples':sum(c['active'] for c in checks),'sample_count':len(checks),
                'random_operator_runs':300,'donor_shaping_matched':True,'fixed_cell_width_preserved':True,
                'full_donor_letter_contexts':2*len(SAMPLES),
                'imported_glyph_renders':renders,'fit':{k:rec[k] for k in ('variable_weight','x_scale','y_scale','y_shift','target_plus_stems','fitted_plus_stems')}}
        report.append(result);print(style,'shaping samples and original glyph preservation passed',flush=True)
    (ROOT/'docs/fira-ligatures-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser();p.add_argument('--build-only',action='store_true');p.add_argument('--from-built',action='store_true');a=p.parse_args()
    if not a.from_built:build()
    verify()
    if a.build_only:return
    release_sunshine.VERSION=VERSION;release_sunshine.OUT=ROOT/'fonts/releases'/VERSION
    release_sunshine.main(source_dir=OUT,report_path=ROOT/'docs/fira-ligatures-release-verification.json',
        readme_path=ROOT/'docs/fira-ligatures.md',extra_licenses=('fira-OFL.txt',),
        source_description='Iosevka, Source Han Sans, and Fira Code',
        extra_credit='; Fira Code ligatures by The Fira Code Project Authors')

if __name__=='__main__':main()
