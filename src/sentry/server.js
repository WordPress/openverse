import Sentry from '@sentry/node';

const init = () => Sentry.init({ dsn: process.env.SSR_SENTRY_DSN });

export default init;
