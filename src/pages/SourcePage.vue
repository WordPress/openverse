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
            There is openly licensed content hosted on millions of domains
            across the breadth of the internet. Our team systematically
            identifies providers hosting CC-licensed content. If it’s a good
            fit, we index that content and make it discoverable through CC
            Search.
          </p>
          <p class="body-big margin-vertical-normal">
            Some providers have multiple different groupings of content within
            them. Flickr has sources ranging from NASA to personal photography.
            The Smithsonian Institution comprises a dozen, diverse collections.
            Wikimedia Commons runs the gamut in terms of content, and is used by
            several Galleries, Libraries, Archives, and Museums highlighting
            some or all of their digitized collections.
          </p>
          <p class="body-big margin-vertical-normal">
            CC Search is especially grateful for the work of Europeana, an
            organization that works to digitize and make discoverable cultural
            heritage works across Europe. CC Search is able to index hundreds of
            valuable sources, through a single integration with the Europeana
            API.
          </p>
          <h3 class="b-header">{{ $t('sources.new-content.next') }}</h3>
          <p class="body-big margin-vertical-normal">
            We have a never ending list of possible sources to research prior to
            integration. We ask ourselves questions like:
          </p>
          <ul>
            <li>
              What is the impact or importance of this source to our users? If
              it exists within a provider like Wikimedia Commons, is it valuable
              for our users to be able to filter by this source directly?
            </li>
            <li>
              Is licensing and attribution information clearly displayed to
              enable confident reuse?
            </li>
            <li>
              How many new total items or new types of items can we bring to our
              users through this integration? Some sources are direct
              integrations, while others may be a source within a source.
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
