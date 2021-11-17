module.exports = {
  purge: ['src/**/*.{vue,js,jsx,ts,tsx,mdx}', './nuxt.config.js'],
  theme: {
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
      'dark-charcoal': '#30272e',
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
      'dark-charcoal-06': '#f3f2f2',
      'dark-charcoal-10': '#eae9ea',
      'dark-charcoal-20': '#d6d4d5',
      'dark-charcoal-30': '#c1bec0',
      'dark-charcoal-40': '#aca9ab',
      'dark-charcoal-50': '#989397',
      'dark-charcoal-60': '#837d82',
      'dark-charcoal-70': '#6e686d',
      'dark-charcoal-80': '#595258',

      // Special keywords
      tx: 'transparent',
      curr: 'currentColor',
    },
    fill: (theme) => theme('colors'),
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
      8: '2.00rem',
      10: '2.50rem',
      12: '3.00rem',
      14: '3.50rem',
      16: '4.00rem',
      20: '5.00rem',
      24: '6.00rem',
      30: '7.50rem',
      70: '17.50rem',
      80: '20.00rem',
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
    },
    ringOffsetWidth: {
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
      icons: ['"Vocabulary Icons"'],
    },
  },
  variants: {
    extend: {
      opacity: ['disabled'],
      ringColor: ['focus-visible'],
      ringOffsetWidth: ['focus-visible'],
      ringWidth: ['focus-visible'],
      borderWidth: ['focus', 'focus-within'],
      padding: ['focus', 'focus-within'],
    },
  },
  plugins: [require('tailwindcss-rtl')],
}
