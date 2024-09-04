import { useNuxtApp } from "#imports"

import { useFeatureFlagStore } from "~/stores/feature-flag"
import { createApiClient } from "~/data/api-service"

export function useApiClient() {
  const { $openverseApiToken } = useNuxtApp()
  const accessToken =
    typeof $openverseApiToken === "string" ? $openverseApiToken : undefined

  const featureFlagStore = useFeatureFlagStore()

  const fakeSensitive =
    featureFlagStore.isOn("fake_sensitive") &&
    featureFlagStore.isOn("fetch_sensitive")

  return createApiClient({ accessToken, fakeSensitive })
}
