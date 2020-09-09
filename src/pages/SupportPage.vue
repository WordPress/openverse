<template>
  <div class="page">
    <header-section showNavSearch="true" />
    <main role="main" class="section margin-bottom-large">
      <div class="container is-fluid">
        <div class="margin-bottom-large">
          <h1 class="title is-2">
            {{ $t('support.title') }}
          </h1>
          <p class="margin-bottom-normal">{{ $t('support.inclusive') }}</p>
          <i18n path="support.work" tag="p" class="margin-bottom-normal">
            <template v-slot:license>
              <a
                aria-label="licenses"
                href="https://creativecommons.org/licenses/"
                >CC License Suite</a
              >
            </template>
            <template v-slot:public-domain>
              <a
                aria-label="public domain"
                href="https://creativecommons.org/publicdomain/"
                >public domain tools</a
              >
            </template>
            <template v-slot:photograph>
              <a
                aria-label="photograph"
                href="https://www.parismuseescollections.paris.fr/fr/musee-carnavalet/oeuvres/portrait-de-l-ecrivaine-libertaire-et-feministe-caroline-remy-dite-severine"
                >this photograph</a
              >
            </template>
            <template v-slot:guide>
              <a
                aria-label="guide"
                href="https://pressbooks.library.ryerson.ca/docs/"
                >this guide</a
              >
            </template>
          </i18n>
          <h2 class="title subtitle is-3 margin-bottom-normal">
            {{ $t('support.free') }}
          </h2>
          <p class="margin-bottom-normal">{{ $t('support.access') }}</p>
          <i18n path="support.public-good" tag="p" class="margin-bottom-normal">
            <template v-slot:public-good>
              <strong>public good</strong>
            </template>
          </i18n>
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
