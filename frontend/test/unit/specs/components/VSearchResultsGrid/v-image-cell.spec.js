import { fireEvent } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"
import { image } from "~~/test/unit/fixtures/image"

import { useAnalytics } from "~/composables/use-analytics"

import { IMAGE } from "~/constants/media"

import VImageCell from "~/components/VSearchResultsGrid/VImageCell.vue"

jest.mock("~/composables/use-analytics", () => ({
  useAnalytics: jest.fn(),
}))

describe("VImageCell", () => {
  let options = {}
  let sendCustomEventMock = null

  beforeEach(() => {
    sendCustomEventMock = jest.fn()
    useAnalytics.mockImplementation(() => ({
      sendCustomEvent: sendCustomEventMock,
    }))
    options = {
      props: {
        image,
        searchTerm: "cat",
        relatedTo: null,
      },
    }
  })

  it("sends SELECT_SEARCH_RESULT event when clicked", async () => {
    const { getByRole } = render(VImageCell, options)
    const link = getByRole("link")

    await fireEvent.click(link)

    expect(sendCustomEventMock).toHaveBeenCalledWith("SELECT_SEARCH_RESULT", {
      id: image.id,
      mediaType: IMAGE,
      query: "cat",
      provider: image.provider,
      relatedTo: null,
    })
  })
})
