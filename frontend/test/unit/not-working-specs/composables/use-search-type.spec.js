import { createPinia, setActivePinia } from "~~/test/unit/test-utils/pinia"

import useSearchType from "~/composables/use-search-type"
import { useAnalytics } from "~/composables/use-analytics"

vi.mock("~/composables/use-analytics")

import { ALL_MEDIA, AUDIO, IMAGE } from "~/constants/media"

describe("useSearchType", () => {
  const sendCustomEventMock = vi.fn()
  beforeEach(() => {
    sendCustomEventMock.mockClear()

    setActivePinia(createPinia())
    useAnalytics.mockImplementation(() => ({
      sendCustomEvent: sendCustomEventMock,
    }))
  })

  it("should have correct initial values", () => {
    const {
      activeType,
      types: searchTypes,
      icons,
      labels,
      additionalTypes,
    } = useSearchType()
    expect(activeType.value).toEqual(ALL_MEDIA)
    expect(searchTypes).toEqual([ALL_MEDIA, IMAGE, AUDIO])
    expect(icons).toEqual({
      all: "all",
      audio: "audio",
      image: "image",
      "model-3d": "model-3d",
      video: "video",
    })
    expect(labels).toEqual({
      all: "searchType.all",
      audio: "searchType.audio",
      image: "searchType.image",
      "model-3d": "searchType.model3d",
      video: "searchType.video",
    })
    expect(additionalTypes.value).toEqual([])
  })

  it("should return correct props for active search type when type is not passed", () => {
    const { getSearchTypeProps } = useSearchType()

    const { icon, label } = getSearchTypeProps()
    expect(icon).toEqual(ALL_MEDIA)
    expect(label).toEqual("searchType.all")
  })

  it("should return correct props when type is passed", () => {
    const { getSearchTypeProps } = useSearchType()

    const { icon, label } = getSearchTypeProps(AUDIO)
    expect(icon).toEqual(AUDIO)
    expect(label).toEqual("searchType.audio")
  })

  it("should send the analytics event when setActiveType is called", () => {
    const { setActiveType } = useSearchType()

    setActiveType(AUDIO)
    expect(sendCustomEventMock).toHaveBeenCalledWith("CHANGE_CONTENT_TYPE", {
      component: "Unknown",
      next: AUDIO,
      previous: ALL_MEDIA,
    })
  })

  it("should not send the analytics event when setActiveType is called with current type", () => {
    const { setActiveType } = useSearchType()

    setActiveType(ALL_MEDIA)
    expect(sendCustomEventMock).not.toHaveBeenCalled()
  })
})
