---
title: "Converting Images to 1-Bit Newspaper Ink in Python"
description: "How the Python script in this repo uses Bayer ordered dithering, halftone dots, and Atkinson dithering to give photos and logos a newspaper print look."
pubDate: 2026-10-25
tags: ["python", "design", "frontend"]
draft: false
---

For this portfolio, I wanted a clean retro newspaper look rather than standard full-color cards. Putting regular color images on a textured background felt out of place, so I wrote a small Python script (`scripts/ink_print.py`) to convert photos and company logos into 1-bit dithered PNGs.

## Ink Pixels with Transparent Backgrounds

Instead of exporting black-and-white images with a solid white background, the script outputs RGBA PNGs with only two pixel values:

- **Ink pixel**: `RGBA(0, 0, 0, 255)`
- **Background pixel**: `RGBA(0, 0, 0, 0)`

Because the non-ink pixels are transparent, the page's background color and paper grain texture show straight through the image.

## Running the Script

The script runs inside the project's `.venv` virtual environment using `Pillow` and supports a few different dithering styles:

```bash
# 1. 8x8 Bayer ordered dithering (used on the profile photo)
bun run ink public/profile-image-2.jpg -o public/profile-image.png --mode bayer

# 2. 45-degree rotated halftone dot screen
bun run ink input.jpg -o public/output-halftone.png --mode halftone --dot-size 6

# 3. Atkinson error-diffusion dithering (works well on crests and logos)
bun run ink logo.png -o public/logos/stamp.png --mode atkinson
```

## Why Atkinson Dithering Works Well for Logos

Standard Floyd–Steinberg dithering diffuses 100% of the quantization error to neighboring pixels, which can leave noisy speckles around high-contrast edges. **Atkinson dithering** only propagates $\frac{6}{8}$ ($75\%$) of the error to adjacent pixels:

$$
I_{\text{new}}(x, y) = Q(I(x, y)), \quad e = \frac{I(x, y) - I_{\text{new}}(x, y)}{8}
$$

Dropping the remaining $25\%$ increases contrast along edges and keeps flat areas clean, which turned out to work well for converting detailed crests like the University of Moratuwa and Lyceum logos into small monochrome stamps.
