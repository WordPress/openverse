<template>
  <div>
    <search-grid-manual-load
      :query="query"
      :searchTerm="query.q"
      @onLoadMoreImages="onLoadMoreImages"
    />
    <ScrollButton :showBtn="showScrollButton" />
  </div>
</template>

<script>
export default {
  name: 'search-grid',
  props: ['searchTerm'],
  data: () => ({
    showScrollButton: false,
  }),
  computed: {
    query() {
      return this.$store.state.query
    },
  },
  methods: {
    onLoadMoreImages(searchParams) {
      this.$emit('onLoadMoreImages', searchParams)
    },
    checkScrollLength() {
      if (window.scrollY > 70) this.showScrollButton = true
      else this.showScrollButton = false
    },
  },
  mounted() {
    document.addEventListener('scroll', this.checkScrollLength)
  },
  beforeDestroy() {
    document.removeEventListener('scroll', this.checkScrollLength)
  },
}
</script>
