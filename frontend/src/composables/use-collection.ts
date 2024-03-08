import { computed, ref } from "vue"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { useI18n } from "~/composables/use-i18n"
import type { DetailFromMediaType } from "~/types/media"
import type { SupportedMediaType } from "~/constants/media"

export const useCollection = <T extends SupportedMediaType>({
  mediaType,
}: {
  mediaType: T
}) => {
  const mediaStore = useMediaStore()
  const searchStore = useSearchStore()

  const collectionParams = computed(() => searchStore.collectionParams)
  const isFetching = computed(() => mediaStore.fetchState.isFetching)

  const media = ref<DetailFromMediaType<typeof mediaType>[]>([])
  const creatorUrl = ref<string>()

  const i18n = useI18n()

  const collectionLabel = computed(() => {
    if (!collectionParams.value) {
      return ""
    }
    const { collection, ...params } = collectionParams.value
    return i18n
      .t(`collection.label.${collection}.image`, { ...params })
      .toString()
  })

  const fetchMedia = async (
    { shouldPersistMedia }: { shouldPersistMedia: boolean } = {
      shouldPersistMedia: false,
    }
  ) => {
    if (mediaStore._searchType !== mediaType) {
      throw new Error(
        `Search type is incorrectly set in the store to ${mediaStore._searchType} when it should be "${mediaType}"`
      )
    }
    media.value = (await mediaStore.fetchMedia({
      shouldPersistMedia,
    })) as (typeof media)["value"]
    creatorUrl.value =
      media.value.length > 0 ? media.value[0].creator_url : undefined
  }

  const handleLoadMore = async () => {
    await fetchMedia({ shouldPersistMedia: true })
  }

  const results = computed(() => ({ type: mediaType, items: media.value }))

  return {
    results,
    creatorUrl,
    fetchMedia,
    handleLoadMore,
    collectionLabel,
    isFetching,
  }
}
