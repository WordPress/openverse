import { computed } from '@nuxtjs/composition-api'

import { useMediaStore } from '~/stores/media'

/**
 * Fetches media on 'Load More' button click.
 *
 * @param {import('../pages/search/search-page.types').Props} props
 * @returns {{ onLoadMore: ((function(): Promise<void>)|void), canLoadMore: import('@nuxtjs/composition-api').ComputedRef<boolean>}}
 */
export const useLoadMore = (props) => {
  const canLoadMore = computed(() => {
    return props.searchTerm.trim() !== ''
  })

  const onLoadMore = async () => {
    const mediaStore = useMediaStore()
    if (canLoadMore.value) {
      await mediaStore.fetchMedia({
        shouldPersistMedia: true,
      })
    }
  }

  return { canLoadMore, onLoadMore }
}
