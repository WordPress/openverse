<template>
  <h1
    class="sr-only break-words md:not-sr-only"
    :class="[
      size === 'large'
        ? 'heading-2 lg:heading-1 !leading-none lg:!leading-none'
        : 'heading-2 !leading-none',
    ]"
  >
    <span aria-hidden="true">{{ searchTerm }}</span
    ><span class="sr-only">{{ ariaHeading }}</span>
  </h1>
</template>

<script lang="ts">
import { useI18n } from "#imports"

import { defineComponent, PropType, computed } from "vue"

import type { SupportedMediaType, SupportedSearchType } from "~/constants/media"

import { useGetLocaleFormattedNumber } from "~/composables/use-get-locale-formatted-number"
import { getCountKey } from "~/composables/use-i18n-utilities"

export default defineComponent({
  name: "VSearchResultsTitle",
  props: {
    searchTerm: {
      required: true,
      type: String,
    },
    size: {
      required: false,
      default: "default",
      type: String as PropType<"default" | "large">,
    },
    resultCounts: {
      required: true,
      type: Array as PropType<[SupportedMediaType, number][]>,
    },
    searchType: {
      required: true,
      type: String as PropType<SupportedSearchType>,
    },
  },
  setup(props) {
    const getLocaleFormattedNumber = useGetLocaleFormattedNumber()
    const { t } = useI18n()
    const mediaLocaleCounts = computed(() =>
      props.resultCounts.reduce(
        (acc, [mediaType, count]) => {
          return {
            ...acc,
            [mediaType]: {
              count,
              countKey: getCountKey(count),
              localeCount: getLocaleFormattedNumber(count),
            },
          }
        },
        {} as Record<
          SupportedMediaType,
          { count: number; countKey: string; localeCount: string }
        >
      )
    )

    const _getAllMediaAriaHeading = () => {
      const imageLocaleCounts = mediaLocaleCounts.value.image
      const imageResults = t(
        `browsePage.aria.allResultsHeadingCount.image.${imageLocaleCounts.countKey}`,
        {
          localeCount: imageLocaleCounts.localeCount,
        }
      )

      const audioLocaleCounts = mediaLocaleCounts.value.audio
      const audioResults = t(
        `browsePage.aria.allResultsHeadingCount.audio.${audioLocaleCounts.countKey}`,
        {
          localeCount: audioLocaleCounts.localeCount,
        }
      )

      return t("browsePage.aria.results.all", {
        query: props.searchTerm,
        imageResults,
        audioResults,
      })
    }

    const ariaHeading = computed((): string => {
      switch (props.searchType) {
        case "image": {
          const { count, countKey, localeCount } = mediaLocaleCounts.value.image
          return t(`browsePage.aria.results.image.${countKey}`, {
            count,
            localeCount,
            query: props.searchTerm,
          })
        }
        case "audio": {
          const { count, countKey, localeCount } = mediaLocaleCounts.value.audio
          return t(`browsePage.aria.results.audio.${countKey}`, {
            count,
            localeCount,
            query: props.searchTerm,
          })
        }
        default:
        case "all": {
          return _getAllMediaAriaHeading()
        }
      }
    })

    return {
      ariaHeading,
    }
  },
})
</script>

<style scoped>
/* Title case the user's search query */
h1:first-letter {
  text-transform: uppercase;
}
</style>
