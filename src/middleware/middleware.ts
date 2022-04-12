import { sendWindowMessage } from '~/utils/send-message'
import { useNavStore } from '~/stores/nav'

import type { Context, Middleware } from '@nuxt/types'

/**
 * In embedded mode, the app sends its url
 * to the outer window to improve the user experience.
 *
 * The app is in embedded mode by default. To set it to
 * standalone mode with larger header and a footer,
 * add `?embedded=false` to the end of the URL.
 *
 * Messages sent to the outer window have the following format:
 * `{type: <event type>, value: <event value>}`.
 * Currently, one event type is used:
 * - `urlChange` sends the relative path of the URL on every URL change.
 */
const middleware: Middleware = ({ query, route, $pinia }: Context) => {
  const navStore = useNavStore($pinia)

  if ('embedded' in query) {
    navStore.setIsEmbedded(query.embedded === 'true')
  }
  if (process.client) {
    sendWindowMessage({
      type: 'urlChange',
      value: { path: route.fullPath, title: document.title },
    })
  }

  if (process.client && navStore.isReferredFromCc) {
    navStore.setIsReferredFromCc(false)
  }
}
export default middleware
