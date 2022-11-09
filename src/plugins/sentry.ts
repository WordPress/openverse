import * as Sentry from '@sentry/browser'

/**
 * adds render context to the error event that is sent to sentry
 */

Sentry.setContext('render context', {
  platform: process.client ? 'client' : 'server',
})
