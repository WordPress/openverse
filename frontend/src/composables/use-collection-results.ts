import { ref } from "vue"

import { useMediaStore } from "~/stores/media"
import { AUDIO, IMAGE, type SupportedMediaType } from "~/constants/media"

import type {
  AudioDetail,
  DetailFromMediaType,
  ImageDetail,
} from "~/types/media"

type MediaResultsFromType<T extends SupportedMediaType> = T extends typeof IMAGE
  ? { type: typeof IMAGE; items: ImageDetail[] }
  : T extends typeof AUDIO
  ? { type: typeof AUDIO; items: AudioDetail[] }
  : never

export const useCollectionResults = <T extends SupportedMediaType>(
  mediaType: T
) => {
  const mediaStore = useMediaStore()

  const results = ref<MediaResultsFromType<T>>({
    type: mediaType,
    items: mediaStore.resultItems[
      mediaType
    ] as MediaResultsFromType<T>["items"],
  } as MediaResultsFromType<T>)
  const creatorUrl = ref<string>()

  const fetchMedia = async ({
    shouldPersistMedia,
  }: { shouldPersistMedia?: boolean } = {}) => {
    results.value.items = (await mediaStore.fetchMedia({
      shouldPersistMedia,
    })) as DetailFromMediaType<T>[]
    creatorUrl.value = results.value.items.length
      ? results.value.items[0].creatorUrl
      : undefined
  }

  const handleLoadMore = async () => {
    await fetchMedia({ shouldPersistMedia: true })
  }

  return {
    results,
    fetchMedia,
    handleLoadMore,
    creatorUrl,
  }
}
