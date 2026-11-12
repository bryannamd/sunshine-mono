import Foundation
import CoreText
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers
let root=URL(fileURLWithPath:FileManager.default.currentDirectoryPath)
let data=try Data(contentsOf:root.appendingPathComponent("docs/fira-ligatures-verification.json"))
let reports=try JSONSerialization.jsonObject(with:data) as! [[String:Any]]
let samples=(reports[0]["samples"] as! [[String:Any]]).filter{$0["active"] as! Bool}.map{$0["text"] as! String}
let cg=CGFont(CGDataProvider(url:root.appendingPathComponent("fonts/releases/0.5.1/SunshineMono-Regular.ttf") as CFURL)!)!
let width=1200, height=180+Int(ceil(Double(samples.count)/4))*46
let ctx=CGContext(data:nil,width:width*2,height:height*2,bitsPerComponent:8,bytesPerRow:0,space:CGColorSpaceCreateDeviceRGB(),bitmapInfo:CGImageAlphaInfo.premultipliedLast.rawValue)!
ctx.scaleBy(x:2,y:2)
ctx.setFillColor(CGColor(gray:0.97,alpha:1));ctx.fill(CGRect(x:0,y:0,width:width,height:height))
func draw(_ text:String,_ font:CTFont,_ x:Int,_ y:Int,_ gray:CGFloat=0.12,_ check:Bool=false){
 let line=CTLineCreateWithAttributedString(NSAttributedString(string:text,attributes:[NSAttributedString.Key(kCTFontAttributeName as String):font,NSAttributedString.Key(kCTForegroundColorAttributeName as String):CGColor(gray:gray,alpha:1)]))
 if check { for run in CTLineGetGlyphRuns(line) as! [CTRun] {
 let used=(CTRunGetAttributes(run) as NSDictionary)[kCTFontAttributeName] as! CTFont
 precondition(CTFontCopyPostScriptName(used) as String == "SunshineMono-Regular")
 }}
 ctx.textPosition=CGPoint(x:x,y:height-y);CTLineDraw(line,ctx)
}
let title=CTFontCreateWithName("Helvetica-Bold" as CFString,25,nil)
let label=CTFontCreateWithName("Helvetica" as CFString,15,nil)
let raw=CTFontCreateWithName("Menlo-Regular" as CFString,17,nil)
let applied=CTFontCreateWithGraphicsFont(cg,27,nil,nil)
draw("Sunshine Mono 0.5.1 / Fira Code ligatures",title,28,42)
draw("135 active operator examples  |  source characters  >  rendered ligature",label,28,73,0.4)
draw("꿈 낑",CTFontCreateWithGraphicsFont(cg,32,nil,nil),28,120,0.12,true)
for col in 0..<4 {draw("INPUT                         SUNSHINE",label,28+col*300,154,0.45)}
for (i,s) in samples.enumerated(){
 let col=i%4,row=i/4,x=28+col*300,y=188+row*46
 ctx.setFillColor(CGColor(gray:row%2==0 ? 0.93 : 0.97,alpha:1));ctx.fill(CGRect(x:col*300,y:height-y-14,width:300,height:46))
 draw(s,raw,x,y,0.45);draw("›",label,x+130,y,0.6);draw(s,applied,x+160,y,0.1,true)
}
let url=root.appendingPathComponent("docs/proofs/sunshine-fira-ligature-catalog.png")
let dest=CGImageDestinationCreateWithURL(url as CFURL,UTType.png.identifier as CFString,1,nil)!
CGImageDestinationAddImage(dest,ctx.makeImage()!,nil);precondition(CGImageDestinationFinalize(dest))
print("Rendered \(samples.count) active examples with Sunshine Mono 0.5.1; no font fallback")
