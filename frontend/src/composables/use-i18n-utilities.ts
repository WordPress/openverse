import { useGetLocaleFormattedNumber } from "~/composables/use-get-locale-formatted-number"
import { useI18n } from "~/composables/use-i18n"
import type { SupportedMediaType, SupportedSearchType } from "~/constants/media"
import { ALL_MEDIA, AUDIO, IMAGE } from "~/constants/media"

/**
 * Not using dynamically-generated keys to ensure that
 * correct line is shown in the 'po' locale files
 */
const i18nKeys = {
  [ALL_MEDIA]: {
    noResult: "browse-page.all-no-results",
    result: "browse-page.all-result-count",
    more: "browse-page.all-result-count-more",
  },
  [IMAGE]: {
    noResult: "browse-page.contentLink.image.zero",
    result: "browse-page.contentLink.image.count",
    more: "browse-page.contentLink.image.countMore",
  },
  [AUDIO]: {
    noResult: "browse-page.contentLink.audio.zero",
    result: "browse-page.contentLink.audio.count",
    more: "browse-page.contentLink.audio.countMore",
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
    searchType: SupportedSearchType
  ) => {
    const countKey =
      resultsCount === 0
        ? "noResult"
        : resultsCount >= 10000
        ? "more"
        : "result"
    return i18nKeys[searchType][countKey]
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
    getLoading,
  }
}
