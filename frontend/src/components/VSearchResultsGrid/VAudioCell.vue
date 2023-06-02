<template>
  <li>
    <VAudioTrack
      :audio="audio"
      layout="box"
      :search-term="searchTerm"
      v-bind="$attrs"
      v-on="$listeners"
    />
  </li>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import type { AudioDetail } from "~/types/media"

import VAudioTrack from "~/components/VAudioTrack/VAudioTrack.vue"

export default defineComponent({
  components: { VAudioTrack },
  inheritAttrs: false,
  props: {
    audio: {
      type: Object as PropType<AudioDetail>,
      required: true,
    },
    searchTerm: {
      type: String,
      required: true,
    },
  },
})
</script>
