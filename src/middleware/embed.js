import { SET_EMBEDDED } from '~/store-modules/mutation-types'
import { sendWindowMessage } from '~/utils/sendMessage'
import config from '../../nuxt.config.js'

/**
 * In embedded mode, the app sends its size and url
 * to the outer window to improve the user experience.
 *
 * The app is in embedded mode by default. To set it to
 * standalone mode with larger header and a footer,
 * add `?embedded=false` to the end of the URL.
 *
 * Messages sent to the outer window have the following format:
 * {type: <event type>, value: <event value>}.
 * Currently, two event types are used:
 * - `resize` sends the height of the window (see `src/mixins/iframeHeight.js`)
 * - `urlChange` sends the relative path of the URL on every URL change.
 */
export default function ({ store, query, route }) {
  if ('embedded' in query) {
    const isEmbedded = query.embedded === 'true'
    store.commit(SET_EMBEDDED, { isEmbedded })
  }
  if (process.client) {
    sendWindowMessage({
      debug: config.dev,
      type: 'urlChange',
      value: { path: route.fullPath, title: document.title },
    })
  }
}
