import { sendWindowMessage } from '~/utils/send-message'
import { useNavigationStore } from '~/stores/navigation'
import { useProviderStore } from '~/stores/provider'
import { useFeatureFlagStore } from '~/stores/feature-flag'

import type { Middleware } from '@nuxt/types'

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
const middleware: Middleware = async ({ app, query, route, $pinia }) => {
  /* Nav store */

  const navigationStore = useNavigationStore($pinia)

  if ('embedded' in query) {
    navigationStore.setIsEmbedded(query.embedded === 'true')
  }
  if (process.client) {
    sendWindowMessage({
      type: 'urlChange',
      value: { path: route.fullPath, title: document.title },
    })
  }

  if (process.client && navigationStore.isReferredFromCc) {
    navigationStore.setIsReferredFromCc(false)
  }

  /* Provider store */

  const providerStore = useProviderStore($pinia)
  await providerStore.fetchMediaProviders()

  /* Feature flag store */

  const featureFlagStore = useFeatureFlagStore($pinia)
  featureFlagStore.initFromCookies(app.$cookies.get('features') ?? {})
}
export default middleware
