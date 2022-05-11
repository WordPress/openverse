<template>
  <section
    id="filters"
    aria-labelledby="filters-heading"
    class="filters py-8 px-10"
  >
    <div class="flex items-center justify-between mt-2 mb-6">
      <h4
        id="filters-heading"
        class="text-sr font-semibold py-2 uppercase leading-8"
      >
        {{ $t('filter-list.filter-by') }}
      </h4>
      <VButton
        v-if="isAnyFilterApplied"
        id="clear-filter-button"
        variant="plain"
        class="text-sm font-semibold py-2 px-4 text-pink hover:ring hover:ring-pink"
        @click="clearFilters"
        @keydown.shift.tab.exact="focusFilterButton"
      >
        {{ $t('filter-list.clear') }}
      </VButton>
    </div>
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
    <footer v-if="isAnyFilterApplied" class="md:hidden flex justify-between">
      <VButton variant="primary" @click="$emit('close')">
        {{ $t('filter-list.show') }}
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
  useRoute,
  useRouter,
  watch,
} from '@nuxtjs/composition-api'
import { kebab } from 'case'

import { useSearchStore } from '~/stores/search'
import { areQueriesEqual } from '~/utils/search-query-transform'
import { Focus, focusIn, getFocusableElements } from '~/utils/focus-management'
import type { NonMatureFilterCategory } from '~/constants/filters'
import { useFocusFilters } from '~/composables/use-focus-filters'
import { defineEvent } from '~/types/emits'

import VFilterChecklist from '~/components/VFilters/VFilterChecklist.vue'
import VButton from '~/components/VButton.vue'

export default defineComponent({
  name: 'VSearchGridFilter',
  components: {
    VButton,
    VFilterChecklist,
  },
  emits: {
    close: defineEvent(),
  },
  setup() {
    const searchStore = useSearchStore()

    const { app, i18n } = useContext()
    const route = useRoute()
    const router = useRouter()

    const filtersFormRef = ref<HTMLFormElement>(null)

    const isAnyFilterApplied = computed(() => searchStore.isAnyFilterApplied)
    const filters = computed(() => searchStore.searchFilters)
    const filterTypes = computed(
      () => Object.keys(filters.value) as NonMatureFilterCategory[]
    )
    const filterTypeTitle = (filterType: string) =>
      filterType === 'searchBy'
        ? ''
        : i18n.t(`filters.${kebab(filterType)}.title`)

    /**
     * This watcher fires even when the queries are equal. We update the path only
     * when the queries change.
     */
    watch(
      () => searchStore.searchQueryParams,
      /**
       * @param {import('~/utils/search-query-transform').ApiQueryParams} newQuery
       * @param {import('~/utils/search-query-transform').ApiQueryParams} oldQuery
       */
      (newQuery, oldQuery) => {
        if (!areQueriesEqual(newQuery, oldQuery)) {
          const newPath = app.localePath({
            path: route.value.path,
            query: searchStore.searchQueryParams,
          })
          router.push(newPath)
        }
      }
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
      if (lastFocusableElement.value === event.target) {
        event.preventDefault()
        focusIn(document.querySelector('main'), Focus.First)
      }
    }
    /**
     * Move focus to the filter button only when this checkbox is the first focusable
     * element in the search grid filter, i.e. the 'Clear filters' button is hidden.
     * @param event - The keydown event
     */
    const handleShiftTabKey = (event: KeyboardEvent) => {
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
