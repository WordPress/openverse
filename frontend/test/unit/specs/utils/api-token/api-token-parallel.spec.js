// @vitest-environment node
import { expect, it, vi } from "vitest"

import axios from "axios"

import {
  defaultConfig,
  frozenSeconds,
  getMockTokenResponse,
} from "~~/test/unit/specs/utils/api-token/setup"

import { getApiAccessToken } from "~/plugins/api-token.server"

vi.resetModules()

vi.mock("axios", async (importOriginal) => {
  const original = await importOriginal()
  return {
    default: {
      ...original,
      post: vi.fn(),
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

// https://github.com/wordpress/openverse/issues/411
it.skip("subsequent requests should all block on the same token retrieval promise", async () => {
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
