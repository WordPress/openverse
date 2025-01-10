import { computed } from "vue"

import { IMAGE } from "#shared/constants/media"
import { useI18nResultsCount } from "~/composables/use-i18n-utilities"

describe("i18nResultsCount", () => {
  it.each`
    resultCount | expectedResult
    ${0}        | ${{ visible: "No results", aria: "No images found for cat." }}
    ${1}        | ${{ visible: "1 result", aria: "See 1 image found for cat." }}
    ${10}       | ${{ visible: "10 results", aria: "See 10 images found for cat." }}
    ${240}      | ${{ visible: "Top 240 results", aria: "See the top 240 images found for cat." }}
  `(
    "Should show correct result for $resultCount of type $mediaType",
    ({ resultCount, expectedResult }) => {
      const { getResultCountLabels } = useI18nResultsCount()
      const result = getResultCountLabels(resultCount, IMAGE, "cat")

      expect(result.visible).toEqual(expectedResult.visible)
      expect(result.aria).toEqual(expectedResult.aria)
    }
  )

  it("Shows loading message", () => {
    const showLoading = computed(() => true)
    const { getResultCountLabels } = useI18nResultsCount(showLoading)

    const result = getResultCountLabels(240, IMAGE, "cat")

    expect(result.aria).toEqual("Loading...")
    expect(result.visible).toEqual("Loading...")
  })
})
