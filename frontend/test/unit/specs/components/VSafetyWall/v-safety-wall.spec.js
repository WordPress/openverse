import { fireEvent } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import { useSearchStore } from "~/stores/search"

import VSafetyWall from "~/components/VSafetyWall/VSafetyWall.vue"

jest.mock("~/stores/search", () => ({
  useSearchStore: jest.fn(),
}))

describe("VSafetyWall.vue", () => {
  let mockStore
  let options = {}

  beforeEach(() => {
    mockStore = {
      backToSearchPath: "/somepath",
    }
    useSearchStore.mockReturnValue(mockStore)

    options = {
      props: {
        media: {
          sensitivity: [
            "sensitive_text",
            "provider_supplied_sensitive",
            "user_reported_sensitive",
          ],
        },
      },
    }
  })

  it("emits reveal event when showMedia method is called", async () => {
    const { getByText } = render(VSafetyWall, options)
    const showButton = getByText("Show content")

    await fireEvent.click(showButton)

    expect(useSearchStore).toHaveBeenCalled()
  })

  it("backToSearchPath gets the value from the store", () => {
    render(VSafetyWall, options)

    expect(useSearchStore).toHaveBeenCalled()
  })
})
