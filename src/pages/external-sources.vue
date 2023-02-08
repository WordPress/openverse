<template>
  <VContentPage>
    <h1>
      {{ $t("external-sources-page.title") }}
    </h1>

    <i18n path="external-sources-page.intro" tag="p">
      <template #openverse>Openverse</template>
      <template #link>
        <VLink href="/sources">{{ $t("external-sources-page.link") }}</VLink>
      </template>
    </i18n>
    <p>{{ $t("external-sources-page.license", { openverse: "Openverse" }) }}</p>
    <p>
      {{ $t("external-sources-page.explanation", { openverse: "Openverse" }) }}
    </p>
    <p>
      {{
        $t("external-sources-page.relationships", { openverse: "Openverse" })
      }}
    </p>
    <h2>
      {{ $t("external-sources-page.new.title") }}
    </h2>
    <i18n path="external-sources-page.new.content" tag="p">
      <template #issue>
        <VLink
          aria-label="issue"
          href="https://github.com/WordPress/openverse-catalog/issues/new?assignees=&labels=%F0%9F%9A%A6+status%3A+awaiting+triage%2C%F0%9F%A7%B9+status%3A+ticket+work+required%2C%E2%98%81%EF%B8%8F+provider%3A+any&template=new_source_suggestion.yml&title=%3CSource+name+here%3E"
          >{{ $t("external-sources-page.new.issue") }}</VLink
        >
      </template>
      <template #email>
        <VLink aria-label="email" href="mailto:openverse@wordpress.org">{{
          $t("external-sources-page.new.email")
        }}</VLink>
      </template>
    </i18n>
    <h2>
      {{ $t("external-sources-page.why.title") }}
    </h2>
    <i18n path="external-sources-page.why.content" tag="p">
      <template #old>
        <VLink
          aria-label="email"
          href="https://oldsearch.creativecommons.org"
          >{{ $t("external-sources-page.why.old") }}</VLink
        >
      </template>
    </i18n>

    <p>
      {{ $t("external-sources-page.why.new", { openverse: "Openverse" }) }}
    </p>
    <i18n path="external-sources-page.why.feedback-suggestions" tag="p">
      <template #feedback>
        <VLink
          :aria-label="$t('external-sources-page.why.aria-label')"
          href="/feedback"
          >{{ $t("external-sources-page.why.feedback-link") }}</VLink
        >
      </template>
    </i18n>
  </VContentPage>
</template>
<script lang="ts">
import { defineComponent, useMeta } from "@nuxtjs/composition-api"

import { useFeatureFlagStore } from "~/stores/feature-flag"

import { useI18n } from "~/composables/use-i18n"

import VContentPage from "~/components/VContentPage.vue"
import VLink from "~/components/VLink.vue"

export default defineComponent({
  name: "ExternalSourcesPage",
  components: { VContentPage, VLink },
  layout: "content-layout",
  setup() {
    const i18n = useI18n()
    const featureFlagStore = useFeatureFlagStore()

    useMeta({
      title: `${i18n.t("external-sources-page.title")} | Openverse`,
      meta: featureFlagStore.isOn("new_header")
        ? [{ hid: "robots", name: "robots", content: "all" }]
        : undefined,
    })
  },
  head: {},
})
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
figure {
  @apply mx-auto max-w-full border border-black md:w-[800px];
}
</style>
