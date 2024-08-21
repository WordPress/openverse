<script setup lang="ts">
import { useI18n } from "#imports"

import { computed } from "vue"

import { Metadata } from "~/types/media"

import VTooltip from "~/components/VTooltip/VTooltip.vue"

const props = defineProps<{
  datum: Metadata
  describedBy: string
}>()

const { t } = useI18n({ useScope: "global" })
const description = computed(() => {
  if (!props.datum.name) {
    return ""
  }
  return t(
    props.datum.name === "source"
      ? "mediaDetails.sourceDescription"
      : "mediaDetails.providerDescription"
  )
})
</script>

<template>
  <dt>
    {{ $t(datum.label) }}
    <VTooltip placement="top" :described-by="describedBy" class="ms-1">
      <template #default>
        <p
          class="caption-regular rounded-sm bg-tertiary px-2 py-1 text-over-dark"
        >
          {{ description }}
        </p>
      </template>
    </VTooltip>
  </dt>
</template>
