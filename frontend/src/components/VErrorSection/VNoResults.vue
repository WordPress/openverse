<template>
  <div class="no-results text-center md:text-left">
    <h1 class="heading-4 md:heading-2 break-words">
      {{ t("noResults.heading", { query: searchTerm }) }}
    </h1>
    <h2 class="description-regular md:heading-5 mt-4">
      {{ t("noResults.alternatives") }}
    </h2>

    <div class="mt-10 flex flex-col flex-wrap gap-4 sm:flex-row">
      <VButton
        v-for="source in externalSources"
        :key="source.name"
        as="VLink"
        :href="source.url"
        variant="bordered-gray"
        size="medium"
        class="label-bold !w-full text-dark-charcoal sm:!w-auto"
        show-external-icon
        has-icon-end
        :external-icon-size="6"
        @mousedown="handleClick(source.name)"
      >
        {{ source.name }}
      </VButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useNuxtApp } from "#imports"

import { onMounted } from "vue"

import { useAnalytics } from "~/composables/use-analytics"
import { useExternalSources } from "~/composables/use-external-sources"
import { useUiStore } from "~/stores/ui"

import VButton from "~/components/VButton.vue"

const props = defineProps<{
  /**
   * The search term for which the external sources links are generated.
   */
  searchTerm: string
}>()

const {
  $i18n: { t },
} = useNuxtApp()

const { externalSources, externalSourcesType } = useExternalSources()
const { sendCustomEvent } = useAnalytics()
const handleClick = (sourceName: string) => {
  sendCustomEvent("SELECT_EXTERNAL_SOURCE", {
    name: sourceName,
    mediaType: externalSourcesType.value,
    query: props.searchTerm,
    component: "VNoResults",
  })
}

onMounted(() => {
  const uiStore = useUiStore()
  uiStore.setFiltersState(false)
})
</script>
