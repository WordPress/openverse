<template>
  <div class="page">
    <header-section showNavSearch="true" />
    <main role="main" class="section margin-bottom-large">
      <div class="container is-fluid">
        <div class="margin-bottom-large">
          <h1 class="title is-2">
            {{ $t('meta-search-page.title') }}
          </h1>
        </div>
      </div>
    </main>
    <footer-section />
  </div>
</template>

<script>
import HeaderSection from '@/components/HeaderSection'
import FooterSection from '@/components/FooterSection'
import ServerPrefetchProvidersMixin from '@/pages/mixins/ServerPrefetchProvidersMixin'

const MetaSearchPage = {
  name: 'meta-search-page',
  mixins: [ServerPrefetchProvidersMixin],
  components: {
    HeaderSection,
    FooterSection,
  },
}

export default MetaSearchPage
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
@import '../styles/text-only-page.scss';

figure {
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  border: 1px solid black;
}

h4 {
  margin: 1rem 0;
}
</style>
