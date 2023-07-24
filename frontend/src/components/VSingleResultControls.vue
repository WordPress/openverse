<template>
  <div class="flex w-full justify-between px-4 pb-4 md:px-6">
    <VBackToSearchResultsLink
      v-if="backToSearchPath"
      :id="$route.params.id"
      :href="backToSearchPath"
    />
    <VHideButton v-if="canBeHidden" class="ml-auto" @click="hide" />
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import { useSensitiveMedia } from "~/composables/use-sensitive-media"

import type { AudioDetail, ImageDetail } from "~/types/media"

import { useSearchStore } from "~/stores/search"

import VBackToSearchResultsLink from "~/components/VBackToSearchResultsLink.vue"
import VHideButton from "~/components/VHideButton.vue"

export default defineComponent({
  name: "VSingleResultControls",
  components: {
    VBackToSearchResultsLink,
    VHideButton,
  },
  props: {
    media: {
      type: Object as PropType<AudioDetail | ImageDetail>,
      required: true,
    },
  },
  setup(props) {
    const searchStore = useSearchStore()

    const backToSearchPath = computed(() => searchStore.backToSearchPath)
    const { hide, canBeHidden } = useSensitiveMedia(props.media)

    return {
      hide,
      canBeHidden,
      backToSearchPath,
    }
  },
})
</script>
