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

import { useSearchStore } from "~/stores/search"
import { useFeatureFlagStore } from "~/stores/feature-flag"

import { useI18n } from "~/composables/use-i18n"

const icons = {
  [ALL_MEDIA]: "all",
  [AUDIO]: "audio",
  [IMAGE]: "image",
  [VIDEO]: "video",
  [MODEL_3D]: "model-3d",
} as const

const labels = {
  [ALL_MEDIA]: "search-type.all",
  [IMAGE]: "search-type.image",
  [AUDIO]: "search-type.audio",
  [VIDEO]: "search-type.video",
  [MODEL_3D]: "search-type.model-3d",
} as const

export default function useSearchType() {
  const i18n = useI18n()
  const activeType = computed(() => useSearchStore().searchType)

  const previousSearchType = ref(activeType.value)

  const featureFlagStore = useFeatureFlagStore()

  const additionalTypes = computed(() =>
    featureFlagStore.isOn("external_sources") ? additionalSearchTypes : []
  )
  const searchTypes = [...supportedSearchTypes]

  const setActiveType = (searchType: SearchType) => {
    if (previousSearchType.value === searchType) return
    useSearchStore().setSearchType(searchType)
    previousSearchType.value = searchType
  }

  const getSearchTypeProps = (searchType?: SearchType) => {
    const type = searchType ?? activeType.value
    return {
      label: i18n.t(labels[type]).toString(),
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
