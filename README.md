# Portfolio Website - Nithika Dias

A clean, retro-styled portfolio website built with Astro and Tailwind CSS.

## 🚀 Project Structure

```
portfolio-website/
├── public/
│   ├── profile.jpg          # Add your profile photo here
│   └── company-logo.png     # Add company logos here (optional)
├── src/
│   ├── components/
│   │   ├── Header.astro         # Site header with date
│   │   ├── Hero.astro           # Hero section with name, title, bio
│   │   ├── Section.astro        # Reusable section component
│   │   └── ExperienceCard.astro # Work experience card
│   ├── data/
│   │   └── portfolio.ts         # Portfolio data (info & experiences)
│   ├── layouts/
│   │   └── Layout.astro         # Base layout
│   ├── pages/
│   │   └── index.astro          # Home page
│   └── styles/
│       └── global.css           # Global styles
└── package.json
```

## 📝 Customization

### 1. Add Your Profile Photo

Place your profile image in the `public/` folder as `profile.jpg` (or update the path in `src/data/portfolio.ts`).

### 2. Update Your Information

Edit `src/data/portfolio.ts`:

```typescript
export const personalInfo: PersonalInfo = {
  name: "Your Name",
  title: "Your Title",
  bio: "Your bio...",
  imageUrl: "/profile.jpg"
};

export const experiences: Experience[] = [
  {
    company: "Company Name",
    position: "Your Position",
    startDate: "Start Date",
    endDate: "End Date",
    description: "Description...",
    logo: "/company-logo.png" // optional
  }
];
```

### 3. Update the Header Date

In `src/pages/index.astro`, modify:
```astro
<Header currentDate="1st December 2025" />
```

## 🎨 Design Features

- **Retro aesthetic** with warm beige/tan color scheme
- **Monospace typography** using IBM Plex Mono
- **Responsive design** that works on all devices
- **Clean component architecture** for easy maintenance
- **Type-safe** with TypeScript interfaces

## 🛠️ Commands

| Command           | Action                                       |
|-------------------|----------------------------------------------|
| `bun install`     | Install dependencies                         |
| `bun dev`         | Start dev server at `localhost:4321`        |
| `bun build`       | Build for production to `./dist/`           |
| `bun preview`     | Preview production build locally            |

## 📦 Tech Stack

- **Astro** - Static site generator
- **Tailwind CSS** - Utility-first CSS framework
- **TypeScript** - Type safety
- **IBM Plex Mono** - Monospace font

## 🔧 Best Practices Implemented

✅ Component-based architecture  
✅ Separation of data and presentation  
✅ TypeScript interfaces for type safety  
✅ Semantic HTML structure  
✅ Responsive design  
✅ Accessible markup  
✅ Clean file organization  
✅ Reusable components

## 📄 Adding More Sections

To add more sections (Projects, Skills, etc.), create new components in `src/components/` and add them to `index.astro`:

```astro
<Section title="Projects">
  <!-- Your project cards here -->
</Section>
```

## 🌐 Deployment

Build the site:
```bash
bun build
```

Deploy the `dist/` folder to any static hosting service:
- Vercel
- Netlify
- GitHub Pages
- Cloudflare Pages

---

Built with ❤️ using Astro
