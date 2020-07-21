<template>
  <div class="about-page">
    <header-section showNavSearch="true"></header-section>
    <main role="main" class="margin-normal">
      <h2 role="article">About CC Search</h2>
      <p>
        CC Search is a tool that allows openly licensed and public domain works
        to be discovered and used by everyone. Creative Commons, the nonprofit
        behind CC Search, is the maker of the
        <a
          aria-label="cc licenses"
          href="https://creativecommons.org/share-your-work/licensing-examples/"
          >CC licenses</a
        >, used over 1.4 billion times to help creators share knowledge and
        creativity online.
      </p>
      <p>
        CC Search searches across more than 300 million images from open APIs
        and the
        <a aria-label="common crawl" href="http://commoncrawl.org/"
          >Common Crawl</a
        >
        dataset. It goes beyond simple search to aggregate results across
        multiple public repositories into a single catalog, and facilitates
        reuse through features like machine-generated tags and one-click
        attribution.
      </p>
      <p>
        Currently CC Search only searches images, but we plan to add additional
        media types such as open texts and audio, with the ultimate goal of
        providing access to all 1.4 billion CC licensed and public domain works
        on the web. Learn more about CC’s
        <a
          aria-label="cc search vision"
          href="https://creativecommons.org/2019/03/19/cc-search/"
          >2019 vision, strategy</a
        >
        and
        <a
          aria-label="cc search roadmap"
          href="https://docs.google.com/document/d/19yH2V5K4nzWgEXaZhkzD1egzrRayyDdxlzxZOTCm_pc/edit#heading=h.jih78emira0r"
          >roadmap</a
        >
        for CC Search and see what
        <a
          aria-label="current projects"
          href="https://github.com/orgs/creativecommons/projects/7"
          >we’re currently working on</a
        >. All of our code is open source (<a
          aria-label="cc search repository"
          href="https://github.com/creativecommons/cccatalog-frontend/"
          >CC Search</a
        >,
        <a
          aria-label="cc catalog-api repository"
          href="https://github.com/creativecommons/cccatalog-api/"
          >CC Catalog API</a
        >,
        <a
          aria-label="cc catalog repository"
          href="https://github.com/creativecommons/cccatalog/"
          >CC Catalog</a
        >) and we
        <a
          aria-label="contribution guidelines"
          href="https://creativecommons.github.io/contributing-code/"
          >welcome community contribution</a
        >.
      </p>
      <p>
        Please note that CC does not verify whether the images are properly CC
        licensed, or whether the attribution and other licensing information we
        have aggregated is accurate or complete. Please independently verify the
        licensing status and attribution information before reusing the content.
        For more details, read the
        <a
          aria-label="cc terms of use"
          href="https://creativecommons.org/terms/"
          >CC Terms of Use</a
        >.
      </p>
      <p>
        Looking for the old CC Search portal? Visit
        <a
          aria-label="old cc search"
          href="https://oldsearch.creativecommons.org"
          >https://oldsearch.creativecommons.org</a
        >.
      </p>
      <h3 class="margin-vertical-normal">Sources</h3>
      <table
        aria-label="sources table"
        role="region"
        class="table is-bordered is-striped"
      >
        <thead>
          <th>Source</th>
          <th>Domain</th>
          <th># CC Licensed Works</th>
        </thead>
        <tbody>
          <tr
            role="row"
            v-for="(imageProvider, index) in imageProviders"
            :key="index"
          >
            <td>{{ imageProvider.display_name }}</td>
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
    </main>
    <footer-section></footer-section>
  </div>
</template>

<script>
import HeaderSection from '@/components/HeaderSection'
import FooterSection from '@/components/FooterSection'
import ServerPrefetchProvidersMixin from '@/pages/mixins/ServerPrefetchProvidersMixin'

const AboutPage = {
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

export default AboutPage
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
@import '../styles/text-only-page.scss';
</style>
