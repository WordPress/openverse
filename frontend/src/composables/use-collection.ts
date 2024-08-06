import { useCollectionMeta, useI18n, useRoute } from "#imports"

import { computed, ref, watch } from "vue"

import { SupportedMediaType } from "~/constants/media"
import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import type { AudioDetail, ImageDetail } from "~/types/media"

export const useCollection = <T extends SupportedMediaType>({
  mediaType,
}: {
  mediaType: T
}) => {
  type ResultType = T extends "image" ? ImageDetail : AudioDetail

  const mediaStore = useMediaStore()
  const searchStore = useSearchStore()

  const collectionParams = computed(() => searchStore.collectionParams)
  const isFetching = computed(() => mediaStore.fetchState.isFetching)

  const media = ref<ResultType[]>(
    mediaStore.resultItems[mediaType] as ResultType[]
  )
  const creatorUrl = ref<string>()

  const i18n = useI18n({ useScope: "global" })

  const collectionLabel = computed(() => {
    if (!collectionParams.value) {
      return ""
    }
    const { collection, ...params } = collectionParams.value
    return i18n.t(`collection.ariaLabel.${collection}.image`, { ...params })
  })

  const fetchMedia = async (
    { shouldPersistMedia }: { shouldPersistMedia: boolean } = {
      shouldPersistMedia: false,
    }
  ) => {
    media.value = (await mediaStore.fetchMedia({
      shouldPersistMedia,
    })) as ResultType[]
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

  const loadMore = async () => {
    await fetchMedia({ shouldPersistMedia: true })
  }
  const { pageTitle } = useCollectionMeta({
    collectionParams,
    mediaType,
    i18n,
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
  }
}
