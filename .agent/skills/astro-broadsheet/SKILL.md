---
name: astro-broadsheet
description: Guidelines and workflows for building and extending Nithika's Astro v5 Retro Newspaper / Ink-Print portfolio, Markdown blog collections, and Python 1-bit dithering pipeline.
---

# Astro Broadsheet & Ink-Print Skill

Use this skill whenever adding pages, components, blog articles, or image assets to this portfolio repository.

## 1. Design System Checklist (`DESIGN.md`)
- **Typography**: Use `font-display` (`Playfair Display Variable`) for `h1`–`h3` broadsheet headlines and drop-caps; use `font-mono` (`IBM Plex Mono`) for body text, dates, tags, and code.
- **Borders & Shadows**: Use `border border-primary` (`1px solid var(--color-border)`), double rules (`newspaper-rule-double`), and `.ink-card` hard offset hover shadows. Never use rounded corners or soft blurred shadows.
- **Voice**: Write portfolio blurbs in a casual, first-person engineering voice.

## 2. Converting Images & Logos to Newspaper Ink Prints
All images and organization logos must be converted to 1-bit transparent RGBA PNGs using the repository's `.venv`:

```bash
# Bayer 8x8 ordered dithering (portraits & photos)
.venv/bin/python scripts/ink_print.py input.jpg -o public/output.png --mode bayer --max-width 700

# Halftone rotated newspaper dots
.venv/bin/python scripts/ink_print.py input.jpg -o public/output-halftone.png --mode halftone --dot-size 6

# Atkinson crisp dithering (logos & icons)
.venv/bin/python scripts/ink_print.py logo.png -o public/logos/company.png --mode atkinson --max-width 256
```

Always render the resulting PNG with the `ink-illustration` class so it automatically inverts from black ink `#111111` to light ink `#fcecec` in Dark Mode.

## 3. Astro v5 Content Layer Blog (`src/content/blog/`)
Blog posts live in `src/content/blog/*.md` and are loaded via Astro v5's `glob` loader in `src/content.config.ts`.
Required frontmatter:
```yaml
---
title: "Post Title"
description: "Short editorial deck / summary shown on the front page and /blog index."
pubDate: 2026-10-26
tags: ["security", "systems"]
draft: false
---
```

## 4. Mandatory Quality Gate
Always run before completing any task:
```bash
bun run lint
bun run build
```

