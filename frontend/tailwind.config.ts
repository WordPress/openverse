import defaultTheme from "tailwindcss/defaultTheme"
import plugin from "tailwindcss/plugin"

import { SCREENS } from "./src/constants/screens"
import { Z_INDICES } from "./src/constants/z-indices"

import type { Config } from "tailwindcss"

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
      info: {
        1: "var(--color-info-1)",
        2: "var(--color-info-2)",
        3: "var(--color-info-3)",
        4: "var(--color-info-4)",
        5: "var(--color-info-5)",
        6: "var(--color-info-6)",
        7: "var(--color-info-7)",
        8: "var(--color-info-8)",
        9: "var(--color-info-9)",
        10: "var(--color-info-10)",
        11: "var(--color-info-11)",
        12: "var(--color-info-12)",
        13: "var(--color-info-13)",
      },
      warning: {
        1: "var(--color-warning-1)",
        2: "var(--color-warning-2)",
        3: "var(--color-warning-3)",
        4: "var(--color-warning-4)",
        5: "var(--color-warning-5)",
        6: "var(--color-warning-6)",
        7: "var(--color-warning-7)",
        8: "var(--color-warning-8)",
        9: "var(--color-warning-9)",
        10: "var(--color-warning-10)",
        11: "var(--color-warning-11)",
        12: "var(--color-warning-12)",
        13: "var(--color-warning-13)",
      },
      success: {
        1: "var(--color-success-1)",
        2: "var(--color-success-2)",
        3: "var(--color-success-3)",
        4: "var(--color-success-4)",
        5: "var(--color-success-5)",
        6: "var(--color-success-6)",
        7: "var(--color-success-7)",
        8: "var(--color-success-8)",
        9: "var(--color-success-9)",
        10: "var(--color-success-10)",
        11: "var(--color-success-11)",
        12: "var(--color-success-12)",
        13: "var(--color-success-13)",
      },
      error: {
        1: "var(--color-error-1)",
        2: "var(--color-error-2)",
        3: "var(--color-error-3)",
        4: "var(--color-error-4)",
        5: "var(--color-error-5)",
        6: "var(--color-error-6)",
        7: "var(--color-error-7)",
        8: "var(--color-error-8)",
        9: "var(--color-error-9)",
        10: "var(--color-error-10)",
        11: "var(--color-error-11)",
        12: "var(--color-error-12)",
        13: "var(--color-error-13)",
      },
      black: "var(--color-black)",
      gray: {
        DEFAULT: "var(--color-gray)",
        "dark-gray": "var(--color-dark-gray)",
        "light-gray": "var(--color-light-gray)",
        1: "var(--color-gray-1)",
        2: "var(--color-gray-2)",
        3: "var(--color-gray-3)",
        4: "var(--color-gray-4)",
        5: "var(--color-gray-5)",
        6: "var(--color-gray-6)",
        7: "var(--color-gray-7)",
        8: "var(--color-gray-8)",
        9: "var(--color-gray-9)",
        10: "var(--color-gray-10)",
        11: "var(--color-gray-11)",
        12: "var(--color-gray-12)",
        13: "var(--color-gray-13)",
      },
      "gray-opacity": {
        1: {
          10: "var(--color-gray-1-10)",
          20: "var(--color-gray-1-20)",
          30: "var(--color-gray-1-30)",
          40: "var(--color-gray-1-40)",
          50: "var(--color-gray-1-50)",
          60: "var(--color-gray-1-60)",
          70: "var(--color-gray-1-70)",
          80: "var(--color-gray-1-80)",
          90: "var(--color-gray-1-90)",
        },
        12: {
          10: "var(--color-gray-12-10)",
          20: "var(--color-gray-12-20)",
          30: "var(--color-gray-12-30)",
          40: "var(--color-gray-12-40)",
          50: "var(--color-gray-12-50)",
          60: "var(--color-gray-12-60)",
          70: "var(--color-gray-12-70)",
          80: "var(--color-gray-12-80)",
          90: "var(--color-gray-12-90)",
        },
        13: {
          0: "var(--color-gray-13-0)",
        },
      },
      white: {
        DEFAULT: "var(--color-white)",
        0: "var(--color-white-0)",
      },
      pink: {
        1: "var(--color-pink-1)",
        2: "var(--color-pink-2)",
        3: "var(--color-pink-3)",
        4: "var(--color-pink-4)",
        5: "var(--color-pink-5)",
        6: "var(--color-pink-6)",
        7: "var(--color-pink-7)",
        8: "var(--color-pink-8)",
        9: "var(--color-pink-9)",
        10: "var(--color-pink-10)",
        11: "var(--color-pink-11)",
        12: "var(--color-pink-12)",
        13: "var(--color-pink-13)",
      },
      yellow: {
        1: "var(--color-yellow-1)",
        2: "var(--color-yellow-2)",
        3: "var(--color-yellow-3)",
        4: "var(--color-yellow-4)",
        5: "var(--color-yellow-5)",
        7: "var(--color-yellow-7)",
        8: "var(--color-yellow-8)",
        9: "var(--color-yellow-9)",
        10: "var(--color-yellow-10)",
        11: "var(--color-yellow-11)",
        12: "var(--color-yellow-12)",
        13: "var(--color-yellow-13)",
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
      textColor: {
        default: "var(--color-text)",
        secondary: "var(--color-text-secondary)",
        disabled: "var(--color-text-disabled)",
        link: "var(--color-text-link)",
        "over-dark": "var(--color-text-over-dark)",
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
        zero: "var(--color-bg-zero)",
      },
      borderColor: {
        default: "var(--color-border)",
        hover: "var(--color-border-hover)",
        secondary: "var(--color-border-secondary)",
        "secondary-hover": "var(--color-border-secondary-hover)",
        tertiary: "var(--color-border-tertiary)",
        "transparent-hover": "var(--color-border-transparent-hover)",
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
        {
          values: { ...theme("colors"), DEFAULT: theme("borderColor.focus") },
        }
      )
    }),
  ],
} satisfies Config
