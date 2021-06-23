// TODO: set correct targetOrigin of the parent window
const TARGET_ORIGIN = '*'

/**
 * Send message to the outer window. Can only be called on client-side
 * because it uses `window` object.
 * @typedef {Object} message
 * @property {boolean} debug - whether more verbose debug output should be used
 * @property {'resize'|'changeUrl'} type - event that triggers the message
 * @property {Object} value - the value of event
 */
export const sendWindowMessage = (message) => {
  if (window.parent !== window) {
    window.parent.postMessage(message, TARGET_ORIGIN)
  }
}
