"""Generate a Euro (€) icon (multi-size .ico) for the AR Dashboard shortcut."""
from PIL import Image, ImageDraw, ImageFont
import os, sys

def find_font():
    candidates = [
        r'C:\Windows\Fonts\georgiab.ttf',   # Georgia Bold — handsome € glyph
        r'C:\Windows\Fonts\timesbd.ttf',    # Times New Roman Bold
        r'C:\Windows\Fonts\arialbd.ttf',    # Arial Bold
        r'C:\Windows\Fonts\seguisb.ttf',    # Segoe UI Semibold
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

def draw_euro(size):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size

    # Editorial palette: oxblood disc, cream glyph, brass rim
    bg_color = (30, 24, 20, 255)        # deep ink
    rim_color = (168, 130, 30, 255)      # brass
    glyph_color = (243, 236, 224, 255)   # cream / paper

    # Filled disc with thin brass rim
    pad = max(1, int(s * 0.04))
    d.ellipse([pad, pad, s - pad, s - pad], fill=bg_color)
    rim_w = max(1, int(s * 0.025))
    for i in range(rim_w):
        d.ellipse([pad + i, pad + i, s - pad - i, s - pad - i],
                  outline=rim_color)

    # Draw € glyph centered
    font_path = find_font()
    if font_path and s >= 24:
        # tune size empirically — Georgia Bold € sits well at ~0.72 of disc
        font_size = int(s * 0.72)
        font = ImageFont.truetype(font_path, font_size)
        text = '€'
        # measure
        bbox = d.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        # bbox y-offset accounts for font ascent
        x = (s - tw) // 2 - bbox[0]
        y = (s - th) // 2 - bbox[1]
        d.text((x, y), text, font=font, fill=glyph_color)
    else:
        # Fallback: draw € from primitives at small sizes
        cx, cy = s / 2, s / 2
        rx, ry = s * 0.26, s * 0.32
        thick = max(2, int(s * 0.09))
        # Open C-shape (left-facing)
        d.arc([cx - rx, cy - ry, cx + rx, cy + ry], 35, 325,
              fill=glyph_color, width=thick)
        # Two horizontal cross-strokes
        bar_w = int(s * 0.42)
        bar_h = max(2, int(s * 0.07))
        bar_x = int(cx - bar_w / 2 - s * 0.02)
        d.rectangle([bar_x, int(cy - s * 0.10) - bar_h // 2,
                     bar_x + bar_w, int(cy - s * 0.10) + bar_h // 2],
                    fill=glyph_color)
        d.rectangle([bar_x, int(cy + s * 0.06) - bar_h // 2,
                     bar_x + bar_w, int(cy + s * 0.06) + bar_h // 2],
                    fill=glyph_color)

    return img

sizes = [16, 24, 32, 48, 64, 128, 256]
master = draw_euro(256)
out_path = r'C:\Users\I588206\Documents\AR_Dashboard\euro.ico'
master.save(out_path, format='ICO', sizes=[(s, s) for s in sizes])
print('Saved:', out_path)
