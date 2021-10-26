<!-- noresult is hardcoded since it does not yet support built-in audio search -->
<template>
  <div id="tab-audio" role="tabpanel" aria-labelledby="audio">
    <AudioResultsList v-if="supported" @onLoadMoreAudios="onLoadMoreAudios" />
    <MetaSearchForm type="audio" :noresult="false" :supported="supported" />
  </div>
</template>

<script>
export default {
  name: 'AudioSearch',
  data() {
    return {
      // Only show audio results if non-image results are supported
      supported: process.env.enableAudio,
    }
  },
  methods: {
    onLoadMoreAudios(searchParams) {
      if (!this.supported) return
      this.$emit('onLoadMoreItems', searchParams)
    },
  },
}
</script>
