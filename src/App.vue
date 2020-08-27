<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
import { FETCH_IMAGE_PROVIDERS } from '../store/action-types'

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
    if (typeof document !== 'undefined') {
      const el = document.createElement('script')
      el.src = 'https://unpkg.com/@creativecommons/vocabulary/js/vocabulary.js'
      el.defer = true
      el.addEventListener('load', () => {
        if (!document.querySelector('.cc-global-header')) {
          window.vocabulary.createGlobalHeader()
        }
      })
      document.head.appendChild(el)
    }
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
