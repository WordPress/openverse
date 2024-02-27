<template>
  <div class="p-6 pt-0 lg:p-10 lg:pt-2">
    <VCollectionHeader
      v-if="collectionParams"
      :collection-params="collectionParams"
      :creator-url="creatorUrl"
      :media-type="mediaType"
      :class="mediaType === 'image' ? 'mb-4' : 'mb-2'"
    />
    <VAudioList
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
import { computed, defineComponent, PropType } from "vue"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import type { SupportedMediaType } from "~/constants/media"

import { Results } from "~/types/result"

import { useI18n } from "~/composables/use-i18n"

import VCollectionHeader from "~/components/VCollectionHeader/VCollectionHeader.vue"
import VImageGrid from "~/components/VSearchResultsGrid/VImageGrid.vue"
import VAudioList from "~/components/VSearchResultsGrid/VAudioList.vue"

export default defineComponent({
  name: "VCollectionPage",
  components: { VAudioList, VImageGrid, VCollectionHeader },
  props: {
    mediaType: {
      type: String as PropType<SupportedMediaType>,
      required: true,
    },
  },
  setup(props) {
    const i18n = useI18n()
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
      if (!collectionParams.value) {
        return ""
      }
      const key = `collection.ariaLabel.${collectionParams.value.collection}.${props.mediaType}`
      const params = collectionParams.value
      return i18n.t(key, params).toString()
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
