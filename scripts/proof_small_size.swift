// File-backed font comparison; no browser or installed-font cache involved.
import Foundation
import CoreText
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers
let root=URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let geometry=CommandLine.arguments.contains("--geometry")
var fonts:[String:CGFont]=[:]
for version in ["0.5.0","0.5.1"] {
 for style in ["Regular","Bold"] {
  let path=(geometry && version == "0.5.1") ? "fonts/small-size/MMCodingB3-\(style).ttf" : "fonts/releases/\(version)/SunshineMono-\(style).ttf"
  fonts["\(version)-\(style)"]=CGFont(CGDataProvider(url:root.appendingPathComponent(path) as CFURL)!)!
 }
}
func line(_ text:String,_ font:CTFont,_ dark:Bool)->CTLine {
 CTLineCreateWithAttributedString(NSAttributedString(string:text,attributes:[NSAttributedString.Key(kCTFontAttributeName as String):font,NSAttributedString.Key(kCTForegroundColorAttributeName as String):CGColor(gray:dark ? 0.92 : 0.08,alpha:1)]))
}
var results:[[String:Any]]=[]
for scale in [1,2] {
 let width=1460,height=1680
 let ctx=CGContext(data:nil,width:width*scale,height:height*scale,bitsPerComponent:8,bytesPerRow:0,space:CGColorSpaceCreateDeviceRGB(),bitmapInfo:CGImageAlphaInfo.premultipliedLast.rawValue)!
 ctx.scaleBy(x:CGFloat(scale),y:CGFloat(scale));ctx.setShouldAntialias(true)
 for (section,combination) in [("Regular",false),("Bold",false),("Regular",true),("Bold",true)].enumerated() {
  let (style,dark)=combination;let top=height-section*420
  ctx.setFillColor(CGColor(gray:dark ? 0.07 : 0.98,alpha:1));ctx.fill(CGRect(x:0,y:top-420,width:width,height:420))
  for (col,version) in ["0.5.0","0.5.1"].enumerated() {
   let x=24+col*730;let label=CTFontCreateWithName("Helvetica" as CFString,14,nil)
   ctx.textPosition=CGPoint(x:x,y:top-26)
   CTLineDraw(line("\(version) / \(style) / \(scale)x / \(col == 0 ? "Before" : "Small-size Hangul spacing")",label,dark),ctx)
   let samples:[(Int,String)]=[(12,"입력값을 읽고 없으면 빈 값을 반환합니다. 괜찮은 글꼴"),(14,"if (입력값 != null) return 읽은값; // 삶과 균형"),(16,"값 없 읽 닮 삶 앉 뚫 꽉 흙 뿔 꿈 끙 낑"),(24,"가 고 구 간 갑 값 읽 뚫 뿔 쌓"),(48,"값 읽 뚫 뿔 꿈 끙 낑")]
   for (row,sample) in samples.enumerated() {
    let (size,text)=sample
    let cg=fonts["\(version)-\(style)"]!
    let font=CTFontCreateWithGraphicsFont(cg,CGFloat(size),nil,nil)
    let rendered=line(text,font,dark)
    for run in CTLineGetGlyphRuns(rendered) as! [CTRun] {
     let used=(CTRunGetAttributes(run) as NSDictionary)[kCTFontAttributeName] as! CTFont
     precondition(CTFontCopyPostScriptName(used) as String == cg.postScriptName! as String)
    }
    let a=CTLineGetTypographicBounds(line("한",font,dark),nil,nil,nil)
    let b=CTLineGetTypographicBounds(line("HH",font,dark),nil,nil,nil)
    precondition(abs(a-b)<0.001)
    precondition(CTLineGetTypographicBounds(rendered,nil,nil,nil)<690)
    let y=top-75-row*72
    ctx.textPosition=CGPoint(x:x,y:y+25)
    CTLineDraw(line("\(size) px",label,dark),ctx)
    ctx.textPosition=CGPoint(x:x,y:y-(size==48 ? 20 : 0))
    CTLineDraw(rendered,ctx)
    results.append(["version":version,"style":style,"scale":scale,"size":size,"dark":dark,"fallback":false,"two_to_one_advance":true])
   }
  }
 }
 let prefix=geometry ? "small-size-geometry" : "small-size-comparison"
 let dest=CGImageDestinationCreateWithURL(root.appendingPathComponent("docs/proofs/\(prefix)-\(scale)x.png") as CFURL,UTType.png.identifier as CFString,1,nil)!
 CGImageDestinationAddImage(dest,ctx.makeImage()!,nil);precondition(CGImageDestinationFinalize(dest))
}
if !geometry {
 try JSONSerialization.data(withJSONObject:results,options:[.prettyPrinted,.sortedKeys]).write(to:root.appendingPathComponent("docs/small-size-coretext-verification.json"))
}
print("CoreText: \(results.count) comparisons; crowded Hangul and mixed code shown, no fallback, 2:1 advance")
