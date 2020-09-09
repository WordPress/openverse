<template>
  <div>
    <search-grid-manual-load
      :query="query"
      :search-term="query.q"
      @onLoadMoreImages="onLoadMoreImages"
    />
    <ScrollButton :show-btn="showScrollButton" />
  </div>
</template>

<script>
export default {
  name: 'SearchGrid',
  props: ['searchTerm'],
  data: () => ({
    showScrollButton: false,
  }),
  computed: {
    query() {
      return this.$store.state.query
    },
  },
  mounted() {
    document.addEventListener('scroll', this.checkScrollLength)
  },
  beforeDestroy() {
    document.removeEventListener('scroll', this.checkScrollLength)
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
}
</script>
