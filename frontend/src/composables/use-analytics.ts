import { computed } from "vue"
import { useContext } from "@nuxtjs/composition-api"

import type { Events, EventName } from "~/types/analytics"
import { useUiStore } from "~/stores/ui"

/**
 * The `ctx` parameter must be supplied if using this composable outside the
 * bounds of the composition API.
 */
export const useAnalytics = () => {
  const { $plausible, $ua, i18n } = useContext()
  const uiStore = useUiStore()

  /**
   * the Plausible props that work identically on the server-side and the
   * client-side; This excludes props that need `window`.
   */
  const isomorphicProps = computed(() => ({
    timestamp: new Date().toISOString(),
    language: i18n.locale,
    breakpoint: uiStore.breakpoint,
    ...($ua
      ? {
          ua: $ua.source,
          os: $ua.os,
          platform: $ua.platform,
          browser: $ua.browser,
          version: $ua.version,
        }
      : {}),
  }))

  /**
   * the Plausible props that work only on the client-side; This only includes
   * props that need `window`.
   */
  const windowProps = computed(() =>
    window
      ? {
          origin: window.location.origin,
          pathname: window.location.pathname,
          referrer: window.document.referrer,
          width: window.innerWidth,
          height: window.innerHeight,
        }
      : {}
  )

  /**
   * Send a custom event to Plausible. Mandatory props are automatically merged
   * with the event-specific props.
   *
   * @param name - the name of the event being recorded
   * @param payload - the additional information to record about the event
   */
  const sendCustomEvent = <T extends EventName>(
    name: T,
    payload: Events[T]
  ) => {
    $plausible.trackEvent(name, {
      props: {
        ...isomorphicProps.value,
        ...windowProps.value,
        ...payload, // can override mandatory props
      },
    })
  }

  return {
    sendCustomEvent,
  }
}
