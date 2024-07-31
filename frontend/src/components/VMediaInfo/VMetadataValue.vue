<template>
  <dd class="label-bold flex justify-start overflow-hidden break-words p-1">
    <VLink
      v-if="datum.url"
      :href="datum.url"
      class="text-text-link focus-visible:ring-pink-8 flex focus-visible:rounded-sm focus-visible:outline-none focus-visible:ring focus-visible:ring-offset-1"
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
<script lang="ts">
import type { Metadata } from "~/types/media"

import { defineEvent } from "~/types/emits"

import VLink from "~/components/VLink.vue"

import VIcon from "~/components/VIcon/VIcon.vue"

import type { PropType } from "vue"

export default {
  name: "VMetadataValue",
  components: { VIcon, VLink },
  props: {
    datum: {
      type: Object as PropType<Metadata>,
      required: true,
    },
  },
  emits: {
    click: defineEvent<[string | undefined]>(),
  },
}
</script>
