<template>
  <FiltersList
    :class="{
      'search-filters': true,
      'search-filters__visible': isFilterVisible,
    }"
    data-testid="filters-list"
    @onUpdateFilter="onUpdateFilter"
    @onToggleSearchGridFilter="onToggleSearchGridFilter"
    @onClearFilters="onClearFilters"
  />
</template>

<script>
import { mapActions, mapMutations, mapState } from 'vuex'
import {
  SET_FILTER_IS_VISIBLE,
  CLEAR_FILTERS,
} from '~/constants/mutation-types'
import { TOGGLE_FILTER } from '~/constants/action-types'
import { FILTER } from '~/constants/store-modules'
import FiltersList from '~/components/Filters/FiltersList'

export default {
  name: 'SearchGridFilter',
  components: { FiltersList },
  computed: {
    ...mapState(FILTER, ['filters', 'isFilterVisible']),
  },
  methods: {
    ...mapActions(FILTER, {
      toggleFilter: TOGGLE_FILTER,
      clearFilters: CLEAR_FILTERS,
    }),
    ...mapMutations(FILTER, {
      setFilterVisible: SET_FILTER_IS_VISIBLE,
    }),
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
}

.search-filters__visible {
  display: block;
}
</style>
