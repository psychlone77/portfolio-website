---
title: "Building a Newspaper Portfolio with 1-Bit Dithering"
description: "How I built a retro broadsheet portfolio with Python 1-bit dithering, procedural 3D paper grain, and SVG letterpress ink bleed."
pubDate: 2026-10-25
updatedDate: 2026-10-27
tags: ["design", "python", "svg", "frontend"]
draft: false
---

Most developer portfolios look practically identical. You usually get a dark mode background, purple and cyan gradient badges, soft blurred glassmorphism cards, and a razor-sharp 4K headshot.

I wanted something completely different. I wanted my site to feel like a tactile, tangible physical object—specifically, a weathered 1980s broadsheet newspaper or an indie printing press zine.

```plaintext
+-------------------------------------------------------+
|  THE DAILY DISPATCH            Vol. 1 -- Oct 2026     |
+=======================================================+
|  +---------+   HEADLINE: RETRO INK ON NEWSPRINT       |
|  | * . * * |                                          |
|  | . * . * |   Real newsprint isn't smooth plastic.   |
|  | * * . . |   It has wood fibers, uneven ink dots,   |
|  +---------+   and rough, bleeding edges.             |
+-------------------------------------------------------+
```

When I first started building this, I thought it would be easy: pick a warm yellowish paper background color, pick a vintage serif font, and call it a day.

It looked awful.

The page didn't look like a newspaper at all. It looked like crisp digital vector text and high-res RGB photos unceremoniously pasted onto a flat beige webpage. To make it genuinely feel like ink printed on physical paper, I had to solve three distinct engineering problems:

1. **Images:** Standard photos have millions of colors. Real newspapers only have a single color of black ink.
2. **Paper:** Real paper has tactile texture—fiber bumps, creases, and light catching the folds. A flat CSS `#fcecec` background color feels dead.
3. **Typography:** Mathematical vector fonts rendered by browsers have perfectly sharp edges. Real ink pressed into porous paper fibers bleeds slightly at the boundaries.

Here is the breakdown of how I solved each of these problems using Python image processing and browser-native SVG filters.

---

## 1. Turning Photos into Pure Ink (1-Bit Dithering)

In computer graphics, a standard color photograph stores 24 bits per pixel: 8 bits for Red, 8 for Green, and 8 for Blue ($256 \times 256 \times 256 \approx 16.7\text{ million colors}$).

A newspaper printing press, however, has no grey ink. It only has black ink and blank paper. In digital terms, that is a **1-bit image**: every pixel is either a `1` (ink) or a `0` (paper).

### The Naive Mistake: Hard Thresholding

If you are a first-year CS student, your first instinct to convert a photo to black and white might look like this:

```python
# Convert to grayscale (0 = black, 255 = white)
gray_pixel = 0.299 * r + 0.587 * g + 0.114 * b

# Simple cutoff threshold
if gray_pixel < 128:
    output_pixel = 0   # Black ink
else:
    output_pixel = 255 # White paper
```

This is called **hard thresholding**, and the result on human faces is terrifying:

```plaintext
Original Gradient:       [ 10% | 30% | 50% | 70% | 90% ]
Hard Threshold (< 50%):  [  0  |  0  |  1  |  1  |  1  ]
                         (All gentle shading is wiped out)
```

Anything slightly darker than medium gray becomes a solid black puddle, and anything slightly lighter turns completely white. All shading, gradients, and subtle facial features disappear.

### How Dithering Works

To preserve shades of gray without actual gray ink, printers use **dithering**. Dithering exploits a quirk of human vision: when tiny black dots are placed close together on a bright background, your eyes and brain blend them together, perceiving smooth shades of gray.

```plaintext
Dark Shadow (75% ink):   [ * * * . ]
Midtone Gray (50% ink):  [ * . * . ]
Bright Light (25% ink):  [ . . * . ]
Paper White (0% ink):    [ . . . . ]
```

In the Python script I wrote for this site (`scripts/ink_print.py`), I implemented two primary dithering algorithms depending on the type of asset: **Bayer Ordered Dithering** for portraits, and **Atkinson Error Diffusion** for university crests and logos.

### Technique A: Bayer Ordered Dithering (For Portraits)

For my profile photo, I wanted a uniform, crosshatch press look reminiscent of vintage Apple Macintosh graphics and classic newspaper prints. I used **Bayer ordered dithering**.

Instead of comparing every pixel to a fixed threshold like `128`, we compare each pixel $(x, y)$ against a repeating grid of spatial thresholds known as the **Bayer Matrix**. For an $8 \times 8$ matrix, the formula cycles through 64 distinct threshold values:

```plaintext
Repeating 4x4 Bayer Threshold Concept:
+----+----+----+----+
|  0 |  8 |  2 | 10 |  <- Scaled from 0 to 255 across
+----+----+----+----+     the grid
| 12 |  4 | 14 |  6 |
+----+----+----+----+
|  3 | 11 |  1 |  9 |
+----+----+----+----+
| 15 |  7 | 13 |  5 |
+----+----+----+----+
```

In Python, the loop is lightning fast because it only requires coordinate modulo operations:

```python
# scripts/ink_print.py
def dither_bayer(width: int, height: int, luminance_bytes: bytes) -> bytearray:
    mask = bytearray(width * height)
    idx = 0
    for y in range(height):
        bayer_row = BAYER_8X8[y & 7]  # y mod 8
        for x in range(width):
            pixel_val = luminance_bytes[idx]
            # If the pixel is darker than the local threshold, print ink!
            if pixel_val < 245 and pixel_val < bayer_row[x & 7]:
                mask[idx] = 1  # 1 = Ink
            idx += 1
    return mask
```

Because each pixel is decided purely by its coordinates without depending on its neighbors, Bayer dithering produces a clean, structured dot pattern that holds its shape even when scaled.

### Technique B: Atkinson Dithering (For Logos and Crests)

When I tried Bayer dithering on intricate university crests (like the University of Moratuwa coat of arms), the crosshatch pattern broke the fine line art.

Standard **Floyd–Steinberg** error diffusion wasn't great either. Floyd–Steinberg takes the rounding error from deciding a pixel and distributes $100\%$ of it to neighboring pixels. On small graphics with sharp contrast, that $100\%$ error propagation causes "dirty" speckles and worms in plain white areas.

Bill Atkinson (one of the original engineers on the Apple Macintosh team in the 1980s) came up with a brilliant tweak: **propagate only $\frac{6}{8}$ ($75\%$) of the error to neighbors and discard the remaining $25\%$**.

$$e = \frac{\text{Pixel}_{\text{original}} - \text{Pixel}_{\text{quantized}}}{8}$$

The error is distributed across 6 neighboring pixels:

```plaintext
           [ Current Pixel ] -> (Right +1): +e -> (Right +2): +e
 (Down-Left -1): +e -> (Down): +e -> (Down-Right +1): +e
                       (Down +2): +e
```

Dropping that extra $25\%$ of error acts like a high-pass filter. It keeps flat background areas clean white while keeping letter outlines and fine emblems crisp:

```python
# scripts/ink_print.py
thresh_val = int(threshold * 255)
for y in range(height):
    for x in range(width):
        idx = y * width + x
        old_val = buffer[idx]
        new_val = 0.0 if old_val < thresh_val else 255.0
        mask[idx] = 1 if old_val < thresh_val else 0

        # Diffuse 6/8ths of the quantization error
        err = (old_val - new_val) / 8.0
        if x + 1 < width: buffer[idx + 1] += err
        if x + 2 < width: buffer[idx + 2] += err
        if y + 1 < height:
            if x - 1 >= 0: buffer[idx + width - 1] += err
            buffer[idx + width] += err
            if x + 1 < width: buffer[idx + width + 1] += err
        if y + 2 < height:
            buffer[idx + 2 * width] += err
```

### The Alpha Channel Trick & WebP Savings

Traditional black-and-white graphics output ink as black (`RGB(0, 0, 0)`) and paper as white (`RGB(255, 255, 255)`).

If you put a white box on top of textured paper, the illusion shatters immediately:

```plaintext
[ WRONG: Solid White Box ]       [ RIGHT: Transparent Alpha ]
+-------------------------+     +-------------------------+
| Paper Grain Background  |     | Paper Grain Background  |
|   +-----------------+   |     |   .  *  *  .  .  *      |
|   | [SOLID WHITE]   |   |     |    *   *   *    *       |
|   |  *  *  .  *     |   |     |   (Paper grain shows    |
|   +-----------------+   |     |    between ink dots)    |
+-------------------------+     +-------------------------+
```

Instead of white pixels, the script creates **transparent pixels**:

- **Ink pixels**: `RGBA(0, 0, 0, 255)`
- **Paper pixels**: `RGBA(0, 0, 0, 0)` (Alpha = 0)

Because non-ink pixels are fully transparent, the real browser paper texture, creases, and background color show through the gaps between the dots!

Furthermore, converting these images from 32-bit PNGs to lossless `.webp` using Python (`Pillow`) saved **~63% of the bandwidth**:

- Profile avatar: $45\text{ KiB} \rightarrow 16.4\text{ KiB}$
- University & company logos: $\approx 12\text{ KiB} \rightarrow 3.5\text{ KiB}$ each

---

## 2. The "Too-Clean Digital Text" Problem (SVG Ink Bleed)

Once the photos looked like newspaper clippings, an even weirder problem showed up: the text looked fake.

In a physical printing press, metal lead type coated in oily ink is pressed firmly against porous, fibrous paper pulp. Under pressure, capillary action sucks wet ink into micro-crevices in the paper fibers. If you look at a real newspaper through a magnifying glass, the edges of letters aren't straight vectors—they are slightly rough, wavy, and bled into the paper.

In a web browser, fonts are rendered with mathematical Bézier curves. They are too sharp. They looked like stickers hovering above the paper.

```plaintext
Digital Vector (Too clean):   |---|
                              |   |  (Perfect, sterile, digital lines)
                              |---|

Letterpress Bleed (Tactile):  |~-~|
                              {~  |  (Ink bleeding into microscopic fibers)
                              |~_~}
```

### Fixing It with Native SVG Filters

I didn't want to use canvas or external image assets for text. Instead, I built a procedural SVG filter pipeline using `<feTurbulence>` and `<feDisplacementMap>` inside `Layout.astro`.

Here is the concept:

1. **Generate Noise:** `<feTurbulence>` creates a high-frequency Perlin noise texture.
2. **Displace Coordinates:** `<feDisplacementMap>` takes that noise texture and uses its color values as $(x, y)$ coordinate offsets, shifting the outline of the letters by fractions of a pixel.

```xml
<!-- src/layouts/Layout.astro -->
<svg class="hidden" aria-hidden="true">
  <defs>
    <!-- Ink-Bleed Filter for Display Headlines and Section Rules -->
    <filter id="ink-bleed" x="-20%" y="-35%" width="140%" height="170%">
      <!-- 1. Low-frequency line wobble (uneven press pressure) -->
      <feTurbulence
        type="fractalNoise"
        baseFrequency="0.045 0.065"
        numOctaves="3"
        seed="5"
        result="lineWobble" />

      <!-- 2. High-frequency fiber edge (ink bleeding into paper grains) -->
      <feTurbulence
        type="turbulence"
        baseFrequency="0.35"
        numOctaves="2"
        seed="11"
        result="fiberEdge" />

      <!-- 3. Displace letters by the wobble -->
      <feDisplacementMap
        in="SourceGraphic"
        in2="lineWobble"
        scale="1.4"
        xChannelSelector="R"
        yChannelSelector="G"
        result="wobbled" />

      <!-- 4. Displace again by fiber edge -->
      <feDisplacementMap
        in="wobbled"
        in2="fiberEdge"
        scale="0.7"
        xChannelSelector="R"
        yChannelSelector="B" />
    </filter>
  </defs>
</svg>
```

Applying this in CSS is simple:

```css
/* src/styles/global.css */
h1, h2, .newspaper-headline {
  filter: url(#ink-bleed);
}

.newspaper-rule-double, .newspaper-rule-single {
  filter: url(#ink-bleed);
}
```

Instantly, headlines and horizontal divider rules looked like they were stamped onto the page by a mechanical press.

### The CSS Containing Block Trap

While implementing this, I ran into a subtle CSS bug that every frontend developer should know:

> **CSS Spec Rule:** When you apply a `filter`, `transform`, or `perspective` to an element, the browser turns that element into a new **containing block** and **stacking context** for all descendants—even those with `position: fixed` or `position: absolute`!

Initially, I had lazily slapped `filter: url(#ink-bleed)` onto an entire layout card wrapper. Suddenly, absolute links and mobile dropdown menus inside that card stopped positioning relative to the viewport and were trapped inside the card boundary!

**The fix:** Never apply SVG displacement filters to layout wrappers or interactive container tags. Apply them directly to terminal typography nodes (`h1`, `h2`, `p`, `hr`, `.ink-bleed`) or inline spans.

---

## 3. Procedural 3D Paper (Zero-Kilobyte Texture)

Many retro websites achieve paper textures by downloading a $2\text{ MB}$ seamless JPEG photo of crumpled parchment. That bloats page weight, slows down mobile devices, and creates visible repeating tiles.

Instead, this site generates its paper relief **procedurally using the browser GPU**:

```plaintext
[ feTurbulence (Noise) ] ---> [ Heightmap of Paper Bumps ]
                                       |
                                       v
[ Directional Light (Azimuth 128°, Elevation 45°) ]
                                       |
                                       v
                     [ 3D Shaded Creases & Highlights ]
```

```xml
<!-- src/layouts/Layout.astro -->
<filter id="newspaper-crumple-relief" x="0%" y="0%" width="100%" height="100%">
  <!-- Large folds and creases -->
  <feTurbulence
    type="fractalNoise"
    baseFrequency="0.008 0.012"
    numOctaves="4"
    seed="1"
    result="macroCrumple" />

  <!-- Fine paper pulp bumps -->
  <feTurbulence
    type="turbulence"
    baseFrequency="0.045 0.055"
    numOctaves="4"
    seed="3"
    result="fiberBumps" />

  <!-- Combine them into a single surface heightmap -->
  <feBlend mode="multiply" in="macroCrumple" in2="fiberBumps" result="combinedSurface" />

  <!-- Illuminate the surface with a virtual grazing lamp! -->
  <feDiffuseLighting
    in="combinedSurface"
    lighting-color="#ffffff"
    surfaceScale="4.5"
    diffuseConstant="1.05"
    result="litPaper">
    <feDistantLight azimuth="128" elevation="45" />
  </feDiffuseLighting>
</filter>
```

By computing lighting with `<feDiffuseLighting>` and `<feDistantLight>`, the browser calculates real Lambertian diffuse reflections. When you scroll, subtle shadows and highlights track across the page just like sunlight hitting folded newsprint on a wooden desk.

Best of all? **The network transfer size is 0 bytes.** It is generated purely by code.

---

## 4. Full-Screen Print Grain Overlay

To tie the typography, 1-bit photos, and 3D paper together into a cohesive visual plane, I added an SVG grain layer fixed over the viewport with CSS:

```css
.screen-grain-overlay {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 9999;
  opacity: 0.27;
  mix-blend-mode: hard-light;
}
```

The key detail is `mix-blend-mode: hard-light`.

Unlike `multiply` (which only darkens) or `screen` (which only lightens), `hard-light` blends relative to $50\%$ gray:

- Bright paper areas receive subtle dark specks.
- Solid black ink letters receive faint paper-colored micro-pores.

It mimics the microscopic imperfections of cheap, recycled newsprint without impacting clickability (`pointer-events: none`).

---

## What We Learned

Building a retro aesthetic on the modern web isn't about slapping retro fonts onto a page; it's about understanding how physical media behaves and translating those physical rules into code:

1. **Physical printing is 1-bit:** Use algorithms like Bayer and Atkinson dithering to simulate tone, and use alpha-channel transparency so your paper texture breathes through the ink.
2. **Ink spreads into paper:** Perfect vector text feels sterile; procedural SVG displacement filters introduce the organic bleed of a mechanical press.
3. **Procedural math beats large bitmap images:** SVG lighting filters (`feDiffuseLighting`) can simulate 3D paper folds on the GPU for $0$ network bytes.

In the next post, I'll dive into the performance side: how we combined all these heavy SVG filters and custom fonts while still achieving a **flawless 100/100/100/100 on Google Lighthouse**.
