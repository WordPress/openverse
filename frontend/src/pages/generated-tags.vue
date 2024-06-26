<template>
  <VContentPage>
    <h1>{{ $t("generatedTags.title") }}</h1>
    <p>{{ $t("generatedTags.intro.content") }}</p>
  </VContentPage>
</template>

<script lang="ts">
import { defineComponent, useMeta } from "@nuxtjs/composition-api"

import { useI18n } from "~/composables/use-i18n"

import VContentPage from "~/components/VContentPage.vue"

export default defineComponent({
  name: "VGeneratedTagsPage",
  components: { VContentPage },
  layout: "content-layout",
  setup() {
    const i18n = useI18n()

    useMeta({
      title: `${i18n.t("generatedTags.title")} | Openverse`,
      meta: [{ hid: "robots", name: "robots", content: "all" }],
    })

    return {}
  },
  head: {},
})
</script>
