// @vitest-environment node
import axios from "axios"

import { describe, expect, it, vi } from "vitest"

import {
  defaultConfig,
  defaultPromise,
  frozenNow,
  frozenSeconds,
  getMockTokenResponse,
  twelveHoursInSeconds,
} from "~~/test/unit/specs/utils/api-token/setup"

import { expiryThreshold, getApiAccessToken } from "~/plugins/api-token.server"

vi.resetModules()

vi.mock("axios", async (importOriginal) => {
  const original = await importOriginal()
  return {
    default: {
      ...original,
      post: vi.fn(() => Promise.resolve({ data: {} })),
    },
  }
})

vi.mock("#app/nuxt", async () => {
  const original = await import("#app/nuxt")
  return {
    ...original,
    useNuxtApp: vi.fn(),
    useRuntimeConfig: vi.fn(() => ({
      public: { apiUrl: "https://api.openverse.org/" },
    })),
  }
})

vi.spyOn(global.Date, "now").mockReturnValue(frozenNow)

describe.sequential("api-token", () => {
  afterEach(() => {
    process.tokenData = {
      accessToken: "",
      accessTokenExpiry: 0,
    }
    process.tokenFetching = defaultPromise
  })

  describe("successful token retrieval", () => {
    // https://github.com/wordpress/openverse/issues/411
    it.skip("should save the token into the process and inject into the context", async () => {
      const mockTokenResponse = getMockTokenResponse()
      axios.post.mockImplementationOnce(() =>
        Promise.resolve({ data: mockTokenResponse })
      )

      const token = await getApiAccessToken(defaultConfig)

      expect(token).toEqual(mockTokenResponse.access_token)
      expect(process.tokenData).toMatchObject({
        accessToken: mockTokenResponse.access_token,
        accessTokenExpiry: frozenSeconds + twelveHoursInSeconds,
      })
    })

    // https://github.com/wordpress/openverse/issues/411
    it.skip("should re-retrieve the token when about to expire", async () => {
      const mockTokenResponse = getMockTokenResponse(expiryThreshold - 1)
      const nextMockTokenResponse = getMockTokenResponse()

      axios.post.mockImplementationOnce(() =>
        Promise.resolve({ data: mockTokenResponse })
      )
      axios.post.mockImplementationOnce(() =>
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

    // https://github.com/wordpress/openverse/issues/411
    it.skip("should not request a new token if the token is not about to expire", async () => {
      const mockTokenResponse = getMockTokenResponse(twelveHoursInSeconds)
      const nextMockTokenResponse = getMockTokenResponse()

      axios.post.mockImplementationOnce(() =>
        Promise.resolve({ data: mockTokenResponse })
      )
      axios.post.mockImplementationOnce(() =>
        Promise.resolve({ data: nextMockTokenResponse })
      )

      await getApiAccessToken(defaultConfig)
      const token = await getApiAccessToken(defaultConfig)

      expect(token).toEqual(mockTokenResponse.access_token)
      expect(process.tokenData.accessTokenExpiry).toEqual(
        frozenSeconds + twelveHoursInSeconds
      )
    })
  })
})
