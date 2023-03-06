import { useAnalytics } from "~/composables/use-analytics"

import type { Middleware } from "@nuxt/types"

/**
 * This middleware sends events to Plausible.
 *
 * - For the initial page load, executed on the server, it sends a
 *   `SERVER_RENDERED` event.
 * - For subsequent page loads, executed on the client, it sends a
 *   `VIEW_PAGE` event between every navigation.
 *
 * These events are in addition to the `pageview` events automatically sent by
 * the Plausible integration.
 *
 * @param context - the Nuxt context
 */
const pageViews: Middleware = async (context) => {
  const { from, route } = context

  if (process.client) {
    const { sendCustomEvent } = useAnalytics(context)
    sendCustomEvent("VIEW_PAGE", {
      name: route.name ?? "<no name>",
      pathname: route.fullPath, // Overrides `pathname` from mandatory payload.
      fromPathname: from.fullPath,
    })
  } else {
    const { sendCustomEventApi } = useAnalytics(context)
    await sendCustomEventApi("SERVER_RENDERED", {
      name: route.name ?? "<no name>",
    })
  }
}

export default pageViews
