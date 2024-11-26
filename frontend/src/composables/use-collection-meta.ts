import { computed } from "vue"
import type { ComputedRef } from "vue"

import type { SupportedMediaType } from "#shared/constants/media"
import type { CollectionParams } from "#shared/types/search"
import { useProviderStore } from "~/stores/provider"

import type { Composer } from "vue-i18n"

export const useCollectionMeta = ({
  collectionParams,
  mediaType,
  t,
}: {
  collectionParams: ComputedRef<CollectionParams | null>
  mediaType: SupportedMediaType
  t: Composer["t"]
}) => {
  const pageTitle = computed(() => {
    const params = collectionParams.value

    if (params) {
      if (params.collection === "creator") {
        return `${params.creator} | Openverse`
      }

      if (params.collection === "source") {
        const sourceName = useProviderStore().getProviderName(
          params.source,
          mediaType
        )
        return `${t(`collection.pageTitle.source.${mediaType}`, { source: sourceName })} | Openverse`
      }

      if (params.collection === "tag") {
        return `${t(`collection.pageTitle.tag.${mediaType}`, { tag: params.tag })} | Openverse`
      }
    }

    return "Openly Licensed Images, Audio and More | Openverse"
  })

  return {
    pageTitle,
  }
}
