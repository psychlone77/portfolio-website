# Nithika Dias — Portfolio & Technical Dispatches

A retro 1980s broadsheet newspaper and indie zine portfolio website, built with **Astro v5**, **Tailwind CSS v4**, and an automated **Python 1-bit dithering pipeline**. Designed for physical tactile materiality, zero render-blocking requests, and a perfect **100/100/100/100** score on Google Lighthouse.

---

## Design Philosophy

- **Tactile Materiality**: Procedural 3D paper fiber relief (`feTurbulence` + `feDiffuseLighting`), full-viewport monochrome print grain (`mix-blend-mode: hard-light`), and letterpress ink bleed (`feDisplacementMap`) simulating ink capillary action into porous paper pulp.
- **Broadsheet Structure**: High-contrast editorial serif headlines paired with technical monospace body copy, sharp 1px ink rules, double-ruled masthead borders, and hard press shadows (`3px 3px 0px var(--color-border)`). Zero blurry drop shadows, zero rounded cards.
- **Editorial Voice**: Informal, conversational, and first-person developer dispatches rather than stiff corporate resume language.
- **Dual Theme Support**: Light Print (warm newsprint `#fcecec`) and Dark Press (carbon plate `#1b1a1a`) with seamless client-side persistence and zero-flash View Transitions.

---

## Features

- **100/100/100/100 on Google Lighthouse**:
  - Inlined critical CSS (`build.inlineStylesheets: "always"`) eliminating 400ms render-blocking request delays on mobile 4G.
  - Preloaded WOFF2 font subsets via Vite asset hashing queries (`?url`) locking Cumulative Layout Shift (CLS) to a rock-solid `0.000`.
  - Scoped heavy CSS (`katex.min.css`) strictly to mathematical blog posts to keep the homepage featherlight.
  - Eager high-priority preloading and explicit dimensions for Largest Contentful Paint (LCP) assets.
- **1-Bit Ink-Print Dithering Pipeline (`scripts/ink_print.py`)**:
  - Custom Python/Pillow CLI converting color photos and logos into 1-bit transparent images (ink = black, paper = transparent alpha).
  - Preserves paper texture and grain through the gaps between ink dots.
  - Supports **Bayer 8×8 ordered dithering** (portraits), **Halftone dot screens**, and **Atkinson error diffusion** (razor-sharp university crests and logos).
  - Lossless WebP output saving ~63% bandwidth over PNG.
- **Markdown Blog & Mathematical Typesetting**:
  - Astro v5 Content Layer API with Zod schema validation.
  - Mathematical equations via KaTeX (`remark-math` and `rehype-katex`).
  - Automatic responsive table container wrapper (`satteriTablePlugin`) with broadsheet borders, alternating newsprint tints, and touch scrolling.
  - Syntax highlighting via Shiki with dual-theme GitHub Light/Dark bindings.
- **Glitch-Free View Transitions (`ClientRouter`)**:
  - Stationary masthead and footer across navigations with a tactile 28px content ink-fade.
  - Theme state pre-synchronization (`astro:before-swap`) preventing dark-mode flashes during page hops.
  - Persistent SVG texture overlays (`transition:persist`) preventing shader recalculation hitching.
- **Accessible Mobile Experience**:
  - Mobile sections accordion with ARIA attributes (`aria-expanded`, `aria-controls`), focus management, and `Escape` key trapping.
  - High-contrast tokens meeting WCAG AAA ratios (11.8:1).

---

## Project Structure

```plaintext
portfolio-website/
├── public/
│   ├── logos/                  # 1-bit transparent organization WebP stamps
│   ├── favicon.svg             # Adaptive Playfair Display SVG favicon
│   ├── favicon.ico             # Multi-resolution fallback favicon
│   └── profile-image.webp      # 1-bit Bayer-dithered LCP avatar
├── scripts/
│   └── ink_print.py            # Python 1-bit dithering script (Bayer, Halftone, Atkinson)
├── src/
│   ├── components/
│   │   ├── Header.astro        # Masthead, dynamic date, nav rules & mobile menu
│   │   ├── Hero.astro          # Headline, bio, dithered avatar & social links
│   │   ├── Section.astro       # Broadsheet section wrapper with ink rules
│   │   └── ExperienceCard.astro# Editorial job clipping with 1-bit stamps
│   ├── content/
│   │   └── blog/               # Markdown dispatches & engineering articles
│   ├── data/
│   │   └── portfolio.ts        # Typed portfolio experiences, awards, & bio
│   ├── layouts/
│   │   └── Layout.astro        # Base broadsheet layout, SVG filters & transition hooks
│   ├── pages/
│   │   ├── index.astro         # Front page
│   │   └── blog/
│   │       ├── index.astro     # Dispatches catalog
│   │       └── [...slug].astro # Individual markdown post reader with KaTeX
│   ├── styles/
│   │   └── global.css          # Tailwind CSS v4 broadsheet tokens & typography
│   └── content.config.ts       # Astro Content Layer blog schema
├── astro.config.mjs            # Astro config, Satteri plugins & build options
└── package.json
```

---

## Commands

| Command | Action |
| :--- | :--- |
| `bun install` | Install JavaScript dependencies |
| `bun run dev` | Start local development server at `http://localhost:4321` |
| `bun run build` | Compile static production site to `./dist/` |
| `bun run preview` | Preview production build locally |
| `bun run lint` | Run `astro check` diagnostics and `eslint .` |
| `bun run ink <input> -o <out.webp> --mode <mode>` | Convert an image to 1-bit newsprint WebP |

### 1-Bit Image Processing Examples

```bash
# 1. 8x8 Bayer ordered dithering (portraits & photos)
bun run ink input.jpg -o public/profile-image.webp --mode bayer

# 2. Atkinson error diffusion (logos, crests, and emblems)
bun run ink logo.png -o public/logos/crest.webp --mode atkinson

# 3. 45-degree angled newspaper halftone dots
bun run ink photo.jpg -o public/halftone.webp --mode halftone --dot-size 6
```

---

## Tech Stack

- **Framework**: [Astro v5](https://astro.build/) (Static Site Generation + Content Layer API + ClientRouter)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/) with custom broadsheet CSS variables
- **Typography**: [Playfair Display Variable](https://fontsource.org/fonts/playfair-display) (display/headlines) & [IBM Plex Mono](https://fontsource.org/fonts/ibm-plex-mono) (body, code, metadata)
- **Math**: [KaTeX](https://katex.org/) (`remark-math` + `rehype-katex`)
- **Image Processing**: Python 3 (`.venv`) with [Pillow](https://python-pillow.org/)
- **UI Components**: Astro components (`.astro`) & React 19 (`@astrojs/react`)
