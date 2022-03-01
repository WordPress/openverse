import { isProd } from '~/utils/node-env'

export const getLogger = (level: 'log' | 'warn' | 'error') =>
  isProd
    ? () => {
        // do nothing
      }
    : console[level]

export const warn = getLogger('warn')
export const log = getLogger('log')
