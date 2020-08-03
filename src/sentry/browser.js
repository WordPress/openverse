import * as Sentry from '@sentry/browser'
import initSentry from './initSentry'

const init = (Vue) => initSentry({ Sentry, dsn: process.env.SENTRY_DSN, Vue })

export default init
