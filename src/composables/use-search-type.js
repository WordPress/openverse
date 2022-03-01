import { computed, ref, useContext } from '@nuxtjs/composition-api'

import { supportedSearchTypes } from '~/constants/media'
import { SEARCH } from '~/constants/store-modules'
import { UPDATE_QUERY } from '~/constants/action-types'

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
  const { store } = useContext()

  const activeType = computed(() => store.state.search.searchType)
  const previousSearchType = ref(activeType.value)
  const setActiveType = async (searchType) => {
    if (previousSearchType.value === searchType) return
    await store.dispatch(`${SEARCH}/${UPDATE_QUERY}`, {
      searchType,
    })
    previousSearchType.value = searchType
  }
  return {
    setActiveType,
    activeType,
    types: searchTypes,
    icons,
  }
}
