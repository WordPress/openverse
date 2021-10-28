<template>
  <SearchGridManualLoad
    :query="query"
    :search-term="query.q"
    data-testid="search-grid"
    @onLoadMoreImages="onLoadMoreImages"
  />
</template>

<script>
export default {
  name: 'SearchGrid',
  props: ['searchTerm'],
  computed: {
    query() {
      return this.$store.state.query
    },
  },
  methods: {
    onLoadMoreImages(searchParams) {
      this.$emit('onLoadMoreImages', searchParams)
    },
  },
}
</script>
