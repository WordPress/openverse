import { useNuxtApp } from "#imports"
import type { ComputedRef } from "vue"

import { ALL_MEDIA, AUDIO, IMAGE } from "#shared/constants/media"
import type {
  SupportedMediaType,
  SupportedSearchType,
} from "#shared/constants/media"
import type { Collection } from "#shared/types/search"
import { useGetLocaleFormattedNumber } from "~/composables/use-get-locale-formatted-number"

type KeyCollection = {
  zero: string
  count: string
  countMore: string
}
type KeyMapping = Record<SupportedMediaType, KeyCollection> & {
  all?: KeyCollection
}
/**
 * Not using dynamically-generated keys to ensure that
 * correct line is shown in the 'po' locale files
 */
const searchResultKeys = {
  [ALL_MEDIA]: {
    zero: "browsePage.allNoResults",
    count: "browsePage.allResultCount",
    countMore: "browsePage.allResultCountMore",
  },
  [IMAGE]: {
    zero: "browsePage.contentLink.image.zero",
    count: "browsePage.contentLink.image.count",
    countMore: "browsePage.contentLink.image.countMore",
  },
  [AUDIO]: {
    zero: "browsePage.contentLink.audio.zero",
    count: "browsePage.contentLink.audio.count",
    countMore: "browsePage.contentLink.audio.countMore",
  },
} satisfies KeyMapping

const collectionKeys = {
  source: {
    [IMAGE]: {
      zero: "collection.resultCountLabel.source.image.zero",
      count: "collection.resultCountLabel.source.image.count",
      countMore: "collection.resultCountLabel.source.image.countMore",
    },
    [AUDIO]: {
      zero: "collection.resultCountLabel.source.audio.zero",
      count: "collection.resultCountLabel.source.audio.count",
      countMore: "collection.resultCountLabel.source.audio.countMore",
    },
  },
  creator: {
    [IMAGE]: {
      zero: "collection.resultCountLabel.creator.image.zero",
      count: "collection.resultCountLabel.creator.image.count",
      countMore: "collection.resultCountLabel.creator.image.countMore",
    },
    [AUDIO]: {
      zero: "collection.resultCountLabel.creator.audio.zero",
      count: "collection.resultCountLabel.creator.audio.count",
      countMore: "collection.resultCountLabel.creator.audio.countMore",
    },
  },
  tag: {
    [IMAGE]: {
      zero: "collection.resultCountLabel.tag.image.zero",
      count: "collection.resultCountLabel.tag.image.count",
      countMore: "collection.resultCountLabel.tag.image.countMore",
    },
    [AUDIO]: {
      zero: "collection.resultCountLabel.tag.audio.zero",
      count: "collection.resultCountLabel.tag.audio.count",
      countMore: "collection.resultCountLabel.tag.audio.countMore",
    },
  },
} satisfies Record<Collection, KeyMapping>

export function getCountKey(resultsCount: number): keyof KeyCollection {
  return resultsCount === 0
    ? "zero"
    : resultsCount >= 240
      ? "countMore"
      : "count"
}

/**
 * Returns the localized text for the number of search results.
 */
export function useI18nResultsCount(showLoading?: ComputedRef<boolean>) {
  const { t } = useNuxtApp().$i18n
  const getLocaleFormattedNumber = useGetLocaleFormattedNumber()

  const getLoading = () => t("header.loading")

  const getI18nKey = (
    resultsCount: number,
    searchType: SupportedSearchType
  ) => {
    if (showLoading?.value) {
      return "header.loading"
    }
    const countKey = getCountKey(resultsCount)
    return searchResultKeys[searchType][countKey]
  }

  const getI18nCollectionResultCountLabel = (
    resultCount: number,
    mediaType: SupportedMediaType,
    collectionType: Collection,
    params: Record<string, string> | undefined = undefined
  ) => {
    if (showLoading?.value) {
      return ""
    }
    const key =
      collectionKeys[collectionType][mediaType][getCountKey(resultCount)]
    return t(key, {
      count: resultCount,
      localeCount: getLocaleFormattedNumber(resultCount),
      ...params,
    })
  }

  /**
   * Returns the localized text for the number of search results, using corresponding
   * pluralization rules and decimal separators.
   * E.g. "No results", "132 results", "Top 240 results".
   */
  const getI18nCount = (resultsCount: number) => {
    return t(getI18nKey(resultsCount, ALL_MEDIA), {
      count: resultsCount,
      localeCount: getLocaleFormattedNumber(resultsCount),
    })
  }

  /**
   * The result count labels for screen readers and visible text, used in the content links
   * on all results page. Localized text for the number of search results, using corresponding
   * pluralization rules and decimal separators.
   * For the visible label, does not specify the media type, e.g.,
   * "Loading...", "No results", "132 results", "Top 240 results".
   * For the aria label, adds details about the media type and search query, e.g.,
   * "See 240 image results for 'cats'".
   */
  const getResultCountLabels = (
    resultsCount: number,
    mediaType: SupportedMediaType,
    query: string
  ) => {
    if (showLoading?.value) {
      return { aria: getLoading(), visible: getLoading() }
    }
    return {
      aria: t(getI18nKey(resultsCount, mediaType), {
        count: resultsCount,
        localeCount: getLocaleFormattedNumber(resultsCount),
        query,
        mediaType,
      }),
      visible: getI18nCount(resultsCount),
    }
  }

  return {
    getI18nCollectionResultCountLabel,
    getResultCountLabels,
    getI18nCount,
  }
}
