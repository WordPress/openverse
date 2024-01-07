import { computed } from "vue"

import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useSearchStore } from "~/stores/search"
import {
  IMAGE,
  isAdditionalSearchType,
  isSupportedMediaType,
} from "~/constants/media"
import { getAdditionalSources } from "~/utils/get-additional-sources"

/**
 * This component uses `useStore` composables, and should only be called from within a component's setup function.
 */
export const useExternalSources = () => {
  const featureFlagStore = useFeatureFlagStore()
  const searchStore = useSearchStore()
  /**
   * Show the sources of the current media type, or fall back to "image"
   * when the search type is not supported.
   */
  const externalSourcesType = computed(() => {
    const searchType = searchStore.searchType
    if (
      isSupportedMediaType(searchType) ||
      (featureFlagStore.isOn("additional_search_types") &&
        isAdditionalSearchType(searchType))
    ) {
      return searchType
    }
    return IMAGE
  })
  const externalSources = computed(() => {
    const query = searchStore.apiSearchQueryParams
    const type = externalSourcesType.value
    return getAdditionalSources(type, query)
  })

  return {
    externalSources,
    externalSourcesType,
  }
}
