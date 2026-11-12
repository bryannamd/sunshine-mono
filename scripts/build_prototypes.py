"""Build four OFL comparison prototypes; preserve the Latin outlines/layout tables."""
from pathlib import Path
import hashlib
import json
import shutil
import statistics

from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "sources/upstream"
OUT = ROOT / "fonts/prototypes"
FAMILIES = [
    ("A", "JetBrains Mono", "jetbrains.ttf"),
    ("B", "Iosevka Custom 550", "iosevka.ttf"),
    ("C", "Cascadia Mono", "cascadia.ttf"),
    ("D", "Fira Code", "fira.ttf"),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(families=FAMILIES, output=OUT):
    OUT = output
    OUT.mkdir(parents=True, exist_ok=True)
    source = TTFont(UPSTREAM / "source-han.otf")
    source_upm = source["head"].unitsPerEm
    cmap = source.getBestCmap()
    glyphs = source.getGlyphSet()
    syllables = list(range(0xAC00, 0xD7A4))
    codepoints = syllables + [cp for cp in list(range(0x1100, 0x1200))
                             + list(range(0x3130, 0x3190)) if cp in cmap]
    boxes = {}
    for cp in codepoints:
        pen = BoundsPen(glyphs)
        glyphs[cmap[cp]].draw(pen)
        boxes[cp] = pen.bounds
    ratios = [(boxes[cp][2] - boxes[cp][0]) / (boxes[cp][3] - boxes[cp][1])
              for cp in syllables]
    original_ratio = statistics.median(ratios)
    horizontal_scale = 0.85 / original_ratio
    print(f"Hangul: median {original_ratio:.6f}; horizontal scale {horizontal_scale:.6f}", flush=True)
    manifest = {"prototype_version": "0.1.0", "hangul": {
        "source_version": source["name"].getDebugName(5),
        "sha256": sha(UPSTREAM / "source-han.otf"),
        "measurement": "median outline width/height across all 11172 modern Hangul syllables",
        "original_median": original_ratio, "target_median": 0.85,
        "horizontal_scale": horizontal_scale, "vertical_scale": 1,
        "note": "Common transform, not per-glyph stretching; unhinted Hangul prototypes."}, "fonts": []}
    for letter, label, filename in families:
        path = UPSTREAM / filename
        font = TTFont(path, recalcTimestamp=False)
        upm = font["head"].unitsPerEm
        old_cmap = font.getBestCmap()
        widths = {font["hmtx"].metrics[old_cmap[cp]][0] for cp in range(32, 127)}
        assert len(widths) == 1, (label, widths)
        cell = widths.pop()
        # glyf.__setitem__ updates its own order; keep a separate final order.
        order = list(font.getGlyphOrder())
        for cp in codepoints:
            name = f"mmkr{cp:04X}"
            original_advance = source["hmtx"].metrics[cmap[cp]][0]
            advance = 0 if original_advance == 0 else 2 * cell
            sx, sy = horizontal_scale * upm / source_upm, upm / source_upm
            # Center the original design cell, retaining its optical sidebearing differences.
            dx = (advance - original_advance * sx) / 2
            ttpen = TTGlyphPen(None)
            quadpen = Cu2QuPen(ttpen, max_err=upm / 1000, reverse_direction=True)
            glyphs[cmap[cp]].draw(TransformPen(quadpen, (sx, 0, 0, sy, dx, 0)))
            glyph = ttpen.glyph()
            font["glyf"][name] = glyph
            glyph.recalcBounds(font["glyf"])
            font["hmtx"].metrics[name] = (advance, getattr(glyph, "xMin", 0))
            order.append(name)
            for table in font["cmap"].tables:
                if table.isUnicode() and table.format in (4, 12):
                    table.cmap[cp] = name
        font.setGlyphOrder(order)
        # Common line metrics keep comparison line spacing consistent; Latin shapes stay intact.
        font["hhea"].ascent = round(1.2 * upm)
        font["hhea"].descent = -round(0.3 * upm)
        font["hhea"].lineGap = 0
        os2 = font["OS/2"]
        os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = round(1.2 * upm), -round(.3 * upm), 0
        os2.usWinAscent = max(os2.usWinAscent, round(1.2 * upm))
        os2.usWinDescent = max(os2.usWinDescent, round(.3 * upm))
        if os2.version >= 4:
            os2.fsSelection |= 1 << 7
        os2.recalcUnicodeRanges(font)
        os2.recalcCodePageRanges(font)
        os2.usLastCharIndex = min(0xFFFF, max(font.getBestCmap()))
        font["post"].isFixedPitch = 1
        if "DSIG" in font:
            del font["DSIG"]
        family = f"MM Coding {letter}"
        psname = f"MMCoding{letter}-Regular"
        names = font["name"]
        copyright_text = (names.getDebugName(0) or "") + "\n" + (source["name"].getDebugName(0) or "")
        replace_ids = {0, 1, 2, 3, 4, 5, 6, 13, 14, 16, 17, 18, 21, 22, 25}
        names.names = [n for n in names.names if n.nameID not in replace_ids]
        values = {0: copyright_text, 1: family, 2: "Regular", 3: f"0.100;MMCF;{psname}",
                  4: family + " Regular", 5: "Version 0.100; comparison prototype",
                  6: psname, 13: "SIL Open Font License 1.1. See accompanying licenses.",
                  14: "https://openfontlicense.org", 16: family, 17: "Regular"}
        for nid, text in values.items():
            names.setName(text, nid, 3, 1, 0x409)
        ttf = OUT / f"{psname}.ttf"
        font.save(ttf)
        font.flavor = "woff2"
        font.save(OUT / f"{psname}.woff2")
        record = {"id": letter, "label": label, "family": family, "postscript": psname,
                  "upm": upm, "cell_units": cell, "cell_em": cell/upm,
                  "hangul_cell_units": 2*cell, "input_file": filename,
                  "input_sha256": sha(path), "ttf_sha256": sha(ttf),
                  "ttf": ttf.name, "woff2": f"{psname}.woff2"}
        manifest["fonts"].append(record)
        print(f"Built {label}: {cell/upm:.6f}em", flush=True)
    shutil.copytree(ROOT / "sources/licenses", OUT / "licenses", dirs_exist_ok=True)
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--refine-b", action="store_true")
    args = parser.parse_args()
    if args.refine_b:
        main([("B2", "Iosevka 550 · 문자 구분 개선", "iosevka-b2.ttf")], ROOT / "fonts/refinement")
    else:
        main()
