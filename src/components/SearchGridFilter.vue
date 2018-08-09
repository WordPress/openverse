<template>
  <div class="search-filter" v-if="isVisible">
    <div class="x-grid">
      <div class="search-filter_providers cell large-4">

      </div>
      <div class="search-filter_license large-4">

      </div>
      <div class="search-filter_licenseType large-4">

      </div>
    </div>
  </div>
</template>

<script>

export default {
  name: 'search-grid-filter',
  props: {
    isVisible: false,
  },
  data: () => (
    { providers:
      [[
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
      ]],
    license:
      [[
        'BY-NC',
        'BY-SA',
        'BY-NC-ND',
        'PDM', 'BY-ND',
        'BY',
        'CC0',
        'BY-NC-SA'
      ]],
    licenseType:
      [[
        'all',
        'all-cc',
        'commercial',
        'modification',
      ]],
  }),
};
</script>

<style lang="scss" scoped>
.search-filter {
  height: 100;

  button {
    height: 100%;
    margin: 0;
  }

  &__visible {
    height: 70px;
  }
}
</style>

