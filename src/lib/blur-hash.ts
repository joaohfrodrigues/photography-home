import { decode } from 'blurhash'

// CRC32 lookup table for PNG chunks
const CRC_TABLE = (() => {
  const t = new Uint32Array(256)
  for (let n = 0; n < 256; n++) {
    let c = n
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1
    t[n] = c
  }
  return t
})()

function crc32(data: Uint8Array): number {
  let crc = 0xffffffff
  for (const b of data) crc = CRC_TABLE[(crc ^ b) & 0xff] ^ (crc >>> 8)
  return (crc ^ 0xffffffff) >>> 0
}

function pngChunk(type: string, data: Uint8Array): Uint8Array {
  const typeBytes = new Uint8Array([...type].map((c) => c.charCodeAt(0)))
  const buf = new Uint8Array(4 + 4 + data.length + 4)
  const view = new DataView(buf.buffer)
  view.setUint32(0, data.length, false)
  buf.set(typeBytes, 4)
  buf.set(data, 8)
  const crcInput = new Uint8Array(4 + data.length)
  crcInput.set(typeBytes)
  crcInput.set(data, 4)
  view.setUint32(8 + data.length, crc32(crcInput), false)
  return buf
}

function adler32(data: Uint8Array): number {
  let s1 = 1, s2 = 0
  for (const b of data) {
    s1 = (s1 + b) % 65521
    s2 = (s2 + s1) % 65521
  }
  return (s2 << 16) | s1
}

// Deflate "store" block — valid zlib-wrapped uncompressed data, no external deps
function deflateStore(data: Uint8Array): Uint8Array {
  const n = data.length
  const out = new Uint8Array(2 + 5 + n + 4)
  const view = new DataView(out.buffer)
  out[0] = 0x78; out[1] = 0x01 // zlib header: deflate, window 32K, check bits OK
  out[2] = 0x01                  // BFINAL=1, BTYPE=00 (no compression)
  view.setUint16(3, n, true)     // LEN (little-endian)
  view.setUint16(5, (~n) & 0xffff, true) // NLEN (one's complement)
  out.set(data, 7)
  view.setUint32(7 + n, adler32(data), false) // Adler-32 over uncompressed data
  return out
}

/** Convert a Unsplash blur hash to a base64 PNG data URL for use as Next.js blurDataURL. */
export function blurHashToDataURL(hash: string, w = 8, h = 8): string {
  if (!hash) return ''
  let pixels: Uint8ClampedArray
  try {
    pixels = decode(hash, w, h)
  } catch {
    return ''
  }

  // Build PNG scanlines: 1 filter byte (None) + RGBA pixels per row
  const rowLen = 1 + w * 4
  const raw = new Uint8Array(h * rowLen)
  for (let y = 0; y < h; y++) {
    raw[y * rowLen] = 0 // filter: None
    for (let x = 0; x < w; x++) {
      const s = (y * w + x) * 4
      const d = y * rowLen + 1 + x * 4
      raw[d] = pixels[s]; raw[d + 1] = pixels[s + 1]
      raw[d + 2] = pixels[s + 2]; raw[d + 3] = pixels[s + 3]
    }
  }

  // IHDR: width, height, 8-bit, RGBA (type 6), no compression/filter/interlace
  const ihdr = new Uint8Array(13)
  const ihdrV = new DataView(ihdr.buffer)
  ihdrV.setUint32(0, w, false); ihdrV.setUint32(4, h, false)
  ihdr.set([8, 6, 0, 0, 0], 8)

  const sig = new Uint8Array([137, 80, 78, 71, 13, 10, 26, 10])
  const parts = [sig, pngChunk('IHDR', ihdr), pngChunk('IDAT', deflateStore(raw)), pngChunk('IEND', new Uint8Array(0))]
  const total = parts.reduce((a, p) => a + p.length, 0)
  const png = new Uint8Array(total)
  let off = 0
  for (const p of parts) { png.set(p, off); off += p.length }

  return `data:image/png;base64,${Buffer.from(png).toString('base64')}`
}
