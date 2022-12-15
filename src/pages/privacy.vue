<template>
  <VContentPage>
    <h1>
      {{ $t("privacy.title", { openverse: "Openverse" }) }}
    </h1>
    <i18n path="privacy.intro.content" tag="p">
      <template #link>
        <VLink href="https://wordpress.org/about/privacy/">{{
          $t("privacy.intro.link")
        }}</VLink>
      </template>
      <template #openverse>Openverse</template>
    </i18n>

    <h2>
      {{ $t("privacy.cookies.title") }}
    </h2>
    <i18n path="privacy.cookies.content" tag="p">
      <template #openverse>Openverse</template>
    </i18n>

    <h2>
      {{ $t("privacy.contact.title") }}
    </h2>

    <i18n path="privacy.contact.content" tag="p">
      <template #openverse>Openverse</template>
      <template #email>
        <VLink href="mailto:openverse@wordpress.org"
          >openverse@wordpress.org</VLink
        >
      </template>
      <template #issue>
        <VLink href="https://github.com/WordPress/openverse/issues/new/choose">
          {{ $t("privacy.contact.issue") }}</VLink
        >
      </template>
      <template #chat>
        <VLink href="https://make.wordpress.org/chat/">
          {{ $t("privacy.contact.chat") }}</VLink
        >
      </template>
    </i18n>
  </VContentPage>
</template>

<script lang="ts">
import { defineComponent, useMeta } from "@nuxtjs/composition-api"

import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useI18n } from "~/composables/use-i18n"

import VLink from "~/components/VLink.vue"
import VContentPage from "~/components/VContentPage.vue"

export default defineComponent({
  name: "VPrivacyPage",
  components: { VLink, VContentPage },
  setup() {
    const i18n = useI18n()
    const featureFlagStore = useFeatureFlagStore()

    useMeta({
      title: `${i18n.t("privacy.title", {
        openverse: "Openverse",
      })} | Openverse`,
      meta: featureFlagStore.isOn("new_header")
        ? [{ hid: "robots", name: "robots", content: "all" }]
        : undefined,
    })
  },
  head: {},
})
</script>
