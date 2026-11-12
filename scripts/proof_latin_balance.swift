// File-backed font comparison; no browser or installed-font cache involved.
import Foundation
import CoreText
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers
let root=URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let geometry=CommandLine.arguments.contains("--geometry")
var fonts:[String:CGFont]=[:]
for version in ["0.4.1","0.4.2"] {
 for style in ["Regular","Bold"] {
  let path=geometry ? "fonts/\(version == "0.4.1" ? "final-radius" : "latin-balance")/MMCodingB3-\(style)-Unhinted.ttf" : "fonts/releases/\(version)/SunshineMono-\(style).ttf"
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
  for (col,version) in ["0.4.1","0.4.2"].enumerated() {
   let x=24+col*730;let label=CTFontCreateWithName("Helvetica" as CFString,14,nil)
   ctx.textPosition=CGPoint(x:x,y:top-26)
   CTLineDraw(line("\(version) / \(style) / \(scale)x / \(col == 0 ? "Before" : "Compact Latin curves")",label,dark),ctx)
   let samples:[(Int,String)]=[(14,"function filter(입력값) { return true; }"),(16,"let job = '한글 받침과 영문 f t r j l J';"),(24,"abcdefghijklmnopqrstuvwxyz"),(24,"ABCDEFGHIJKLMNOPQRSTUVWXYZ"),(48,"f t r j l J 한글")]
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
 let prefix=geometry ? "latin-balance-geometry" : "latin-balance-comparison"
 let dest=CGImageDestinationCreateWithURL(root.appendingPathComponent("docs/proofs/\(prefix)-\(scale)x.png") as CFURL,UTType.png.identifier as CFString,1,nil)!
 CGImageDestinationAddImage(dest,ctx.makeImage()!,nil);precondition(CGImageDestinationFinalize(dest))
}
if !geometry {
 try JSONSerialization.data(withJSONObject:results,options:[.prettyPrinted,.sortedKeys]).write(to:root.appendingPathComponent("docs/latin-balance-coretext-verification.json"))
}
print("CoreText: \(results.count) comparisons; Latin alphabet and Hangul shown, no fallback, 2:1 advance")
