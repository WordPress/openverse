import { defu } from "defu"

import { i18n } from "~~/test/unit/test-utils/i18n"
import { renderSuspended } from "~~/test/unit/test-utils/render-suspended"

export const render = async (Component, options = {}) => {
  options = defu(options, {
    global: {
      plugins: [i18n],
    },
  })
  return await renderSuspended(Component, options)
}
