<template>
  <VLink
    :href="to"
    class="text-dark-charcoal bg-white border border-dark-charcoal/20 rounded-sm flex flex-col md:flex-row md:justify-between items-start md:items-center hover:bg-dark-charcoal hover:text-white hover:no-underline focus:border-tx overflow-hidden py-4 ps-4 pe-12 w-full md:p-6 focus:outline-none focus-visible:ring focus-visible:ring-pink"
    @keydown.native.shift.tab.exact="$emit('shift-tab', $event)"
  >
    <div class="flex flex-col items-start md:flex-row md:items-center">
      <VIcon :icon-path="iconPath" />
      <p class="hidden md:block font-semibold pt-1 md:pt-0 md:ps-2 md:text-2xl">
        {{ $t(`search-type.see-${mediaType}`) }}
      </p>
      <p class="block md:hidden font-semibold pt-1 md:pt-0 md:ps-2 md:text-2xl">
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
