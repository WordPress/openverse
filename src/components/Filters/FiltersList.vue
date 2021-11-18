<template>
  <div class="p-4">
    <div class="flex items-center justify-between mt-4 mb-8">
      <h4 class="text-2xl">
        {{ $t('filter-list.filter-by') }}
      </h4>
      <button
        id="hide-filters-button"
        type="button"
        class="text-sm font-medium my-auto"
        @click="onToggleSearchGridFilter"
      >
        <span class="text-trans-blue hidden lg:block text-sm lowercase">{{
          $t('filter-list.hide')
        }}</span>
        <span class="me-4 text-lg lg:hidden">
          <i class="icon cross" />
        </span>
      </button>
    </div>
    <form class="filters-form">
      <FilterChecklist
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
        id="clear-filter-button"
        class="text-sm py-2 px-4 lowercase rounded color-dark-blue border border-dark-blue hover:text-white hover:bg-dark-gray hover:border-dark-gray"
        @click="onClearFilters"
      >
        {{ $t('filter-list.clear') }}
      </button>
      <button
        class="text-sm py-4 px-6 lowercase rounded bg-trans-blue text-white lg:hidden hover:bg-trans-blue-action"
        @click="onToggleSearchGridFilter"
      >
        {{ $t('filter-list.show') }}
      </button>
    </footer>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { kebabize } from '~/utils/format-strings'
import { SEARCH } from '~/constants/store-modules'
import FilterChecklist from './FilterChecklist'

export default {
  name: 'FiltersList',
  components: {
    FilterChecklist,
  },
  computed: {
    ...mapGetters(SEARCH, ['mediaFiltersForDisplay', 'isAnyFilterApplied']),
    filters() {
      return this.mediaFiltersForDisplay || {}
    },
    filterTypes() {
      return Object.keys(this.filters)
    },
  },
  methods: {
    filterTypeTitle(filterType) {
      if (filterType === 'searchBy') {
        return ''
      }
      return this.$t(`filters.${kebabize(filterType)}.title`)
    },
    onUpdateFilter({ code, filterType }) {
      this.$emit('onUpdateFilter', { code, filterType })
    },
    onToggleSearchGridFilter() {
      this.$emit('onToggleSearchGridFilter')
    },
    onClearFilters() {
      this.$emit('onClearFilters')
    },
  },
}
</script>
