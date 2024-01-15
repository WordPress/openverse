import { describe, expect, it } from "vitest"

import { render } from "~~/test/unit/test-utils/render"

import VSearchResultsTitle from "~/components/VSearchResultsTitle.vue"

const DEFAULT_PROPS = {
  size: "large",
  searchTerm: "zack",
  searchType: "all",
  resultCounts: [
    ["image", 10],
    ["audio", 10],
  ],
}

/**
 * Build test scenarios out of all possible
 * result count combinations.
 */
function getScenarios() {
  const counts = [0, 10, 4300, 240, 240]
  let scenarios = []
  counts.forEach((count) => {
    counts.forEach((innerCount) => {
      scenarios.push({
        searchType: "all",
        resultCounts: [
          ["image", count],
          ["audio", innerCount],
        ],
      })
    })
    scenarios.push({
      searchType: "image",
      resultCounts: [
        ["image", count],
        ["audio", 0],
      ],
    })
    scenarios.push({
      searchType: "audio",
      resultCounts: [
        ["audio", count],
        ["image", 0],
      ],
    })
  })
  return scenarios.map((scenario) => [JSON.stringify(scenario), scenario])
}

describe("VSearchResultsTitle", () => {
  const getOptions = ({ props, ...options } = {}) => ({
    ...options,
    props: {
      ...DEFAULT_PROPS,
      ...props,
    },
  })

  it("should render an h1 tag containing the correct text", async () => {
    const { container } = await render(VSearchResultsTitle, getOptions())
    expect(container).toMatchSnapshot()
  })

  describe("accessible heading", () => {
    it.each(getScenarios())("%s", async (_, { searchType, resultCounts }) => {
      const { container } = await render(
        VSearchResultsTitle,
        getOptions({
          props: {
            searchType,
            resultCounts,
          },
        })
      )

      // Cannot use inline snapshot in `each` test
      expect(container).toMatchSnapshot()
    })
  })
})
