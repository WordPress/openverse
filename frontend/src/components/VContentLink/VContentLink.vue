<template>
  <!-- We 'disable' the link when there are 0 results by removing the href and setting aria-disabled. -->
  <VLink
    :href="hasResults ? to : undefined"
    class="flex w-full flex-col items-start overflow-hidden rounded-sm border border-dark-charcoal/20 bg-white py-4 pe-12 ps-4 md:flex-row md:items-center md:justify-between md:p-6"
    :class="
      hasResults
        ? ' text-dark-charcoal hover:bg-dark-charcoal hover:text-white hover:no-underline focus:border-tx focus:outline-none focus-visible:ring focus-visible:ring-pink'
        : 'cursor-not-allowed text-dark-charcoal/40'
    "
    @keydown.native.shift.tab.exact="$emit('shift-tab', $event)"
    @mousedown="handleClick"
  >
    <div class="flex flex-col items-start md:flex-row md:items-center">
      <VIcon :name="mediaType" />
      <p class="hidden pt-1 font-semibold md:block md:ps-2 md:pt-0 md:text-2xl">
        {{ $t(`search-type.see-${mediaType}`) }}
      </p>
      <p class="block pt-1 font-semibold md:hidden md:ps-2 md:pt-0 md:text-2xl">
        {{ $t(`search-type.${mediaType}`) }}
      </p>
    </div>
    <span class="text-sr">{{ resultsCountLabel }}</span>
  </VLink>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import { useAnalytics } from "~/composables/use-analytics"

import { useI18nResultsCount } from "~/composables/use-i18n-utilities"
import type { SupportedMediaType } from "~/constants/media"

import { defineEvent } from "~/types/emits"

import useSearchType from "~/composables/use-search-type"

import VIcon from "~/components/VIcon/VIcon.vue"
import VLink from "~/components/VLink.vue"

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
    const { getI18nCount } = useI18nResultsCount()
    const hasResults = computed(() => props.resultsCount > 0)
    const resultsCountLabel = computed(() => getI18nCount(props.resultsCount))

    const { activeType } = useSearchType()
    const analytics = useAnalytics()

    const handleClick = () => {
      analytics.sendCustomEvent("CHANGE_CONTENT_TYPE", {
        previous: activeType.value,
        next: props.mediaType,
        component: "VContentLink",
      })
    }

    return {
      resultsCountLabel,
      hasResults,

      handleClick,
    }
  },
})
</script>
