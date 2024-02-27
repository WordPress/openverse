<template>
  <VRelatedResults
    v-if="showRelated"
    :collection-label="$t(labelKey).toString()"
    :results="results"
    :search-term="searchTerm"
    :related-to="relatedTo"
  />
</template>

<script lang="ts">
import { computed, defineComponent, PropType, watch } from "vue"
import { useRoute } from "@nuxtjs/composition-api"

import { useRelatedMediaStore } from "~/stores/media/related-media"

import type { SupportedMediaType } from "~/constants/media"
import type { AudioResults, ImageResults } from "~/types/result"

import VRelatedResults from "~/components/VSearchResultsGrid/VRelatedResults.vue"

export default defineComponent({
  name: "VRelatedMedia",
  components: { VRelatedResults },
  props: {
    mediaType: {
      type: String as PropType<SupportedMediaType>,
      required: true,
    },
    relatedTo: {
      type: String as PropType<string>,
      required: true,
    },
  },
  setup(props) {
    const relatedMediaStore = useRelatedMediaStore()

    const route = useRoute()

    const results = computed(() => {
      const media = relatedMediaStore.media ?? []
      return { type: props.mediaType, items: media } as
        | ImageResults
        | AudioResults
    })
    watch(
      route,
      async (newRoute) => {
        if (newRoute.params.id !== relatedMediaStore.mainMediaId) {
          await relatedMediaStore.fetchMedia(
            props.mediaType,
            newRoute.params.id
          )
        }
      },
      { immediate: true }
    )

    const showRelated = computed(
      () =>
        results.value.items.length > 0 ||
        relatedMediaStore.fetchState.isFetching
    )

    const searchTerm = computed(() => {
      const q = Array.isArray(route.value.query.q)
        ? route.value.query.q[0]
        : route.value.query.q
      return q ?? ""
    })

    const labelKey = computed(() => {
      return props.mediaType === "audio"
        ? "audioDetails.relatedAudios"
        : "imageDetails.relatedImages"
    })

    return {
      results,
      showRelated,
      searchTerm,
      labelKey,
    }
  },
})
</script>
