// eslint-disable-next-line no-restricted-imports
import * as pinia from "pinia"
import { vi } from "vitest"

export const createPinia = () =>
  pinia.createPinia().use(() => ({
    $nuxt: {
      $openverseApiToken: "",
      $sentry: {
        captureException: vi.fn(),
        captureEvent: vi.fn(),
      },
      $cookies: {
        set: vi.fn(),
        get: vi.fn(),
        setAll: vi.fn(),
      },
      i18n: {
        localeProperties: {
          code: "es",
          translated: 100,
          name: "Spanish",
        },
      },
      error: vi.fn(),
      localePath: vi.fn(),
    },
  }))

export const setActivePinia = pinia.setActivePinia

export const PiniaVuePlugin = pinia.PiniaVuePlugin
