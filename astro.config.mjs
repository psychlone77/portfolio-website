// @ts-check
import { defineConfig } from "astro/config";
import { satteri } from "@astrojs/markdown-satteri";
import tailwindcss from "@tailwindcss/vite";
import react from "@astrojs/react";
import sitemap from "@astrojs/sitemap";
import katex from "katex";

/**
 * Sätteri HAST plugin that renders inline (`code.math-inline`) and
 * display (`pre > code.math-display`) math nodes via KaTeX at build time.
 */
const satteriKatexPlugin = {
  name: "satteri-katex",
  element: {
    filter: ["pre", "code"],
    /**
     * @param {any} node
     * @param {any} ctx
     */
    visit(node, ctx) {
      if (node.tagName === "pre") {
        const codeChild = node.children?.find(
          (/** @type {any} */ c) => c.type === "element" && c.tagName === "code",
        );
        const classes = Array.isArray(codeChild?.properties?.className)
          ? codeChild.properties.className
          : [];
        if (classes.includes("math-display") || classes.includes("language-math")) {
          const tex = ctx.textContent(codeChild).trim();
          const html = katex.renderToString(tex, {
            displayMode: true,
            throwOnError: false,
          });
          ctx.replaceNode(node, { type: "raw", value: html });
        }
        return;
      }

      if (node.tagName === "code") {
        const parent = ctx.parent(node);
        if (parent?.type === "element" && parent.tagName === "pre") return;
        const classes = Array.isArray(node.properties?.className) ? node.properties.className : [];
        if (classes.includes("math-inline") || classes.includes("language-math")) {
          const tex = ctx.textContent(node).trim();
          const html = katex.renderToString(tex, {
            displayMode: false,
            throwOnError: false,
          });
          ctx.replaceNode(node, { type: "raw", value: html });
        }
      }
    },
  },
};

/**
 * Sätteri HAST plugin that wraps markdown <table> elements in a responsive
 * scrollable container (<div class="newspaper-table-wrapper">) for mobile viewports.
 */
const satteriTablePlugin = {
  name: "satteri-table-wrap",
  element: {
    filter: ["table"],
    /**
     * @param {any} node
     * @param {any} ctx
     */
    visit(node, ctx) {
      const parent = ctx.parent(node);
      const classes = Array.isArray(parent?.properties?.className)
        ? parent.properties.className
        : [];
      if (classes.includes("newspaper-table-wrapper")) return;

      ctx.replaceNode(node, {
        type: "element",
        tagName: "div",
        properties: { className: ["newspaper-table-wrapper"] },
        children: [
          {
            type: "element",
            tagName: "table",
            properties: node.properties,
            children: node.children,
          },
        ],
      });
    },
  },
};

// https://astro.build/config
export default defineConfig({
  site: "https://nithikadias.pages.dev.",
  build: {
    inlineStylesheets: "always",
  },
  vite: {
    plugins: [tailwindcss()],
  },
  markdown: {
    syntaxHighlight: {
      type: "shiki",
      excludeLangs: ["math"],
    },
    processor: satteri({
      features: {
        math: true,
      },
      hastPlugins: [satteriKatexPlugin, satteriTablePlugin],
    }),
    shikiConfig: {
      themes: {
        light: "github-light",
        dark: "github-dark",
      },
    },
  },
  integrations: [react(), sitemap()],
});
