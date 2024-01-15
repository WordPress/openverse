import type { Sentry } from "@sentry/node"

declare module "h3" {
  interface H3EventContext {
    $sentry?: Sentry
  }
}
