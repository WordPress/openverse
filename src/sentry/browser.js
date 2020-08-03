import * as Sentry from '@sentry/browser'
import initSentry from './initSentry'

const init = (Vue) =>
  initSentry({ Sentry, dsn: process.env.BROWSER_SENTRY_DSN, Vue })

export default init
