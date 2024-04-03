import { computed } from "vue"

import { useI18n } from "~/composables/use-i18n"
import { useProviderStore } from "~/stores/provider"
import type { SupportedMediaType } from "~/constants/media"
import type { CollectionParams } from "~/types/search"

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
    // The default page title. It should be overwritten by the specific collection type.
    const title = "Openly Licensed Images, Audio and More"

    switch (collectionParams.value?.collection) {
      case "creator": {
        return `${collectionParams.value.creator} | Openverse`
      }

      case "source": {
        const sourceName = useProviderStore().getProviderName(
          collectionParams.value.source,
          mediaType
        )
        return `${i18n.t(`collection.pageTitle.source.${mediaType}`, {
          source: sourceName,
        })} | Openverse`
      }

      case "tag": {
        return `${i18n.t(`collection.pageTitle.tag.${mediaType}`, {
          tag: collectionParams.value.tag,
        })} | Openverse`
      }
    }

    return `${title} | Openverse`
  })

  return {
    pageTitle,
  }
}
