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

    <h2>{{ $t("searchGuide.negate.title") }}</h2>

    <i18n path="searchGuide.negate.content" tag="p" class="mb-4">
      <template #operator
        ><!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
        <em :aria-label="$t('searchGuide.negate.operatorAriaLabel').toString()"
          >- {{ $t("searchGuide.negate.operatorName").toString() }}</em
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
    </i18n>
  </VContentPage>
</template>

<script lang="ts">
import { defineComponent, useMeta } from "@nuxtjs/composition-api"

import { useSearchStore } from "~/stores/search"

import { useI18n } from "~/composables/use-i18n"

import VLink from "~/components/VLink.vue"
import VContentPage from "~/components/VContentPage.vue"

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
    return { pathFromQuery }
  },
  head: {},
})
</script>
