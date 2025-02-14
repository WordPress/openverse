import { beforeEach, describe, expect, it } from "vitest"
import { createPinia, setActivePinia } from "~~/test/unit/test-utils/pinia"

import { ALL_MEDIA, AUDIO, IMAGE } from "#shared/constants/media"
import useSearchType from "~/composables/use-search-type"

describe("useSearchType", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it("should have correct initial values", async () => {
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

  it("should return correct props for active search type when type is not passed", async () => {
    const { getSearchTypeProps } = useSearchType()

    const { label } = getSearchTypeProps()
    expect(label).toBe("All content")
  })

  it("should return correct props when type is passed", async () => {
    const { getSearchTypeProps } = useSearchType()

    const { label } = getSearchTypeProps(AUDIO)
    expect(label).toBe("Audio")
  })
})
