import initSentry from './initSentry';

const init = () => initSentry(process.env.SSR_SENTRY_DSN);

export default init;
