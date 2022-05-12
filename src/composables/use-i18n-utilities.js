import { useGetLocaleFormattedNumber } from '~/composables/use-get-locale-formatted-number'
import { useI18n } from '~/composables/use-i18n'

/**
 * Not using dynamically-generated keys to ensure that
 * correct line is shown in the 'po' locale files
 */
const i18nKeys = {
  noResult: 'browse-page.all-no-results',
  result: 'browse-page.all-result-count',
  more: 'browse-page.all-result-count-more',
}

/**
 * Returns the localized text for the number of search results.
 */
export function useI18nResultsCount() {
  const i18n = useI18n()
  const getLocaleFormattedNumber = useGetLocaleFormattedNumber()

  /**
   * @param {number} resultsCount
   * @returns {string}
   */
  const getI18nCount = (resultsCount) => {
    const countKey =
      resultsCount === 0
        ? 'noResult'
        : resultsCount >= 10000
        ? 'more'
        : 'result'
    const fullKey = i18nKeys[countKey]
    const localeCount = getLocaleFormattedNumber(resultsCount)
    return i18n.tc(fullKey, resultsCount, { localeCount })
  }
  return {
    getI18nCount,
  }
}
