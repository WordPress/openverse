<template>
  <VContentPage>
    <h1>
      {{ $t("about.title", { openverse: "Openverse" }) }}
    </h1>
    <p>
      {{ $t("about.description.content", { openverse: "Openverse" }) }}
    </p>

    <i18n path="about.collection.content" tag="p">
      <template #openverse>Openverse</template>
      <template #common-crawl>
        <VLink href="https://commoncrawl.org/">Common Crawl</VLink>
      </template>
    </i18n>

    <i18n path="about.planning.content" tag="p">
      <template #openverse>Openverse</template>
      <template #frontend>
        <VLink href="https://github.com/wordpress/openverse-frontend/">{{
          $t("about.planning.frontend", { openverse: "Openverse" })
        }}</VLink>
      </template>
      <template #api>
        <VLink href="https://github.com/wordpress/openverse-api/">{{
          $t("about.planning.api", { openverse: "Openverse" })
        }}</VLink>
      </template>
      <template #catalog>
        <VLink href="https://github.com/wordpress/openverse-catalog/">{{
          $t("about.planning.catalog", { openverse: "Openverse" })
        }}</VLink>
      </template>
      <template #community>
        <VLink href="https://make.wordpress.org/openverse/">{{
          $t("about.planning.community")
        }}</VLink>
      </template>
      <template #working>
        <VLink href="https://github.com/orgs/WordPress/projects/3">{{
          $t("about.planning.working")
        }}</VLink>
      </template>
    </i18n>

    <i18n path="about.transfer.content" tag="p">
      <template #openverse>Openverse</template>
      <template #creative-commons>
        <VLink
          href="https://creativecommons.org/2021/05/03/cc-search-to-join-wordpress/"
          >Creative Commons</VLink
        >
      </template>
      <template #wordpress>
        <VLink href="https://ma.tt/2021/04/cc-search-to-join-wordpress-org/"
          >WordPress</VLink
        >
      </template>
    </i18n>

    <i18n path="about.declaration.content" tag="p">
      <template #openverse>Openverse</template>
      <template #terms>
        <VLink href="https://creativecommons.org/terms/">{{
          $t("about.declaration.terms", { openverse: "Openverse" })
        }}</VLink>
      </template>
    </i18n>

    <h2 id="external-sources">
      {{ $t("external-sources-page.title") }}
    </h2>

    <i18n path="external-sources-page.intro" tag="p">
      <template #openverse>Openverse</template>
      <template #link>
        <VLink href="/sources">{{ $t("external-sources-page.link") }}</VLink>
      </template>
    </i18n>
    <p>
      {{ $t("external-sources-page.license", { openverse: "Openverse" }) }}
    </p>
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

import VLink from "~/components/VLink.vue"
import VContentPage from "~/components/VContentPage.vue"

export default defineComponent({
  name: "AboutPage",
  components: { VLink, VContentPage },
  layout: "content-layout",
  setup() {
    const i18n = useI18n()
    const featureFlagStore = useFeatureFlagStore()

    useMeta({
      title: `${i18n.t("about.title", {
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
