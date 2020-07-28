<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
import { FETCH_IMAGE_PROVIDERS } from '@/store/action-types'

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
    height: 100vh;
    position: sticky;
    top: 0;
  }
}
</style>
