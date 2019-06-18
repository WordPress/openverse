<template>
<div class="grid-container full">
  <header-section showNavSearch="true"></header-section>
  <div class="page_body">
    <h1>CC Search Advanced Search User Guide</h1>
    <p>
      When using CC Search, users can search for things like
      <a href="https://ccsearch.creativecommons.org/search?q=cats">"cats"</a> and
      <a href="https://ccsearch.creativecommons.org/search?q=dogs">"dogs"</a>.
      Users can filter the search query for
      <a href="https://search.creativecommons.org/search?q=dogs&provider=&li=&lt=commercial&searchBy">
      photos of "dogs" that I can use commercially
      </a>.
      In addition to that, it also supports using a special search syntax that lets users apply
      those filters directly on the search input box, without having to use the provided filter
      user interface. The following guide explains how you can take advantage of that special
      search syntax to enjoy a more powerful search capability.
    </p>

    <h2>Search by title</h2>
    <p>
      You can search by title by putting "<em>title:</em>" in front of the query.
    </p>
    <p>Example:
    <a href="https://search.creativecommons.org/search?q=title%3A%20cats">
      <em>title: cats</em>
    </a>
    </p>

    <h2>Search by license</h2>
    <p>
      You can search by license by putting "<em>license:</em>" in front of the query.
    </p>
    <p>Example:
    <a href='https://search.creativecommons.org/search?q=license%3A%20"by"'>
      <em>license: "by"</em>
    </a>
    <br />
    The results will be images licensed under the CC-BY license.
    You can use any of the other CC licenses: "by", "by-sa", "by-nc", "by-nd", "by-nc-sa",
    "by-nc-nd", "cc0", "pdm".
    </p>

    <h2>Search by provider</h2>
    <p>
      You can search by provider by putting "<em>provider:</em>" in front of the query.
    </p>
    <p>Example:
    <a href='https://search.creativecommons.org/search?q=provider%3A%20"met"'>
      <em>provider: "met"</em>
    </a>
    <br />
    Notice that we don't accept  "Metropolitan Museum of Art". We accept the provider code when
    searching by provider using this syntax. Use the following table with the provider
    code of every provider in our collection.
    </p>

    <div class="about-page_provider-stats-ctr">
      <table class="about-page_provider-stats-table">
        <thead>
          <th>Provider Name</th>
          <th>Provider Code</th>
        </thead>
        <tbody>
          <tr v-for="(imageProvider, index) in imageProviders"
              :key="index">
            <td>{{ imageProvider.display_name }}</td>
            <td>
              <a :href="providerSearchLink(imageProvider.provider_name)">
                {{ imageProvider.provider_name }}
              </a>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <h2>Search by tags</h2>
    <p>
      You can search by tags by putting "<em>tags.name:</em>" in front of the query.
    </p>
    <p>Example:
    <a href='https://search.creativecommons.org/search?q=tags.name%3A"sky"'>
      <em>tags.name:"sky"</em>
    </a>
    </p>

    <p>
    If you want to combine tags, you can use the AND operator, or the OR operator, depending on
    your search preference.
    </p>

    <p>Example:
    <a href='https://search.creativecommons.org/search?q=tags.name%3A"sky"%20AND%20tags.name%3A"airplane"'>
      <em>tags.name:"sky" AND tags.name:"airplane"</em>
    </a>
    <br />
    This will search for images with both tags, sky and airplane.
    </p>

    <p>Example:
    <a href='https://search.creativecommons.org/search?q=tags.name%3A%20"phone"%20OR%20tags.name%3A%20"sky"'>
      <em>tags.name: "phone" OR tags.name: "sky"</em>
    </a>
    <br />
    This will search for images tagged with sky or with phone, but not necessarily both.
    </p>

    <h2>Combining filters</h2>
    <p>
      Users can get a lot more interesting results when combining these filters.
      Let's get to a few examples.
    </p>

    <h3>Provider and license</h3>
    <p>Example:
    <a href='https://search.creativecommons.org/search?q=provider%3A%20"flickr"%20AND%20license%3A%20"by"'>
      <em>provider: "flickr" AND license: "by"</em>
    </a>
    <br />
    Will search for all images from Flickr licensed under CC-BY. Refer to the Licenses section
    above for filtering by other licenses.
    </p>

    <h3>Title and provider</h3>
    <p>Example:
    <a href='https://search.creativecommons.org/search?q=title%3A%20"nature"%20AND%20provider%3A%20"met"'>
      <em>title: "nature" AND provider: "met"</em>
    </a>
    <br />
    Will search for all images containing the word "nature" in their title in the MET collection.
    Refer to the Provider section above for filtering by other providers.
    </p>
  </div>
  <footer-section></footer-section>
</div>
</template>

<script>
import HeaderSection from '@/components/HeaderSection';
import FooterSection from '@/components/FooterSection';

const AboutPage = {
  name: 'search-help-page',
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
    providerSearchLink(providerCode) {
      return `https://search.creativecommons.org/search?q=provider%3A%20"${providerCode}"`;
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
</style>
