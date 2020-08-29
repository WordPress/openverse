<template>
  <SearchGrid @onLoadMoreImages="onLoadMoreImages" />
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
