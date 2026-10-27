import { defineNuxtPlugin, useTrackEvent } from "#imports"

import type { SendCustomEvent } from "#shared/types/analytics"
import { useUiStore } from "~/stores/ui"

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

  const sendCustomEvent: SendCustomEvent = (name, payload) => {
    useTrackEvent(name, {
      // The tracker types props as strings, but Plausible accepts any scalar value.
      props: {
        breakpoint: uiStore.breakpoint,
        width: window.innerWidth,
        height: window.innerHeight,
        ...payload,
      } as unknown as Record<string, string>,
    })
  }

  return {
    provide: {
      sendCustomEvent,
    },
  }
})
