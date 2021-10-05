<template>
  <SearchGrid
    id="tab-all"
    role="tabpanel"
    aria-labelledby="all"
    @onLoadMoreImages="onLoadMoreImages"
  />
</template>

<script>
import { UPDATE_SEARCH_TYPE } from '~/constants/action-types'
import { ALL_MEDIA } from '~/constants/media'

export default {
  name: 'SearchIndex',
  async mounted() {
    await this.$store.dispatch(UPDATE_SEARCH_TYPE, { searchType: ALL_MEDIA })
  },
  methods: {
    onLoadMoreImages(searchParams) {
      this.$emit('onLoadMoreItems', searchParams)
    },
  },
}
</script>
