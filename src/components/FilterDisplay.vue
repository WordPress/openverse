<template>
    <div class="padding-horizontal-normal">
        <span>Filter By</span>
        <span v-for="filter in filters" :key="filter"><filter-block :filter="filter"/></span>
    </div>
</template>
<script>
import FilterBlock from '@/components/FilterBlock';

export default {
  name: 'filter-display',
  props: ['query'],
  components: {
    FilterBlock,
  },
  computed: {
    filters() {
      const filterTags = [];
      const filters = this.$store.state.filters;
      const licenseFilters = this.query.license.split(',');
      const licenseTypeFilters = this.query.license_type.split(',');
      const categoryFilters = this.query.categories.split(',');
      const extensionFilters = this.query.extension.split(',');
      const aspectRatioFilters = this.query.aspect_ratio.split(',');
      const sizeFilters = this.query.size.split(',');
      const sourceFilters = this.query.source.split(',');
      licenseFilters.forEach((filter) => {
        const filterObj = filters.licenses.find(o => o.code === filter);
        if (filterObj) {
          filterTags.push(filterObj);
        }
      });
      licenseTypeFilters.forEach((filter) => {
        const filterObj = filters.licenseTypes.find(o => o.code === filter);
        if (filterObj) {
          filterTags.push(filterObj);
        }
      });
      categoryFilters.forEach((filter) => {
        const filterObj = filters.categories.find(o => o.code === filter);
        if (filterObj) {
          filterTags.push(filterObj);
        }
      });
      extensionFilters.forEach((filter) => {
        const filterObj = filters.extensions.find(o => o.code === filter);
        if (filterObj) {
          filterTags.push(filterObj);
        }
      });
      aspectRatioFilters.forEach((filter) => {
        const filterObj = filters.aspectRatios.find(o => o.code === filter);
        if (filterObj) {
          filterTags.push(filterObj);
        }
      });
      sizeFilters.forEach((filter) => {
        const filterObj = filters.sizes.find(o => o.code === filter);
        if (filterObj) {
          filterTags.push(filterObj);
        }
      });
      sourceFilters.forEach((filter) => {
        const filterObj = filters.providers.find(o => o.code === filter);
        if (filterObj) {
          filterTags.push(filterObj);
        }
      });
      if (filters.searchBy.creator) {
        filterTags.push(filters.searchBy);
      }
      return filterTags;
    },
  },
};
</script>
