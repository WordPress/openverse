import VueI18n from "~/vue-i18n"

import type { Sentry } from "@sentry/node"

declare module "h3" {
  interface H3EventContext {
    $sentry?: Sentry
  }
}

declare module "@vue/runtime-core" {
  interface ComponentCustomProperties {
    $t: typeof VueI18n.prototype.t
  }
}

export {}
