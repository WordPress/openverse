<template>
    <div class="padding-horizontal-normal">
        <span class="caption has-text-weight-semibold">Filter By</span>
        <span v-for="filter in licenseFilters" :key="filter">
          <filter-block :filter="filter"
                        filterType="licenses"
                        @filterChanged="onUpdateFilter" />
        </span>
        <span v-for="filter in licenseTypeFilters" :key="filter">
          <filter-block :filter="filter"
                        filterType="licenseTypes"
                        @filterChanged="onUpdateFilter" />
        </span>
        <span v-for="filter in categoryFilters" :key="filter">
          <filter-block :filter="filter"
                        filterType="categories"
                        @filterChanged="onUpdateFilter" />
        </span>
        <span v-for="filter in extensionFilters" :key="filter">
          <filter-block :filter="filter"
                        filterType="extensions"
                        @filterChanged="onUpdateFilter" />
        </span>
        <span v-for="filter in aspectRatioFilters" :key="filter">
          <filter-block :filter="filter"
                        filterType="aspectRatios"
                        @filterChanged="onUpdateFilter" />
        </span>
        <span v-for="filter in sizeFilters" :key="filter">
          <filter-block :filter="filter"
                        filterType="sizes"
                        @filterChanged="onUpdateFilter" />
        </span>
        <span v-for="filter in sourceFilters" :key="filter">
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

export default {
  name: 'filter-display',
  props: ['query', 'isCollectionsPage', 'provider'],
  components: {
    FilterBlock,
  },
  computed: {
    licenseFilters() {
      const filterTags = [];
      this.query.license.split(',').forEach((filter) => {
        const filterObj = this.$store.state.filters.licenses.find(o => o.code === filter);
        if (filterObj) {
          filterTags.push(filterObj);
        }
      });
      return filterTags;
    },
    licenseTypeFilters() {
      const filterTags = [];
      this.query.license_type.split(',').forEach((filter) => {
        const filterObj = this.$store.state.filters.licenseTypes.find(o => o.code === filter);
        if (filterObj) {
          filterTags.push(filterObj);
        }
      });
      return filterTags;
    },
    categoryFilters() {
      const filterTags = [];
      this.query.categories.split(',').forEach((filter) => {
        const filterObj = this.$store.state.filters.categories.find(o => o.code === filter);
        if (filterObj) {
          filterTags.push(filterObj);
        }
      });
      return filterTags;
    },
    extensionFilters() {
      const filterTags = [];
      this.query.extension.split(',').forEach((filter) => {
        const filterObj = this.$store.state.filters.extensions.find(o => o.code === filter);
        if (filterObj) {
          filterTags.push(filterObj);
        }
      });
      return filterTags;
    },
    aspectRatioFilters() {
      const filterTags = [];
      this.query.aspect_ratio.split(',').forEach((filter) => {
        const filterObj = this.$store.state.filters.aspectRatios.find(o => o.code === filter);
        if (filterObj) {
          filterTags.push(filterObj);
        }
      });
      return filterTags;
    },
    sizeFilters() {
      const filterTags = [];
      this.query.size.split(',').forEach((filter) => {
        const filterObj = this.$store.state.filters.sizes.find(o => o.code === filter);
        if (filterObj) {
          filterTags.push(filterObj);
        }
      });
      return filterTags;
    },
    sourceFilters() {
      const filterTags = [];
      this.query.source.split(',').forEach((filter) => {
        const filterObj = this.$store.state.filters.providers.find(o => o.code === filter);
        if (filterObj) {
          filterTags.push(filterObj);
        }
      });
      return filterTags;
    },
    searchByFilters() {
      return this.$store.state.filters.searchBy.creator ? this.$store.state.filters.searchBy : null;
    },
  },
  methods: {
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
