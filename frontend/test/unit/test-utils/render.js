import { defu } from "defu"
import { renderSuspended } from "@nuxt/test-utils/runtime"
import { i18n } from "~~/test/unit/test-utils/i18n"

export const render = async (Component, options = {}) => {
  options = defu(options, {
    global: {
      plugins: [i18n],
    },
  })
  return await renderSuspended(Component, options)
}
