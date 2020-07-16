import * as Sentry from '@sentry/node'
import initSentry from './initSentry'

const init = () => initSentry(Sentry, process.env.SSR_SENTRY_DSN)

export default init
