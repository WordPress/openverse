<template>
  <FiltersList
    :class="{
      'search-filters': true,
      'search-filters__visible': isFilterVisible,
    }"
    @onUpdateFilter="onUpdateFilter"
    @onToggleSearchGridFilter="onToggleSearchGridFilter"
    @onClearFilters="onClearFilters"
  />
</template>

<script>
import { mapState } from 'vuex'
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
    ...mapState(['filters', 'isFilterVisible']),
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
    onToggleSearchGridFilter() {
      this.$store.commit(SET_FILTER_IS_VISIBLE, {
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
