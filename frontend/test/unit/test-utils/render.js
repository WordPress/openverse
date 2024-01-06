import { renderSuspended } from "@nuxt/test-utils/runtime"

export const render = (Component, options = {}) => {
  return renderSuspended(Component, options)
}
