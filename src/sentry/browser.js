import initSentry from './initSentry';

const init = () => initSentry(process.env.BROWSER_SENTRY_DSN);

export default init;
