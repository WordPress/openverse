import { useI18nResultsCount } from "~/composables/use-i18n-utilities"

describe("i18nResultsCount", () => {
  it.each`
    resultCount | expectedResult
    ${0}        | ${{ fullKey: "browsePage.allNoResults", resultsCount: 0, localeCount: "0" }}
    ${1}        | ${{ fullKey: "browsePage.allResultCount", resultsCount: 1, localeCount: "1" }}
    ${10}       | ${{ fullKey: "browsePage.allResultCount", resultsCount: 10, localeCount: "10" }}
    ${10000}    | ${{ fullKey: "browsePage.allResultCountMore", resultsCount: 10000, localeCount: "10,000" }}
  `(
    "Should show correct result for $resultCount of type $mediaType",
    ({ resultCount, expectedResult }) => {
      const { getI18nCount } = useI18nResultsCount()
      const result = getI18nCount(resultCount)

      expect(result).toEqual(expectedResult)
    }
  )
})
