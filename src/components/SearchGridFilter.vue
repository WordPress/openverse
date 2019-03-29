<template>
  <div :class="{ 'search-filters': true,
                 'search-filters__visible': isFilterVisible, }">
    <div class="grid-x">
      <div class="filter-option search-filters_providers">
        <multiselect
          v-model="filter.provider"
          @input="onUpdateFilter"
          tag-placeholder="Add this as new tag"
          placeholder="All Providers"
          label="name"
          track-by="code"
          :options="providers"
          :multiple="true"
          :taggable="true"
          :searchable="false">
        </multiselect>
      </div>
      <div class="filter-option search-filters_license-types">
        <multiselect
          v-model="filter.lt"
          @input="onUpdateFilter"
          :disabled="filter.li.length > 0"
          tag-placeholder="Add this as new tag"
          placeholder="All License Types"
          label="name"
          track-by="code"
          :options="licenseTypes"
          :multiple="true"
          :taggable="true"
          :searchable="false">
        </multiselect>
      </div>
      <div class="filter-option search-filters_licenses">
        <multiselect
          v-model="filter.li"
          @input="onUpdateFilter"
          :disabled="filter.lt.length > 0"
          tag-placeholder="Add this as new tag"
          placeholder="All Licenses"
          label="name"
          track-by="code"
          :options="licenses"
          :multiple="true"
          :taggable="true"
          :searchable="false">
        </multiselect>
      </div>
      <div class="filter-option search-filters_search-by">
        <input type="checkbox" id="creator-chk"
               v-model="filter.searchBy.creator"
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
  </div>
</template>

<script>
import { SET_QUERY } from '@/store/mutation-types';
import Multiselect from 'vue-multiselect';

const transformFilterValue = (filter, key) => {
  if (Array.isArray(filter[key])) {
    return filter[key].map(filterItem => filterItem.code).join(',');
  }
  else if (key === 'searchBy') {
    return filter.searchBy.creator ? 'creator' : null;
  }
  return null;
};

export default {
  name: 'search-grid-filter',
  components: {
    Multiselect,
  },
  mounted() {
    this.parseQueryFilters();
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
  },
  methods: {
    onUpdateFilter() {
      const filter = Object.assign({}, this.filter);
      Object.keys(this.filter).forEach((key) => {
        filter[key] = transformFilterValue(filter, key);
      });
      this.$store.commit(SET_QUERY, { query: filter, shouldNavigate: true });
    },
    onClearFilters() {
      const filter = Object.assign({}, this.filter);
      Object.keys(this.filter).forEach((key) => { filter[key] = []; });
      this.filter = filter;
      this.$store.commit(SET_QUERY, { query: filter, shouldNavigate: true });
    },
    parseQueryFilters() {
      const filterLookup = {
        provider: 'providers',
        li: 'licenses',
        lt: 'licenseTypes',
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
  data: () => (
    { providers:
      [
        { code: '500px', name: '500px' },
        { code: 'animaldiversity', name: 'Animal Diversity Web' },
        { code: 'behance', name: 'Behance' },
        { code: 'brooklynmuseum', name: 'Brooklyn Museum' },
        { code: 'clevelandmuseum', name: 'Cleveland Museum of Art' },
        { code: 'deviantart', name: 'DeviantArt' },
        { code: 'digitaltmuseum', name: 'Digitalt Museum' },
        { code: 'eol', name: 'Encyclopedia of Life' },
        { code: 'flickr', name: 'Flickr' },
        { code: 'floraon', name: 'Flora-On' },
        { code: 'geographorguk', name: 'Geograph® Britain and Ireland' },
        { code: 'iha', name: 'IHA Holiday Ads' },
        { code: 'mccordmuseum', name: 'Montreal Social History Museum' },
        { code: 'met', name: 'Metropolitan Museum of Art' },
        { code: 'museumsvictoria', name: 'Museums Victoria' },
        { code: 'nhl', name: 'London Natural History Museum' },
        { code: 'nypl', name: 'New York Public Library' },
        { code: 'rijksmuseum', name: 'Rijksmuseum NL' },
        { code: 'sciencemuseum', name: 'Science Museum – UK' },
        { code: 'thingiverse', name: 'Thingiverse' },
        { code: 'WoRMS', name: 'World Register of Marine Species' },
      ],
    licenses:
      [
        { code: 'cc0', name: 'CC0' },
        { code: 'pdm', name: 'Public Domain Mark' },
        { code: 'by', name: 'BY' },
        { code: 'by-sa', name: 'BY-SA' },
        { code: 'by-nc', name: 'BY-NC' },
        { code: 'by-nd', name: 'BY-ND' },
        { code: 'by-nc-sa', name: 'BY-NC-SA' },
        { code: 'by-nc-nd', name: 'BY-NC-ND' },
      ],
    licenseTypes:
      [
        { code: 'all-cc', name: 'CC-licensed works only (no PD)' },
        { code: 'all', name: 'All Public Domain (PD)' },
        { code: 'commercial', name: 'Commercial use permitted' },
        { code: 'modification', name: 'Modifications permitted' },
      ],
    filter: {
      provider: [],
      li: [],
      lt: [],
      searchBy: {
        creator: false,
      },
    } }),
};
</script>

<style lang="scss" scoped>
@import '../styles/app';

.search-filters {
  background: #fafafa;
  display: none;
  padding: 10px ;
  width: 100%;

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
  margin-right: 1vw;
  min-width: 17vw;
  padding-bottom: 0.5vh;
  padding-top: 0.5vh;
}

.grid-x {
  /* Small only */
  @media screen and (max-width: 39.9375em) {
    display: block;
  }
}

.search-filters_search-by,
.clear-filters {
  margin-top: 0.4em;
  min-width: 10vw;
}

.search-filters_clear-btn {
  height: auto;
  border-radius: 2px;
  margin: auto;
}
</style>
