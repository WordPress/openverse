<template>
  <SearchGrid
    id="tab-all"
    role="tabpanel"
    aria-labelledby="all"
    @onLoadMoreImages="onLoadMoreImages"
  />
</template>

<script>
export default {
  name: 'SearchIndex',
  methods: {
    onLoadMoreImages(searchParams) {
      this.$emit('onLoadMoreItems', searchParams)
    },
  },
}
</script>
