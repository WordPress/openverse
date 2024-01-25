<template>
  <VContentPage>
    <h1>{{ $t("searchGuide.title", { openverse: "Openverse" }) }}</h1>
    <p>{{ $t("searchGuide.intro") }}</p>

    <h2>{{ $t("searchGuide.exact.title") }}</h2>
    <i18n-t scope="global" keypath="searchGuide.exact.content" tag="p">
      <template #link>
        <VLink
          :aria-label="$t('searchGuide.exact.ariaLabel')"
          :href="pathFromQuery('&quot;Claude Monet&quot;')"
        >
          <em>{{ $t("searchGuide.exact.claudeMonet") }}</em>
        </VLink>
      </template>
    </i18n-t>

    <h2>{{ $t("searchGuide.negate.title") }}</h2>

    <i18n-t
      scope="global"
      keypath="searchGuide.negate.content"
      tag="p"
      class="mb-4"
    >
      <template #operator
        ><!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
        <em :aria-label="$t('searchGuide.negate.operatorAriaLabel')"
          >- {{ $t("searchGuide.negate.operatorName") }}</em
        >
        <!-- eslint-enable @intlify/vue-i18n/no-raw-text -->
      </template>
      <template #link>
        <VLink
          :aria-label="$t('searchGuide.negate.ariaLabel')"
          :href="pathFromQuery('dog -pug')"
        >
          <em>{{ $t("searchGuide.negate.example") }}</em>
        </VLink>
      </template>
      <template #br>
        <br />
      </template>
    </i18n-t>
  </VContentPage>
</template>

<script setup lang="ts">
import { definePageMeta } from "#imports"

import { useSearchStore } from "~/stores/search"

import VLink from "~/components/VLink.vue"
import VContentPage from "~/components/VContentPage.vue"

definePageMeta({
  layout: "content-layout",
})
const searchStore = useSearchStore()

const pathFromQuery = (queryString: string) => {
  return searchStore.getSearchPath({
    query: { q: queryString },
  })
}
</script>
