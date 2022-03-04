import { isProd } from '~/utils/node-env'

// TODO: set correct targetOrigin of the parent window
const TARGET_ORIGIN = '*'

interface Message<T extends ResizeValue | UrlChangeValue> {
  type: 'resize' | 'urlChange'
  value: T
}

interface ResizeValue {
  height: number
}

interface UrlChangeValue {
  path: string
  title: string
}

/**
 * Send message to the outer window. Can only be called on client-side
 * because it uses `window` object.
 * @param debug - whether to log the messages from the parent
 * @param message - the message to emit to the parent window
 */
export const sendWindowMessage = <T extends UrlChangeValue | ResizeValue>({
  debug = !isProd,
  ...message
}: { debug?: boolean } & Message<T>) => {
  if (window.parent !== window) {
    window.parent.postMessage({ debug, ...message }, TARGET_ORIGIN)
  }
}
