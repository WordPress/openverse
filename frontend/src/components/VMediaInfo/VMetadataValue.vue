<template>
  <dd class="label-bold overflow-hidden break-words">
    <VLink
      v-if="datum.url"
      :href="datum.url"
      class="text-pink"
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
}
</script>
