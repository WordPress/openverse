<template>
  <div class="relative max-w-[280px]" data-testid="source-list-popover">
    <h2 class="description-bold mb-2 px-4 pt-5 text-start">
      {{ $t("externalSources.title") }}
    </h2>
    <VCloseButton
      :label="$t('modal.close')"
      class="!absolute end-0 top-0"
      @close="$emit('close')"
    />
    <p class="caption-regular mb-4 px-4 text-start">
      {{ $t("externalSources.caption", { openverse: "Openverse" }) }}
    </p>
    <VButton
      v-for="source in externalSources"
      :key="source.name"
      as="VLink"
      variant="transparent-tx"
      size="disabled"
      class="caption-bold !w-full justify-between px-4 py-3 text-dark-charcoal hover:bg-dark-charcoal-10"
      show-external-icon
      :external-icon-size="4"
      :href="source.url"
      @mousedown="handleClick(source.name)"
    >
      {{ source.name }}
    </VButton>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue"

import { useAnalytics } from "~/composables/use-analytics"

import { useExternalSources } from "~/composables/use-external-sources"

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
     * The search term for which the external sources links are generated.
     */
    searchTerm: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const { externalSources, externalSourcesType } = useExternalSources()

    const { sendCustomEvent } = useAnalytics()
    const handleClick = (sourceName: string) => {
      sendCustomEvent("SELECT_EXTERNAL_SOURCE", {
        name: sourceName,
        mediaType: externalSourcesType.value,
        query: props.searchTerm,
        component: "VExternalSourceList",
      })
    }

    return {
      externalSources,
      externalSourcesType,
      handleClick,
    }
  },
})
</script>
