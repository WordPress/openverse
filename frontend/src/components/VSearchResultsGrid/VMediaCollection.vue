<template>
  <div>
    <header
      v-if="metadata.kind === 'search' && metadata.searchTerm"
      class="my-0 md:mb-8 md:mt-4"
    >
      <VSearchResultsTitle
        :size="results.type === 'all' ? 'large' : 'default'"
        >{{ metadata.searchTerm }}</VSearchResultsTitle
      >
    </header>
    <VCollectionHeader
      v-if="
        metadata.kind === 'collection' && isSupportedMediaType(results.type)
      "
      class="my-0 md:mb-8 md:mt-4"
      :class="results.type === 'image' ? 'mb-4' : 'mb-2'"
      :media-type="results.type"
      :collection-params="metadata.collectionParams"
    />
    <VGridSkeleton v-if="showSkeleton" :is-for-tab="results.type" class="" />
    <VImageCollection
      v-if="results.type === 'image'"
      :results="results.items"
      :kind="metadata.kind"
      :collection-label="collectionLabel"
      class="pt-2 sm:pt-0"
    />
    <VAudioCollection
      v-if="results.type === 'audio'"
      :results="results.items"
      :kind="metadata.kind"
      :collection-label="collectionLabel"
    />
    <VAllResultsGrid
      v-if="metadata.kind === 'search' && results.type === 'all'"
      :results="results.items"
      :search-term="metadata.searchTerm"
      :collection-label="collectionLabel"
    />
    <footer class="mb-6 mt-4 lg:mb-10">
      <VLoadMore
        :search-type="results.type"
        :results-term="resultsTerm"
        :is-fetching="isFetching"
        class="mb-4"
        @load-more="$emit('load-more')"
      />
      <VExternalSearchForm
        v-if="metadata.kind === 'search' && results.type !== 'all'"
        :search-term="metadata.searchTerm"
        :is-supported="true"
        :has-no-results="false"
      />
    </footer>
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
import type { CollectionParams } from "~/types/search"

import { useMediaStore } from "~/stores/media"

import { useI18n } from "~/composables/use-i18n"

import { defineEvent } from "~/types/emits"

import VGridSkeleton from "~/components/VSkeleton/VGridSkeleton.vue"
import VSearchResultsTitle from "~/components/VSearchResultsTitle.vue"
import VCollectionHeader from "~/components/VCollectionHeader/VCollectionHeader.vue"
import VAllResultsGrid from "~/components/VSearchResultsGrid/VAllResultsGrid.vue"
import VAudioCollection from "~/components/VSearchResultsGrid/VAudioCollection.vue"
import VImageCollection from "~/components/VSearchResultsGrid/VImageCollection.vue"
import VExternalSearchForm from "~/components/VExternalSearch/VExternalSearchForm.vue"
import VScrollButton from "~/components/VScrollButton.vue"
import VLoadMore from "~/components/VLoadMore.vue"

export default defineComponent({
  components: {
    VScrollButton,
    VExternalSearchForm,
    VSearchResultsTitle,
    VCollectionHeader,
    VLoadMore,
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
    metadata: {
      type: Object as PropType<
        | { kind: "search"; searchTerm: string }
        | {
            kind: "collection"
            collectionParams: CollectionParams
            creatorUrl?: string
          }
      >,
      required: true,
    },
  },
  emits: {
    "load-more": defineEvent(),
  },
  setup(props) {
    const showScrollButton = inject(ShowScrollButtonKey, ref(false))
    const isSidebarVisible = inject(IsSidebarVisibleKey, ref(false))

    const mediaStore = useMediaStore()

    const isFetching = computed(() => mediaStore.fetchState.isFetching)

    const showSkeleton = computed(() => {
      return isFetching.value && props.results.items.length === 0
    })

    const resultsTerm = computed(() => {
      if (props.metadata.kind === "search") {
        return props.metadata.searchTerm
      }
      const params = props.metadata.collectionParams
      return params.collection === "tag"
        ? params.tag
        : params.collection === "source"
        ? params.source
        : `${params.source}/${params.creator}`
    })

    const i18n = useI18n()
    const collectionLabel = computed(() => {
      if (props.metadata.kind === "search") {
        return i18n
          .t("browsePage.aria.results", { query: props.metadata.searchTerm })
          .toString()
      }
      const params = props.metadata.collectionParams
      return params.collection === "tag"
        ? params.tag
        : params.collection === "source"
        ? params.source
        : `${params.source}/${params.creator}`
    })

    return {
      showSkeleton,
      showScrollButton,
      isSidebarVisible,
      resultsTerm,
      isFetching,
      collectionLabel,
    }
  },
  methods: { isSupportedMediaType },
})
</script>
