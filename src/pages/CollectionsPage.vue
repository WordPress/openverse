<template>
  <div>
    <header-section></header-section>
    <main role="main" class="collections-page padding-larger">
      <h1>{{$t('collections.title')}}</h1>
      <h2 role="region" class="margin-bottom-normal">{{$t('collections.museum')}}</h2>
      <div class="providers-list columns is-multiline">
        <collection-item
          v-for="(provider, index) in museumProviders"
          :key="index"
          :provider="provider"
        />
      </div>
      <hr />
      <h2 role="region" class="margin-bottom-normal">{{$t('collections.other')}}</h2>
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
