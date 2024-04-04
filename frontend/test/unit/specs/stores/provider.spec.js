import { AxiosError } from "axios"
import nock from "nock"

import {
  setActivePinia,
  createPinia,
  mockApiClient,
} from "~~/test/unit/test-utils/pinia"
import { baseUrl } from "~~/test/unit/test-utils/api-client"

import { warn } from "~/utils/console"
import { AUDIO, IMAGE, supportedMediaTypes } from "~/constants/media"
import { useSearchStore } from "~/stores/search"
import { useProviderStore } from "~/stores/provider"

jest.mock("@nuxtjs/composition-api", () => ({
  ssrRef: (v) => jest.fn(v),
}))
jest.mock("~/utils/console", () => ({ warn: jest.fn(), log: jest.fn() }))

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

describe("Provider Store", () => {
  let providerStore
  beforeEach(() => {
    setActivePinia(createPinia())
    providerStore = useProviderStore()
  })
  afterAll(() => {
    warn.mockReset()
  })

  const mockSuccessApi = () =>
    nock(baseUrl)
      .get("/v1/audio/stats/")
      .reply(200, mockData)
      .get("/v1/images/stats/")
      .reply(200, mockData)

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
      const scope = mockSuccessApi()
      await providerStore.fetchMediaProviders()
      expect(providerStore.getProviderName(providerCode, IMAGE)).toEqual(
        displayName
      )
      scope.done()
    }
  )

  it("fetchMediaProviders on success", async () => {
    const scope = mockSuccessApi()
    await providerStore.fetchMediaProviders()
    expect(providerStore.fetchState[IMAGE]).toEqual({
      fetchingError: null,
      hasStarted: true,
      isFetching: false,
    })
    expect(providerStore.providers[IMAGE]).toEqual(mockData)
    scope.done()
  })

  it("fetchMediaProviders on error", async () => {
    const scope = nock(baseUrl)
      .get(/v1\/(images|audio)\/stats/)
      .times(2)
      .reply(404)
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
    scope.done()
  })
})
