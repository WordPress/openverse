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

describe("VSearchResultsTitle", () => {
  const getOptions = ({ props, ...options } = {}) => ({
    ...options,
    props: {
      ...DEFAULT_PROPS,
      ...props,
    },
  })

  it("should render an h1 tag containing the correct text", async () => {
    const { container } = render(VSearchResultsTitle, getOptions())
    expect(container).toMatchSnapshot()
  })

  describe("accessible heading", () => {
    const cs = [0, 10, 4300, 10000, 10001]

    const scenarios = [
      ...cs.reduce(
        (all, i) => [
          ...all,
          ...cs.map((a) => ({
            searchType: "all",
            resultCounts: [
              ["image", i],
              ["audio", a],
            ],
          })),
        ],
        []
      ),
      ...cs.map((count) => ({
        searchType: "image",
        resultCounts: [
          ["image", count],
          ["audio", 0],
        ],
      })),
      ...cs.map((count) => ({
        searchType: "audio",
        resultCounts: [
          ["audio", count],
          ["image", 0],
        ],
      })),
    ].map((scenario) => [JSON.stringify(scenario), scenario])

    it.each(scenarios)("%s", (_, { searchType, resultCounts }) => {
      const { container } = render(
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
