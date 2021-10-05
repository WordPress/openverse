<template>
  <div>
    <SearchGridManualLoad
      :query="query"
      :search-term="query.q"
      data-testid="search-grid"
      @onLoadMoreImages="onLoadMoreImages"
    />
    <ScrollButton data-testid="scroll-button" :show-btn="showScrollButton" />
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
      this.showScrollButton = window.scrollY > 70
    },
  },
}
</script>
