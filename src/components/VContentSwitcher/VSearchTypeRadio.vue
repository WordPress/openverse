<template>
  <button
    type="button"
    class="flex flex-row items-center p-2 pe-3 rounded-sm text-sr font-semibold border border-dark-charcoal hover:text-white hover:bg-dark-charcoal focus:outline-none focus-visible:ring focus-visible:ring-pink focus-visible:hover:border-white"
    :class="[
      selected
        ? 'text-white bg-dark-charcoal focus-visible:border focus-visible:border-white'
        : 'bg-tx focus-visible:border-tx',
    ]"
    :aria-pressed="selected"
    @click="handleClick"
  >
    <VIcon :icon-path="iconPath" class="me-1 flex-shrink-0" />
    <span>{{ $t(`search-type.${searchType}`) }}</span>
  </button>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from '@nuxtjs/composition-api'

import { ALL_MEDIA, AUDIO, IMAGE, SupportedSearchType } from '~/constants/media'
import { defineEvent } from '~/types/emits'

import VIcon from '~/components/VIcon/VIcon.vue'

import audioIcon from '~/assets/icons/audio-wave.svg'
import imageIcon from '~/assets/icons/image.svg'
import allIcon from '~/assets/icons/all-content.svg'

const iconMapping = {
  [AUDIO]: audioIcon,
  [IMAGE]: imageIcon,
  [ALL_MEDIA]: allIcon,
}

export default defineComponent({
  name: 'VSearchTypeRadio',
  components: { VIcon },
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
    const handleClick = () => emit('select', props.searchType)
    return { iconPath, handleClick }
  },
})
</script>
