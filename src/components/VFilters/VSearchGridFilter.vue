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
        class="label-bold absolute py-1 px-4 text-pink end-0 hover:ring hover:ring-pink"
        @click="clearFilters"
        @keydown.shift.tab.exact="focusFilterButton"
      >
        {{ $t("filter-list.clear") }}
      </VButton>
    </header>
    <form
      ref="filtersFormRef"
      class="filters-form"
      @keydown.tab.exact="handleTabKey"
      @keydown.shift.tab.exact="handleShiftTabKey"
    >
      <VFilterChecklist
        v-for="filterType in filterTypes"
        :key="filterType"
        :options="filters[filterType]"
        :title="filterTypeTitle(filterType)"
        :filter-type="filterType"
        @toggle-filter="toggleFilter"
      />
    </form>
    <footer
      v-if="showFilterHeader && isAnyFilterApplied"
      class="flex justify-between md:hidden"
    >
      <VButton variant="primary" @click="$emit('close')">
        {{ $t("filter-list.show") }}
      </VButton>
    </footer>
  </section>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  ref,
  useContext,
  useRouter,
} from "@nuxtjs/composition-api"
import { kebab } from "case"

import { watchDebounced } from "@vueuse/core"

import { useSearchStore } from "~/stores/search"
import { areQueriesEqual, ApiQueryParams } from "~/utils/search-query-transform"
import { Focus, focusIn, getFocusableElements } from "~/utils/focus-management"
import type { NonMatureFilterCategory } from "~/constants/filters"
import { useFocusFilters } from "~/composables/use-focus-filters"
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
  setup(props) {
    const searchStore = useSearchStore()

    const { i18n } = useContext()
    const router = useRouter()

    const filtersFormRef = ref<HTMLFormElement>(null)

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

    const focusableElements = computed(() =>
      getFocusableElements(filtersFormRef.value)
    )
    /**
     * Find the last focusable element in VSearchGridFilter to add a 'Tab' keydown event
     * handler to it.
     * We could actually hard-code this because 'searchBy' is always the last now.
     */
    const lastFocusableElement = computed<HTMLElement>(() => {
      return focusableElements.value[focusableElements.value.length - 1]
    })

    /**
     * We add the `Shift-Tab` handler to the first focusable checkbox so that focus can go back
     * to the filter button
     */
    const firstFocusableElement = computed<HTMLElement | undefined>(
      () => focusableElements.value[0]
    )

    /**
     * When the user presses 'Tab' on the last focusable element, we need to
     * move focus to the first focusable element in main.
     * @param event
     */
    const handleTabKey = (event: KeyboardEvent) => {
      if (!props.changeTabOrder) return
      if (lastFocusableElement.value === event.target) {
        event.preventDefault()
        focusIn(document.querySelector("main"), Focus.First)
      }
    }
    /**
     * Move focus to the filter button only when this checkbox is the first focusable
     * element in the search grid filter, i.e. the 'Clear filters' button is hidden.
     * @param event - The keydown event
     */
    const handleShiftTabKey = (event: KeyboardEvent) => {
      if (!props.changeTabOrder) return
      if (
        firstFocusableElement.value === event.target &&
        !isAnyFilterApplied.value
      ) {
        focusFilterButton(event)
      }
    }

    const focusFilters = useFocusFilters()
    const focusFilterButton = (event?: KeyboardEvent) => {
      focusFilters.focusFilterButton(event)
    }

    return {
      firstFocusableElement,
      filtersFormRef,
      isAnyFilterApplied,
      filters,
      filterTypes,
      filterTypeTitle,
      clearFilters: searchStore.clearFilters,
      toggleFilter: searchStore.toggleFilter,
      handleTabKey,
      handleShiftTabKey,
      focusFilterButton,
    }
  },
})
</script>
