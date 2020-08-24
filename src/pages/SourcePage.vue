<template>
  <div class="about-page">
    <header-section showNavSearch="true" />
    <main role="main" class="section">
      <div class="container is-fluid columns">
        <header class="column is-full margin-bottom-small">
          <h1 class="title is-2" role="article">{{ $t('sources.title') }}</h1>
        </header>
      </div>
      <div class="container is-fluid columns is-variable is-4">
        <div class="column">
          <i18n path="sources.detail" tag="p" class="body-big">
            <template v-slot:single-name>
              <strong>
                {{ $t('sources.single-name') }}
              </strong>
            </template>
          </i18n>
          <table
            :aria-label="$t('about.aria.sources')"
            role="region"
            class="table is-bordered is-striped margin-bottom-large margin-top-normal"
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
                    :href="`/search?source=${imageProvider.source_name}`"
                  >
                    {{ imageProvider.display_name }}
                  </a>
                </td>
                <td class="number-cell">
                  {{ getProviderImageCount(imageProvider.image_count) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="column">
          <h3 class="b-header">{{ $t('sources.cc-content.where') }}</h3>
          <p class="body-big margin-vertical-normal">
            {{ $t('sources.cc-content.content') }}
          </p>
          <i18n
            path="sources.cc-content.provider"
            tag="p"
            class="body-big margin-vertical-normal"
          >
            <template v-slot:flickr>
              <a aria-label="flickr" href="https://www.flickr.com/">Flickr</a>
            </template>
            <template v-slot:smithsonian>
              <a aria-label="smithsonian" href="https://naturalhistory.si.edu/"
                >Smithsonian Institute</a
              >
            </template>
          </i18n>
          <i18n
            path="sources.cc-content.europeana"
            tag="p"
            class="body-big margin-vertical-normal"
          >
            <template v-slot:link>
              <a aria-label="europeana" href="https://www.europeana.eu/en"
                >Europeana</a
              >
            </template>
            <template v-slot:link-api>
              <a
                aria-label="europeana-api"
                href="https://pro.europeana.eu/page/apis"
                >Europeana API</a
              >
            </template>
          </i18n>
          <h3 class="b-header">{{ $t('sources.new-content.next') }}</h3>
          <p class="body-big margin-vertical-normal">
            {{ $t('sources.new-content.integrate') }}
          </p>
          <div class="content">
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
          <h5 class="b-header margin-vertical-normal">
            {{ $t('sources.suggestions') }}
          </h5>
          <a
            href="https://github.com/creativecommons/cccatalog/issues/new?assignees=&labels=awaiting+triage%2C+ticket+work+required%2C+providers&template=new-source-suggestion.md&title=%5BSource+Suggestion%5D+Insert+source+name+here"
            class="button is-primary is-uppercase"
          >
            {{ $t('sources.issue-button') }}
            <i class="margin-left-small icon external-link" />
          </a>
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

.table.is-bordered {
  td,
  th {
  }
}
</style>
