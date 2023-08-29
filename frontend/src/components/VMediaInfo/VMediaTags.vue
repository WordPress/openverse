<template>
  <ul v-if="tags.length" class="flex flex-wrap gap-2">
    <VMediaTag v-for="(tag, index) in tags" :key="index" tag="li">{{
      tag.name
    }}</VMediaTag>
  </ul>
</template>
<script lang="ts">
import { defineComponent, PropType } from "vue"

import type { Tag } from "~/types/media"

import VMediaTag from "~/components/VMediaTag/VMediaTag.vue"

export default defineComponent({
  name: "VMediaTags",
  components: { VMediaTag },
  props: {
    tags: {
      type: Array as PropType<Tag[]>,
      required: true,
    },
  },
})
</script>
