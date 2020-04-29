<template>
  <div :class="{ 'search-filters': true,
                 'search-filters__visible': isFilterVisible, }">
    <form class="filters-form" role="filter">
      <filter-check-list :options="filters.licenseTypes"
                         :disabled="licenseTypesDisabled"
                         title="I want something that I can"
                         filterType="licenseTypes"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list :options="filters.licenses"
                         :disabled="licensesDisabled"
                         title="Licenses"
                         filterType="licenses"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list v-if="renderProvidersFilter"
                         :options="filters.providers"
                         title="Collections"
                         filterType="providers"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list :options="filters.categories"
                         title="Image Type"
                         filterType="categories"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list :options="filters.extensions"
                         title="File Type"
                         filterType="extensions"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list :options="filters.aspectRatios"
                         title="Aspect Ratio"
                         filterType="aspectRatios"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list :options="filters.sizes"
                         title="Image Size"
                         filterType="sizes"
                         @filterChanged="onUpdateFilter" />
    </form>

    <div class="margin-normal filter-option small-filter search-filters_search-by">
      <input type="checkbox" id="creator-chk"
              :checked="filters.searchBy.creator"
              @change="onUpdateSearchByCreator">
      <label for="creator-chk">Search by Creator</label>
    </div>

    <div class="margin-normal filter-option small-filter search-filters_search-by">
      <input type="checkbox" id="mature-chk"
              :checked="filters.mature"
              @change="onUpdateMature">
      <label for="mature-chk">Enable Mature Content</label>
    </div>

    <div class="margin-big padding-bottom-normal clear-filters"
          v-if="isFilterApplied">
      <button class="button tiny"
              @click="onClearFilters">
        Clear filters
      </button>
    </div>
  </div>
</template>

<script>
import { TOGGLE_FILTER } from '@/store/action-types';
import { CLEAR_FILTERS } from '@/store/mutation-types';
import FilterCheckList from './FilterChecklist';

export default {
  name: 'search-grid-filter',
  props: ['isCollectionsPage', 'provider'],
  components: {
    FilterCheckList,
  },
  computed: {
    isFilterApplied() {
      return this.$store.state.isFilterApplied;
    },
    isFilterVisible() {
      return this.$store.state.isFilterVisible;
    },
    filters() {
      return this.$store.state.filters;
    },
    renderProvidersFilter() {
      return !this.$props.isCollectionsPage;
    },
    licensesDisabled() {
      return this.$store.state.filters.licenseTypes.some(li => li.checked);
    },
    licenseTypesDisabled() {
      return this.$store.state.filters.licenses.some(li => li.checked);
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
    onUpdateMature() {
      this.$store.dispatch(TOGGLE_FILTER, {
        filterType: 'mature',
        isCollectionsPage: this.$props.isCollectionsPage,
        provider: this.$props.provider,
        shouldNavigate: true,
      });
    },
    onClearFilters() {
      this.$store.commit(CLEAR_FILTERS, {
        isCollectionsPage: this.$props.isCollectionsPage,
        provider: this.$props.provider,
        shouldNavigate: true,
      });
    },
  },
};
</script>

<style lang="scss" scoped>

.search-filters {
  display: none;
  height: auto;
  top: 0;
  position: sticky;

  label {
    color: #333333;
  }

  &__visible {
    border-top: 1px solid #e8e8e8;
    display: block;
  }
}

</style>
