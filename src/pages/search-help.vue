<template>
  <div class="section">
    <div class="container is-fluid">
      <div class="margin-bottom-large">
        <h1 class="title is-2">
          {{ $t('search-guide.title') }}
        </h1>
        <p>
          {{ $t('search-guide.intro') }}
        </p>

        <h3 class="margin-top-large">
          {{ $t('search-guide.exact.title') }}
        </h3>
        <i18n path="search-guide.exact.content" tag="p">
          <template v-slot:link>
            <!-- eslint-disable -->
            <a
              aria-label="quote unquote Claude Monet"
              href='https://search.creativecommons.org/search?q="Claude%20Monet"'
            >
              <em>"Claude Monet"</em>
            </a>
            <!-- eslint-enable -->
          </template>
        </i18n>

        <h3 role="region" class="margin-vertical-normal">
          {{ $t('search-guide.combine.title') }}
        </h3>

        <p class="margin-vertical-normal">
          {{ $t('search-guide.combine.description') }}
        </p>

        <ul>
          <i18n path="search-guide.combine.and" tag="li" class="listitem">
            <template v-slot:symbol>
              <code aria-label="plus" class="literal">+</code>
            </template>
          </i18n>
          <i18n path="search-guide.combine.or" tag="li" class="listitem">
            <template v-slot:symbol>
              <code aria-label="vertical bar" class="literal">|</code>
            </template>
          </i18n>
          <i18n path="search-guide.combine.negate" tag="li" class="listitem">
            <template v-slot:symbol>
              <code aria-label="minus" class="literal">-</code>
            </template>
          </i18n>
          <i18n path="search-guide.combine.prefix" tag="li" class="listitem">
            <template v-slot:symbol>
              <code aria-label="star" class="literal">*</code>
            </template>
          </i18n>
          <i18n
            path="search-guide.combine.precedence"
            tag="li"
            class="listitem"
          >
            <template v-slot:open>
              <code aria-label="open paranthesis" class="literal">(</code>
            </template>
            <template v-slot:close>
              <code aria-label="close paranthesis" class="literal">)</code>
            </template>
          </i18n>
          <i18n path="search-guide.combine.fuzziness" tag="li" class="listitem">
            <template v-slot:symbol>
              <code aria-label="tilde N" class="literal">~N</code>
            </template>
          </i18n>
        </ul>

        <i18n
          path="search-guide.example.and"
          tag="p"
          class="margin-vertical-normal"
        >
          <template v-slot:link>
            <a
              aria-label="dog plus cat"
              href="https://search.creativecommons.org/search?q=dog%2Bcat"
            >
              <em>dog+cat</em>
            </a>
          </template>
          <template v-slot:br>
            <br />
          </template>
        </i18n>

        <i18n
          path="search-guide.example.or"
          tag="p"
          class="margin-vertical-normal"
        >
          <template v-slot:link>
            <a
              aria-label="dog vertical bar cat"
              href="https://search.creativecommons.org/search?q=dog%7Ccat"
            >
              <em>dog|cat</em>
            </a>
          </template>
          <template v-slot:br>
            <br />
          </template>
        </i18n>

        <i18n
          path="search-guide.example.negate.description"
          tag="p"
          class="margin-top-normal"
        >
          <template v-slot:highlight>
            <em aria-label="minus operator (signifies NOT)"
              >- operator (signifies NOT)</em
            >
          </template>
        </i18n>

        <i18n
          path="search-guide.example.negate.content"
          tag="p"
          class="margin-bottom-normal"
        >
          <template v-slot:link>
            <a
              aria-label="dog minus pug"
              href="https://search.creativecommons.org/search?q=dog%20-pug"
            >
              <em>dog -pug</em>
            </a>
          </template>
          <template v-slot:br>
            <br />
          </template>
        </i18n>

        <i18n
          path="search-guide.example.prefix.description"
          tag="p"
          class="margin-top-normal"
        >
          <template v-slot:highlight>
            <em>* operator (wildcard)</em>
          </template>
        </i18n>

        <i18n
          path="search-guide.example.prefix.content"
          tag="p"
          class="margin-bottom-normal"
        >
          <template v-slot:link>
            <a
              aria-label="net star"
              href="https://search.creativecommons.org/search?q=net%2a"
            >
              <em>net*</em>
            </a>
          </template>
          <template v-slot:br>
            <br />
          </template>
        </i18n>

        <i18n
          path="search-guide.example.precedence.description"
          tag="p"
          class="margin-top-normal"
        >
          <template v-slot:highlight>
            <em>( and )</em>
          </template>
        </i18n>

        <i18n
          path="search-guide.example.precedence.content"
          tag="p"
          class="margin-bottom-normal"
        >
          <template v-slot:link>
            <a
              aria-label="dogs plus open paranthesis corgis vertical bar labrador close paranthesis"
              href="https://search.creativecommons.org/search?q=dogs%20%2B%20%28corgis%20%7C%20labrador%29"
            >
              <em>dogs + (corgis | labrador)</em>
            </a>
          </template>
          <template v-slot:br>
            <br />
          </template>
        </i18n>

        <i18n
          path="search-guide.example.fuzziness.description"
          tag="p"
          class="margin-top-normal"
        >
          <template v-slot:highlight>
            <em aria-label="tilde N">~N</em>
          </template>
          <template v-slot:link>
            <a href="http://en.wikipedia.org/wiki/Levenshtein_distance"
              >Levenshtein Edit Distance</a
            >
          </template>
        </i18n>

        <i18n
          path="search-guide.example.fuzziness.content"
          tag="p"
          class="margin-bottom-normal"
        >
          <template v-slot:link>
            <a
              aria-label="theatre tilde 1"
              href="https://search.creativecommons.org/search?q=theatre~1"
            >
              <em>theatre~1</em>
            </a>
          </template>
          <template v-slot:br>
            <br />
          </template>
        </i18n>
      </div>
    </div>
  </div>
</template>

<script>
/* eslint-disable vue/html-quotes */

const SearchHelpPage = {
  name: 'search-help-page',
  layout: 'with-nav-search',
  computed: {
    imageProviders() {
      return this.$store.state.imageProviders
    },
  },
  methods: {
    providerSearchLink(providerCode) {
      return `https://search.creativecommons.org/search?q=provider%3A%20"${providerCode}"`
    },
  },
}

export default SearchHelpPage
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
@import '~/styles/text-only-page.scss';
</style>
