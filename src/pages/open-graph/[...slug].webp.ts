import fs from "node:fs";
import path from "node:path";
import type { ReactNode } from "react";
import type { APIRoute, GetStaticPaths } from "astro";
import { getCollection } from "astro:content";
import satori from "satori";
import { Resvg } from "@resvg/resvg-js";
import sharp from "sharp";
import { personalInfo } from "../../data/portfolio";

interface CardProps {
  title: string;
  subtitle: string;
  kicker: string;
  tags: string[];
}

// Pre-load font buffers in module scope for fast multi-page builds
const playfairBold = fs.readFileSync(
  path.resolve(
    process.cwd(),
    "node_modules/@fontsource/playfair-display/files/playfair-display-latin-700-normal.woff",
  ),
);

const ibmMonoRegular = fs.readFileSync(
  path.resolve(
    process.cwd(),
    "node_modules/@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-400-normal.woff",
  ),
);

const ibmMonoSemiBold = fs.readFileSync(
  path.resolve(
    process.cwd(),
    "node_modules/@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-600-normal.woff",
  ),
);

async function generateOgImage({
  title,
  subtitle,
  kicker,
  tags,
}: CardProps): Promise<Buffer> {
  const cardElement = {
    type: "div",
    props: {
        style: {
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          width: "1200px",
          height: "630px",
          backgroundColor: "#fcecec",
          padding: "44px 52px",
          border: "12px solid #111111",
          fontFamily: "IBM Plex Mono",
          color: "#111111",
          boxSizing: "border-box",
        },
        children: [
          // Header / Masthead
          {
            type: "div",
            props: {
              style: {
                display: "flex",
                flexDirection: "column",
                width: "100%",
              },
              children: [
                {
                  type: "div",
                  props: {
                    style: {
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      paddingBottom: "12px",
                    },
                    children: [
                      {
                        type: "div",
                        props: {
                          style: {
                            fontSize: "16px",
                            fontWeight: 600,
                            letterSpacing: "2.5px",
                          },
                          children: "THE DAILY DISPATCH • SPECIAL EDITION",
                        },
                      },
                      {
                        type: "div",
                        props: {
                          style: {
                            fontSize: "16px",
                            fontWeight: 600,
                            letterSpacing: "1.5px",
                          },
                          children: "NITHIKA DIAS",
                        },
                      },
                    ],
                  },
                },
                {
                  type: "div",
                  props: {
                    style: {
                      height: "4px",
                      width: "100%",
                      borderTop: "1px solid #111111",
                      borderBottom: "1px solid #111111",
                    },
                  },
                },
              ],
            },
          },

          // Center: Headline & Subtitle
          {
            type: "div",
            props: {
              style: {
                display: "flex",
                flexDirection: "column",
                gap: "14px",
                margin: "auto 0",
              },
              children: [
                {
                  type: "div",
                  props: {
                    style: {
                      fontSize: "15px",
                      fontWeight: 600,
                      letterSpacing: "3px",
                      textTransform: "uppercase",
                      color: "#6b625b",
                    },
                    children: kicker,
                  },
                },
                {
                  type: "div",
                  props: {
                    style: {
                      fontFamily: "Playfair Display",
                      fontSize: title.length > 45 ? "46px" : "54px",
                      fontWeight: 700,
                      lineHeight: 1.15,
                      color: "#111111",
                      letterSpacing: "-0.5px",
                    },
                    children: title,
                  },
                },
                {
                  type: "div",
                  props: {
                    style: {
                      fontSize: "20px",
                      color: "#4a4343",
                      lineHeight: 1.45,
                      marginTop: "6px",
                    },
                    children: subtitle,
                  },
                },
              ],
            },
          },

          // Footer: Tags & Domain
          {
            type: "div",
            props: {
              style: {
                display: "flex",
                flexDirection: "column",
                width: "100%",
              },
              children: [
                {
                  type: "div",
                  props: {
                    style: {
                      height: "2px",
                      width: "100%",
                      backgroundColor: "#111111",
                      marginBottom: "14px",
                    },
                  },
                },
                {
                  type: "div",
                  props: {
                    style: {
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    },
                    children: [
                      {
                        type: "div",
                        props: {
                          style: { display: "flex", gap: "10px" },
                          children: tags.slice(0, 4).map((t) => ({
                            type: "span",
                            props: {
                              style: {
                                border: "1px solid #111111",
                                padding: "4px 10px",
                                fontSize: "14px",
                                fontWeight: 600,
                                backgroundColor: "#f6e0e0",
                                letterSpacing: "1px",
                              },
                              children: `#${t}`,
                            },
                          })),
                        },
                      },
                      {
                        type: "div",
                        props: {
                          style: {
                            fontSize: "16px",
                            fontWeight: 600,
                            letterSpacing: "0.5px",
                          },
                          children: "nithikadias.pages.dev",
                        },
                      },
                    ],
                  },
                },
              ],
            },
          },
        ],
      },
    };

  const svg = await satori(cardElement as unknown as ReactNode, {
    width: 1200,
    height: 630,
    fonts: [
        {
          name: "Playfair Display",
          data: playfairBold,
          weight: 700,
          style: "normal",
        },
        {
          name: "IBM Plex Mono",
          data: ibmMonoRegular,
          weight: 400,
          style: "normal",
        },
        {
          name: "IBM Plex Mono",
          data: ibmMonoSemiBold,
          weight: 600,
          style: "normal",
        },
      ],
    },
  );

  const resvg = new Resvg(svg, { fitTo: { mode: "width", value: 1200 } });
  const pngData = resvg.render().asPng();
  return await sharp(pngData).webp({ quality: 90 }).toBuffer();
}

export const getStaticPaths: GetStaticPaths = async () => {
  const posts = await getCollection("blog", ({ data }) => !data.draft);

  return [
    {
      params: { slug: "index" },
      props: {
        title: personalInfo.name,
        subtitle:
          "Associate Engineer in Application Security. Resilient systems and vintage broadsheet aesthetics.",
        kicker: "FRONT PAGE // SPECIAL EDITION",
        tags: ["APPSEC", "SOFTWARE", "SYSTEMS"],
      } satisfies CardProps,
    },
    {
      params: { slug: "blog" },
      props: {
        title: "Dispatches & Articles",
        subtitle:
          "Technical write-ups on application security, web vitals, systems programming, and retro print.",
        kicker: "SECTION // EDITORIAL CATALOG",
        tags: ["ARTICLES", "SECURITY", "PERFORMANCE"],
      } satisfies CardProps,
    },
    ...posts.map((post) => ({
      params: { slug: `blog/${post.id}` },
      props: {
        title: post.data.title,
        subtitle: post.data.description,
        kicker: `DISPATCH // ${post.data.tags.slice(0, 2).join(" & ").toUpperCase()}`,
        tags: post.data.tags.map((t) => t.toUpperCase()),
      } satisfies CardProps,
    })),
  ];
};

export const GET: APIRoute = async ({ props }) => {
  const cardProps = props as CardProps;
  const webpBuffer = await generateOgImage(cardProps);

  return new Response(new Uint8Array(webpBuffer), {
    headers: {
      "Content-Type": "image/webp",
      "Cache-Control": "public, max-age=31536000, immutable",
    },
  });
};
