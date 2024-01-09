import { useI18nResultsCount } from "~/composables/use-i18n-utilities"

describe("i18nResultsCount", () => {
  it.each`
    resultCount | expectedResult
    ${0}        | ${"No results"}
    ${1}        | ${"1 result"}
    ${10}       | ${"10 results"}
    ${10000}    | ${"Over 10,000 results"}
  `(
    "Should show correct result for $resultCount of type $mediaType",
    ({ resultCount, expectedResult }) => {
      const { getI18nCount } = useI18nResultsCount()
      const result = getI18nCount(resultCount)

      expect(result).toEqual(expectedResult)
    }
  )
})
