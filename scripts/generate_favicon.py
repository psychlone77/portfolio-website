#!/usr/bin/env python3
"""
Generate broadsheet-styled adaptive SVG and multi-resolution ICO favicons
for Nithika Dias's portfolio website using Playfair Display bold serifs.
"""

import ctypes
from ctypes import c_long, c_int, c_short, c_ushort, c_char_p, c_void_p, c_char, Structure, POINTER, CFUNCTYPE, byref
from PIL import Image, ImageDraw, ImageFont
import os

class FT_Vector(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

MOVE_TO = CFUNCTYPE(c_int, POINTER(FT_Vector), c_void_p)
LINE_TO = CFUNCTYPE(c_int, POINTER(FT_Vector), c_void_p)
CONIC_TO = CFUNCTYPE(c_int, POINTER(FT_Vector), POINTER(FT_Vector), c_void_p)
CUBIC_TO = CFUNCTYPE(c_int, POINTER(FT_Vector), POINTER(FT_Vector), POINTER(FT_Vector), c_void_p)

class FT_Outline_Funcs(Structure):
    _fields_ = [
        ("move_to", MOVE_TO),
        ("line_to", LINE_TO),
        ("conic_to", CONIC_TO),
        ("cubic_to", CUBIC_TO),
        ("shift", c_int),
        ("delta", c_long)
    ]

class FT_BBox(Structure):
    _fields_ = [("xMin", c_long), ("yMin", c_long), ("xMax", c_long), ("yMax", c_long)]

class FT_Generic(Structure):
    _fields_ = [("data", c_void_p), ("finalizer", c_void_p)]

class FT_Outline(Structure):
    _fields_ = [
        ("n_contours", c_short),
        ("n_points", c_short),
        ("points", POINTER(FT_Vector)),
        ("tags", POINTER(c_char)),
        ("contours", POINTER(c_short)),
        ("flags", c_int)
    ]

class FT_Bitmap(Structure):
    _fields_ = [
        ("rows", c_int),
        ("width", c_int),
        ("pitch", c_int),
        ("buffer", c_void_p),
        ("num_grays", c_short),
        ("pixel_mode", c_char),
        ("palette_mode", c_char),
        ("palette", c_void_p)
    ]

class FT_Glyph_Metrics(Structure):
    _fields_ = [
        ("width", c_long),
        ("height", c_long),
        ("horiBearingX", c_long),
        ("horiBearingY", c_long),
        ("horiAdvance", c_long),
        ("vertBearingX", c_long),
        ("vertBearingY", c_long),
        ("vertAdvance", c_long)
    ]

class FT_GlyphSlotRec(Structure):
    _fields_ = [
        ("library", c_void_p),
        ("face", c_void_p),
        ("next", c_void_p),
        ("glyph_index", c_int),
        ("generic", FT_Generic),
        ("metrics", FT_Glyph_Metrics),
        ("linearHoriAdvance", c_long),
        ("linearVertAdvance", c_long),
        ("advance", FT_Vector),
        ("format", c_int),
        ("bitmap", FT_Bitmap),
        ("bitmap_left", c_int),
        ("bitmap_top", c_int),
        ("outline", FT_Outline),
    ]

class FT_FaceRec(Structure):
    _fields_ = [
        ("num_faces", c_long),
        ("face_index", c_long),
        ("face_flags", c_long),
        ("style_flags", c_long),
        ("num_glyphs", c_long),
        ("family_name", c_char_p),
        ("style_name", c_char_p),
        ("num_fixed_sizes", c_int),
        ("available_sizes", c_void_p),
        ("num_charmaps", c_int),
        ("charmaps", c_void_p),
        ("generic", FT_Generic),
        ("bbox", FT_BBox),
        ("units_per_EM", c_ushort),
        ("ascender", c_short),
        ("descender", c_short),
        ("height", c_short),
        ("max_advance_width", c_short),
        ("max_advance_height", c_short),
        ("underline_position", c_short),
        ("underline_thickness", c_short),
        ("glyph", POINTER(FT_GlyphSlotRec)),
    ]

def extract_playfair_nd_path(font_path: str, weight: int = 800):
    ft = ctypes.CDLL("libfreetype.so.6")
    library = c_void_p()
    ft.FT_Init_FreeType(byref(library))
    face = POINTER(FT_FaceRec)()
    err = ft.FT_New_Face(library, font_path.encode("utf-8"), 0, byref(face))
    if err != 0:
        raise RuntimeError(f"FT_New_Face failed: {err}")
    
    # Set variation weight (e.g. 750 or 800)
    coords = (c_long * 1)(weight << 16)
    ft.FT_Set_Var_Design_Coordinates(face, 1, coords)

    def get_glyph_commands(ch):
        ft.FT_Load_Char(face, ord(ch), 1) # FT_LOAD_NO_SCALE
        outline = face.contents.glyph.contents.outline
        metrics = face.contents.glyph.contents.metrics

        commands = []
        def move_to(to, user):
            commands.append(("M", [(to.contents.x, to.contents.y)]))
            return 0
        def line_to(to, user):
            commands.append(("L", [(to.contents.x, to.contents.y)]))
            return 0
        def conic_to(c, to, user):
            commands.append(("Q", [(c.contents.x, c.contents.y), (to.contents.x, to.contents.y)]))
            return 0
        def cubic_to(c1, c2, to, user):
            commands.append(("C", [(c1.contents.x, c1.contents.y), (c2.contents.x, c2.contents.y), (to.contents.x, to.contents.y)]))
            return 0

        funcs = FT_Outline_Funcs(
            move_to=MOVE_TO(move_to),
            line_to=LINE_TO(line_to),
            conic_to=CONIC_TO(conic_to),
            cubic_to=CUBIC_TO(cubic_to),
            shift=0,
            delta=0
        )
        ft.FT_Outline_Decompose(byref(outline), byref(funcs), None)

        bbox = FT_BBox()
        ft.FT_Outline_Get_BBox(byref(outline), byref(bbox))
        return commands, metrics.horiAdvance, bbox

    cmds_N, adv_N, bbox_N = get_glyph_commands("N")
    cmds_D, adv_D, bbox_D = get_glyph_commands("D")

    # Tight letter-spacing for stamp monogram: shift D slightly left so serifs sit in close harmony
    tracking_offset = -30
    d_x_shift = adv_N + tracking_offset

    all_points_x = []
    all_points_y = []

    for cmd, pts in cmds_N:
        for x, y in pts:
            all_points_x.append(x)
            all_points_y.append(y)
    for cmd, pts in cmds_D:
        for x, y in pts:
            all_points_x.append(x + d_x_shift)
            all_points_y.append(y)

    min_x, max_x = min(all_points_x), max(all_points_x)
    min_y, max_y = min(all_points_y), max(all_points_y)
    raw_w = max_x - min_x
    raw_h = max_y - min_y

    return cmds_N, cmds_D, d_x_shift, (min_x, min_y, raw_w, raw_h)

def build_svg_and_ico():
    font_path = "node_modules/@fontsource-variable/playfair-display/files/playfair-display-latin-wght-normal.woff2"
    cmds_N, cmds_D, d_x_shift, (min_x, min_y, raw_w, raw_h) = extract_playfair_nd_path(font_path, weight=850)

    # 64x64 coordinate system
    # Stamp box: 60x60 from (2, 2) to fill the favicon canvas
    # Monogram scaled to 54.5px wide so it sits snug against the margins for maximum visibility
    target_mono_w = 54.5
    scale = target_mono_w / raw_w
    target_mono_h = raw_h * scale

    target_cx = 32.0
    target_cy = 32.0

    offset_x = target_cx - (target_mono_w / 2.0) - (min_x * scale)
    offset_y = target_cy + (target_mono_h / 2.0) + (min_y * scale) # Note: font y is upwards

    def format_commands(cmds, x_shift=0):
        parts = []
        first = True
        for cmd, pts in cmds:
            if cmd == "M":
                if not first:
                    parts.append("Z")
                first = False
                x, y = pts[0]
                sx = round((x + x_shift) * scale + offset_x, 2)
                sy = round(offset_y - y * scale, 2)
                parts.append(f"M {sx} {sy}")
            elif cmd == "L":
                x, y = pts[0]
                sx = round((x + x_shift) * scale + offset_x, 2)
                sy = round(offset_y - y * scale, 2)
                parts.append(f"L {sx} {sy}")
            elif cmd == "Q":
                cx, cy = pts[0]
                x, y = pts[1]
                scx = round((cx + x_shift) * scale + offset_x, 2)
                scy = round(offset_y - cy * scale, 2)
                sx = round((x + x_shift) * scale + offset_x, 2)
                sy = round(offset_y - y * scale, 2)
                parts.append(f"Q {scx} {scy} {sx} {sy}")
            elif cmd == "C":
                c1x, c1y = pts[0]
                c2x, c2y = pts[1]
                x, y = pts[2]
                sc1x = round((c1x + x_shift) * scale + offset_x, 2)
                sc1y = round(offset_y - c1y * scale, 2)
                sc2x = round((c2x + x_shift) * scale + offset_x, 2)
                sc2y = round(offset_y - c2y * scale, 2)
                sx = round((x + x_shift) * scale + offset_x, 2)
                sy = round(offset_y - y * scale, 2)
                parts.append(f"C {sc1x} {sc1y} {sc2x} {sc2y} {sx} {sy}")
        if parts:
            parts.append("Z")
        return " ".join(parts)

    path_n_svg = format_commands(cmds_N, 0)
    path_d_svg = format_commands(cmds_D, d_x_shift)
    combined_nd_path = f"{path_n_svg} {path_d_svg}"

    # Build adaptive SVG
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <defs>
    <style>
      :root {{
        --ink-block: #1b1a1a;
        --ink-cutout: #fcecec;
        --border-color: #1b1a1a;
      }}
      @media (prefers-color-scheme: dark) {{
        :root {{
          --ink-block: #f4e4e4;
          --ink-cutout: #1b1a1a;
          --border-color: #f4e4e4;
        }}
      }}
      .stamp-block {{
        fill: var(--ink-block);
        stroke: var(--border-color);
        stroke-width: 1;
      }}
      .monogram {{
        fill: var(--ink-cutout);
      }}
    </style>
  </defs>
  <!-- Letterpress Inverted Stamp Block (matches .ink-stamp-filled) -->
  <rect class="stamp-block" x="2" y="2" width="60" height="60" rx="3" />
  <!-- Playfair Display Bold Serifs "ND" Cutout -->
  <path class="monogram" fill-rule="evenodd" d="{combined_nd_path}" />
</svg>
'''
    with open("public/favicon.svg", "w") as f:
        f.write(svg_content)
    print("Wrote public/favicon.svg")

    # Generate multi-resolution favicon.ico (16x16, 32x32, 48x48)
    font = ImageFont.truetype(font_path, 290)
    font.set_variation_by_axes([850])

    master_size = 512
    img = Image.new("RGBA", (master_size, master_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Inverted Stamp Block in Charcoal Ink (#1b1a1a) filling the canvas
    box_pad = 16
    draw.rounded_rectangle(
        [box_pad, box_pad, master_size - box_pad, master_size - box_pad],
        radius=24,
        fill=(27, 26, 26, 255)
    )

    # Measure ND text
    bbox = font.getbbox("ND")
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (master_size - tw) // 2 - bbox[0]
    ty = (master_size - th) // 2 - bbox[1]

    # Draw cutout letters in warm newsprint off-white (#fcecec)
    draw.text((tx, ty), "ND", font=font, fill=(252, 236, 236, 255))

    # Save multi-size ICO
    img.save("public/favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    print("Wrote public/favicon.ico")

    # Also generate a preview comparison image for the user (showing light and dark tab appearance)
    preview = Image.new("RGBA", (800, 320), (240, 240, 240, 255))
    p_draw = ImageDraw.Draw(preview)

    # Left: Light Tab Chrome simulation (#eaeaea background)
    p_draw.rectangle([0, 0, 400, 320], fill=(238, 236, 234, 255))
    p_draw.text((30, 25), "LIGHT TAB CHROME SIMULATION", fill=(80, 75, 75, 255))
    
    # 72x72 preview
    img_64 = img.resize((72, 72), Image.Resampling.LANCZOS)
    preview.paste(img_64, (50, 80), img_64)

    # 32x32 tab preview
    img_32 = img.resize((32, 32), Image.Resampling.LANCZOS)
    preview.paste(img_32, (160, 100), img_32)
    p_draw.text((205, 106), "Nithika Dias — Portfolio", fill=(40, 35, 35, 255))

    # 16x16 tab preview
    img_16 = img.resize((16, 16), Image.Resampling.LANCZOS)
    preview.paste(img_16, (160, 160), img_16)
    p_draw.text((188, 160), "16x16 standard browser tab size", fill=(100, 95, 95, 255))

    # Right: Dark Tab Chrome simulation (#202020 background)
    p_draw.rectangle([400, 0, 800, 320], fill=(32, 33, 36, 255))
    p_draw.text((430, 25), "DARK TAB CHROME SIMULATION", fill=(200, 195, 195, 255))

    # Dark mode inversion: light stamp block with dark cutout
    img_dark = Image.new("RGBA", (master_size, master_size), (0, 0, 0, 0))
    d_draw = ImageDraw.Draw(img_dark)
    d_draw.rounded_rectangle(
        [box_pad, box_pad, master_size - box_pad, master_size - box_pad],
        radius=24,
        fill=(244, 228, 228, 255)
    )
    d_draw.text((tx, ty), "ND", font=font, fill=(27, 26, 26, 255))

    # 72x72 dark preview
    img_dark_64 = img_dark.resize((72, 72), Image.Resampling.LANCZOS)
    preview.paste(img_dark_64, (450, 80), img_dark_64)

    # 32x32 dark tab preview
    img_dark_32 = img_dark.resize((32, 32), Image.Resampling.LANCZOS)
    preview.paste(img_dark_32, (560, 100), img_dark_32)
    p_draw.text((605, 106), "Nithika Dias — Portfolio", fill=(230, 225, 225, 255))

    # 16x16 dark tab preview
    img_dark_16 = img_dark.resize((16, 16), Image.Resampling.LANCZOS)
    preview.paste(img_dark_16, (560, 160), img_dark_16)
    p_draw.text((588, 160), "16x16 standard browser tab size", fill=(160, 155, 155, 255))

    preview_path = "/home/nithika/.gemini/antigravity/brain/c9939f2a-c3d5-4e9f-b54b-4f7fac000271/favicon_preview.png"
    preview.save(preview_path)
    print(f"Saved preview image to {preview_path}")

if __name__ == "__main__":
    build_svg_and_ico()

