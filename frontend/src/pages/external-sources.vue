<template>
  <VContentPage>
    <h1>
      {{ $t("externalSourcesPage.title") }}
    </h1>

    <i18n path="externalSourcesPage.intro" tag="p">
      <template #openverse>Openverse</template>
      <template #link>
        <VLink href="/sources">{{ $t("externalSourcesPage.link") }}</VLink>
      </template>
    </i18n>
    <p>{{ $t("externalSourcesPage.license", { openverse: "Openverse" }) }}</p>
    <p>
      {{ $t("externalSourcesPage.explanation", { openverse: "Openverse" }) }}
    </p>
    <p>
      {{ $t("externalSourcesPage.relationships", { openverse: "Openverse" }) }}
    </p>
    <h2>
      {{ $t("externalSourcesPage.new.title") }}
    </h2>
    <i18n path="externalSourcesPage.new.content" tag="p">
      <template #issue>
        <VLink
          aria-label="issue"
          href="https://github.com/WordPress/openverse/issues/new?assignees=&labels=%F0%9F%9A%A6+status%3A+awaiting+triage%2C%F0%9F%A7%B9+status%3A+ticket+work+required%2C%E2%98%81%EF%B8%8F+provider%3A+any&template=new_source_suggestion.yml&title=%3CSource+name+here%3E"
          >{{ $t("externalSourcesPage.new.issue") }}</VLink
        >
      </template>
      <template #email>
        <VLink aria-label="email" href="mailto:openverse@wordpress.org">{{
          $t("externalSourcesPage.new.email")
        }}</VLink>
      </template>
    </i18n>
    <h2>
      {{ $t("externalSourcesPage.why.title") }}
    </h2>
    <i18n path="externalSourcesPage.why.content" tag="p">
      <template #old>
        <VLink
          aria-label="email"
          href="https://oldsearch.creativecommons.org"
          >{{ $t("externalSourcesPage.why.old") }}</VLink
        >
      </template>
    </i18n>

    <p>
      {{ $t("externalSourcesPage.why.new", { openverse: "Openverse" }) }}
    </p>
    <i18n path="externalSourcesPage.why.feedbackSuggestions" tag="p">
      <template #feedback>
        <VLink
          :aria-label="$t('externalSourcesPage.why.ariaLabel')"
          href="/feedback"
          >{{ $t("externalSourcesPage.why.feedbackLink") }}</VLink
        >
      </template>
    </i18n>
  </VContentPage>
</template>
<script lang="ts">
import { defineComponent, useMeta } from "@nuxtjs/composition-api"

import { useI18n } from "~/composables/use-i18n"

import VContentPage from "~/components/VContentPage.vue"
import VLink from "~/components/VLink.vue"

export default defineComponent({
  name: "ExternalSourcesPage",
  components: { VContentPage, VLink },
  layout: "content-layout",
  setup() {
    const i18n = useI18n()

    useMeta({
      title: `${i18n.t("externalSourcesPage.title")} | Openverse`,
      meta: [{ hid: "robots", name: "robots", content: "all" }],
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
