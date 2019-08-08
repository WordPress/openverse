import Sentry from '@sentry/node';

const initSentry = (dsn) => {
  if (dsn) {
    Sentry.init({ dsn });
  }
};

export default initSentry;
