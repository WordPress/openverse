<script setup lang="ts">
import { definePageMeta, useHead, useI18n } from "#imports"

import VContentPage from "~/components/VContentPage.vue"

defineOptions({
  name: "TagsPage",
})

definePageMeta({
  layout: "content-layout",
})

const { t } = useI18n({ useScope: "global" })

useHead({ title: `${t("tags.title")} | Openverse` })
</script>

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
