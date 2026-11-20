import os
import sys
import io
import struct
import fitz
from PIL import Image

def write_windows_ico(src_image: Image.Image, out_ico_path: str):
    """
    Writes a strict Microsoft Windows-compliant multi-resolution .ico file.
    Sizes 16, 24, 32, 48, 64 are written as uncompressed 32-bit DIB bitmaps
    (BITMAPINFOHEADER + BGRA + 1-bit AND mask) for 100% Windows Shell compatibility.
    Size 256x256 is written as standard PNG for Vista/Win10/Win11 jumbo previews.
    """
    entries = []
    images_data = []

    # 1. Standard DIB sizes
    for s in [16, 24, 32, 48, 64]:
        im = src_image.resize((s, s), Image.Resampling.LANCZOS)
        bgra = bytearray()
        for y in reversed(range(s)):
            for x in range(s):
                r, g, b, a = im.getpixel((x, y))
                bgra.extend([b, g, r, a])

        # 1-bit AND mask: 1 for transparent (a == 0), 0 for opaque (a > 0)
        row_bytes = ((s + 31) // 32) * 4
        and_mask = bytearray(row_bytes * s)
        for y_idx, y in enumerate(reversed(range(s))):
            for x in range(s):
                _, _, _, a = im.getpixel((x, y))
                if a == 0:
                    byte_index = y_idx * row_bytes + (x // 8)
                    bit_index = 7 - (x % 8)
                    and_mask[byte_index] |= (1 << bit_index)

        bih = struct.pack(
            '<LLLHHLLLLLL',
            40,         # biSize (BITMAPINFOHEADER)
            s,          # biWidth
            s * 2,      # biHeight (doubled for XOR + AND)
            1,          # biPlanes
            32,         # biBitCount
            0,          # biCompression (BI_RGB)
            len(bgra) + len(and_mask), # biSizeImage
            0, 0, 0, 0
        )
        dib_data = bih + bytes(bgra) + bytes(and_mask)
        images_data.append(dib_data)
        entries.append({
            'width': s,
            'height': s,
            'colors': 0,
            'reserved': 0,
            'planes': 1,
            'bpp': 32,
            'size': len(dib_data)
        })

    # 2. Jumbo 256x256 icon as PNG (standard Windows Shell Vista+)
    im256 = src_image.resize((256, 256), Image.Resampling.LANCZOS)
    png_buf = io.BytesIO()
    im256.save(png_buf, format='PNG', optimize=True)
    png_data = png_buf.getvalue()
    images_data.append(png_data)
    entries.append({
        'width': 0,  # 0 means 256 in ICO spec
        'height': 0, # 0 means 256 in ICO spec
        'colors': 0,
        'reserved': 0,
        'planes': 1,
        'bpp': 32,
        'size': len(png_data)
    })

    # Calculate offsets
    header_size = 6 + len(entries) * 16
    offset = header_size
    for entry in entries:
        entry['offset'] = offset
        offset += entry['size']

    # Write ICO binary
    with open(out_ico_path, 'wb') as f:
        f.write(struct.pack('<HHH', 0, 1, len(entries)))
        for e in entries:
            f.write(struct.pack(
                '<BBBBHHII',
                e['width'],
                e['height'],
                e['colors'],
                e['reserved'],
                e['planes'],
                e['bpp'],
                e['size'],
                e['offset']
            ))
        for data in images_data:
            f.write(data)

    print(f"[+] Saved {out_ico_path} with {len(entries)} sizes (16, 24, 32, 48, 64 DIB + 256 PNG)")

def generate_icons():
    raw_ai_path = os.path.join("web", "assets", "logo_raw.png")
    svg_path = os.path.join("web", "assets", "logo.svg")
    png_path = os.path.join("web", "assets", "logo.png")
    ico_path = "app_icon.ico"

    img = None
    if os.path.exists(raw_ai_path):
        print(f"[*] Loading AI-generated logo from {raw_ai_path}...")
        img = Image.open(raw_ai_path).convert("RGBA")
    elif os.path.exists(svg_path):
        print(f"[*] Rendering SVG from {svg_path} with transparent alpha...")
        doc = fitz.open(svg_path)
        page = doc[0]
        # Critical: alpha=True renders pure transparent background (no white box)
        pix = page.get_pixmap(dpi=150, alpha=True)
        raw_png = os.path.join("web", "assets", "raw_render.png")
        pix.save(raw_png)
        img = Image.open(raw_png).convert("RGBA")
        if os.path.exists(raw_png):
            os.remove(raw_png)
    else:
        print("[-] No source logo found (SVG or PNG).")
        return False

    # Crop tightly to non-transparent bounding box
    bbox = img.getbbox()
    if bbox:
        shield = img.crop(bbox)
    else:
        shield = img

    # Fit within 480x480 inside a 512x512 transparent canvas
    w, h = shield.size
    scale = 480.0 / max(w, h)
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    scaled_shield = shield.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # 100% Transparent master 512x512 canvas
    logo_512 = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    paste_x = (512 - new_w) // 2
    paste_y = (512 - new_h) // 2
    logo_512.paste(scaled_shield, (paste_x, paste_y), scaled_shield)

    logo_512.save(png_path, "PNG")
    print(f"[+] Saved transparent master PNG: {png_path} (512x512)")

    # Save strict Windows-compliant ICO
    write_windows_ico(logo_512, ico_path)

    return True

if __name__ == "__main__":
    success = generate_icons()
    sys.exit(0 if success else 1)
