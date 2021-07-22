<template>
  <div class="section">
    <div :class="['container', isEmbedded ? '' : 'is-fluid']">
      <div>
        <h1 class="title is-2 margin-bottom-large">
          <span role="img" aria-label="construction sign">🚧</span> WIP
        </h1>
        <div class="content">
          <p>Work in progress...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import iframeHeight from '~/mixins/iframeHeight'

const AboutPage = {
  name: 'about-page',
  mixins: [iframeHeight],
  layout({ store }) {
    return store.state.isEmbedded
      ? 'embedded-with-nav-search'
      : 'with-nav-search'
  },
  computed: {
    ...mapState(['isEmbedded']),
  },
}

export default AboutPage
</script>

<style lang="scss" scoped>
@import '~/styles/text-only-page.scss';
</style>
