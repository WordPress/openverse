<template>
  <div class="about-page">
    <header-section showNavSearch="true"></header-section>
    <main role="main" class="margin-normal">
      <h1 class="title is-2" role="article">{{ $t('sources.title') }}</h1>
      <div class="container">
        <div class="left-half">
          <p class="body-big margin-vertical-large">
            {{ $t('sources.detail') }}
          </p>
          <table
            :aria-label="$t('about.aria.sources')"
            role="region"
            class="table is-bordered is-striped"
          >
            <thead>
              <th>{{ $t('sources.providers.source') }}</th>
              <th>{{ $t('sources.providers.item') }}</th>
            </thead>
            <tbody>
              <tr
                role="row"
                v-for="(imageProvider, index) in imageProviders"
                :key="index"
              >
                <td>
                  <a
                    :aria-label="imageProvider.display_name"
                    :href="imageProvider.source_url"
                  >
                    {{ imageProvider.source_url }}
                  </a>
                </td>
                <td class="number-cell">
                  {{ getProviderImageCount(imageProvider.image_count) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="right-half margin-left-large margin-vertical-large">
          <h3 class="b-header">{{ $t('sources.cc-content.where') }}</h3>
          <p class="body-big margin-vertical-normal">
            {{ $t('sources.cc-content.content') }}
          </p>
          <i18n
            path="sources.cc-content.provider"
            tag="p"
            class="body-big margin-vertical-normal"
          >
            <template v-slot:flikr>
              <a aria-label="flikr" href="#">Flikr</a>
            </template>
            <template v-slot:smithsonian>
              <a aria-label="smithsonian" href="#">Smithsonian Institute</a>
            </template>
          </i18n>
          <i18n
            path="sources.cc-content.europena"
            tag="p"
            class="body-big margin-vertical-normal"
          >
            <template v-slot:link>
              <a aria-label="europena" href="#">Europena</a>
            </template>
            <template v-slot:link-api>
              <a aria-label="europena-api" href="#">Europena API</a>
            </template>
          </i18n>
          <h3 class="b-header">{{ $t('sources.new-content.next') }}</h3>
          <p class="body-big margin-vertical-normal">
            {{ $t('sources.new-content.integrate') }}
          </p>
          <ul>
            <li>
              {{ $t('sources.new-content.impact') }}
            </li>
            <li>
              {{ $t('sources.new-content.reuse') }}
            </li>
            <li>
              {{ $t('sources.new-content.total-items') }}
            </li>
          </ul>
        </div>
      </div>
    </main>
    <footer-section></footer-section>
  </div>
</template>

<script>
import HeaderSection from '@/components/HeaderSection'
import FooterSection from '@/components/FooterSection'
import ServerPrefetchProvidersMixin from '@/pages/mixins/ServerPrefetchProvidersMixin'

const SourcePage = {
  name: 'source-page',
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
.container {
  display: flex;
}

.left-half {
  flex: 2;
}

.right-half {
  flex: 2;
}
</style>
