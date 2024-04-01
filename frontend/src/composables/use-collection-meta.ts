import { computed } from "vue"

import type { SupportedMediaType } from "~/constants/media"
import type { CollectionParams } from "~/types/search"
import { useI18n } from "~/composables/use-i18n"
import { useProviderStore } from "~/stores/provider"

import type { ComputedRef } from "vue"

export const useCollectionMeta = ({
  collectionParams,
  mediaType,
  i18n,
}: {
  collectionParams: ComputedRef<CollectionParams | null>
  mediaType: SupportedMediaType
  i18n: ReturnType<typeof useI18n>
}) => {
  const pageTitle = computed(() => {
    const providerStore = useProviderStore()

    if (collectionParams.value?.collection === "creator") {
      return `${collectionParams.value.creator} | Openverse`
    } else if (collectionParams.value?.collection === "source") {
      const sourceName = providerStore.getProviderName(
        collectionParams.value.source,
        mediaType
      )
      return i18n
        .t(`collection.pageTitle.source.${mediaType}`, { source: sourceName })
        .toString()
    } else if (collectionParams.value?.collection === "tag") {
      return i18n
        .t(`collection.pageTitle.tag.${mediaType}`, {
          tag: collectionParams.value.tag,
        })
        .toString()
    }
    return "Openverse"
  })
  return {
    pageTitle,
  }
}
