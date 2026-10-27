---
title: "Cutting milliseconds: tuning this site for a perfect Lighthouse score"
description: "How I optimized this retro broadsheet website to score a flawless 100/100/100/100 on Google Lighthouse: inlining critical CSS, preloading font waterfalls, lossless WebP, and zero-flash View Transitions."
pubDate: 2026-10-27
tags: ["performance", "astro", "web-vitals", "accessibility"]
draft: false
---

Whenever developers talk about website performance, you often hear advice like "use a CDN", "minify your JavaScript", or "compress your images".

That advice is fine for getting a site to an 85 or 90 on Google Lighthouse. But if you want to hit a **flawless 100/100/100/100** across Performance, Accessibility, Best Practices, and SEO—especially when Lighthouse tests on an emulated low-end mobile phone (Moto G Power) throttled to a Slow 4G connection—every single millisecond and byte matters.

```plaintext
+---------------------------------------------------------+
|                  LIGHTHOUSE AUDIT REPORT                |
+=========================================================+
|  [ 100 ]        [ 100 ]         [ 100 ]         [ 100 ] |
| Performance  Accessibility   Best Practices       SEO   |
+---------------------------------------------------------+
```

When I first ran Lighthouse on this portfolio, the results were respectable: Accessibility, Best Practices, and SEO were already at 100, but **Performance was stuck at 98**.

98 is good, but looking closely at the audit revealed real bottlenecks:

- A render-blocking CSS request was costing ~400 ms of delay.
- The browser was chaining network requests for web fonts.
- Image transfer sizes were higher than necessary.

Here is the story of how I diagnosed each bottleneck, how the browser engine actually handles these resources, and the exact steps I took to reach 100.

---

## 1. The Render-Blocking CSS Trap (Why Inlining 8 KiB Saved 400 ms)

To understand why my site scored 98 initially, we need to look at how a browser paints pixels on your screen.

When a browser downloads an HTML file, it parses it from top to bottom. If it encounters a line like this in the `<head>`:

```html
<link rel="stylesheet" href="/_astro/Header.CGqCsfX8.css" />
```

The browser hits an emergency brake.

Because CSS defines colors, layouts, and font sizes, the browser refuses to render any HTML below that tag until the CSS file is completely downloaded and parsed. If it didn't wait, you would see an ugly unstyled flash of raw HTML before the styles applied (known as Flash of Unstyled Content, or FOUC).

This is why stylesheets are called **Render-Blocking Resources**.

```plaintext
TRADITIONAL EXTERNAL CSS WATERFALL:
Browser receives HTML  [================>]
Finds <link rel="stylesheet">            |
Round-Trip: DNS + TLS + HTTP Request     +-----> [=== 400 ms wait ===]
CSS arrives & parses                                                  |
First Contentful Paint (FCP)                                          v (Page finally renders!)
```

On a fast fiber connection at home, downloading an $8\text{ KiB}$ stylesheet takes $15\text{ ms}$. But on mobile with a high Round Trip Time (RTT), setting up that second HTTP request can take **$300\text{ ms}$ to $400\text{ ms}$**!

### The Fix: Inlining Stylesheets in Astro

Lighthouse gave me a direct warning:
> *Requests are blocking the page's initial render. Est savings of 400 ms.*

The entire production stylesheet for my site (compiled with Tailwind CSS v4) was only about $8\text{ KiB}$ gzipped. Making the phone pause and fire an entirely separate network request just to fetch $8\text{ KiB}$ was silly.

In Astro v5, you can fix this with a single configuration flag in `astro.config.mjs`:

```javascript
// astro.config.mjs
export default defineConfig({
  build: {
    // Inlines all stylesheets directly into the HTML <head>
    inlineStylesheets: "always",
  },
  // ...
});
```

Instead of generating an external `<link rel="stylesheet">`, Astro injects the CSS directly inside a `<style>` block in the initial HTML document.

```plaintext
INLINED CSS WATERFALL:
Browser receives HTML (containing <style>) [================>]
Styles are ALREADY present!                                  |
First Contentful Paint (FCP)                                 v (Page renders immediately!)
```

**The Result:** The render-blocking request completely vanished. The browser painted the page immediately upon receiving the first packet of HTML, saving $\approx 400\text{ ms}$ on mobile 4G.

---

## 2. Flattening the Font Waterfall (Zero Layout Shift)

Typography is the core of this retro broadsheet newspaper aesthetic. The site uses two primary typefaces:

- **Playfair Display Variable** for headlines and title broadsheets
- **IBM Plex Mono** (weights 400, 500, and 600) for body copy, timestamps, and metadata

The naive way to load custom web fonts is via standard CSS:

```css
@font-face {
  font-family: "IBM Plex Mono";
  font-weight: 500;
  src: url("/fonts/ibm-plex-mono.woff2") format("woff2");
}
```

Here is the trap: **Browsers are lazy by default.**

When the browser parses `@font-face` in your CSS, it does *not* download the font file immediately. It waits until the DOM tree is built, matches CSS selectors, and finds an element on the screen that actually uses that font family.

This creates a nasty 3-step waterfall:

```plaintext
NAIVE FONT LOADING CHAIN:
1. HTML Download  [========>]
2. CSS Download             [========>]
3. Font Discovered                    [========>] Text finally appears!
```

If the font takes too long to load, one of two bad things happens:

1. **FOIT (Flash of Invisible Text):** The browser leaves the text completely blank until the font arrives.
2. **FOUT (Flash of Unstyled Text) & CLS:** The browser renders a fallback font (like Times New Roman), and when the custom font arrives $200\text{ ms}$ later, the text shifts size, jumping page layout around.

Lighthouse tracks this with **Cumulative Layout Shift (CLS)**. Even a tiny jump lowers your score.

### The Fix: Preloading WOFF2 Subsets with Astro & Vite

To eliminate the waterfall, we tell the browser to start downloading the font files at the exact same moment it begins reading the HTML `<head>`, before it even finishes parsing the page layout.

Because Astro hashes asset names in production (e.g., `ibm-plex-mono-latin-500-normal.DSY6xOcd.woff2`), we import the font URLs using Vite's `?url` query in `Layout.astro`:

```astro
---
// src/layouts/Layout.astro
import playfairWoff2 from "@fontsource-variable/playfair-display/files/playfair-display-latin-wght-normal.woff2?url";
import ibmPlexMono400 from "@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-400-normal.woff2?url";
import ibmPlexMono500 from "@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-500-normal.woff2?url";
import ibmPlexMono600 from "@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-600-normal.woff2?url";
---

<head>
  <!-- Preload fonts to eliminate the network waterfall -->
  <link
    rel="preload"
    href={playfairWoff2}
    as="font"
    type="font/woff2"
    crossorigin="anonymous"
  />
  <link
    rel="preload"
    href={ibmPlexMono400}
    as="font"
    type="font/woff2"
    crossorigin="anonymous"
  />
  <link
    rel="preload"
    href={ibmPlexMono500}
    as="font"
    type="font/woff2"
    crossorigin="anonymous"
  />
  <link
    rel="preload"
    href={ibmPlexMono600}
    as="font"
    type="font/woff2"
    crossorigin="anonymous"
  />
</head>
```

```plaintext
PARALLEL PRELOAD PIPELINE:
HTML arrives   [================>]
Font Preloads       [============]  (Downloaded in parallel with DOM construction!)
Page Paints    [Text renders instantly with custom fonts]
```

**The Result:** Fonts are already available when the browser paints the text elements. **Cumulative Layout Shift (CLS) dropped to a perfect 0.000.**

---

## 3. Cutting Image Payload by 63% with Lossless WebP

As discussed in my previous post on dithering, this website renders photos and logos as 1-bit ink masks with alpha transparency.

Originally, all images were exported as PNG (`image/png`). While PNG is lossless, its DEFLATE compression algorithm was designed in the 1990s.

Modern **lossless WebP** uses advanced predictive filtering and LZ77 entropy coding, which compresses repetitive sparse 1-bit patterns far more efficiently.

We re-ran our Python converter across every image in the project:

```bash
# Convert profile avatar and partner stamps to lossless WebP
bun run ink public/profile-image-src.jpg -o public/profile-image.webp --mode bayer
```

| Asset | Original PNG Size | Lossless WebP Size | Bandwidth Saved |
| :--- | :--- | :--- | :--- |
| `profile-image` (LCP avatar) | $45.2\text{ KiB}$ | $16.4\text{ KiB}$ | **-63.7%** |
| `moratuwa.webp` (University crest) | $11.8\text{ KiB}$ | $3.5\text{ KiB}$ | **-70.3%** |
| `sliit.webp` (University logo) | $8.4\text{ KiB}$ | $2.6\text{ KiB}$ | **-69.0%** |
| `sysco-labs.webp` | $9.1\text{ KiB}$ | $2.9\text{ KiB}$ | **-68.1%** |

### Optimizing Largest Contentful Paint (LCP)

Lighthouse measures **Largest Contentful Paint (LCP)**: how long it takes for the largest visual block above the fold to appear. On the homepage, that block is my profile avatar.

To ensure the avatar renders with zero delay:

1. We added an explicit `<link rel="preload" as="image" href="/profile-image.webp" fetchpriority="high">` in `<head>`.
2. On the `<img>` tag itself, we specified `loading="eager"` and `fetchpriority="high"`.
3. We set explicit `width="160"` and `height="160"` attributes so the browser could reserve the space before the image bytes even finished downloading, preventing any layout shift.

---

## 4. Scoping Heavy Assets (The KaTeX Trap)

For blog posts that feature mathematical formulas, this site uses KaTeX (`remark-math` and `rehype-katex`).

KaTeX requires a stylesheet (`katex.min.css`) that is about $25\text{ KiB}$.

A common mistake in Astro projects is importing CSS globally in `Layout.astro`:

```astro
---
// DON'T DO THIS GLOBALLY IF ONLY BLOG POSTS NEED IT!
import "katex/dist/katex.min.css";
---
```

If you do that, every user visiting your homepage or project showcase is forced to download $25\text{ KiB}$ of mathematical font rules they will never use.

Instead, we moved the KaTeX import exclusively into `src/pages/blog/[...slug].astro`:

```astro
---
// src/pages/blog/[...slug].astro
import "katex/dist/katex.min.css";
---
```

The homepage and project list remain featherlight, while articles that actually contain math equations get the full KaTeX styling loaded on demand.

---

## 5. View Transitions Without Glitches or Flashes

Astro includes `ClientRouter` (formerly View Transitions), which intercepts internal link clicks and swaps page contents dynamically with the browser View Transitions API. This gives a multi-page static site the smooth feel of a Single Page App (SPA).

However, introducing client-side navigation can introduce subtle visual bugs:

### Bug A: The Dark Mode Flash

If a user switched to Dark Mode and clicked a link to `/blog`, the incoming HTML page would initially render in Light Mode for a split second before the dark-mode script ran. This produced a blinding white flash.

**The Fix:** Astro provides a lifecycle hook called `astro:before-swap`. This runs *after* the new HTML document is fetched, but *before* it is swapped into the DOM:

```javascript
// src/layouts/Layout.astro
document.addEventListener("astro:before-swap", (event) => {
  const savedTheme = localStorage.getItem("theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const isDark = savedTheme === "dark" || (!savedTheme && prefersDark);

  if (isDark) {
    event.newDocument.documentElement.classList.add("dark");
    event.newDocument.documentElement.setAttribute("data-theme", "dark");
  } else {
    event.newDocument.documentElement.classList.remove("dark");
    event.newDocument.documentElement.setAttribute("data-theme", "light");
  }
});
```

By injecting the theme class directly into `event.newDocument` before the swap, the incoming page renders in dark mode on its very first frame. Zero flash.

### Bug B: Preserving Procedural SVG Filters

As explained in the design post, this site uses SVG filters (`#newspaper-crumple-relief` and `#global-print-grain`) to create physical paper grain and folds.

During View Transitions, if the SVG filter element is destroyed and recreated, the GPU has to recompile the noise shaders, causing an audible hitch or visual flicker.

We marked the SVG overlay with Astro's `transition:persist` directive:

```html
<svg class="screen-grain-overlay" aria-hidden="true" transition:persist="screen-grain">
  <!-- Filters stay alive in GPU memory across navigations -->
</svg>
```

The browser keeps the grain overlay alive in memory across page changes without re-rendering it.

---

## 6. Accessibility & Best Practices (The Other 100s)

A 100 in Performance doesn't mean much if visually impaired users or screen readers can't navigate your site.

Here are the key accessibility details we baked in:

1. **High Contrast Broadsheet Tokens:** Even with an antique warm newsprint background (`#fcecec`), our primary ink color (`#242020`) has a contrast ratio of $11.8:1$, far surpassing WCAG AAA requirements ($7:1$).
2. **Accessible Mobile Navigation:** Our mobile accordion menu includes proper ARIA attributes (`aria-expanded`, `aria-controls`, `aria-label`). When the menu opens, keyboard focus is trapped; pressing `Escape` cleanly closes the menu and returns focus to the toggle button.
3. **Semantic Landmarks:** We use proper HTML5 landmarks (`<header>`, `<main>`, `<article>`, `<footer>`, `<nav>`) so assistive tools can jump between sections effortlessly.
4. **SVG Screen Reader Hiding:** Purely decorative visual layers (paper folds, noise filters, icons) are marked with `aria-hidden="true"`.

---

## The Scorecard: Before vs After

Here is what the numbers look like after applying all these optimizations:

| Metric | Before Optimization | After Optimization | Real-World Impact |
| :--- | :--- | :--- | :--- |
| **Lighthouse Performance** | 98 | **100** | Perfect score on Slow 4G mobile |
| **Render-Blocking Requests** | 1 request (Header.css) | **0 requests** | Inlined into HTML `<style>` |
| **Render-Blocking Delay** | ~400 ms | **0 ms** | Instant initial paint |
| **Cumulative Layout Shift** | 0.008 | **0.000** | Zero visual movement |
| **LCP Avatar Size** | 45.2 KiB (PNG) | **16.4 KiB (WebP)** | 63.7% less bandwidth |
| **FCP (First Contentful Paint)** | 1.2 s | **~0.8 s** | Snappy mobile response |
| **Page Transitions** | White flash in dark mode | **Seamless ink-fade** | Persistent theme state |

Achieving a 100 on Lighthouse isn't about using magical tricks or disabling features. It's about respecting the browser's critical rendering path: giving it what it needs immediately, deferring what it doesn't, and making sure every single byte sent over the wire earns its place.
