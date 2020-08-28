<template>
  <div class="filter-display padding-normal" aria-live="polite">
    <span v-if="anyFilterApplied" class="caption has-text-weight-semibold"
      >Filter By</span
    >
    <span v-for="filter in getFilters('licenses')" :key="filter.code">
      <filter-block
        :code="filter.code"
        :label="filter.name"
        filter-type="licenses"
        @filterChanged="onUpdateFilter"
      />
    </span>
    <span v-for="filter in getFilters('licenseTypes')" :key="filter.code">
      <filter-block
        :code="filter.code"
        :label="filter.name"
        filter-type="licenseTypes"
        @filterChanged="onUpdateFilter"
      />
    </span>
    <span v-for="filter in getFilters('categories')" :key="filter.code">
      <filter-block
        :code="filter.code"
        :label="filter.name"
        filter-type="categories"
        @filterChanged="onUpdateFilter"
      />
    </span>
    <span v-for="filter in getFilters('extensions')" :key="filter.code">
      <filter-block
        :code="filter.code"
        :label="filter.name"
        filter-type="extensions"
        @filterChanged="onUpdateFilter"
      />
    </span>
    <span v-for="filter in getFilters('aspectRatios')" :key="filter.code">
      <filter-block
        :code="filter.code"
        :label="filter.name"
        filter-type="aspectRatios"
        @filterChanged="onUpdateFilter"
      />
    </span>
    <span v-for="filter in getFilters('sizes')" :key="filter.code">
      <filter-block
        :code="filter.code"
        :label="filter.name"
        filter-type="sizes"
        @filterChanged="onUpdateFilter"
      />
    </span>
    <span v-for="filter in getFilters('providers')" :key="filter.code">
      <filter-block
        :code="filter.code"
        :label="filter.name"
        filter-type="providers"
        @filterChanged="onUpdateFilter"
      />
    </span>
    <span>
      <filter-block
        v-if="searchByCreator"
        label="Creator"
        filter-type="searchBy"
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
      this.$store.dispatch(TOGGLE_FILTER, {
        code,
        filterType,
        provider: this.$props.provider,
      })
    },
    onUpdateBoolFilter({ filterType }) {
      this.$store.dispatch(TOGGLE_FILTER, {
        filterType,
        provider: this.$props.provider,
      })
    },
  },
}
</script>
