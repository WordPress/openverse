<template>
  <section
    id="filters"
    aria-labelledby="filters-heading"
    class="filters py-8 px-10"
  >
    <div class="flex items-center justify-between mt-2 mb-6">
      <h4 id="filters-heading" class="text-sr font-semibold py-2 uppercase">
        {{ $t('filter-list.filter-by') }}
      </h4>
      <button
        v-if="isAnyFilterApplied"
        id="clear-filter-button"
        type="button"
        class="text-sm py-2 px-4 text-pink hover:border-dark-gray"
        @click="clearFilters"
      >
        {{ $t('filter-list.clear') }}
      </button>
    </div>
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
    <footer v-if="isAnyFilterApplied" class="flex justify-between">
      <button
        class="text-sm py-4 px-6 lowercase rounded bg-trans-blue text-white md:hidden hover:bg-trans-blue-action"
        type="button"
        @click="$emit('close')"
      >
        {{ $t('filter-list.show') }}
      </button>
    </footer>
  </section>
</template>

<script>
import {
  computed,
  useContext,
  useRoute,
  useRouter,
  watch,
} from '@nuxtjs/composition-api'
import { kebab } from 'case'

import { useSearchStore } from '~/stores/search'
import { areQueriesEqual } from '~/utils/search-query-transform'

import VFilterChecklist from '~/components/VFilters/VFilterChecklist.vue'

export default {
  name: 'VSearchGridFilter',
  components: {
    VFilterChecklist,
  },
  setup() {
    const searchStore = useSearchStore()

    const { app, i18n } = useContext()
    const route = useRoute()
    const router = useRouter()

    const isAnyFilterApplied = computed(() => searchStore.isAnyFilterApplied)
    const filters = computed(() => searchStore.searchFilters)
    const filterTypes = computed(() => Object.keys(filters.value))
    const filterTypeTitle = (filterType) => {
      if (filterType === 'searchBy') {
        return ''
      }
      return i18n.t(`filters.${kebab(filterType)}.title`)
    }

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

    return {
      isAnyFilterApplied,
      filters,
      filterTypes,
      filterTypeTitle,
      clearFilters: searchStore.clearFilters,
      toggleFilter: searchStore.toggleFilter,
    }
  },
}
</script>
