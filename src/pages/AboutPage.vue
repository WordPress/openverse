<template>
<div class="about-page grid-container full">
  <header-section showNavSearch="true"></header-section>
  <div class="about-page_body">
    <h1>About CC Search</h1>
      <p class="about-page_lead-paragraph">
        CC Search is a tool that allows openly licensed and public domain works to be discovered
        and used by everyone. Creative Commons, the nonprofit behind CC Search, is the maker of the
        <a href="https://creativecommons.org/share-your-work/licensing-types-examples/">CC licenses</a>,
        used over 1.4 billion times to help creators share knowledge and creativity online.
      </p>
      <p>
        CC Search searches across more than 300 million images from open APIs and the
        <a href="http://commoncrawl.org/">Common Crawl</a> dataset.
        It goes beyond simple search to aggregate results across multiple public repositories
         into a single catalog, and facilitates reuse through features like machine-generated tags
         and one-click attribution.
      </p>
      <p>
        Currently CC Search only searches images, but we plan to add additional media types such as
        open texts and audio, with the ultimate goal of providing access to all 1.4 billion CC
        licensed and public domain works on the web. Learn more about CC’s 2019 vision, strategy
        and roadmap for CC Search <a href="https://creativecommons.org/2019/03/19/cc-search/">here</a> and
        see what we’re currently working on <a href="https://github.com/orgs/creativecommons/projects/7">here</a>.
        All of our code is open source
        (<a href="https://github.com/creativecommons/cccatalog-frontend/">CC Search</a>,
        <a href="https://github.com/creativecommons/cccatalog-api/">CC Catalog API</a>,
        <a href="https://github.com/creativecommons/cccatalog/">CC Catalog</a>)
        and we <a href="https://creativecommons.github.io/contributing-code/">welcome community contribution</a>.
      </p>
      <p>
        Please note that CC does not verify whether the images are properly CC licensed, or whether
        the attribution and other licensing information we have aggregated is accurate or complete.
        Please independently verify the licensing status and attribution information before reusing
        the content. For more details, read the <a href="https://creativecommons.org/terms/">CC Terms of Use</a>.
      </p>
      <p>
        Looking for the old CC Search portal? Visit
        <a href="https://oldsearch.creativecommons.org">https://oldsearch.creativecommons.org</a>.
      </p>
      <h2>Providers</h2>
      <div class="about-page_provider-stats-ctr">
        <table class="about-page_provider-stats-table">
          <thead>
            <th>Provider</th>
            <th>Domain</th>
            <th># CC Licensed Works</th>
          </thead>
          <tbody>
            <tr v-for="(imageProvider, index) in imageProviders"
                :key="index">
              <td>{{ imageProvider.display_name }}</td>
              <td>
                <a :href="imageProvider.provider_url">
                  {{ imageProvider.provider_url }}
                </a>
              </td>
              <td>{{ getProviderImageCount(imageProvider.image_count) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
  </div>
  <footer-section></footer-section>
</div>
</template>

<script>
import HeaderSection from '@/components/HeaderSection';
import FooterSection from '@/components/FooterSection';

const AboutPage = {
  name: 'about-page',
  components: {
    HeaderSection,
    FooterSection,
  },
  computed: {
    imageProviders() {
      return this.$store.state.imageProviders;
    },
  },
  methods: {
    getProviderImageCount(imageCount) {
      return (imageCount).toLocaleString('en');
    },
  },
};

export default AboutPage;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  h1 {
    margin-bottom: .44117647em;
    font-size: 2.125em;
    font-weight: normal;
    letter-spacing: initial;
    line-height: 1.25;
    text-transform: initial;
  }

  h2 {
    margin-bottom: .57692308em;
    font-size: 1.5em;
    font-weight: normal;
    letter-spacing: initial;
    line-height: 1.25;
    text-transform: initial;
  }

  .about-page {
    background: #e9ebee;
  }

  .about-page_body {
    font-size: 1em;
    margin: 45px !important;
  }

  .about-page_lead-paragraph {
    margin-bottom: 1em;
  }

  .photo_tag-provider-badge {
    height: 24px;
  }

  /* Small only */
  @media screen and (max-width: 39.9375em) {
    .about-page_body {
      margin: 30px 15px 15px 15px !important;
    }
  }
</style>
