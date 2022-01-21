<template>
  <div
    class="bg-white border border-dark-charcoal/20 rounded-sm flex hover:bg-dark-charcoal hover:text-white overflow-hidden flex-col items-start py-4 ps-4 pe-12 w-full lg:flex-row lg:justify-between lg:items-center lg:p-6"
  >
    <div class="flex flex-col items-start lg:flex-row lg:items-center">
      <VIcon :icon-path="iconPath" />
      <p class="hidden lg:block font-semibold pt-1 lg:ps-2 lg:text-2xl">
        {{ $t(`search-tab.see-${mediaType}`) }}
      </p>
      <p class="block lg:hidden font-semibold pt-1 lg:ps-2 lg:text-2xl">
        {{ $t(`search-tab.${mediaType}`) }}
      </p>
    </div>
    <span class="text-sr lg:text-base">{{ resultsCountLabel }}</span>
  </div>
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
  },
  setup(props) {
    const iconMapping = {
      [AUDIO]: audioIcon,
      [IMAGE]: imageIcon,
    }
    const iconPath = computed(() => iconMapping[props.mediaType])
    const resultsCountLabel = computed(() => resultsCount(props.resultsCount))

    return { iconPath, imageIcon, resultsCountLabel }
  },
})
</script>

<style scoped>
button[aria-checked='true'] {
  @apply bg-dark-charcoal text-white;
}
</style>
