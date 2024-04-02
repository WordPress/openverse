import { computed } from "vue"

import { TranslateResult } from "vue-i18n"

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
    // The default page title. It should be overwritten by the specific collection type.
    let title: string | TranslateResult =
      "Openly Licensed Images, Audio and More"

    switch (collectionParams.value?.collection) {
      case "creator": {
        title = collectionParams.value.creator
        break
      }

      case "source": {
        const sourceName = useProviderStore().getProviderName(
          collectionParams.value.source,
          mediaType
        )
        title = i18n.t(`collection.pageTitle.source.${mediaType}`, {
          source: sourceName,
        })
        break
      }

      case "tag": {
        title = i18n.t(`collection.pageTitle.tag.${mediaType}`, {
          tag: collectionParams.value.tag,
        })
        break
      }
    }

    return `${title} | Openverse`
  })

  return {
    pageTitle,
  }
}
