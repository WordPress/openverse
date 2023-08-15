<template>
  <ul v-if="filteredTags.length" class="flex flex-wrap gap-2">
    <VMediaTag v-for="(tag, index) in filteredTags" :key="index" tag="li">{{
      tag.name
    }}</VMediaTag>
  </ul>
</template>
<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import VMediaTag from "~/components/VMediaTag/VMediaTag.vue"

export default defineComponent({
  name: "VMediaTags",
  components: { VMediaTag },
  props: {
    tags: {
      type: Array as PropType<{ name: string }[]>,
      required: true,
    },
  },
  setup(props) {
    const filteredTags = computed(() => {
      return props.tags.filter((i: { name: string }) => !!i)
    })
    return {
      filteredTags,
    }
  },
})
</script>
