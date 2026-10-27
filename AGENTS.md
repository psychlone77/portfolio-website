# AGENTS.md — AI Coding Agent Instructions

Welcome to Nithika Dias's portfolio & blog repository (`portfolio-website`). Read this file carefully before making any modifications.

---

## 1. Project Overview & Tech Stack

- **Framework**: Astro v5 (Static Site Generation + Content Layer API)
- **Styling**: Tailwind CSS v4 (`@tailwindcss/vite`) + custom broadsheet tokens in [`src/styles/global.css`](file:///home/nithika/Uni/Personal%20Projects/portfolio-website/src/styles/global.css)
- **UI & Fonts**: Astro components (`.astro`), React 19 (`@astrojs/react`), `Playfair Display Variable` (headlines), and `IBM Plex Mono` (body, metadata, code)
- **Blog Content**: Markdown posts in [`src/content/blog/`](file:///home/nithika/Uni/Personal%20Projects/portfolio-website/src/content/blog) configured via [`src/content.config.ts`](file:///home/nithika/Uni/Personal%20Projects/portfolio-website/src/content.config.ts) with KaTeX math (`remark-math` + `rehype-katex`)
- **Image Processing**: Python virtual environment (`.venv/`) running [`scripts/ink_print.py`](file:///home/nithika/Uni/Personal%20Projects/portfolio-website/scripts/ink_print.py) to convert photos and logos into 1-bit transparent newspaper ink prints

---

## 2. Design & Content Rules

1. **Always Consult [`DESIGN.md`](file:///home/nithika/Uni/Personal%20Projects/portfolio-website/DESIGN.md)**:
   - Maintain the **retro newspaper / indie zine ink-print aesthetic** at all times.
   - Do **not** introduce rounded cards (`rounded-lg`, `rounded-xl`), soft blurred drop shadows (`shadow-lg`), or un-dithered full-color photos.
   - Keep the copy on the homepage **informal, conversational, and first-person** rather than stiff corporate resume language.
2. **Processing Images & Logos**:
   - Always use the local Python virtual environment (`.venv/bin/python`) when running Python scripts:
     ```bash
     bun run ink <input_image> -o <output_webp_or_png> --mode bayer|halftone|atkinson
     ```
   - Prefer lossless WebP (`.webp`) for superior compression (~60% bandwidth reduction).
   - Apply the `.ink-illustration` class to all 1-bit transparent images so they invert cleanly in Dark Mode.
3. **Adding Blog Posts**:
   - Place `.md` files in `src/content/blog/` with frontmatter matching the schema in `src/content.config.ts` (`title`, `description`, `pubDate`, `tags`, optional `heroImage`, `draft`).

---

## 3. Mandatory Post-Change Verification (REQUIRED)

After making **any** code, style, configuration, or content changes, you **MUST** run both linting and the production build and ensure there are **zero errors** before finishing your turn:

```bash
bun run lint
bun run build
```

- `bun run lint` runs `astro check` (TypeScript + Astro template diagnostics) and `eslint .`.
- `bun run build` verifies that all static routes (`/`, `/blog`, `/blog/[slug]`, `/sitemap-index.xml`) compile cleanly.
- Never leave broken types, unused imports, or failing builds.

---

## 4. Git Commit Guidelines

When creating git commits, follow this format:

```bash
git commit -m "action: commit summary" -m "optional detailed message if commit is large"
```

- **Format**: `<action>: <concise summary>` in lowercase/imperative mood (e.g. `feat: add mobile sections dropdown and view transitions`, `fix: prevent dark mode flash on hash navigation`, `style: refine broadsheet paper texture`).
- **Detailed Message**: Use a second `-m "..."` flag for a bulleted or detailed explanation if the commit is large or covers multiple changes.
- **Verification First**: Always ensure `bun run lint` and `bun run build` exit with zero errors before committing.

