<template>
  <div>
    <header-section></header-section>
    <main role="main" class="collections-page padding-larger">
      <h1>{{ $t('collections.title') }}</h1>
      <h2 role="region" class="margin-bottom-normal">
        {{ $t('collections.museum') }}
      </h2>
      <div class="providers-list columns is-multiline">
        <collection-item
          v-for="(provider, index) in museumProviders"
          :key="index"
          :provider="provider"
        />
      </div>
      <hr />
      <h2 role="region" class="margin-bottom-normal">
        {{ $t('collections.other') }}
      </h2>
      <div class="providers-list columns is-multiline">
        <collection-item
          v-for="(provider, index) in otherProviders"
          :key="index"
          :provider="provider"
        />
      </div>
    </main>
    <footer-section></footer-section>
  </div>
</template>

<script>
import CollectionItem from '@/components/CollectionItem'
import HeaderSection from '@/components/HeaderSection'
import FooterSection from '@/components/FooterSection'
import ServerPrefetchProvidersMixin from '@/pages/mixins/ServerPrefetchProvidersMixin'

const MUSEUM_PROVIDERS = [
  'brooklynmuseum',
  'clevelandmuseum',
  'digitaltmuseum',
  'europeana',
  'mccordmuseum',
  'met',
  'museumsvictoria',
  'nhl',
  'rijksmuseum',
  'sciencemuseum',
  'smithsonian',
  'smithsonian_national_museum_of_natural_history',
  'smithsonian_anacostia_museum',
  'smithsonian_cooper_hewitt_museum',
  'smithsonian_field_book_project',
  'smithsonian_freer_gallery_of_art',
  'smithsonian_gardens',
  'smithsonian_hirshhorn_museum',
  'smithsonian_anthropological_archives',
  'smithsonian_air_and_space_museum',
  'smithsonian_african_american_history_museum',
  'smithsonian_american_history_museum',
  'smithsonian_american_indian_museum',
  'smithsonian_african_art_museum',
  'smithsonian_portrait_gallery',
  'smithsonian_postal_museum',
  'smithsonian_zoo_and_conservation',
  'smithsonian_american_art_museum',
  'smithsonian_institution_archives',
  'smithsonian_libraries',
  'statensmuseum',
  'thorvaldsensmuseum',
]

const CollectionsPage = {
  name: 'collections-page',
  mixins: [ServerPrefetchProvidersMixin],
  components: {
    HeaderSection,
    FooterSection,
    CollectionItem,
  },
  computed: {
    museumProviders() {
      if (this.providers) {
        return this.providers.filter(
          (provider) => MUSEUM_PROVIDERS.indexOf(provider.source_name) >= 0
        )
      }
      return []
    },
    otherProviders() {
      if (this.providers) {
        return this.providers.filter(
          (provider) => MUSEUM_PROVIDERS.indexOf(provider.source_name) === -1
        )
      }
      return []
    },
    providers() {
      return this.$store.state.imageProviders
    },
  },
}

export default CollectionsPage
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
h1 {
  margin-bottom: 0.44117647em;
  letter-spacing: initial;
  line-height: 1.25;
  text-transform: initial;
}

.collections-page {
  background-color: #f5f5f5;
}
</style>
