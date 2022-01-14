import { useContext } from '@nuxtjs/composition-api'
import { ALL_MEDIA } from '~/constants/media'

/**
 * Returns the localized text for the number of search results according to the
 * media type.
 *
 * @param {number} resultsCount
 * @param {string} mediaType
 * @returns {string}
 */
export function resultsCount(resultsCount, mediaType = ALL_MEDIA) {
  const { i18n } = useContext()

  const countKey =
    resultsCount === 0
      ? 'no-results'
      : resultsCount >= 10000
      ? 'result-count-more'
      : 'result-count'
  const fullKey = `browse-page.${mediaType}-${countKey}`
  const localeCount = resultsCount.toLocaleString(i18n.locale)
  return i18n.tc(fullKey, resultsCount, { localeCount })
}
