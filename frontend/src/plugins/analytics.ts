import { defineNuxtPlugin, useTrackEvent } from "#imports"

import type { Events, EventName } from "~/types/analytics"
import { useUiStore } from "~/stores/ui"
import { useFeatureFlagStore } from "~/stores/feature-flag"

type SendCustomEvent = <T extends EventName>(
  name: T,
  payload: Events[T]
) => void

export default defineNuxtPlugin(() => {
  if (import.meta.server) {
    // Inject a noop on the server, as vue-plausible does not support SSR
    return {
      provide: {
        sendCustomEvent: (() => {}) as SendCustomEvent,
      },
    }
  }

  const uiStore = useUiStore()
  const featureFlagStore = useFeatureFlagStore()

  featureFlagStore.syncAnalyticsWithLocalStorage()

  const sendCustomEvent: SendCustomEvent = (name, payload) => {
    useTrackEvent(name, {
      props: {
        breakpoint: uiStore.breakpoint,
        width: window.innerWidth,
        height: window.innerHeight,
        ...payload,
      },
    })
  }

  return {
    provide: {
      sendCustomEvent,
    },
  }
})
