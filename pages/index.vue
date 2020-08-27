<template>
  <hero-section />
</template>

<script>
import { CLEAR_FILTERS } from '../src/store/mutation-types'

const HomePage = {
  name: 'home-page',
  fetch() {
    this.$store.commit(CLEAR_FILTERS, {
      provider: null,
      shouldNavigate: false,
    })
  },
  fetchOnServer: false,
}

export default HomePage
</script>
