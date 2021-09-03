<template>
  <div id="tab-audio" role="tabpanel" aria-labelledby="audio">
    <AudioResultsList />
    <MetaSearchForm type="audio" :query="query" :supported="true" />
  </div>
</template>

<script>
import { UPDATE_SEARCH_TYPE } from '~/store-modules/action-types'
import { AUDIO } from '~/constants/media'

export default {
  name: 'AudioSearch',
  computed: {
    query() {
      return this.$store.state.query
    },
  },
  async mounted() {
    await this.$store.dispatch(UPDATE_SEARCH_TYPE, { searchType: AUDIO })
  },
}
</script>
