<template>
  <SearchGrid
    id="tab-image"
    role="tabpanel"
    aria-labelledby="image"
    @onLoadMoreImages="onLoadMoreImages"
  />
</template>

<script>
export default {
  name: 'ImageSearch',
  methods: {
    onLoadMoreImages(searchParams) {
      this.$emit('onLoadMoreItems', searchParams)
    },
  },
}
</script>
