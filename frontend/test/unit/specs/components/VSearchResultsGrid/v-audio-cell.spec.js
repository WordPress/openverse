import { fireEvent } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import { getAudioObj } from "~~/test/unit/fixtures/audio"

import { useAnalytics } from "~/composables/use-analytics"
import { AUDIO } from "~/constants/media"

import VAudioCell from "~/components/VSearchResultsGrid/VAudioCell.vue"

jest.mock("~/composables/use-analytics", () => ({
  useAnalytics: jest.fn(),
}))

describe("VAudioCell", () => {
  let options = {}
  let sendCustomEventMock = null
  const audio = getAudioObj()

  beforeEach(() => {
    sendCustomEventMock = jest.fn()
    useAnalytics.mockImplementation(() => ({
      sendCustomEvent: sendCustomEventMock,
    }))
    options = {
      props: {
        audio,
        searchTerm: "cat",
        relatedTo: null,
      },
    }
  })

  it("sends SELECT_SEARCH_RESULT event when clicked", async () => {
    const { getByRole } = render(VAudioCell, options)
    const link = getByRole("application")

    await fireEvent.click(link)

    expect(sendCustomEventMock).toHaveBeenCalledWith("SELECT_SEARCH_RESULT", {
      id: audio.id,
      mediaType: AUDIO,
      query: "cat",
      provider: audio.provider,
      relatedTo: null,
    })
  })
})
