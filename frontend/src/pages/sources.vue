<script setup lang="ts">
import { definePageMeta, useHead, useNuxtApp } from "#imports"

import { supportedMediaTypes } from "#shared/constants/media"

import VButton from "~/components/VButton.vue"
import VLink from "~/components/VLink.vue"
import VContentPage from "~/components/VContentPage.vue"
import VSourcesTable from "~/components/VSourcesTable.vue"

defineOptions({
  name: "SourcesPage",
})

definePageMeta({
  layout: "content-layout",
})

const {
  $i18n: { t },
} = useNuxtApp()

useHead({ title: `${t("sources.title")} | Openverse` })
</script>

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
      <i18n-t scope="global" keypath="sources.ccContent.provider.a" tag="span">
        <template #flickr>
          <VLink href="https://www.flickr.com/">Flickr</VLink>
        </template>
        <template #smithsonian>
          <VLink href="https://www.si.edu/">Smithsonian Institute</VLink>
        </template>
      </i18n-t>
      {{ " " }}
      <i18n-t
        scope="global"
        keypath="sources.ccContent.provider.b"
        tag="span"
      ></i18n-t>
    </p>

    <i18n-t scope="global" keypath="sources.ccContent.europeana" tag="p">
      <template #link>
        <VLink href="https://www.europeana.eu/en">Europeana</VLink>
      </template>
      <template #linkApi>
        <VLink href="https://pro.europeana.eu/page/apis"> Europeana API </VLink>
      </template>
    </i18n-t>

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
        variant="filled-pink-8"
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

    <i18n-t scope="global" keypath="sources.detail" tag="p">
      <template #singleName>
        <strong>
          {{ $t("sources.singleName") }}
        </strong>
      </template>
    </i18n-t>
    <template v-for="(mediaType, i) in supportedMediaTypes" :key="mediaType">
      <h3>{{ $t(`sources.heading.${mediaType}`) }}</h3>
      <VSourcesTable
        :media="mediaType"
        class="mt-4"
        :class="i < supportedMediaTypes.length - 1 ? 'mb-10' : ''"
      />
    </template>
  </VContentPage>
</template>
