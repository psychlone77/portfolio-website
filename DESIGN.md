# DESIGN.md — The Nithika Broadsheet Design System

This document is the canonical design reference for Nithika Dias's portfolio & blog. Any UI component, page layout, typography choice, or image asset added to this repository **must** follow these specifications.

---

## 1. Aesthetic Direction & Editorial Voice

- **Visual Metaphor**: 1970s/80s independent technical broadsheet, hacker zine, and vintage letterpress newspaper printed on warm rose-tinted newsprint.
- **Tactile Materiality**:
  - Visible **paper grain and fiber texture** across the entire viewport using a procedural SVG fractal-noise overlay (`.paper-texture`).
  - Crisp **1px solid ink rules** and **double-ruled masthead borders** (`border-double border-b-4`) separating columns and sections.
  - **Zero soft drop shadows or blurry glassmorphism**. Elevation is communicated strictly through solid ink borders (`1px solid var(--color-border)`) and hard offset press shadows (`3px 3px 0px var(--color-border)` on hover/interactive cards).
  - **Zero rounded pill corners on structural containers** (`border-radius: 0px`). Everything is cut like physical newsprint clippings and ink stamps.
- **Editorial Tone**:
  - **Informal, conversational, and first-person**. Write like an engineer chatting over coffee or writing a personal zine column—not a stiff third-person corporate resume.
  - Keep project and job blurbs punchy (1–3 sentences focusing on what was genuinely interesting to build or break), paired with scannable tech-stack stamps.

---

## 2. Color & Ink Tokens

The palette uses CSS custom properties in [`src/styles/global.css`](file:///home/nithika/Uni/Personal%20Projects/portfolio-website/src/styles/global.css) to switch seamlessly between **Light Print (Default)** and **Dark Press (`[data-theme="dark"]`)**.

| Token | Light Print (Newsprint) | Dark Press (Carbon Plate) | Purpose |
| :--- | :--- | :--- | :--- |
| `--color-background` | `#fcecec` | `#1b1a1a` | Primary newsprint canvas |
| `--color-surface` | `#f6e0e0` | `#242222` | Highlighted clipping boxes, code blocks, tags |
| `--color-primary` | `#111111` | `#fcecec` | Primary carbon ink (headings, body text, icons) |
| `--color-secondary` | `#4a4343` | `#cfc2c2` | Subtitles, datelines, secondary paragraphs |
| `--color-muted` | `#7a6f6f` | `#8a7f7f` | Captions, metadata, subtle dividers |
| `--color-border` | `#111111` | `#fcecec` | Structural newspaper rules, borders, hard shadows |
| `--color-rule-subtle` | `rgba(17, 17, 17, 0.22)` | `rgba(252, 236, 236, 0.22)` | Dashed internal column dividers |

---

## 3. Typography Hierarchy

We pair a high-contrast editorial serif for broadsheet headlines with a crisp technical monospace for body copy, metadata, and code.

- **Display / Headlines (`--font-display`)**: `"Playfair Display Variable", Georgia, Cambria, "Times New Roman", serif`
  - **Masthead / Hero Title (`h1`)**: `clamp(2.5rem, 5vw, 4rem)`, `font-weight: 700`, tight tracking (`-0.02em`), line-height `1.08`.
  - **Section Broadsheet Banner (`h2`)**: `1.5rem` – `1.75rem`, `font-weight: 700`, paired with a horizontal ink rule.
  - **Article / Card Headline (`h3`)**: `1.2rem` – `1.35rem`, `font-weight: 600`.
- **Body, Metadata & Code (`--font-mono`)**: `"IBM Plex Mono", monospace`
  - **Body Copy**: `0.9rem` (`14.4px`), line-height `1.7`, comfortable reading measure (`65ch` max for articles).
  - **Datelines, Issue Badges & Tags**: `0.75rem` (`12px`), uppercase tracking (`0.06em`), medium weight (`500`).
  - **Editorial Drop-Caps (`.drop-cap`)**: First paragraph of blog articles uses a `Playfair Display` 3-line float drop-cap (`font-size: 3.4rem`, `line-height: 0.85`).

---

## 4. Imagery & 1-Bit Ink-Print Pipeline

Full-color photographs and smooth gradients are **never** placed directly onto the page. All raster portraits, company logos, and blog illustrations must look like 1-bit newspaper ink prints:

1. **Conversion via Python CLI**:
   Use `.venv/bin/python scripts/ink_print.py` (or `bun run ink`) to convert source images into 1-bit RGBA PNGs where:
   - Ink pixels = `(0, 0, 0, 255)` (pure black)
   - Paper pixels = `(0, 0, 0, 0)` (100% transparent alpha so the underlying `.paper-texture` shows through)
2. **Supported Dithering Modes**:
   - `--mode bayer`: 8x8 Bayer ordered dithering (crosshatch retro computer-press texture; used for portraits & hero images).
   - `--mode halftone`: Classic angled newspaper dot matrix screen.
   - `--mode atkinson`: High-contrast error diffusion with crisp edge preservation (ideal for logos, diagrams, and stamps).
3. **Dark Mode Treatment for Portraits vs. Logos**:
   - **Portraits (`Hero.astro`)**: Kept un-inverted in Dark Mode on a fixed `#fcecec` newsprint backing (`bg-[#fcecec]`) so facial shadows and highlights never look like a photo negative.
   - **Logos & Stamps (`.ink-illustration`)**: 1-bit transparent organization logos use `.ink-illustration` so black ink inverts cleanly to `#fcecec` light ink in Dark Mode.

---

## 5. Layout & Component Patterns

- **Container**: Centered broadsheet container (`max-w-4xl mx-auto px-5 sm:px-8 py-8`).
- **Masthead (`Header.astro`)**:
  - Top metadata strip: Volume/Edition number, location weather/status quip, dynamic publication date, and `[ DARK_INK / LIGHT_PRINT ]` toggle.
  - Double-ruled navigation bar linking to `Front Page (/)`, `Dispatches (/blog)`, `Projects (/#projects)`, and `Contact`.
- **Clipping Cards (`.ink-card`)**:
  - `1px solid var(--color-border)` border, transparent paper background, subtle hover lift (`transform: translate(-2px, -2px)` with `box-shadow: 4px 4px 0 var(--color-border)`).
- **Stamp Badges (`.ink-stamp`)**:
  - Compact uppercase rectangular badges (`border: 1px solid var(--color-border)`, `px-2 py-0.5 text-xs font-medium`) used for tech stacks, dates, and award ranks (`1ST PLACE`, `GLOBAL 268TH`).

