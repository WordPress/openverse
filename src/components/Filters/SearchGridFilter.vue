<template>
  <div
    class="p-4 search-filters h-auto max-h-full overflow-y-scroll"
    :class="[isFilterVisible ? 'block' : 'hidden']"
    data-testid="filters-list"
    @onUpdateFilter="onUpdateFilter"
    @onToggleSearchGridFilter="onToggleSearchGridFilter"
    @onClearFilters="onClearFilters"
  >
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
          <CloseIcon class="w-4 h-4" />
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
        type="button"
        class="text-sm py-2 px-4 lowercase rounded color-dark-blue border border-dark-blue hover:text-white hover:bg-dark-gray hover:border-dark-gray"
        @click="onClearFilters"
      >
        {{ $t('filter-list.clear') }}
      </button>
      <button
        class="text-sm py-4 px-6 lowercase rounded bg-trans-blue text-white lg:hidden hover:bg-trans-blue-action"
        type="button"
        @click="onToggleSearchGridFilter"
      >
        {{ $t('filter-list.show') }}
      </button>
    </footer>
  </div>
</template>

<script>
import { mapActions, mapGetters, mapMutations, mapState } from 'vuex'
import { SET_FILTER_IS_VISIBLE } from '~/constants/mutation-types'
import { CLEAR_FILTERS, TOGGLE_FILTER } from '~/constants/action-types'
import { SEARCH } from '~/constants/store-modules'
import { kebabize } from '~/utils/format-strings'
import FilterChecklist from '~/components/Filters/FilterChecklist'
import CloseIcon from '~/assets/icons/close.svg?inline'

export default {
  name: 'SearchGridFilter',
  components: {
    CloseIcon,
    FilterChecklist,
  },
  computed: {
    ...mapState(SEARCH, ['isFilterVisible']),
    ...mapGetters(SEARCH, ['mediaFiltersForDisplay', 'isAnyFilterApplied']),
    filters() {
      return this.mediaFiltersForDisplay || {}
    },
    filterTypes() {
      return Object.keys(this.filters)
    },
  },
  methods: {
    ...mapActions(SEARCH, {
      toggleFilter: TOGGLE_FILTER,
      clearFilters: CLEAR_FILTERS,
    }),
    ...mapMutations(SEARCH, {
      setFilterVisible: SET_FILTER_IS_VISIBLE,
    }),
    filterTypeTitle(filterType) {
      if (filterType === 'searchBy') {
        return ''
      }
      return this.$t(`filters.${kebabize(filterType)}.title`)
    },
    onUpdateFilter({ code, filterType }) {
      this.toggleFilter({ code, filterType })
    },
    onClearFilters() {
      this.clearFilters()
    },
    onToggleSearchGridFilter() {
      this.setFilterVisible({
        isFilterVisible: !this.isFilterVisible,
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.search-filters {
  /* Works on Firefox */
  scrollbar-color: transparent transparent;
  scrollbar-width: thin;
  /* Works on Chrome, Edge, and Safari */
  &::-webkit-scrollbar {
    width: 12px;
  }
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  &::-webkit-scrollbar-thumb {
    background-color: transparent;
    border-radius: 20px;
  }
  @include touch {
    width: 21.875rem;
    max-width: 100%;
    max-height: 37rem;
    overflow-x: hidden;
  }
}
</style>
