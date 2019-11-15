<template>
  <div :class="{ 'search-filters': true,
                 'search-filters__visible': isFilterVisible, }">
    <form class="filter-option" role="filter">
      <filter-check-list :options="filters.licenseTypes"
                         title="I want something that I can"
                         filterType="licenseTypes"
                         @filterChanged="onUpdateFilter" />
      <filter-check-list :options="filters.providers"
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
              v-model="filters.searchBy.creator"
              @change="onUpdateFilter">
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
import clonedeep from 'lodash.clonedeep';
import { TOGGLE_FILTER } from '@/store/action-types';
import FilterCheckList from './FilterChecklist';

const filterData = {
  licenseTypes: [
    { code: 'commercial', name: 'Use for commercial purposes' },
    { code: 'modification', name: 'Modify or adapt' },
  ],
  imageTypes: [
    { code: 'photo', name: 'Photographs' },
    { code: 'illustration', name: 'Illustrations' },
    { code: 'vector', name: 'Vector Graphics' },
  ],
  extensions: [
    { code: 'jpg', name: 'JPEGs' },
    { code: 'png', name: 'PNGs' },
  ],
  filter: {
    provider: [],
    lt: [],
    searchBy: {
      creator: false,
    },
  },
};

export default {
  name: 'search-grid-filter',
  props: ['showProvidersFilter'],
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
    query() {
      return this.$store.state.query;
    },
    filters() {
      return this.$store.state.filters;
    },
  },
  methods: {
    onUpdateFilter({ code, filterType }) {
      this.$store.dispatch(TOGGLE_FILTER, {
        code,
        filterType,
        shouldNavigate: true,
      });
    },
    onClearFilters() {
      this.filter = clonedeep(filterData.filter);
      const filter = {};
      Object.keys(this.filter).forEach((key) => {
        filter[key] = transformFilterValue(this.filter, key);
      });
      ['providers', 'licenseTypes', 'imageTypes', 'extensions']
        // eslint-disable-next-line no-param-reassign
        .forEach(key => this[key].forEach((value) => { value.checked = false; }));
      this.$emit('onSearchFilterChanged', { query: filter, shouldNavigate: true });
    },
    parseQueryFilters() {
      const filterLookup = {
        provider: 'providers',
        lt: 'licenseTypes',
        imageType: 'imageTypes',
        extension: 'extensions',
      };

      if (this.query) {
        Object.keys(filterLookup).forEach((key) => {
          if (this.query[key]) {
            const codes = this.query[key].split(',');
            if (codes.length) {
              codes.forEach((code) => {
                const filter = this[filterLookup[key]]
                  .find(filterItem => filterItem.code === code);
                if (filter) {
                  this.filter[key].push(filter);
                }
              });
            }
          }
        });
        if (this.query.searchBy) {
          // searchBy query string term can be "creator" for example
          const searchByKey = this.query.searchBy;
          this.filter.searchBy[searchByKey] = true;
        }
      }
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
