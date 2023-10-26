<template>
  <VContentPage>
    <h1>{{ $t("searchGuide.title", { openverse: "Openverse" }) }}</h1>
    <p>{{ $t("searchGuide.intro") }}</p>

    <h2>{{ $t("searchGuide.exact.title") }}</h2>
    <i18n path="searchGuide.exact.content" tag="p">
      <template #link>
        <VLink
          :aria-label="$t('searchGuide.exact.ariaLabel')"
          :href="pathFromQuery('&quot;Claude Monet&quot;')"
        >
          <em>{{ $t("searchGuide.exact.claudeMonet") }}</em>
        </VLink>
      </template>
    </i18n>

    <h2>{{ $t("searchGuide.combine.title") }}</h2>

    <p>{{ $t("searchGuide.combine.description") }}</p>
    <ul class="not-prose list-inside list-disc marker:text-dark-charcoal-20">
      <i18n
        v-for="[name, operator] in Object.entries(operators)"
        :key="name"
        :path="`searchGuide.combine.${name}`"
        tag="li"
      >
        <template #symbol>
          <code
            :aria-label="
              $t(`searchGuide.combine.ariaLabels.${name}`).toString()
            "
            >{{ operator.symbol }}</code
          >
        </template>
      </i18n>
    </ul>
    <!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
    <i18n path="searchGuide.example.and.description" tag="p">
      <template #link>
        <VLink
          :aria-label="$t('searchGuide.example.and.ariaLabel').toString()"
          :href="pathFromQuery('dog+cat')"
        >
          <em>{{ $t("searchGuide.example.and.example") }}</em>
        </VLink>
      </template>
      <template #br><br /></template>
    </i18n>

    <i18n path="searchGuide.example.or.description" tag="p">
      <template #link>
        <VLink
          :aria-label="$t('searchGuide.example.or.ariaLabel')"
          :href="pathFromQuery('dog|cat')"
        >
          <em>{{ $t("searchGuide.example.or.example").toString() }}</em>
        </VLink>
      </template>
      <template #br>
        <br />
      </template>
    </i18n>

    <i18n path="searchGuide.example.negate.description" tag="p" class="mt-4">
      <template #operator>
        <em
          :aria-label="
            $t('searchGuide.example.negate.operatorAriaLabel').toString()
          "
          >- {{ $t("searchGuide.example.negate.operatorName").toString() }}</em
        >
      </template>
    </i18n>

    <i18n path="searchGuide.example.negate.content" tag="p" class="mb-4">
      <template #link>
        <VLink
          :aria-label="$t('searchGuide.example.negate.ariaLabel')"
          :href="pathFromQuery('dog -pug')"
        >
          <em>{{ $t("searchGuide.example.negate.example") }}</em>
        </VLink>
      </template>
      <template #br>
        <br />
      </template>
    </i18n>

    <i18n path="searchGuide.example.prefix.description" tag="p" class="mt-4">
      <template #operator>
        <em :aria-label="$t('searchGuide.example.prefix.ariaLabel').toString()"
          >* {{ $t("searchGuide.example.prefix.operatorName").toString() }}</em
        >
      </template>
    </i18n>

    <i18n path="searchGuide.example.prefix.content" tag="p" class="mb-4">
      <template #link>
        <VLink
          :aria-label="$t('searchGuide.example.prefix.ariaLabel')"
          :href="pathFromQuery('net*')"
        >
          <em>{{ $t("searchGuide.example.prefix.example") }}</em>
        </VLink>
      </template>
      <template #br>
        <br />
      </template>
    </i18n>

    <i18n path="searchGuide.example.precedence.description" tag="p">
      <template #highlight>
        <em>( and )</em>
      </template>
    </i18n>

    <i18n path="searchGuide.example.precedence.content" tag="p" class="mb-4">
      <template #link>
        <VLink
          :aria-label="$t('searchGuide.example.precedence.ariaLabel')"
          :href="pathFromQuery('dog (corgis | labrador)')"
        >
          <em>{{ $t("searchGuide.example.precedence.example") }}</em>
        </VLink>
      </template>
      <template #br>
        <br />
      </template>
    </i18n>

    <i18n path="searchGuide.example.fuzziness.description" tag="p">
      <template #highlight>
        <em aria-label="tilde N">~N</em>
      </template>
      <template #link>
        <VLink href="https://en.wikipedia.org/wiki/Levenshtein_distance">
          {{ $t("searchGuide.example.fuzziness.linkText") }}
        </VLink>
      </template>
    </i18n>

    <i18n path="searchGuide.example.fuzziness.content" tag="p">
      <template #link>
        <VLink
          :aria-label="$t('searchGuide.example.fuzziness.ariaLabel')"
          :href="pathFromQuery('theatre~1')"
        >
          <em>{{ $t("searchGuide.example.fuzziness.example") }}</em>
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
      title: `${i18n.t("searchGuide.title", {
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
