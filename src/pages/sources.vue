<template>
  <VContentPage>
    <h1>
      {{ $t('sources.title') }}
    </h1>

    <h3>
      {{ $t('sources.cc-content.where', { openverse: 'Openverse' }) }}
    </h3>
    <p>
      {{ $t('sources.cc-content.content', { openverse: 'Openverse' }) }}
    </p>
    <i18n path="sources.cc-content.provider" tag="p">
      <template #flickr>
        <VLink href="https://www.flickr.com/">Flickr</VLink>
      </template>
      <template #smithsonian>
        <VLink href="https://www.si.edu/">{{
          $t('sources.cc-content.smithsonian')
        }}</VLink>
      </template>
    </i18n>
    <i18n path="sources.cc-content.europeana" tag="p">
      <template #openverse>Openverse</template>
      <template #link>
        <VLink href="https://www.europeana.eu/en">Europeana</VLink>
      </template>
      <template #link-api>
        <VLink href="https://pro.europeana.eu/page/apis">{{
          $t('sources.cc-content.europeana-api')
        }}</VLink>
      </template>
    </i18n>

    <h3>
      {{ $t('sources.new-content.next') }}
    </h3>
    <p>
      {{ $t('sources.new-content.integrate') }}
    </p>
    <ul>
      <li>
        {{ $t('sources.new-content.impact') }}
      </li>
      <li>
        {{ $t('sources.new-content.reuse') }}
      </li>
      <li>
        {{ $t('sources.new-content.total-items') }}
      </li>
    </ul>

    <h3>
      {{ $t('sources.suggestions') }}
    </h3>

    <p class="inline-block">
      <VButton
        as="VLink"
        variant="primary"
        size="disabled"
        class="not-prose font-semibold mt-5 px-6 py-4"
        href="https://github.com/WordPress/openverse-catalog/issues/new?assignees=&labels=%F0%9F%9A%A6+status%3A+awaiting+triage%2C+%F0%9F%A7%B9+status%3A+ticket+work+required%2C+%E2%98%81%EF%B8%8F+provider%3A+any&template=new-source-suggestion.md&title=%5BSource+Suggestion%5D+Insert+source+name+here"
      >
        {{ $t('sources.issue-button') }}
        <VIcon :icon-path="externalLinkIcon" :rtl-flip="true" class="mx-2" />
      </VButton>
    </p>

    <i18n path="sources.detail" tag="p">
      <template #single-name>
        <strong>
          {{ $t('sources.single-name') }}
        </strong>
      </template>
    </i18n>
    <template v-for="mediaType in supportedMediaTypes">
      <h3 :key="mediaType">{{ $t(`sources.heading.${mediaType}`) }}</h3>
      <VSourcesTable :key="mediaType" :media="mediaType" />
    </template>
  </VContentPage>
</template>

<script lang="ts">
import { defineComponent } from '@nuxtjs/composition-api'

import { supportedMediaTypes } from '~/constants/media'

import VButton from '~/components/VButton.vue'
import VLink from '~/components/VLink.vue'
import VIcon from '~/components/VIcon/VIcon.vue'
import VContentPage from '~/components/VContentPage.vue'
import VSourcesTable from '~/components/VSourcesTable.vue'

import externalLinkIcon from '~/assets/icons/external-link.svg'

export default defineComponent({
  name: 'SourcePage',
  components: { VButton, VContentPage, VIcon, VLink, VSourcesTable },
  setup() {
    return { externalLinkIcon, supportedMediaTypes }
  },

  head() {
    return {
      title: `${this.$t('sources.title')} | Openverse`,
    }
  },
})
</script>
