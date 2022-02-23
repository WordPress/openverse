export const warn =
  process.env.NODE_ENV !== 'production'
    ? console.warn
    : () => {
        /* silence warnings in production */
      }
