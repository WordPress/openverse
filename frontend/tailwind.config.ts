import defaultTheme from "tailwindcss/defaultTheme"
import plugin from "tailwindcss/plugin"

import { SCREENS } from "./src/constants/screens"
import { Z_INDICES } from "./src/constants/z-indices"

import type { Config } from "tailwindcss"

/**
 * Create a scale of shades for the given color.
 *
 * The scale will have the specified number of points, indexed from 1.
 *
 * @param color - the color to generate the scale for
 * @param points - the number of points to have in the scale
 * @returns - the object mapping an index to the color CSS variable
 */
export const shadeScale = (color: string, points = 13) =>
  Object.fromEntries(
    Array.from({ length: points }, (_, idx) => [
      idx + 1,
      `var(--color-${color}-${idx + 1})`,
    ])
  )

/**
 * Create a scale of opacities for the given color.
 *
 * The scale will have opacities from 10% to 90%, in 10% increments. Use
 * the regular color for 100% opacity and `tx` for 0% opacity.
 *
 * @param color - the color to generate the scale for
 * @returns - the object mapping an opacity to the color CSS variable
 */
export const opacityScale = (color: string) =>
  Object.fromEntries(
    Array.from({ length: 9 }, (_, idx) => [
      (idx + 1) * 10,
      `var(--color-${color}-${(idx + 1) * 10})`,
    ])
  )

export default {
  darkMode: [
    "variant",
    [
      "@media (prefers-color-scheme: dark) { &:not(.light-mode *) }",
      "&:is(.dark-mode *)", // :is is so the specificity matches and there's not unexpected behavior
    ],
  ],
  content: [
    "./src/**/*.{vue,js,jsx,ts,tsx,mdx}",
    "./nuxt.config.ts",
    "./tailwind.safelist.txt",
  ],
  theme: {
    screens: SCREENS,
    zIndex: Z_INDICES,
    /**
     * See the extend.color, extend.backgroundColor, and extend.borderColor
     * sections for additional, context-specific colors.
     */
    colors: {
      icon: {
        warning: "var(--color-icon-warning)",
        info: "var(--color-icon-info)",
        success: "var(--color-icon-success)",
        error: "var(--color-icon-error)",
      },
      wave: {
        active: "var(--color-wave-active)",
        inactive: "var(--color-wave-inactive)",
      },
      "modal-layer": "var(--color-modal-layer)",

      // Semantic colors

      info: shadeScale("info"),
      warning: shadeScale("warning"),
      success: shadeScale("success"),
      error: shadeScale("error"),

      // Grayscale

      black: "var(--color-black)",
      white: "var(--color-white)",
      gray: shadeScale("gray"),

      // Opacities of grayscale

      "gray-opacity": {
        1: opacityScale("gray-1"),
        12: opacityScale("gray-12"),
      },

      // Accent colors

      pink: shadeScale("pink"),
      yellow: shadeScale("yellow"),

      // Focus ring colors
      focus: {
        DEFAULT: "var(--color-border-focus)",
        yellow: "var(--color-yellow-3)",
      },

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
      22: "5.50rem",
      24: "6.00rem",
      26: "6.50rem",
      30: "7.50rem",
      40: "10.00rem",
      50: "12.50rem",
      64: "16.00rem",
      66: "16.25rem",
      70: "17.50rem",
      80: "20.00rem",
      90: "25.00rem",
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
      4: "4px",
      8: "8px",
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
      textColor: {
        default: "var(--color-text)",
        secondary: "var(--color-text-secondary)",
        disabled: "var(--color-text-disabled)",
        link: "var(--color-text-link)",
        "over-dark": "var(--color-text-over-dark)",
        "over-negative": "var(--color-text-over-negative)",
        "secondary-over-dark": "var(--color-text-secondary-over-dark)",
      },
      backgroundColor: {
        default: "var(--color-bg)",
        surface: "var(--color-bg-surface)",
        overlay: "var(--color-bg-overlay)",
        primary: "var(--color-bg-primary)",
        "primary-hover": "var(--color-bg-primary-hover)",
        secondary: "var(--color-bg-secondary)",
        "secondary-hover": "var(--color-bg-secondary-hover)",
        tertiary: "var(--color-bg-tertiary)",
        "tertiary-hover": "var(--color-bg-tertiary-hover)",
        "transparent-hover": "var(--color-bg-transparent-hover)",
        complementary: "var(--color-bg-complementary)",
        warning: "var(--color-bg-warning)",
        info: "var(--color-bg-info)",
        success: "var(--color-bg-success)",
        error: "var(--color-bg-error)",
        disabled: "var(--color-bg-disabled)",
        blur: "var(--color-bg-blur)",
        "curr-page": "var(--color-bg-curr-page, var(--color-bg))",
      },
      borderColor: {
        default: "var(--color-border)",
        hover: "var(--color-border-hover)",
        secondary: "var(--color-border-secondary)",
        "secondary-hover": "var(--color-border-secondary-hover)",
        tertiary: "var(--color-border-tertiary)",
        "transparent-hover": "var(--color-border-transparent-hover)",
        overlay: "var(--color-border-overlay)",
        focus: "var(--color-border-focus)",
        "bg-ring": "var(--color-border-bg-ring)",
        disabled: "var(--color-border-disabled)",
      },
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
        "ring-1.5": "inset 0 0 0 1.5px var(--color-bg-curr-page)",
        "el-2": "0 0.125rem 0.25rem rgba(0, 0, 0, 0.1)",
        "slim-filled": "inset 0 0 0 1.5px var(--color-bg-curr-page)",
        "bold-filled": "inset 0 0 0 3px var(--color-bg-curr-page)",
      },
      borderRadius: {
        inherit: "inherit",
      },
      outlineWidth: {
        1.5: "1.5px",
        3: "3px",
      },
      typography: () => ({
        DEFAULT: {
          css: {
            a: {
              textDecoration: "none",
              "&:hover": {
                "text-decoration": "underline",
              },
            },
          },
        },
      }),
      keyframes: {
        "new-highlight": {
          "0%,100%": { "--deg": "0deg" },
          "50%": { "--deg": "50deg" },
          "99.99%": { "--deg": "360deg" },
        },
      },
      animation: {
        "new-highlight": "new-highlight 5s linear infinite",
      },
    },
  },
  plugins: [
    require("@tailwindcss/typography"), // eslint-disable-line @typescript-eslint/no-require-imports
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
              "--tw-ring-offset-color": "var(--color-bg-curr-page)",
              "--tw-ring-color": value,
              "--tw-outline-color": value,
            }),
          ])
        ),
        {
          values: { ...theme("colors.focus") },
        }
      )
    }),
  ],
} satisfies Config
