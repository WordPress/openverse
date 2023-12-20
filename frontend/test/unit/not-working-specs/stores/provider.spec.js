import { beforeEach, describe, expect, vi } from "vitest"

import { AxiosError } from "axios"

import { setActivePinia, createPinia } from "~~/test/unit/test-utils/pinia"

import { warn } from "~/utils/console"
import { AUDIO, IMAGE, supportedMediaTypes } from "~/constants/media"
import { useSearchStore } from "~/stores/search"
import { useProviderStore } from "~/stores/provider"
import { initProviderServices } from "~/data/media-provider-service"

vi.mock("~/utils/console", () => ({ warn: vi.fn(), log: vi.fn() }))

process.env.providerUpdateFrequency = "0"

const mockData = [
  {
    source_name: "test_source",
    display_name: "",
    source_url: "https://test.org",
    logo_url: null,
    media_count: 4,
  },
  {
    source_name: "wikimedia",
    display_name: "Wikimedia Commons",
    source_url: "https://commons.wikimedia.org",
    logo_url: null,
    media_count: 47823833,
  },
  {
    source_name: "wordpress",
    display_name: "WP Photo Directory",
    source_url: "https://wordpress.org/photos",
    logo_url: null,
    media_count: 154,
  },
]

const mockImplementation = () => Promise.resolve([...mockData])
const mock = vi.fn().mockImplementation(mockImplementation)
vi.mock("~/data/media-provider-service", () => ({
  initProviderServices: {
    audio: () =>
      /** @type {typeof import('~/data/media-provider-services').MediaProviderService} */ ({
        getProviderStats: mock,
      }),
    image: () =>
      /** @type {typeof import('~/data/media-provider-services').MediaProviderService} */ ({
        getProviderStats: mock,
      }),
  },
}))

describe("Provider Store", () => {
  let providerStore
  beforeEach(() => {
    setActivePinia(createPinia())
    providerStore = useProviderStore()
  })
  afterEach(() => {
    mock.mockClear()
  })
  afterAll(() => {
    warn.mockReset()
  })

  it("sets the default state", () => {
    expect(providerStore.providers).toEqual({
      [AUDIO]: [],
      [IMAGE]: [],
    })
    expect(providerStore.fetchState).toEqual({
      [AUDIO]: { hasStarted: false, isFetching: false, fetchingError: null },
      [IMAGE]: { hasStarted: false, isFetching: false, fetchingError: null },
    })
  })

  it.each`
    providerCode     | displayName
    ${"wikimedia"}   | ${"Wikimedia Commons"}
    ${"wordpress"}   | ${"WP Photo Directory"}
    ${"test_source"} | ${"Test Source"}
  `(
    "getProviderName returns provider name or capitalizes providerCode",
    async ({ providerCode, displayName }) => {
      await providerStore.fetchMediaProviders()
      expect(providerStore.getProviderName(providerCode, IMAGE)).toEqual(
        displayName
      )
    }
  )

  it("fetchMediaProviders on success", async () => {
    await providerStore.fetchMediaProviders()
    expect(providerStore.fetchState[IMAGE]).toEqual({
      fetchingError: null,
      hasStarted: true,
      isFetching: false,
    })
    expect(providerStore.providers[IMAGE]).toEqual(mockData)
  })

  it("fetchMediaProviders on error", async () => {
    for (const mediaType of supportedMediaTypes) {
      initProviderServices[mediaType] = () => ({
        getProviderStats: vi.fn().mockImplementation(() =>
          Promise.reject(
            new AxiosError(
              "Not found",
              AxiosError.ERR_BAD_REQUEST,
              {},
              {},
              {
                data: { detail: "Not found" },
                status: 404,
                statusText: "Not found",
                headers: {},
                config: {},
              }
            )
          )
        ),
      })
    }
    const searchStore = useSearchStore()
    await providerStore.fetchMediaProviders()
    for (const mediaType of supportedMediaTypes) {
      expect(providerStore.fetchState[mediaType].fetchingError).toEqual({
        code: AxiosError.ERR_BAD_REQUEST,
        message: "Not found",
        requestKind: "provider",
        searchType: mediaType,
        statusCode: 404,
      })
      expect(providerStore.providers[mediaType]).toEqual([])
      expect(searchStore.filters[`${mediaType}Providers`]).toEqual([])
    }
  })
})
