const initSentry = (Sentry, dsn) => {
  if (Sentry && dsn) {
    Sentry.init({ dsn })
  }
}

export default initSentry
