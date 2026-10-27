#!/usr/bin/env python3
"""
ink_print.py — Retro Newspaper 1-Bit Ink Print Converter

Converts any input image or logo into a 1-bit newspaper ink-print PNG where:
  - Ink pixels are pure black RGBA (0, 0, 0, 255)
  - Paper pixels are fully transparent RGBA (0, 0, 0, 0) (or opaque paper if --opaque-bg is passed)

Supported Modes:
  - bayer     : 8x8 Bayer ordered dithering (retro crosshatch press texture, matches profile-image.png)
  - halftone  : Classic angled 45-degree newspaper halftone dot screen
  - atkinson  : High-contrast Atkinson error-diffusion dithering (crisp edges, great for logos/stamps)
  - threshold : Clean 1-bit ink stamp thresholding (ideal for monochrome/vector-style company logos)

Usage:
  .venv/bin/python scripts/ink_print.py input.jpg -o public/output.png --mode bayer
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps


# 8x8 Bayer Ordered Dithering Matrix (0..63 scaled to 0..255)
BAYER_8X8: list[list[int]] = [
    [int((v + 0.5) * 255 / 64) for v in row]
    for row in [
        [0, 32, 8, 40, 2, 34, 10, 42],
        [48, 16, 56, 24, 50, 18, 58, 26],
        [12, 44, 4, 36, 14, 46, 6, 38],
        [60, 28, 52, 20, 62, 30, 54, 22],
        [3, 35, 11, 43, 1, 33, 9, 41],
        [51, 19, 59, 27, 49, 17, 57, 25],
        [15, 47, 7, 39, 13, 45, 5, 37],
        [63, 31, 55, 23, 61, 29, 53, 21],
    ]
]


def preprocess_image(
    img: Image.Image,
    max_width: int | None = None,
    contrast: float = 1.25,
    brightness: float = 1.05,
    sharpness: float = 1.2,
    invert_input: bool = False,
) -> tuple[int, int, bytes, bytes]:
    """
    Loads an image, composites alpha onto white, adjusts contrast/brightness,
    and returns (width, height, luminance_bytes, alpha_bytes).
    """
    rgba = img.convert("RGBA")

    if max_width and rgba.width > max_width:
        ratio = max_width / float(rgba.width)
        new_height = max(1, int(round(rgba.height * ratio)))
        rgba = rgba.resize((max_width, new_height), Image.Resampling.LANCZOS)

    alpha_bytes = rgba.getchannel("A").tobytes()

    # Composite onto white background before grayscale conversion
    white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, rgba).convert("L")

    if invert_input:
        composited = ImageOps.invert(composited)

    if brightness != 1.0:
        composited = ImageEnhance.Brightness(composited).enhance(brightness)
    if contrast != 1.0:
        composited = ImageEnhance.Contrast(composited).enhance(contrast)
    if sharpness != 1.0:
        composited = ImageEnhance.Sharpness(composited).enhance(sharpness)

    return rgba.width, rgba.height, composited.tobytes(), alpha_bytes


def dither_bayer(width: int, height: int, lum: bytes) -> bytearray:
    """
    Returns bytearray mask (1 = ink, 0 = paper) using 8x8 Bayer ordered dithering.
    """
    mask = bytearray(width * height)
    idx = 0
    for y in range(height):
        bayer_row = BAYER_8X8[y & 7]
        for x in range(width):
            val = lum[idx]
            if val < 245 and val < bayer_row[x & 7]:
                mask[idx] = 1
            idx += 1
    return mask


def dither_atkinson(width: int, height: int, lum: bytes, threshold: float = 0.5) -> bytearray:
    """
    Atkinson error-diffusion dithering (propagates 6/8 of quantization error).
    Produces high-contrast vintage Macintosh / zine style prints.
    """
    thresh_val = int(threshold * 255)
    buf = [float(b) for b in lum]
    mask = bytearray(width * height)

    for y in range(height):
        row_offset = y * width
        for x in range(width):
            idx = row_offset + x
            old = buf[idx]
            if old < thresh_val:
                new = 0.0
                mask[idx] = 1
            else:
                new = 255.0
            err = (old - new) / 8.0
            if x + 1 < width:
                buf[idx + 1] += err
            if x + 2 < width:
                buf[idx + 2] += err
            if y + 1 < height:
                next_row = idx + width
                if x - 1 >= 0:
                    buf[next_row - 1] += err
                buf[next_row] += err
                if x + 1 < width:
                    buf[next_row + 1] += err
            if y + 2 < height:
                buf[idx + 2 * width] += err
    return mask


def dither_halftone(
    width: int, height: int, lum: bytes, dot_size: float = 6.0, angle_deg: float = 45.0
) -> bytearray:
    """
    Rotated newspaper halftone dot screen.
    Darker regions produce larger circular ink dots on a rotated grid.
    """
    mask = bytearray(width * height)
    theta = math.radians(angle_deg)
    cos_t = math.cos(theta) / dot_size
    sin_t = math.sin(theta) / dot_size
    inv_max_dist = 1.0 / math.sqrt(0.5)

    idx = 0
    for y in range(height):
        yc = y * cos_t
        ys = y * sin_t
        for x in range(width):
            val = lum[idx]
            if val < 242:
                u = x * cos_t - ys
                v = x * sin_t + yc
                du = u - round(u)
                dv = v - round(v)
                dist = math.sqrt(du * du + dv * dv) * inv_max_dist
                darkness = (255 - val) / 255.0
                if darkness > dist:
                    mask[idx] = 1
            idx += 1
    return mask


def dither_threshold(width: int, height: int, lum: bytes, threshold: float = 0.55) -> bytearray:
    """
    Crisp 1-bit ink threshold for clean vector-like logos and stamps.
    """
    thresh_val = int(threshold * 255)
    mask = bytearray(width * height)
    for i, val in enumerate(lum):
        if val < thresh_val:
            mask[i] = 1
    return mask


def build_rgba_output(
    width: int,
    height: int,
    ink_mask: bytearray,
    alpha_bytes: bytes,
    opaque_bg: bool = False,
    bg_color: tuple[int, int, int] = (252, 236, 236),
) -> Image.Image:
    """
    Converts ink_mask into an RGBA Image:
      - Ink pixels   -> (0, 0, 0, 255)
      - Paper pixels -> (0, 0, 0, 0)
    """
    out = bytearray(width * height * 4)
    for i in range(width * height):
        base = i * 4
        is_ink = ink_mask[i] == 1 and alpha_bytes[i] > 38
        if is_ink:
            out[base] = 0
            out[base + 1] = 0
            out[base + 2] = 0
            out[base + 3] = 255
        elif opaque_bg:
            out[base] = bg_color[0]
            out[base + 1] = bg_color[1]
            out[base + 2] = bg_color[2]
            out[base + 3] = 255

    return Image.frombytes("RGBA", (width, height), bytes(out))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert images or logos into 1-bit transparent newspaper ink prints."
    )
    parser.add_argument("input", type=Path, help="Input image path")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Output PNG path",
    )
    parser.add_argument(
        "--mode",
        choices=["bayer", "halftone", "atkinson", "threshold"],
        default="bayer",
        help="Dithering / ink screen algorithm (default: bayer)",
    )
    parser.add_argument(
        "--max-width",
        type=int,
        default=700,
        help="Resize image to maximum width before dithering (0 to disable, default: 700)",
    )
    parser.add_argument(
        "--contrast",
        type=float,
        default=1.25,
        help="Contrast multiplier before dithering (default: 1.25)",
    )
    parser.add_argument(
        "--brightness",
        type=float,
        default=1.05,
        help="Brightness multiplier before dithering (default: 1.05)",
    )
    parser.add_argument(
        "--dot-size",
        type=float,
        default=6.0,
        help="Halftone dot grid spacing in pixels (default: 6.0)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.55,
        help="Threshold value (0..1) for atkinson/threshold modes (default: 0.55)",
    )
    parser.add_argument(
        "--invert-input",
        action="store_true",
        help="Invert input luminance before converting (useful for white-on-dark logos)",
    )
    parser.add_argument(
        "--opaque-bg",
        action="store_true",
        help="Fill paper pixels with opaque #fcecec instead of transparent alpha",
    )

    args = parser.parse_args()

    img = Image.open(args.input)
    width, height, lum, alpha_bytes = preprocess_image(
        img,
        max_width=args.max_width if args.max_width > 0 else None,
        contrast=args.contrast,
        brightness=args.brightness,
        invert_input=args.invert_input,
    )

    if args.mode == "bayer":
        ink_mask = dither_bayer(width, height, lum)
    elif args.mode == "halftone":
        ink_mask = dither_halftone(width, height, lum, dot_size=args.dot_size)
    elif args.mode == "atkinson":
        ink_mask = dither_atkinson(width, height, lum, threshold=args.threshold)
    else:
        ink_mask = dither_threshold(width, height, lum, threshold=args.threshold)

    out_img = build_rgba_output(width, height, ink_mask, alpha_bytes, opaque_bg=args.opaque_bg)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    out_img.save(args.output, format="PNG")
    print(f"[ink_print] Saved {args.mode} ink print -> {args.output} ({out_img.width}x{out_img.height})")


if __name__ == "__main__":
    main()

