<template>
  <SearchGridManualLoad
    :query="query"
    :search-term="query.q"
    data-testid="search-grid"
    @onLoadMoreImages="onLoadMoreImages"
  />
</template>

<script>
import { mapState } from 'vuex'
import { SEARCH } from '~/constants/store-modules'

export default {
  name: 'SearchGrid',
  props: ['searchTerm'],
  computed: {
    ...mapState(SEARCH, ['query']),
  },
  methods: {
    onLoadMoreImages(searchParams) {
      this.$emit('onLoadMoreImages', searchParams)
    },
  },
}
</script>
