<template>
<div class="about-page grid-container full">
  <header-section showNavSearch="true"></header-section>
  <div class="about-page_body">
    <h1>About CC Search</h1>
      <p class="about-page_lead-paragraph">
        There is no larger compendium of shared human knowledge and creativity than the
        Commons, including over 1.1 billion digital works available under CC licenses.
        Despite the tremendous growth of the Commons, and the widespread use of the CC
        licenses and public domain marks, there is no simple way to maximize use of, and
        engagement with, all of that content. There is no front door — no tool designed for
        the general public to facilitate discovery for the purpose of reuse and remix, to simplify
        the license terms, make attribution easy, or support curation, and crowdsourced metadata.
      </p>
      <p>
        Creative Commons’ “CC Search” project will develop and release an open online search and
        re-use tool that will allow high-quality content from the commons to surface in a more
        seamless and accessible way. Our first prototype relies on open APIs and focuses on
        photos as its first media type. It is meant to elicit discussion and inform our
        development as we build out the full set of tools. “CC Search” will enable users to
        curate, tag, and remix that content. It will go beyond simple search to aggregate results
        from across the hundreds of public repositories into a single ledger, and also facilitate
        the use and re-use through tools like curated lists, saved searches, one- or no-click
        attribution, and provenance.
      </p>
    <hr>
    <h3>Full list of providers:</h3>
    <table>
      <tbody>
        <tr>
          <td><b>Provider</b></td>
          <td><b>Domain</b></td>
          <td><b># CC Licensed Works</b></td>
        </tr>
        <tr>
          <td><b>Animal Diversity Web</b></td>
          <td><a href="https://animaldiversity.org/">
            <span>https://animaldiversity.org/</span></a>
          </td>
          <td><span>14,839</span></td>
        </tr>
        <tr>
          <td><b>Behance</b></td>
          <td><a href="https://www.behance.net/">
            <span>https://www.behance.net/</span></a>
          </td>
          <td><span>5,245,785</span></td>
        </tr>
        <tr>
          <td><b>Deviantart</b></td>
          <td>
            <a href="https://www.deviantart.com/">
            <span>https://www.deviantart.com/</span></a>
          </td>
          <td><span>206,506</span></td>
        </tr>
        <tr>
          <td><b>Digitalt Museum</b></td>
          <td>
            <a href="https://digitaltmuseum.org/">
            <span>https://digitaltmuseum.org/</span></a>
          </td>
          <td><span>88,970</span></td>
        </tr>
        <tr>
          <td><b>Encyclopedia of Life</b></td>
          <td>
            <a href="http://eol.org/">
              <span>http://eol.org/</span>
            </a>
          </td>
          <td><span>547,488</span></td>
        </tr>
        <tr>
          <td><b>Flickr</b></td>
          <td>
            <a href="https://www.flickr.com/">
              <span>https://www.flickr.com/</span>
            </a>
          </td>
          <td><span>426,214</span></td>
        </tr>
        <tr>
          <td><b>Flora-On</b></td>
          <td>
            <a href="http://flora-on.pt/">
              <span>http://flora-on.pt/</span>
            </a>
          </td>
          <td><span>26,498</span></td>
        </tr>
        <tr>
          <td><b>Geograph UK</b></td>
          <td>
            <a href="http://www.geograph.org.uk/">
              <span>http://www.geograph.org.uk/</span>
            </a>
          </td>
          <td><span>1,018,560</span></td>
        </tr>
        <tr>
          <td><b>IHA Holiday Ads</b></td>
          <td>
            <a href="http://www.iha.com/">
              <span>http://www.iha.com/</span>
            </a>
          </td>
          <td><span>2,058,272</span></td>
        </tr>
        <tr>
          <td><b>McCord Museum</b></td>
          <td>
            <a href="http://www.musee-mccord.qc.ca/en/">
              <span>http://www.musee-mccord.qc.ca/en/</span>
            </a>
          </td>
          <td><span>108,800</span></td>
        </tr>
        <tr>
          <td><b>The Metropolitan Museum of Art</b></td>
          <td>
            <a href="https://www.metmuseum.org/">
              <span>https://www.metmuseum.org/</span>
            </a>
          </td>
          <td><span>96,260</span></td>
        </tr>
        <tr>
          <td><b>Museums Victoria</b></td>
          <td>
            <a href="https://collections.museumvictoria.com.au/">
              <span>https://collections.museumvictoria.com.au/</span>
            </a>
          </td>
          <td><span>64,719</span></td>
        </tr>
        <tr>
          <td><b>Science Museum – UK</b></td>
          <td>
            <a href="https://www.sciencemuseum.org.uk/">
              <span>https://www.sciencemuseum.org.uk/</span>
            </a>
          </td>
          <td><span>14,280</span></td>
        </tr>
      </tbody>
    </table>
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

  h3 {
    margin-bottom: .83333333em;
    font-size: 1.125em;
    font-weight: 500;
    letter-spacing: initial;
    line-height: 1.25;
    text-transform: initial;
  }

  hr {
    margin: 2.5rem auto
  }
  .about-page_body {
    margin: 45px !important;
  }

  .about-page_lead-paragraph {
    margin-bottom: .68181818em;
    font-size: 1.25em;
    font-weight: normal;
    letter-spacing: initial;
    line-height: 1.25;
    text-transform: initial;
    margin-top: 1.36363636em;
    margin-bottom: .83333333em;
  }

  /* Small only */
  @media screen and (max-width: 39.9375em) {
    .about-page_body {
      margin: 15px !important;
    }
  }
</style>
