import { computed } from "vue"
import { useContext } from "@nuxtjs/composition-api"

import type { Events, EventName } from "~/types/analytics"

import type { Context } from "@nuxt/types"

export const useAnalytics = (context?: Context) => {
  const { $plausible, $ua, i18n } = context ?? useContext()

  /**
   * fields that should always be sent from custom events
   */
  const mandatoryProps = computed(() => ({
    timestamp: new Date().toISOString(),
    origin: window.location.origin,
    pathname: window.location.pathname,
    referrer: document.referrer,
    language: i18n.locale,
    width: window.innerWidth,
    height: window.innerHeight,
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
        ...mandatoryProps.value,
        ...payload, // can override mandatory props
      },
    })
  }

  return {
    sendCustomEvent,
  }
}
