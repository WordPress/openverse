import { computed } from "vue"

import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useSearchStore } from "~/stores/search"
import {
  IMAGE,
  isAdditionalSearchType,
  isSupportedMediaType,
} from "~/constants/media"
import { getAdditionalSources } from "~/utils/get-additional-sources"

export const useExternalSources = () => {
  /**
   * External sources search form shows the external sources for current search type, or for images if the search type is 'All Content'.
   */
  const externalSourcesType = computed(() => {
    const featureFlagStore = useFeatureFlagStore()
    const searchStore = useSearchStore()
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
    const searchStore = useSearchStore()
    const query = searchStore.searchQueryParams
    const type = externalSourcesType.value
    return getAdditionalSources(type, query)
  })

  return {
    externalSources,
    externalSourcesType,
  }
}
