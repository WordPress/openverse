<script setup lang="ts">
import type { Metadata } from "#shared/types/media"

import VLink from "~/components/VLink.vue"
import VIcon from "~/components/VIcon/VIcon.vue"

defineProps<{
  datum: Metadata
}>()

defineEmits<{
  click: [string | undefined]
}>()
</script>

<template>
  <dd class="flex justify-start overflow-hidden p-1 label-bold wrap-break-word">
    <VLink
      v-if="datum.url"
      :href="datum.url"
      class="flex text-link focus-visible:rounded-xs focus-visible:ring focus-visible:ring-focus focus-visible:ring-offset-1 focus-visible:outline-hidden"
      :send-external-link-click-event="false"
      @click="$emit('click', datum.source)"
      ><span
        >{{ datum.value
        }}<VIcon
          name="external-link"
          :size="4"
          class="ms-1 inline-flex"
          rtl-flip /></span
    ></VLink>
    <template v-else>{{ datum.value }}</template>
  </dd>
</template>
