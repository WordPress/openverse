import { computed, ref } from '@nuxtjs/composition-api'

import { supportedSearchTypes } from '~/constants/media'

import { useSearchStore } from '~/stores/search'

import allIcon from '~/assets/icons/all-content.svg'
import audioIcon from '~/assets/icons/audio-content.svg'
import imageIcon from '~/assets/icons/image-content.svg'

const icons = {
  all: allIcon,
  audio: audioIcon,
  image: imageIcon,
}
const searchTypes = [...supportedSearchTypes]

export default function useSearchType() {
  const activeType = computed(() => useSearchStore().searchType)
  const previousSearchType = ref(activeType.value)
  const setActiveType = (searchType) => {
    if (previousSearchType.value === searchType) return
    useSearchStore().setSearchType(searchType)
    previousSearchType.value = searchType
  }
  return {
    setActiveType,
    activeType,
    types: searchTypes,
    icons,
  }
}
