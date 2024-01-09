import { beforeEach, describe, expect, it } from "vitest"

import { createPinia, setActivePinia } from "~~/test/unit/test-utils/pinia"

import useSearchType from "~/composables/use-search-type"

import { ALL_MEDIA, AUDIO, IMAGE } from "~/constants/media"

describe("useSearchType", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
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
    expect(label).toBe("All content")
  })

  it("should return correct props when type is passed", () => {
    const { getSearchTypeProps } = useSearchType()

    const { icon, label } = getSearchTypeProps(AUDIO)
    expect(icon).toEqual(AUDIO)
    expect(label).toBe("Audio")
  })
})
