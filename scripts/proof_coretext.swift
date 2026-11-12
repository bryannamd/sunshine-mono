// Native CoreText proof; process-local registration, no user settings changed.
import Foundation
import CoreText
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers
let root=URL(fileURLWithPath:FileManager.default.currentDirectoryPath)
let releaseMode=CommandLine.arguments.contains("--sunshine")
let fontDirectory=releaseMode ? "fonts/releases/0.3.0" : "fonts/rounded"
let fontPrefix=releaseMode ? "SunshineMono" : "MMCodingB3"
let proofPrefix=releaseMode ? "sunshine" : "b3"
for style in ["Regular","Bold"] {
 let url=root.appendingPathComponent("\(fontDirectory)/\(fontPrefix)-\(style).ttf")
 var error:Unmanaged<CFError>?
 guard CTFontManagerRegisterFontsForURL(url as CFURL,.process,&error) else {fatalError("Registration failed: \(String(describing:error))")}
}
let regular=CTFontCreateWithName("\(fontPrefix)-Regular" as CFString,14,nil)
let bold=CTFontCreateCopyWithSymbolicTraits(regular,14,nil,.boldTrait,.boldTrait)!
assert((CTFontCopyPostScriptName(bold) as String)=="\(fontPrefix)-Bold")
let sample="한글 값 읽기 난 단 달 맘 밥 뚫 꽉 햇 에헤 Hmn 0O1Il != =>"
func line(_ text:String,_ font:CTFont)->CTLine {
 return CTLineCreateWithAttributedString(NSAttributedString(string:text,attributes:[NSAttributedString.Key(kCTFontAttributeName as String):font,NSAttributedString.Key(kCTForegroundColorAttributeName as String):CGColor(gray:0.08,alpha:1)]))
}
var results:[[String:Any]]=[]
for scale in [1,2] {
 let width=1300,height=760
 let context=CGContext(data:nil,width:width*scale,height:height*scale,bitsPerComponent:8,bytesPerRow:0,space:CGColorSpaceCreateDeviceRGB(),bitmapInfo:CGImageAlphaInfo.premultipliedLast.rawValue)!
 context.scaleBy(x:CGFloat(scale),y:CGFloat(scale));context.setFillColor(CGColor(gray:0.97,alpha:1));context.fill(CGRect(x:0,y:0,width:width,height:height))
 context.setShouldAntialias(true)
 for (column,style) in ["Regular","Bold"].enumerated() {
  for (row,size) in [12,13,14,16,24,26,28,32].enumerated() {
   let font=CTFontCreateWithName("\(fontPrefix)-\(style)" as CFString,CGFloat(size),nil)
   let text=line(sample,font)
   let runs=CTLineGetGlyphRuns(text) as! [CTRun]
   for run in runs {
    let attrs=CTRunGetAttributes(run) as NSDictionary
    let used=attrs[kCTFontAttributeName] as! CTFont
    assert(CTFontCopyPostScriptName(used) as String == "\(fontPrefix)-\(style)","Unexpected fallback")
   }
   let latin=CTLineGetTypographicBounds(line("HH",font),nil,nil,nil)
   let hangul=CTLineGetTypographicBounds(line("한",font),nil,nil,nil)
   assert(abs(latin-hangul)<0.001)
   let labelFont=CTFontCreateWithName("Helvetica" as CFString,12,nil)
   context.textPosition=CGPoint(x:20+column*640,y:height-30-row*88)
   CTLineDraw(line("\(style) · \(size) px · \(scale)x",labelFont),context)
   context.textPosition=CGPoint(x:20+column*640,y:height-65-row*88)
   // The largest rows use a shorter specimen to avoid clipping.
   CTLineDraw(size>20 ? line("한글 값 읽기 뚫 에헤 Hmn 0O1Il",font):text,context)
   results.append(["style":style,"size":size,"scale":scale,"latinTwoCells":latin,"hangulOneGlyph":hangul,"fallback":false])
  }
 }
 let image=context.makeImage()!
 let dest=CGImageDestinationCreateWithURL(root.appendingPathComponent("docs/proofs/\(proofPrefix)-coretext-\(scale)x.png") as CFURL,UTType.png.identifier as CFString,1,nil)!
 CGImageDestinationAddImage(dest,image,nil);assert(CGImageDestinationFinalize(dest))
}
let data=try JSONSerialization.data(withJSONObject:results,options:[.prettyPrinted,.sortedKeys])
try data.write(to:root.appendingPathComponent("docs/\(proofPrefix)-coretext-verification.json"))
print("CoreText: 32 style/size/scale cases passed; native Bold selection; no sample fallback; 2:1 advance")
