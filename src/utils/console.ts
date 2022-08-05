import { isProd, isClient } from '~/utils/node-env'

export const getLogger = (level: 'log' | 'warn' | 'error') =>
  isProd && isClient
    ? () => {
        // do nothing
      }
    : console[level]

export const warn = getLogger('warn')
export const log = getLogger('log')
export const error = getLogger('error')
