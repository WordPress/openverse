<template>
  <SearchGrid id="tab-image" @onLoadMoreImages="onLoadMoreImages" />
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
