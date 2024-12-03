const NUMBER_OF_RECORDS = "800 million"
const DESCRIPTION = `Search over ${NUMBER_OF_RECORDS} free and openly licensed images, photos, audio, and other media types for reuse and remixing.`

/**
 * The default metadata for the site. Can be extended and/or overwritten per page. And even in components!
 * See the Nuxt.js docs for more info.
 * {@link https://nuxtjs.org/guides/features/meta-tags-seo} Nuxt.js Docs
 */
export const meta = [
  { charset: "utf-8" },
  {
    name: "viewport",
    content: "width=device-width,initial-scale=1",
  },
  {
    key: "theme-color",
    name: "theme-color",
    content: "#ffffff",
  },
  {
    name: "description",
    content: DESCRIPTION,
  },
  { key: "og:title", property: "og:title", content: "Openverse" },
  {
    key: "og:image",
    property: "og:image",
    content: "/openverse-default.jpg",
  },
  {
    key: "og:description",
    name: "og:description",
    content: DESCRIPTION,
  },
  { name: "twitter:card", content: "summary_large_image" },
  { name: "twitter:site", content: "@WPOpenverse" },
]
