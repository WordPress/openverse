<template>
  <div class="filter-display" aria-live="polite">
    <span v-if="isAnyFilterApplied" class="caption font-semibold">{{
      $t('filters.filter-by')
    }}</span>
    <FilterTag
      v-for="filter in appliedFilterTags"
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
import FilterTag from '~/components/Filters/FilterTag'

export default {
  name: 'FilterDisplay',
  components: { FilterTag },
  computed: {
    searchType() {
      return this.$store.state.searchType
    },
    isAnyFilterApplied() {
      return this.$store.getters.isAnyFilterApplied
    },
    appliedFilterTags() {
      return this.$store.getters.appliedFilterTags
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
