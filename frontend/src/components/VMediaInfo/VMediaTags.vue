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
import { computed, defineComponent, type PropType } from "vue"
import { useRoute } from "@nuxtjs/composition-api"

import { useFeatureFlagStore } from "~/stores/feature-flag"
import type { Tag } from "~/types/media"
import type { SupportedMediaType } from "~/constants/media"

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
    mediaType: {
      type: String as PropType<SupportedMediaType>,
      required: true,
    },
  },
  setup(props) {
    const route = useRoute()
    const featureFlagStore = useFeatureFlagStore()

    const additionalSearchViews = computed(() =>
      featureFlagStore.isOn("additional_search_views")
    )

    const localizedTagPath = (tag: Tag) => {
      // Not using `localePath` because it decodes the path and converts `%2F` to `/`.
      const localePrefix = route.value.fullPath.split(`/${props.mediaType}/`)[0]
      return `${localePrefix}/${props.mediaType}/tag/${encodeURIComponent(
        tag.name
      )}`
    }

    return { additionalSearchViews, localizedTagPath }
  },
})
</script>
