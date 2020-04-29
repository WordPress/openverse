<template>
    <div class="filter-display padding-horizontal-normal" aria-live="polite">
        <span v-if="anyFilterApplied()" class="caption has-text-weight-semibold">Filter By</span>
        <span v-for="filter in getFilters('licenses')" :key="filter.code">
          <filter-block :filter="filter"
                        filterType="licenses"
                        @filterChanged="onUpdateFilter" />
        </span>
        <span v-for="filter in getFilters('licenseTypes')" :key="filter.code">
          <filter-block :filter="filter"
                        filterType="licenseTypes"
                        @filterChanged="onUpdateFilter" />
        </span>
        <span v-for="filter in getFilters('categories')" :key="filter.code">
          <filter-block :filter="filter"
                        filterType="categories"
                        @filterChanged="onUpdateFilter" />
        </span>
        <span v-for="filter in getFilters('extensions')" :key="filter.code">
          <filter-block :filter="filter"
                        filterType="extensions"
                        @filterChanged="onUpdateFilter" />
        </span>
        <span v-for="filter in getFilters('aspectRatios')" :key="filter.code">
          <filter-block :filter="filter"
                        filterType="aspectRatios"
                        @filterChanged="onUpdateFilter" />
        </span>
        <span v-for="filter in getFilters('sizes')" :key="filter.code">
          <filter-block :filter="filter"
                        filterType="sizes"
                        @filterChanged="onUpdateFilter" />
        </span>
        <span v-for="filter in getFilters('providers')" :key="filter.code">
          <filter-block :filter="filter"
                        filterType="providers"
                        @filterChanged="onUpdateFilter" />
        </span>
        <span>
          <filter-block v-if="searchByFilters"
                        :filter="searchByFilters"
                        filterType="searchByCreator"
                        @filterChanged="onUpdateSearchByCreator" />
        </span>
    </div>
</template>
<script>
import { TOGGLE_FILTER } from '@/store/action-types';
import FilterBlock from '@/components/FilterBlock';

const filterMap = {
  licenses: 'license',
  licenseTypes: 'license_type',
  categories: 'categories',
  extensions: 'extension',
  aspectRatios: 'aspect_ratio',
  sizes: 'size',
  providers: 'source',
};

export default {
  name: 'filter-display',
  props: ['query', 'isCollectionsPage', 'provider'],
  components: {
    FilterBlock,
  },
  computed: {
    searchByFilters() {
      return this.$store.state.filters.searchBy.creator ? this.$store.state.filters.searchBy : null;
    },
  },
  methods: {
    getFilters(filterType) {
      const filterTags = [];
      this.$props.query[filterMap[filterType]].split(',').forEach((filter) => {
        const filterObj = this.$store.state.filters[filterType].find(o => o.code === filter);
        if (filterObj) {
          filterTags.push(filterObj);
        }
      });
      return filterTags;
    },
    anyFilterApplied() {
      const filters = Object.keys(filterMap).map(key => this.getFilters(key));

      return filters.some(f => f.length !== 0);
    },
    onUpdateFilter({ code, filterType }) {
      this.$store.dispatch(TOGGLE_FILTER, {
        code,
        filterType,
        isCollectionsPage: this.$props.isCollectionsPage,
        provider: this.$props.provider,
        shouldNavigate: true,
      });
    },
    onUpdateSearchByCreator() {
      this.$store.dispatch(TOGGLE_FILTER, {
        filterType: 'searchBy',
        isCollectionsPage: this.$props.isCollectionsPage,
        provider: this.$props.provider,
        shouldNavigate: true,
      });
    },
  },
};
</script>
