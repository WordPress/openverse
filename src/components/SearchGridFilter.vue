<template>
  <div :class="{ 'search-filter': true,
                 'search-filter__visible': isVisible, }">
    <div class="grid-x grid-margin-x grid-padding-x">
      <div class="search-filter_providers
                  cell
                  medium-4
                  large-2
                  large-offset-3">
        <label><span>Collection</span></label>
        <select v-model="filter.provider" v-on:change="onUpdateFilter">
          <option v-for="(provider, index) in providers"
                  :key="index"
                  :value="provider.value">
            {{ provider.text }}
          </option>
        </select>
      </div>
      <div class="search-filter_license
                  cell
                  medium-4
                  large-2">
        <label><span>Licenses</span></label>
        <select v-model="filter.li"
                v-on:change="onUpdateFilter"
                :disabled="filter.lt !== ''">
          <option v-for="(license, index) in licenses"
                  :key="index"
                  :value="license.value">
            {{ license.text }}
          </option>
        </select>
      </div>
      <div class="search-filter_licenseType
                  cell
                  medium-4
                  large-2">
        <label><span>License Types</span></label>
        <select v-model="filter.lt"
                v-on:change="onUpdateFilter"
                :disabled="filter.li !== ''">
          <option v-for="(licenseType, index) in licenseTypes"
                  :key="index"
                  :value="licenseType.value">
            {{ licenseType.text }}
          </option>
        </select>
      </div>
       <div class="search-filter_licenseType
                  cell
                  medium-4
                  large-2">
          <a class="button hollow search-filter_clear-btn"
                  :disabled="hasFilter===false"
                  @click="onClearFilters">clear filters</a>
      </div>
    </div>
  </div>
</template>

<script>
import { SET_GRID_FILTER } from '@/store/mutation-types';

export default {
  name: 'search-grid-filter',
  props: {
    isVisible: false,
  },
  computed: {
    hasFilter() {
      return Object.keys(this.filter).some(key => this.filter[key]);
    },
  },
  methods: {
    onUpdateFilter() {
      const filter = this.filter;

      this.$store.commit(SET_GRID_FILTER, { filter });
    },
    onClearFilters() {
      if (this.hasFilter) {
        Object.keys(this.filter).forEach((key) => { this.filter[key] = ''; });
        this.onUpdateFilter();
      }
    },
  },
  data: () => (
    { providers:
      [
        { value: '', text: '' },
        { value: 'rijksmuseum', text: 'Rijksmuseum NL' },
        { value: 'nypl', text: 'New York Public Library' },
        { value: 'museumsvictoria', text: 'Museums Victoria' },
        { value: 'met', text: 'Metropolitan Museum of Art' },
        { value: 'geographorguk', text: 'Geograph® Britain and Ireland' },
        { value: 'flickr', text: 'Flickr' },
        { value: 'europeana', text: 'Europena collections' },
        { value: 'deviantart', text: 'DeviantArt' },
        { value: 'behance', text: 'Behance' },
        { value: '500px', text: '500px' },
      ],
    licenses:
      [
        { value: '', text: '' },
        { value: 'by-nc', text: 'BY-NC' },
        { value: 'by-sa', text: 'BY-SA' },
        { value: 'by-nc-nd', text: 'BY-NC-ND' },
        { value: 'pdm', text: 'PD' },
        { value: 'by', text: 'BY' },
        { value: 'cc0', text: 'CC0' },
        { value: 'by-nc-sa', text: 'BY-NC-SA' },
      ],
    licenseTypes:
      [
        { value: '', text: '' },
        { value: 'all', text: 'All' },
        { value: 'all-cc', text: 'CC-licensed works only (no PD)' },
        { value: 'commercial', text: 'Commercial use permitted' },
        { value: 'modification', text: 'Modification' },
      ],
    filter: {
      provider: '',
      li: '',
      lt: '',
    } }),
};
</script>

<style lang="scss" scoped>
@import '../styles/app';

.search-filter {
  @include xy-grid-container(100%, 0);
  padding: 20px 0 5px 0;
  margin: -100% auto 0 auto;
  max-width: 100%;
  transition: margin .7s ease-in-out;

  select: {
    margin: 0;
  }

  &__visible {
    border-top: 1px solid #d6d6d6;
    margin-top: 0;
  }

  label {
    border-top: 1px solid #d6d6d6;

    span {
      margin-bottom: 1.07142857em;
      font-size: .85em;
      letter-spacing: 1px;
      line-height: 1.25;
      display: inline-block;
      padding-top: .28571429em;
      border-top: 5px solid #4DA5EF;
      margin-top: -3px;
    }
  }
}

.search-filter_clear-btn {
  height: auto;
}
</style>
