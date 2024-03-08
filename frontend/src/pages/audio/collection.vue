<template>
  <div class="p-6 pt-0 lg:p-10 lg:pt-2">
    <VCollectionResults
      v-if="collectionParams"
      search-term=""
      :is-fetching="isFetching"
      :results="{ type: 'audio', items: media }"
      :collection-label="collectionLabel"
      :collection-params="collectionParams"
      @load-more="handleLoadMore"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, useFetch, useMeta } from "@nuxtjs/composition-api"
import { computed, ref } from "vue"

import { useMediaStore } from "~/stores/media"
import { collectionMiddleware } from "~/middleware/collection"

import { useSearchStore } from "~/stores/search"
import type { AudioDetail } from "~/types/media"
import { AUDIO } from "~/constants/media"
import { useI18n } from "~/composables/use-i18n"

import VCollectionResults from "~/components/VSearchResultsGrid/VCollectionResults.vue"

export default defineComponent({
  name: "VAudioCollectionPage",
  components: { VCollectionResults },
  layout: "content-layout",
  middleware: collectionMiddleware,
  setup() {
    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()

    const collectionParams = computed(() => searchStore.collectionParams)
    const isFetching = computed(() => mediaStore.fetchState.isFetching)

    const media = ref<AudioDetail[]>([])
    const creatorUrl = ref<string>()

    const fetchMedia = async (shouldPersistMedia: boolean = false) => {
      if (mediaStore._searchType !== AUDIO) {
        throw new Error(
          `Search type is incorrectly set in the store to ${mediaStore._searchType} when it should be "audio"`
        )
      }
      media.value = (await mediaStore.fetchMedia({
        shouldPersistMedia,
      })) as AudioDetail[]
      creatorUrl.value =
        media.value.length > 0 ? media.value[0].creator_url : undefined
    }

    useFetch(async () => {
      await fetchMedia()
    })

    const handleLoadMore = async () => {
      await fetchMedia(true)
    }

    const i18n = useI18n()

    const collectionLabel = computed(() => {
      if (!collectionParams.value) {
        return ""
      }
      const { collection, ...params } = collectionParams.value
      return i18n
        .t(`collection.label.${collection}.audio`, { ...params })
        .toString()
    })

    useMeta({
      meta: [{ hid: "robots", name: "robots", content: "all" }],
    })

    return {
      collectionParams,
      media,
      isFetching,
      creatorUrl,
      collectionLabel,
      handleLoadMore,
    }
  },
  head: {},
})
</script>
