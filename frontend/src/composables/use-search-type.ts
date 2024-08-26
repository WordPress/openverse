import { useNuxtApp } from "#imports"

import { computed, ref } from "vue"

import {
  ALL_MEDIA,
  AUDIO,
  IMAGE,
  MODEL_3D,
  VIDEO,
  additionalSearchTypes,
  supportedSearchTypes,
  type SearchType,
} from "~/constants/media"

import { useSearchStore } from "~/stores/search"
import { useFeatureFlagStore } from "~/stores/feature-flag"

const icons = {
  [ALL_MEDIA]: "all",
  [AUDIO]: "audio",
  [IMAGE]: "image",
  [VIDEO]: "video",
  [MODEL_3D]: "model-3d",
} as const

const labels = {
  [ALL_MEDIA]: "searchType.all",
  [IMAGE]: "searchType.image",
  [AUDIO]: "searchType.audio",
  [VIDEO]: "searchType.video",
  [MODEL_3D]: "searchType.model3d",
} as const

export default function useSearchType({
  component = "Unknown",
}: { component?: string } = {}) {
  const {
    $i18n: { t },
    $sendCustomEvent,
  } = useNuxtApp()

  const activeType = computed<SearchType>(() => {
    return useSearchStore().searchType
  })

  const previousSearchType = ref(activeType.value)

  const featureFlagStore = useFeatureFlagStore()

  const additionalTypes = computed(() =>
    featureFlagStore.isOn("additional_search_types")
      ? additionalSearchTypes
      : []
  )
  const searchTypes = [...supportedSearchTypes]

  const setActiveType = (searchType: SearchType) => {
    if (previousSearchType.value === searchType) {
      return
    }

    $sendCustomEvent("CHANGE_CONTENT_TYPE", {
      previous: previousSearchType.value,
      next: searchType,
      component,
    })

    // `setActiveType` is called after the search middleware
    // ran and updated the search store state
    // TODO: Figure out why
    if (activeType.value === searchType) {
      return
    }
    useSearchStore().setSearchType(searchType)
    previousSearchType.value = searchType
  }

  const getSearchTypeProps = (searchType?: SearchType) => {
    const type = searchType ?? activeType.value
    return {
      label: t(labels[type]),
      icon: icons[type],
      searchType: type,
    }
  }

  return {
    setActiveType,
    activeType,
    getSearchTypeProps,
    types: searchTypes,
    icons,
    labels,
    additionalTypes,
  }
}
