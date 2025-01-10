<script setup lang="ts">
import { useNuxtApp } from "#imports"

import type { SupportedMediaType } from "#shared/constants/media"
import useSearchType from "~/composables/use-search-type"
import { useHydrating } from "~/composables/use-hydrating"

import VButton from "~/components/VButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"

const props = defineProps<{
  mediaType: SupportedMediaType
  /**
   * The route target of the link.
   */
  to: string | undefined
  labels: {
    aria: string
    visible: string
  }
}>()

defineEmits<{
  "shift-tab": [KeyboardEvent]
}>()

const { activeType } = useSearchType({ component: "VContentLink" })
const { $sendCustomEvent } = useNuxtApp()

const handleClick = () => {
  $sendCustomEvent("CHANGE_CONTENT_TYPE", {
    previous: activeType.value,
    next: props.mediaType,
    component: "VContentLink",
  })
}

const { doneHydrating } = useHydrating()
</script>

<template>
  <VButton
    as="VLink"
    :href="to"
    :aria-label="labels.aria"
    variant="bordered-gray"
    size="disabled"
    :disabled="!doneHydrating"
    class="h-auto w-full flex-col !items-start !justify-start gap-1 overflow-hidden p-4 sm:h-18 sm:flex-row sm:!items-center sm:gap-2 sm:px-6"
    @keydown.shift.tab.exact="$emit('shift-tab', $event)"
    @mousedown="handleClick"
  >
    <VIcon :name="mediaType" />
    <p class="label-bold sm:description-bold mt-1 sm:mt-0">
      {{ $t(`searchType.${mediaType}`) }}
    </p>
    <span
      class="label-regular sm:description-regular text-secondary group-hover/button:text-default sm:ms-auto"
      >{{ labels.visible }}</span
    >
  </VButton>
</template>
