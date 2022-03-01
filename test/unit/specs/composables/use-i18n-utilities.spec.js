import { useI18nResultsCount } from '~/composables/use-i18n-utilities'

jest.mock('@nuxtjs/composition-api', () => ({
  useContext: () => ({
    i18n: {
      tc: (fullKey, resultsCount, { localeCount }) => ({
        fullKey,
        resultsCount,
        localeCount,
      }),
      locale: 'en',
    },
  }),
}))

describe('i18nResultsCount', () => {
  it.each`
    resultCount | expectedResult
    ${0}        | ${{ fullKey: 'browse-page.all-no-results', resultsCount: 0, localeCount: '0' }}
    ${1}        | ${{ fullKey: 'browse-page.all-result-count', resultsCount: 1, localeCount: '1' }}
    ${10}       | ${{ fullKey: 'browse-page.all-result-count', resultsCount: 10, localeCount: '10' }}
    ${10000}    | ${{ fullKey: 'browse-page.all-result-count-more', resultsCount: 10000, localeCount: '10,000' }}
  `(
    'Should show correct result for $resultCount of type $mediaType',
    ({ resultCount, expectedResult }) => {
      const { getI18nCount } = useI18nResultsCount()
      const result = getI18nCount(resultCount)

      expect(result).toEqual(expectedResult)
    }
  )
})
