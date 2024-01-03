import { useNuxtApp } from "#imports"

import { mockCreateApiService } from "~~/test/unit/test-utils/api-service-mock"

import apiTokenPlugin, {
  Process,
  expiryThreshold,
} from "~/plugins/api-token.server"

import type { AxiosRequestConfig } from "axios"

// Comment this out if you need to debug the tests as the logs are quite helpful
jest.mock("~/utils/console", () => ({
  log: () => {
    /* noop */
  },
  error: () => {
    /* noop */
  },
}))

// Need to export this for TS to be happy
// eslint-disable-next-line jest/no-export
export declare let process: NodeJS.Process & Process

const matchTokenDataRequest = /auth_tokens\/token/

type $config = Partial<{
  apiClientId: string
  apiClientSecret: string
}>

const defaultConfig: Required<$config> = {
  apiClientId: "abcdefg_client_i_d",
  apiClientSecret: "shhhhhhhhh_1234_super_secret",
}

const matchTokenDataRequestBody = new URLSearchParams({
  client_id: defaultConfig.apiClientId,
  client_secret: defaultConfig.apiClientSecret,
  grant_type: "client_credentials",
}).toString()

const getMockContext = ($config: $config = defaultConfig) =>
  ({
    $sentry: {
      captureException: jest.fn(),
    },
    $config: $config,
  })

const mockInject = jest.fn()

const frozenNow = Date.now()
const frozenSeconds = Math.floor(frozenNow / 1e3)
jest.spyOn(global.Date, "now").mockReturnValue(frozenNow)
const twelveHoursInSeconds = 12 * 3600
let tokenCount = 1
const getMockTokenResponse = (expires_in = twelveHoursInSeconds) => ({
  access_token: `abcd1234_${tokenCount++}`,
  expires_in,
})

const mockResponseAndAssertData =
  (response: [number, unknown?], data = matchTokenDataRequestBody) =>
  (config: AxiosRequestConfig) => {
    expect(config.data).toEqual(data)
    return response
  }

const defaultPromise = Promise.resolve()

describe("api-token.server plugin", () => {
  afterEach(() => {
    mockInject.mockReset()
    process.tokenData = {
      accessToken: "",
      accessTokenExpiry: 0,
    }
    process.tokenFetching = defaultPromise
  })

  describe("successful token retrieval", () => {
    it("should save the token into the process and inject into the context", async () => {
      const mockTokenResponse = getMockTokenResponse()
      mockCreateApiService((axiosMockAdapter) => {
        axiosMockAdapter
          .onPost(matchTokenDataRequest)
          .replyOnce(mockResponseAndAssertData([200, mockTokenResponse]))
      })
      const nuxtApp = useNuxtApp()
      await apiTokenPlugin(nuxtApp)

      expect(process.tokenData).toMatchObject({
        accessToken: mockTokenResponse.access_token,
        accessTokenExpiry: frozenSeconds + twelveHoursInSeconds,
      })

      expect(mockInject).toHaveBeenCalledWith(
        "openverseApiToken",
        process.tokenData.accessToken
      )
    })

    it("should re-retrieve the token when about to expire", async () => {
      const mockTokenResponse = getMockTokenResponse(expiryThreshold - 1)
      const nextMockTokenResponse = getMockTokenResponse()
      mockCreateApiService((axiosMockAdapter) => {
        axiosMockAdapter
          .onPost(matchTokenDataRequest)
          .replyOnce(mockResponseAndAssertData([200, mockTokenResponse]))

          .onPost(matchTokenDataRequest)
          .replyOnce(mockResponseAndAssertData([200, nextMockTokenResponse]))
      })

      const nuxtApp = useNuxtApp()
      await apiTokenPlugin(nuxtApp)
      await apiTokenPlugin(nuxtApp)

      expect(process.tokenData).toMatchObject({
        accessToken: nextMockTokenResponse.access_token,
        accessTokenExpiry: frozenSeconds + twelveHoursInSeconds,
      })
    })

    it("should not request a new token if the token is not about to expire", async () => {
      const mockTokenResponse = getMockTokenResponse(twelveHoursInSeconds)
      const nextMockTokenResponse = getMockTokenResponse()
      mockCreateApiService((axiosMockAdapter) => {
        axiosMockAdapter
          .onPost(matchTokenDataRequest)
          .replyOnce(mockResponseAndAssertData([200, mockTokenResponse]))

          .onPost(matchTokenDataRequest)
          .replyOnce(mockResponseAndAssertData([200, nextMockTokenResponse]))
      })

      const nuxtApp = useNuxtApp()
      await apiTokenPlugin(nuxtApp)
      await apiTokenPlugin(nuxtApp)

      expect(process.tokenData).toMatchObject({
        accessToken: mockTokenResponse.access_token,
        accessTokenExpiry: frozenSeconds + twelveHoursInSeconds,
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
       * calls up to the first blocking await which will either be the the call to
       * `refreshApiAccessToken` which makes the axios call (blocked by the adapter
       * mock in this test) _or_ awaiting the promise shared by the entire process.
       */
      const mockTokenResponse = getMockTokenResponse()
      const nextMockTokenResponse = getMockTokenResponse()
      let resolveFirstRequestPromise: undefined | ((value: unknown) => void) =
        undefined
      const resolveFirstRequest = async () => {
        while (!resolveFirstRequestPromise) {
          await new Promise((r) => setTimeout(r, 1))
        }
        resolveFirstRequestPromise({})
      }

      mockCreateApiService((mockAdapter) => {
        mockAdapter
          .onPost(matchTokenDataRequest)
          .replyOnce(async () => {
            const promise = new Promise((resolve) => {
              resolveFirstRequestPromise = resolve as () => void
            })

            await promise

            return [200, mockTokenResponse]
          })

          .onPost(matchTokenDataRequest)
          .replyOnce(mockResponseAndAssertData([200, nextMockTokenResponse]))
      })

      const nuxtApp = useNuxtApp()
      const promises = [
        apiTokenPlugin(nuxtApp),
        apiTokenPlugin(nuxtApp),
        apiTokenPlugin(nuxtApp),
      ]

      await resolveFirstRequest()
      await Promise.all(promises)

      // If the process tokenData still matches the first
      // request's return then we know that all three requests
      // used the same response.
      expect(process.tokenData).toMatchObject({
        accessToken: mockTokenResponse.access_token,
        accessTokenExpiry: frozenSeconds + twelveHoursInSeconds,
      })
    })
  })

  describe("unnecessful token retrieval", () => {
    it("should record the error in sentry", async () => {
      mockCreateApiService((mockAdapter) => {
        mockAdapter
          .onPost(matchTokenDataRequest)
          .replyOnce(mockResponseAndAssertData([418]))
      })

      const mockContext = getMockContext()
      let capturedError: Error | undefined = undefined
      ;(
        mockContext.$sentry.captureException as jest.Mock
      ).mockImplementationOnce((e: Error) => {
        capturedError = e
      })

      await apiTokenPlugin(useNuxtApp())

      expect(mockContext.$sentry.captureException).toHaveBeenCalledTimes(1)
      expect(capturedError).not.toBeUndefined()
      expect((capturedError as unknown as Error).message).toMatch(
        "Unable to retrieve API token. Request failed with status code 418"
      )
    })

    it("should empty the token data", async () => {
      mockCreateApiService((mockAdapter) => {
        mockAdapter
          .onPost(matchTokenDataRequest)
          .replyOnce(
            mockResponseAndAssertData([
              200,
              getMockTokenResponse(expiryThreshold - 1),
            ])
          )

          .onPost(matchTokenDataRequest)
          .replyOnce(mockResponseAndAssertData([418]))
      })

      await apiTokenPlugin(useNuxtApp())
      expect(process.tokenData.accessToken).not.toEqual("")
      await apiTokenPlugin(useNuxtApp())
      expect(process.tokenData.accessToken).toEqual("")
    })

    it("should properly release the mutex and allow for subsequent requests to retry the token refresh", async () => {
      const finalTokenResponse = getMockTokenResponse()
      mockCreateApiService((mockAdapter) => {
        mockAdapter
          .onPost(matchTokenDataRequest)
          .replyOnce(
            mockResponseAndAssertData([
              200,
              getMockTokenResponse(expiryThreshold - 1),
            ])
          )

          .onPost(matchTokenDataRequest)
          .replyOnce(mockResponseAndAssertData([418]))

          .onPost(matchTokenDataRequest)
          .replyOnce(mockResponseAndAssertData([200, finalTokenResponse]))
      })

      const nuxtApp = useNuxtApp()
      await apiTokenPlugin(nuxtApp)
      await apiTokenPlugin(nuxtApp)
      expect(process.fetchingMutex.isLocked()).toBe(false)
      await apiTokenPlugin(nuxtApp)
      expect(process.tokenData.accessToken).toEqual(
        finalTokenResponse.access_token
      )
    })
  })

  describe("missing client credentials", () => {
    describe("completely missing", () => {
      it("should not make any requests and fall back to tokenless", async () => {
        await apiTokenPlugin(useNuxtApp())
        expect(mockInject).toHaveBeenCalledWith("openverseApiToken", "")
      })
    })

    describe("explicitly undefined", () => {
      it("should not make any requests and fall back to tokenless", async () => {
        await apiTokenPlugin(useNuxtApp())
        expect(mockInject).toHaveBeenCalledWith("openverseApiToken", "")
      })
    })
  })
})
