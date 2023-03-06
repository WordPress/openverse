import { computed } from "vue"
import { useContext } from "@nuxtjs/composition-api"

import type { Events, EventName } from "~/types/analytics"

import type { Context } from "@nuxt/types"

type ContextReturn = ReturnType<typeof useContext>

/**
 * Get Plausible props that work identically on the server-side and the
 * client-side. This excludes props that need `window`.
 *
 * @param $ua - the User-Agent information from `express-useragent`
 * @param i18n - the Nuxt i18n instance from `@nuxtjs/i18n`
 */
export const getIsomorphicProps = ({ $ua, i18n }: Context | ContextReturn) => ({
  timestamp: new Date().toISOString(),
  language: i18n.locale,
  ...($ua
    ? {
        ua: $ua.source,
        os: $ua.os,
        platform: $ua.platform,
        browser: $ua.browser,
        version: $ua.version,
      }
    : {}),
})

/**
 * Get Plausible props that work only on the client-side. This only includes
 * props that need `window`.
 */
export const getWindowProps = () => ({
  origin: window.location.origin,
  pathname: window.location.pathname,
  referrer: window.document.referrer,
  width: window.innerWidth,
  height: window.innerHeight,
})

/**
 * The `ctx` parameter must be supplied if using this composable outside the
 * bounds of the composition API.
 *
 * @param ctx - the Nuxt context
 */
export const useAnalytics = (ctx?: Context) => {
  const context = ctx ?? useContext()
  const { $plausible } = context

  /**
   * fields that should always be sent from custom events
   */
  const mandatoryProps = computed(() => ({
    ...getIsomorphicProps(context),
    ...getWindowProps(),
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
