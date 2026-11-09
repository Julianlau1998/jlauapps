// Draws the JL Apps logo: "jl" in white on a dark circle with a thin ring and an orange-to-purple dot.
// The letters are turned into outlines with CoreText, so the logo looks the same without Apple's fonts.
// Writes assets/logo.svg, icon.png (512, transparent), favicon.png (64) and apple-touch-icon.png
// (180, square, because iOS puts touch icons on a black square anyway).
//   swift _tools/logo.swift
import AppKit
import CoreText

let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent()

// Same layout as the chosen mockup, in a 64 × 64 box: "jl" centered on x = 29, baseline at y = 45.
let font = NSFont.systemFont(ofSize: 34, weight: .heavy) as CTFont
let tracking: CGFloat = -2
let glyphPath = CGMutablePath()
var glyphs = [CGGlyph](repeating: 0, count: 2)
CTFontGetGlyphsForCharacters(font, Array("jl".utf16), &glyphs, 2)
var advances = [CGSize](repeating: .zero, count: 2)
CTFontGetAdvancesForGlyphs(font, .horizontal, glyphs, &advances, 2)
let width = advances.reduce(0) { $0 + $1.width } + tracking
var x = 29 - width / 2
for (glyph, advance) in zip(glyphs, advances) {
    if let outline = CTFontCreatePathForGlyph(font, glyph, nil) {
        // Glyph outlines point up; the 64 × 64 box points down like SVG.
        glyphPath.addPath(outline, transform: CGAffineTransform(a: 1, b: 0, c: 0, d: -1, tx: x, ty: 45))
    }
    x += advance.width + tracking
}

func svgPath(_ path: CGPath) -> String {
    var d = ""
    let f = { (p: CGPoint) in String(format: "%.2f %.2f", p.x, p.y) }
    path.applyWithBlock { element in
        let e = element.pointee
        switch e.type {
        case .moveToPoint: d += "M" + f(e.points[0])
        case .addLineToPoint: d += "L" + f(e.points[0])
        case .addQuadCurveToPoint: d += "Q" + f(e.points[0]) + " " + f(e.points[1])
        case .addCurveToPoint: d += "C" + f(e.points[0]) + " " + f(e.points[1]) + " " + f(e.points[2])
        case .closeSubpath: d += "Z"
        @unknown default: break
        }
    }
    return d
}

let svg = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><defs><linearGradient id="jl-dot" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fb923c"/><stop offset="1" stop-color="#a855f7"/></linearGradient></defs><circle cx="32" cy="32" r="32" fill="#1a1730"/><circle cx="32" cy="32" r="31.25" fill="none" stroke="#fff" stroke-opacity=".18" stroke-width="1.5"/><path fill="#fff" d="\(svgPath(glyphPath))"/><circle cx="45" cy="41" r="5" fill="url(#jl-dot)"/></svg>

"""
try! svg.write(to: root.appendingPathComponent("assets/logo.svg"), atomically: true, encoding: .utf8)

func png(_ name: String, size: Int, square: Bool) {
    let space = CGColorSpace(name: CGColorSpace.sRGB)!
    let ctx = CGContext(data: nil, width: size, height: size, bitsPerComponent: 8, bytesPerRow: 0,
                        space: space, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
    let s = CGFloat(size) / 64
    ctx.translateBy(x: 0, y: CGFloat(size))
    ctx.scaleBy(x: s, y: -s)
    let dark = CGColor(srgbRed: 0x1a / 255, green: 0x17 / 255, blue: 0x30 / 255, alpha: 1)
    ctx.setFillColor(dark)
    if square {
        ctx.fill(CGRect(x: 0, y: 0, width: 64, height: 64))
    } else {
        ctx.fillEllipse(in: CGRect(x: 0, y: 0, width: 64, height: 64))
        ctx.setStrokeColor(CGColor(srgbRed: 1, green: 1, blue: 1, alpha: 0.18))
        ctx.setLineWidth(1.5)
        ctx.strokeEllipse(in: CGRect(x: 0.75, y: 0.75, width: 62.5, height: 62.5))
    }
    ctx.addPath(glyphPath)
    ctx.setFillColor(CGColor(srgbRed: 1, green: 1, blue: 1, alpha: 1))
    ctx.fillPath()
    ctx.saveGState()
    ctx.addEllipse(in: CGRect(x: 40, y: 36, width: 10, height: 10))
    ctx.clip()
    let gradient = CGGradient(colorsSpace: space, colors: [
        CGColor(srgbRed: 0xfb / 255, green: 0x92 / 255, blue: 0x3c / 255, alpha: 1),
        CGColor(srgbRed: 0xa8 / 255, green: 0x55 / 255, blue: 0xf7 / 255, alpha: 1),
    ] as CFArray, locations: [0, 1])!
    ctx.drawLinearGradient(gradient, start: CGPoint(x: 40, y: 36), end: CGPoint(x: 50, y: 46), options: [])
    ctx.restoreGState()
    let rep = NSBitmapImageRep(cgImage: ctx.makeImage()!)
    try! rep.representation(using: .png, properties: [:])!.write(to: root.appendingPathComponent(name))
}

png("icon.png", size: 512, square: false)
png("favicon.png", size: 64, square: false)
png("apple-touch-icon.png", size: 180, square: true)
print("logo written")
