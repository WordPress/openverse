<template>
  <VButton
    type="button"
    variant="secondary-bordered"
    size="disabled"
    class="caption-bold h-10 py-2 ps-2 pe-3"
    :aria-pressed="selected"
    @click="handleClick"
  >
    <VIcon :icon-path="iconPath" class="flex-shrink-0 me-1" />
    <span>{{ $t(labelMapping[searchType]) }}</span>
  </VButton>
</template>

<script lang="ts">
import { computed, defineComponent, type PropType } from "vue"

import {
  ALL_MEDIA,
  AUDIO,
  IMAGE,
  type SupportedSearchType,
} from "~/constants/media"
import { defineEvent } from "~/types/emits"

import VButton from "~/components/VButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"

import audioIcon from "~/assets/icons/audio-wave.svg"
import imageIcon from "~/assets/icons/image.svg"
import allIcon from "~/assets/icons/all-content.svg"

const iconMapping = {
  [AUDIO]: audioIcon,
  [IMAGE]: imageIcon,
  [ALL_MEDIA]: allIcon,
}
const labelMapping = {
  [AUDIO]: "search-type.audio",
  [IMAGE]: "search-type.image",
  [ALL_MEDIA]: "search-type.all",
}

export default defineComponent({
  name: "VSearchTypeRadio",
  components: { VButton, VIcon },
  props: {
    /**
     * One of the media types supported.
     */
    searchType: {
      type: String as PropType<SupportedSearchType>,
      required: true,
    },
    selected: {
      type: Boolean,
      default: false,
    },
  },
  emits: {
    select: defineEvent<[SupportedSearchType]>(),
  },
  setup(props, { emit }) {
    const iconPath = computed(() => iconMapping[props.searchType])
    const handleClick = () => emit("select", props.searchType)
    return { iconPath, handleClick, labelMapping }
  },
})
</script>
