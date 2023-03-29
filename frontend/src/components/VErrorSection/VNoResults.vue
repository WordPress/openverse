<template>
  <div class="no-results text-center md:text-left">
    <h1 class="heading-4 md:heading-2 break-words">
      {{ $t("no-results.heading", { query: searchTerm }) }}
    </h1>
    <h2 class="description-regular md:heading-5 mt-4">
      {{ $t("no-results.alternatives") }}
    </h2>

    <div class="mt-10 flex flex-col flex-wrap gap-2 gap-4 md:flex-row">
      <VButton
        v-for="source in externalSources"
        :key="source.name"
        as="VLink"
        :href="source.url"
        variant="secondary-bordered"
        class="label-bold justify-between text-dark-charcoal md:justify-start md:gap-x-2"
      >
        {{ source.name }}
        <VIcon :icon-path="externalLinkIcon" :size="4" rtl-flip />
      </VButton>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import type { ExternalSource } from "~/types/external-source"

import VButton from "~/components/VButton.vue"

import VIcon from "~/components/VIcon/VIcon.vue"

import externalLinkIcon from "~/assets/icons/external-link.svg"

export default defineComponent({
  name: "VNoResults",
  components: { VIcon, VButton },
  props: {
    externalSources: {
      type: Array as PropType<ExternalSource[]>,
      required: true,
    },
    searchTerm: {
      type: String,
      required: true,
    },
  },
  setup() {
    return {
      externalLinkIcon,
    }
  },
})
</script>
