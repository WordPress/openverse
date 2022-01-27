<template>
  <div
    class="text-dark-charcoal bg-white border border-dark-charcoal/20 rounded-sm flex flex-col hover:bg-dark-charcoal hover:text-white overflow-hidden items-start py-4 ps-4 pe-12 w-full lg:flex-row lg:justify-between lg:items-center lg:p-6 focus:bg-white focus:border-tx focus:ring focus:ring-pink focus:outline-none focus:shadow-ring focus:text-black"
  >
    <div class="flex flex-col items-start lg:flex-row lg:items-center">
      <VIcon :icon-path="iconPath" />
      <p class="hidden lg:block font-semibold pt-1 lg:ps-2 lg:text-2xl">
        {{ $t(`search-type.see-${mediaType}`) }}
      </p>
      <p class="block lg:hidden font-semibold pt-1 lg:ps-2 lg:text-2xl">
        {{ $t(`search-type.${mediaType}`) }}
      </p>
    </div>
    <span class="text-sr lg:text-base">{{ resultsCountLabel }}</span>
  </div>
</template>

<script>
import { computed, defineComponent } from '@nuxtjs/composition-api'
import { useI18nResultsCount } from '~/composables/use-i18n-utilities'
import { AUDIO, IMAGE, supportedMediaTypes } from '~/constants/media'
import VIcon from '~/components/VIcon/VIcon.vue'

import audioIcon from '~/assets/icons/audio-wave.svg'
import imageIcon from '~/assets/icons/image.svg'

const iconMapping = {
  [AUDIO]: audioIcon,
  [IMAGE]: imageIcon,
}

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
      validator: (val) => supportedMediaTypes.includes(val),
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
    const iconPath = computed(() => iconMapping[props.mediaType])
    const { getI18nCount } = useI18nResultsCount()
    const resultsCountLabel = computed(() => getI18nCount(props.resultsCount))

    return { iconPath, imageIcon, resultsCountLabel }
  },
})
</script>
