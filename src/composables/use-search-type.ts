import { computed, ref } from '@nuxtjs/composition-api'

import {
  ALL_MEDIA,
  AUDIO,
  IMAGE,
  MODEL_3D,
  VIDEO,
  additionalSearchTypes,
  supportedSearchTypes,
  SearchType,
} from '~/constants/media'

import { useSearchStore } from '~/stores/search'
import { useFeatureFlagStore } from '~/stores/feature-flag'

import allIcon from '~/assets/icons/all-content.svg'
import audioIcon from '~/assets/icons/audio-content.svg'
import imageIcon from '~/assets/icons/image-content.svg'
import videoIcon from '~/assets/icons/video-content.svg'
import model3dIcon from '~/assets/icons/model-3d.svg'

const icons = {
  [ALL_MEDIA]: allIcon,
  [AUDIO]: audioIcon,
  [IMAGE]: imageIcon,
  [VIDEO]: videoIcon,
  [MODEL_3D]: model3dIcon,
} as const

export default function useSearchType() {
  const activeType = computed(() => useSearchStore().searchType)

  const previousSearchType = ref(activeType.value)

  const featureFlagStore = useFeatureFlagStore()

  const additionalTypes = computed(() =>
    featureFlagStore.isOn('external_sources') ? additionalSearchTypes : []
  )
  const searchTypes = [...supportedSearchTypes]

  const setActiveType = (searchType: SearchType) => {
    if (previousSearchType.value === searchType) return
    useSearchStore().setSearchType(searchType)
    previousSearchType.value = searchType
  }

  return {
    setActiveType,
    activeType,
    types: searchTypes,
    icons,
    additionalTypes,
  }
}

export type UseSearchTypeReturn = ReturnType<typeof useSearchType>
