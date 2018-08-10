<template>
  <div :class="{ 'search-filter': true,
                 'search-filter__visible': isVisible,
                 'grid-container full': true, }">
    <div class="grid-x grid-margin-x grid-padding-x">
      <div class="search-filter_providers
                  cell
                  medium-4
                  large-2
                  large-offset-3">
        <label><span>Providers</span></label>
        <select v-model="filter.provider" v-on:change="onUpdateFilter">
          <option v-for="(provider, index) in providers"
                  :key="index"
                  @click.prevent="onSelectProvider(provider)">
            {{ provider }}
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
                  :key="index">
            {{ license }}
          </option>
        </select>
      </div>
      <div class="search-filter_licenseType
                  search-filter_license
                  cell
                  medium-4
                  large-2">
        <label><span>License Types</span></label>
        <select v-model="filter.lt"
                v-on:change="onUpdateFilter"
                :disabled="filter.li !== ''">
          <option v-for="(licenseType, index) in licenseTypes"
                  :key="index"
                  @change="onSelectProvider(licenseType)">
            {{ licenseType }}
          </option>
        </select>
      </div>
    </div>
  </div>
</transition>
</template>

<script>
import { SET_GRID_FILTER } from '@/store/mutation-types';

export default {
  name: 'search-grid-filter',
  props: {
    isVisible: false,
  },
  methods: {
    onUpdateFilter() {
      const filter = this.filter;


      this.$store.commit( SET_GRID_FILTER , { filter })
    },
  },
  data: () => (
    { providers:
      [
        '',
        'rijksmuseum',
        'nypl',
        'museumvictoria',
        'met',
        'geographorguk',
        'flickr',
        'europeana',
        'deviantart',
        'behance',
        '500px',
      ],
    licenses:
      [
        '',
        'by-nc',
        'by-sa',
        'by-nc-nd',
        'pdm', 'by-nd',
        'by',
        'cc0',
        'by-nc-sa'
      ],
    licenseTypes:
      [
        '',
        'all',
        'all-cc',
        'commercial',
        'modification',
      ],
    filter: {
      provider: '',
      li: '',
      lt: '',
    },
  }),
};
</script>

<style lang="scss" scoped>
.search-filter {
  padding: 20px 0 5px 0;
  margin-top: -100%;
  transition: margin .7s ease-in-out;

  select: {
    margin: 0;
  }

  button {
    height: 100%;
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
</style>
