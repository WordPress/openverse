<template>
  <div class="w-full lg:w-auto">
    <h1 class="heading-6 mb-3 sm:mb-1">{{ media.title }}</h1>
    <VByLine
      :media-type="media.frontendMediaType"
      :source-slug="source"
      :source-name="sourceName"
      :creator="media.creator"
    />
  </div>
</template>
<script lang="ts">
import { computed, defineComponent } from "vue"

import { Media } from "~/types/media"
import { useProviderStore } from "~/stores/provider"

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
  setup(props) {
    const source = computed(() => {
      return props.media.source ?? props.media.provider
    })

    const providerStore = useProviderStore()
    const sourceName = computed(() => {
      return providerStore.getProviderName(
        source.value,
        props.media.frontendMediaType
      )
    })
    return { source, sourceName }
  },
})
</script>
