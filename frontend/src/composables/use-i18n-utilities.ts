import { useNuxtApp } from "#imports"

import { useGetLocaleFormattedNumber } from "~/composables/use-get-locale-formatted-number"
import { ALL_MEDIA, AUDIO, IMAGE } from "~/constants/media"
import type { SupportedMediaType, SupportedSearchType } from "~/constants/media"
import type { Collection } from "~/types/search"

/**
 * Not using dynamically-generated keys to ensure that
 * correct line is shown in the 'po' locale files
 */
const searchResultKeys = {
  [ALL_MEDIA]: {
    noResult: "browsePage.allNoResults",
    result: "browsePage.allResultCount",
    more: "browsePage.allResultCountMore",
  },
  [IMAGE]: {
    noResult: "browsePage.contentLink.image.zero",
    result: "browsePage.contentLink.image.count",
    more: "browsePage.contentLink.image.countMore",
  },
  [AUDIO]: {
    noResult: "browsePage.contentLink.audio.zero",
    result: "browsePage.contentLink.audio.count",
    more: "browsePage.contentLink.audio.countMore",
  },
}
const collectionKeys = {
  source: {
    [IMAGE]: {
      noResult: "collection.resultCountLabel.source.image.zero",
      result: "collection.resultCountLabel.source.image.count",
      more: "collection.resultCountLabel.source.image.countMore",
    },
    [AUDIO]: {
      noResult: "collection.resultCountLabel.source.audio.zero",
      result: "collection.resultCountLabel.source.audio.count",
      more: "collection.resultCountLabel.source.audio.countMore",
    },
  },
  creator: {
    [IMAGE]: {
      noResult: "collection.resultCountLabel.creator.image.zero",
      result: "collection.resultCountLabel.creator.image.count",
      more: "collection.resultCountLabel.creator.image.countMore",
    },
    [AUDIO]: {
      noResult: "collection.resultCountLabel.creator.audio.zero",
      result: "collection.resultCountLabel.creator.audio.count",
      more: "collection.resultCountLabel.creator.audio.countMore",
    },
  },
  tag: {
    [IMAGE]: {
      noResult: "collection.resultCountLabel.tag.image.zero",
      result: "collection.resultCountLabel.tag.image.count",
      more: "collection.resultCountLabel.tag.image.countMore",
    },
    [AUDIO]: {
      noResult: "collection.resultCountLabel.tag.audio.zero",
      result: "collection.resultCountLabel.tag.audio.count",
      more: "collection.resultCountLabel.tag.audio.countMore",
    },
  },
}

function getCountKey(resultsCount: number) {
  return resultsCount === 0
    ? "noResult"
    : resultsCount >= 10000
    ? "more"
    : "result"
}

/**
 * Returns the localized text for the number of search results.
 */
export function useI18nResultsCount() {
  const { t } = useNuxtApp().$i18n
  const getLocaleFormattedNumber = useGetLocaleFormattedNumber()

  const getLoading = () => t("header.loading")

  const getI18nKey = (
    resultsCount: number,
    searchType: SupportedSearchType
  ) => {
    const countKey = getCountKey(resultsCount)
    return searchResultKeys[searchType][countKey]
  }

  /**
   * Returns the localized text for the content link label.
   * E.g. "See 3,567 image results for 'cats'".
   */
  const getI18nContentLinkLabel = (
    resultsCount: number,
    query: string,
    mediaType: SupportedMediaType
  ) => {
    return t(getI18nKey(resultsCount, mediaType), {
      count: resultsCount,
      localeCount: getLocaleFormattedNumber(resultsCount),
      query,
      mediaType,
    })
  }
  const getI18nCollectionResultCountLabel = (
    resultCount: number,
    mediaType: SupportedMediaType,
    collectionType: Collection,
    params: Record<string, string> | undefined = undefined
  ) => {
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
   * E.g. "No results", "3,567 results", "Over 10,000 results".
   */
  const getI18nCount = (resultsCount: number) => {
    return t(getI18nKey(resultsCount, ALL_MEDIA), {
      count: resultsCount,
      localeCount: getLocaleFormattedNumber(resultsCount),
    })
  }

  return {
    getI18nCount,
    getI18nContentLinkLabel,
    getI18nCollectionResultCountLabel,
    getLoading,
  }
}
