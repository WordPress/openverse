import * as Sentry from '@sentry/browser';

const init = () => {
  const options = { dsn: process.env.SSR_SENTRY_DSN };
  Sentry.init(options);
};

export default init;
