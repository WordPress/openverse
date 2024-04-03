<template>
  <div
    :id="skipToContentTargetId"
    tabindex="-1"
    class="p-6 pt-0 lg:p-10 lg:pt-2"
  >
    <VCollectionResults
      v-if="collectionParams"
      search-term=""
      :is-fetching="isFetching"
      :results="{ type: 'image', items: media }"
      :collection-label="collectionLabel"
      :collection-params="collectionParams"
      @load-more="loadMore"
    />
  </div>
</template>

<script lang="ts">
import {
  defineComponent,
  useFetch,
  useMeta,
  useRoute,
} from "@nuxtjs/composition-api"
import { computed, ref, watch } from "vue"

import { collectionMiddleware } from "~/middleware/collection"
import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { useCollectionMeta } from "~/composables/use-collection-meta"
import { skipToContentTargetId } from "~/constants/window"
import { useI18n } from "~/composables/use-i18n"
import type { ImageDetail } from "~/types/media"

import VCollectionResults from "~/components/VSearchResultsGrid/VCollectionResults.vue"

export default defineComponent({
  name: "VImageCollectionPage",
  components: { VCollectionResults },
  layout: "content-layout",
  middleware: collectionMiddleware,
  setup() {
    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()

    const collectionParams = computed(() => searchStore.collectionParams)
    const isFetching = computed(() => mediaStore.fetchState.isFetching)

    const media = ref<ImageDetail[]>([])
    const creatorUrl = ref<string>()

    const i18n = useI18n()

    const collectionLabel = computed(() => {
      if (!collectionParams.value) {
        return ""
      }
      const { collection, ...params } = collectionParams.value
      return i18n
        .t(`collection.ariaLabel.${collection}.image`, { ...params })
        .toString()
    })

    const fetchMedia = async (
      { shouldPersistMedia }: { shouldPersistMedia: boolean } = {
        shouldPersistMedia: false,
      }
    ) => {
      media.value = (await mediaStore.fetchMedia({
        shouldPersistMedia,
      })) as (typeof media)["value"]
      creatorUrl.value =
        media.value.length > 0 ? media.value[0].creator_url : undefined
    }
    const loadMore = () => {
      fetchMedia({ shouldPersistMedia: true })
    }

    const { pageTitle } = useCollectionMeta({
      collectionParams,
      mediaType: "image",
      i18n,
    })

    useMeta(() => ({
      meta: [
        { hid: "robots", name: "robots", content: "all" },
        { hid: "og:title", property: "og:title", content: pageTitle.value },
      ],
      title: pageTitle.value,
    }))

    useFetch(async () => {
      await fetchMedia()
    })

    // Fetch media when the route changes, e.g. when the user navigates from
    // a creator collection page to a source collection page.
    const route = useRoute()
    watch(route, () => {
      fetchMedia()
    })

    return {
      collectionParams,
      isFetching,
      creatorUrl,
      collectionLabel,
      loadMore,
      media,
      skipToContentTargetId,
    }
  },
  head: {},
})
</script>
