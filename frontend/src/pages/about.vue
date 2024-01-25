<template>
  <VContentPage>
    <h1>
      {{ $t("about.title", { openverse: "Openverse" }) }}
    </h1>
    <p>
      {{ $t("about.description.content", { openverse: "Openverse" }) }}
    </p>

    <i18n-t scope="global" keypath="about.collection.content" tag="p">
      <template #openverse>Openverse</template>
      <template #commonCrawl>
        <VLink href="https://commoncrawl.org/">Common Crawl</VLink>
      </template>
    </i18n-t>

    <i18n-t scope="global" keypath="about.planning.content" tag="p">
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
    </i18n-t>

    <i18n-t scope="global" keypath="about.transfer.content" tag="p">
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
    </i18n-t>

    <i18n-t scope="global" keypath="about.declaration.content" tag="p">
      <template #openverse>Openverse</template>
      <template #terms>
        <VLink href="https://creativecommons.org/terms/">{{
          $t("about.declaration.terms", { openverse: "Openverse" })
        }}</VLink>
      </template>
    </i18n-t>

    <h2 id="external-sources">
      {{ $t("externalSourcesPage.title") }}
    </h2>

    <i18n-t scope="global" keypath="externalSourcesPage.intro" tag="p">
      <template #openverse>Openverse</template>
      <template #link>
        <VLink href="/sources">{{ $t("externalSourcesPage.link") }}</VLink>
      </template>
    </i18n-t>
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
    <i18n-t scope="global" keypath="externalSourcesPage.new.content" tag="p">
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
    </i18n-t>
    <h2>
      {{ $t("externalSourcesPage.why.title") }}
    </h2>
    <i18n-t scope="global" keypath="externalSourcesPage.why.content" tag="p">
      <template #old>
        <VLink
          aria-label="email"
          href="https://oldsearch.creativecommons.org"
          >{{ $t("externalSourcesPage.why.old") }}</VLink
        >
      </template>
    </i18n-t>

    <p>
      {{ $t("externalSourcesPage.why.new", { openverse: "Openverse" }) }}
    </p>
    <i18n-t
      scope="global"
      keypath="externalSourcesPage.why.feedbackSuggestions"
      tag="p"
    >
      <template #feedback>
        <VLink
          :aria-label="$t('externalSourcesPage.why.ariaLabel')"
          href="/feedback"
          >{{ $t("externalSourcesPage.why.feedbackLink") }}</VLink
        >
      </template>
    </i18n-t>
  </VContentPage>
</template>

<script setup lang="ts">
import { definePageMeta } from "#imports"

import VLink from "~/components/VLink.vue"
import VContentPage from "~/components/VContentPage.vue"

definePageMeta({
  layout: "content-layout",
})
</script>
