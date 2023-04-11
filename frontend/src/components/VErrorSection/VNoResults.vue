<template>
  <div class="no-results text-center md:text-left">
    <h1 class="heading-4 md:heading-2 break-words">
      {{ $t("no-results.heading", { query: searchTerm }) }}
    </h1>
    <h2 class="description-regular md:heading-5 mt-4">
      {{ $t("no-results.alternatives") }}
    </h2>

    <div class="mt-10 flex flex-col flex-wrap gap-4 md:flex-row">
      <VButton
        v-for="source in externalSources"
        :key="source.name"
        as="VLink"
        :href="source.url"
        variant="secondary-bordered"
        class="label-bold justify-between text-dark-charcoal md:justify-start md:gap-x-2"
        show-external-icon
        :external-icon-size="4"
        @mousedown="handleClick(source.name, source.url)"
      >
        {{ source.name }}
      </VButton>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import { useAnalytics } from "~/composables/use-analytics"

import type { ExternalSource } from "~/types/external-source"

import type { MediaType } from "~/constants/media"

import VButton from "~/components/VButton.vue"

export default defineComponent({
  name: "VNoResults",
  components: { VButton },
  props: {
    /**
     * The list of external sources information: their name and url.
     */
    externalSources: {
      type: Array as PropType<ExternalSource[]>,
      required: true,
    },
    /**
     * The media type to use as the criteria for filtering additional sources
     */
    mediaType: {
      type: String as PropType<MediaType>,
      required: true,
    },
    /**
     * The search term for which the external sources links are generated.
     */
    searchTerm: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const { sendCustomEvent } = useAnalytics()
    const handleClick = (sourceName: string, sourceUrl: string) => {
      sendCustomEvent("SELECT_EXTERNAL_SOURCE", {
        name: sourceName,
        url: sourceUrl,
        mediaType: props.mediaType,
        query: props.searchTerm,
        component: "VNoResults",
      })
    }

    return {
      handleClick,
    }
  },
})
</script>
