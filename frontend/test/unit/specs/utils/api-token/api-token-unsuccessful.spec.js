import { useNuxtApp } from "#imports"

import { describe, expect, it, vi } from "vitest"

import axios from "axios"

import {
  defaultConfig,
  defaultPromise,
  frozenNow,
  getMockTokenResponse,
  iAmATeapotError,
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

const useRuntimeConfigMock = vi.fn()

vi.doMock("#app/nuxt", async () => {
  const original = await import("#app/nuxt")
  return {
    ...original,
    useRuntimeConfig: useRuntimeConfigMock,
  }
})

vi.spyOn(global.Date, "now").mockReturnValue(frozenNow)

describe("unsuccessful token retrieval", () => {
  beforeEach(() => {
    process.tokenData = {
      accessToken: "",
      accessTokenExpiry: 0,
    }
    process.tokenFetching = defaultPromise
  })
  // https://github.com/wordpress/openverse/issues/411
  it.skip("should empty the token data", async () => {
    const app = useNuxtApp()
    const firstTokenResponse = getMockTokenResponse(expiryThreshold - 1)
    axios.post.mockImplementationOnce(() =>
      Promise.resolve({ data: firstTokenResponse })
    )
    axios.post.mockImplementationOnce(() => Promise.reject(iAmATeapotError))

    await getApiAccessToken()
    const { $openverseApiToken: token1 } = app
    expect(token1).toBeUndefined()

    await getApiAccessToken()
    let { $openverseApiToken: token2 } = app
    expect(process.tokenData.accessToken).toBeFalsy()
    expect(process.tokenData.accessTokenExpiry).toBeFalsy()
    expect(token2).toEqual("")
  })

  // https://github.com/wordpress/openverse/issues/411
  it.skip("should properly release the mutex and allow for subsequent requests to retry the token refresh", async () => {
    const firstTokenResponse = getMockTokenResponse(expiryThreshold - 1)
    const finalTokenResponse = getMockTokenResponse()
    axios.post.mockImplementationOnce(() =>
      Promise.resolve({ data: firstTokenResponse })
    )
    axios.post.mockImplementationOnce(() => Promise.reject(iAmATeapotError))
    axios.post.mockImplementationOnce(() =>
      Promise.resolve({ data: finalTokenResponse })
    )

    let token = await getApiAccessToken(defaultConfig)
    expect(token).toEqual(firstTokenResponse.access_token)

    token = await getApiAccessToken(defaultConfig)
    expect(process.fetchingMutex.isLocked()).toBe(false)
    expect(token).toEqual("")

    token = await getApiAccessToken(defaultConfig)
    expect(token).toEqual(finalTokenResponse.access_token)
  })
})
