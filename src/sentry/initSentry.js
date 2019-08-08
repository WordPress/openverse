const initSentry = (Sentry, dsn) => {
  if (dsn) {
    Sentry.init({ dsn });
  }
};

export default initSentry;
