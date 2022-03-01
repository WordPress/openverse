import { isProd } from '~/utils/node-env'

// TODO: set correct targetOrigin of the parent window
const TARGET_ORIGIN = '*'

/**
 * Send message to the outer window. Can only be called on client-side
 * because it uses `window` object.
 * @param {Object} message
 * @param {boolean} [message.debug] - whether more verbose debug output should be used
 * @param {'resize'|'changeUrl'} message.type - event that triggers the message
 * @param {any} message.value - the value of event
 */
export const sendWindowMessage = ({ debug = !isProd, ...message }) => {
  if (window.parent !== window) {
    window.parent.postMessage({ debug, ...message }, TARGET_ORIGIN)
  }
}
