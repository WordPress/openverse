<template>
  <div
    class="py-8 px-10 search-filters"
    :class="{
      'bg-dark-charcoal-06': isMinScreenMd,
    }"
    data-testid="filters-list"
    @onUpdateFilter="onUpdateFilter"
    @onToggleSearchGridFilter="$emit('close')"
    @onClearFilters="clearFilters"
  >
    <div class="flex items-center justify-between mt-4 mb-8">
      <h4 class="text-2xl">
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
import { computed, useContext } from '@nuxtjs/composition-api'
import { kebabize } from '~/utils/format-strings'

import { CLEAR_FILTERS, TOGGLE_FILTER } from '~/constants/action-types'
import { SEARCH } from '~/constants/store-modules'
import { isMinScreen } from '~/composables/use-media-query'

import VFilterChecklist from '~/components/VFilters/VFilterChecklist.vue'

export default {
  name: 'VSearchGridFilter',
  components: {
    VFilterChecklist,
  },
  setup() {
    const { i18n, store } = useContext()
    const isMinScreenMd = isMinScreen('md')

    const isAnyFilterApplied = computed(
      () => store.getters[`${SEARCH}/isAnyFilterApplied`]
    )
    const filters = computed(() => {
      return store.getters[`${SEARCH}/mediaFiltersForDisplay`] || {}
    })
    const filterTypes = computed(() => Object.keys(filters.value))
    const filterTypeTitle = (filterType) => {
      if (filterType === 'searchBy') {
        return ''
      }
      return i18n.t(`filters.${kebabize(filterType)}.title`)
    }
    const onUpdateFilter = ({ code, filterType }) => {
      store.dispatch(`${SEARCH}/${TOGGLE_FILTER}`, { code, filterType })
    }
    const clearFilters = () => {
      store.dispatch(`${SEARCH}/${CLEAR_FILTERS}`)
    }

    return {
      isAnyFilterApplied,
      filters,
      filterTypes,
      filterTypeTitle,
      clearFilters,
      onUpdateFilter,
      isMinScreenMd,
    }
  },
}
</script>
