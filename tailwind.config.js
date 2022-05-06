const { SCREEN_SIZES } = require('./src/constants/screens')

module.exports = {
  content: [
    'src/**/*.{vue,js,jsx,ts,tsx,mdx}',
    './nuxt.config.js',
    './tailwind.safelist.txt',
  ],
  theme: {
    screens: Object.fromEntries(
      Array.from(SCREEN_SIZES, ([name, width]) => [
        name,
        `${width}px`,
      ]).reverse()
    ),
    colors: {
      // Accents
      tomato: '#e23600',
      gold: '#efbe00',
      'forest-green': '#008300',
      'dark-turquoise': '#05b5da',
      'dark-slate-blue': '#3c5c99',
      'trans-blue': '#3e58e1',
      'trans-blue-action': '#5067e4',
      'dark-blue': '#23282d',

      // Brand
      yellow: '#ffe033',
      pink: '#c52b9b',
      // Active
      'dark-pink': '#7c2264',

      // Grayscale
      black: 'black',
      'dark-gray': '#767676', // rgb(118, 118, 188)
      gray: '#b0b0b0', // rgb(176, 176, 176)
      'light-gray': '#d8d8d8', // rgb(216, 216, 216)
      white: 'white',

      // WordPress
      'admin-gray': '#dcdcde',

      // Dark Charcoal
      'dark-charcoal': {
        DEFAULT: '#30272e',
        '06': '#f3f2f2', // rgb(243, 242, 242)
        10: '#eae9ea', // rgb(234, 233, 234)
        20: '#d6d4d5',
        30: '#c1bec0',
        40: '#aca9ab',
        50: '#989397',
        60: '#837d82',
        70: '#6e686d',
        80: '#595258',
      },

      // Special keywords
      tx: 'transparent',
      curr: 'currentColor',
      current: 'currentColor',
    },
    spacing: {
      // Constants
      '0.5px': '0.5px',
      px: '1px',
      '1.5px': '1.5px',
      ch: '1ch',
      ex: '1ex',
      half: '50%',
      full: '100%',

      // Indexed by multiples of baseline (~ `0.25rem`)
      0: '0',
      0.5: '0.125rem',
      1: '0.25rem',
      2: '0.50rem',
      3: '0.75rem',
      4: '1.00rem',
      5: '1.25rem',
      6: '1.50rem',
      7: '1.75rem',
      8: '2.00rem',
      10: '2.50rem',
      12: '3.00rem',
      14: '3.50rem',
      15: '3.75rem',
      16: '4.00rem',
      20: '5.00rem',
      24: '6.00rem',
      30: '7.50rem',
      40: '10.00rem',
      64: '16.00rem',
      70: '17.50rem',
      80: '20.00rem',
      120: '30.00rem',
    },
    ringWidth: {
      DEFAULT: '1.5px',
      0: 0,
    },
    borderWidth: {
      0: '0px',
      DEFAULT: '1px',
      1.5: '1.5px',
      2: '2px',
      3: '3px',
    },
    ringOffsetWidth: {
      0: '0px',
      1: '1px',
      2: '2px',
    },
    fontSize: {
      // Deprecated
      lg: '1.12rem',
      lgr: '1.43rem',

      // Headings, where h[n] => [7-n]xl
      '6xl': [
        '2.0000rem', // 32px
        '1.3', // 130%
      ],
      '5xl': [
        '1.7500rem', // 28px
        '1.3', // 130%
      ],
      '4xl': [
        '1.5000rem', // 24px
        '1.3', // 130%
      ],
      '3xl': [
        '1.1875rem', // 19px
        '1.3', // 130%
      ],
      '2xl': [
        '1.0000rem', // 16px
        '1.3', // 130%
      ],

      // Content
      base: [
        '0.8750rem', // 14px
        '1.5', // 150%
      ],
      sm: [
        // small, eg. label
        '0.8125rem', // 13px
        '1.3', // 130%
      ],
      sr: [
        // smaller, eg. caption, category
        '0.7500rem', // 12px
        '1.3', // 130%
      ],
      xs: [
        // extra small, eg. time
        '0.6875rem', // 11px
        '1.2', // 120%
      ],
    },
    lineHeights: {
      normal: '1.5',
      snug: '1.3',
      tight: '1.2',
      none: '1.0',
    },
    flexGrow: {
      0: 0,
      DEFAULT: 1,
      2: 2,
    },
    fontFamily: {
      system: [
        'ui-sans-serif',
        'system-ui',
        '-apple-system',
        'BlinkMacSystemFont',
        '"Segoe UI"',
        'Roboto',
        '"Helvetica Neue"',
        'Arial',
        '"Noto Sans"',
        '"Oxygen"',
        '"Cantarell"',
        '"Fira Sans"',
        '"Droid Sans"',
        'sans-serif',
        '"Apple Color Emoji"',
        '"Segoe UI Emoji"',
        '"Segoe UI Symbol"',
        '"Noto Color Emoji"',
      ],
      heading: ['"Inter"', 'sans-serif'],
      mono: ['"JetBrains Mono"', 'monospace'],
      sans: ['"Inter"', 'sans-serif'],
      serif: ['Times New Roman'],
      icons: ['"Vocabulary Icons"'],
    },
    extend: {
      scale: {
        '-100': '-1',
      },
      boxShadow: {
        ring: 'inset 0 0 0 1px white',
        'ring-1.5': 'inset 0 0 0 1.5px white',
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            '--tw-prose-body': theme('colors.dark-charcoal'),
            '--tw-prose-headings': theme('colors.dark-charcoal'),
            '--tw-prose-links': theme('colors.pink'),
            a: {
              textDecoration: 'none',
              '&:hover': {
                'text-decoration': 'underline',
              },
            },
          },
        },
      }),
    },
  },
  plugins: [
    require('tailwindcss-rtl'),
    require('@tailwindcss/line-clamp'),
    require('@tailwindcss/typography'),
  ],
}
