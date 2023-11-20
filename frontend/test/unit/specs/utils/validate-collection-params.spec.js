import { createPinia, setActivePinia } from "~~/test/unit/test-utils/pinia"

import { validateCollectionParams } from "~/utils/validate-collection-params"
import { useProviderStore } from "~/stores/provider"
import { useFeatureFlagStore } from "~/stores/feature-flag"
import { AUDIO, IMAGE } from "~/constants/media"
import { warn } from "~/utils/console"

jest.mock("~/utils/console", () => ({
  warn: jest.fn(),
}))

describe("validateCollectionParams", () => {
  /** @type { import("pinia").Pinia } **/
  let pinia

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    useProviderStore().isSourceNameValid = jest.fn(() => true)
    useFeatureFlagStore().toggleFeature("additional_search_views", "on")
  })

  it("returns null if feature flag is off", () => {
    useFeatureFlagStore().toggleFeature("additional_search_views", "off")

    const result = validateCollectionParams({
      firstParam: "tag",
      mediaType: IMAGE,
      params: { tag: "nature" },
      $pinia: pinia,
    })

    expect(result).toBeNull()
  })

  it.each`
    firstParam  | mediaType | params                                                                                  | expected
    ${"tag"}    | ${IMAGE}  | ${{ tag: "nature" }}                                                                    | ${{ collection: "tag", tag: "nature" }}
    ${"source"} | ${IMAGE}  | ${{ source: "flickr", pathMatch: "/flickr" }}                                           | ${{ collection: "source", source: "flickr" }}
    ${"source"} | ${AUDIO}  | ${{ source: "freesound", pathMatch: "/freesound" }}                                     | ${{ collection: "source", source: "freesound" }}
    ${"source"} | ${IMAGE}  | ${{ source: "flickr", pathMatch: "/flickr/creator/creatorName" }}                       | ${{ collection: "creator", source: "flickr", creator: "creatorName" }}
    ${"source"} | ${IMAGE}  | ${{ source: "flickr", pathMatch: "/flickr/creator/http%3A%2F%2FcreatorName.com%2Fme" }} | ${{ collection: "creator", source: "flickr", creator: "http%3A%2F%2FcreatorName.com%2Fme" }}
  `(
    "returns $expected for $firstParam and $mediaType",
    ({ firstParam, mediaType, params, expected }) => {
      const result = validateCollectionParams({
        firstParam,
        mediaType,
        params,
        $pinia: pinia,
      })

      expect(result).toEqual(expected)
    }
  )
  it.each`
    firstParam  | mediaType | params
    ${"source"} | ${IMAGE}  | ${{ source: "flickr", pathMatch: "/invalidSourceName/creator/creatorName" }}
    ${"source"} | ${AUDIO}  | ${{ source: "invalidSourceName", pathMatch: "/invalidSourceName" }}
  `(
    "returns `null` for invalid source name",
    ({ firstParam, mediaType, params }) => {
      useProviderStore().isSourceNameValid = jest.fn(() => false)

      const result = validateCollectionParams({
        firstParam,
        mediaType,
        params,
        $pinia: pinia,
      })

      expect(result).toBeNull()
      expect(warn).toHaveBeenCalledWith(
        'Invalid source name "invalidSourceName" for a creator collection page.'
      )
    }
  )
})
