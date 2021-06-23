// TODO: set correct targetOrigin of the parent window
const TARGET_ORIGIN = '*'

/**
 * Send message to the outer window. Can only be called on client-side
 * because it uses `window` object.
 * @typedef {Object} message
 * @property {'resize'|'changeUrl'} type - event that triggers the message
 * @property {Object} value - the value of event
 */
export const sendWindowMessage = (message) => {
  window.parent.postMessage(
    {
      debug: config.dev,
      type: message.type,
      value: message.value,
    },
    TARGET_ORIGIN
  )
}
