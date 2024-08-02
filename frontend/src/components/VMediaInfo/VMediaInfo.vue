<template>
  <div class="w-full lg:w-auto">
    <h1 class="heading-6 mb-3 sm:mb-1">{{ media.title }}</h1>
    <VByLine :media="media" />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue"

import type { Media } from "~/types/media"

import VByLine from "~/components/VMediaInfo/VByLine/VByLine.vue"

import type { PropType } from "vue"

export default defineComponent({
  name: "VMediaInfo",
  components: { VByLine },
  props: {
    media: {
      type: Object as PropType<Media>,
      required: true,
    },
  },
})
</script>
