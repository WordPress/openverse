<template>
  <section id="filters" aria-labelledby="filters-heading" class="filters">
    <header
      v-if="showFilterHeader"
      class="relative mb-6 flex items-center justify-between"
    >
      <h4 id="filters-heading" class="caption-bold uppercase">
        {{ $t("filterList.filterBy") }}
      </h4>
      <VButton
        v-show="isAnyFilterApplied"
        id="clear-filter-button"
        variant="transparent-gray"
        size="small"
        class="label-bold absolute end-0 !text-pink"
        @click="clearFilters"
      >
        {{ $t("filterList.clear") }}
      </VButton>
    </header>
    <form class="filters-form">
      <VFilterChecklist
        v-for="filterType in filterTypes"
        :key="filterType"
        :options="filters[filterType]"
        :title="filterTypeTitle(filterType)"
        :filter-type="filterType"
        @toggle-filter="toggleFilter"
      />
    </form>
  </section>
</template>

<script lang="ts">
import { computed, defineComponent } from "vue"
import { storeToRefs } from "pinia"

import { useRouter } from "@nuxtjs/composition-api"

import { watchDebounced } from "@vueuse/core"

import { useSearchStore } from "~/stores/search"
import { areQueriesEqual, ApiQueryParams } from "~/utils/search-query-transform"
import type { NonMatureFilterCategory } from "~/constants/filters"
import { useI18n } from "~/composables/use-i18n"
import { useAnalytics } from "~/composables/use-analytics"

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
  setup() {
    const searchStore = useSearchStore()

    const i18n = useI18n()
    const router = useRouter()

    const { sendCustomEvent } = useAnalytics()

    const {
      isAnyFilterApplied,
      searchQueryParams,
      searchTerm,
      searchType,
      searchFilters: filters,
    } = storeToRefs(searchStore)

    const filterTypes = computed(
      () => Object.keys(filters.value) as NonMatureFilterCategory[]
    )
    const filterTypeTitle = (filterType: NonMatureFilterCategory) => {
      return i18n.t(`filters.${filterType}.title`).toString()
    }

    /**
     * This watcher fires even when the queries are equal. We update the path only
     * when the queries change.
     */
    watchDebounced(
      searchQueryParams,
      (newQuery: ApiQueryParams, oldQuery: ApiQueryParams) => {
        if (!areQueriesEqual(newQuery, oldQuery)) {
          router.push(searchStore.getSearchPath())
        }
      },
      { debounce: 800, maxWait: 5000 }
    )

    const toggleFilter = ({
      filterType,
      code,
    }: {
      filterType: NonMatureFilterCategory
      code: string
    }) => {
      const checked = searchStore.toggleFilter({ filterType, code })
      sendCustomEvent("APPLY_FILTER", {
        category: filterType,
        key: code,
        checked,
        searchType: searchType.value,
        query: searchTerm.value,
      })
    }

    return {
      isAnyFilterApplied,
      filters,
      filterTypes,
      filterTypeTitle,
      clearFilters: searchStore.clearFilters,
      toggleFilter,
    }
  },
})
</script>
