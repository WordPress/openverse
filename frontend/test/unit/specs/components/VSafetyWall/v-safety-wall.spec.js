import { fireEvent, waitFor } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import VSafetyWall from "~/components/VSafetyWall/VSafetyWall.vue"

describe("VSafetyWall.vue", () => {
  let mockStore
  let options = {}

  beforeEach(() => {
    mockStore = {
      backToSearchPath: "/somepath",
    }

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
    const { getByText, emitted } = await render(VSafetyWall, options)
    const showButton = getByText("Show content")

    await fireEvent.click(showButton)

    await waitFor(() => {
      expect(emitted().reveal).toBeTruthy()
    })
  })

  it("backToSearchPath gets the value from the store", async () => {
    const { findByText } = await render(VSafetyWall, options)

    const backToSearchButton = await findByText("Back to results")
    expect(backToSearchButton).toBeInTheDocument()
    expect(backToSearchButton.getAttribute("href")).toBe(
      mockStore.backToSearchPath
    )
  })
})
