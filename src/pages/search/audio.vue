<template>
  <MetaSearchForm
    id="tab-audio"
    type="audio"
    role="tabpanel"
    aria-labelledby="audio"
  />
</template>

<script>
import { UPDATE_SEARCH_TYPE } from '~/store-modules/action-types'
import { AUDIO } from '~/constants/media'

export default {
  name: 'AudioSearch',
  async mounted() {
    await this.$store.dispatch(UPDATE_SEARCH_TYPE, { searchType: AUDIO })
  },
}
</script>
