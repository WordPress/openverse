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

    <slot name="footer" v-bind="{ isFetching }" />

    <VScrollButton
      v-show="showScrollButton"
      :is-filter-sidebar-visible="isSidebarVisible"
      data-testid="scroll-button"
    />
  </section>
</template>
<script lang="ts">
import { computed, defineComponent, inject, type PropType, ref } from "vue"

import { IsSidebarVisibleKey, ShowScrollButtonKey } from "~/types/provides"
import type { Results } from "~/types/result"

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
    isFetching: {
      type: Boolean,
      required: true,
    },
  },
  emits: {
    "load-more": defineEvent(),
  },
  setup(props) {
    const showScrollButton = inject(ShowScrollButtonKey, ref(false))
    const isSidebarVisible = inject(IsSidebarVisibleKey, ref(false))

    const showSkeleton = computed(() => {
      return props.isFetching && props.results.items.length === 0
    })

    const component = computed(() => {
      if (props.results.type === "image") {
        return "VImageCollection"
      } else if (props.results.type === "audio") {
        return "VAudioCollection"
      } else {
        return "VAllResultsGrid"
      }
    })

    return {
      showSkeleton,
      showScrollButton,
      isSidebarVisible,
      component,
    }
  },
})
</script>
