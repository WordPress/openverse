<template>
<div class="page grid-container full">
  <header-section showNavSearch="true"></header-section>
  <div class="page_body">
    <h1>CC Search Syntax Guide</h1>
    <p>
      When you search, you can enter special symbols or words to your search term
      to make your search results more precise.
    </p>

    <h2>Search for an exact match</h2>
    <p>
      Put a word or phrase inside quotes. For example,
      <a href='https://search.creativecommons.org/search?q="Claude%20Monet"'>
        <em>"Claude Monet"</em>
      </a>.
    </p>

    <h2>Search by title</h2>
    <p>
      Put <em>title:</em> in front of your search term to see only results whose
      title contains the specified term. For example,
      <a href='https://search.creativecommons.org/search?q=title%3A%20"cats"'>
        <em>title:"cats"</em>
      </a>.
    </p>

    <h2>Search by license</h2>
    <p>
      Put <em>license:</em> in front of your search term to see only results
      from the specified license. For example,
      <a href='https://search.creativecommons.org/search?q=license%3A%20"by"'>
        <em>license:"by"</em>
      </a>
      <br />
      The results will be images licensed under the CC-BY license.
      You can use any of the other CC licenses: "by", "by-sa", "by-nc", "by-nd", "by-nc-sa",
      "by-nc-nd", "cc0", "pdm".
    </p>

    <h2>Search by provider</h2>
    <p>
      Put <em>provider:</em> in front of your search term to see only results from the
      specified source. For example,
      <a href='https://search.creativecommons.org/search?q=provider%3A%20"met"'>
        <em>provider:"met"</em>
      </a>
      <br />
      Note that you must use one of the provider codes specified below, searching for
      something like <em>provider:"Metropolitan Museum of Art"</em> will not return any results.
      Use the following table with the provider code of every provider in our collection.
    </p>

    <div class="page_provider-stats-ctr">
      <table class="page_provider-stats-table">
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
      Put <em>tags.name:</em> in front of your search term to see only results that are
      tagged with the specified tag. For example,
    <a href='https://search.creativecommons.org/search?q=tags.name%3A"sky"'>
      <em>tags.name:"sky"</em>
    </a>
    <br />
    If you want to combine tags, you can use the AND operator, or the OR operator, depending on
    your search preference.

    <br />

    <p>Example:
    <a href='https://search.creativecommons.org/search?q=tags.name%3A"sky"%20AND%20tags.name%3A"airplane"'>
      <em>tags.name:"sky" AND tags.name:"airplane"</em>
    </a>
    <br />
    This will search for images with both tags, sky and airplane.
    </p>

    <p>Example:
    <a href='https://search.creativecommons.org/search?q=tags.name%3A%20"phone"%20OR%20tags.name%3A%20"sky"'>
      <em>tags.name:"phone" OR tags.name:"sky"</em>
    </a>
    <br />
    This will search for images tagged with sky or with phone, but not necessarily both.
    </p>

    <h2>Combining keywords</h2>

    <p>
      Put <em>AND</em> in between two queries to see only results that match both queries.
      For example:
      <ul>
        <li>
          <a href='https://ccsearch.creativecommons.org/search?q=title%3A%20"nature"%20AND%20provider%3A%20"met"'>
            <em>title:"nature" AND provider:"met"</em>
          </a>
          will return images from the MET and whose title contains nature.
        </li>
        <li>
          <a href='https://ccsearch.creativecommons.org/search?q=tags.name%3A"sky"AND%20tags.name%3A"airplane"'>
            <em>tags.name:"sky" AND tags.name:"airplane"</em>
          </a>
          will return images tagged both sky and  airplane.
        </li>
      </ul>
    </p>

    <p>
      Put <em>OR</em> in between two queries to see only results that match either query.
      For example:
      <ul>
        <li>
          <a href='https://ccsearch.creativecommons.org/search?q=title%3A%20"nature"%20AND%20provider%3A%20"met"'>
            <em>provider:"met" OR provider:"flickr"</em>
          </a>
          will return images which are either from MET or from Flickr.
        </li>
        <li>
          <a href='https://ccsearch.creativecommons.org/search?q=tags.name%3A"phone"%20OR%20tags.name%3A"tablet"'>
            <em>tags.name:"phone" OR tags.name:"tablet"</em>
          </a>
          will return images tagged either phone or  tablet.
        </li>
      </ul>
    </p>

    <p>
      Put <em>NOT</em> in between two queries to see only results that match the first query
      and do not match the second query. You can also use parentheses to combine more than one
      of these operations For example:
      <ul>
        <li>
          <a href='https://ccsearch.creativecommons.org/search?q=license%3A"by"%20AND%20%28NOT%20provider%3A"flickr"%29'>
            <em>license:"by" AND (NOT provider:"flickr")</em>
          </a>
          will return images licensed under CC BY from all providers except from Flickr.
        </li>
        <li>
          <a href='https://ccsearch.creativecommons.org/search?q=tags.name%3A"bird"%20AND%20%28NOT%20tags.name%3A"flamingo"%29'>
            <em>tags.name:"bird" AND (NOT tags.name:"flamingo")</em>
          </a>
          will return all images tagged bird except images also tagged  flamingo.
        </li>
      </ul>
    </p>
  </div>
  <footer-section></footer-section>
</div>
</template>

<script>
import HeaderSection from '@/components/HeaderSection';
import FooterSection from '@/components/FooterSection';
import ServerPrefetchProvidersMixin from '@/pages/mixins/ServerPrefetchProvidersMixin';

const SearchHelpPage = {
  name: 'search-help-page',
  mixins: [ServerPrefetchProvidersMixin],
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

export default SearchHelpPage;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  @import '../styles/text-only-page.scss';
</style>
