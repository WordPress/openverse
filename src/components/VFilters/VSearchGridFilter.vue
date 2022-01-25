<template>
  <div
    class="py-8 px-10 min-h-full"
    :class="{
      'bg-dark-charcoal-06': isMinScreenMd,
    }"
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
import { kebabize } from '~/utils/format-strings'

import {
  CLEAR_FILTERS,
  FETCH_MEDIA,
  TOGGLE_FILTER,
} from '~/constants/action-types'
import { MEDIA, SEARCH } from '~/constants/store-modules'
import { isMinScreen } from '~/composables/use-media-query'

import VFilterChecklist from '~/components/VFilters/VFilterChecklist.vue'

export default {
  name: 'VSearchGridFilter',
  components: {
    VFilterChecklist,
  },
  setup() {
    const { i18n, store } = useContext()
    const router = useRouter()
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
      isMinScreenMd,
    }
  },
}
</script>
