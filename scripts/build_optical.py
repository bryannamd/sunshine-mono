"""Build the local 0.4.0 optical study; retain the 0.3.0 release unchanged."""
from pathlib import Path
import argparse
import json
import statistics
import unicodedata
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
import build_rounded
import hint_rounded
import release_sunshine
from verify_rounded import shape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'fonts/optical'
VERSION = '0.4.0'


def outline(font, cp):
    pen = DecomposingRecordingPen(font.getGlyphSet())
    font.getGlyphSet()[font.getBestCmap()[cp]].draw(pen)
    return pen.value


def verify():
    manifest = json.loads((OUT / 'manifest.json').read_text())
    baseline = json.loads((ROOT / 'fonts/rounded/manifest.json').read_text())
    results = []
    for record, previous in zip(manifest['fonts'], baseline['fonts']):
        style = record['style']
        old = TTFont(ROOT / f'fonts/releases/0.3.0/SunshineMono-{style}.ttf')
        path = ROOT / f'fonts/releases/{VERSION}/SunshineMono-{style}.ttf'
        new = TTFont(path)
        raw = TTFont(OUT / record['unhinted_ttf'])
        old_cmap, cmap = old.getBestCmap(), new.getBestCmap()
        widths, old_widths, gaps, old_gaps = [], [], [], []
        for cp in range(0xAC00, 0xD7A4):
            glyph = new['glyf'][cmap[cp]]
            old_glyph = old['glyf'][old_cmap[cp]]
            assert new['hmtx'][cmap[cp]][0] == 1100
            assert 0 <= glyph.xMin < glyph.xMax <= 1100, (style, hex(cp))
            assert -300 <= glyph.yMin < glyph.yMax <= 1200
            assert outline(new, cp) == outline(raw, cp)
            widths.append(glyph.xMax-glyph.xMin)
            old_widths.append(old_glyph.xMax-old_glyph.xMin)
            gaps.append(1100-widths[-1])
            old_gaps.append(1100-old_widths[-1])
        for cp in range(32, 127):
            assert new['hmtx'][cmap[cp]] == old['hmtx'][old_cmap[cp]]
            assert outline(new, cp) == outline(old, cp)
        for tag in ('GSUB', 'GPOS', 'GDEF'):
            assert new.getTableData(tag) == old.getTableData(tag), tag
        for text in ('한글 입력값 없습니다', '괜찮은 폰트 값 읽기 뚫 꽉', '가각갂간갅갆갇갈'):
            assert shape(path, text) == shape(path, unicodedata.normalize('NFD', text))
        changes = {axis: record['hangul_stems'][axis]/previous['hangul_stems'][axis]-1
                   for axis in ('vertical', 'horizontal')}
        assert all(-.11 < value < -.03 for value in changes.values()), changes
        result = {'style': style, 'stem_change_fraction': changes,
                  'median_outline_width_before': statistics.median(old_widths),
                  'median_outline_width_after': statistics.median(widths),
                  'median_sidebearings_sum_before': statistics.median(old_gaps),
                  'median_sidebearings_sum_after': statistics.median(gaps),
                  'all_11172_hangul_inside_cells': True,
                  'ascii_outlines_and_metrics_unchanged': True,
                  'layout_tables_unchanged': True, 'nfc_nfd_equivalent': True,
                  'hinted_outlines_unchanged': True}
        assert result['median_sidebearings_sum_after'] < result['median_sidebearings_sum_before']
        results.append(result)
        print(json.dumps(result, ensure_ascii=False), flush=True)
    (ROOT / 'docs/optical-verification.json').write_text(json.dumps(results, indent=2)+'\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    if not args.verify_only:
        build_rounded.main(out=OUT, ratio=.884, stem_scale=.925)
        manifest = json.loads((OUT / 'manifest.json').read_text())
        previous = json.loads((ROOT / 'fonts/rounded/manifest.json').read_text())
        manifest['version'] = VERSION
        manifest['optical_design'] = {'outline_ratio': .884, 'stem_target_vs_latin': .925,
                                      'advance_unchanged': True, 'rounding_unchanged': True}
        (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
        profiles = json.loads((ROOT / 'sources/b3-hint-profiles.json').read_text())
        # Follow the measured horizontal-stem reduction instead of restoring old weight in hints.
        for current, old in zip(manifest['fonts'], previous['fonts']):
            style = current['style']
            scale = current['hangul_stems']['horizontal']/old['hangul_stems']['horizontal']
            profiles[style] = {size: round(width*scale, 5) for size, width in profiles[style].items()}
        hint_rounded.main(out=OUT, policies=profiles)
        release_sunshine.VERSION = VERSION
        release_sunshine.OUT = ROOT / 'fonts/releases' / VERSION
        release_sunshine.main(source_dir=OUT,
                              report_path=ROOT / 'docs/optical-release-verification.json',
                              readme_path=ROOT / 'docs/optical-study.md')
    verify()


if __name__ == '__main__':
    main()
