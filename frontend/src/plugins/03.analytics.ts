import {
  defineNuxtPlugin,
  useRouter,
  useRuntimeConfig,
  useTrackEvent,
  useTrackPageview,
} from "#imports"

import type { SendCustomEvent } from "#shared/types/analytics"
import { useUiStore } from "~/stores/ui"

export default defineNuxtPlugin((nuxtApp) => {
  if (import.meta.server) {
    // Inject a noop on the server, as vue-plausible does not support SSR
    return {
      provide: {
        sendCustomEvent: (() => {}) as SendCustomEvent,
      },
    }
  }

  const uiStore = useUiStore()

  // The Plausible tracker only sends a pageview when the path changes. Also count
  // query-only navigations (new searches, filter changes), as the previous tracker did.
  if (useRuntimeConfig().public.plausible.autoPageviews) {
    useRouter().afterEach((to, from) => {
      if (
        from.matched.length &&
        to.path === from.path &&
        to.fullPath !== from.fullPath
      ) {
        nuxtApp.runWithContext(() => useTrackPageview())
      }
    })
  }

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
