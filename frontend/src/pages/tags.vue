<template>
  <VContentPage>
    <h1>{{ $t("tags.title", { openverse: "Openverse" }) }}</h1>
    <p>{{ $t("tags.intro.a", { openverse: "Openverse" }) }}</p>
    <p>{{ $t("tags.intro.b") }}</p>
    <h2>{{ $t("tags.sourceTags.title") }}</h2>
    <p>
      {{ $t("tags.sourceTags.content.a") }}{{ $t("tags.sourceTags.content.b") }}
    </p>
    <h2>{{ $t("tags.generatedTags.title") }}</h2>
    <p>
      {{ $t("tags.generatedTags.content.a")
      }}{{ $t("tags.generatedTags.content.b") }}
    </p>
    <p>
      {{ $t("tags.generatedTags.content.c")
      }}{{ $t("tags.generatedTags.content.d") }}
    </p>
  </VContentPage>
</template>

<script lang="ts">
import { defineComponent, useMeta } from "@nuxtjs/composition-api"

import { useI18n } from "~/composables/use-i18n"

import VContentPage from "~/components/VContentPage.vue"

export default defineComponent({
  name: "VTagsPage",
  components: { VContentPage },
  layout: "content-layout",
  setup() {
    const i18n = useI18n()

    useMeta({
      title: `${i18n.t("tags.title")} | Openverse`,
      meta: [{ hid: "robots", name: "robots", content: "all" }],
    })

    return {}
  },
  head: {},
})
</script>
