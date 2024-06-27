<template>
  <VMediaCollection
    v-if="showRelated"
    :results="results"
    :is-fetching="isFetching"
    :collection-label="collectionLabel"
    kind="related"
    :related-to="relatedTo"
    :search-term="searchTerm"
    :aria-label="collectionLabel"
  >
    <template #header>
      <h2
        id="related-heading"
        class="heading-6 mb-6"
        :class="results.type === 'image' ? 'md:heading-5' : 'lg:heading-6'"
      >
        {{ collectionLabel }}
      </h2>
    </template>
  </VMediaCollection>
</template>

<script lang="ts">
import { computed, defineComponent, PropType, watch } from "vue"
import { useRoute } from "@nuxtjs/composition-api"

import { useRelatedMediaStore } from "~/stores/media/related-media"
import { useI18n } from "~/composables/use-i18n"

import type { SupportedMediaType } from "~/constants/media"
import type { AudioResults, ImageResults } from "~/types/result"

import VMediaCollection from "~/components/VSearchResultsGrid/VMediaCollection.vue"

export default defineComponent({
  name: "VRelatedMedia",
  components: { VMediaCollection },
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

    const isFetching = computed(() => relatedMediaStore.fetchState.isFetching)
    const showRelated = computed(
      () => results.value.items.length > 0 || isFetching.value
    )

    const searchTerm = computed(() => {
      const q = Array.isArray(route.value?.query?.q)
        ? route.value?.query?.q[0]
        : route.value?.query?.q
      return q ?? ""
    })

    const i18n = useI18n()

    const collectionLabel = computed(() => {
      const key =
        props.mediaType === "audio"
          ? "audioDetails.relatedAudios"
          : "imageDetails.relatedImages"
      return i18n.t(key).toString()
    })

    return {
      results,
      showRelated,
      isFetching,

      searchTerm,
      collectionLabel,
    }
  },
})
</script>
