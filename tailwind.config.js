module.exports = {
  purge: ['src/**/*.{vue,js,jsx,ts,tsx}', './nuxt.config.js'],
  theme: {
    screens: {
      // Determined by the lower bound of screen width
      tab: '768px',
      desk: '1024px',
      wide: '1216px',
      hd: '1408px',
    },
    colors: {
      // Accents
      tomato: '#e23600',
      gold: '#efbe00',
      'forest-green': '#008300',
      'dark-turquoise': '#05b5da',
      'dark-slate-blue': '#3c5c99',
      'trans-blue': '#3e58e1',

      // Grayscale
      black: 'black',
      'dark-gray': '#767676', // rgb(118, 118, 188)
      gray: '#b0b0b0', // rgb(176, 176, 176)
      'light-gray': '#d8d8d8', // rgb(216, 216, 216)
      white: 'white',

      // Special keywords
      tx: 'transparent',
      curr: 'currentColor',
    },
    spacing: {
      // Indexed by multiples of baseline (~ `0.25rem`)
      1: '0.25rem',
      2: '0.50rem',
      4: '1.00rem',
      6: '1.50rem',
      8: '2.00rem',
      10: '2.50rem',
      12: '3.00rem',
      16: '4.00rem',
      24: '6.00rem',
    },
    fontSize: {
      // Body
      sm: '0.80rem',
      base: '1.00rem',
      lg: '1.12rem',
      lgr: '1.25rem',

      // Headings, where h[n] => [7-n]xl
      '1xl': '1.12rem',
      '2xl': '1.25rem',
      '3xl': '1.43rem',
      '4xl': '1.75rem',
      '5xl': '2.25rem',
      '6xl': '3.56rem',
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
    extend: {},
  },
  plugins: [],
}
