<template>
  <div
    :class="{
      'search-filters': true,
      'search-filters__visible': isFilterVisible,
    }"
  >
    <FiltersList
      :filters="filters"
      :is-filter-applied="isFilterApplied"
      :license-types-disabled="licenseTypesDisabled"
      :licenses-disabled="licensesDisabled"
      @onUpdateFilter="onUpdateFilter"
      @onUpdateSearchByCreator="onUpdateSearchByCreator"
      @onToggleSearchGridFilter="onToggleSearchGridFilter"
      @onClearFilters="onClearFilters"
    />
  </div>
</template>

<script>
import {
  SET_FILTER_IS_VISIBLE,
  CLEAR_FILTERS,
} from '~/store-modules/mutation-types'
import { TOGGLE_FILTER } from '~/store-modules/action-types'
import FiltersList from './FiltersList'

export default {
  name: 'SearchGridFilter',
  components: {
    FiltersList,
  },
  computed: {
    isFilterApplied() {
      return this.$store.state.isFilterApplied
    },
    isFilterVisible() {
      return this.$store.state.isFilterVisible
    },
    filters() {
      return this.$store.state.filters
    },
    licensesDisabled() {
      return this.$store.state.filters.licenseTypes.some((li) => li.checked)
    },
    licenseTypesDisabled() {
      return this.$store.state.filters.licenses.some((li) => li.checked)
    },
    /**
     * Show filters expanded by default
     * @todo: The A/B test is over and we're going with the expanded view. Can remove a lot of this old test logic
     */

    filtersExpandedByDefault() {
      return true
    },
  },
  methods: {
    onUpdateFilter({ code, filterType }) {
      this.$store.dispatch(TOGGLE_FILTER, {
        code,
        filterType,
      })
    },
    onClearFilters() {
      this.$store.commit(CLEAR_FILTERS, {})
    },
    onUpdateSearchByCreator() {
      this.$store.dispatch(TOGGLE_FILTER, {
        filterType: 'searchBy',
      })
    },
    onToggleSearchGridFilter() {
      this.$store.commit(SET_FILTER_IS_VISIBLE, {
        isFilterVisible: !this.isFilterVisible,
      })
    },
  },
}
</script>

<style lang="scss" scoped>
@import 'bulma/sass/utilities/_all.sass';

.search-filters {
  display: none;
  height: auto;
  max-height: 100%;
  overflow-y: scroll;

  label {
    color: #333333;
  }

  @include touch {
    width: 21.875rem;
    max-width: 100%;
    max-height: 37rem;
    overflow-x: hidden;
  }

  &__visible {
    border-top: 1px solid #e8e8e8;
    display: block;
  }
}
</style>
