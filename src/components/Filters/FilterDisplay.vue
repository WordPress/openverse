<template>
  <div class="filter-display" aria-live="polite">
    <span v-if="anyFilterApplied" class="caption font-semibold">{{
      $t('filters.filter-by')
    }}</span>
    <FilterBlock
      v-for="filter in getFilters('licenses')"
      :key="filter.code"
      :code="filter.code"
      :label="filter.name"
      filter-type="licenses"
      @filterChanged="onUpdateFilter"
    />
    <FilterBlock
      v-for="filter in getFilters('licenseTypes')"
      :key="filter.code"
      :code="filter.code"
      :label="filter.name"
      filter-type="licenseTypes"
      @filterChanged="onUpdateFilter"
    />
    <FilterBlock
      v-for="filter in getFilters('categories')"
      :key="filter.code"
      :code="filter.code"
      :label="filter.name"
      filter-type="categories"
      @filterChanged="onUpdateFilter"
    />
    <FilterBlock
      v-for="filter in getFilters('extensions')"
      :key="filter.code"
      :code="filter.code"
      :label="filter.name"
      filter-type="extensions"
      @filterChanged="onUpdateFilter"
    />
    <FilterBlock
      v-for="filter in getFilters('aspectRatios')"
      :key="filter.code"
      :code="filter.code"
      :label="filter.name"
      filter-type="aspectRatios"
      @filterChanged="onUpdateFilter"
    />
    <FilterBlock
      v-for="filter in getFilters('sizes')"
      :key="filter.code"
      :code="filter.code"
      :label="filter.name"
      filter-type="sizes"
      @filterChanged="onUpdateFilter"
    />
    <FilterBlock
      v-for="filter in getFilters('providers')"
      :key="filter.code"
      :code="filter.code"
      :label="filter.name"
      filter-type="providers"
      @filterChanged="onUpdateFilter"
    />
    <FilterBlock
      v-if="searchByCreator"
      label="Creator"
      filter-type="searchBy"
      @filterChanged="onUpdateBoolFilter"
    />
  </div>
</template>
<script>
import { TOGGLE_FILTER } from '~/store-modules/action-types'
import FilterBlock from './FilterBlock'

const filterMap = {
  licenses: 'license',
  licenseTypes: 'license_type',
  categories: 'categories',
  extensions: 'extension',
  aspectRatios: 'aspect_ratio',
  sizes: 'size',
  providers: 'source',
}

export default {
  name: 'FilterDisplay',
  components: {
    FilterBlock,
  },
  props: ['query', 'provider'],
  computed: {
    searchByCreator() {
      return this.$store.state.filters.searchBy.creator
    },
    mature() {
      return this.$store.state.filters.mature
    },
    anyFilterApplied() {
      return this.$store.state.isFilterApplied
    },
  },
  methods: {
    getFilters(filterType) {
      const filterTags = []
      const activeFilter = this.$props.query[filterMap[filterType]]
      if (!activeFilter) return []

      activeFilter.split(',').forEach((filter) => {
        const filterObj = this.$store.state.filters[filterType].find(
          (o) => o.code === filter
        )
        if (filterObj) {
          filterTags.push(filterObj)
        }
      })
      return filterTags
    },
    onUpdateFilter({ code, filterType }) {
      this.$store.dispatch(TOGGLE_FILTER, { code, filterType })
    },
    onUpdateBoolFilter({ filterType }) {
      this.$store.dispatch(TOGGLE_FILTER, { filterType })
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
