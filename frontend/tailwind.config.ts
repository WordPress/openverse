import defaultTheme from "tailwindcss/defaultTheme"
import plugin from "tailwindcss/plugin"

import { SCREENS } from "./src/constants/screens"
import { Z_INDICES } from "./src/constants/z-indices"

import type { Config } from "tailwindcss"
import type { PluginAPI } from "tailwindcss/types/config"

export default {
  content: [
    "./src/**/*.{vue,js,jsx,ts,tsx,mdx}",
    "./nuxt.config.ts",
    "./tailwind.safelist.txt",
  ],
  theme: {
    screens: SCREENS,
    zIndex: Z_INDICES,
    colors: {
      // Semantic
      "info-soft": "#dbe2ff",
      info: "#2349e7",
      "warning-soft": "#fff1cc",
      warning: "#9d650b",
      "success-soft": "#dbf0d6",
      success: "#3b772c",
      "error-soft": "#ffe0d1",
      error: "#b43e04",

      // Brand
      yellow: "#fde034",
      pink: "#ad1f85",
      // Active
      "dark-pink": "#7c2264",

      // Grayscale
      black: "#000000",
      "dark-gray": "#767676",
      gray: "#b0b0b0",
      "light-gray": "#d8d8d8",
      white: "white",
      // Dark Charcoal
      "dark-charcoal": {
        DEFAULT: "#232323",
        "06": "#f7f7f7",
        10: "#ededed",
        20: "#dfdfdf",
        30: "#c5c5c5",
        40: "#a9a9a9",
        50: "#929292",
        60: "#7e7e7e",
        70: "#676767",
        80: "#474747",
        90: "#363636",
        12: "#0d0d0d",
      },
      "gray-9": "#565656",
      "gray-13": "#0d0d0d",

      // Special keywords
      tx: "transparent",
      curr: "currentColor",
      current: "currentColor",
    },
    spacing: {
      // Constants
      "0.5px": "0.5px",
      px: "1px",
      "1.5px": "1.5px",
      ch: "1ch",
      ex: "1ex",
      half: "50%",
      full: "100%",
      "full-with-border": "calc(100% + 2px)",

      // Indexed by multiples of baseline (~ `0.25rem`)
      0: "0",
      0.5: "0.125rem",
      0.75: "0.1875rem",
      1: "0.25rem",
      2: "0.50rem",
      3: "0.75rem",
      4: "1.00rem",
      4.5: "1.125rem",
      5: "1.25rem",
      6: "1.50rem",
      7: "1.75rem",
      8: "2.00rem",
      9: "2.25rem",
      10: "2.50rem",
      11: "2.75rem",
      12: "3.00rem",
      14: "3.50rem",
      15: "3.75rem",
      16: "4.00rem",
      18: "4.50rem",
      20: "5.00rem",
      24: "6.00rem",
      26: "6.50rem",
      30: "7.50rem",
      40: "10.00rem",
      50: "12.50rem",
      64: "16.00rem",
      66: "16.25rem",
      70: "17.50rem",
      80: "20.00rem",
      120: "30.00rem",
    },
    ringWidth: {
      DEFAULT: "1.5px", // aka slim
      bold: "3.0px",
      1: "1px",
      0: "0",
    },
    borderWidth: {
      0: "0px",
      DEFAULT: "1px",
      1.5: "1.5px",
      2: "2px",
      3: "3px",
    },
    ringOffsetWidth: {
      0: "0px",
      1: "1px",
      2: "2px",
    },
    fontSize: {
      // Deprecated
      lg: "1.12rem",
      lgr: "1.43rem",
      "7xl": [
        // Heading 1
        "5.625rem", // 90px
        "1.3", // 130%
      ],
      "6xl": [
        // Heading 2
        "2.0000rem", // 32px
        "1.3", // 130%
      ],
      "5xl": [
        // Heading 3
        "1.7500rem", // 28px
        "1.3", // 130%
      ],
      "4xl": [
        // Heading 4
        "1.5000rem", // 24px
        "1.3", // 130%
      ],
      "3xl": [
        // Heading 5
        "1.1875rem", // 19px
        "1.3", // 130%
      ],
      "2xl": [
        // Heading 6
        "1.0000rem", // 16px
        "1.3", // 130%
      ],

      // Content
      base: [
        "0.8750rem", // 14px
        "1.5", // 150%
      ],
      sm: [
        // small, eg. label
        "0.8125rem", // 13px
        "1.3", // 130%
      ],
      sr: [
        // smaller, eg. caption, category
        "0.7500rem", // 12px
        "1.3", // 130%
      ],
      xs: [
        // extra small, eg. time
        "0.6875rem", // 11px
        "1.2", // 120%
      ],
    },
    flexGrow: {
      0: "0",
      DEFAULT: "1",
      2: "2",
    },
    fontFamily: {
      mono: ['"JetBrains Mono"', "monospace"],
      sans: ["Inter", ...defaultTheme.fontFamily.sans],
      serif: [...defaultTheme.fontFamily.serif],
    },
    extend: {
      blur: {
        image: "60px",
        text: "4px",
      },
      lineHeight: {
        loose: "2.0",
        larger: "1.9",
        relaxed: "1.8",
        large: "1.7",
        normal: "1.5",
        close: "1.4",
        snug: "1.3",
        tight: "1.2",
        none: "1.0",
      },
      scale: {
        "-100": "-1",
      },
      boxShadow: {
        ring: "inset 0 0 0 1px white",
        "ring-1.5": "inset 0 0 0 1.5px white",
        "el-2": "0 0.125rem 0.25rem rgba(0, 0, 0, 0.1)",
        "slim-filled": "inset 0 0 0 1.5px white",
        "bold-filled": "inset 0 0 0 3px white",
      },
      borderRadius: {
        inherit: "inherit",
      },
      outlineWidth: {
        1.5: "1.5px",
        3: "3px",
      },
      typography: (theme: PluginAPI["theme"]) => ({
        DEFAULT: {
          css: {
            "--tw-prose-body": theme("colors.dark-charcoal.default"),
            "--tw-prose-headings": theme("colors.dark-charcoal.default"),
            "--tw-prose-links": theme("colors.pink"),
            a: {
              textDecoration: "none",
              "&:hover": {
                "text-decoration": "underline",
              },
            },
          },
        },
      }),
    },
  },
  plugins: [
    require("@tailwindcss/typography"),
    // Focus styles
    // This plugin has related stylesheets in `src/styles/tailwind.css`.
    plugin(({ matchUtilities, theme }) => {
      matchUtilities(
        Object.fromEntries(
          [
            "focus-slim-offset",
            "focus-slim-tx",
            "focus-slim-filled",
            "focus-bold-filled",
            "focus-slim-borderless-filled",
          ].map((item) => [
            item,
            (value) => ({
              "--tw-ring-color": value,
              "--tw-outline-color": value,
            }),
          ])
        ),
        { values: { ...theme("colors"), DEFAULT: theme("colors.pink") } }
      )
    }),
  ],
} satisfies Config
