/**
 * The default metadata for the site. Can be extended and/or overwritten per page. And even in components!
 * See the Nuxt.js docs for more info.
 * {@link https://nuxtjs.org/guides/features/meta-tags-seo} Nuxt.js Docs
 */

const NUMBER_OF_RECORDS = "700 million"
const DESCRIPTION = `Search over ${NUMBER_OF_RECORDS} free and openly licensed images, photos, audio, and other media types for reuse and remixing.`

export const meta = [
  { charset: "utf-8" },
  {
    name: "viewport",
    content: "width=device-width,initial-scale=1",
  },
  // By default, tell all robots not to index pages. Will be overwritten in the
  // search, content and home pages.
  { hid: "robots", name: "robots", content: "noindex" },
  {
    vmid: "monetization",
    name: "monetization",
    content: "$ilp.uphold.com/edR8erBDbRyq",
  },
  {
    hid: "theme-color",
    name: "theme-color",
    content: "#ffffff",
  },
  {
    name: "description",
    content: DESCRIPTION,
  },
  { hid: "og:title", name: "og:title", content: "Openverse" },
  {
    hid: "og:image",
    name: "og:image",
    content: "/openverse-default.jpg",
  },
  {
    hid: "og:description",
    name: "og:description",
    content: DESCRIPTION,
  },
  { name: "twitter:card", content: "summary_large_image" },
  { name: "twitter:site", content: "@WPOpenverse" },
]
