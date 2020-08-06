import * as Sentry from '@sentry/node'
import initSentry from './initSentry'

const init = () =>
  initSentry({ Sentry, dsn: process.env.SENTRY_DSN, ssr: true })

export default init
