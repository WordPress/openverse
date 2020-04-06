<template>
<div class="page">
  <header-section showNavSearch="true"></header-section>
  <div class="margin-larger">
    <h2 class="margin-vertical-normal">CC Search Syntax Guide</h2>
    <p>
      When you search, you can enter special symbols or words to your search term
      to make your search results more precise.
    </p>

    <h3 class="margin-vertical-normal">Search for an exact match</h3>
    <p>
      Put a word or phrase inside quotes. For example,
      <a href='https://search.creativecommons.org/search?q="Claude%20Monet"'>
        <em>"Claude Monet"</em>
      </a>.
    </p>

    <h3 class="margin-vertical-normal">Combining terms</h3>

    <p class="margin-vertical-normal">
    If you want to combine terms, you can use the following operators
    to perform more complex queries
    </p>

    <ul >
      <li class="listitem">
        <code class="literal">+</code> signifies AND operation
      </li>
      <li class="listitem">
        <code class="literal">|</code> signifies OR operation
      </li>
      <li class="listitem">
        <code class="literal">-</code> negates a single token
      </li>
      <li class="listitem">
        <code class="literal">*</code> at the end of a term signifies a prefix query
      </li>
      <li class="listitem">
        <code class="literal">(</code> and <code class="literal">)</code> signify precedence
      </li>
      <li class="listitem">
        <code class="literal">~N</code> after a word signifies edit distance (fuzziness)
      </li>
    </ul>


    <p class="margin-vertical-normal">Example:
    <a href='https://search.creativecommons.org/search?q=dog%2Bcat'>
      <em>dog+cat</em>
    </a>
    <br />
    This will search for images related to both dog and cat.
    </p>

    <p class="margin-vertical-normal">Example:
      <a href='https://search.creativecommons.org/search?q=dog%2Bcat'>
        <em>dog|cat</em>
      </a>
      <br />
      This will search for images related to dog or cat, but not necessarily both.
    </p>

    <p class="margin-vertical-normal">
      You can use the <em>- operator (signifies NOT)</em>
      to exclude a search term from the results.
    </p>

    <p class="margin-vertical-normal">Example:
      <a href='https://search.creativecommons.org/search?q=dog%20-pug'>
        <em>dog -pug</em>
      </a>
      <br />
      This will search for images related to dog but won't include results related to "pug"
    </p>

    <p class="margin-vertical-normal">
      You can use the <em>* operator (wildcard)</em>
      to mark a prefix term. This will match anything after the *.
    </p>

    <p class="margin-vertical-normal">Example:
      <a href='https://search.creativecommons.org/search?q=net%2a'>
        <em>net*</em>
      </a>
      <br />
      This will search for images matching anything with "net".
      This might include "network", "Netflix", "Netherlands", etc..
    </p>

    <p class="margin-vertical-normal">
      You can use parentheses <em>( and )</em>
      to specify precedence of terms or combine more complex queries.
    </p>

    <p class="margin-vertical-normal">Example:
      <a href='https://search.creativecommons.org/search?q=dogs%20%2B%20%28corgies%20%7C%20labrador%29'>
        <em>dogs + (corgies | labrador)</em>
      </a>
      <br />
      This will search for images that match dogs that are either corgies or labrador.
    </p>

    <p class="margin-vertical-normal">
      You can use <em>~N</em>
      to specify some fuzzy logic to the term according to the
      <a href="http://en.wikipedia.org/wiki/Levenshtein_distance">Levenshtein Edit Distance</a>
      — the number of one character changes that need to be made to one string to make
      it the same as another string.
    </p>

    <p class="margin-vertical-normal">Example:
      <a href='https://search.creativecommons.org/search?q=theatre~1'>
        <em>theatre~1</em>
      </a>
      <br />
      This will search for images that match strings close to the term "theatre" with a difference
      of one character. Results might include terms with different spellings like "theater".
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
