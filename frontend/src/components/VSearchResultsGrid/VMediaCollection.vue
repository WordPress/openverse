<script setup lang="ts">
import { computed } from "vue"

import type { MediaCollectionComponentProps } from "~/types/collection-component-props"
import { ALL_MEDIA, AUDIO, IMAGE } from "~/constants/media"

import VGridSkeleton from "~/components/VSkeleton/VGridSkeleton.vue"
import VAllResultsGrid from "~/components/VSearchResultsGrid/VAllResultsGrid.vue"
import VAudioCollection from "~/components/VSearchResultsGrid/VAudioCollection.vue"
import VImageCollection from "~/components/VSearchResultsGrid/VImageCollection.vue"

const props = withDefaults(defineProps<MediaCollectionComponentProps>(), {
  relatedTo: "null",
})

defineEmits<{ "load-more": [] }>()

const showSkeleton = computed(() => {
  return props.isFetching && props.results.items.length === 0
})

const components = {
  [IMAGE]: VImageCollection,
  [AUDIO]: VAudioCollection,
  [ALL_MEDIA]: VAllResultsGrid,
}

const component = computed(() => components[props.results.type])
</script>

<template>
  <section>
    <slot name="header" />

    <VGridSkeleton v-if="showSkeleton" :is-for-tab="results.type" />

    <Component
      :is="component"
      v-if="!showSkeleton"
      :results="results.items"
      :kind="kind"
      :search-term="searchTerm"
      :related-to="relatedTo"
      :collection-label="collectionLabel"
      :class="{ 'pt-2 sm:pt-0': results.type === 'image' }"
    />

    <slot name="footer" />
  </section>
</template>
