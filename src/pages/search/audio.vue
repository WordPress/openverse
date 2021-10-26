<!-- noresult is hardcoded since it does not yet support built-in audio search -->
<template>
  <div id="tab-audio" role="tabpanel" aria-labelledby="audio">
    <AudioResultsList
      v-if="supported"
      :query="query"
      @onLoadMoreAudios="onLoadMoreAudios"
    />
    <MetaSearchForm type="audio" :noresult="false" :supported="supported" />
  </div>
</template>

<script>
import { UPDATE_SEARCH_TYPE } from '~/constants/action-types'
import { AUDIO } from '~/constants/media'

export default {
  name: 'AudioSearch',
  data() {
    return {
      // Only show audio results if non-image results are supported
      supported: process.env.enableAudio,
    }
  },
  computed: {
    query() {
      return this.$store.state.query
    },
  },
  async mounted() {
    await this.$store.dispatch(UPDATE_SEARCH_TYPE, { searchType: AUDIO })
  },
  methods: {
    onLoadMoreAudios(searchParams) {
      if (!this.supported) return
      this.$emit('onLoadMoreItems', searchParams)
    },
  },
}
</script>
