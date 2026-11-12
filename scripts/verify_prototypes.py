"""Verify actual font binaries and shaping, including the Latin regression boundary."""
from pathlib import Path
import json
import statistics
import unicodedata
import argparse

from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
import uharfbuzz as hb

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--refine-b", action="store_true")
args = parser.parse_args()
OUT = ROOT / ("fonts/refinement" if args.refine_b else "fonts/prototypes")
manifest = json.loads((OUT / "manifest.json").read_text())


def shape(path, text, ligatures=False):
    font = hb.Font(hb.Face(path.read_bytes()))
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(font, buffer, {"calt": ligatures, "liga": ligatures})
    return [(i.codepoint, p.x_advance, p.y_advance, p.x_offset, p.y_offset)
            for i, p in zip(buffer.glyph_infos, buffer.glyph_positions)]


report = []
for item in manifest["fonts"]:
    path = OUT / item["ttf"]
    font = TTFont(path)
    original_path = ROOT / "sources/upstream" / item["input_file"]
    original = TTFont(original_path)
    cmap, original_cmap = font.getBestCmap(), original.getBestCmap()
    gs, original_gs = font.getGlyphSet(), original.getGlyphSet()
    glyph_order = font.getGlyphOrder()
    assert len(glyph_order) == len(set(glyph_order)), "duplicate glyph names"
    assert all(cp in cmap for cp in range(0xAC00, 0xD7A4)), "missing Hangul"
    assert {font["hmtx"].metrics[cmap[cp]][0] for cp in range(32, 127)} == {item["cell_units"]}
    assert {font["hmtx"].metrics[cmap[cp]][0] for cp in range(0xAC00, 0xD7A4)} == {2 * item["cell_units"]}
    for cp in range(32, 127):
        before, after = RecordingPen(), RecordingPen()
        original_gs[original_cmap[cp]].draw(before)
        gs[cmap[cp]].draw(after)
        assert before.value == after.value, f"Latin outline changed: {cp}"
        assert original["hmtx"].metrics[original_cmap[cp]] == font["hmtx"].metrics[cmap[cp]]
    ratios = []
    for cp in range(0xAC00, 0xD7A4):
        pen = BoundsPen(gs)
        gs[cmap[cp]].draw(pen)
        x0, y0, x1, y1 = pen.bounds
        ratios.append((x1-x0)/(y1-y0))
        assert 0 <= x0 < x1 <= 2 * item["cell_units"], f"cell overflow: {cp}"
        assert y0 >= -font["OS/2"].usWinDescent and y1 <= font["OS/2"].usWinAscent
    median = statistics.median(ratios)
    assert abs(median - .85) < .003, median
    latin = "const a = b !== 0 && c <= 10; // -> => === != 0O1Il rn m"
    for enabled in (False, True):
        assert shape(path, latin, enabled) == shape(original_path, latin, enabled), "Latin shaping regression"
    korean = "한글 읽기 값 꿇 뚫 뷁 힣"
    nfc = shape(path, korean)
    nfd = shape(path, unicodedata.normalize("NFD", korean))
    assert all(g[0] != 0 for g in nfc + nfd), "notdef in Hangul"
    assert nfc == nfd, "NFC/NFD shaping mismatch"
    assert sum(g[1] for g in shape(path, "한글")) == 4 * item["cell_units"]
    webfont = TTFont(OUT / item["woff2"])
    assert webfont.getBestCmap() == cmap, "webfont cmap mismatch"
    if item["id"] in ("B", "B2"):
        assert item["cell_em"] == .55
    if item["id"] == "B2":
        baseline = TTFont(ROOT / "fonts/prototypes/MMCodingB-Regular.ttf")
        baseline_gs = baseline.getGlyphSet()
        baseline_cmap = baseline.getBestCmap()
        changed_ascii = []
        for cp in range(32, 127):
            before, after = RecordingPen(), RecordingPen()
            baseline_gs[baseline_cmap[cp]].draw(before)
            gs[cmap[cp]].draw(after)
            if before.value != after.value:
                changed_ascii.append(chr(cp))
        assert set(changed_ascii) == {"0", "1", "l"}, changed_ascii
        for cp in range(0xAC00, 0xD7A4):
            before, after = RecordingPen(), RecordingPen()
            baseline_gs[baseline_cmap[cp]].draw(before)
            gs[cmap[cp]].draw(after)
            assert before.value == after.value, f"Hangul changed from B: {cp}"
        print("B → B2: ASCII changes", changed_ascii, "; I and all Hangul unchanged", flush=True)
    report.append({"id": item["id"], "label": item["label"], "hangul_count": 11172,
                   "hangul_median_aspect": median, "cell_ratio": "1:2",
                   "ascii_outlines_metrics_unchanged": True,
                   "latin_shaping_ligatures_on_off_unchanged": True,
                   "nfc_nfd_hangul_shaping_equal": True, "woff2_cmap_equal": True})
    print("PASS", item["label"], f"Hangul median {median:.6f}", flush=True)
if args.refine_b:
    report[-1]["changed_ascii_from_B"] = changed_ascii
    report[-1]["hangul_outlines_unchanged_from_B"] = True
(ROOT / "docs" / ("b2-verification.json" if args.refine_b else "prototype-verification.json")).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
