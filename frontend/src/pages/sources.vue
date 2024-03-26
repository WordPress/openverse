<template>
  <VContentPage>
    <h1>
      {{ $t("sources.title") }}
    </h1>

    <h2>
      {{ $t("sources.ccContent.where", { openverse: "Openverse" }) }}
    </h2>
    <p>
      {{ $t("sources.ccContent.content", { openverse: "Openverse" }) }}
    </p>
    <p>
      <i18n path="sources.ccContent.provider.a" tag="span">
        <template #flickr>
          <VLink href="https://www.flickr.com/">Flickr</VLink>
        </template>
        <template #smithsonian>
          <VLink href="https://www.si.edu/">Smithsonian Institute</VLink>
        </template>
      </i18n>
      <i18n path="sources.ccContent.provider.b" tag="span"></i18n>
    </p>

    <i18n path="sources.ccContent.europeana" tag="p">
      <template #openverse>Openverse</template>
      <template #link>
        <VLink href="https://www.europeana.eu/en">Europeana</VLink>
      </template>
      <template #linkApi>
        <VLink href="https://pro.europeana.eu/page/apis"> Europeana API </VLink>
      </template>
    </i18n>

    <h2>
      {{ $t("sources.newContent.next") }}
    </h2>
    <p>
      {{ $t("sources.newContent.integrate") }}
    </p>
    <ul>
      <li>
        {{ $t("sources.newContent.impact") }}
      </li>
      <li>
        {{ $t("sources.newContent.reuse") }}
      </li>
      <li>
        {{ $t("sources.newContent.totalItems") }}
      </li>
    </ul>

    <h2>
      {{ $t("sources.suggestions") }}
    </h2>

    <p class="mt-5 inline-block">
      <VButton
        as="VLink"
        variant="filled-pink"
        size="large"
        class="not-prose description-bold"
        show-external-icon
        :external-icon-size="6"
        has-icon-end
        href="https://github.com/WordPress/openverse/issues/new?assignees=&labels=%F0%9F%9A%A6+status%3A+awaiting+triage%2C+%F0%9F%A7%B9+status%3A+ticket+work+required%2C+%E2%98%81%EF%B8%8F+provider%3A+any&template=new-source-suggestion.md&title=[Source+Suggestion]+Insert+source+name+here"
      >
        {{ $t("sources.issueButton") }}
      </VButton>
    </p>

    <i18n path="sources.detail" tag="p">
      <template #singleName>
        <strong>
          {{ $t("sources.singleName") }}
        </strong>
      </template>
    </i18n>
    <template v-for="(mediaType, i) in supportedMediaTypes">
      <h3 :key="`h3-${mediaType}`">{{ $t(`sources.heading.${mediaType}`) }}</h3>
      <VSourcesTable
        :key="`table-${mediaType}`"
        :media="mediaType"
        class="mt-4"
        :class="i < supportedMediaTypes.length - 1 ? 'mb-10' : ''"
      />
    </template>
  </VContentPage>
</template>

<script lang="ts">
import { defineComponent, useMeta } from "@nuxtjs/composition-api"

import { supportedMediaTypes } from "~/constants/media"
import { useI18n } from "~/composables/use-i18n"

import VButton from "~/components/VButton.vue"
import VLink from "~/components/VLink.vue"
import VContentPage from "~/components/VContentPage.vue"
import VSourcesTable from "~/components/VSourcesTable.vue"

export default defineComponent({
  name: "SourcePage",
  components: { VButton, VContentPage, VLink, VSourcesTable },
  layout: "content-layout",
  setup() {
    const i18n = useI18n()

    useMeta({
      title: `${i18n.t("sources.title")} | Openverse`,
      meta: [{ hid: "robots", name: "robots", content: "all" }],
    })

    return { supportedMediaTypes }
  },
  head: {},
})
</script>
