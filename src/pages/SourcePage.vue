<template>
  <div class="about-page">
    <header-section showNavSearch="true"></header-section>
    <main role="main" class="margin-normal">
      <h1 class="title is-2" role="article">Sources</h1>
    </main>
    <footer-section></footer-section>
  </div>
</template>

<script>
import HeaderSection from '@/components/HeaderSection'
import FooterSection from '@/components/FooterSection'
import ServerPrefetchProvidersMixin from '@/pages/mixins/ServerPrefetchProvidersMixin'

const SourcePage = {
  name: 'about-page',
  mixins: [ServerPrefetchProvidersMixin],
  components: {
    HeaderSection,
    FooterSection,
  },
  computed: {
    imageProviders() {
      return this.$store.state.imageProviders
    },
  },
  methods: {
    getProviderImageCount(imageCount) {
      return imageCount.toLocaleString('en')
    },
  },
}

export default SourcePage
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
@import '../styles/text-only-page.scss';
</style>
