<template>
  <div class="filter-display" aria-live="polite">
    <span v-if="anyFilterApplied" class="caption font-semibold">{{
      $t('filters.filter-by')
    }}</span>
    <FilterBlock
      v-for="filter in getAppliedFilters"
      :key="filter.code"
      :code="filter.code"
      :label="filter.name"
      :filter-type="filter.filterType"
      @filterChanged="onUpdateFilter"
    />
  </div>
</template>
<script>
import { TOGGLE_FILTER } from '~/store-modules/action-types'
import FilterBlock from './FilterBlock'

export default {
  name: 'FilterDisplay',
  components: {
    FilterBlock,
  },
  props: ['provider'],
  computed: {
    getAppliedFilters() {
      return this.$store.getters.getAppliedFilterTags
    },
    anyFilterApplied() {
      return this.$store.state.isFilterApplied
    },
  },
  methods: {
    onUpdateFilter({ code, filterType }) {
      this.$store.dispatch(TOGGLE_FILTER, { code, filterType })
    },
  },
}
</script>
<style lang="scss" scoped>
.filter-display {
  display: flex;
  align-items: center;
  padding: 1rem;
  .caption {
    margin-right: 0.5rem;
  }
}
</style>
