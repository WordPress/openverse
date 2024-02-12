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
      <template #commonCrawl>
        <VLink href="https://commoncrawl.org/">Common Crawl</VLink>
      </template>
    </i18n>

    <i18n path="about.planning.content" tag="p">
      <template #openverse>Openverse</template>
      <template #repository>
        <VLink href="https://github.com/wordpress/openverse">{{
          $t("about.planning.repository", {
            openverse: "Openverse",
            github: "GitHub",
          })
        }}</VLink>
      </template>
      <template #community>
        <VLink href="https://docs.openverse.org/general/contributing">{{
          $t("about.planning.community")
        }}</VLink>
      </template>
      <template #working>
        <VLink href="https://github.com/orgs/WordPress/projects/75">{{
          $t("about.planning.working")
        }}</VLink>
      </template>
    </i18n>

    <i18n path="about.transfer.content" tag="p">
      <template #openverse>Openverse</template>
      <template #creativeCommons>
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
      {{ $t("externalSourcesPage.title") }}
    </h2>

    <i18n path="externalSourcesPage.intro" tag="p">
      <template #openverse>Openverse</template>
      <template #link>
        <VLink href="/sources">{{ $t("externalSourcesPage.link") }}</VLink>
      </template>
    </i18n>
    <p>
      {{ $t("externalSourcesPage.license", { openverse: "Openverse" }) }}
    </p>
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
          href="https://github.com/WordPress/openverse/issues"
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

import VLink from "~/components/VLink.vue"
import VContentPage from "~/components/VContentPage.vue"

export default defineComponent({
  name: "AboutPage",
  components: { VLink, VContentPage },
  layout: "content-layout",
  setup() {
    const i18n = useI18n()

    useMeta({
      title: `${i18n.t("about.title", {
        openverse: "Openverse",
      })} | Openverse`,
      meta: [{ hid: "robots", name: "robots", content: "all" }],
    })
  },
  head: {},
})
</script>
