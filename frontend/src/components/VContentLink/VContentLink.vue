<template>
  <!-- We 'disable' the link when there are 0 results by removing the href and setting aria-disabled. -->
  <VLink
    :href="hasResults ? to : undefined"
    class="flex w-full flex-col items-start overflow-hidden rounded-sm border border-dark-charcoal/20 bg-white py-4 ps-4 pe-12 md:flex-row md:items-center md:justify-between md:p-6"
    :class="
      hasResults
        ? ' text-dark-charcoal hover:bg-dark-charcoal hover:text-white hover:no-underline focus:border-tx focus:outline-none focus-visible:ring focus-visible:ring-pink'
        : 'cursor-not-allowed text-dark-charcoal/40'
    "
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
import { computed, defineComponent, PropType } from "@nuxtjs/composition-api"

import { useI18nResultsCount } from "~/composables/use-i18n-utilities"
import { AUDIO, IMAGE, SupportedMediaType } from "~/constants/media"

import { defineEvent } from "~/types/emits"

import VIcon from "~/components/VIcon/VIcon.vue"
import VLink from "~/components/VLink.vue"

import audioIcon from "~/assets/icons/audio-wave.svg"
import imageIcon from "~/assets/icons/image.svg"

const iconMapping = {
  [AUDIO]: audioIcon,
  [IMAGE]: imageIcon,
}

export default defineComponent({
  name: "VContentLink",
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
     * The number of results that the search returned. The link
     * will be disabled if this value is zero.
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
    "shift-tab": defineEvent<[KeyboardEvent]>(),
  },
  setup(props) {
    const iconPath = computed(() => iconMapping[props.mediaType])
    const { getI18nCount } = useI18nResultsCount()
    const hasResults = computed(() => props.resultsCount > 0)
    const resultsCountLabel = computed(() => getI18nCount(props.resultsCount))

    return {
      iconPath,
      imageIcon,
      resultsCountLabel,
      hasResults,
    }
  },
})
</script>
