<template>
  <div class="relative max-w-[280px]" data-testid="source-list-popover">
    <h2 class="description-bold mb-2 px-4 pt-5 text-start">
      {{ $t("external-sources.title") }}
    </h2>
    <VCloseButton
      :label="$t('modal.close')"
      class="!absolute end-0 top-0"
      @close="$emit('close')"
    />
    <p class="caption-regular mb-4 px-4 text-start">
      {{ $t("external-sources.caption", { openverse: "Openverse" }) }}
    </p>
    <VButton
      v-for="source in externalSources"
      :key="source.name"
      as="VLink"
      variant="plain"
      size="disabled"
      class="caption-bold !w-full justify-between px-4 py-3 text-dark-charcoal hover:bg-dark-charcoal-10"
      show-external-icon
      :external-icon-size="4"
      :href="source.url"
      @mousedown="handleClick(source.name, source.url)"
    >
      {{ source.name }}
    </VButton>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import { useAnalytics } from "~/composables/use-analytics"
import type { ExternalSource } from "~/types/external-source"

import type { MediaType } from "~/constants/media"

import VButton from "~/components/VButton.vue"
import VCloseButton from "~/components/VCloseButton.vue"

/**
 * This component renders a list of pre-populated links to additional sources
 * when there are insufficient or zero search results.
 */
export default defineComponent({
  name: "VExternalSourceList",
  components: { VCloseButton, VButton },
  props: {
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
    /**
     * The list of external sources information: their name and url.
     */
    externalSources: {
      type: Array as PropType<ExternalSource[]>,
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
        component: "VExternalSourceList",
      })
    }

    return {
      handleClick,
    }
  },
})
</script>
