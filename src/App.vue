<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
import { FETCH_IMAGE_PROVIDERS } from '@/store/action-types'
import loadScript from '@/utils/loadScript'

export default {
  name: 'App',

  methods: {
    fetchProviders() {
      return this.$store.dispatch(FETCH_IMAGE_PROVIDERS)
    },
  },
  beforeMount() {
    if (
      !this.$store.state.imageProviders ||
      !this.$store.state.imageProviders.length
    ) {
      this.fetchProviders()
    }
  },
  mounted() {
    const cdn = 'https://unpkg.com/@creativecommons/vocabulary/js/vocabulary.js'
    const header = document.querySelector('.cc-global-header')
    // Load voocabulary global header from the unpkg CDN and render the global header.
    // Make sure all of this only happens once.
    loadScript(cdn).then(() => {
      if (!header) window.vocabulary.createGlobalHeader()
    })
  },
  metaInfo() {
    return {
      meta: [
        {
          vmid: 'monetization',
          name: 'monetization',
          content: '$ilp.uphold.com/edR8erBDbRyq',
        },
      ],
    }
  },
}
</script>

<style lang="scss">
@import '@creativecommons/vocabulary/scss/vocabulary.scss';

body {
  margin: 0;
}

#app {
  font-family: 'Source Sans Pro', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #333333;
}

.full-height-sticky {
  @include desktop {
    z-index: 20;
    height: 100vh;
    position: sticky;
    top: 0;
  }
}

// override global header styles for now
.cc-global-header .container {
  max-width: 100%;
}
</style>
