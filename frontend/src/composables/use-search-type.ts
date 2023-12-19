import { useI18n } from "#imports"

import { computed, ref } from "vue"

import {
  ALL_MEDIA,
  AUDIO,
  IMAGE,
  MODEL_3D,
  VIDEO,
  additionalSearchTypes,
  supportedSearchTypes,
  SearchType,
} from "~/constants/media"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { useFeatureFlagStore } from "~/stores/feature-flag"

import { useAnalytics } from "~/composables/use-analytics"

import { useComponentName } from "./use-component-name"

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

export default function useSearchType() {
  const i18n = useI18n()
  const componentName = useComponentName()
  const analytics = useAnalytics()

  const activeType = computed(() => useSearchStore().searchType)

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

    analytics.sendCustomEvent("CHANGE_CONTENT_TYPE", {
      previous: previousSearchType.value,
      next: searchType,
      component: componentName,
    })
    useSearchStore().setSearchType(searchType)
    useMediaStore().clearMedia()
    previousSearchType.value = searchType
  }

  const getSearchTypeProps = (searchType?: SearchType) => {
    const type = searchType ?? activeType.value
    return {
      label: i18n.t(labels[type]),
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
