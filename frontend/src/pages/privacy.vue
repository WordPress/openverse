<template>
  <VContentPage>
    <h1>
      {{ $t("privacy.title", { openverse: "Openverse" }) }}
    </h1>
    <i18n-t keypath="privacy.intro.content" tag="p">
      <template #link>
        <VLink href="https://wordpress.org/about/privacy/">{{
          $t("privacy.intro.link")
        }}</VLink>
      </template>
      <template #openverse>Openverse</template>
    </i18n-t>

    <h2>
      {{ $t("privacy.cookies.title") }}
    </h2>
    <i18n-t keypath="privacy.cookies.content" tag="p">
      <template #openverse>Openverse</template>
    </i18n-t>

    <h2>
      {{ $t("privacy.contact.title") }}
    </h2>

    <i18n-t keypath="privacy.contact.content" tag="p">
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
    </i18n-t>

    <h2>{{ $t("prefPage.groups.analytics.title") }}</h2>

    <p>
      {{ $t("prefPage.groups.analytics.desc", { openverse: "Openverse" }) }}
    </p>

    <VCheckbox
      id="analytics"
      class="flex-row items-center"
      :checked="isChecked"
      is-switch
      @change="handleChange"
    >
      <div>
        {{ $t("prefPage.features.analytics") }}
      </div>
    </VCheckbox>
  </VContentPage>
</template>

<script lang="ts">
import { defineNuxtComponent, definePageMeta, useHead, useI18n } from "#imports"

import { computed } from "vue"

import { useFeatureFlagStore } from "~/stores/feature-flag"
import { ON, OFF } from "~/constants/feature-flag"

import VLink from "~/components/VLink.vue"
import VCheckbox from "~/components/VCheckbox/VCheckbox.vue"
import VContentPage from "~/components/VContentPage.vue"

export default defineNuxtComponent({
  name: "VPrivacyPage",
  components: { VLink, VCheckbox, VContentPage },
  setup() {
    definePageMeta({
      layout: "content-layout",
    })
    const i18n = useI18n({ useScope: "global" })
    const featureFlagStore = useFeatureFlagStore()

    useHead({
      title: `${i18n.t("privacy.title", {
        openverse: "Openverse",
      })} | Openverse`,
      meta: [{ name: "robots", content: "all" }],
    })

    const isChecked = computed(
      () => featureFlagStore.featureState("analytics") === ON
    )

    const handleChange = ({ checked }: { checked?: boolean }) => {
      featureFlagStore.toggleFeature("analytics", checked ? ON : OFF)
    }

    return {
      isChecked,
      handleChange,
    }
  },
})
</script>
