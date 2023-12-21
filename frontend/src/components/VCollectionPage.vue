<template>
  <div class="p-6 pt-0 lg:p-10 lg:pt-2">
    <VCollectionHeader
      v-if="collectionParams"
      :collection-params="collectionParams"
      :creator-url="creatorUrl"
      :media-type="mediaType"
      :class="mediaType === 'image' ? 'mb-4' : 'mb-2'"
    />
    <VAudioCollection
      v-if="results.type === 'audio'"
      :collection-label="collectionLabel"
      :fetch-state="fetchState"
      kind="collection"
      :results="results.items"
    />
    <VImageGrid
      v-if="results.type === 'image'"
      :image-grid-label="collectionLabel"
      :fetch-state="fetchState"
      kind="collection"
      :results="results.items"
    />
  </div>
</template>
<script lang="ts">
import { useI18n } from "#imports"

import { computed, defineComponent, PropType } from "vue"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import type { SupportedMediaType } from "~/constants/media"

import { Results } from "~/types/result"

import VCollectionHeader from "~/components/VCollectionHeader/VCollectionHeader.vue"
import VAudioCollection from "~/components/VSearchResultsGrid/VAudioCollection.vue"
import VImageGrid from "~/components/VSearchResultsGrid/VImageGrid.vue"

export default defineComponent({
  name: "VCollectionPage",
  components: { VAudioCollection, VImageGrid, VCollectionHeader },
  props: {
    mediaType: {
      type: String as PropType<SupportedMediaType>,
      required: true,
    },
  },
  setup(props) {
    const i18n = useI18n({ useScope: "global" })
    const mediaStore = useMediaStore()

    const fetchState = computed(() => mediaStore.fetchState)
    const results = computed<Results>(() => {
      return {
        type: props.mediaType,
        items: mediaStore.resultItems[props.mediaType],
      } as Results
    })

    const creatorUrl = computed(() => {
      const media = results.value.items
      return media.length > 0 ? media[0].creator_url : undefined
    })

    const searchStore = useSearchStore()
    const collectionParams = computed(() => searchStore.collectionParams)

    const collectionLabel = computed(() => {
      const collection = collectionParams.value?.collection
      switch (collection) {
        case "tag": {
          return i18n.t(`collection.ariaLabel.tag.${props.mediaType}`, {
            tag: collectionParams.value?.tag,
          })
        }
        case "source": {
          return i18n.t(`collection.ariaLabel.source.${props.mediaType}`, {
            source: collectionParams.value?.source,
          })
        }
        case "creator": {
          return i18n.t(`collection.ariaLabel.creator.${props.mediaType}`, {
            creator: collectionParams.value?.creator,
            source: collectionParams.value?.source,
          })
        }
        default: {
          return ""
        }
      }
    })

    return {
      fetchState,
      results,
      creatorUrl,
      collectionParams,
      collectionLabel,
    }
  },
})
</script>
