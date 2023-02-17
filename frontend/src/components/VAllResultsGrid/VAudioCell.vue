<template>
  <VAudioTrack
    :audio="audio"
    layout="box"
    :search-term="searchTerm"
    v-on="$listeners"
  />
</template>

<script lang="ts">
import { defineComponent, PropType } from "@nuxtjs/composition-api"

import type { AudioDetail } from "~/types/media"

import VAudioTrack from "~/components/VAudioTrack/VAudioTrack.vue"

export default defineComponent({
  components: { VAudioTrack },
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
