import { fireEvent, screen } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"
import { getAudioObj } from "~~/test/unit/fixtures/audio"

import { AUDIO } from "~/constants/media"
import { useAnalytics } from "~/composables/use-analytics"
import { useRelatedMediaStore } from "~/stores/media/related-media"
import { useSearchStore } from "~/stores/search"

import VRelatedAudio from "~/components/VAudioDetails/VRelatedAudio.vue"

const audioResults = [getAudioObj(), getAudioObj()]

jest.mock("~/composables/use-analytics", () => ({
  useAnalytics: jest.fn(),
}))
describe("RelatedAudios", () => {
  let options = {
    propsData: {
      media: audioResults,
      fetchState: { isFetching: false, isError: false },
    },
    stubs: { LoadingIcon: true, VAudioThumbnail: true },
  }
  let sendCustomEventMock = null

  beforeEach(() => {
    sendCustomEventMock = jest.fn()
    useAnalytics.mockImplementation(() => ({
      sendCustomEvent: sendCustomEventMock,
    }))
  })

  it("should render content when finished loading related audios", async () => {
    render(VRelatedAudio, options)

    screen.getByText(/related audio/i)

    expect(screen.queryAllByLabelText("Play")).toHaveLength(
      // Two for each as the "row" layout rendered by VRelatedAudio
      // renders a "large" and "small" version that are visually hidden by a parent
      // depending on the breakpoint (but critically still rendered in the
      // DOM)
      audioResults.length * 2
    )
  })

  it("should send SELECT_SEARCH_RESULT event when clicked", async () => {
    const mainMediaId = "123"
    const query = "cat"
    const { queryAllByRole } = render(
      VRelatedAudio,
      options,
      (localVue, options) => {
        const relatedMediaStore = useRelatedMediaStore(options.pinia)
        relatedMediaStore.$patch({ mainMediaId })
        useSearchStore(localVue.pinia).$patch({ searchTerm: query })
      }
    )
    const audioLink = queryAllByRole("application")[0]

    await fireEvent.click(audioLink)

    expect(sendCustomEventMock).toHaveBeenCalledWith("SELECT_SEARCH_RESULT", {
      id: audioResults[0].id,
      mediaType: AUDIO,
      query,
      provider: audioResults[0].provider,
      relatedTo: mainMediaId,
    })
  })
})
