<template>
  <FiltersList
    class="search-filters h-auto max-h-full overflow-y-scroll"
    :class="[isFilterVisible ? 'block' : 'hidden']"
    data-testid="filters-list"
    @onUpdateFilter="onUpdateFilter"
    @onToggleSearchGridFilter="onToggleSearchGridFilter"
    @onClearFilters="onClearFilters"
  />
</template>

<script>
import { mapActions, mapMutations, mapState } from 'vuex'
import { SET_FILTER_IS_VISIBLE } from '~/constants/mutation-types'
import { CLEAR_FILTERS, TOGGLE_FILTER } from '~/constants/action-types'
import { SEARCH } from '~/constants/store-modules'
import FiltersList from '~/components/Filters/FiltersList'

export default {
  name: 'SearchGridFilter',
  components: { FiltersList },
  computed: {
    ...mapState(SEARCH, ['filters', 'isFilterVisible']),
  },
  methods: {
    ...mapActions(SEARCH, {
      toggleFilter: TOGGLE_FILTER,
      clearFilters: CLEAR_FILTERS,
    }),
    ...mapMutations(SEARCH, {
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
  @include touch {
    width: 21.875rem;
    max-width: 100%;
    max-height: 37rem;
    overflow-x: hidden;
  }
}
</style>
