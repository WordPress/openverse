<template>
  <SearchGrid
    id="tab-image"
    role="tabpanel"
    aria-labelledby="image"
    @onLoadMoreImages="onLoadMoreImages"
  />
</template>

<script>
import { UPDATE_SEARCH_TYPE } from '~/constants/action-types'
import { IMAGE } from '~/constants/media'

export default {
  name: 'ImageSearch',
  async mounted() {
    await this.$store.dispatch(UPDATE_SEARCH_TYPE, { searchType: IMAGE })
  },
  methods: {
    onLoadMoreImages(searchParams) {
      this.$emit('onLoadMoreItems', searchParams)
    },
  },
}
</script>
