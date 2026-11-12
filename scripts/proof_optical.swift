// Compare file-backed CGFonts: identical family names cannot resolve to the wrong installed version.
import Foundation
import CoreText
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers
let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let versions = ["0.3.0", "0.4.0"]
var fonts: [String: CGFont] = [:]
for version in versions {
 for style in ["Regular", "Bold"] {
  let url = root.appendingPathComponent("fonts/releases/\(version)/SunshineMono-\(style).ttf")
  fonts["\(version)-\(style)"] = CGFont(CGDataProvider(url: url as CFURL)!)!
 }
}
func line(_ text: String, _ font: CTFont, _ dark: Bool) -> CTLine {
 CTLineCreateWithAttributedString(NSAttributedString(string: text, attributes: [
  NSAttributedString.Key(kCTFontAttributeName as String): font,
  NSAttributedString.Key(kCTForegroundColorAttributeName as String): CGColor(gray: dark ? 0.9 : 0.1, alpha: 1)]))
}
var results: [[String: Any]] = []
for scale in [1, 2] {
 let width = 1120, height = 1120
 let ctx = CGContext(data: nil, width: width*scale, height: height*scale, bitsPerComponent: 8,
                     bytesPerRow: 0, space: CGColorSpaceCreateDeviceRGB(),
                     bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
 ctx.scaleBy(x: CGFloat(scale), y: CGFloat(scale))
 ctx.setShouldAntialias(true)
 for (section, dark) in [false, true].enumerated() {
  let top = height-section*560
  ctx.setFillColor(CGColor(gray: dark ? 0.08 : 0.98, alpha: 1))
  ctx.fill(CGRect(x: 0, y: top-560, width: width, height: 560))
  for (column, version) in versions.enumerated() {
   let x = 20+column*560
   let label = CTFontCreateWithName("Helvetica" as CFString, 13, nil)
   ctx.textPosition = CGPoint(x: x, y: top-25)
   CTLineDraw(line("\(version) / \(column == 0 ? "Before" : "Optical study") / CoreText \(scale)x", label, dark), ctx)
   for (styleIndex, style) in ["Regular", "Bold"].enumerated() {
    for (row, size) in [12, 14, 16, 24].enumerated() {
     let y = top-55-styleIndex*250-row*58
     let font = CTFontCreateWithGraphicsFont(fonts["\(version)-\(style)"]!, CGFloat(size), nil, nil)
     let sample = size == 24 ? "한글 입력값 읽기 Hmn 01Il" : "const 입력값 = '한글 값 읽기 없습니다';"
     let text = line(sample, font, dark)
     for run in CTLineGetGlyphRuns(text) as! [CTRun] {
      let used = (CTRunGetAttributes(run) as NSDictionary)[kCTFontAttributeName] as! CTFont
      precondition(CTFontCopyPostScriptName(used) as String == "SunshineMono-\(style)")
     }
     let latin = CTLineGetTypographicBounds(line("HH", font, dark), nil, nil, nil)
     let hangul = CTLineGetTypographicBounds(line("한", font, dark), nil, nil, nil)
     precondition(abs(latin-hangul) < 0.001)
     precondition(CTLineGetTypographicBounds(text, nil, nil, nil) < 520)
     ctx.textPosition = CGPoint(x: x, y: y)
     CTLineDraw(line("\(style) / \(size) px", label, dark), ctx)
     ctx.textPosition = CGPoint(x: x, y: y-30)
     CTLineDraw(text, ctx)
     results.append(["version": version, "style": style, "size": size, "scale": scale,
                     "dark": dark, "fallback": false, "two_to_one_advance": true])
    }
   }
  }
 }
 let dest = CGImageDestinationCreateWithURL(root.appendingPathComponent("docs/proofs/optical-comparison-\(scale)x.png") as CFURL, UTType.png.identifier as CFString, 1, nil)!
 CGImageDestinationAddImage(dest, ctx.makeImage()!, nil)
 precondition(CGImageDestinationFinalize(dest))
}
try JSONSerialization.data(withJSONObject: results, options: [.prettyPrinted, .sortedKeys])
 .write(to: root.appendingPathComponent("docs/optical-coretext-verification.json"))
print("CoreText: \(results.count) comparisons passed; file-backed fonts, no sample fallback, 2:1 advance")
