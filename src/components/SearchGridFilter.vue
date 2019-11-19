<template>
  <div :class="{ 'search-filters': true,
                 'search-filters__visible': isFilterVisible, }">
    <form class="filter-option" role="filter">
      <filter-check-list :options="filters.licenseTypes"
                         title="I want something that I can"
                         filterType="licenseTypes"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list v-if="renderProvidersFilter"
                         :options="filters.providers"
                         title="All Sources"
                         filterType="providers"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list :options="filters.imageTypes"
                         title="Image Type"
                         filterType="imageTypes"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list :options="filters.extensions"
                         title="File Type"
                         filterType="extensions"
                         @filterChanged="onUpdateFilter" />
    </form>

    <div class="filter-option small-filter search-filters_search-by">
      <input type="checkbox" id="creator-chk"
              :checked="filters.searchBy.creator"
              @change="onUpdateSearchByCreator">
      <label for="creator-chk">Search by Creator</label>
    </div>
    <div class="clear-filters"
          v-if="isFilterApplied">
      <a class="button primary medium search-filters_clear-btn"
              @click="onClearFilters">
        Clear filters
      </a>
    </div>
  </div>
</template>

<script>
import { TOGGLE_FILTER } from '@/store/action-types';
import { CLEAR_FILTERS } from '@/store/mutation-types';
import FilterCheckList from './FilterChecklist';

export default {
  name: 'search-grid-filter',
  props: ['isCollectionsPage'],
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
  },
  methods: {
    onUpdateFilter({ code, filterType }) {
      this.$store.dispatch(TOGGLE_FILTER, {
        code,
        filterType,
        isCollectionsPage: this.$props.isCollectionsPage,
        shouldNavigate: true,
      });
    },
    onUpdateSearchByCreator() {
      this.$store.dispatch(TOGGLE_FILTER, {
        filterType: 'searchBy',
        isCollectionsPage: this.$props.isCollectionsPage,
        shouldNavigate: true,
      });
    },
    onClearFilters() {
      this.$store.commit(CLEAR_FILTERS, {
        isCollectionsPage: this.$props.isCollectionsPage,
        shouldNavigate: true,
      });
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../styles/app';

.search-filters {
  background: #fafafa;
  display: none;
  padding: 10px ;
  height: 100%;

  label {
    font-size: 1em;
    color: #35495e;
    span {
      margin-bottom: 1.07142857em;
      font-size: .85em;
      letter-spacing: 1px;
      line-height: 1.25;
      display: inline-block;
      padding-top: .28571429em;
      border-top: 5px solid #373737;
      margin-top: -3px;
    }
  }

  &__visible {
    border-top: 1px solid #e8e8e8;
    display: block;
  }
}

.filter-option {
  margin-right: 1em;
  padding-bottom: 0.5em;
  padding-top: 0.5em;
}


.grid-x {
  /* Small only */
  @media screen and (max-width: 49em) {
    display: block;
  }
}

.search-filters_search-by,
.clear-filters {
  margin-top: 0.4em;
}

.search-filters_clear-btn {
  height: auto;
  border-radius: 2px;
  margin: auto;
}
</style>
