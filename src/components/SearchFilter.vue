<template>
  <div class="search-filter"></div>
</template>

<script>

export default {
  name: 'search-filter',
    data: () => (
      { providers: [
        [ 'rijksmuseum',
          'nypl',
          'museumvictoria',
          'met',
          'geographorguk',
          'flickr',
          'europeana',
          'deviantart',
          'behance',
          '500px',
        ]
      ] } ),
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
