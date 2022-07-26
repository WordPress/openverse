<template>
  <VLink
    :href="to"
    class="flex w-full flex-col items-start overflow-hidden rounded-sm border border-dark-charcoal/20 bg-white py-4 text-dark-charcoal ps-4 pe-12 hover:bg-dark-charcoal hover:text-white hover:no-underline focus:border-tx focus:outline-none focus-visible:ring focus-visible:ring-pink md:flex-row md:items-center md:justify-between md:p-6"
    @keydown.native.shift.tab.exact="$emit('shift-tab', $event)"
  >
    <div class="flex flex-col items-start md:flex-row md:items-center">
      <VIcon :icon-path="iconPath" />
      <p class="hidden pt-1 font-semibold md:block md:pt-0 md:text-2xl md:ps-2">
        {{ $t(`search-type.see-${mediaType}`) }}
      </p>
      <p class="block pt-1 font-semibold md:hidden md:pt-0 md:text-2xl md:ps-2">
        {{ $t(`search-type.${mediaType}`) }}
      </p>
    </div>
    <span class="text-sr">{{ resultsCountLabel }}</span>
  </VLink>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from '@nuxtjs/composition-api'

import { useI18nResultsCount } from '~/composables/use-i18n-utilities'
import { AUDIO, IMAGE, SupportedMediaType } from '~/constants/media'

import { defineEvent } from '~/types/emits'

import VIcon from '~/components/VIcon/VIcon.vue'
import VLink from '~/components/VLink.vue'

import audioIcon from '~/assets/icons/audio-wave.svg'
import imageIcon from '~/assets/icons/image.svg'

const iconMapping = {
  [AUDIO]: audioIcon,
  [IMAGE]: imageIcon,
}

export default defineComponent({
  name: 'VContentLink',
  components: { VIcon, VLink },
  props: {
    /**
     * One of the media types supported.
     */
    mediaType: {
      type: String as PropType<SupportedMediaType>,
      required: true,
    },
    /**
     * The number of results that the search returned.
     */
    resultsCount: {
      type: Number,
      required: true,
    },
    /**
     * The route target of the link.
     */
    to: {
      type: String,
    },
  },
  emits: {
    'shift-tab': defineEvent<[KeyboardEvent]>(),
  },
  setup(props) {
    const iconPath = computed(() => iconMapping[props.mediaType])
    const { getI18nCount } = useI18nResultsCount()
    const resultsCountLabel = computed(() => getI18nCount(props.resultsCount))

    return { iconPath, imageIcon, resultsCountLabel }
  },
})
</script>
