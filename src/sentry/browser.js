import * as Sentry from '@sentry/browser';

const init = () => {
  const options = { dsn: process.env.BROWSER_SENTRY_DSN };
  if (options.dsn) {
    Sentry.init(options);
  }
};

export default init;
