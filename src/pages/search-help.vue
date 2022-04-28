<template>
  <VContentPage>
    <h1>
      {{ $t('search-guide.title', { openverse: 'Openverse' }) }}
    </h1>
    <p>
      {{ $t('search-guide.intro') }}
    </p>

    <h2>
      {{ $t('search-guide.exact.title') }}
    </h2>
    <i18n path="search-guide.exact.content" tag="p">
      <template #link>
        <!-- eslint-disable -->
        <VLink
          :aria-label="$t('search-guide.exact.aria-label')"
          :href="pathFromQuery('Claude Monet', true)"
        >
          <em>{{ $t('search-guide.exact.claude-monet') }}</em>
        </VLink>
        <!-- eslint-enable -->
      </template>
    </i18n>

    <h2>
      {{ $t('search-guide.combine.title') }}
    </h2>

    <p>
      {{ $t('search-guide.combine.description') }}
    </p>
    <ul>
      <i18n path="search-guide.combine.and" tag="li">
        <!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
        <template #symbol>
          <code
            :aria-label="$t('search-guide.combine.aria-labels.plus').toString()"
            >+
          </code>
        </template>
      </i18n>
      <i18n path="search-guide.combine.or" tag="li">
        <template #symbol>
          <code
            :aria-label="
              $t('search-guide.combine.aria-labels.vertical-bar').toString()
            "
            >|
          </code>
        </template>
      </i18n>
      <i18n path="search-guide.combine.negate" tag="li">
        <template #symbol>
          <code
            :aria-label="
              $t('search-guide.combine.aria-labels.minus').toString()
            "
            >-
          </code>
        </template>
      </i18n>
      <i18n path="search-guide.combine.prefix" tag="li">
        <template #symbol>
          <code
            :aria-label="$t('search-guide.combine.aria-labels.star').toString()"
            >*
          </code>
        </template>
      </i18n>
      <i18n path="search-guide.combine.precedence" tag="li">
        <template #open>
          <code
            :aria-label="$t('search-guide.combine.aria-labels.open').toString()"
            >(
          </code>
        </template>
        <template #close>
          <code
            :aria-label="
              $t('search-guide.combine.aria-labels.close').toString()
            "
            >)
          </code>
        </template>
      </i18n>
      <i18n path="search-guide.combine.fuzziness" tag="li">
        <template #symbol>
          <code
            :aria-label="
              $t('search-guide.combine.aria-labels.fuzziness').toString()
            "
            >~N
          </code>
        </template>
      </i18n>
    </ul>

    <i18n path="search-guide.example.and.description" tag="p">
      <template #link>
        <VLink
          :aria-label="$t('search-guide.example.and.aria-label').toString()"
          :href="pathFromQuery('dog%2Bcat')"
        >
          <em>{{ $t('search-guide.example.and.example') }}</em>
        </VLink>
      </template>
      <template #br>
        <br />
      </template>
    </i18n>

    <i18n path="search-guide.example.or" tag="p">
      <template #link>
        <VLink
          :aria-label="$t('search-guide.example.or.aria-label')"
          :href="pathFromQuery('dog%7Ccat')"
        >
          <em>{{ $t('search-guide.example.or.example').toString() }}</em>
        </VLink>
      </template>
      <template #br>
        <br />
      </template>
    </i18n>

    <i18n path="search-guide.example.negate.description" tag="p" class="mt-4">
      <template #operator>
        <em
          :aria-label="
            $t('search-guide.example.negate.operator-aria-label').toString()
          "
          >-
          {{ $t('search-guide.example.negate.operator-name').toString() }}</em
        >
      </template>
    </i18n>

    <i18n path="search-guide.example.negate.content" tag="p" class="mb-4">
      <template #link>
        <VLink
          :aria-label="$t('search-guide.example.negate.aria-label')"
          :href="pathFromQuery('dog%20-pug')"
        >
          <em>{{ $t('search-guide.example.negate.example') }}</em>
        </VLink>
      </template>
      <template #br>
        <br />
      </template>
    </i18n>

    <i18n path="search-guide.example.prefix.description" tag="p" class="mt-4">
      <template #operator>
        <em
          :aria-label="$t('search-guide.example.prefix.aria-label').toString()"
          >*
          {{ $t('search-guide.example.prefix.operator-name').toString() }}</em
        >
      </template>
    </i18n>

    <i18n path="search-guide.example.prefix.content" tag="p" class="mb-4">
      <template #link>
        <VLink
          :aria-label="$t('search-guide.example.prefix.aria-label')"
          :href="pathFromQuery('net%2a')"
        >
          <em>{{ $t('search-guide.example.prefix.example') }}</em>
        </VLink>
      </template>
      <template #br>
        <br />
      </template>
    </i18n>

    <i18n path="search-guide.example.precedence.description" tag="p">
      <template #highlight>
        <em>( and )</em>
      </template>
    </i18n>

    <i18n path="search-guide.example.precedence.content" tag="p" class="mb-4">
      <template #link>
        <VLink
          :aria-label="$t('search-guide.example.precedence.aria-label')"
          :href="pathFromQuery('dogs%20%2B%20%28corgis%20%7C%20labrador%29')"
        >
          <em>{{ $t('search-guide.example.precedence.example') }}</em>
        </VLink>
      </template>
      <template #br>
        <br />
      </template>
    </i18n>

    <i18n path="search-guide.example.fuzziness.description" tag="p">
      <template #highlight>
        <em aria-label="tilde N">~N</em>
      </template>
      <template #link>
        <VLink href="https://en.wikipedia.org/wiki/Levenshtein_distance">
          {{ $t('search-guide.example.fuzziness.link-text') }}
        </VLink>
      </template>
    </i18n>

    <i18n path="search-guide.example.fuzziness.content" tag="p" class="mb-4">
      <template #link>
        <VLink
          :aria-label="$t('search-guide.example.fuzziness.aria-label')"
          :href="pathFromQuery('theatre~1')"
        >
          <em>{{ $t('search-guide.example.fuzziness.example') }}</em>
        </VLink>
      </template>
      <template #br>
        <br />
      </template>
    </i18n>
    <!-- eslint-enable @intlify/vue-i18n/no-raw-text -->
  </VContentPage>
</template>

<script lang="ts">
import { defineComponent, useContext } from '@nuxtjs/composition-api'

import VLink from '~/components/VLink.vue'
import VContentPage from '~/components/VContentPage.vue'

export default defineComponent({
  name: 'VSearchHelpPage',
  components: { VLink, VContentPage },
  setup() {
    const { app } = useContext()
    const pathFromQuery = (queryString: string, quote = false) => {
      return app.localePath({
        path: 'search',
        query: {
          q: quote ? `"${queryString}"` : queryString,
        },
      })
    }
    const providerSearchLink = (providerCode: string) => {
      return `https://search.creativecommons.org/search?q=provider%3A%20"${providerCode}"`
    }
    return { pathFromQuery, providerSearchLink }
  },
  head() {
    return {
      title: `${this.$t('search-guide.title', {
        openverse: 'Openverse',
      })} | Openverse`,
    }
  },
})
</script>
