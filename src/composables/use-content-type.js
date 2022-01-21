import { computed, ref, useContext } from '@nuxtjs/composition-api'
import { supportedContentTypes } from '~/constants/media'
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
const contentTypes = [...supportedContentTypes]

export default function useContentType() {
  const { store } = useContext()

  const activeType = computed(() => store.state.search.searchType)
  const previousContentType = ref(activeType.value)
  const setActiveType = async (contentType) => {
    if (previousContentType.value === contentType) return
    await store.dispatch(`${SEARCH}/${UPDATE_QUERY}`, {
      searchType: contentType,
    })
    previousContentType.value = contentType
  }
  return {
    setActiveType,
    activeType,
    types: contentTypes,
    icons,
  }
}
