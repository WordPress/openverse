import { useFeatureFlagStore } from "~/stores/feature-flag"

import type { Middleware } from "@nuxt/types"

export const collectionMiddleware: Middleware = async ({
  $pinia,
  error: nuxtError,
}) => {
  if (!useFeatureFlagStore($pinia).isOn("additional_search_views")) {
    nuxtError({
      statusCode: 404,
      message: "Additional search views are not enabled",
    })
  }
}
