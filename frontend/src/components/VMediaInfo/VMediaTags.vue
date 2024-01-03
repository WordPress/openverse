<template>
  <ul v-if="tags.length && additionalSearchViews" class="flex flex-wrap gap-3">
    <VTag
      v-for="(tag, index) in tags"
      :key="index"
      :href="localizedTagPath(tag)"
      :title="tag.name"
    />
  </ul>
  <ul v-else class="flex flex-wrap gap-2">
    <VMediaTag v-for="(tag, index) in tags" :key="index" tag="li">{{
      tag.name
    }}</VMediaTag>
  </ul>
</template>
<script lang="ts">
import { useLocalePath, useRoute } from "#imports"

import { computed, defineComponent, PropType } from "vue"

import type { Tag } from "~/types/media"
import { useFeatureFlagStore } from "~/stores/feature-flag"

import VMediaTag from "~/components/VMediaTag/VMediaTag.vue"
import VTag from "~/components/VTag/VTag.vue"

export default defineComponent({
  name: "VMediaTags",
  components: { VMediaTag, VTag },
  props: {
    tags: {
      type: Array as PropType<Tag[]>,
      required: true,
    },
  },
  setup() {
    const route = useRoute()
    const localePath = useLocalePath()
    const featureFlagStore = useFeatureFlagStore()

    const additionalSearchViews = computed(() =>
      featureFlagStore.isOn("additional_search_views")
    )

    const localizedTagPath = (tag: Tag) => {
      // TODO: replace with a prop
      const mediaType = route.path.includes("/image/") ? "image" : "audio"
      return localePath(`/${mediaType}/tag/${tag.name}`)
    }

    return { additionalSearchViews, localizedTagPath }
  },
})
</script>
