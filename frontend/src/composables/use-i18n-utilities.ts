import { useGetLocaleFormattedNumber } from "~/composables/use-get-locale-formatted-number"
import { useI18n } from "~/composables/use-i18n"
import type { SupportedMediaType, SupportedSearchType } from "~/constants/media"
import { ALL_MEDIA, AUDIO, IMAGE } from "~/constants/media"

/**
 * Not using dynamically-generated keys to ensure that
 * correct line is shown in the 'po' locale files
 */
const i18nContentLinkKeys = {
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
/**
 * Not using dynamically-generated keys to ensure that
 * correct line is shown in the 'po' locale files
 */
const i18nResultsCountKeys = {
  [ALL_MEDIA]: {
    noResult: "browsePage.searchResultsTitle.all.zero",
    result: "browsePage.searchResultsTitle.all.count",
    more: "browsePage.searchResultsTitle.all.countMore",
  },
  [IMAGE]: {
    noResult: "browsePage.searchResultsTitle.image.zero",
    result: "browsePage.searchResultsTitle.image.count",
    more: "browsePage.searchResultsTitle.image.countMore",
  },
  [AUDIO]: {
    noResult: "browsePage.searchResultsTitle.audio.zero",
    result: "browsePage.searchResultsTitle.audio.count",
    more: "browsePage.searchResultsTitle.audio.countMore",
  },
}

/**
 * Returns the localized text for the number of search results.
 */
export function useI18nResultsCount() {
  const i18n = useI18n()
  const getLocaleFormattedNumber = useGetLocaleFormattedNumber()

  const getLoading = () => i18n.t("header.loading").toString()

  const getI18nKey = (
    resultsCount: number,
    searchType: SupportedSearchType,
    keysObject:
      | typeof i18nResultsCountKeys
      | typeof i18nContentLinkKeys = i18nContentLinkKeys
  ) => {
    const countKey =
      resultsCount === 0
        ? "noResult"
        : resultsCount >= 10000
        ? "more"
        : "result"
    return keysObject[searchType][countKey]
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
    return i18n.tc(getI18nKey(resultsCount, mediaType), resultsCount, {
      localeCount: getLocaleFormattedNumber(resultsCount),
      query,
      mediaType,
    })
  }

  const getI18nResultsTitle = (
    resultsCount: number,
    query: string,
    searchType: SupportedSearchType
  ) => {
    return i18n.tc(
      getI18nKey(resultsCount, searchType, i18nResultsCountKeys),
      resultsCount,
      {
        localeCount: getLocaleFormattedNumber(resultsCount),
        query,
        searchType,
      }
    )
  }
  /**
   * Returns the localized text for the number of search results, using corresponding
   * pluralization rules and decimal separators.
   * E.g. "No results", "3,567 results", "Over 10,000 results".
   */
  const getI18nCount = (resultsCount: number) => {
    return i18n.tc(getI18nKey(resultsCount, ALL_MEDIA), resultsCount, {
      localeCount: getLocaleFormattedNumber(resultsCount),
    })
  }

  return {
    getI18nCount,
    getI18nContentLinkLabel,
    getI18nResultsTitle,
    getLoading,
  }
}
