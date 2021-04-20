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
  methods: {
    onLoadMoreImages(searchParams) {
      this.$emit('onLoadMoreImages', searchParams)
    },
  },
}
</script>
