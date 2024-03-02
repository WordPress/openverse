import type { Events, EventName } from "~/types/analytics"
import { useUiStore } from "~/stores/ui"
import { useFeatureFlagStore } from "~/stores/feature-flag"

import { log } from "~/utils/console"

import type { Plugin } from "@nuxt/types"

type SendCustomEvent = <T extends EventName>(
  name: T,
  payload: Events[T]
) => void

declare module "@nuxt/types" {
  interface Context {
    $sendCustomEvent: SendCustomEvent
  }
}

export default (function analyticsPlugin(context, inject) {
  if (process.server) {
    // Inject a noop on the server, as vue-plausible does not support SSR
    inject("sendCustomEvent", (() => {}) as SendCustomEvent)
    return
  }

  const uiStore = useUiStore(context.$pinia)
  const featureFlagStore = useFeatureFlagStore(context.$pinia)

  featureFlagStore.syncAnalyticsWithLocalStorage()

  const sendCustomEvent: SendCustomEvent = (name, payload) => {
    log(`Analytics event: ${name}`, payload)
    context.$plausible.trackEvent(name, {
      props: {
        breakpoint: uiStore.breakpoint,
        width: window.innerWidth,
        height: window.innerHeight,
        ...payload,
      },
    })
  }

  inject("sendCustomEvent", sendCustomEvent)
} satisfies Plugin)
