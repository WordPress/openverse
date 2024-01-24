<template>
  <ul
    v-if="tagNames.length && additionalSearchViews"
    class="flex flex-wrap gap-3"
  >
    <VTag
      v-for="tag in tagNames"
      :key="tag"
      :href="localizedTagPath(tag)"
      :title="tag"
    />
  </ul>
  <ul v-else class="flex flex-wrap gap-2">
    <VMediaTag v-for="tag in tagNames" :key="tag" tag="li">{{ tag }}</VMediaTag>
  </ul>
</template>
<script lang="ts">
import { useNuxtApp } from "#imports"

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
  setup(props) {
    const localePath = useNuxtApp().$localePath
    const featureFlagStore = useFeatureFlagStore()

    const additionalSearchViews = computed(() =>
      featureFlagStore.isOn("additional_search_views")
    )

    const localizedTagPath = (tag: string) => {
      return localePath({ path: `tag/${tag}` })
    }
    const tagNames = computed<string[]>(() => {
      return Array.from(new Set(props.tags.map((tag) => tag.name)))
    })

    return { additionalSearchViews, localizedTagPath, tagNames }
  },
})
</script>
