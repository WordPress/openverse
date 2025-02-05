import { describe, expect, it, vi } from "vitest"
import axios from "axios"
import { useRuntimeConfig } from "#app/nuxt"

import {
  expiryThreshold,
  getApiAccessToken,
} from "~/plugins/01.api-token.server"

vi.mock("axios", async (importOriginal) => {
  const original = await importOriginal()
  return {
    default: {
      ...original,
      post: vi.fn(() => Promise.resolve({ data: {} })),
    },
  }
})

const mocks = vi.hoisted(() => {
  return {
    useRuntimeConfig: vi.fn(),
  }
})
vi.mock("#app/nuxt", async (importOriginal) => {
  const original = await importOriginal()
  return {
    ...original,
    useRuntimeConfig: mocks.useRuntimeConfig,
  }
})

const frozenNow = Date.now()
vi.spyOn(global.Date, "now").mockReturnValue(frozenNow)

const defaultConfig = {
  public: {
    apiUrl: "https://api.openverse.org/",
  },
  apiClientId: "abcdefg_client_i_d",
  apiClientSecret: "shhhhhhhhh_1234_super_secret",
}

const defaultPromise = Promise.resolve()
const iAmATeapotError = new axios.AxiosError(
  "I'm a teapot",
  {},
  { status: 418 }
)
const frozenSeconds = Math.floor(frozenNow / 1e3)
const twelveHoursInSeconds = 12 * 3600

let tokenCount = 1
const getMockTokenResponse = (expires_in = twelveHoursInSeconds) => ({
  access_token: `abcd1234_${tokenCount++}`,
  expires_in,
})

describe("token retrieval", () => {
  beforeEach(() => {
    vi.resetAllMocks()
    process.tokenData = {
      accessToken: "",
      accessTokenExpiry: 0,
    }
    process.tokenFetching = defaultPromise
  })

  describe("unsuccessful", () => {
    beforeEach(() => {
      vi.mocked(useRuntimeConfig).mockReturnValue({ ...defaultConfig })
    })
    it("should empty the token data", async () => {
      const firstTokenResponse = getMockTokenResponse(expiryThreshold - 1)

      // Mock first request success, second request failure
      axios.post
        .mockImplementationOnce(() =>
          Promise.resolve({ data: firstTokenResponse })
        )
        .mockImplementationOnce(() => Promise.reject(iAmATeapotError))

      // First call should get valid token
      const firstToken = await getApiAccessToken()
      expect(firstToken).toBe(firstTokenResponse.access_token)

      // Second call should fail and clear token
      const secondToken = await getApiAccessToken()
      expect(secondToken).toBe("")
      expect(process.tokenData.accessToken).toBe("")
      expect(process.tokenData.accessTokenExpiry).toBe(0)
    })

    it("should properly release the mutex and allow for subsequent requests to retry the token refresh", async () => {
      const firstTokenResponse = getMockTokenResponse(expiryThreshold - 1)
      const finalTokenResponse = getMockTokenResponse()

      // Mock sequence: success -> failure -> success
      axios.post
        .mockImplementationOnce(() =>
          Promise.resolve({ data: firstTokenResponse })
        )
        .mockImplementationOnce(() => Promise.reject(iAmATeapotError))
        .mockImplementationOnce(() =>
          Promise.resolve({ data: finalTokenResponse })
        )

      // First successful call
      const token1 = await getApiAccessToken()
      expect(token1).toBe(firstTokenResponse.access_token)

      // Failed refresh should return empty string
      const token2 = await getApiAccessToken()
      expect(token2).toBe("")

      // New successful call with fresh token
      const token3 = await getApiAccessToken()
      expect(token3).toBe(finalTokenResponse.access_token)
    })
  })

  describe("missing client credentials", () => {
    it("completely missing: should not make any requests and fall back to tokenless", async () => {
      vi.mocked(useRuntimeConfig).mockReturnValue({
        public: { ...defaultConfig.public },
      })

      const token = await getApiAccessToken()

      expect(token).toEqual(undefined)
    })

    it("explicitly undefined: should not make any requests and fall back to tokenless", async () => {
      vi.mocked(useRuntimeConfig).mockReturnValue({
        public: { ...defaultConfig.public },
        apiClientId: undefined,
        apiClientSecret: undefined,
      })
      const token = await getApiAccessToken()
      expect(token).toEqual(undefined)
    })
  })

  describe("successful token retrieval", () => {
    beforeEach(() => {
      vi.clearAllMocks()
      vi.mocked(useRuntimeConfig).mockReturnValue({ ...defaultConfig })
    })
    it("should save the token into the process and inject into the context", async () => {
      const mockTokenResponse = getMockTokenResponse()
      axios.post.mockImplementationOnce(() =>
        Promise.resolve({ data: mockTokenResponse })
      )

      const token = await getApiAccessToken()

      expect(token).toEqual(mockTokenResponse.access_token)
      expect(process.tokenData).toMatchObject({
        accessToken: mockTokenResponse.access_token,
        accessTokenExpiry: frozenSeconds + twelveHoursInSeconds,
      })
    })

    it("should re-retrieve the token when about to expire", async () => {
      const mockTokenResponse = getMockTokenResponse(expiryThreshold - 1)
      const nextMockTokenResponse = getMockTokenResponse()

      axios.post
        .mockImplementationOnce(() =>
          Promise.resolve({ data: mockTokenResponse })
        )
        .mockImplementationOnce(() =>
          Promise.resolve({ data: nextMockTokenResponse })
        )

      await getApiAccessToken(defaultConfig)
      const token = await getApiAccessToken(defaultConfig)

      expect(token).toEqual(nextMockTokenResponse.access_token)
      expect(process.tokenData).toMatchObject({
        accessToken: nextMockTokenResponse.access_token,
        accessTokenExpiry: frozenSeconds + twelveHoursInSeconds,
      })
    })

    it("should not request a new token if the token is not about to expire", async () => {
      const mockTokenResponse = getMockTokenResponse(twelveHoursInSeconds)
      const nextMockTokenResponse = getMockTokenResponse()

      axios.post
        .mockImplementationOnce(() =>
          Promise.resolve({ data: mockTokenResponse })
        )
        .mockImplementationOnce(() =>
          Promise.resolve({ data: nextMockTokenResponse })
        )

      await getApiAccessToken()
      const token = await getApiAccessToken()

      expect(token).toEqual(mockTokenResponse.access_token)
      expect(process.tokenData.accessTokenExpiry).toEqual(
        frozenSeconds + twelveHoursInSeconds
      )
    })
  })

  it("subsequent requests should all block on the same token retrieval promise", async () => {
    /**
     * This test is pretty complicated because we need to simulate
     * multiple requests coming in at the same time with requests
     * to the token API resolving only after the multiple
     * requests have come in. If we didn't cause the request for the
     * token to block until we'd fired off all three requests then
     * the first request could resolve before the other two had a chance
     * to check the mutex and await on the fetching promise.
     *
     * This relies on the behavior of the Node event loop where
     * several async functions called synchronously in succession will execute
     * up until the first blocking `await` and then return the promise. This allows
     * us to effectively get all three of the async api token plugin function
     * calls up to the first blocking await which will either be the call to
     * `refreshApiAccessToken` which makes the axios call (blocked by the adapter
     * mock in this test) _or_ awaiting the promise shared by the entire process.
     */
    vi.mocked(useRuntimeConfig).mockReturnValue({ ...defaultConfig })
    const mockTokenResponse = getMockTokenResponse()
    const nextMockTokenResponse = getMockTokenResponse()
    let resolveFirstRequestPromise = undefined
    const resolveFirstRequest = async () => {
      while (!resolveFirstRequestPromise) {
        await new Promise((r) => setTimeout(r, 1))
      }
      resolveFirstRequestPromise({})
    }

    axios.post.mockImplementationOnce(async () => {
      const promise = new Promise((resolve) => {
        resolveFirstRequestPromise = resolve
      })

      await promise
      return { data: mockTokenResponse }
    })
    axios.post.mockImplementationOnce(() =>
      Promise.resolve({ data: nextMockTokenResponse })
    )

    const promises = [
      getApiAccessToken(defaultConfig),
      getApiAccessToken(defaultConfig),
      getApiAccessToken(defaultConfig),
    ]

    await resolveFirstRequest()
    await Promise.all(promises)

    // If the process tokenData still matches the first
    // request's return then we know that all three requests
    // used the same response.
    expect(process.tokenData).toMatchObject({
      accessToken: mockTokenResponse.access_token,
      accessTokenExpiry: mockTokenResponse.expires_in + frozenSeconds,
    })
  })
})
