<template>
  <div :class="{ 'search-filter cell small-12 medium-12 large-12': true,
                 'search-filter__visible': isFilterVisible, }">
    <router-view :key="$route.fullPath"></router-view>
    <div class="grid-x grid-margin-x grid-margin-y">
      <div class="search-filter_providers
                  cell
                  small-12
                  large-12">
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
      <div class="search-filter_licenses
                  cell
                  large-12">
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
      <div class="search-filter_license-types
                  cell
                  large-12">
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
      <div class="cell
                  large-12">
        <a class="button primary medium search-filter_clear-btn"
                :disabled="isFilterApplied===false"
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
        filter[key] = filter[key].map(filterItem => filterItem.code).join(',');
      });
      this.$store.commit(SET_QUERY, { query: filter, shouldNavigate: true });
    },
    onClearFilters() {
      const filter = Object.assign({}, this.filter);
      Object.keys(this.filter).forEach((key) => { this.filter[key] = []; });
      this.$store.commit(SET_QUERY, { query: filter, shouldNavigate: true });
    },
    parseQueryFilters() {
      const filterLookup = {
        provider: 'providers',
        li: 'licenses',
        lt: 'licenseTypes',
      };

      if (this.query) {
        Object.keys(this.query).forEach((key) => {
          if (this[filterLookup[key]]) {
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
        { code: 'nhl', name: 'TODO' },
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
    } }),
};
</script>

<style lang="scss" scoped>
@import '../styles/app';

.search-filter {
  background: #fff;
  border: 1px solid #e8e8e8;
  visibility: hidden;
  left: 0;
  padding: 10px ;
  position: absolute;
  right: 0;
  transition: all .15s ease-in-out;
  width: 300px;
  opacity: 0;
  transform: translate3d(0px, -20px, 0px);

  label {
    border-top: 1px solid #d6d6d6;
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
    margin-top: 0;
    visibility: visible;
    opacity: 1;
    transform: translate3d(0px, 0px, 0px);
  }
}

.search-filter_clear-btn {
  height: auto;
  border-radius: 2px;
  margin: auto;
}

.multiselect__tags {
  border-radius: 0 !important
}
</style>
