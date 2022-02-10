<template>
  <div class="section" dir="ltr">
    <div class="container">
      <div class="mb-10">
        <h1 class="text-5xl mb-10">
          {{ $t('search-guide.title') }}
        </h1>
        <p>
          {{ $t('search-guide.intro') }}
        </p>

        <h2 class="mt-10 text-2xl mb-4">
          {{ $t('search-guide.exact.title') }}
        </h2>
        <i18n path="search-guide.exact.content" tag="p">
          <template #link>
            <!-- eslint-disable -->
            <a
              :aria-label="$t('search-guide.exact.aria-label')"
              href='https://search.creativecommons.org/search?q="Claude%20Monet"'
            >
              <em>{{ $t('search-guide.exact.claude-monet') }}</em>
            </a>
            <!-- eslint-enable -->
          </template>
        </i18n>

        <h2 class="my-4 text-2xl">
          {{ $t('search-guide.combine.title') }}
        </h2>

        <p class="my-4">
          {{ $t('search-guide.combine.description') }}
        </p>
        <!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
        <ul>
          <i18n path="search-guide.combine.and" tag="li" class="listitem">
            <template #symbol>
              <code
                :aria-label="$t('search-guide.combine.aria-labels.plus')"
                class="literal"
                >+</code
              >
            </template>
          </i18n>
          <i18n path="search-guide.combine.or" tag="li" class="listitem">
            <template #symbol>
              <code
                :aria-label="
                  $t('search-guide.combine.aria-labels.vertical-bar')
                "
                class="literal"
                >|</code
              >
            </template>
          </i18n>
          <i18n path="search-guide.combine.negate" tag="li" class="listitem">
            <template #symbol>
              <code
                :aria-label="$t('search-guide.combine.aria-labels.minus')"
                class="literal"
                >-</code
              >
            </template>
          </i18n>
          <i18n path="search-guide.combine.prefix" tag="li" class="listitem">
            <template #symbol>
              <code
                :aria-label="$t('search-guide.combine.aria-labels.star')"
                class="literal"
                >*</code
              >
            </template>
          </i18n>
          <i18n
            path="search-guide.combine.precedence"
            tag="li"
            class="listitem"
          >
            <template #open>
              <code
                :aria-label="$t('search-guide.combine.aria-labels.open')"
                class="literal"
                >(</code
              >
            </template>
            <template #close>
              <code
                :aria-label="$t('search-guide.combine.aria-labels.close')"
                class="literal"
                >)</code
              >
            </template>
          </i18n>
          <i18n path="search-guide.combine.fuzziness" tag="li" class="listitem">
            <template #symbol>
              <code
                :aria-label="$t('search-guide.combine.aria-labels.fuzziness')"
                class="literal"
                >~N</code
              >
            </template>
          </i18n>
        </ul>

        <i18n path="search-guide.example.and.description" tag="p" class="my-4">
          <template #link>
            <a
              :aria-label="$t('search-guide.example.and.aria-label')"
              href="https://search.creativecommons.org/search?q=dog%2Bcat"
            >
              <em>{{ $t('search-guide.example.and.example') }}</em>
            </a>
          </template>
          <template #br>
            <br />
          </template>
        </i18n>

        <i18n path="search-guide.example.or" tag="p" class="my-4">
          <template #link>
            <a
              :aria-label="$t('search-guide.example.or.aria-label')"
              href="https://search.creativecommons.org/search?q=dog%7Ccat"
            >
              <em>{{ $t('search-guide.example.or.example') }}</em>
            </a>
          </template>
          <template #br>
            <br />
          </template>
        </i18n>

        <i18n
          path="search-guide.example.negate.description"
          tag="p"
          class="mt-4"
        >
          <template #operator>
            <em
              :aria-label="
                $t('search-guide.example.negate.operator-aria-label')
              "
              >- {{ $t('search-guide.example.negate.operator-name') }}</em
            >
          </template>
        </i18n>

        <i18n path="search-guide.example.negate.content" tag="p" class="mb-4">
          <template #link>
            <a
              :aria-label="$t('search-guide.example.negate.aria-label')"
              href="https://search.creativecommons.org/search?q=dog%20-pug"
            >
              <em>{{ $t('search-guide.example.negate.example') }}</em>
            </a>
          </template>
          <template #br>
            <br />
          </template>
        </i18n>

        <i18n
          path="search-guide.example.prefix.description"
          tag="p"
          class="mt-4"
        >
          <template #operator>
            <em :aria-label="$t('search-guide.example.prefix.aria-label')"
              >* {{ $t('search-guide.example.prefix.operator-name') }}</em
            >
          </template>
        </i18n>

        <i18n path="search-guide.example.prefix.content" tag="p" class="mb-4">
          <template #link>
            <a
              :aria-label="$t('search-guide.example.prefix.aria-label')"
              href="https://search.creativecommons.org/search?q=net%2a"
            >
              <em>{{ $t('search-guide.example.prefix.example') }}</em>
            </a>
          </template>
          <template #br>
            <br />
          </template>
        </i18n>

        <i18n
          path="search-guide.example.precedence.description"
          tag="p"
          class="mt-4"
        >
          <template #highlight>
            <em>( and )</em>
          </template>
        </i18n>

        <i18n
          path="search-guide.example.precedence.content"
          tag="p"
          class="mb-4"
        >
          <template #link>
            <a
              :aria-label="$t('search-guide.example.precedence.aria-label')"
              href="https://search.creativecommons.org/search?q=dogs%20%2B%20%28corgis%20%7C%20labrador%29"
            >
              <em>{{ $t('search-guide.example.precedence.example') }}</em>
            </a>
          </template>
          <template #br>
            <br />
          </template>
        </i18n>

        <i18n
          path="search-guide.example.fuzziness.description"
          tag="p"
          class="mt-4"
        >
          <template #highlight>
            <em aria-label="tilde N">~N</em>
          </template>
          <template #link>
            <a href="http://en.wikipedia.org/wiki/Levenshtein_distance">
              {{ $t('search-guide.example.fuzziness.link-text') }}
            </a>
          </template>
        </i18n>

        <i18n
          path="search-guide.example.fuzziness.content"
          tag="p"
          class="mb-4"
        >
          <template #link>
            <a
              :aria-label="$t('search-guide.example.fuzziness.aria-label')"
              href="https://search.creativecommons.org/search?q=theatre~1"
            >
              <em>{{ $t('search-guide.example.fuzziness.example') }}</em>
            </a>
          </template>
          <template #br>
            <br />
          </template>
        </i18n>
        <!-- eslint-enable -->
      </div>
    </div>
  </div>
</template>

<script>
const SearchHelpPage = {
  name: 'search-help-page',
  methods: {
    providerSearchLink(providerCode) {
      return `https://search.creativecommons.org/search?q=provider%3A%20"${providerCode}"`
    },
  },
  head() {
    return {
      title: `${this.$t('search-guide.title')} | ${this.$t('hero.brand')}`,
    }
  },
}

export default SearchHelpPage
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
@import '~/styles/text-only-page.scss';
</style>
