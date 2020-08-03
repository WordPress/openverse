import { Vue as VueIntegration } from '@sentry/integrations'

const initSentry = ({ Sentry, dsn, Vue = null, ssr = false }) => {
  const host =
    (typeof document !== 'undefined' && document.location.hostname) || ''

  // Check if we're on production or staging based on url
  let environment =
    host.indexOf('search.') >= 0 || host.indexOf('ccsearch.') >= 0
      ? 'production'
      : 'staging'

  // override for local:
  if (process.env.NODE_ENV === 'development') {
    environment = 'development'
  }

  if (Sentry && dsn) {
    Sentry.init({
      dsn,
      environment,
      integrations: [
        new VueIntegration({
          Vue,
          attachProps: true,
          logErrors: environment === 'development',
        }),
      ],
    })
    Sentry.configureScope((scope) => {
      scope.setTag('SSR', ssr)
    })
  }
}

export default initSentry
