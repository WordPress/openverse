<template>
  <VMediaCollection
    :collection-label="collectionLabel"
    :results="results"
    :search-term="searchTerm"
    kind="search"
  >
    <template #header>
      <header v-if="searchTerm" class="my-0 md:mb-8 md:mt-4">
        <VSearchResultsTitle
          :size="results.type === 'all' ? 'large' : 'default'"
          >{{ searchTerm }}</VSearchResultsTitle
        >
      </header>
    </template>
    <template #footer="{ isFetching }">
      <footer class="mb-6 mt-4 lg:mb-10">
        <VLoadMore
          :search-type="results.type"
          kind="search"
          :search-term="searchTerm"
          :is-fetching="isFetching"
          class="mb-4"
          @load-more="$emit('load-more')"
        />
        <VExternalSearchForm
          v-if="results.type !== 'all'"
          :search-term="searchTerm"
          :is-supported="true"
          :has-no-results="false"
        />
      </footer>
    </template>
  </VMediaCollection>
</template>
<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import { Results } from "~/types/result"

import { useI18n } from "~/composables/use-i18n"

import { defineEvent } from "~/types/emits"

import VSearchResultsTitle from "~/components/VSearchResultsTitle.vue"
import VMediaCollection from "~/components/VSearchResultsGrid/VMediaCollection.vue"
import VLoadMore from "~/components/VLoadMore.vue"
import VExternalSearchForm from "~/components/VExternalSearch/VExternalSearchForm.vue"

export default defineComponent({
  name: "VSearchResults",
  components: {
    VExternalSearchForm,
    VLoadMore,
    VMediaCollection,
    VSearchResultsTitle,
  },
  props: {
    searchTerm: {
      type: String as PropType<string>,
      required: true,
    },
    results: {
      type: Object as PropType<Results>,
      required: true,
    },
  },
  emits: {
    "load-more": defineEvent(),
  },
  setup(props) {
    const i18n = useI18n()

    const collectionLabel = computed(() => {
      return i18n
        .t("browsePage.aria.results", { query: props.searchTerm })
        .toString()
    })

    return { collectionLabel }
  },
})
</script>
