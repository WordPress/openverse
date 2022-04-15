import { sendWindowMessage } from '~/utils/send-message'
import { useNavigationStore } from '~/stores/navigation'

import type { Plugin } from '@nuxt/types'

/**
 * In embedded mode, we need to notify the outer window of the current URL.
 * Normally, the `src/middleware/embed.js` middleware does this on every
 * route change. However, it does not run on the initial render.
 * So, for the initial render this plugin runs when router is ready.
 */
const urlChangePlugin: Plugin = ({ app, $pinia }): void => {
  app.router?.onReady(() => {
    const isEmbedded = useNavigationStore($pinia).isEmbedded
    if (process.client && isEmbedded && app.router) {
      sendWindowMessage({
        type: 'urlChange',
        value: {
          path: app.router.currentRoute.fullPath,
          title: document.title,
        },
      })
    }
  })
}

export default urlChangePlugin
