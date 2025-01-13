import { useI18n, useRoute } from "#imports"
import { computed, Ref, ref, watch } from "vue"

import type { SupportedMediaType } from "#shared/constants/media"
import type { AudioDetail, ImageDetail } from "#shared/types/media"
import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { useCollectionMeta } from "~/composables/use-collection-meta"

export const useCollection = <T extends SupportedMediaType>({
  mediaType,
}: {
  mediaType: T
}) => {
  type ResultType = T extends "image" ? ImageDetail : AudioDetail

  const mediaStore = useMediaStore()
  const searchStore = useSearchStore()

  const collectionParams = computed(() => searchStore.collectionParams)
  const isFetching = computed(() => mediaStore.isFetching)

  const media = ref(mediaStore.resultItems[mediaType]) as Ref<ResultType[]>
  const creatorUrl = ref<string>()

  const { t } = useI18n({ useScope: "global" })

  const collectionLabel = computed(() => {
    if (!collectionParams.value) {
      return ""
    }
    const { collection, ...params } = collectionParams.value
    return t(`collection.ariaLabel.${collection}.image`, { ...params })
  })

  const fetchMedia = async (
    { shouldPersistMedia }: { shouldPersistMedia: boolean } = {
      shouldPersistMedia: false,
    }
  ) => {
    const results = await mediaStore.fetchMedia({ shouldPersistMedia })
    media.value = results.items as ResultType[]
    creatorUrl.value =
      media.value.length > 0 ? media.value[0].creator_url : undefined
    return media.value
  }
  // `useAsyncData` is not triggered when the query changes, e.g. when the user navigates from
  // a creator collection page to a source collection page.
  const route = useRoute()
  const routeQuery = computed(() => route.query)
  watch(routeQuery, async () => {
    await fetchMedia()
  })

  const canLoadMore = computed(() => mediaStore.canLoadMore)
  const loadMore = async () => {
    await fetchMedia({ shouldPersistMedia: true })
  }
  const { pageTitle } = useCollectionMeta({
    collectionParams,
    mediaType,
    t,
  })

  return {
    collectionParams,
    pageTitle,
    collectionLabel,
    creatorUrl,
    isFetching,
    media,
    fetchMedia,
    loadMore,
    canLoadMore,
  }
}
