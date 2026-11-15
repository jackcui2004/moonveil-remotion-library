import Foundation
import Vision
import AppKit
import CoreImage
import ImageIO

let input = URL(fileURLWithPath: CommandLine.arguments[1])
let output = URL(fileURLWithPath: CommandLine.arguments[2], isDirectory: true)
try FileManager.default.createDirectory(at: output, withIntermediateDirectories: true)
let names = CommandLine.arguments.dropFirst(3)
let context = CIContext(options: [.useSoftwareRenderer: false])
for name in names {
    do {
        let url = input.appendingPathComponent(name + ".png")
        let handler = VNImageRequestHandler(url: url, options: [:])
        let request = VNGenerateForegroundInstanceMaskRequest()
        try handler.perform([request])
        guard let observation = request.results?.first, let source = CIImage(contentsOf: url) else { continue }
        var entries: [[String: Any]] = []
        for id in observation.allInstances {
            let buffer = try observation.generateScaledMaskForImage(forInstances: IndexSet(integer: id), from: handler)
            let mask = CIImage(cvPixelBuffer: buffer)
            let clear = CIImage(color: CIColor.clear).cropped(to: source.extent)
            let cut = source.applyingFilter("CIBlendWithMask", parameters: [kCIInputBackgroundImageKey: clear, kCIInputMaskImageKey: mask])
            guard let cg = context.createCGImage(cut, from: source.extent) else { continue }
            let image = NSBitmapImageRep(cgImage: cg)
            let file = "\(name)-instance-\(id).png"
            try image.representation(using: .png, properties: [:])!.write(to: output.appendingPathComponent(file))
            // Extent is measured from the actual native mask, never guessed from a face box.
            CVPixelBufferLockBaseAddress(buffer, .readOnly)
            let w = CVPixelBufferGetWidth(buffer), h = CVPixelBufferGetHeight(buffer), stride = CVPixelBufferGetBytesPerRow(buffer)
            let ptr = CVPixelBufferGetBaseAddress(buffer)!.assumingMemoryBound(to: UInt8.self)
            var minX=w, minY=h, maxX=0, maxY=0, count=0
            for y in 0..<h { for x in 0..<w {
                if ptr[y*stride+x] > 128 { minX=min(minX,x);minY=min(minY,y);maxX=max(maxX,x);maxY=max(maxY,y);count += 1 }
            }}
            CVPixelBufferUnlockBaseAddress(buffer, .readOnly)
            entries.append(["instance": id,"file":file,"bbox":[minX,minY,maxX+1,maxY+1],"opaquePixels":count,"width":w,"height":h])
        }
        let metadata: [String:Any] = ["parent_asset_id":name,"method":"Apple Vision foreground instance mask; original photographic RGB retained","instances":entries,"verified":false]
        try JSONSerialization.data(withJSONObject: metadata, options: [.prettyPrinted,.sortedKeys]).write(to: output.appendingPathComponent(name + ".json"))
        print("\(name): \(entries.count) instances")
        fflush(stdout)
    } catch { print("ERROR \(name): \(error)");fflush(stdout) }
}
