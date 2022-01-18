<template>
  <button
    class="bg-white border border-dark-charcoal/20 rounded-sm flex hover:bg-dark-charcoal hover:text-white focus:bg-white focus:border-tx focus:ring focus:ring-pink focus:outline-none focus:shadow-ring focus:text-black overflow-hidden"
    :class="[
      isStacked
        ? 'flex-col items-start py-4 ps-4 pe-12'
        : 'flex-row justify-between items-center w-full min-w-[22rem] p-6',
    ]"
    role="radio"
    type="button"
    :aria-checked="isSelected"
    v-on="$listeners"
  >
    <div
      class="flex"
      :class="[isStacked ? 'flex-col items-start' : ' flex-row items-center']"
    >
      <VIcon :icon-path="iconPath" />
      <p class="font-semibold" :class="[isStacked ? 'pt-1' : 'ps-2 text-2xl']">
        {{
          isStacked
            ? $t(`search-tab.${mediaType}`)
            : $t(`search-tab.see-${mediaType}`)
        }}
      </p>
    </div>
    <span :class="{ 'text-sr': !isStacked }">{{ resultsCountLabel }}</span>
  </button>
</template>

<script>
import { computed, defineComponent } from '@nuxtjs/composition-api'
import { resultsCount } from '~/composables/use-i18n-utilities'
import {
  AUDIO,
  IMAGE,
  supportedMediaTypes as mediaTypes,
} from '~/constants/media'
import VIcon from '~/components/VIcon/VIcon.vue'

import audioIcon from '~/assets/icons/audio-wave.svg'
import imageIcon from '~/assets/icons/image.svg'

export default defineComponent({
  name: 'VContentLink',
  components: { VIcon },
  props: {
    /**
     * One of the media types supported.
     */
    mediaType: {
      type: String,
      required: true,
      validator: (val) => mediaTypes.includes(val),
    },
    /**
     * The number of results that the search returned.
     */
    resultsCount: {
      type: Number,
      required: true,
    },
    /**
     * Whether the indicated media type is currently selected.
     */
    isSelected: {
      type: Boolean,
      default: false,
    },
    /**
     * `stacked` intended for mobile and `horizontal` for desktop.
     */
    layout: {
      type: String,
      default: 'stacked',
      validator: (val) => ['stacked', 'horizontal'].includes(val),
    },
  },
  setup(props) {
    const iconMapping = {
      [AUDIO]: audioIcon,
      [IMAGE]: imageIcon,
    }
    const iconPath = computed(() => iconMapping[props.mediaType])

    const resultsCountLabel = computed(() => resultsCount(props.resultsCount))

    const isStacked = computed(() => props.layout == 'stacked')

    return { iconPath, imageIcon, resultsCountLabel, isStacked }
  },
})
</script>

<style scoped>
button[aria-checked='true'] {
  @apply bg-dark-charcoal text-white;
}
</style>
