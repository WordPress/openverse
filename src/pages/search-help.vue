<template>
  <VContentPage>
    <h1>{{ $t("search-guide.title", { openverse: "Openverse" }) }}</h1>
    <p>{{ $t("search-guide.intro") }}</p>

    <h2>{{ $t("search-guide.exact.title") }}</h2>
    <i18n path="search-guide.exact.content" tag="p">
      <template #link>
        <VLink
          :aria-label="$t('search-guide.exact.aria-label')"
          :href="pathFromQuery('&quot;Claude Monet&quot;')"
        >
          <em>{{ $t("search-guide.exact.claude-monet") }}</em>
        </VLink>
      </template>
    </i18n>

    <h2>{{ $t("search-guide.combine.title") }}</h2>

    <p>{{ $t("search-guide.combine.description") }}</p>
    <ul class="not-prose marker:text-dark-charcoal-20">
      <i18n
        v-for="[name, operator] in Object.entries(operators)"
        :key="name"
        :path="`search-guide.combine.${name}`"
        tag="li"
      >
        <template #symbol>
          <code
            :aria-label="
              $t(`search-guide.combine.aria-labels.${name}`).toString()
            "
            >{{ operator.symbol }}</code
          >
        </template>
      </i18n>
    </ul>
    <!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
    <i18n path="search-guide.example.and.description" tag="p">
      <template #link>
        <VLink
          :aria-label="$t('search-guide.example.and.aria-label').toString()"
          :href="pathFromQuery('dog+cat')"
        >
          <em>{{ $t("search-guide.example.and.example") }}</em>
        </VLink>
      </template>
      <template #br><br /></template>
    </i18n>

    <i18n path="search-guide.example.or.description" tag="p">
      <template #link>
        <VLink
          :aria-label="$t('search-guide.example.or.aria-label')"
          :href="pathFromQuery('dog|cat')"
        >
          <em>{{ $t("search-guide.example.or.example").toString() }}</em>
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
          {{ $t("search-guide.example.negate.operator-name").toString() }}</em
        >
      </template>
    </i18n>

    <i18n path="search-guide.example.negate.content" tag="p" class="mb-4">
      <template #link>
        <VLink
          :aria-label="$t('search-guide.example.negate.aria-label')"
          :href="pathFromQuery('dog -pug')"
        >
          <em>{{ $t("search-guide.example.negate.example") }}</em>
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
          {{ $t("search-guide.example.prefix.operator-name").toString() }}</em
        >
      </template>
    </i18n>

    <i18n path="search-guide.example.prefix.content" tag="p" class="mb-4">
      <template #link>
        <VLink
          :aria-label="$t('search-guide.example.prefix.aria-label')"
          :href="pathFromQuery('net*')"
        >
          <em>{{ $t("search-guide.example.prefix.example") }}</em>
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
          :href="pathFromQuery('dog (corgis | labrador)')"
        >
          <em>{{ $t("search-guide.example.precedence.example") }}</em>
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
          {{ $t("search-guide.example.fuzziness.link-text") }}
        </VLink>
      </template>
    </i18n>

    <i18n path="search-guide.example.fuzziness.content" tag="p">
      <template #link>
        <VLink
          :aria-label="$t('search-guide.example.fuzziness.aria-label')"
          :href="pathFromQuery('theatre~1')"
        >
          <em>{{ $t("search-guide.example.fuzziness.example") }}</em>
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
import { defineComponent, useMeta } from "@nuxtjs/composition-api"

import { useSearchStore } from "~/stores/search"

import { useI18n } from "~/composables/use-i18n"

import VLink from "~/components/VLink.vue"
import VContentPage from "~/components/VContentPage.vue"

const operators = {
  and: { symbol: "+", query: "dog+cat" },
  not: { symbol: "-", query: "dog-cat" },
  or: { symbol: "|", query: "dog|cat" },
  prefix: { symbol: "*", query: "net*" },
  precedence: { symbol: "()", query: "dogs+(corgis|labrador)" },
  fuzziness: {
    symbol: "~",
    query: "theatre~1",
    reference: "https://en.wikipedia.org/wiki/Levenshtein_distance",
  },
}

export default defineComponent({
  name: "VSearchHelpPage",
  components: { VLink, VContentPage },
  layout: "content-layout",
  setup() {
    const i18n = useI18n()
    const searchStore = useSearchStore()

    useMeta({
      title: `${i18n.t("search-guide.title", {
        openverse: "Openverse",
      })} | Openverse`,
      meta: [{ hid: "robots", name: "robots", content: "all" }],
    })

    const pathFromQuery = (queryString: string) => {
      return searchStore.getSearchPath({
        query: { q: queryString },
      })
    }
    return { pathFromQuery, operators }
  },
  head: {},
})
</script>
