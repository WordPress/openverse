import * as Sentry from '@sentry/browser'
import initSentry from './initSentry'

const init = () => initSentry(Sentry, process.env.BROWSER_SENTRY_DSN)

export default init
