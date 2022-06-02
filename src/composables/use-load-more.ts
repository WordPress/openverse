import { computed, ComputedRef } from '@nuxtjs/composition-api'

import { useMediaStore } from '~/stores/media'

/**
 * Fetches media on 'Load More' button click.
 */
export const useLoadMore = (searchTerm: ComputedRef<string>) => {
  const canLoadMore = computed(() => searchTerm.value.trim() !== '')

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
