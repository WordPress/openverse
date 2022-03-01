<template>
  <button
    type="button"
    class="transition-colors"
    :class="[$style.button, selected && $style['button-pressed']]"
    :aria-pressed="selected"
    @click="handleClick"
  >
    <VIcon :icon-path="iconPath" class="me-1 flex-shrink-0" />
    <span>{{ $t(`search-type.${searchType}`) }}</span>
  </button>
</template>

<script>
import { computed, defineComponent } from '@nuxtjs/composition-api'

import {
  ALL_MEDIA,
  AUDIO,
  IMAGE,
  supportedSearchTypes,
} from '~/constants/media'

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
      type: String,
      required: true,
      validator: (v) => supportedSearchTypes.includes(v),
    },
    selected: {
      type: Boolean,
      default: false,
    },
  },
  setup(props, { emit }) {
    const iconPath = computed(() => iconMapping[props.searchType])
    const handleClick = () => emit('select', props.searchType)
    return { iconPath, handleClick }
  },
})
</script>
<style module>
.button {
  @apply flex flex-row items-center p-2 pe-3 rounded-sm text-sr font-semibold bg-tx border border-dark-charcoal focus-visible:outline-none  focus-visible:ring focus-visible:ring-pink hover:text-white hover:bg-dark-charcoal focus-visible:hover:border-white focus-visible:border-tx;
}
.button-pressed {
  @apply text-white bg-dark-charcoal focus-visible:border focus-visible:border-white;
}
</style>
