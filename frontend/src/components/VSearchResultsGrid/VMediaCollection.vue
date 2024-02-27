<template>
  <div>
    <slot name="header" />

    <VGridSkeleton v-if="showSkeleton" :is-for-tab="results.type" />

    <VImageCollection
      v-if="results.type === 'image'"
      :results="results.items"
      :kind="kind"
      :search-term="searchTerm"
      :collection-label="collectionLabel"
      class="pt-2 sm:pt-0"
    />
    <VAudioCollection
      v-if="results.type === 'audio'"
      :results="results.items"
      :search-term="searchTerm"
      :related-to="relatedTo"
      :kind="kind"
      :collection-label="collectionLabel"
    />
    <VAllResultsGrid
      v-if="results.type === 'all'"
      :results="results.items"
      :search-term="searchTerm"
      :related-to="relatedTo"
      :collection-label="collectionLabel"
    />
    <slot name="footer" v-bind="{ isFetching }" />
    <VScrollButton
      v-show="showScrollButton"
      :is-filter-sidebar-visible="isSidebarVisible"
      data-testid="scroll-button"
    />
  </div>
</template>
<script lang="ts">
import { computed, defineComponent, inject, type PropType, ref } from "vue"

import { isSupportedMediaType } from "~/constants/media"
import { IsSidebarVisibleKey, ShowScrollButtonKey } from "~/types/provides"
import type { Results } from "~/types/result"

import { useMediaStore } from "~/stores/media"

import { defineEvent } from "~/types/emits"

import VGridSkeleton from "~/components/VSkeleton/VGridSkeleton.vue"
import VAllResultsGrid from "~/components/VSearchResultsGrid/VAllResultsGrid.vue"
import VAudioCollection from "~/components/VSearchResultsGrid/VAudioCollection.vue"
import VImageCollection from "~/components/VSearchResultsGrid/VImageCollection.vue"
import VScrollButton from "~/components/VScrollButton.vue"

export default defineComponent({
  name: "VMediaCollection",
  components: {
    VScrollButton,
    VAllResultsGrid,
    VAudioCollection,
    VImageCollection,
    VGridSkeleton,
  },
  props: {
    results: {
      type: Object as PropType<Results>,
      required: true,
    },
    searchTerm: {
      type: String as PropType<string>,
      required: true,
    },
    kind: {
      type: String as PropType<"search" | "collection" | "related">,
      required: true,
    },
    collectionLabel: {
      type: String,
      required: true,
    },
    relatedTo: {
      type: String as PropType<string | null>,
      default: null,
    },
  },
  emits: {
    "load-more": defineEvent(),
  },
  setup(props) {
    console.log("VMediaCollection:searchTerm", props.searchTerm)
    const showScrollButton = inject(ShowScrollButtonKey, ref(false))
    const isSidebarVisible = inject(IsSidebarVisibleKey, ref(false))

    const mediaStore = useMediaStore()

    const isFetching = computed(() => mediaStore.fetchState.isFetching)

    const showSkeleton = computed(() => {
      return isFetching.value && props.results.items.length === 0
    })

    return {
      showSkeleton,
      showScrollButton,
      isSidebarVisible,
      isFetching,
    }
  },
  methods: { isSupportedMediaType },
})
</script>
