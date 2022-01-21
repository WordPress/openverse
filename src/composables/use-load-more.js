import { computed, useContext } from '@nuxtjs/composition-api'
import { FETCH_MEDIA } from '~/constants/action-types'
import { MEDIA } from '~/constants/store-modules'

/**
 * Fetches media on 'Load More' button click.
 *
 * @param {import('../pages/search/search-page.types').Props} props
 * @returns {{ onLoadMore: ((function(): Promise<void>)|void), canLoadMore: import('@nuxtjs/composition-api').ComputedRef<boolean>}}
 */
export const useLoadMore = (props) => {
  const { store } = useContext()

  const searchParams = computed(() => {
    const pages = {}
    Object.keys(props.mediaResults).forEach((key) => {
      const mediaPage = props.mediaResults[key]?.page || 0
      pages[key] = mediaPage ? mediaPage + 1 : undefined
    })
    return {
      page: pages,
      shouldPersistMedia: true,
    }
  })

  const canLoadMore = computed(() => {
    return props.searchTerm.trim() !== ''
  })

  const onLoadMore = async () => {
    if (canLoadMore) {
      await store.dispatch(`${MEDIA}/${FETCH_MEDIA}`, searchParams.value)
    }
  }

  return { canLoadMore, onLoadMore }
}
