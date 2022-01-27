import { useContext } from '@nuxtjs/composition-api'

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
  const { i18n } = useContext()
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
    const countLocale =
      i18n.localeProperties?.dir === 'rtl' ? 'en' : i18n.locale
    const localeCount = resultsCount.toLocaleString(countLocale)
    return i18n.tc(fullKey, resultsCount, { localeCount })
  }
  return {
    getI18nCount,
  }
}
