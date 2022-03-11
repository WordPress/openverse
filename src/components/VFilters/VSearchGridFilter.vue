<template>
  <div
    class="filters py-8 px-10 min-h-full md:bg-dark-charcoal-06"
    data-testid="filters-list"
    @onUpdateFilter="onUpdateFilter"
    @onToggleSearchGridFilter="$emit('close')"
    @onClearFilters="clearFilters"
  >
    <div class="flex items-center justify-between mt-2 mb-6">
      <h4 class="text-sr font-semibold py-2 uppercase">
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
        @filterChanged="onUpdateFilter"
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
  </div>
</template>

<script>
import { computed, useContext, useRouter } from '@nuxtjs/composition-api'
import { kebab } from 'case'

import { useFilterStore } from '~/stores/filter'
import {
  CLEAR_FILTERS,
  FETCH_MEDIA,
  TOGGLE_FILTER,
} from '~/constants/action-types'
import { MEDIA, SEARCH } from '~/constants/store-modules'

import VFilterChecklist from '~/components/VFilters/VFilterChecklist.vue'

export default {
  name: 'VSearchGridFilter',
  components: {
    VFilterChecklist,
  },
  setup() {
    const filterStore = useFilterStore()
    const { i18n, store } = useContext()
    const router = useRouter()

    const isAnyFilterApplied = computed(() => filterStore.isAnyFilterApplied)

    const filters = computed(() => {
      return store.getters[`${SEARCH}/searchFilters`]
    })
    const filterTypes = computed(() => Object.keys(filters.value))
    const filterTypeTitle = (filterType) => {
      if (filterType === 'searchBy') {
        return ''
      }
      return i18n.t(`filters.${kebab(filterType)}.title`)
    }

    const updateSearch = async () => {
      await router.push({ query: store.getters['search/searchQueryParams'] })
      await store.dispatch(`${MEDIA}/${FETCH_MEDIA}`, {
        ...store.getters['search/searchQueryParams'],
      })
    }

    const onUpdateFilter = async ({ code, filterType }) => {
      await store.dispatch(`${SEARCH}/${TOGGLE_FILTER}`, { code, filterType })
      await updateSearch()
    }
    const clearFilters = async () => {
      await store.dispatch(`${SEARCH}/${CLEAR_FILTERS}`)

      await updateSearch()
    }

    return {
      isAnyFilterApplied,
      filters,
      filterTypes,
      filterTypeTitle,
      clearFilters,
      onUpdateFilter,
    }
  },
}
</script>
<style scoped>
.filters {
  border-inline-start: 1px solid transparent;
}
@screen md {
  .filters {
    /* dark-charcoal-20*/
    border-inline-start: 1px solid #d6d4d5;
  }
}
</style>
