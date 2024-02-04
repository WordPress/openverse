import { expect, describe, it, beforeEach } from "vitest"

import { setActivePinia, createPinia } from "~~/test/unit/test-utils/pinia"

import { image as imageObject } from "~~/test/unit/fixtures/image"

import { deepClone } from "~/utils/clone"

import { initialResults, useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import {
  ALL_MEDIA,
  AUDIO,
  IMAGE,
  supportedMediaTypes,
  VIDEO,
} from "~/constants/media"
import { NO_RESULT } from "~/constants/errors"
import { useFeatureFlagStore } from "~/stores/feature-flag"
import { ON } from "~/constants/feature-flag"

const uuids = [
  "0dea3af1-27a4-4635-bab6-4b9fb76a59f5",
  "32c22b5b-f2f9-47db-b64f-6b86c2431942",
  "fd527776-00f8-4000-9190-724fc4f07346",
  "81e551de-52ab-4852-90eb-bc3973c342a0",
]
const items = (mediaType) =>
  uuids.map((uuid, i) => ({
    id: uuid,
    title: `${mediaType} ${i + 1}`,
    creator: `creator ${i + 1}`,
    tags: [],
  }))

const audioItems = items(AUDIO)
const imageItems = items(IMAGE)
const testResultItems = (mediaType) =>
  items(mediaType).reduce((acc, item) => {
    acc[item.id] = item
    return acc
  }, {})

const testResult = (mediaType) => ({
  count: 10001,
  items: testResultItems(mediaType),
  page: 2,
  pageCount: 20,
})

const testApiResult = (mediaType) => ({
  count: 10001,
  results: items(mediaType),
  page: 2,
  pageCount: 20,
})

describe("media store", () => {
  describe("state", () => {
    it("sets default state", () => {
      setActivePinia(createPinia())
      const mediaStore = useMediaStore()

      expect(mediaStore.results).toEqual({
        image: { ...initialResults },
        audio: { ...initialResults },
      })
      expect(mediaStore.mediaFetchState).toEqual({
        audio: {
          fetchingError: null,
          hasStarted: false,
          isFetching: false,
          isFinished: false,
        },
        image: {
          fetchingError: null,
          hasStarted: false,
          isFetching: false,
          isFinished: false,
        },
      })
    })
  })

  describe("getters", () => {
    beforeEach(() => {
      setActivePinia(createPinia())
    })

    it("searchType falls back to ALL_MEDIA for additional search types", () => {
      const featureFlagStore = useFeatureFlagStore()
      featureFlagStore.toggleFeature("additional_search_types", ON)

      const searchStore = useSearchStore()
      searchStore.setSearchType(VIDEO)

      const mediaStore = useMediaStore()
      expect(mediaStore._searchType).toEqual(ALL_MEDIA)
    })

    it("getItemById returns undefined if there are no items", () => {
      const mediaStore = useMediaStore()
      expect(mediaStore.getItemById(IMAGE, "foo")).toBeUndefined()
    })

    it("getItemById returns correct item", () => {
      const mediaStore = useMediaStore()
      const expectedItem = { id: "foo", title: "ImageFoo" }
      mediaStore.results.image.items = { foo: expectedItem }
      expect(mediaStore.getItemById(IMAGE, "foo")).toEqual(expectedItem)
    })

    it("resultItems returns correct items", () => {
      const mediaStore = useMediaStore()
      mediaStore.results.audio = testResult(AUDIO)
      mediaStore.results.image = testResult(IMAGE)

      expect(mediaStore.resultItems).toEqual({
        [AUDIO]: audioItems,
        [IMAGE]: imageItems,
      })
    })

    it("allMedia returns correct items", () => {
      const mediaStore = useMediaStore()
      mediaStore.results.audio = testResult(AUDIO)
      mediaStore.results.image = testResult(IMAGE)

      expect(mediaStore.allMedia).toEqual([
        imageItems[0],
        audioItems[0],
        audioItems[1],
        imageItems[1],
        imageItems[2],
        imageItems[3],
      ])
    })

    /**
     * Normally, this should randomly intersperse items from other media types.
     * Now, however, it simply returns the audio items in order.
     * TODO: Add video and check for randomization.
     */
    it("allMedia returns items even if there are no images", () => {
      const mediaStore = useMediaStore()
      mediaStore.results.audio = testResult(AUDIO)

      expect(mediaStore.allMedia).toEqual(audioItems)
    })
    it("resultCountsPerMediaType returns correct items for %s", () => {
      const mediaStore = useMediaStore()
      mediaStore.results.image = testResult(IMAGE)

      // image is first in the returned list
      expect(mediaStore.resultCountsPerMediaType).toEqual([
        [IMAGE, testResult(IMAGE).count],
        [AUDIO, initialResults.count],
      ])
    })

    it.each`
      searchType   | count
      ${ALL_MEDIA} | ${10000}
      ${AUDIO}     | ${0}
      ${IMAGE}     | ${10000}
    `("resultCount for $searchType returns $count", ({ searchType, count }) => {
      const mediaStore = useMediaStore()
      const searchStore = useSearchStore()
      searchStore.setSearchType(searchType)
      mediaStore.results.image = testResult(IMAGE)

      expect(mediaStore.resultCount).toEqual(count)
    })

    it.each`
      searchType   | audioError             | fetchState
      ${ALL_MEDIA} | ${{ code: NO_RESULT }} | ${{ fetchingError: null, hasStarted: true, isFetching: true, isFinished: false }}
      ${ALL_MEDIA} | ${{ statusCode: 429 }} | ${{ fetchingError: { requestKind: "search", statusCode: 429, searchType: ALL_MEDIA }, hasStarted: true, isFetching: true, isFinished: false }}
      ${AUDIO}     | ${{ statusCode: 429 }} | ${{ fetchingError: { requestKind: "search", statusCode: 429, searchType: AUDIO }, hasStarted: true, isFetching: false, isFinished: true }}
      ${IMAGE}     | ${null}                | ${{ fetchingError: null, hasStarted: true, isFetching: true, isFinished: false }}
    `(
      "fetchState for $searchType returns $fetchState",
      ({ searchType, audioError, fetchState }) => {
        const mediaStore = useMediaStore()
        const searchStore = useSearchStore()
        searchStore.setSearchType(searchType)
        const audioFetchError = audioError
          ? { requestKind: "search", searchType: AUDIO, ...audioError }
          : null
        mediaStore._updateFetchState(AUDIO, "end", audioFetchError)
        mediaStore._updateFetchState(IMAGE, "start")

        expect(mediaStore.fetchState).toEqual(fetchState)
      }
    )

    it("returns NO_RESULT error if all media types have NO_RESULT errors", () => {
      const mediaStore = useMediaStore()
      const searchStore = useSearchStore()
      searchStore.setSearchType(ALL_MEDIA)
      mediaStore._updateFetchState(AUDIO, "end", {
        requestKind: "search",
        searchType: AUDIO,
        code: NO_RESULT,
      })
      mediaStore._updateFetchState(IMAGE, "end", {
        requestKind: "search",
        searchType: IMAGE,
        code: NO_RESULT,
      })

      expect(mediaStore.fetchState).toEqual({
        fetchingError: {
          requestKind: "search",
          code: NO_RESULT,
          searchType: ALL_MEDIA,
        },
        hasStarted: true,
        isFetching: false,
        isFinished: true,
      })
    })

    it("fetchState for ALL_MEDIA returns no error when media types have no errors", () => {
      const mediaStore = useMediaStore()
      const searchStore = useSearchStore()
      searchStore.setSearchType(ALL_MEDIA)
      mediaStore._updateFetchState(AUDIO, "end")
      mediaStore._updateFetchState(IMAGE, "end")

      expect(mediaStore.fetchState).toEqual({
        fetchingError: null,
        hasStarted: true,
        isFetching: false,
        isFinished: false,
      })
    })

    it("fetchState for ALL_MEDIA returns compound error if all types have errors", () => {
      const mediaStore = useMediaStore()
      const searchStore = useSearchStore()
      searchStore.setSearchType(ALL_MEDIA)
      mediaStore._updateFetchState(AUDIO, "end", {
        message: "Error",
        statusCode: 500,
      })
      mediaStore._updateFetchState(IMAGE, "end", {
        message: "Error",
        statusCode: 500,
        requestKind: "search",
        searchType: IMAGE,
      })

      expect(mediaStore.fetchState).toEqual({
        fetchingError: {
          message: "Error",
          statusCode: 500,
          requestKind: "search",
          searchType: IMAGE,
        },
        hasStarted: true,
        isFetching: false,
        isFinished: true,
      })
    })
  })

  describe("actions", () => {
    beforeEach(() => {
      setActivePinia(createPinia())
    })

    it("setMedia updates state persisting images", () => {
      const mediaStore = useMediaStore()

      const img1 = {
        id: "81e551de-52ab-4852-90eb-bc3973c342a0",
        title: "Foo",
        creator: "foo",
        tags: [],
      }
      const img2 = {
        id: "0dea3af1-27a4-4635-bab6-4b9fb76a59f5",
        title: "Bar",
        creator: "bar",
        tags: [],
      }
      mediaStore.results.image.items = { [img1.id]: img1 }
      const params = {
        media: { [img2.id]: img2 },
        mediaCount: 2,
        page: 2,
        pageCount: 1,
        shouldPersistMedia: true,
        mediaType: IMAGE,
      }
      mediaStore.setMedia(params)

      expect(mediaStore.results.image.items).toEqual({
        [img1.id]: img1,
        [img2.id]: img2,
      })
      expect(mediaStore.results.image.count).toBe(params.mediaCount)
      expect(mediaStore.results.image.page).toBe(params.page)
    })

    it("setMedia updates state not persisting images", () => {
      const mediaStore = useMediaStore()
      const image = { ...imageObject, id: "img0" }

      const img = imageObject

      mediaStore.results.image.items = {
        ...mediaStore.results.image.items,
        image,
      }
      mediaStore.results.image.count = 10

      const params = {
        media: { [img.id]: img },
        mediaCount: 2,
        page: 2,
        pageCount: 1,
        shouldPersistMedia: false,
        mediaType: IMAGE,
      }
      mediaStore.setMedia(params)

      expect(mediaStore.results.image).toEqual({
        items: { [img.id]: img },
        count: params.mediaCount,
        page: params.page,
        pageCount: params.pageCount,
      })
    })

    it("setMedia updates state with default count and page", () => {
      const mediaStore = useMediaStore()

      const img = { title: "Foo", creator: "bar", tags: [] }
      mediaStore.results.image.items = ["img1"]
      const params = { media: [img], mediaType: IMAGE }

      mediaStore.setMedia(params)

      expect(mediaStore.results.image.count).toEqual(0)
      expect(mediaStore.results.image.page).toEqual(1)
    })

    it("clearMedia resets the results", () => {
      const mediaStore = useMediaStore()
      const searchStore = useSearchStore()
      searchStore.setSearchType(ALL_MEDIA)
      mediaStore.results.image.items = {
        ...mediaStore.results.image.items,
        ...testResult(IMAGE),
      }
      mediaStore.results.audio.items = {
        ...mediaStore.results.audio.items,
        ...testResult(AUDIO),
      }

      mediaStore.clearMedia()
      supportedMediaTypes.forEach((mediaType) => {
        expect(mediaStore.results[mediaType]).toEqual(initialResults)
      })
    })

    it("setMediaProperties merges the existing media item together with the properties passed in allowing overwriting", () => {
      const mediaStore = useMediaStore()
      mediaStore.results.audio = testResult(AUDIO)

      const existingMediaItem = deepClone(
        mediaStore.getItemById(AUDIO, uuids[0])
      )
      const hasLoaded = Symbol()
      mediaStore.setMediaProperties(AUDIO, uuids[0], {
        hasLoaded,
      })

      expect(mediaStore.getItemById(AUDIO, uuids[0])).toMatchObject({
        ...existingMediaItem,
        hasLoaded,
      })
    })

    it.each`
      mediaType | page | shouldPersistMedia | expectedPathSlug | expectedQueryParams
      ${IMAGE}  | ${0} | ${true}            | ${""}            | ${{}}
      ${IMAGE}  | ${1} | ${true}            | ${""}            | ${{}}
      ${IMAGE}  | ${2} | ${true}            | ${""}            | ${{ page: "2" }}
      ${IMAGE}  | ${1} | ${false}           | ${""}            | ${{}}
      ${AUDIO}  | ${1} | ${true}            | ${""}            | ${{ peaks: "true" }}
      ${AUDIO}  | ${2} | ${true}            | ${""}            | ${{ page: "2", peaks: "true" }}
    `(
      "getSearchUrlParts for search returns correct url parts",
      ({
        mediaType,
        page,
        shouldPersistMedia,
        expectedPathSlug,
        expectedQueryParams,
      }) => {
        const searchStore = useSearchStore()

        searchStore.setSearchTerm("cat")

        const mediaStore = useMediaStore()

        const actualUrlParts = mediaStore.getSearchUrlParts(
          mediaType,
          page,
          shouldPersistMedia
        )

        expect(actualUrlParts.pathSlug).toEqual(expectedPathSlug)
        expect(actualUrlParts.queryParams).toEqual({
          q: "cat",
          ...expectedQueryParams,
        })
      }
    )
  })

  it.each`
    mediaType | collectionParams                                                  | page | shouldPersistMedia | expectedPathSlug                   | expectedQueryParams
    ${IMAGE}  | ${{ source: "flickr", collection: "source" }}                     | ${0} | ${true}            | ${"source/flickr/"}                | ${{}}
    ${IMAGE}  | ${{ tag: "cat", collection: "tag" }}                              | ${1} | ${true}            | ${"tag/cat/"}                      | ${{}}
    ${IMAGE}  | ${{ source: "flickr", collection: "source" }}                     | ${2} | ${true}            | ${"source/flickr/"}                | ${{ page: "2" }}
    ${IMAGE}  | ${{ source: "flickr", creator: "author", collection: "creator" }} | ${1} | ${false}           | ${"source/flickr/creator/author/"} | ${{}}
    ${AUDIO}  | ${{ tag: "cat", collection: "tag" }}                              | ${1} | ${true}            | ${"tag/cat/"}                      | ${{ peaks: "true" }}
    ${AUDIO}  | ${{ source: "flickr", collection: "source" }}                     | ${2} | ${true}            | ${"source/flickr/"}                | ${{ page: "2", peaks: "true" }}
  `(
    "getSearchUrlParts for search returns correct url parts",
    ({
      mediaType,
      collectionParams,
      page,
      shouldPersistMedia,
      expectedPathSlug,
      expectedQueryParams,
    }) => {
      const searchStore = useSearchStore()

      searchStore.setCollectionState(collectionParams, mediaType)

      const mediaStore = useMediaStore()

      const actualUrlParts = mediaStore.getSearchUrlParts(
        mediaType,
        page,
        shouldPersistMedia
      )

      expect(actualUrlParts.pathSlug).toEqual(expectedPathSlug)
      expect(actualUrlParts.queryParams).toEqual(expectedQueryParams)
    }
  )

  it("decodeData returns correct data", () => {
    const mediaStore = useMediaStore()
    const apiResult = testApiResult(IMAGE)
    const data = mediaStore.decodeData(apiResult, IMAGE)

    expect(data.page).toEqual(apiResult.page)
    expect(data.page_size).toEqual(apiResult.page_size)
    expect(data.page_count).toEqual(apiResult.page_count)
    expect(data.count).toEqual(apiResult.count)

    for (const item of Object.values(apiResult.results)) {
      const id = item.id
      for (const [key, value] of Object.entries(item)) {
        expect(data.results[id][key]).toEqual(value)
      }
      expect(data.results[id].frontendMediaType).toEqual(IMAGE)
      expect(data.results[id].isSensitive).toEqual(false)
      expect(data.results[id].sensitivity).toEqual([])
      expect(data.results[id].originalTitle).toEqual(item.title)
    }
  })
})
