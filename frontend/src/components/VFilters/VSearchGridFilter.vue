<template>
  <section id="filters" aria-labelledby="filters-heading" class="filters">
    <header
      v-if="showFilterHeader"
      class="relative mb-6 flex items-center justify-between"
    >
      <h4 id="filters-heading" class="caption-bold uppercase">
        {{ $t("filter-list.filter-by") }}
      </h4>
      <VButton
        v-show="isAnyFilterApplied"
        id="clear-filter-button"
        variant="plain"
        class="label-bold absolute end-0 px-4 py-1 text-pink hover:ring hover:ring-pink"
        @click="clearFilters"
      >
        {{ $t("filter-list.clear") }}
      </VButton>
    </header>
    <form ref="filtersFormRef" class="filters-form">
      <VFilterChecklist
        v-for="filterType in filterTypes"
        :key="filterType"
        :options="filters[filterType]"
        :title="filterTypeTitle(filterType).toString()"
        :filter-type="filterType"
        @toggle-filter="toggleFilter"
      />
    </form>
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, ref } from "vue"

import { useContext, useRouter } from "@nuxtjs/composition-api"
import { kebab } from "case"

import { watchDebounced } from "@vueuse/core"

import { useSearchStore } from "~/stores/search"
import { areQueriesEqual, ApiQueryParams } from "~/utils/search-query-transform"
import type { NonMatureFilterCategory } from "~/constants/filters"
import { defineEvent } from "~/types/emits"

import VFilterChecklist from "~/components/VFilters/VFilterChecklist.vue"
import VButton from "~/components/VButton.vue"

export default defineComponent({
  name: "VSearchGridFilter",
  components: {
    VButton,
    VFilterChecklist,
  },
  props: {
    /**
     * Whether to show the header with the title and the clear button.
     */
    showFilterHeader: {
      type: Boolean,
      default: true,
    },
    /**
     * When the filters are in the sidebar, we change the keyboard tabbing order:
     * the focus moves from the Filters button to the filter,
     * and from the last tabbable element to the main content on Tab,
     * and from the filters to the filters button on Shift Tab.
     */
    changeTabOrder: {
      type: Boolean,
      default: true,
    },
  },
  emits: {
    close: defineEvent(),
  },
  setup() {
    const searchStore = useSearchStore()

    const { i18n } = useContext()
    const router = useRouter()

    const filtersFormRef = ref<HTMLFormElement | null>(null)

    const isAnyFilterApplied = computed(() => searchStore.isAnyFilterApplied)
    const filters = computed(() => searchStore.searchFilters)
    const filterTypes = computed(
      () => Object.keys(filters.value) as NonMatureFilterCategory[]
    )
    const filterTypeTitle = (filterType: string) =>
      i18n.t(`filters.${kebab(filterType)}.title`)

    /**
     * This watcher fires even when the queries are equal. We update the path only
     * when the queries change.
     */
    watchDebounced(
      () => searchStore.searchQueryParams,
      (newQuery: ApiQueryParams, oldQuery: ApiQueryParams) => {
        if (!areQueriesEqual(newQuery, oldQuery)) {
          router.push(searchStore.getSearchPath())
        }
      },
      { debounce: 800, maxWait: 5000 }
    )

    return {
      filtersFormRef,
      isAnyFilterApplied,
      filters,
      filterTypes,
      filterTypeTitle,
      clearFilters: searchStore.clearFilters,
      toggleFilter: searchStore.toggleFilter,
    }
  },
})
</script>
