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
      /**
       * Semantic color names.
       */
      bg: "var(--bg)",
      "bg-surface": "var(--bg-surface)",
      "bg-overlay": "var(--bg-overlay)",
      "bg-fill-primary": "var(--bg-fill-primary)",
      "bg-fill-primary-hover": "var(--bg-fill-primary-hover)",
      "bg-fill-secondary": "var(--bg-fill-secondary)",
      "bg-fill-secondary-hover": "var(--bg-fill-secondary-hover)",
      "bg-fill-tertiary": "var(--bg-fill-tertiary)",
      "bg-fill-tertiary-hover": "var(--bg-fill-tertiary-hover)",
      "bg-fill-transparent-hover": "var(--bg-fill-transparent-hover)",
      "bg-fill-complementary": "var(--bg-fill-complementary)",
      "bg-fill-warning": "var(--bg-fill-warning)",
      "bg-fill-info": "var(--bg-fill-info)",
      "bg-fill-success": "var(--bg-fill-success)",
      "bg-fill-error": "var(--bg-fill-error)",
      "bg-fill-disabled": "var(--bg-fill-disabled)",
      "bg-zero": "var(--bg-zero)",
      border: "var(--border)",
      "border-hover": "var(--border-hover)",
      "border-secondary": "var(--border-secondary)",
      "border-secondary-hover": "var(--border-secondary-hover)",
      "border-tertiary": "var(--border-tertiary)",
      "border-transparent-hover": "var(--border-transparent-hover)",
      "border-focus": "var(--border-focus)",
      "border-bg-ring": "var(--border-bg-ring)",
      "border-disabled": "var(--border-disabled)",
      text: "var(--text)",
      "text-secondary": "var(--text-secondary)",
      "text-disabled": "var(--text-disabled)",
      "text-link": "var(--text-link)",
      "text-over-dark": "var(--text-over-dark)",
      "text-secondary-over-dark": "var(--text-secondary-over-dark)",
      "icon-warning": "var(--icon-warning)",
      "icon-info": "var(--icon-info)",
      "icon-success": "var(--icon-success)",
      "icon-error": "var(--icon-error)",
      "wave-active": "var(--wave-active)",
      "wave-inactive": "var(--wave-inactive)",
      "modal-layer": "var(--modal-layer)",

      /**
       * Raw colors.
       *
       * These should be used sparingly as an "escape hatch" from the
       * semantic color names.
       */

      "info-1": "var(--info-1)",
      "info-2": "var(--info-2)",
      "info-3": "var(--info-3)",
      "info-4": "var(--info-4)",
      "info-5": "var(--info-5)",
      "info-6": "var(--info-6)",
      "info-7": "var(--info-7)",
      "info-8": "var(--info-8)",
      "info-9": "var(--info-9)",
      "info-10": "var(--info-10)",
      "info-11": "var(--info-11)",
      "info-12": "var(--info-12)",
      "info-13": "var(--info-13)",

      "warning-1": "var(--warning-1)",
      "warning-2": "var(--warning-2)",
      "warning-3": "var(--warning-3)",
      "warning-4": "var(--warning-4)",
      "warning-5": "var(--warning-5)",
      "warning-6": "var(--warning-6)",
      "warning-7": "var(--warning-7)",
      "warning-8": "var(--warning-8)",
      "warning-9": "var(--warning-9)",
      "warning-10": "var(--warning-10)",
      "warning-11": "var(--warning-11)",
      "warning-12": "var(--warning-12)",
      "warning-13": "var(--warning-13)",

      "success-1": "var(--success-1)",
      "success-2": "var(--success-2)",
      "success-3": "var(--success-3)",
      "success-4": "var(--success-4)",
      "success-5": "var(--success-5)",
      "success-6": "var(--success-6)",
      "success-7": "var(--success-7)",
      "success-8": "var(--success-8)",
      "success-9": "var(--success-9)",
      "success-10": "var(--success-10)",
      "success-11": "var(--success-11)",
      "success-12": "var(--success-12)",
      "success-13": "var(--success-13)",

      "error-1": "var(--error-1)",
      "error-2": "var(--error-2)",
      "error-3": "var(--error-3)",
      "error-4": "var(--error-4)",
      "error-5": "var(--error-5)",
      "error-6": "var(--error-6)",
      "error-7": "var(--error-7)",
      "error-8": "var(--error-8)",
      "error-9": "var(--error-9)",
      "error-10": "var(--error-10)",
      "error-11": "var(--error-11)",
      "error-12": "var(--error-12)",
      "error-13": "var(--error-13)",

      // Grayscale
      black: "var(--black)",
      "dark-gray": "var(--dark-gray)",
      gray: "var(--gray)",
      "light-gray": "var(--light-gray)",

      white: "var(--white)",

      // Dark Charcoal (now Gray with new shades)
      "gray-1": "var(--gray-1)",
      "gray-2": "var(--gray-2)",
      "gray-3": "var(--gray-3)",
      "gray-4": "var(--gray-4)",
      "gray-5": "var(--gray-5)",
      "gray-6": "var(--gray-6)",
      "gray-7": "var(--gray-7)",
      "gray-8": "var(--gray-8)",
      "gray-9": "var(--gray-9)",
      "gray-10": "var(--gray-10)",
      "gray-11": "var(--gray-11)",
      "gray-12": "var(--gray-12)",
      "gray-13": "var(--gray-13)",

      // Gray Opacities
      "gray-1-10": "var(--gray-1-10)",
      "gray-1-20": "var(--gray-1-20)",
      "gray-1-30": "var(--gray-1-30)",
      "gray-1-40": "var(--gray-1-40)",
      "gray-1-50": "var(--gray-1-50)",
      "gray-1-60": "var(--gray-1-60)",
      "gray-1-70": "var(--gray-1-70)",
      "gray-1-80": "var(--gray-1-80)",
      "gray-1-90": "var(--gray-1-90)",
      "gray-12-10": "var(--gray-12-10)",
      "gray-12-20": "var(--gray-12-20)",
      "gray-12-30": "var(--gray-12-30)",
      "gray-12-40": "var(--gray-12-40)",
      "gray-12-50": "var(--gray-12-50)",
      "gray-12-60": "var(--gray-12-60)",
      "gray-12-70": "var(--gray-12-70)",
      "gray-12-80": "var(--gray-12-80)",
      "gray-12-90": "var(--gray-12-90)",
      "gray-13-0": "var(--gray-13-0)",

      "white-0": "var(--white-0)",

      "pink-1": "var(--pink-1)",
      "pink-2": "var(--pink-2)",
      "pink-3": "var(--pink-3)",
      "pink-4": "var(--pink-4)",
      "pink-5": "var(--pink-5)",
      "pink-6": "var(--pink-6)",
      "pink-7": "var(--pink-7)",
      "pink-8": "var(--pink-8)",
      "pink-9": "var(--pink-9)",
      "pink-10": "var(--pink-10)",
      "pink-11": "var(--pink-11)",
      "pink-12": "var(--pink-12)",
      "pink-13": "var(--pink-13)",

      "yellow-1": "var(--yellow-1)",
      "yellow-2": "var(--yellow-2)",
      "yellow-3": "var(--yellow-3)",
      "yellow-4": "var(--yellow-4)",
      "yellow-5": "var(--yellow-5)",
      "yellow-7": "var(--yellow-7)",
      "yellow-8": "var(--yellow-8)",
      "yellow-9": "var(--yellow-9)",
      "yellow-10": "var(--yellow-10)",
      "yellow-11": "var(--yellow-11)",
      "yellow-12": "var(--yellow-12)",
      "yellow-13": "var(--yellow-13)",

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
            "--tw-prose-body": theme("colors.gray-12.default"),
            "--tw-prose-headings": theme("colors.gray-12.default"),
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
