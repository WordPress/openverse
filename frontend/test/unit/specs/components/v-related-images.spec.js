import { fireEvent, screen } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import { IMAGE } from "~/constants/media"
import { useSearchStore } from "~/stores/search"
import { useRelatedMediaStore } from "~/stores/media/related-media"
import { useAnalytics } from "~/composables/use-analytics"

import VRelatedImages from "~/components/VImageDetails/VRelatedImages.vue"

jest.mock("~/composables/use-analytics", () => ({
  useAnalytics: jest.fn(),
}))

const media = [
  { id: "img1", url: "https://wp.org/img1.jpg" },
  { id: "img2", url: "https://wp.org/img2.jpg" },
]

describe("RelatedImage", () => {
  let props
  let options
  let sendCustomEventMock = null
  beforeEach(() => {
    props = { media, fetchState: { isFetching: false } }
    options = {
      propsData: props,
      stubs: ["VLicense"],
    }
    sendCustomEventMock = jest.fn()
    useAnalytics.mockImplementation(() => ({
      sendCustomEvent: sendCustomEventMock,
    }))
  })
  it("should render an image grid", () => {
    render(VRelatedImages, options)

    expect(
      screen.getAllByRole("heading", { name: /related images/i })
    ).toHaveLength(1)
    expect(screen.queryAllByRole("heading").length).toEqual(3)
    expect(screen.queryAllByRole("img").length).toEqual(2)
    expect(screen.queryAllByRole("figure").length).toEqual(2)
  })

  it("should not render data when media array is empty", () => {
    options.propsData.media = []
    render(VRelatedImages, options)
    expect(screen.getByRole("heading").textContent).toContain("Related images")
    expect(screen.queryAllByRole("img").length).toEqual(0)
  })

  it("should send SELECT_SEARCH_RESULT event when clicked", async () => {
    const mainMediaId = "123"
    const query = "cat"

    const { queryAllByRole } = render(
      VRelatedImages,
      options,
      (localVue, options) => {
        const relatedMediaStore = useRelatedMediaStore(options.pinia)
        relatedMediaStore.$patch({ mainMediaId })
        useSearchStore(options.pinia).$patch({ searchTerm: query })
      }
    )
    const imageLink = queryAllByRole("link")[0]

    await fireEvent.click(imageLink)

    expect(sendCustomEventMock).toHaveBeenCalledWith("SELECT_SEARCH_RESULT", {
      id: media[0].id,
      mediaType: IMAGE,
      query,
      provider: media[0].provider,
      relatedTo: mainMediaId,
    })
  })
})
