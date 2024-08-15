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

<template>
  <!-- Only display these controls if one of the children is shown,
    to prevent rendering extra whitespace when both buttons are hidden. -->
  <div
    v-show="canBeHidden || backToSearchPath"
    class="flex w-full justify-between px-4 pb-4 md:px-8"
  >
    <VBackToSearchResultsLink
      v-if="backToSearchPath"
      :id="media.id"
      :href="backToSearchPath"
    />
    <VHideButton v-if="canBeHidden" class="ml-auto" @click="hide" />
  </div>
</template>
