<template>
  <div class="filter-display padding-normal" aria-live="polite">
    <span v-if="anyFilterApplied" class="caption has-text-weight-semibold"
      >Filter By</span
    >
    <span v-for="filter in getFilters('licenses')" :key="filter.code">
      <filter-block
        :code="filter.code"
        :label="filter.name"
        filterType="licenses"
        @filterChanged="onUpdateFilter"
      />
    </span>
    <span v-for="filter in getFilters('licenseTypes')" :key="filter.code">
      <filter-block
        :code="filter.code"
        :label="filter.name"
        filterType="licenseTypes"
        @filterChanged="onUpdateFilter"
      />
    </span>
    <span v-for="filter in getFilters('categories')" :key="filter.code">
      <filter-block
        :code="filter.code"
        :label="filter.name"
        filterType="categories"
        @filterChanged="onUpdateFilter"
      />
    </span>
    <span v-for="filter in getFilters('extensions')" :key="filter.code">
      <filter-block
        :code="filter.code"
        :label="filter.name"
        filterType="extensions"
        @filterChanged="onUpdateFilter"
      />
    </span>
    <span v-for="filter in getFilters('aspectRatios')" :key="filter.code">
      <filter-block
        :code="filter.code"
        :label="filter.name"
        filterType="aspectRatios"
        @filterChanged="onUpdateFilter"
      />
    </span>
    <span v-for="filter in getFilters('sizes')" :key="filter.code">
      <filter-block
        :code="filter.code"
        :label="filter.name"
        filterType="sizes"
        @filterChanged="onUpdateFilter"
      />
    </span>
    <span v-for="filter in getFilters('providers')" :key="filter.code">
      <filter-block
        :code="filter.code"
        :label="filter.name"
        filterType="providers"
        @filterChanged="onUpdateFilter"
      />
    </span>
    <span>
      <filter-block
        v-if="searchByCreator"
        label="Creator"
        filterType="searchBy"
        @filterChanged="onUpdateBoolFilter"
      />
    </span>
    <!-- <span>
          <filter-block v-if="mature"
                        label="Mature"
                        filterType="mature"
                        @filterChanged="onUpdateBoolFilter" />
        </span> -->
  </div>
</template>
<script>
import { TOGGLE_FILTER } from '../../src/store/action-types'
import FilterBlock from '../../src/components/Filters/FilterBlock'

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
  name: 'filter-display',
  props: ['query', 'provider'],
  components: {
    FilterBlock,
  },
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
      this.$store.dispatch(TOGGLE_FILTER, {
        code,
        filterType,
        provider: this.$props.provider,
        shouldNavigate: true,
      })
    },
    onUpdateBoolFilter({ filterType }) {
      this.$store.dispatch(TOGGLE_FILTER, {
        filterType,
        provider: this.$props.provider,
        shouldNavigate: true,
      })
    },
  },
}
</script>
